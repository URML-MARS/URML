"""URML ROS 2 action server — exposing URML as a ROS 2 action.

This is the "ROS Action interface to your system" that an external behavior
engine (FlexBE, BehaviorTree.CPP, a custom orchestrator) calls to run a URML
program through URML's validate-before-actuate pipeline. It is the inverse of
``RclpyAdapter``: the adapter dispatches URML primitives *to* ROS 2 actions
(Nav2 / MoveIt 2); this server exposes URML *as* a ROS 2 action that drives
that adapter.

## Two layers

1. ``execute_request`` — the **pure, rclpy-free core**. It runs the exact
   ``translate? -> validate -> execute`` flow the ``urml`` CLI runs
   (``cmd_translate`` + ``cmd_execute``), against any ``ROSAdapter`` and any
   provider-agnostic ``Bridge`` provider. It is hermetically testable with
   ``MockROSAdapter`` + ``EchoProvider``; no ROS 2 is required to exercise it.
   This is the part that runs in CI on every host, including Windows.

2. ``URMLActionServerNode`` — a thin ``rclpy`` shell that lazy-imports rclpy
   and the generated ``ExecuteURML`` action, builds an adapter + provider from
   node parameters, and delegates each goal to ``execute_request``. It only
   constructs under a real ROS 2 environment (the generated ``urml_ros2_msgs``
   action package must be on the ``AMENT_PREFIX_PATH``).

## Safety boundary

``execute_request`` always runs the full validator before any actuation, and
refuses (returning ``refused=True`` with the rendered verdict) when the program
is rejected. The validation verdict is exactly what an operator-in-the-loop
engine surfaces before approving a state. Never bypass it. The runtime then
re-validates with the same manifest, envelope and policy before its first
adapter call.

## Pinned constraints

A goal can carry its own manifest, envelope and ``no_policy`` flag. The
client sending goals may be an AI agent, so a deployment pins the constraints
instead (``PinnedConstraints``): the server validates every goal against the
pinned manifest, envelope and policy, and refuses a goal that tries to set any
of them before any provider or adapter call.

Rulebooks (RFC-0702, Draft) come from the operator only. A goal has no field
for them: a deployment rulebook can carry exceptions, so an agent that could
supply one could grant itself a waiver. The pinned constraints carry the
operator's rulebooks and the switch for the bundled ones; an unpinned server
applies the bundled rulebooks and nothing else.

## Natural language

The NL path is provider-agnostic per CLAUDE.md: ``execute_request`` takes an
``LLMProvider`` (never a hard-coded vendor) and builds a ``Bridge`` per request.
The program path is fully offline; the NL path requires a provider to be
configured, exactly like ``urml translate``.

## Evidence log

The ``evidence_log`` node parameter (a file path; empty, the default, turns it
off) makes the server append one validation record per verdict: the bridge's
verdict for a sentence and the validator's verdict for every goal, accepted or
refused, and the runtime's own refusals. It is operator configuration, like
the pins; a goal cannot set it. See ``docs/evidence/validation-records.md``.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError as PydanticValidationError
from urml_validator import ValidationResult, validate
from urml_validator.evidence import Stage, append_record, build_record
from urml_validator.schemas.policy import Policy
from urml_validator.schemas.rulebook import Rulebook

from urml_ros2_runtime.errors import ValidationRejectedError
from urml_ros2_runtime.runtime import RuntimeResult, URMLRuntime
from urml_ros2_runtime.substrate.base import ROSAdapter

# A feedback sink receives a phase event the server can forward as ROS 2
# action feedback. Phase is one of: "translating" | "validating" |
# "executing" | "done". ``detail`` is a short human-readable string.
FeedbackSink = Callable[[dict[str, Any]], None]

PolicyArg = dict[str, Any] | Policy | None | Literal["DEFAULT"]


class ExecuteRequest:
    """A normalized ``ExecuteURML`` goal, decoupled from ROS message types.

    Built from the action goal in the node, or directly in tests. Exactly one
    of ``program`` / ``sentence`` drives the run: a program is executed as-is;
    a sentence is translated first (requires a provider). ``manifest`` is
    None when the goal carries none, which is what a pinned server expects.
    """

    def __init__(
        self,
        *,
        manifest: dict[str, Any] | None = None,
        program: dict[str, Any] | None = None,
        sentence: str | None = None,
        envelope: dict[str, Any] | None = None,
        profiles: tuple[str, ...] = (),
        no_policy: bool = False,
    ) -> None:
        self.manifest = manifest
        self.program = program
        self.sentence = sentence
        self.envelope = envelope
        self.profiles = tuple(profiles)
        self.no_policy = no_policy


@dataclass(frozen=True)
class PinnedConstraints:
    """Deployment constraints fixed when the server starts.

    Every goal is validated against these, never against constraints the goal
    carries. ``policy`` has the ``validate()`` contract (``"DEFAULT"``, None
    for no compliance pass, or a policy mapping). ``manifest_base_dir`` is the
    pinned manifest file's directory, for RFC-0005 HBOM-content rules.
    ``rulebooks`` are the operator's rulebooks (RFC-0702, Draft) and
    ``default_rulebooks`` switches the bundled ones; a goal can set neither.
    """

    manifest: dict[str, Any]
    envelope: dict[str, Any] | None = None
    policy: PolicyArg = "DEFAULT"
    manifest_base_dir: Path | None = None
    rulebooks: tuple[dict[str, Any], ...] = ()
    default_rulebooks: bool = True


def _refused(reason: str) -> dict[str, Any]:
    """A serialized refusal result — no actuation happened."""
    return {
        "success": False,
        "refused": True,
        "reason": reason,
        "steps_executed": 0,
        "audit_log_json": "[]",
        "bindings_json": "{}",
    }


def _render_verdict(result: ValidationResult) -> str:
    """Compact, operator-facing rendering of a rejection verdict."""
    lines = [e.render() for e in result.errors]
    return "validation refused:\n" + "\n".join(lines) if lines else "validation refused"


def _serialize(result: RuntimeResult) -> dict[str, Any]:
    """Serialize a RuntimeResult into the action's flat, string-carrying shape."""
    return {
        "success": result.success,
        "refused": False,
        "reason": (result.last_outcome.reason or "") if result.last_outcome else "",
        "steps_executed": result.steps_executed,
        "audit_log_json": json.dumps(result.audit_log),
        "bindings_json": json.dumps(result.bindings),
    }


