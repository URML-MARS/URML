"""The five-pass URML validator.

`validate(program, manifest, envelope, profiles, policy)` returns a
`ValidationResult` that the LLM bridge consumes. The five passes, in order:

  1. **Argument typing.** Delegated to pydantic via `URMLProgram.model_validate`.
     Surfaced here as namespaced `argument.*` errors.
  2. **Capability checks.** Each primitive declares Layer-1 capability fields
     the manifest must contain. Missing fields produce `capability.*` errors.
  3. **Safety envelope.** Numeric caps and spatial constraints from the
     deployment envelope and the manifest are intersected (strictest wins).
     Violations produce `envelope.*` errors.
  4. **Variable bindings.** `store_as` names must be unique within their
     scope; `$var` references must resolve to a prior binding. This pass
     produces `binding.*` errors.
  5. **Compliance policy (RFC-0004).** Evaluates a pluggable policy file
     against the manifest's `provenance` block. Produces `policy.*` errors
     and warnings. Default policy is the bundled US-federal rule set.

The passes are best-effort sequential: argument failure short-circuits the
later passes (because the program tree is invalid); capability/envelope/
binding/policy errors all collect into the same result so authors get full
feedback in one round trip.

Scope of this milestone:

- Capability checks cover every primitive in RFC-0002.
- Envelope checks cover numeric caps (velocity, altitude, payload, force).
- Geofence and people-occupancy *containment* is named-location-only for now;
  polygon-vertex math arrives once the validator gains a geometry helper.
- Variable bindings: name uniqueness + reference resolution. Type checking
  across primitives (`grasp` requires an object-typed reference, etc.) is
  deferred to the next milestone.
- Policy enforcement: evaluates only when the manifest declares a
  `provenance:` block. Manifests without provenance trigger no Pass 5
  errors (policy enforcement is opt-in at the manifest level).
"""

from __future__ import annotations

from collections.abc import Iterator
from importlib import resources
from typing import Any, Literal

import yaml
from pydantic import ValidationError as PydanticValidationError

from urml_validator.errors import ErrorCode, ValidationError, ValidationResult
from urml_validator.policy_engine import evaluate_policy
from urml_validator.schemas.composition import Branch, Parallel, Retry, Sequence, Step
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import Camera, CapabilityManifest, Gripper, Sensor
from urml_validator.schemas.policy import Policy
from urml_validator.schemas.primitives import (
    CaptureArgs,
    DetectArgs,
    DockArgs,
    GraspArgs,
    HoverArgs,
    ListenArgs,
    MeasureArgs,
    MoveToArgs,
    ReleaseArgs,
    ReportArgs,
    ScanArgs,
    SpeakArgs,
    WaitForArgs,
)
from urml_validator.schemas.program import URMLProgram

# =============================================================================
# Default-policy sentinel
# =============================================================================

#: Sentinel passed as the default value of the `policy` parameter.
#: Indicates "load the bundled default policy"; distinct from None which
#: indicates "skip Pass 5 entirely".
DEFAULT_POLICY: Literal["DEFAULT"] = "DEFAULT"

#: Name of the default policy YAML file shipped under urml_validator/policies/.
_DEFAULT_POLICY_RESOURCE = "us_federal_default.yaml"

#: Cache for the bundled default policy. Loaded once per process.
_DEFAULT_POLICY_CACHE: Policy | None = None


def _load_default_policy() -> Policy:
    """Load and cache the bundled US-federal default policy."""
    global _DEFAULT_POLICY_CACHE
    if _DEFAULT_POLICY_CACHE is None:
        text = resources.files("urml_validator.policies").joinpath(
            _DEFAULT_POLICY_RESOURCE
        ).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise RuntimeError(
                f"bundled default policy {_DEFAULT_POLICY_RESOURCE} did not parse as a mapping"
            )
        _DEFAULT_POLICY_CACHE = Policy.model_validate(data)
    return _DEFAULT_POLICY_CACHE

