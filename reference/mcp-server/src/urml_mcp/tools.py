"""Pure tool logic for the URML MCP server.

Each function returns a JSON-serializable dict and takes either a parsed mapping
or a path to a YAML file, so it works both from MCP clients (which pass JSON
objects) and from a shell. No MCP dependency lives here, so this module is
hermetically testable on its own.

The operator can pin the manifest, envelope, profiles and policy when the
server starts (``load_pinned``). Every tool takes those pins as ``pinned=``: a
pinned value is used on every call, and an agent value that differs from it is
refused with ``PermissionError`` before any runtime or adapter is built. The
agent proposes the program; the operator's rules decide whether it runs.

Rulebooks (RFC-0702, Draft) are operator configuration only. No tool takes a
rulebook or the switch for the bundled rulebooks as an argument: a deployment
rulebook can carry exceptions, so an agent that could supply one could grant
itself a waiver. The operator sets them with ``URML_MCP_RULEBOOKS`` and
``URML_MCP_DEFAULT_RULEBOOKS`` (or the matching flags), and every validation,
including the runtime's re-validation, uses them.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from urml_llm_bridge import build_system_prompt
from urml_llm_bridge.few_shot import few_shots_for
from urml_validator import Policy, ValidationResult, validate
from urml_validator.schema_export import export_schema
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.schemas.rulebook import Rulebook

#: Profiles the bridge ships few-shot libraries for.
AVAILABLE_PROFILES: tuple[str, ...] = ("home", "industrial", "drone", "educational", "fleet")

_PROFILE_BLURB = {
    "home": "household / service robots (the default core vocabulary)",
    "industrial": "industrial arms and cobots (pick_from / place_at / swap_tool)",
    "drone": "aerial vehicles (take_off / land / hover)",
    "educational": "classroom robots (relative drive / turn)",
    "fleet": "multi-robot programs (roster + on: + barrier)",
}

#: Env var that must be truthy before a real adapter (ros2, px4, ardupilot) can run.
_REAL_EXECUTE_ENV = "URML_MCP_ALLOW_REAL_EXECUTE"
#: Optional path to an adapter-config YAML for the real adapters.
_ADAPTER_CONFIG_ENV = "URML_MCP_ADAPTER_CONFIG"

#: Env vars the operator pins constraints with. The matching flag wins.
_MANIFEST_ENV = "URML_MCP_MANIFEST"
_ENVELOPE_ENV = "URML_MCP_ENVELOPE"
_PROFILES_ENV = "URML_MCP_PROFILES"
_POLICY_ENV = "URML_MCP_POLICY"
#: RFC-0702 (Draft): rulebook files, separated by ``os.pathsep``.
_RULEBOOKS_ENV = "URML_MCP_RULEBOOKS"
#: RFC-0702 (Draft): ``on`` (default) or ``off`` for the bundled rulebooks.
_DEFAULT_RULEBOOKS_ENV = "URML_MCP_DEFAULT_RULEBOOKS"

#: Every adapter ``execute_program`` accepts. All but ``mock`` drive hardware.
_ADAPTERS: tuple[str, ...] = ("mock", "ros2", "px4", "ardupilot")

#: How many validator errors a rejection message quotes.
_MAX_ERRORS_SHOWN = 5


@dataclass(frozen=True)
class Pinned:
    """Constraints the operator pinned when the server started.

    A field left as ``None`` is not pinned: the agent supplies that value as
    before. A pinned value is used on every tool call, and an agent value that
    differs from it is refused. ``policy`` is ``"DEFAULT"`` (the bundled
    US-federal policy), ``"none"`` (no compliance pass), or a policy mapping.

    ``rulebooks`` and ``default_rulebooks`` (RFC-0702, Draft) are never agent
    values: no tool has an argument for them. With nothing set, every call
    applies the bundled rulebooks and nothing else.
    """

    manifest: dict[str, Any] | None = None
    manifest_path: Path | None = None
    envelope: dict[str, Any] | None = None
    envelope_path: Path | None = None
    profiles: tuple[str, ...] | None = None
    policy: str | dict[str, Any] | None = None
    policy_path: Path | None = None
    rulebooks: tuple[dict[str, Any], ...] = ()
    rulebook_paths: tuple[Path, ...] = ()
    default_rulebooks: bool = True

    @property
    def names(self) -> tuple[str, ...]:
        """The pinned constraints, in a fixed order."""
        values: tuple[tuple[str, object], ...] = (
            ("manifest", self.manifest),
            ("envelope", self.envelope),
            ("profiles", self.profiles),
            ("policy", self.policy),
            ("rulebooks", self.rulebooks or None),
            ("default_rulebooks", None if self.default_rulebooks else False),
        )
        return tuple(name for name, value in values if value is not None)


class PinnedConfigError(ValueError):
    """A pinned constraint did not load, so the server must not start."""


def _as_dict(value: Any, *, kind: str) -> dict[str, Any]:
    """Accept a parsed mapping or a path to a YAML file; return a dict."""
    if isinstance(value, dict):
        return value
    if isinstance(value, (str, Path)):
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(f"{kind} path not found: {value}")
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError(f"{kind} file {path} is not a YAML mapping")
        return data
    raise TypeError(f"{kind} must be a mapping or a file path, got {type(value).__name__}")


def _profiles_tuple(profiles: Any) -> tuple[str, ...]:
    """Normalize None / list / tuple / comma-string into a tuple of names."""
    if profiles is None:
        return ()
    if isinstance(profiles, str):
        return tuple(p.strip() for p in profiles.split(",") if p.strip())
    if isinstance(profiles, (list, tuple)):
        return tuple(str(p).strip() for p in profiles if str(p).strip())
    raise TypeError(f"profiles must be a list, tuple, comma-string, or null, got {type(profiles).__name__}")


def _real_execute_allowed() -> bool:
    return os.environ.get(_REAL_EXECUTE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


# --- Operator pins ------------------------------------------------------------


def _arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urml-mcp",
        description=(
            "Serve the URML tools over stdio. Each flag pins one constraint for every "
            "tool call and wins over the matching URML_MCP_* env var."
        ),
    )
    parser.add_argument("--manifest", metavar="PATH", help=f"robot capability manifest YAML ({_MANIFEST_ENV})")
    parser.add_argument("--envelope", metavar="PATH", help=f"site safety envelope YAML ({_ENVELOPE_ENV})")
    parser.add_argument(
        "--profiles",
        metavar="LIST",
        help=f"comma-separated profiles, for example home or drone,fleet ({_PROFILES_ENV})",
    )
    parser.add_argument(
        "--policy",
        metavar="PATH|DEFAULT|none",
        help=f"compliance policy YAML, DEFAULT for the bundled US-federal policy, or none ({_POLICY_ENV})",
    )
    parser.add_argument(
        "--rulebooks",
        metavar="PATHS",
        help=(
            f"rulebook YAML files separated by {os.pathsep!r}, applied after the bundled "
            f"rulebooks ({_RULEBOOKS_ENV})"
        ),
    )
    parser.add_argument(
        "--default-rulebooks",
        metavar="on|off",
        help=f"off switches off the bundled rulebooks; on is the default ({_DEFAULT_RULEBOOKS_ENV})",
    )
    return parser


def _pick(flag_value: str | None, flag: str, environ: Mapping[str, str], env_var: str) -> tuple[str, str] | None:
    """Return ``(value, source)`` for one pin. The flag wins; a blank value pins nothing."""
    if flag_value is not None and flag_value.strip():
        return flag_value.strip(), flag
    env_value = environ.get(env_var, "").strip()
    if env_value:
        return env_value, env_var
    return None


def _load_pinned_file(raw: str, source: str, *, kind: str, schema: type[BaseModel]) -> tuple[dict[str, Any], Path]:
    """Load one pinned YAML file and check it against its schema."""
    path = Path(raw).expanduser().resolve()
    try:
        data = _as_dict(path, kind=kind)
        schema.model_validate(data)
    except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
        raise PinnedConfigError(f"{source}: the pinned {kind} {path} did not load: {exc}") from exc
    return data, path


def load_pinned(environ: Mapping[str, str], argv: Sequence[str]) -> Pinned:
    """Read the operator's pinned constraints from flags and ``URML_MCP_*`` env vars.

    ``--manifest`` / ``URML_MCP_MANIFEST`` and ``--envelope`` /
    ``URML_MCP_ENVELOPE`` take a YAML path. ``--profiles`` /
    ``URML_MCP_PROFILES`` take comma-separated names. ``--policy`` /
    ``URML_MCP_POLICY`` take a policy YAML path, ``DEFAULT`` for the bundled
    US-federal policy, or ``none`` for no compliance pass. ``--rulebooks`` /
    ``URML_MCP_RULEBOOKS`` take rulebook YAML paths separated by
    ``os.pathsep``, and ``--default-rulebooks`` / ``URML_MCP_DEFAULT_RULEBOOKS``
    take ``on`` or ``off`` (RFC-0702, Draft). A flag wins over its env var,
    and a blank value pins nothing.

    Each pinned file is read once, here, and checked against its schema, so a
    bad pin stops the server at startup instead of failing every call. Raises
    ``PinnedConfigError`` naming the flag or env var at fault. An unknown flag
    exits with argparse's usage message.
    """
    args = _arg_parser().parse_args(list(argv))

    manifest: dict[str, Any] | None = None
    manifest_path: Path | None = None
    picked = _pick(args.manifest, "--manifest", environ, _MANIFEST_ENV)
    if picked is not None:
        manifest, manifest_path = _load_pinned_file(*picked, kind="manifest", schema=CapabilityManifest)

    envelope: dict[str, Any] | None = None
    envelope_path: Path | None = None
    picked = _pick(args.envelope, "--envelope", environ, _ENVELOPE_ENV)
    if picked is not None:
        envelope, envelope_path = _load_pinned_file(*picked, kind="envelope", schema=SafetyEnvelope)

    profiles: tuple[str, ...] | None = None
    picked = _pick(args.profiles, "--profiles", environ, _PROFILES_ENV)
    if picked is not None:
        raw, source = picked
        profiles = _profiles_tuple(raw)
        if not profiles:
            raise PinnedConfigError(f"{source}: no profile names in {raw!r}")

    policy: str | dict[str, Any] | None = None
    policy_path: Path | None = None
    picked = _pick(args.policy, "--policy", environ, _POLICY_ENV)
    if picked is not None:
        raw, source = picked
        if raw.lower() == "none":
            policy = "none"
        elif raw.lower() == "default":
            policy = "DEFAULT"
        else:
            policy, policy_path = _load_pinned_file(raw, source, kind="policy", schema=Policy)

    rulebooks: list[dict[str, Any]] = []
    rulebook_paths: list[Path] = []
    picked = _pick(args.rulebooks, "--rulebooks", environ, _RULEBOOKS_ENV)
    if picked is not None:
        raw, source = picked
        for entry in (part.strip() for part in raw.split(os.pathsep)):
            if entry:
                data, path = _load_pinned_file(entry, source, kind="rulebook", schema=Rulebook)
                rulebooks.append(data)
                rulebook_paths.append(path)

    default_rulebooks = True
    picked = _pick(args.default_rulebooks, "--default-rulebooks", environ, _DEFAULT_RULEBOOKS_ENV)
    if picked is not None:
        raw, source = picked
        if raw.lower() not in {"on", "off"}:
            raise PinnedConfigError(f"{source}: expected on or off, got {raw!r}")
        default_rulebooks = raw.lower() == "on"

    return Pinned(
        manifest=manifest,
        manifest_path=manifest_path,
        envelope=envelope,
        envelope_path=envelope_path,
        profiles=profiles,
        policy=policy,
        policy_path=policy_path,
        rulebooks=tuple(rulebooks),
        rulebook_paths=tuple(rulebook_paths),
        default_rulebooks=default_rulebooks,
    )


def _canonical(value: Any) -> Any:
    """``value`` as it round-trips through JSON, so YAML and JSON copies compare equal."""
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _refusal(name: str, env_var: str) -> PermissionError:
    return PermissionError(
        f"the operator pinned the {name} for this server ({env_var}), and the {name} argument "
        f"does not match it. Omit the {name} argument; the server uses the pinned value on every call."
    )


def _resolve_mapping(agent: Any, pinned: dict[str, Any] | None, *, name: str, env_var: str) -> dict[str, Any] | None:
    """The pinned mapping when there is one, else the agent's. A differing agent value is refused."""
    if pinned is None:
        return None if agent is None else _as_dict(agent, kind=name)
    if agent is not None and _canonical(_as_dict(agent, kind=name)) != _canonical(pinned):
        raise _refusal(name, env_var)
    return copy.deepcopy(pinned)