def execute_request(
    request: ExecuteRequest,
    *,
    adapter: ROSAdapter,
    provider: Any | None = None,
    feedback: FeedbackSink | None = None,
    pinned: PinnedConstraints | None = None,
    evidence_log: Path | str | None = None,
) -> dict[str, Any]:
    """Run one URML request through translate? -> validate -> execute.

    Returns a JSON-serializable result dict matching the ``ExecuteURML`` action
    result: ``success``, ``refused``, ``reason``, ``steps_executed``,
    ``audit_log_json``, ``bindings_json``. Never raises on a *validation*
    refusal (that is a normal, surfaced outcome); only unrecoverable substrate
    errors propagate, exactly as in the CLI ``execute`` path.

    Args:
        request:  The normalized goal.
        adapter:  The substrate to dispatch through (``MockROSAdapter`` in
                  tests / dry-run, ``RclpyAdapter`` on a real robot).
        provider: A provider-agnostic ``LLMProvider`` for the NL path. Required
                  iff ``request.sentence`` is set and ``request.program`` is not.
        feedback: Optional sink for phase events (forwarded as action feedback).
        pinned:   Deployment constraints fixed at server start. When set, the
                  goal is validated against these, and a goal that sets its own
                  manifest, envelope or ``no_policy`` is refused before any
                  provider or adapter call.
        evidence_log: Optional JSON Lines file (opt-in, local). Each verdict
                  this call makes, the bridge's for a sentence and the
                  validator's for the program, is appended as a validation
                  record, and the runtime appends its own refusals. A record
                  that cannot be written refuses the goal before anything
                  executes.
    """
    manifest: dict[str, Any]
    envelope: dict[str, Any] | None
    policy: PolicyArg
    manifest_base_dir: Path | None
    # Rulebooks come from the operator only (RFC-0702): the goal has no field
    # for them, and an unpinned server applies the bundled rulebooks.
    rulebooks: tuple[dict[str, Any], ...] = pinned.rulebooks if pinned is not None else ()
    default_rulebooks = pinned.default_rulebooks if pinned is not None else True
    if pinned is not None:
        carried = [
            name
            for name, is_set in (
                ("manifest_yaml", request.manifest is not None),
                ("envelope_yaml", request.envelope is not None),
                ("no_policy", request.no_policy),
            )
            if is_set
        ]
        if carried:
            return _refused(
                "this action server pins its manifest, envelope and policy; the goal "
                f"may not set {', '.join(carried)}. Send only the program or sentence "
                "and the profiles."
            )
        manifest = pinned.manifest
        envelope = pinned.envelope
        policy = pinned.policy
        manifest_base_dir = pinned.manifest_base_dir
    else:
        manifest = request.manifest or {}
        envelope = request.envelope
        policy = None if request.no_policy else "DEFAULT"
        manifest_base_dir = None

    def emit(phase: str, detail: str) -> None:
        if feedback is not None:
            feedback({"phase": phase, "detail": detail})

    log = Path(evidence_log) if evidence_log else None

    def record(
        stage: Stage,
        result: ValidationResult,
        program: dict[str, Any] | None,
        *,
        as_of: date | None = None,
        attempts: int | None = None,
        attempt_codes: list[list[str]] | None = None,
    ) -> str | None:
        """Append one verdict to the evidence log. Returns why it failed, else None."""
        if log is None:
            return None
        try:
            append_record(
                log,
                build_record(
                    surface="action_server",
                    stage=stage,
                    result=result,
                    program=program,
                    manifest=manifest,
                    envelope=envelope,
                    policy=policy,
                    rulebooks=rulebooks,
                    default_rulebooks=default_rulebooks,
                    as_of=as_of,
                    profiles=request.profiles,
                    request=request.sentence if stage == "bridge" else None,
                    attempts=attempts,
                    attempt_codes=attempt_codes,
                ),
            )
        except OSError as exc:
            return f"the evidence log {log} could not be written ({exc}); nothing was executed"
        return None

    # 1. Resolve the program: execute as-is, or translate a sentence first.
    program = request.program
    if program is None:
        if not request.sentence:
            return _refused("goal has neither a `program` nor a `sentence`")
        if provider is None:
            return _refused(
                "natural-language goal requires an LLM provider, but none is "
                "configured on the action server (set the `llm_provider` param)"
            )
        emit("translating", "translating natural language to URML")
        # Lazy import: the bridge package is an optional dependency of the
        # action server, only needed for the NL path.
        from urml_llm_bridge import Bridge  # type: ignore[import-not-found,unused-ignore]
        from urml_llm_bridge.errors import BridgeError  # type: ignore[import-not-found,unused-ignore]

        bridge = Bridge(
            provider=provider,
            manifest=manifest,
            envelope=envelope,
            profiles=request.profiles,
            policy=policy,
            rulebooks=rulebooks,
            default_rulebooks=default_rulebooks,
        )
        try:
            translated = bridge.translate(request.sentence)
        except BridgeError as exc:
            reason = f"translation failed: {exc}"
            # A refusal carries the bridge's final verdict. A provider error
            # carries none: nothing was judged, so nothing is recorded.
            last = getattr(exc, "last_result", None)
            if isinstance(last, ValidationResult):
                problem = record(
                    "bridge",
                    last,
                    getattr(exc, "last_program", None),
                    attempts=getattr(exc, "attempts", None),
                    attempt_codes=getattr(exc, "attempt_codes", None),
                )
                if problem is not None:
                    reason += f"\n{problem}"
            return _refused(reason)
        problem = record(
            "bridge",
            translated.last_validation,
            translated.program,
            attempts=translated.revision_count + 1,
            attempt_codes=list(translated.attempt_codes),
        )
        if problem is not None:
            return _refused(problem)
        program = translated.program

    assert program is not None  # resolved above or returned

    # 2. Validate before any actuation. This is the safety boundary; the
    #    verdict is what an operator-in-the-loop engine approves.
    emit("validating", "validating program against manifest + envelope")
    as_of = datetime.now(UTC).date()
    verdict = validate(
        program,
        manifest,
        envelope,
        profiles=request.profiles,
        policy=policy,
        manifest_base_dir=manifest_base_dir,
        rulebooks=rulebooks,
        default_rulebooks=default_rulebooks,
        as_of=as_of,
    )
    problem = record("validation", verdict, program, as_of=as_of)
    if not verdict.accepted:
        rendered = _render_verdict(verdict)
        return _refused(rendered if problem is None else f"{rendered}\n{problem}")
    if problem is not None:
        return _refused(problem)

    # 3. Execute. The runtime re-validates with the same manifest, envelope,
    #    policy and rulebooks before its first adapter call (defense in depth),
    #    and records a refusal of its own in the same evidence log.
    emit("executing", f"executing {len(program.get('behavior', {}).get('steps', []))} step(s)")
    runtime = URMLRuntime(adapter, evidence_log=log)
    try:
        result = runtime.execute(
            program,
            manifest,
            envelope,
            request.profiles,
            policy=policy,
            manifest_base_dir=manifest_base_dir,
            rulebooks=rulebooks,
            default_rulebooks=default_rulebooks,
            as_of=as_of,
        )
    except ValidationRejectedError as exc:
        rejected = exc.validation_result
        if isinstance(rejected, ValidationResult):
            return _refused(_render_verdict(rejected))
        return _refused(f"validation refused: {exc}")
    emit("done", "execution complete" if result.success else "execution finished with failure")
    return _serialize(result)


