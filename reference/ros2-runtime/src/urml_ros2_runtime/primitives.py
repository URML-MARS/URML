"""Per-primitive executors.

Each function maps one URML primitive Step to one (or more) ``ROSAdapter``
calls, threads the result back into the runtime's variable bindings, and
returns a ``PrimitiveOutcome``. The runtime calls these via the registry
in ``PRIMITIVE_EXECUTORS``.

The functions here are deliberately small: they unpack pydantic args from
the validator's schema, call the adapter, and pack the response back.
Anything fancier (geometric planning, perception post-processing) lives
in the adapter implementation, not here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict
from urml_validator.schemas.composition import Step
from urml_validator.schemas.primitives import (
    CaptureArgs,
    DetectArgs,
    DockArgs,
    GraspArgs,
    HoverArgs,
    MeasureArgs,
    MoveToArgs,
    ReleaseArgs,
    ReportArgs,
    ScanArgs,
    WaitArgs,
    WaitForArgs,
)

from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ROSAdapter,
    ScanResult,
    SubstrateResult,
    WaitResult,
)

# ---------------------------------------------------------------------------
# Outcome record passed back to the runtime
# ---------------------------------------------------------------------------


# The full union of substrate results a primitive's `raw` field can hold.
RawSubstrateResult = (
    SubstrateResult
    | NavigationResult
    | ManipulationResult
    | DetectionResult
    | ScanResult
    | MeasurementResult
    | CaptureResult
    | WaitResult
)


class PrimitiveOutcome(BaseModel):
    """What a primitive executor returns to the runtime.

    `success` drives on-error handling. `bindings` is merged into the
    runtime's variable scope so later steps can see `$name` references.
    `raw` is the underlying adapter result, kept for diagnostics.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    success: bool
    reason: str | None = None
    bindings: dict[str, Any] = {}
    raw: RawSubstrateResult | None = None


# ---------------------------------------------------------------------------
# Executor protocol
# ---------------------------------------------------------------------------