# =============================================================================
# Public entry point
# =============================================================================


def validate(
    program: dict[str, Any] | URMLProgram,
    manifest: dict[str, Any] | CapabilityManifest,
    envelope: dict[str, Any] | SafetyEnvelope | None = None,
    profiles: tuple[str, ...] = (),
    policy: dict[str, Any] | Policy | None | Literal["DEFAULT"] = "DEFAULT",
) -> ValidationResult:
    """Validate a URML program against a manifest and (optionally) an envelope.

    Inputs may be raw dicts (already-parsed YAML) or pre-validated pydantic
    models. Raw dicts are model-validated first; failures surface as
    pass-1 errors and short-circuit the remaining passes.

    Args:
        program:    The URML program. Raw dict or `URMLProgram`.
        manifest:   The robot's capability manifest. Raw dict or `CapabilityManifest`.
        envelope:   Optional deployment safety envelope. Raw dict, `SafetyEnvelope`, or None.
        profiles:   Profile names the validator should consider active. Currently
                    informational; profile-specific constraints land in per-profile RFCs.
        policy:     Compliance policy for Pass 5. Pass ``"DEFAULT"`` (the default)
                    to load the bundled US-federal policy; ``None`` to skip Pass 5
                    entirely; or a raw dict / ``Policy`` model to use a specific policy.

    Returns:
        A `ValidationResult` with `accepted=True` iff no error-severity errors fired.
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # ----- Pass 1: argument typing -----
    try:
        program_model: URMLProgram = (
            program if isinstance(program, URMLProgram) else URMLProgram.model_validate(program)
        )
    except PydanticValidationError as exc:
        errors.extend(_pydantic_errors_to_validation_errors(exc))
        return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    try:
        manifest_model: CapabilityManifest = (
            manifest
            if isinstance(manifest, CapabilityManifest)
            else CapabilityManifest.model_validate(manifest)
        )
    except PydanticValidationError as exc:
        # A bad manifest is a hard stop — no further pass can be meaningful.
        for e in _pydantic_errors_to_validation_errors(exc):
            e.path = ["<manifest>", *e.path]
            errors.append(e)
        return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    envelope_model: SafetyEnvelope | None
    if envelope is None:
        envelope_model = None
    elif isinstance(envelope, SafetyEnvelope):
        envelope_model = envelope
    else:
        try:
            envelope_model = SafetyEnvelope.model_validate(envelope)
        except PydanticValidationError as exc:
            for e in _pydantic_errors_to_validation_errors(exc):
                e.path = ["<envelope>", *e.path]
                errors.append(e)
            return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    # ----- Pass 2: capability checks -----
    for path, step in walk_program(program_model):
        errors.extend(_check_capabilities(step, manifest_model, path))

    # ----- Pass 3: envelope checks -----
    for path, step in walk_program(program_model):
        errors.extend(_check_envelope(step, manifest_model, envelope_model, path))

    # ----- Pass 4: variable bindings -----
    errors.extend(_check_bindings(program_model))

    # ----- Pass 5: compliance policy (RFC-0004) -----
    policy_model = _resolve_policy(policy, errors)
    if policy_model is not None:
        for issue in evaluate_policy(manifest_model, policy_model):
            if issue.severity == "warning":
                warnings.append(issue)
            else:
                errors.append(issue)

    return ValidationResult(
        accepted=not errors,
        errors=errors,
        warnings=warnings,
    )


def _resolve_policy(
    policy: dict[str, Any] | Policy | None | Literal["DEFAULT"],
    errors: list[ValidationError],
) -> Policy | None:
    """Resolve the `policy` argument into a Policy model (or None to skip Pass 5).

    A malformed dict policy is converted into a `policy.rule_invalid` error
    appended to `errors` and Pass 5 is skipped.
    """
    if policy is None:
        return None
    if policy == "DEFAULT":
        return _load_default_policy()
    if isinstance(policy, Policy):
        return policy
    if isinstance(policy, dict):
        try:
            return Policy.model_validate(policy)
        except PydanticValidationError as exc:
            errors.append(
                ValidationError(
                    code=ErrorCode.POLICY_RULE_INVALID,
                    message=f"policy file failed schema validation: {exc.error_count()} error(s)",
                    path=["<policy>"],
                    detail={"pydantic_errors": exc.errors()},
                )
            )
            return None
    raise TypeError(
        f"policy must be Policy, dict, None, or 'DEFAULT' sentinel; got {type(policy).__name__}"
    )


# =============================================================================
# Tree walker
# =============================================================================


def walk_program(program: URMLProgram) -> Iterator[tuple[list[str], Step]]:
    """Yield every Step in a program in execution order, with its JSON path.

    Recursively walks Sequence/Branch/Parallel/Retry composition nodes.
    Order is depth-first; Branch yields both branches; Parallel yields each
    branch in declaration order.
    """
    yield from _walk_behavior(program.behavior, ["behavior"])


def _walk_behavior(node: object, path: list[str]) -> Iterator[tuple[list[str], Step]]:
    if isinstance(node, Step):
        yield path, node
        return
    if isinstance(node, Sequence):
        for idx, sub in enumerate(node.steps):
            yield from _walk_behavior(sub, [*path, "steps", str(idx)])
        return
    if isinstance(node, Branch):
        yield from _walk_behavior(node.if_true, [*path, "if_true"])
        if node.if_false is not None:
            yield from _walk_behavior(node.if_false, [*path, "if_false"])
        return
    if isinstance(node, Parallel):
        for idx, sub in enumerate(node.branches):
            yield from _walk_behavior(sub, [*path, "branches", str(idx)])
        return
    if isinstance(node, Retry):
        yield from _walk_behavior(node.behavior, [*path, "behavior"])
        return
    raise TypeError(f"unexpected behavior node type: {type(node).__name__!r}")


# =============================================================================
# Pass 1: pydantic error translation
# =============================================================================


_PYDANTIC_KIND_TO_CODE: dict[str, ErrorCode] = {
    "missing": ErrorCode.ARGUMENT_MISSING_REQUIRED,
    "extra_forbidden": ErrorCode.ARGUMENT_UNKNOWN_FIELD,
}


def _pydantic_errors_to_validation_errors(
    exc: PydanticValidationError,
) -> list[ValidationError]:
    out: list[ValidationError] = []
    for raw in exc.errors():
        kind = raw.get("type", "")
        code = _PYDANTIC_KIND_TO_CODE.get(kind, ErrorCode.ARGUMENT_TYPE)
        if "value_error" in kind:
            code = ErrorCode.ARGUMENT_CONSTRAINT
        loc = [str(p) for p in raw.get("loc", ())]
        out.append(
            ValidationError(
                code=code,
                primitive=_guess_primitive_from_path(loc),
                path=loc,
                field=loc[-1] if loc else None,
                message=str(raw.get("msg", "argument validation failed")),
                suggestion=None,
            )
        )
    return out


_PRIMITIVE_NAMES_FROZEN = (
    "move_to",
    "dock",
    "hover",
    "wait",
    "wait_for",
    "grasp",
    "release",
    "detect",
    "scan",
    "measure",
    "capture",
    "report",
    "speak",
    "listen",
)


def _guess_primitive_from_path(loc: list[str]) -> str | None:
    """If a pydantic error path crosses a primitive name, return that name."""
    for part in loc:
        if part in _PRIMITIVE_NAMES_FROZEN:
            return part
    return None


# =============================================================================
# Pass 2: capability checks
# =============================================================================


def _check_capabilities(
    step: Step,
    manifest: CapabilityManifest,
    path: list[str],
) -> list[ValidationError]:
    name = step.primitive_name
    args = getattr(step, name)
    if name == "move_to":
        return _check_move_to_caps(args, manifest, path)
    if name == "dock":
        return _check_dock_caps(args, manifest, path)
    if name == "hover":
        return _check_hover_caps(args, manifest, path)
    if name == "wait":
        return []  # wait has no capability requirements
    if name == "wait_for":
        return _check_wait_for_caps(args, manifest, path)
    if name == "grasp":
        return _check_grasp_caps(args, manifest, path)
    if name == "release":
        return _check_release_caps(args, manifest, path)
    if name == "detect":
        return _check_detect_caps(args, manifest, path)
    if name == "scan":
        return _check_scan_caps(args, manifest, path)
    if name == "measure":
        return _check_measure_caps(args, manifest, path)
    if name == "capture":
        return _check_capture_caps(args, manifest, path)
    if name == "report":
        return _check_report_caps(args, manifest, path)
    if name == "speak":
        return _check_speak_caps(args, manifest, path)
    if name == "listen":
        return _check_listen_caps(args, manifest, path)
    raise AssertionError(f"unknown primitive {name!r}")


def _err(
    code: ErrorCode,
    primitive: str,
    path: list[str],
    message: str,
    field: str | None = None,
    suggestion: str | None = None,
) -> ValidationError:
    return ValidationError(
        code=code,
        primitive=primitive,
        path=path,
        field=field,
        message=message,
        suggestion=suggestion,
    )


def _location_declared(manifest: CapabilityManifest, name: str) -> bool:
    return any(loc.name == name for loc in manifest.declared_locations)


def _frame_declared(manifest: CapabilityManifest, name: str) -> bool:
    return any(f.name == name for f in manifest.frames)


def _check_move_to_caps(
    args: MoveToArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "move_to",
                path,
                "move_to requires the manifest to declare `mobility`.",
                suggestion="Add a `mobility` block to the manifest with at least `drive_type` and `max_velocity`.",
            )
        )
    if args.location is not None and not _location_declared(manifest, args.location):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_LOCATION,
                "move_to",
                path,
                f"move_to references undeclared location {args.location!r}.",
                field="location",
                suggestion=f"Add {args.location!r} to manifest.declared_locations, "
                "or use `pose` + `frame` instead of a named location.",
            )
        )
    if args.pose is not None and args.frame is not None and not _frame_declared(manifest, args.frame):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_FRAME,
                "move_to",
                path,
                f"move_to.pose references undeclared frame {args.frame!r}.",
                field="frame",
                suggestion=f"Add {args.frame!r} to manifest.frames.",
            )
        )
    return out


def _check_dock_caps(
    args: DockArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "dock",
                path,
                "dock requires the manifest to declare `mobility`.",
                suggestion="Add a `mobility` block to the manifest.",
            )
        )
    stations = manifest.docking_stations
    if args.at is not None:
        target = next((s for s in stations if s.name == args.at), None)
    else:
        target = stations[0] if stations else None
    if target is None:
        descr = f"named {args.at!r}" if args.at is not None else "(no `at` and no default station)"
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_DOCKING_STATION,
                "dock",
                path,
                f"dock has no resolvable docking station {descr}.",
                field="at",
                suggestion="Declare the docking station in manifest.docking_stations.",
            )
        )
    elif args.service not in target.services:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_DOCKING_SERVICE,
                "dock",
                path,
                f"dock(service: {args.service!r}) is not declared at station {target.name!r}.",
                field="service",
                suggestion=f"Add {args.service!r} to manifest.docking_stations[{target.name!r}].services, "
                f"or pick from declared services: {target.services!r}.",
            )
        )
    return out


def _check_hover_caps(
    _args: HoverArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "hover",
                path,
                "hover requires the manifest to declare `mobility`.",
            )
        )
    elif not manifest.mobility.station_keeping:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_STATION_KEEPING,
                "hover",
                path,
                "hover requires `mobility.station_keeping: true` on the manifest.",
                suggestion="Set `mobility.station_keeping: true` if the robot can actively maintain position.",
            )
        )
    return out


def _check_wait_for_caps(
    args: WaitForArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    cond = args.condition
    if cond.event is not None and cond.event not in manifest.declared_events:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_EVENT,
                "wait_for",
                path,
                f"wait_for references undeclared event {cond.event!r}.",
                field="condition.event",
                suggestion=f"Add {cond.event!r} to manifest.declared_events.",
            )
        )
    if cond.sensor_threshold is not None:
        sensor_name = cond.sensor_threshold.sensor
        if (
            manifest.perception is None
            or not any(s.name == sensor_name for s in manifest.perception.sensors)
        ):
            out.append(
                _err(
                    ErrorCode.CAPABILITY_MISSING_SENSOR,
                    "wait_for",
                    path,
                    f"wait_for(sensor_threshold) references undeclared sensor {sensor_name!r}.",
                    field="condition.sensor_threshold.sensor",
                    suggestion=f"Declare sensor {sensor_name!r} in manifest.perception.sensors.",
                )
            )
    return out


def _gripper_in_range(g: Gripper, force_value: float) -> bool:
    return g.force_min_n <= force_value <= g.force_max_n


def _resolve_force(force: Any) -> float | None:
    """Map gentle/firm to a representative newton value; pass numbers through.

    The mapping here is conservative — it's a static check, not a guarantee.
    """
    if force is None:
        return None
    if isinstance(force, (int, float)):
        return float(force)
    # pydantic union may resolve to a Force model with .level or .newtons.
    level = getattr(force, "level", None)
    if level is not None:
        return {"gentle": 1.5, "firm": 8.0}.get(level)
    newtons = getattr(force, "newtons", None)
    if isinstance(newtons, (int, float)):
        return float(newtons)
    if isinstance(force, str):
        return {"gentle": 1.5, "firm": 8.0}.get(force)
    return None


def _check_grasp_caps(
    args: GraspArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.manipulation is None or not manifest.manipulation.grippers:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MANIPULATION,
                "grasp",
                path,
                "grasp requires the manifest to declare `manipulation` with at least one gripper.",
                suggestion="Add a `manipulation.grippers` list with at least one gripper to the manifest.",
            )
        )
        return out
    force_val = _resolve_force(args.force)
    if force_val is not None:
        usable = [g for g in manifest.manipulation.grippers if _gripper_in_range(g, force_val)]
        if not usable:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_MISSING_GRIPPER,
                    "grasp",
                    path,
                    f"no declared gripper supports the requested force ({force_val} N). "
                    f"Declared ranges: "
                    f"{[(g.name, g.force_min_n, g.force_max_n) for g in manifest.manipulation.grippers]!r}.",
                    field="force",
                    suggestion="Pick a softer/firmer level, or declare a gripper covering the requested range.",
                )
            )
    return out


def _check_release_caps(
    _args: ReleaseArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.manipulation is None or not manifest.manipulation.grippers:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MANIPULATION,
                "release",
                path,
                "release requires the manifest to declare `manipulation` with at least one gripper.",
            )
        )
    return out


def _check_detect_caps(
    args: DetectArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    perception = manifest.perception
    if perception is None or (not perception.cameras and not perception.sensors):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_PERCEPTION,
                "detect",
                path,
                "detect requires the manifest to declare `perception` with at least one camera or sensor.",
            )
        )
        return out
    if args.object not in perception.object_vocabulary:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_OBJECT_CLASS,
                "detect",
                path,
                f"detect references object class {args.object!r} which is not in the manifest's "
                "perception.object_vocabulary.",
                field="object",
                suggestion=f"Add {args.object!r} to manifest.perception.object_vocabulary, "
                "or pick a declared class.",
            )
        )
    return out


def _check_scan_caps(
    args: ScanArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "scan",
                path,
                "scan requires the manifest to declare `mobility`.",
            )
        )
    if manifest.perception is None or (
        not manifest.perception.cameras and not manifest.perception.sensors
    ):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_PERCEPTION,
                "scan",
                path,
                "scan requires the manifest to declare `perception` with at least one camera or sensor.",
            )
        )
    if args.sensor is not None and manifest.perception is not None:
        all_perception_names = {c.name for c in manifest.perception.cameras} | {
            s.name for s in manifest.perception.sensors
        }
        if args.sensor not in all_perception_names:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_MISSING_SENSOR,
                    "scan",
                    path,
                    f"scan references undeclared sensor or camera {args.sensor!r}.",
                    field="sensor",
                    suggestion=f"Declare {args.sensor!r} under manifest.perception.",
                )
            )
    return out


def _check_measure_caps(
    args: MeasureArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    perception = manifest.perception
    if perception is None or not perception.sensors:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_PERCEPTION,
                "measure",
                path,
                "measure requires the manifest to declare `perception.sensors` with at least one sensor.",
            )
        )
        return out
    matching: list[Sensor]
    if args.sensor is not None:
        matching = [s for s in perception.sensors if s.name == args.sensor]
        if not matching:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_MISSING_SENSOR,
                    "measure",
                    path,
                    f"measure references undeclared sensor {args.sensor!r}.",
                    field="sensor",
                )
            )
            return out
    else:
        matching = [s for s in perception.sensors if s.measurement_type == args.what]
        if not matching:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_MISSING_SENSOR,
                    "measure",
                    path,
                    f"measure(what: {args.what!r}) has no sensor declared for that measurement type.",
                    field="what",
                    suggestion="Declare a sensor with the matching `measurement_type` in manifest.perception.sensors.",
                )
            )
    return out


def _check_capture_caps(
    args: CaptureArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    perception = manifest.perception
    if perception is None or not perception.cameras:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_CAMERA,
                "capture",
                path,
                "capture requires the manifest to declare `perception.cameras` with at least one camera.",
            )
        )
        return out
    needed_video = args.media == "video"
    eligible: list[Camera] = [
        c
        for c in perception.cameras
        if (needed_video and c.supports_video) or (not needed_video and c.supports_photo)
    ]
    if not eligible:
        out.append(
            _err(
                ErrorCode.CAPABILITY_VIDEO_UNSUPPORTED if needed_video else ErrorCode.CAPABILITY_MISSING_CAMERA,
                "capture",
                path,
                f"no declared camera supports {args.media} capture.",
                field="media",
                suggestion="Declare a camera that supports the requested media mode.",
            )
        )
    if args.target is not None and all(not c.movable for c in (eligible or perception.cameras)):
        out.append(
            _err(
                ErrorCode.CAPABILITY_FIXED_CAMERA_TARGET,
                "capture",
                path,
                "capture targets a specific subject but every declared camera is fixed (non-movable).",
                field="target",
                suggestion="Omit `target` and rely on the current camera view, "
                "or declare a movable camera in the manifest.",
            )
        )
    return out


def _check_report_caps(
    args: ReportArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if args.to in ("user", "log", "caller"):
        return out
    # Custom endpoint: must be declared in manifest.outputs.named_endpoints.
    if args.to not in manifest.outputs.named_endpoints:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_OUTPUT,
                "report",
                path,
                f"report(to: {args.to!r}) references an undeclared output endpoint.",
                field="to",
                suggestion=f"Add {args.to!r} to manifest.outputs.named_endpoints, "
                "or use one of: user, log, caller.",
            )
        )
    return out


def _check_speak_caps(
    _args: SpeakArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Home profile: `speak` requires a declared `speech` output endpoint."""
    out: list[ValidationError] = []
    if "speech" not in manifest.outputs.named_endpoints:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_SPEECH_OUTPUT,
                "speak",
                path,
                "speak requires the manifest to declare `speech` in outputs.named_endpoints.",
                suggestion="Add `speech` to manifest.outputs.named_endpoints, "
                "or omit `speak` from this program.",
            )
        )
    return out