# ---------------------------------------------------------------------------
# rclpy shell — only constructible under a real ROS 2 environment
# ---------------------------------------------------------------------------


def _require_rclpy() -> Any:
    """Lazy-import rclpy with an actionable error (mirrors RclpyAdapter)."""
    try:
        import rclpy  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "rclpy is not installed. URMLActionServerNode requires a ROS 2 "
            "environment.\n"
            "  On Linux: install ROS 2 and source /opt/ros/<distro>/setup.bash, "
            "then build the urml_ros2_msgs action package (colcon).\n"
            "  On Windows / for development: use execute_request() directly with "
            "MockROSAdapter (no ROS 2 needed)."
        ) from exc
    return rclpy


def _yaml_or_none(text: str) -> dict[str, Any] | None:
    """Parse a YAML/JSON string goal field; empty string -> None."""
    if not text or not text.strip():
        return None
    import yaml

    parsed = yaml.safe_load(text)
    return parsed if isinstance(parsed, dict) else None


def _goal_constraint(text: str) -> dict[str, Any] | None:
    """A goal's manifest or envelope field: None when blank, else its mapping.

    A non-blank field that is not a YAML mapping becomes an empty mapping, so
    it still counts as set: a pinned server refuses it, and an unpinned
    server's validator rejects it.
    """
    if not text or not text.strip():
        return None
    return _yaml_or_none(text) or {}