class PrimitiveExecutor(Protocol):
    """The shape every per-primitive function satisfies."""

    def __call__(self, args: BaseModel, adapter: ROSAdapter) -> PrimitiveOutcome: ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _duration_seconds(value: float | str | None) -> float | None:
    """Normalize a Duration (number or '30s' / '2m' / etc.) into float seconds."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # String form like "30s", "2m", "500ms", "1h".
    suffix_map = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0}
    for suffix, scale in sorted(suffix_map.items(), key=lambda kv: -len(kv[0])):
        if value.endswith(suffix):
            number = float(value[: -len(suffix)])
            return number * scale
    raise ValueError(f"unrecognized duration string: {value!r}")


def _force_newtons(force: Any) -> float | None:
    """Normalize a Force (`gentle`/`firm`/number/Force model) into newtons."""
    if force is None:
        return None
    if isinstance(force, (int, float)):
        return float(force)
    if isinstance(force, str):
        return {"gentle": 1.5, "firm": 8.0}.get(force)
    # pydantic Force union may resolve to a model with .level or .newtons.
    level = getattr(force, "level", None)
    if isinstance(level, str):
        return {"gentle": 1.5, "firm": 8.0}.get(level)
    newtons = getattr(force, "newtons", None)
    if isinstance(newtons, (int, float)):
        return float(newtons)
    return None


# ---------------------------------------------------------------------------
# Per-primitive executors
# ---------------------------------------------------------------------------


def exec_move_to(args: MoveToArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    pose = None
    if args.pose is not None:
        pose = {"x": args.pose.x, "y": args.pose.y}
        for field in ("z", "yaw", "pitch", "roll"):
            v = getattr(args.pose, field)
            if v is not None:
                pose[field] = v
    speed_value: float | None = None
    if isinstance(args.speed, (int, float)):
        speed_value = float(args.speed)
    elif args.speed is not None:
        speed_value = float(getattr(args.speed, "value", 0.0)) or None
    result = adapter.send_navigation_goal(
        location=args.location,
        pose=pose,
        frame=args.frame,
        carrying=args.carrying,
        speed=speed_value,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_dock(args: DockArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    until_str: str | None = None
    if args.until is not None:
        until_str = str(args.until)
    result = adapter.send_docking_goal(
        station=args.at or "primary",
        service=args.service,
        until=until_str,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_hover(args: HoverArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    # Hover is implemented as a stationary navigation goal at current pose.
    # The adapter is responsible for interpreting "hold position for duration".
    result = adapter.send_navigation_goal(
        location=args.over if isinstance(args.over, str) and not args.over.startswith("$") else None,
        pose=None,
        frame=None,
        carrying=None,
        speed=0.0,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_wait(args: WaitArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    seconds = _duration_seconds(args.duration) or 0.0
    result = adapter.wait_passively(duration_seconds=seconds)
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_wait_for(args: WaitForArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    cond = args.condition
    kind: Literal["event", "signal", "input", "sensor_threshold"]
    name: str | None = None
    input_mode: str | None = None
    threshold: dict[str, Any] | None = None
    if cond.event is not None:
        kind = "event"
        name = cond.event
    elif cond.signal is not None:
        kind = "signal"
        name = cond.signal
    elif cond.input is not None:
        kind = "input"
        input_mode = cond.input
    else:
        kind = "sensor_threshold"
        threshold = cond.sensor_threshold.model_dump() if cond.sensor_threshold else None
    timeout = _duration_seconds(args.timeout)
    result = adapter.wait_for_condition(
        kind=kind,
        name=name,
        input_mode=input_mode,
        threshold=threshold,
        timeout_seconds=timeout,
    )
    bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=bindings
    )


def exec_grasp(args: GraspArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    result = adapter.send_manipulation_goal(
        action="grasp",
        target_ref=args.target,
        force_n=_force_newtons(args.force),
        approach=args.approach,
        release_mode=None,
        release_at=None,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_release(args: ReleaseArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    release_at: str | None = None
    if isinstance(args.at, str):
        release_at = args.at
    result = adapter.send_manipulation_goal(
        action="release",
        target_ref=None,
        force_n=None,
        approach="auto",
        release_mode=args.mode,
        release_at=release_at,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_detect(args: DetectArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    where_near: str | None = None
    where_within: float | None = None
    if args.where is not None:
        if isinstance(args.where.near, str):
            where_near = args.where.near
        where_within = args.where.within
    attributes = args.attributes.model_dump(exclude_none=True) if args.attributes else None
    result = adapter.query_detection(
        object_class=args.object,
        attributes=attributes,
        where_near=where_near,
        where_within=where_within,
    )
    bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=bindings
    )


def exec_scan(args: ScanArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    result = adapter.run_scan(
        area=args.area.model_dump(exclude_none=True),
        pattern=args.pattern,
        overlap=args.overlap,
        altitude=args.altitude,
        media=args.media,
        sensor=args.sensor,
    )
    bindings: dict[str, Any] = {}
    if result.payload is not None:
        bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=bindings
    )


def exec_measure(args: MeasureArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    target_str: str | None = None
    if isinstance(args.target, str):
        target_str = args.target
    result = adapter.take_measurement(
        what=str(args.what),
        target=target_str,
        sensor=args.sensor,
    )
    bindings: dict[str, Any] = {}
    if result.payload is not None:
        bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=bindings
    )


def exec_capture(args: CaptureArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    target_str: str | None = None
    if isinstance(args.target, str):
        target_str = args.target
    duration_s = _duration_seconds(args.duration)
    attributes = args.attributes.model_dump(exclude_none=True) if args.attributes else None
    result = adapter.capture_media(
        media=args.media,
        target=target_str,
        duration_seconds=duration_s,
        attributes=attributes,
    )
    bindings: dict[str, Any] = {}
    if result.payload is not None:
        bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=bindings
    )


def exec_report(args: ReportArgs, adapter: ROSAdapter) -> PrimitiveOutcome:
    result = adapter.emit_report(
        to=args.to,
        facts=args.facts,
        attachments=args.attachments,
        status=args.status,
        severity=args.severity,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


# ---------------------------------------------------------------------------
# Registry — runtime dispatch table
# ---------------------------------------------------------------------------


PRIMITIVE_EXECUTORS: dict[str, Callable[[Any, ROSAdapter], PrimitiveOutcome]] = {
    "move_to": exec_move_to,
    "dock": exec_dock,
    "hover": exec_hover,
    "wait": exec_wait,
    "wait_for": exec_wait_for,
    "grasp": exec_grasp,
    "release": exec_release,
    "detect": exec_detect,
    "scan": exec_scan,
    "measure": exec_measure,
    "capture": exec_capture,
    "report": exec_report,
}


def execute_step(step: Step, adapter: ROSAdapter) -> PrimitiveOutcome:
    """Dispatch one Step through the right executor."""
    name = step.primitive_name
    executor = PRIMITIVE_EXECUTORS[name]  # KeyError here = unknown primitive => bug
    args = getattr(step, name)
    return executor(args, adapter)