def _resolve_manifest(agent: Any, pins: Pinned) -> dict[str, Any]:
    manifest = _resolve_mapping(agent, pins.manifest, name="manifest", env_var=_MANIFEST_ENV)
    if manifest is None:
        raise ValueError(
            f"a manifest is required: pass one, or have the operator pin it with {_MANIFEST_ENV} or --manifest"
        )
    return manifest


def _resolve_profiles(agent: Any, pinned: tuple[str, ...] | None) -> tuple[str, ...]:
    if pinned is None:
        return _profiles_tuple(agent)
    if agent is not None and set(_profiles_tuple(agent)) != set(pinned):
        raise _refusal("profiles", _PROFILES_ENV)
    return pinned


def _normalize_policy(value: str | dict[str, Any]) -> str | dict[str, Any]:
    """Fold the accepted policy spellings into ``"DEFAULT"``, ``"none"``, or a mapping."""
    if isinstance(value, dict):
        return value
    literal = value.strip().lower()
    if literal == "none":
        return "none"
    if literal == "default":
        return "DEFAULT"
    raise ValueError(f"policy must be 'DEFAULT', 'none', or a policy mapping, got {value!r}")


def _resolve_policy(agent: str | dict[str, Any] | None, pinned: str | dict[str, Any] | None) -> str | dict[str, Any]:
    if pinned is None:
        return "DEFAULT" if agent is None else _normalize_policy(agent)
    if agent is not None and _canonical(_normalize_policy(agent)) != _canonical(pinned):
        raise _refusal("policy", _POLICY_ENV)
    return copy.deepcopy(pinned)


