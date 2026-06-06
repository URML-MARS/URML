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
    BimanualArgs,
    CallProgramArgs,
    CaptureArgs,
    DetectArgs,
    DockArgs,
    FollowTrajectoryArgs,
    GraspArgs,
    HoverArgs,
    LandArgs,
    ListenArgs,
    MeasureArgs,
    MoveToArgs,
    PickFromArgs,
    PlaceAtArgs,
    PlanPathArgs,
    ReleaseArgs,
    ReportArgs,
    ReturnToHomeArgs,
    ScanArgs,
    SpeakArgs,
    SwapToolArgs,
    TakeOffArgs,
    WaitArgs,
    WaitForArgs,
)

from urml_ros2_runtime.bindings import resolve, resolve_all
from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ProgramCallResult,
    ROSAdapter,
    ScanResult,
    SubstrateResult,
    TrajectoryAdapter,
    TrajectoryPlanResult,
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
    | ListenResult
    | ProgramCallResult
    | TrajectoryPlanResult
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

    def __call__(
        self,
        args: BaseModel,
        adapter: ROSAdapter,
        bindings: dict[str, Any],
    ) -> PrimitiveOutcome: ...


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


def _resolve_target_field(value: Any, bindings: dict[str, Any]) -> dict[str, Any] | str | None:
    """For fields like `release.at` that can be a $ref OR a literal name.

    Returns:
        - dict resolved from a $ref
        - str literal (the original)
        - None
    """
    if value is None:
        return None
    if isinstance(value, str) and value.startswith("$"):
        resolved = resolve(value, bindings)
        if isinstance(resolved, dict):
            return resolved
        # Refs that resolve to non-dicts (rare) are passed through as-is.
        return resolved  # type: ignore[no-any-return]
    if isinstance(value, str):
        return value
    return value  # type: ignore[no-any-return]