def request_from_goal(goal: Any) -> ExecuteRequest:
    """Normalize an ``ExecuteURML`` goal (or any object with its fields)."""
    return ExecuteRequest(
        manifest=_goal_constraint(goal.manifest_yaml),
        program=_yaml_or_none(goal.program_yaml),
        sentence=goal.sentence or None,
        envelope=_goal_constraint(goal.envelope_yaml),
        profiles=tuple(goal.profiles),
        no_policy=bool(goal.no_policy),
    )


def _load_mapping(path: str, param: str) -> dict[str, Any]:
    """Load a YAML mapping named by a node parameter, or raise ValueError."""
    file = Path(path)
    if not file.is_file():
        raise ValueError(f"{param} not found: {path}")
    import yaml

    with file.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{param} {path} is not a YAML mapping")
    return data


def _load_rulebook(path: str) -> dict[str, Any]:
    """Load one pinned rulebook file and check it against the rulebook format."""
    data = _load_mapping(path, "rulebooks")
    try:
        Rulebook.model_validate(data)
    except PydanticValidationError as exc:
        raise ValueError(
            f"rulebooks {path} does not follow the rulebook format: {exc.error_count()} problem(s)"
        ) from exc
    return data


def load_pinned(
    manifest_path: str,
    envelope_path: str,
    policy_path: str,
    rulebook_paths: Sequence[str] = (),
    default_rulebooks: bool = True,
) -> PinnedConstraints | None:
    """Build the server's pinned constraints from its node parameters.

    Returns None when ``manifest_path`` is empty: nothing is pinned and each
    goal carries its own constraints, which only the mock adapter allows.
    ``policy_path`` is empty for the bundled default policy, ``none`` to skip
    the compliance pass, or a policy file. ``rulebook_paths`` are the
    operator's rulebook files (RFC-0702, Draft), each checked against the
    rulebook format here, and ``default_rulebooks`` False switches off the
    bundled rulebooks. ``envelope_path``, ``policy_path`` and the rulebook
    settings pin nothing without ``manifest_path``, so setting any of them
    alone is a configuration error.
    """
    paths = [path for path in rulebook_paths if path]
    if not manifest_path:
        if envelope_path or policy_path or paths or not default_rulebooks:
            raise ValueError(
                "envelope_path, policy_path, rulebooks and default_rulebooks are pinned "
                "together with manifest_path; set manifest_path as well."
            )
        return None
    policy: PolicyArg
    if not policy_path:
        policy = "DEFAULT"
    elif policy_path == "none":
        policy = None
    else:
        policy = _load_mapping(policy_path, "policy_path")
    return PinnedConstraints(
        manifest=_load_mapping(manifest_path, "manifest_path"),
        envelope=_load_mapping(envelope_path, "envelope_path") if envelope_path else None,
        policy=policy,
        manifest_base_dir=Path(manifest_path).parent,
        rulebooks=tuple(_load_rulebook(path) for path in paths),
        default_rulebooks=default_rulebooks,
    )