def _policy_arg(policy: str | dict[str, Any]) -> dict[str, Any] | Literal["DEFAULT"] | None:
    """Map a resolved policy onto ``validate()``'s ``policy`` argument."""
    if isinstance(policy, dict):
        return policy
    return None if policy == "none" else "DEFAULT"


def _manifest_base_dir(pins: Pinned) -> Path | None:
    """The pinned manifest's directory, for relative HBOM references, as the CLI resolves them."""
    return pins.manifest_path.parent if pins.manifest_path is not None else None


def _rulebooks(pins: Pinned) -> list[dict[str, Any]]:
    """Fresh copies of the operator's rulebooks for one validation (RFC-0702)."""
    return [copy.deepcopy(book) for book in pins.rulebooks]


def _require_real_adapter_pins(adapter: str, pins: Pinned) -> None:
    """Refuse a real adapter unless the operator opted in and pinned the manifest and envelope."""
    missing: list[str] = []
    if not _real_execute_allowed():
        missing.append(f"{_REAL_EXECUTE_ENV}=1")
    if pins.manifest is None:
        missing.append(f"{_MANIFEST_ENV} (or --manifest)")
    if pins.envelope is None:
        missing.append(f"{_ENVELOPE_ENV} (or --envelope)")
    if missing:
        raise PermissionError(
            f"the {adapter!r} adapter actuates real hardware and is disabled until the operator "
            f"sets {', '.join(missing)} when starting the server. A real adapter runs only against "
            f"the operator's pinned manifest and envelope, never against ones the agent passes. "
            f"Use adapter='mock' for a hermetic run."
        )