def exec_move_to(
    args: MoveToArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
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
    # `carrying` is always a $ref per the schema (VarRef). Resolve it.
    carrying_resolved: dict[str, Any] | None = None
    if args.carrying is not None:
        resolved = resolve(args.carrying, bindings)
        if isinstance(resolved, dict):
            carrying_resolved = resolved
    result = adapter.send_navigation_goal(
        location=args.location,
        pose=pose,
        frame=args.frame,
        carrying=carrying_resolved,
        speed=speed_value,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_dock(
    args: DockArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    until_str: str | None = None
    if args.until is not None:
        until_str = str(args.until)
    result = adapter.send_docking_goal(
        station=args.at or "primary",
        service=args.service,
        until=until_str,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_hover(
    args: HoverArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    # `over` may be a $ref or a literal name. Literal names go through as `location`;
    # $refs become navigation goals at the bound pose (when resolvable).
    location: str | None = None
    pose: dict[str, float] | None = None
    if isinstance(args.over, str):
        if args.over.startswith("$"):
            resolved = resolve(args.over, bindings)
            if isinstance(resolved, dict) and "pose" in resolved:
                pose = resolved["pose"]
        else:
            location = args.over
    result = adapter.send_navigation_goal(
        location=location,
        pose=pose,
        frame=None,
        carrying=None,
        speed=0.0,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_wait(
    args: WaitArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    seconds = _duration_seconds(args.duration) or 0.0
    result = adapter.wait_passively(duration_seconds=seconds)
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_wait_for(
    args: WaitForArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
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
    new_bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_grasp(
    args: GraspArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    # `target` is always a $ref per the schema (VarRef).
    resolved = resolve(args.target, bindings)
    target_dict: dict[str, Any] | None = resolved if isinstance(resolved, dict) else None
    result = adapter.send_manipulation_goal(
        action="grasp",
        target=target_dict,
        force_n=_force_newtons(args.force),
        approach=args.approach,
        release_mode=None,
        release_at=None,
        arm=args.arm,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_release(
    args: ReleaseArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    release_at = _resolve_target_field(args.at, bindings)
    result = adapter.send_manipulation_goal(
        action="release",
        target=None,
        force_n=None,
        approach="auto",
        release_mode=args.mode,
        release_at=release_at,
        arm=args.arm,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_bimanual(
    args: BimanualArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """RFC-0010: decompose a bimanual intent into two arm-addressed
    manipulation goals (left then right) and record the coordination mode.

    True joint force coordination for a shared payload is a substrate concern;
    the reference runtime issues the two goals and reports combined success.
    """
    results: list[ManipulationResult] = []
    for side, sub in (("left", args.left), ("right", args.right)):
        if isinstance(sub, GraspArgs):
            resolved = resolve(sub.target, bindings)
            target_dict: dict[str, Any] | None = resolved if isinstance(resolved, dict) else None
            results.append(
                adapter.send_manipulation_goal(
                    action="grasp",
                    target=target_dict,
                    force_n=_force_newtons(sub.force),
                    approach=sub.approach,
                    release_mode=None,
                    release_at=None,
                    arm=side,
                )
            )
        else:
            release_at = _resolve_target_field(sub.at, bindings)
            results.append(
                adapter.send_manipulation_goal(
                    action="release",
                    target=None,
                    force_n=None,
                    approach="auto",
                    release_mode=sub.mode,
                    release_at=release_at,
                    arm=side,
                )
            )
    success = all(r.success for r in results)
    reason = None if success else next((r.reason for r in results if not r.success), None)
    # The two arm-addressed goals are the runtime evidence in the audit log;
    # `mode` is an intent-level declaration carried by the program. `raw` holds
    # the combined manipulation outcome (one ManipulationResult, like the
    # single-arm path), keeping the result model substrate-agnostic.
    grip = next((r.grip_force_n for r in results if r.grip_force_n is not None), None)
    return PrimitiveOutcome(
        success=success,
        reason=reason,
        raw=ManipulationResult(success=success, reason=reason, grip_force_n=grip),
    )


def exec_detect(
    args: DetectArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    where_near: str | None = None
    where_within: float | None = None
    if args.where is not None:
        if isinstance(args.where.near, str):
            # `near` may be a $ref or a literal location name. For now we
            # extract a string locator (the literal name, or a resolved
            # location identifier from the bound object). The adapter
            # receives a string to keep its surface compact.
            if args.where.near.startswith("$"):
                resolved = resolve(args.where.near, bindings)
                if isinstance(resolved, dict) and "name" in resolved:
                    where_near = resolved["name"]
                elif isinstance(resolved, str):
                    where_near = resolved
            else:
                where_near = args.where.near
        where_within = args.where.within
    attributes = args.attributes.model_dump(exclude_none=True) if args.attributes else None
    result = adapter.query_detection(
        object_class=args.object,
        attributes=attributes,
        where_near=where_near,
        where_within=where_within,
    )
    new_bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_scan(
    args: ScanArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    result = adapter.run_scan(
        area=args.area.model_dump(exclude_none=True),
        pattern=args.pattern,
        overlap=args.overlap,
        altitude=args.altitude,
        media=args.media,
        sensor=args.sensor,
    )
    new_bindings: dict[str, Any] = {}
    if result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_measure(
    args: MeasureArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    # `target` may be a $ref, a literal name, or omitted.
    target_str: str | None = None
    if isinstance(args.target, str):
        if args.target.startswith("$"):
            resolved = resolve(args.target, bindings)
            if isinstance(resolved, dict) and "name" in resolved:
                target_str = resolved["name"]
            elif isinstance(resolved, str):
                target_str = resolved
        else:
            target_str = args.target
    result = adapter.take_measurement(
        what=str(args.what),
        target=target_str,
        sensor=args.sensor,
    )
    new_bindings: dict[str, Any] = {}
    if result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_capture(
    args: CaptureArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    # `target` may be a $ref or a literal name.
    target_str: str | None = None
    if isinstance(args.target, str):
        if args.target.startswith("$"):
            resolved = resolve(args.target, bindings)
            if isinstance(resolved, dict) and "name" in resolved:
                target_str = resolved["name"]
            elif isinstance(resolved, str):
                target_str = resolved
        else:
            target_str = args.target
    duration_s = _duration_seconds(args.duration)
    attributes = args.attributes.model_dump(exclude_none=True) if args.attributes else None
    result = adapter.capture_media(
        media=args.media,
        target=target_str,
        duration_seconds=duration_s,
        attributes=attributes,
    )
    new_bindings: dict[str, Any] = {}
    if result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_report(
    args: ReportArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    # `facts` may contain $ref values; `attachments` is a list of $refs.
    resolved_facts = resolve_all(args.facts, bindings)
    resolved_attachments: list[Any] | None = None
    if args.attachments is not None:
        resolved_attachments = [resolve(ref, bindings) for ref in args.attachments]
    result = adapter.emit_report(
        to=args.to,
        facts=resolved_facts,
        attachments=resolved_attachments,
        status=args.status,
        severity=args.severity,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_speak(
    args: SpeakArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Home profile: emit a spoken utterance."""
    result = adapter.emit_speech(
        utterance=args.utterance,
        locale=args.locale,
        style=args.style,
        interrupt=args.interrupt,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_listen(
    args: ListenArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Home profile: block until the user provides spoken input."""
    timeout = _duration_seconds(args.timeout)
    result = adapter.acquire_speech(
        prompt=args.prompt,
        locale=args.locale,
        timeout_seconds=timeout,
        expected=args.expected,
        choices=args.choices,
    )
    new_bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success,
        reason=result.reason,
        raw=result,
        bindings=new_bindings,
    )


def exec_take_off(
    args: TakeOffArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Drone profile: ascend from ground to declared altitude."""
    result = adapter.send_takeoff_goal(
        altitude=args.altitude,
        climb_rate=args.climb_rate,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_land(
    args: LandArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Drone profile: descend to declared landing location (or current position)."""
    result = adapter.send_land_goal(
        at=args.at,
        precision=args.precision,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_return_to_home(
    args: ReturnToHomeArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Drone profile: abort current intent and fly to declared home."""
    result = adapter.send_return_to_home_goal(
        speed=args.speed,
        altitude=args.altitude,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_pick_from(
    args: PickFromArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Industrial profile: navigate to a station, detect, and grasp.

    Composes the existing navigation / detection / manipulation adapter
    calls — no new substrate Protocol method (RFC-0013). Binds the detected
    object (same payload shape as `detect`) when `store_as` is set, so
    `place_at.held` can reference it.
    """
    nav = adapter.send_navigation_goal(
        location=args.source,
        pose=None,
        frame=None,
        carrying=None,
        speed=None,
    )
    if not nav.success:
        return PrimitiveOutcome(success=False, reason=nav.reason, raw=nav)
    attributes = args.attributes.model_dump(exclude_none=True) if args.attributes else None
    det = adapter.query_detection(
        object_class=args.object,
        attributes=attributes,
        where_near=args.source,
        where_within=None,
    )
    if not det.success or det.payload is None:
        return PrimitiveOutcome(success=False, reason=det.reason, raw=det)
    grip = adapter.send_manipulation_goal(
        action="grasp",
        target=det.payload if isinstance(det.payload, dict) else None,
        force_n=_force_newtons(args.force),
        approach="auto",
        release_mode=None,
        release_at=None,
    )
    new_bindings: dict[str, Any] = {}
    if args.store_as is not None:
        new_bindings[args.store_as] = det.payload
    return PrimitiveOutcome(
        success=grip.success, reason=grip.reason, raw=grip, bindings=new_bindings
    )


def exec_place_at(
    args: PlaceAtArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Industrial profile: navigate to a station and release the held object.

    Composes navigation (carrying the resolved held object) + release. No
    new substrate Protocol method (RFC-0013). `height` is advisory in v0.1
    (the manipulation surface has no height parameter).
    """
    resolved = resolve(args.held, bindings)
    carrying = resolved if isinstance(resolved, dict) else None
    nav = adapter.send_navigation_goal(
        location=args.target,
        pose=None,
        frame=None,
        carrying=carrying,
        speed=None,
    )
    if not nav.success:
        return PrimitiveOutcome(success=False, reason=nav.reason, raw=nav)
    rel = adapter.send_manipulation_goal(
        action="release",
        target=None,
        force_n=None,
        approach="auto",
        release_mode=args.mode,
        release_at=args.target,
    )
    return PrimitiveOutcome(success=rel.success, reason=rel.reason, raw=rel)


def exec_swap_tool(
    args: SwapToolArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Industrial profile: change the end-of-arm tool at a tool-change station.

    Rides the existing docking-station service mechanism (RFC-0013): the
    target tool name travels in `until`. This intentionally reuses
    `send_docking_goal` rather than adding a substrate Protocol method, so
    every adapter supports it for free. The `until`-carries-tool-name
    overload is documented in RFC-0013 Drawbacks.
    """
    result = adapter.send_docking_goal(
        station=args.at,
        service="swap_tool",
        until=args.to,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


def exec_call_program(
    args: CallProgramArgs, adapter: ROSAdapter, _bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """Invoke a substrate-declared program by name (RFC-0015 `call_program`).

    The validator has already confirmed the program and its arg signature
    against the manifest. Args are literal scalars (no `$ref` resolution).
    When `expect: value` was used, the opaque return payload is bound to
    `store_as` as a `program_result`.
    """
    result = adapter.call_named_program(name=args.name, args=args.args)
    new_bindings: dict[str, Any] = {}
    if args.store_as is not None and result.payload is not None:
        new_bindings[args.store_as] = result.payload
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def _location_or_pose_value(value: Any) -> dict[str, float] | str | None:
    """Normalize a LocationOrPose (str location name or Pose) for the adapter."""
    if value is None or isinstance(value, str):
        return value
    out: dict[str, float] = {"x": value.x, "y": value.y}
    for field in ("z", "yaw", "pitch", "roll"):
        v = getattr(value, field, None)
        if v is not None:
            out[field] = v
    return out


def exec_plan_path(
    args: PlanPathArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """RFC-0020: compute a trajectory and bind it (compute verb, no actuation)."""
    if not isinstance(adapter, TrajectoryAdapter):
        return PrimitiveOutcome(
            success=False,
            reason="not_supported: this substrate has no trajectory planner "
            "(plan_path requires a TrajectoryAdapter, RFC-0020).",
        )
    result = adapter.plan_trajectory(
        start=_location_or_pose_value(args.from_),
        goal=_location_or_pose_value(args.to),
        along=args.along,
    )
    new_bindings: dict[str, Any] = {}
    if result.payload is not None:
        new_bindings[args.store_as] = result.payload
        if args.store_alt_as is not None:
            # Minimum-Risk fallback binding; same shape, flagged so a consumer
            # can tell it apart at runtime.
            new_bindings[args.store_alt_as] = {**result.payload, "fallback": True}
    return PrimitiveOutcome(
        success=result.success, reason=result.reason, raw=result, bindings=new_bindings
    )


def exec_follow_trajectory(
    args: FollowTrajectoryArgs, adapter: ROSAdapter, bindings: dict[str, Any]
) -> PrimitiveOutcome:
    """RFC-0020: execute a trajectory bound by plan_path (the only AV actuator)."""
    if not isinstance(adapter, TrajectoryAdapter):
        return PrimitiveOutcome(
            success=False,
            reason="not_supported: this substrate cannot follow a trajectory "
            "(follow_trajectory requires a TrajectoryAdapter, RFC-0020).",
        )
    resolved = resolve(args.trajectory, bindings)
    traj = resolved if isinstance(resolved, dict) else None
    se = args.speed_envelope
    result = adapter.follow_trajectory_goal(
        trajectory=traj,
        max_velocity_mps=getattr(se, "max_velocity_mps", None) if se is not None else None,
        max_accel_mps2=getattr(se, "max_accel_mps2", None) if se is not None else None,
        on_off_route=args.on_off_route,
    )
    return PrimitiveOutcome(success=result.success, reason=result.reason, raw=result)


# ---------------------------------------------------------------------------
# Registry — runtime dispatch table
# ---------------------------------------------------------------------------


PRIMITIVE_EXECUTORS: dict[
    str, Callable[[Any, ROSAdapter, dict[str, Any]], PrimitiveOutcome]
] = {
    "move_to": exec_move_to,
    "dock": exec_dock,
    "hover": exec_hover,
    "wait": exec_wait,
    "wait_for": exec_wait_for,
    "grasp": exec_grasp,
    "release": exec_release,
    "bimanual": exec_bimanual,
    "detect": exec_detect,
    "scan": exec_scan,
    "measure": exec_measure,
    "capture": exec_capture,
    "report": exec_report,
    "speak": exec_speak,
    "listen": exec_listen,
    "take_off": exec_take_off,
    "land": exec_land,
    "return_to_home": exec_return_to_home,
    "pick_from": exec_pick_from,
    "place_at": exec_place_at,
    "swap_tool": exec_swap_tool,
    "call_program": exec_call_program,
    "plan_path": exec_plan_path,
    "follow_trajectory": exec_follow_trajectory,
}


def execute_step(step: Step, adapter: ROSAdapter, bindings: dict[str, Any]) -> PrimitiveOutcome:
    """Dispatch one Step through the right executor.

    `bindings` is the runtime's current variable scope. Executors resolve
    `$ref` arguments against it before calling the adapter so the adapter
    only sees concrete data.
    """
    name = step.primitive_name
    executor = PRIMITIVE_EXECUTORS[name]  # KeyError here = unknown primitive => bug
    args = getattr(step, name)
    return executor(args, adapter, bindings)
