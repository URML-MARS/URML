"""Pure tool logic for the URML MCP server.

Each function returns a JSON-serializable dict and takes either a parsed mapping
or a path to a YAML file, so it works both from MCP clients (which pass JSON
objects) and from a shell. No MCP dependency lives here, so this module is
hermetically testable on its own.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from urml_llm_bridge import build_system_prompt
from urml_llm_bridge.few_shot import few_shots_for
from urml_validator import validate
from urml_validator.schema_export import export_schema

#: Profiles the bridge ships few-shot libraries for.
AVAILABLE_PROFILES: tuple[str, ...] = ("home", "industrial", "drone", "educational", "fleet")

_PROFILE_BLURB = {
    "home": "household / service robots (the default core vocabulary)",
    "industrial": "industrial arms and cobots (pick_from / place_at / swap_tool)",
    "drone": "aerial vehicles (take_off / land / hover)",
    "educational": "classroom robots (relative drive / turn)",
    "fleet": "multi-robot programs (roster + on: + barrier)",
}

#: Env var that must be truthy before the ros2 / px4 adapters can run.
_REAL_EXECUTE_ENV = "URML_MCP_ALLOW_REAL_EXECUTE"
#: Optional path to an adapter-config YAML for the real adapters.
_ADAPTER_CONFIG_ENV = "URML_MCP_ADAPTER_CONFIG"


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


def get_contract(
    manifest: dict[str, Any] | str,
    profiles: Any = (),
    envelope: dict[str, Any] | str | None = None,
) -> dict[str, Any]:
    """Return the Layer-4 contract an agent emits URML against.

    This is the read-only first step: the agent calls it to learn the target
    (the system prompt plus the URML program JSON Schema), emits a program
    itself, then calls ``validate``. The server never calls an LLM.
    """
    manifest_d = _as_dict(manifest, kind="manifest")
    envelope_d = _as_dict(envelope, kind="envelope") if envelope is not None else None
    prof = _profiles_tuple(profiles)
    schema = export_schema("program")
    prompt = build_system_prompt(
        schema=schema,
        manifest=manifest_d,
        envelope=envelope_d,
        profiles=prof,
        few_shots=few_shots_for(prof),
    )
    return {"system_prompt": prompt, "program_schema": schema, "profiles": list(prof)}


def validate_program(
    program: dict[str, Any] | str,
    manifest: dict[str, Any] | str,
    envelope: dict[str, Any] | str | None = None,
    profiles: Any = (),
    policy: str | dict[str, Any] | None = "DEFAULT",
) -> dict[str, Any]:
    """Validate a URML program. This is the safety check, and it is read-only.

    ``policy`` is ``"DEFAULT"`` (the bundled US-federal compliance policy),
    ``"none"`` to skip compliance, or a policy mapping. Returns the
    ``ValidationResult`` as a dict: ``accepted`` plus structured ``errors`` and
    ``warnings`` (each ``{code, severity, primitive, path, field, message,
    suggestion, detail}``).
    """
    program_d = _as_dict(program, kind="program")
    manifest_d = _as_dict(manifest, kind="manifest")
    envelope_d = _as_dict(envelope, kind="envelope") if envelope is not None else None
    prof = _profiles_tuple(profiles)

    resolved_policy: Any = policy
    if isinstance(policy, str):
        if policy.strip().lower() == "none":
            resolved_policy = None
        elif policy.strip().upper() == "DEFAULT":
            resolved_policy = "DEFAULT"

    result = validate(program_d, manifest_d, envelope=envelope_d, profiles=prof, policy=resolved_policy)
    return result.model_dump(mode="json")


def execute_program(
    program: dict[str, Any] | str,
    manifest: dict[str, Any] | str,
    envelope: dict[str, Any] | str | None = None,
    profiles: Any = (),
    adapter: str = "mock",
) -> dict[str, Any]:
    """Execute a validated URML program against a substrate adapter.

    ``adapter`` is ``"mock"`` (default, hermetic, touches no hardware),
    ``"ros2"``, or ``"px4"``. The real adapters require both the relevant
    runtime/environment and an explicit opt-in: the ``URML_MCP_ALLOW_REAL_EXECUTE``
    env var must be truthy. The runtime re-validates before running (defense in
    depth); there is no path that reaches an actuator without the validator.
    Returns the ``RuntimeResult`` as a dict.
    """
    program_d = _as_dict(program, kind="program")
    manifest_d = _as_dict(manifest, kind="manifest")
    envelope_d = _as_dict(envelope, kind="envelope") if envelope is not None else None
    prof = _profiles_tuple(profiles)

    runtime, cleanup = _build_runtime(adapter)
    try:
        result = runtime.execute(program_d, manifest_d, envelope=envelope_d, profiles=prof)
        return result.model_dump(mode="json")
    finally:
        for close in cleanup:
            try:
                close()
            except Exception:  # noqa: BLE001 - best-effort teardown, never mask the result
                pass


def _build_runtime(adapter: str) -> tuple[Any, list[Any]]:
    """Construct (runtime, cleanup-callables) for the chosen adapter.

    Mirrors the CLI's adapter selection. ``mock`` is always available; ``ros2``
    and ``px4`` are gated behind ``URML_MCP_ALLOW_REAL_EXECUTE`` and their
    respective runtime dependencies.
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
        from urml_ros2_runtime import RclpyAdapter, load_adapter_config  # type: ignore[attr-defined]

        config = load_adapter_config(Path(config_path)) if config_path else None
        rclpy.init()
        cleanup.append(rclpy.shutdown)
        ros_adapter = RclpyAdapter(config)
        cleanup.append(ros_adapter.close)
        return URMLRuntime(ros_adapter), cleanup

    if adapter == "ardupilot":
        try:
            from urml_ardupilot_runtime import (  # type: ignore[import-not-found]
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
        from urml_px4_runtime import PX4Adapter, load_px4_config  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "the px4 adapter requires urml-px4-runtime (pip install urml-px4-runtime), "
            "plus a reachable PX4 SITL/autopilot."
        ) from exc

    config = load_px4_config(Path(config_path)) if config_path else None
    px4_adapter = PX4Adapter(config)
    close = getattr(px4_adapter, "close", None)
    if callable(close):
        cleanup.append(close)
    return URMLRuntime(px4_adapter), cleanup


def list_profiles() -> dict[str, Any]:
    """List the URML profiles available for ``get_contract`` and ``validate``."""
    return {"profiles": [{"name": p, "description": _PROFILE_BLURB.get(p, "")} for p in AVAILABLE_PROFILES]}


def describe_manifest(manifest: dict[str, Any] | str) -> dict[str, Any]:
    """Return a compact, structural summary of a capability manifest.

    A convenience read-only view so an agent can reason about what a robot
    declares before emitting intent. Makes no schema assumptions: it reports the
    top-level keys and a shallow shape of each.
    """
    manifest_d = _as_dict(manifest, kind="manifest")
    summary: dict[str, Any] = {}
    for key, value in manifest_d.items():
        if isinstance(value, dict):
            summary[key] = {"keys": sorted(value.keys())}
        elif isinstance(value, list):
            summary[key] = {"count": len(value)}
        else:
            summary[key] = value
    return {"top_level_keys": sorted(manifest_d.keys()), "summary": summary}