def _rejection_message(result: ValidationResult) -> str:
    shown = [f"{err.code}: {err.message}" for err in result.errors[:_MAX_ERRORS_SHOWN]]
    extra = len(result.errors) - len(shown)
    more = f" (and {extra} more)" if extra > 0 else ""
    return (
        "the validator rejected the program, so no runtime or adapter was built. "
        + "; ".join(shown)
        + more
    )


# --- Tools --------------------------------------------------------------------


def get_contract(
    manifest: dict[str, Any] | str | None = None,
    profiles: Any = None,
    envelope: dict[str, Any] | str | None = None,
    *,
    pinned: Pinned | None = None,
) -> dict[str, Any]:
    """Return the Layer-4 contract an agent emits URML against.

    This is the read-only first step: the agent calls it to learn the target
    (the system prompt plus the URML program JSON Schema), emits a program
    itself, then calls ``validate``. The server never calls an LLM. Pinned
    values stand in for omitted arguments; ``pinned`` in the result names them
    so the agent knows what to leave out.
    """
    pins = pinned if pinned is not None else Pinned()
    manifest_d = _resolve_manifest(manifest, pins)
    envelope_d = _resolve_mapping(envelope, pins.envelope, name="envelope", env_var=_ENVELOPE_ENV)
    prof = _resolve_profiles(profiles, pins.profiles)
    schema = export_schema("program")
    prompt = build_system_prompt(
        schema=schema,
        manifest=manifest_d,
        envelope=envelope_d,
        profiles=prof,
        few_shots=few_shots_for(prof),
    )
    return {
        "system_prompt": prompt,
        "program_schema": schema,
        "profiles": list(prof),
        "pinned": list(pins.names),
    }