def evidence_log_path(value: str) -> Path | None:
    """The ``evidence_log`` node parameter as a path. Blank leaves the log off."""
    text = value.strip()
    return Path(text).expanduser() if text else None


def require_pinned_for_adapter(adapter_kind: str, pinned: PinnedConstraints | None) -> None:
    """Refuse to start a real-adapter server whose goals could pick their own limits.

    The mock adapter moves nothing, so it may run unpinned. Any other adapter
    drives a robot and needs a pinned manifest and envelope.
    """
    if adapter_kind == "mock":
        return
    missing: list[str] = []
    if pinned is None:
        missing = ["manifest_path", "envelope_path"]
    elif pinned.envelope is None:
        missing = ["envelope_path"]
    if missing:
        raise RuntimeError(
            f"the {adapter_kind!r} adapter drives a real robot, so the action server "
            f"will not start without pinned constraints: set {' and '.join(missing)}. "
            "Goals then cannot choose their own manifest, envelope or policy."
        )


def main(args: list[str] | None = None) -> None:
    """Console entry point: spin a URML ``ExecuteURML`` action server.

    Node parameters:
        adapter        "mock" (default) | "ros2" — substrate backing.
        llm_provider   "none" (default) | "echo" | "anthropic" | "openai".
        ros2_namespace optional namespace forwarded to RclpyAdapter.
        manifest_path  capability manifest file to pin. When set, goals may
                       not carry manifest_yaml, envelope_yaml or no_policy.
        envelope_path  safety envelope file to pin (needs manifest_path).
        policy_path    "" (default) for the bundled policy, "none" to skip
                       the compliance pass, or a policy file (needs
                       manifest_path).
        rulebooks      string array of rulebook files to pin (RFC-0702,
                       Draft; needs manifest_path). Empty entries are ignored.
        default_rulebooks  bool, default true. False switches off the bundled
                       rulebooks (needs manifest_path).
        evidence_log   "" (default, off) or a JSON Lines file that receives
                       one validation record per verdict. Works with or
                       without pinned constraints.

    With any adapter other than "mock", the server will not start unless
    manifest_path and envelope_path are both set. Goals can never set the
    rulebooks, the default switch or the evidence log.
    """
    rclpy = _require_rclpy()
    from rclpy.action import ActionServer  # type: ignore[import-not-found,unused-ignore]
    from rclpy.node import Node  # type: ignore[import-not-found,unused-ignore]
    from urml_ros2_msgs.action import ExecuteURML  # type: ignore[import-not-found,unused-ignore]

    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig
    from urml_ros2_runtime.substrate.mock import MockROSAdapter

    class URMLActionServerNode(Node):  # type: ignore[misc]
        """ROS 2 node serving the ``ExecuteURML`` action."""

        def __init__(self) -> None:
            super().__init__("urml_action_server")
            self.declare_parameter("adapter", "mock")
            self.declare_parameter("llm_provider", "none")
            self.declare_parameter("ros2_namespace", "")
            self.declare_parameter("manifest_path", "")
            self.declare_parameter("envelope_path", "")
            self.declare_parameter("policy_path", "")
            # A one-empty-string default declares a string array; empty
            # entries are ignored when the pins load.
            self.declare_parameter("rulebooks", [""])
            self.declare_parameter("default_rulebooks", True)
            self.declare_parameter("evidence_log", "")
            # Pinned once, before the server accepts any goal.
            self._pinned = load_pinned(
                self._string_param("manifest_path"),
                self._string_param("envelope_path"),
                self._string_param("policy_path"),
                list(self.get_parameter("rulebooks").get_parameter_value().string_array_value),
                bool(self.get_parameter("default_rulebooks").get_parameter_value().bool_value),
            )
            require_pinned_for_adapter(self._string_param("adapter"), self._pinned)
            self._evidence_log = evidence_log_path(self._string_param("evidence_log"))
            self._action_server = ActionServer(
                self,
                ExecuteURML,
                "execute_urml",
                self._on_goal,
            )
            self.get_logger().info(
                "URML ExecuteURML action server ready"
                + (" (constraints pinned)." if self._pinned is not None else ".")
                + (f" Evidence log: {self._evidence_log}." if self._evidence_log is not None else "")
            )

        def _string_param(self, name: str) -> str:
            return str(self.get_parameter(name).get_parameter_value().string_value)

        def _build_adapter(self) -> ROSAdapter:
            kind = self.get_parameter("adapter").get_parameter_value().string_value
            if kind == "ros2":
                from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

                ns = self.get_parameter("ros2_namespace").get_parameter_value().string_value
                return RclpyAdapter(AdapterConfig(ros2_namespace=ns or None))
            return MockROSAdapter()

        def _build_provider(self) -> Any | None:
            name = self.get_parameter("llm_provider").get_parameter_value().string_value
            if name in ("", "none"):
                return None
            # Provider-agnostic per CLAUDE.md: construct by name, never hard-wire
            # a single vendor. Mirrors the CLI's `_build_provider` dispatch.
            if name == "anthropic":
                from urml_llm_bridge.providers.anthropic import (  # type: ignore[import-not-found,unused-ignore]
                    AnthropicProvider,
                )

                return AnthropicProvider()
            if name == "openai":
                from urml_llm_bridge.providers.openai import (  # type: ignore[import-not-found,unused-ignore]
                    OpenAIProvider,
                )

                return OpenAIProvider()
            raise RuntimeError(
                f"unsupported llm_provider {name!r}; use 'none', 'anthropic', or 'openai'"
            )

        def _on_goal(self, goal_handle: Any) -> Any:
            req = request_from_goal(goal_handle.request)

            def feedback(event: dict[str, Any]) -> None:
                fb = ExecuteURML.Feedback()
                fb.phase = str(event.get("phase", ""))
                fb.detail = str(event.get("detail", ""))
                goal_handle.publish_feedback(fb)

            adapter = self._build_adapter()
            try:
                out = execute_request(
                    req,
                    adapter=adapter,
                    provider=self._build_provider(),
                    feedback=feedback,
                    pinned=self._pinned,
                    evidence_log=self._evidence_log,
                )
            finally:
                close = getattr(adapter, "close", None)
                if callable(close):
                    close()

            result = ExecuteURML.Result()
            result.success = bool(out["success"])
            result.refused = bool(out["refused"])
            result.reason = str(out["reason"])
            result.steps_executed = int(out["steps_executed"])
            result.audit_log_json = str(out["audit_log_json"])
            result.bindings_json = str(out["bindings_json"])
            if out["refused"]:
                goal_handle.abort()
            elif out["success"]:
                goal_handle.succeed()
            else:
                goal_handle.abort()
            return result

    rclpy.init(args=args)
    try:
        node = URMLActionServerNode()
    except (RuntimeError, ValueError) as exc:
        # Unpinned real adapter or a bad pinned file: refuse to start.
        rclpy.shutdown()
        raise SystemExit(f"urml-ros2-action-server: {exc}") from exc
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
