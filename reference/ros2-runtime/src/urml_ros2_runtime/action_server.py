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
engine surfaces before approving a state — never bypass it.

## Natural language

The NL path is provider-agnostic per CLAUDE.md: ``execute_request`` takes an
``LLMProvider`` (never a hard-coded vendor) and builds a ``Bridge`` per request.
The program path is fully offline; the NL path requires a provider to be
configured, exactly like ``urml translate``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Literal

from urml_validator import ValidationResult, validate
from urml_validator.schemas.policy import Policy

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
    a sentence is translated first (requires a provider).
    """

    def __init__(
        self,
        *,
        manifest: dict[str, Any],
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
    """
    policy: PolicyArg = None if request.no_policy else "DEFAULT"

    def emit(phase: str, detail: str) -> None:
        if feedback is not None:
            feedback({"phase": phase, "detail": detail})

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
            manifest=request.manifest,
            envelope=request.envelope,
            profiles=request.profiles,
            policy=policy,
        )
        try:
            translated = bridge.translate(request.sentence)
        except BridgeError as exc:
            return _refused(f"translation failed: {exc}")
        program = translated.program

    assert program is not None  # resolved above or returned

    # 2. Validate before any actuation. This is the safety boundary; the
    #    verdict is what an operator-in-the-loop engine approves.
    emit("validating", "validating program against manifest + envelope")
    verdict = validate(
        program,
        request.manifest,
        request.envelope,
        profiles=request.profiles,
        policy=policy,
    )
    if not verdict.accepted:
        return _refused(_render_verdict(verdict))

    # 3. Execute. The runtime is already-validated input, so skip its
    #    defense-in-depth re-validation pass (we just ran it here).
    emit("executing", f"executing {len(program.get('behavior', {}).get('steps', []))} step(s)")
    runtime = URMLRuntime(adapter, revalidate=False)
    result = runtime.execute(program, request.manifest, request.envelope, request.profiles)
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


def main(args: list[str] | None = None) -> None:
    """Console entry point: spin a URML ``ExecuteURML`` action server.

    Node parameters:
        adapter        "mock" (default) | "ros2" — substrate backing.
        llm_provider   "none" (default) | "echo" | "anthropic" | "openai".
        ros2_namespace optional namespace forwarded to RclpyAdapter.
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
            self._action_server = ActionServer(
                self,
                ExecuteURML,
                "execute_urml",
                self._on_goal,
            )
            self.get_logger().info("URML ExecuteURML action server ready.")

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
            g = goal_handle.request
            req = ExecuteRequest(
                manifest=_yaml_or_none(g.manifest_yaml) or {},
                program=_yaml_or_none(g.program_yaml),
                sentence=g.sentence or None,
                envelope=_yaml_or_none(g.envelope_yaml),
                profiles=tuple(g.profiles),
                no_policy=bool(g.no_policy),
            )

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
    node = URMLActionServerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