def validate_program(
    program: dict[str, Any] | str,
    manifest: dict[str, Any] | str | None = None,
    envelope: dict[str, Any] | str | None = None,
    profiles: Any = None,
    policy: str | dict[str, Any] | None = None,
    *,
    pinned: Pinned | None = None,
) -> dict[str, Any]:
    """Validate a URML program. This is the safety check, and it is read-only.

    ``policy`` is ``"DEFAULT"`` (the bundled US-federal compliance policy),
    ``"none"`` to skip compliance, or a policy mapping. Omitted, it is the
    operator's pinned policy, else ``"DEFAULT"``. Returns the
    ``ValidationResult`` as a dict: ``accepted`` plus structured ``errors`` and
    ``warnings`` (each ``{code, severity, primitive, path, field, message,
    suggestion, detail}``).
    """
    pins = pinned if pinned is not None else Pinned()
    manifest_d = _resolve_manifest(manifest, pins)
    envelope_d = _resolve_mapping(envelope, pins.envelope, name="envelope", env_var=_ENVELOPE_ENV)
    prof = _resolve_profiles(profiles, pins.profiles)
    resolved_policy = _resolve_policy(policy, pins.policy)
    program_d = _as_dict(program, kind="program")

    result = validate(
        program_d,
        manifest_d,
        envelope=envelope_d,
        profiles=prof,
        policy=_policy_arg(resolved_policy),
        manifest_base_dir=_manifest_base_dir(pins),
        rulebooks=_rulebooks(pins),
        default_rulebooks=pins.default_rulebooks,
    )
    return result.model_dump(mode="json")