def _check_listen_caps(
    _args: ListenArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Home profile: `listen` requires a sensor with measurement_type 'speech'."""
    out: list[ValidationError] = []
    perception = manifest.perception
    has_speech_sensor = (
        perception is not None
        and any(s.measurement_type == "speech" for s in perception.sensors)
    )
    if not has_speech_sensor:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_SPEECH_INPUT,
                "listen",
                path,
                "listen requires the manifest to declare a sensor with "
                "measurement_type: speech in perception.sensors.",
                suggestion="Declare a speech-input sensor in manifest.perception.sensors, "
                "or omit `listen` from this program.",
            )
        )
    return out


# =============================================================================
# Pass 3: safety envelope
# =============================================================================


def _check_envelope(
    step: Step,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    name = step.primitive_name
    args = getattr(step, name)
    out: list[ValidationError] = []

    if name == "move_to":
        out.extend(_check_envelope_move_to(args, manifest, envelope, path))
    elif name == "scan":
        out.extend(_check_envelope_scan(args, manifest, envelope, path))
    elif name == "grasp":
        out.extend(_check_envelope_grasp(args, manifest, envelope, path))
    elif name == "hover":
        out.extend(_check_envelope_hover(args, envelope, path))
    elif name in ("move_to", "dock", "wait", "wait_for", "release", "detect", "measure", "capture", "report"):
        pass  # no numeric-envelope obligation for these in this milestone

    return out


def _strictest(*values: float | None) -> float | None:
    """Return the smallest non-None of the given numbers, or None if all are None."""
    finite = [v for v in values if v is not None]
    return min(finite) if finite else None


def _check_envelope_move_to(
    args: MoveToArgs,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    out: list[ValidationError] = []
    # Velocity cap: declared `speed` (if given) must be at or below the
    # strictest of (manifest.mobility.max_velocity, envelope.max_velocity).
    manifest_max = manifest.mobility.max_velocity if manifest.mobility else None
    envelope_max = envelope.max_velocity if envelope else None
    cap = _strictest(manifest_max, envelope_max)
    declared_speed: float | None = None
    if isinstance(args.speed, (int, float)):
        declared_speed = float(args.speed)
    elif args.speed is not None and getattr(args.speed, "units", None) == "m_per_s":
        declared_speed = float(args.speed.value)
    if declared_speed is not None and cap is not None and declared_speed > cap:
        out.append(
            _err(
                ErrorCode.ENVELOPE_VELOCITY_EXCEEDED,
                "move_to",
                path,
                f"move_to.speed ({declared_speed} m/s) exceeds the strictest "
                f"declared cap ({cap} m/s).",
                field="speed",
                suggestion=f"Reduce speed to at most {cap} m/s, "
                "or relax the manifest/envelope cap if the deployment allows.",
            )
        )
    # Altitude cap (drone profile-ish; applies if `pose.z` is set).
    if args.pose is not None and args.pose.z is not None:
        ceiling = _strictest(
            manifest.mobility.service_ceiling if manifest.mobility else None,
            envelope.max_altitude if envelope else None,
        )
        if ceiling is not None and args.pose.z > ceiling:
            out.append(
                _err(
                    ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                    "move_to",
                    path,
                    f"move_to.pose.z ({args.pose.z} m) exceeds the strictest altitude cap ({ceiling} m).",
                    field="pose.z",
                )
            )
    return out


def _check_envelope_scan(
    args: ScanArgs,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    out: list[ValidationError] = []
    if args.altitude is not None:
        ceiling = _strictest(
            manifest.mobility.service_ceiling if manifest.mobility else None,
            envelope.max_altitude if envelope else None,
        )
        if ceiling is not None and args.altitude > ceiling:
            out.append(
                _err(
                    ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                    "scan",
                    path,
                    f"scan.altitude ({args.altitude} m) exceeds the strictest altitude cap ({ceiling} m).",
                    field="altitude",
                )
            )
    return out


def _check_envelope_hover(
    _args: HoverArgs,
    _envelope: SafetyEnvelope | None,
    _path: list[str],
) -> list[ValidationError]:
    # Hover has no declared altitude argument; envelope altitude is checked at
    # the move_to that *got* the robot to hover position. This pass intentionally
    # returns no envelope errors for hover in this milestone.
    return []


def _check_envelope_grasp(
    args: GraspArgs,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    out: list[ValidationError] = []
    force_val = _resolve_force(args.force)
    if force_val is None:
        return out
    grippers = manifest.manipulation.grippers if manifest.manipulation else []
    gripper_max = max((g.force_max_n for g in grippers), default=None)
    envelope_max = envelope.max_grip_force_n if envelope else None
    cap = _strictest(gripper_max, envelope_max)
    if cap is not None and force_val > cap:
        out.append(
            _err(
                ErrorCode.ENVELOPE_FORCE_EXCEEDED,
                "grasp",
                path,
                f"grasp.force ({force_val} N) exceeds the strictest declared force cap ({cap} N).",
                field="force",
                suggestion=f"Reduce the grasp force to at most {cap} N.",
            )
        )
    return out


# =============================================================================
# Pass 4: variable bindings
# =============================================================================


def _check_bindings(program: URMLProgram) -> list[ValidationError]:
    """Name uniqueness + reference resolution.

    Conservative semantics in this milestone:

      * `store_as` names must be unique across the program (no shadowing).
      * `$var` references are resolved iff the same name is bound *anywhere
        earlier in the linear walk order*. Branch / Parallel / Retry boundaries
        are treated permissively; a future milestone tightens this to proper
        definite-assignment analysis.
    """
    out: list[ValidationError] = []
    bound: dict[str, list[str]] = {}  # name -> path where bound

    for path, step in walk_program(program):
        name = step.primitive_name
        args = getattr(step, name)

        # Collect references this step consumes.
        for ref in _references_used(name, args):
            head = ref.lstrip("$").split(".", 1)[0]
            if head not in bound:
                out.append(
                    _err(
                        ErrorCode.BINDING_UNRESOLVED_REFERENCE,
                        name,
                        path,
                        f"{ref} references an unbound name; "
                        f"known bindings at this point: {sorted(bound.keys())!r}.",
                        suggestion=f"Bind {head!r} earlier with a primitive that supports `store_as`.",
                    )
                )

        # Then bind anything new.
        store_as = _store_as_of(args)
        if store_as is not None:
            if store_as in bound:
                out.append(
                    _err(
                        ErrorCode.BINDING_DUPLICATE_STORE_AS,
                        name,
                        path,
                        f"duplicate `store_as: {store_as!r}` (first bound at "
                        f"{'/'.join(bound[store_as])}).",
                        field="store_as",
                        suggestion=f"Pick a different name (e.g., {store_as!r}_2).",
                    )
                )
            else:
                bound[store_as] = path
    return out


def _store_as_of(args: object) -> str | None:
    return getattr(args, "store_as", None)


def _references_used(name: str, args: object) -> list[str]:
    """Return every `$var[.field]` reference the args carry, as raw strings."""
    refs: list[str] = []

    def _maybe(value: Any) -> None:
        if isinstance(value, str) and value.startswith("$"):
            refs.append(value)

    # move_to.carrying
    if name == "move_to":
        _maybe(getattr(args, "carrying", None))
    # grasp.target
    if name == "grasp":
        _maybe(getattr(args, "target", None))
    # release.at
    if name == "release":
        _maybe(getattr(args, "at", None))
    # detect.where.near
    if name == "detect":
        where = getattr(args, "where", None)
        if where is not None:
            _maybe(getattr(where, "near", None))
    # hover.over
    if name == "hover":
        _maybe(getattr(args, "over", None))
    # capture.target
    if name == "capture":
        _maybe(getattr(args, "target", None))
    # measure.target
    if name == "measure":
        _maybe(getattr(args, "target", None))
    # report.attachments (list of refs)
    if name == "report":
        attachments = getattr(args, "attachments", None) or []
        for a in attachments:
            _maybe(a)
    return refs