def execute_program(
    program: dict[str, Any] | str,
    manifest: dict[str, Any] | str | None = None,
    envelope: dict[str, Any] | str | None = None,
    profiles: Any = None,
    adapter: str = "mock",
    *,
    pinned: Pinned | None = None,
) -> dict[str, Any]:
    """Execute a validated URML program against a substrate adapter.

    ``adapter`` is ``"mock"`` (default, hermetic, touches no hardware),
    ``"ros2"``, ``"px4"``, or ``"ardupilot"``. The real adapters need their
    runtime, the ``URML_MCP_ALLOW_REAL_EXECUTE`` opt-in, and a manifest and an
    envelope pinned by the operator: the agent's own manifest or envelope never
    unlocks them. On a real adapter the agent does not pick the profiles
    either; unpinned, they are empty.

    The program is validated against the operator's values (and the pinned
    policy, else the bundled one) before any runtime or adapter is built, and
    the runtime re-validates before running (defense in depth). There is no
    path that reaches an actuator without the validator. Returns the
    ``RuntimeResult`` as a dict. Raises ``ValidationRejectedError`` when the
    validator rejects the program.
    """
    pins = pinned if pinned is not None else Pinned()
    if adapter not in _ADAPTERS:
        raise ValueError(f"unknown adapter: {adapter!r} (expected 'mock', 'ros2', 'px4', or 'ardupilot')")
    if adapter != "mock":
        _require_real_adapter_pins(adapter, pins)
        if pins.profiles is None and _profiles_tuple(profiles):
            raise PermissionError(
                f"the {adapter!r} adapter actuates real hardware, so the operator sets the profiles: "
                f"pin them with {_PROFILES_ENV} or --profiles, or omit the profiles argument."
            )

    manifest_d = _resolve_manifest(manifest, pins)
    envelope_d = _resolve_mapping(envelope, pins.envelope, name="envelope", env_var=_ENVELOPE_ENV)
    prof = _resolve_profiles(profiles, pins.profiles)
    policy = _resolve_policy(None, pins.policy)
    program_d = _as_dict(program, kind="program")

    # Validate before anything is built: a rejected program never gets a
    # runtime or an adapter. This pass also applies a pinned policy, which the
    # runtime's own re-validation below does not take. The runtime does take
    # the operator's rulebooks and the same validation date (RFC-0702).
    as_of = datetime.now(UTC).date()
    check = validate(
        program_d,
        manifest_d,
        envelope=envelope_d,
        profiles=prof,
        policy=_policy_arg(policy),
        manifest_base_dir=_manifest_base_dir(pins),
        rulebooks=_rulebooks(pins),
        default_rulebooks=pins.default_rulebooks,
        as_of=as_of,
    )
    if not check.accepted:
        from urml_ros2_runtime import ValidationRejectedError  # local import: keeps tools import light

        raise ValidationRejectedError(_rejection_message(check), validation_result=check)

    runtime, cleanup = _build_runtime(adapter)
    try:
        result = runtime.execute(
            program_d,
            manifest_d,
            envelope=envelope_d,
            profiles=prof,
            rulebooks=_rulebooks(pins),
            default_rulebooks=pins.default_rulebooks,
            as_of=as_of,
        )
        out: dict[str, Any] = result.model_dump(mode="json")
        return out
    finally:
        for close in cleanup:
            try:
                close()
            except Exception:  # noqa: BLE001 - best-effort teardown, never mask the result
                pass


def _build_runtime(adapter: str) -> tuple[Any, list[Any]]:
    """Construct (runtime, cleanup-callables) for the chosen adapter.

    Mirrors the CLI's adapter selection. ``mock`` is always available;
    ``ros2``, ``px4`` and ``ardupilot`` are gated behind
    ``URML_MCP_ALLOW_REAL_EXECUTE`` and their respective runtime dependencies.
    ``execute_program`` also requires the operator's pinned manifest and
    envelope before it gets here.
    """
    from urml_ros2_runtime import URMLRuntime  # local import: keeps tools import light

    cleanup: list[Any] = []

    if adapter == "mock":
        from urml_ros2_runtime import MockROSAdapter

        return URMLRuntime(MockROSAdapter()), cleanup

    if adapter not in {"ros2", "px4", "ardupilot"}:
        raise ValueError(f"unknown adapter: {adapter!r} (expected 'mock', 'ros2', 'px4', or 'ardupilot')")

    if not _real_execute_allowed():
        raise PermissionError(
            f"the {adapter!r} adapter actuates real hardware and is disabled by default. "
            f"Set {_REAL_EXECUTE_ENV}=1 to enable it; otherwise use adapter='mock' for a "
            f"hermetic run."
        )

    config_path = os.environ.get(_ADAPTER_CONFIG_ENV)

    if adapter == "ros2":
        try:
            import rclpy  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "the ros2 adapter requires a ROS 2 environment (rclpy is not importable). "
                "Source a ROS 2 install, or use adapter='mock'."
            ) from exc
        from urml_ros2_runtime import RclpyAdapter, load_adapter_config

        config = load_adapter_config(Path(config_path)) if config_path else None
        rclpy.init()
        cleanup.append(rclpy.shutdown)
        ros_adapter = RclpyAdapter(config)
        cleanup.append(ros_adapter.close)
        return URMLRuntime(ros_adapter), cleanup

    if adapter == "ardupilot":
        try:
            from urml_ardupilot_runtime import (  # type: ignore[import-not-found,import-untyped,unused-ignore]
                ArduCopterAdapter,
                load_ardupilot_config,
            )
        except ImportError as exc:
            raise RuntimeError(
                "the ardupilot adapter requires urml-ardupilot-runtime "
                "(pip install urml-ardupilot-runtime[ardupilot]), plus a reachable ArduCopter SITL/autopilot."
            ) from exc

        ap_config = load_ardupilot_config(Path(config_path)) if config_path else None
        ap_adapter = ArduCopterAdapter(ap_config)
        ap_close = getattr(ap_adapter, "close", None)
        if callable(ap_close):
            cleanup.append(ap_close)
        return URMLRuntime(ap_adapter), cleanup

    # adapter == "px4"
    try:
        from urml_px4_runtime import (  # type: ignore[import-not-found,import-untyped,unused-ignore]
            PX4Adapter,
            load_px4_config,
        )
    except ImportError as exc:
        raise RuntimeError(
            "the px4 adapter requires urml-px4-runtime (pip install urml-px4-runtime), "
            "plus a reachable PX4 SITL/autopilot."
        ) from exc

    px4_config = load_px4_config(Path(config_path)) if config_path else None
    px4_adapter = PX4Adapter(px4_config)
    close = getattr(px4_adapter, "close", None)
    if callable(close):
        cleanup.append(close)
    return URMLRuntime(px4_adapter), cleanup


def list_profiles() -> dict[str, Any]:
    """List the URML profiles available for ``get_contract`` and ``validate``."""
    return {"profiles": [{"name": p, "description": _PROFILE_BLURB.get(p, "")} for p in AVAILABLE_PROFILES]}


def describe_manifest(
    manifest: dict[str, Any] | str | None = None,
    *,
    pinned: Pinned | None = None,
) -> dict[str, Any]:
    """Return a compact, structural summary of a capability manifest.

    A convenience read-only view so an agent can reason about what a robot
    declares before emitting intent. Makes no schema assumptions: it reports the
    top-level keys and a shallow shape of each. Omitted, ``manifest`` is the
    operator's pinned manifest.
    """
    manifest_d = _resolve_manifest(manifest, pinned if pinned is not None else Pinned())
    summary: dict[str, Any] = {}
    for key, value in manifest_d.items():
        if isinstance(value, dict):
            summary[key] = {"keys": sorted(value.keys())}
        elif isinstance(value, list):
            summary[key] = {"count": len(value)}
        else:
            summary[key] = value
    return {"top_level_keys": sorted(manifest_d.keys()), "summary": summary}
