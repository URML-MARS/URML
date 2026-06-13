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

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from importlib import resources
from math import hypot
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import ValidationError as PydanticValidationError

from urml_validator.errors import ErrorCode, ValidationError, ValidationResult
from urml_validator.policy_engine import evaluate_policy
from urml_validator.schemas.composition import (
    Barrier,
    Branch,
    OnMember,
    Parallel,
    Retry,
    Sequence,
    Step,
)
from urml_validator.schemas.connectivity import LinkLossAction, LinkRole
from urml_validator.monitorable import (
    MonitorableParseError,
    parse_property,
    referenced_signals,
    referenced_signals_custom,
)
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import (
    LICENSE_RESTRICTIVENESS,
    VENDORABLE_LICENSES,
    Camera,
    CapabilityManifest,
    Frame,
    Gripper,
    Sensor,
)
from urml_validator.schemas.policy import Policy
from urml_validator.schemas.roster import FleetRoster, FrameAnchor
from urml_validator.transforms import resolve_to_world, transform_point_between
from urml_validator.schemas.primitives import (
    BimanualArgs,
    CallProgramArgs,
    CaptureArgs,
    DetectArgs,
    DockArgs,
    GraspArgs,
    HoverArgs,
    LandArgs,
    ListenArgs,
    MeasureArgs,
    MoveToArgs,
    PickFromArgs,
    PlaceAtArgs,
    ReleaseArgs,
    ReportArgs,
    ReturnToHomeArgs,
    ScanArgs,
    SpeakArgs,
    SwapToolArgs,
    TakeOffArgs,
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
    *,
    manifest_base_dir: Path | None = None,
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
        manifest_base_dir: Directory a component's relative ``hbom_ref.uri`` is
                    resolved against for RFC-0005 HBOM-content policy rules,
                    normally the manifest file's own directory. ``None`` (the
                    default for in-memory callers) disables local-HBOM
                    resolution; HBOM-content rules then degrade to a
                    ``policy.hbom_uri_unreachable`` warning. The CLI passes the
                    manifest file's parent directory automatically.

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
    # RFC-0006: connectivity is a whole-program capability check.
    errors.extend(_check_connectivity_caps(manifest_model, envelope_model))
    # RFC-0250: substrate.autopilot_class is required for drone manifests.
    errors.extend(_check_substrate_required_for_drone(manifest_model))
    # RFC-0251: substrate.rmw_implementation + qos_profile rules.
    errors.extend(_check_substrate_rmw_options(manifest_model))
    # RFC-0385: substrate.ipc generation coherence.
    errors.extend(_check_substrate_ipc(manifest_model))
    # RFC-0477: substrate.clock time-synchronization coherence.
    errors.extend(_check_substrate_clock(manifest_model))
    # RFC-0478: substrate.bringup ordered-sequence coherence.
    errors.extend(_check_substrate_bringup(manifest_model))
    # RFC-0016: realtime timing-block coherence.
    errors.extend(_check_realtime(manifest_model))
    # RFC-0019: AUTOSAR ara::com program bindings must declare the full id triple.
    errors.extend(_check_program_bindings(manifest_model))
    # RFC-0290: the frame graph must be acyclic with declared parents.
    errors.extend(_check_frame_graph(manifest_model))
    # RFC-0384: whole-body kinematic structure + stability consistency.
    errors.extend(_check_whole_body_caps(manifest_model))
    # RFC-0518: base-level mobility-bounds coherence.
    errors.extend(_check_base_mobility_bounds(manifest_model))
    # RFC-0018: minimal sensor/actuator MCU-node declaration coherence.
    errors.extend(_check_minimal_node(manifest_model))
    # RFC-0260: Layer-4 NL-infrastructure (language block) coherence + advisories.
    for issue in _check_language_static(manifest_model):
        (warnings if issue.severity == "warning" else errors).append(issue)
    for issue in _check_language_primitives(program_model, manifest_model):
        (warnings if issue.severity == "warning" else errors).append(issue)
    # RFC-0262: license-boundary coherence (vendored-copyleft is a hard error).
    errors.extend(_check_licensing(manifest_model))
    # RFC-0268: deployment_class vs commercial_use consistency (warning).
    for issue in _check_deployment_consistency(manifest_model):
        (warnings if issue.severity == "warning" else errors).append(issue)

    # ----- Pass 3: envelope checks -----
    for path, step in walk_program(program_model):
        errors.extend(_check_envelope(step, manifest_model, envelope_model, path))
    # RFC-0006: link-loss policy coherence is a whole-envelope check.
    errors.extend(_check_link_loss_coherence(manifest_model, envelope_model))
    # RFC-0382: monitorable temporal-logic properties parse + resolve signals.
    errors.extend(_check_monitorable_properties(manifest_model, envelope_model))
    # RFC-0383: learned-policy training-envelope coherence (severity per enforcement).
    for issue in _check_learned_policy(manifest_model, envelope_model):
        (warnings if issue.severity == "warning" else errors).append(issue)

    # ----- Pass 4: variable bindings -----
    errors.extend(_check_bindings(program_model))

    # ----- Pass 5: compliance policy (RFC-0004; HBOM-content sub-pass RFC-0005) -----
    policy_model = _resolve_policy(policy, errors)
    if policy_model is not None:
        for issue in evaluate_policy(
            manifest_model, policy_model, manifest_base_dir=manifest_base_dir
        ):
            if issue.severity == "warning":
                warnings.append(issue)
            else:
                errors.append(issue)
        # RFC-0260: US-federal origin gate on a declared STT engine, enforced
        # only under the bundled default policy (the two-layer split: schema
        # accepts the value, policy refuses the substrate's origin).
        errors.extend(_check_language_origin_gate(manifest_model, policy_model))
        # RFC-0262: refuse a component more restrictive than the declared cap.
        errors.extend(_check_licensing_policy(manifest_model, policy_model))

    # RFC-0268: commercial-use gate. Under a policy a commercial deployment with
    # a commercial_use_gate component is an error; in default mode it is a soft
    # advisory. Runs regardless of policy state, so it sits outside the guard.
    for issue in _check_commercial_gate(manifest_model, policy_model is not None):
        (warnings if issue.severity == "warning" else errors).append(issue)

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
    if isinstance(node, OnMember):
        # RFC-0286: an `on:` scope is transparent to the single-robot passes —
        # they still see (and check) every step beneath it. The member handle is
        # only meaningful under `validate_fleet`; here the body's steps are
        # walked against whatever single manifest the caller passed.
        yield from _walk_behavior(node.body, [*path, "body"])
        return
    if isinstance(node, Barrier):
        # RFC-0286: a barrier is a leaf rendezvous marker, not a step. It carries
        # no primitive, so the per-step passes have nothing to check here.
        return
    raise TypeError(f"unexpected behavior node type: {type(node).__name__!r}")


# =============================================================================
# RFC-0286: fleet validation
# =============================================================================
#
# `validate_fleet` is the multi-robot entry point. It reuses every single-robot
# pass verbatim, re-keyed by fleet member, and adds four cross-robot checks:
#
#   fleet.undeclared_member             an `on:`/`barrier:` names a member the
#                                       roster does not declare (or a step in a
#                                       multi-member fleet is unaddressed).
#   fleet.capability_unsupported_on_member  a primitive scoped to a member whose
#                                       manifest fails the existing per-robot
#                                       capability check.
#   fleet.concurrent_shared_workspace   two members driven to the same declared
#                                       location concurrently in one `parallel`.
#   fleet.barrier_missing_peer_link     a `barrier` member lacks the `peer_link`
#                                       connectivity role (RFC-0006 reserved it).
#
# A single-robot program (no `on:`/`barrier:` node) validated through `validate`
# is wholly unaffected — none of this code runs on that path.


def walk_program_scoped(
    program: URMLProgram,
) -> Iterator[tuple[list[str], Step, str | None]]:
    """Like `walk_program`, but also yields the nearest enclosing `on:` member.

    The member is None for a step outside any `on:` scope. `validate_fleet`
    resolves None against the sole roster member (a fleet of one) or rejects it
    (an unaddressed step in a multi-member fleet).
    """
    yield from _walk_behavior_scoped(program.behavior, ["behavior"], None)


def _walk_behavior_scoped(
    node: object, path: list[str], member: str | None
) -> Iterator[tuple[list[str], Step, str | None]]:
    if isinstance(node, Step):
        yield path, node, member
        return
    if isinstance(node, Sequence):
        for idx, sub in enumerate(node.steps):
            yield from _walk_behavior_scoped(sub, [*path, "steps", str(idx)], member)
        return
    if isinstance(node, Branch):
        yield from _walk_behavior_scoped(node.if_true, [*path, "if_true"], member)
        if node.if_false is not None:
            yield from _walk_behavior_scoped(node.if_false, [*path, "if_false"], member)
        return
    if isinstance(node, Parallel):
        for idx, sub in enumerate(node.branches):
            yield from _walk_behavior_scoped(sub, [*path, "branches", str(idx)], member)
        return
    if isinstance(node, Retry):
        yield from _walk_behavior_scoped(node.behavior, [*path, "behavior"], member)
        return
    if isinstance(node, OnMember):
        yield from _walk_behavior_scoped(node.body, [*path, "body"], node.member)
        return
    if isinstance(node, Barrier):
        return
    raise TypeError(f"unexpected behavior node type: {type(node).__name__!r}")


def _iter_barriers(program: URMLProgram) -> Iterator[tuple[list[str], Barrier]]:
    """Yield every Barrier node in the program, with its path."""

    def visit(node: object, path: list[str]) -> Iterator[tuple[list[str], Barrier]]:
        if isinstance(node, Barrier):
            yield path, node
            return
        if isinstance(node, Sequence):
            for idx, sub in enumerate(node.steps):
                yield from visit(sub, [*path, "steps", str(idx)])
        elif isinstance(node, Branch):
            yield from visit(node.if_true, [*path, "if_true"])
            if node.if_false is not None:
                yield from visit(node.if_false, [*path, "if_false"])
        elif isinstance(node, Parallel):
            for idx, sub in enumerate(node.branches):
                yield from visit(sub, [*path, "branches", str(idx)])
        elif isinstance(node, Retry):
            yield from visit(node.behavior, [*path, "behavior"])
        elif isinstance(node, OnMember):
            yield from visit(node.body, [*path, "body"])

    yield from visit(program.behavior, ["behavior"])


def _step_location_names(step: Step) -> set[str]:
    """Declared-location names a step targets, for the workspace-collision check.

    Name-based and conservative: v0.1 has no workspace-volume geometry in the
    manifest, so two members are "in the same workspace" iff they target the
    same declared location *name*. A `workspace_volumes` block with polygon
    overlap is named as future work in RFC-0286.
    """
    name = step.primitive_name
    args = getattr(step, name)
    locs: set[str] = set()
    if name == "move_to" and args.location is not None:
        locs.add(args.location)
    elif name == "pick_from":
        locs.add(args.source)
    elif name == "place_at":
        locs.add(args.target)
    elif name == "dock" and args.at is not None:
        locs.add(args.at)
    elif name == "swap_tool":
        locs.add(args.at)
    return locs


# RFC-0291: medium is derived from drive_type, not declared. Air and water
# operations never share physical space.
_WATER_DRIVE_TYPES = {"underwater_thrusters"}


def _medium_of(manifest: CapabilityManifest) -> str | None:
    """The operating medium of a robot: 'air' | 'water' | 'ground' | None."""
    if manifest.mobility is None:
        return None
    drive = manifest.mobility.drive_type
    if drive in _AERIAL_DRIVE_TYPES:
        return "air"
    if drive in _WATER_DRIVE_TYPES:
        return "water"
    return "ground"


@dataclass(frozen=True)
class _MemberTarget:
    """One member's spatial target, resolved into the fleet's world (RFC-0291/0288).

    ``wx/wy/wz`` are world coordinates and ``world_id`` is the comparison frame id
    (the world frame for an anchored member, or the shared-frame name); two targets
    are compared only when both resolved to the same ``world_id``.
    """

    member: str | None
    name: str | None
    wx: float | None
    wy: float | None
    wz: float | None
    world_id: str | None
    radius: float | None
    vertical: float | None
    medium: str | None


def _step_member_targets(
    step: Step,
    member: str | None,
    manifest: CapabilityManifest,
    anchor: FrameAnchor | None,
    world_frame: str | None,
    shared_frames: set[str],
) -> list[_MemberTarget]:
    """Resolve a step's spatial targets to world-frame operational volumes."""
    medium = _medium_of(manifest)
    clearance = manifest.mobility.clearance if manifest.mobility is not None else None
    radius = clearance.radius_m if clearance is not None else None
    vertical = clearance.vertical_m if clearance is not None else None
    frames_by_name = {f.name: f for f in manifest.frames}

    def make(loc_name: str | None, x: float | None, y: float | None, z: float | None, frame: str | None) -> _MemberTarget:
        if x is None or y is None or frame is None:
            return _MemberTarget(member, loc_name, None, None, None, None, radius, vertical, medium)
        resolved = resolve_to_world(
            (x, y, z if z is not None else 0.0), frame, frames_by_name, anchor, world_frame, shared_frames
        )
        if resolved is None:
            return _MemberTarget(member, loc_name, None, None, None, None, radius, vertical, medium)
        (wx, wy, wz), world_id = resolved
        return _MemberTarget(member, loc_name, wx, wy, wz, world_id, radius, vertical, medium)

    name = step.primitive_name
    args = getattr(step, name)

    # move_to with an explicit pose+frame (no named location).
    if name == "move_to" and args.location is None and args.pose is not None and args.frame is not None:
        z = float(args.pose.z) if args.pose.z is not None else None
        return [make(None, float(args.pose.x), float(args.pose.y), z, args.frame)]

    out: list[_MemberTarget] = []
    for loc_name in _step_location_names(step):
        resolved = _location_pose_in_manifest(loc_name, manifest)
        if resolved is not None:
            x, y, z, frame = resolved
            out.append(make(loc_name, x, y, z, frame))
        else:
            out.append(make(loc_name, None, None, None, None))
    return out


def _collect_member_targets(
    node: object,
    member: str | None,
    members: Mapping[str, CapabilityManifest],
    anchors: Mapping[str, FrameAnchor | None],
    world_frame: str | None,
    shared_frames: set[str],
) -> list[_MemberTarget]:
    """All world-resolved operational volumes a subtree targets, honoring `on:`."""
    out: list[_MemberTarget] = []
    if isinstance(node, Step):
        if member is not None and member in members:
            out.extend(
                _step_member_targets(
                    node, member, members[member], anchors.get(member), world_frame, shared_frames
                )
            )
    elif isinstance(node, OnMember):
        out.extend(_collect_member_targets(node.body, node.member, members, anchors, world_frame, shared_frames))
    elif isinstance(node, Sequence):
        for sub in node.steps:
            out.extend(_collect_member_targets(sub, member, members, anchors, world_frame, shared_frames))
    elif isinstance(node, Branch):
        out.extend(_collect_member_targets(node.if_true, member, members, anchors, world_frame, shared_frames))
        if node.if_false is not None:
            out.extend(_collect_member_targets(node.if_false, member, members, anchors, world_frame, shared_frames))
    elif isinstance(node, Parallel):
        for sub in node.branches:
            out.extend(_collect_member_targets(sub, member, members, anchors, world_frame, shared_frames))
    elif isinstance(node, Retry):
        out.extend(_collect_member_targets(node.behavior, member, members, anchors, world_frame, shared_frames))
    return out


def _volumes_conflict(a: _MemberTarget, b: _MemberTarget) -> tuple[bool, dict[str, Any] | None]:
    """UTM strategic deconfliction between two world-resolved operational volumes.

    Conflict iff the volumes are NOT separated by world (both must resolve to the
    same world id), by medium (air and water never share space), laterally, or
    vertically. Temporal separation — a `barrier` — is handled by the caller, which
    only compares volumes inside one `parallel`.
    """
    # World gate: both must resolve to the same shared world.
    if a.world_id is None or b.world_id is None or a.world_id != b.world_id:
        return False, None
    # Medium gate: only air vs water is exempt (truly disjoint media). Air vs ground
    # is geometric — a low-flying drone can collide with a ground robot (RFC-0290).
    if a.medium is not None and b.medium is not None and {a.medium, b.medium} == {"air", "water"}:
        return False, None
    # Geometric (UTM): both must declare a clearance volume and have world coordinates.
    if (
        a.radius is not None and b.radius is not None
        and a.vertical is not None and b.vertical is not None
        and a.wx is not None and a.wy is not None and b.wx is not None and b.wy is not None
    ):
        lateral = hypot(a.wx - b.wx, a.wy - b.wy)
        az = a.wz if a.wz is not None else 0.0
        bz = b.wz if b.wz is not None else 0.0
        vertical_lo = max(az - a.vertical, bz - b.vertical)
        vertical_hi = min(az + a.vertical, bz + b.vertical)
        required = a.radius + b.radius
        if lateral < required and vertical_lo <= vertical_hi:
            return True, {
                "reason": "geometric",
                "frame": a.world_id,
                "lateral_m": round(lateral, 3),
                "required_lateral_m": round(required, 3),
                "media": [a.medium, b.medium],
            }
        return False, None
    # Name fallback (world-gated): same declared location name, no clearance declared.
    if a.name is not None and a.name == b.name:
        return True, {"reason": "name", "frame": a.world_id, "location": a.name}
    return False, None


def _check_concurrent_workspace(
    program: URMLProgram,
    sole_member: str | None,
    members: Mapping[str, CapabilityManifest],
    roster: FleetRoster,
) -> list[ValidationError]:
    """Reject two members whose operational volumes conflict in one `parallel`.

    The branches of a `parallel` run concurrently (one UTM time window); a
    `barrier` outside the parallel separates volumes in time. Within a window, each
    member's target is resolved into the fleet's world (via the member's `anchor`
    and frame graph, or a `shared_frames` name), and two distinct members conflict
    only if their world volumes are not separated by medium, laterally, or
    vertically (RFC-0291/0288). When a member declares no `clearance`, the
    comparison falls back to declared-location-name equality, world-gated.
    """
    out: list[ValidationError] = []
    anchors: Mapping[str, FrameAnchor | None] = {m.name: m.anchor for m in roster.members}
    world_frame = roster.world_frame
    shared_frames = roster.shared_frame_set

    def visit(node: object, path: list[str], member: str | None) -> None:
        if isinstance(node, Parallel):
            branch_targets = [
                _collect_member_targets(
                    sub, member if member is not None else sole_member,
                    members, anchors, world_frame, shared_frames,
                )
                for sub in node.branches
            ]
            reported: set[tuple[frozenset[str], str | None, str]] = set()
            for i in range(len(branch_targets)):
                for j in range(i + 1, len(branch_targets)):
                    for a in branch_targets[i]:
                        for b in branch_targets[j]:
                            if a.member is None or b.member is None or a.member == b.member:
                                continue
                            conflict, detail = _volumes_conflict(a, b)
                            if not conflict or detail is None:
                                continue
                            key = (frozenset({a.member, b.member}), a.world_id, detail["reason"])
                            if key in reported:
                                continue
                            reported.add(key)
                            out.append(_fleet_concurrent_workspace_error(path, a, b, detail))
            for idx, sub in enumerate(node.branches):
                visit(sub, [*path, "branches", str(idx)], member)
            return
        if isinstance(node, OnMember):
            visit(node.body, [*path, "body"], node.member)
        elif isinstance(node, Sequence):
            for idx, sub in enumerate(node.steps):
                visit(sub, [*path, "steps", str(idx)], member)
        elif isinstance(node, Branch):
            visit(node.if_true, [*path, "if_true"], member)
            if node.if_false is not None:
                visit(node.if_false, [*path, "if_false"], member)
        elif isinstance(node, Retry):
            visit(node.behavior, [*path, "behavior"], member)

    visit(program.behavior, ["behavior"], None)
    return out


def _fleet_undeclared_member_error(
    path: list[str], member: str | None, declared: set[str]
) -> ValidationError:
    declared_list = sorted(declared)
    if member is None:
        message = (
            "step is not addressed to any fleet member; wrap it in an `on:` node. "
            f"Declared members: {declared_list!r}."
        )
        suggestion = "Wrap this step in `{type: on, member: <name>, body: ...}`."
    else:
        message = (
            f"`on:`/`barrier:` references member {member!r}, which the roster does "
            f"not declare. Declared members: {declared_list!r}."
        )
        suggestion = f"Use a declared member name, or add {member!r} to the roster."
    return ValidationError(
        code=ErrorCode.FLEET_UNDECLARED_MEMBER,
        primitive=None,
        path=path,
        field="member",
        message=message,
        suggestion=suggestion,
        detail={"member": member, "declared_members": declared_list},
    )


def _rekey_capability_to_member(err: ValidationError, member: str) -> ValidationError:
    """Re-wrap a single-robot capability error as a fleet member-scoped error.

    The underlying predicate (and its message/suggestion) is reused verbatim;
    only the code changes and the offending member is named, so the LLM bridge
    knows the fix belongs to one member's manifest, not the shared program.
    """
    return ValidationError(
        code=ErrorCode.FLEET_CAPABILITY_UNSUPPORTED_ON_MEMBER,
        primitive=err.primitive,
        path=err.path,
        field=err.field,
        message=f"member {member!r}: {err.message}",
        suggestion=err.suggestion,
        detail={"member": member, "underlying": err.code_str},
    )


def _fleet_concurrent_workspace_error(
    path: list[str], a: _MemberTarget, b: _MemberTarget, detail: dict[str, Any]
) -> ValidationError:
    pair = sorted({m for m in (a.member, b.member) if m is not None})
    if detail["reason"] == "geometric":
        what = (
            f"their operational volumes overlap in frame {detail['frame']!r} "
            f"({detail['lateral_m']} m apart laterally, vertical bands overlapping; "
            f"they need {detail['required_lateral_m']} m of lateral separation)"
        )
    else:
        what = (
            f"both target the declared location {detail['location']!r} in shared "
            f"frame {detail['frame']!r} (no clearance declared, so name-based)"
        )
    return ValidationError(
        code=ErrorCode.FLEET_CONCURRENT_SHARED_WORKSPACE,
        primitive=None,
        path=path,
        field="branches",
        message=(
            f"members {pair[0]!r} and {pair[1]!r} run concurrently in one `parallel` "
            f"with no barrier and {what} — a cross-robot collision risk."
        ),
        suggestion=(
            "Separate them with a `barrier` (temporal deconfliction), raise their "
            "declared `clearance`, or send them to non-overlapping volumes."
        ),
        detail={"members": pair, **detail},
    )


def _fleet_barrier_peer_link_error(
    path: list[str], member: str
) -> ValidationError:
    return ValidationError(
        code=ErrorCode.FLEET_BARRIER_MISSING_PEER_LINK,
        primitive=None,
        path=path,
        field="members",
        message=(
            f"barrier synchronizes member {member!r}, but that member's manifest "
            f"declares no `peer_link` connectivity role required to rendezvous."
        ),
        suggestion=(
            f"Add a `connectivity` link with role 'peer_link' to {member!r}'s "
            "manifest, or remove it from the barrier."
        ),
        detail={"member": member},
    )


def validate_fleet(
    roster: dict[str, Any] | FleetRoster,
    member_manifests: Mapping[str, dict[str, Any] | CapabilityManifest],
    program: dict[str, Any] | URMLProgram,
    member_envelopes: Mapping[str, dict[str, Any] | SafetyEnvelope] | None = None,
    profiles: tuple[str, ...] = (),
    policy: dict[str, Any] | Policy | None | Literal["DEFAULT"] = "DEFAULT",
) -> ValidationResult:
    """Validate a multi-robot fleet program against a roster of member manifests.

    Args:
        roster:           The fleet roster. Raw dict or `FleetRoster`.
        member_manifests: ``{member_name -> manifest}`` for every roster member.
                          Each manifest is a raw dict or `CapabilityManifest`.
        program:          The fleet program (one tree with `on:`/`barrier:` nodes).
        member_envelopes: Optional ``{member_name -> envelope}`` for per-member
                          envelope checks. Members without an envelope are
                          envelope-unchecked, exactly like the single-robot path.
        profiles:         Informational, as in `validate`.
        policy:           Compliance policy for Pass 5; evaluated per member
                          manifest. ``"DEFAULT"`` / ``None`` / dict / `Policy`,
                          same contract as `validate`.

    Returns:
        A `ValidationResult` aggregating single-robot passes (re-keyed by member)
        and the four cross-robot `fleet.*` checks.
    """
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # ----- roster (Pass-1-style; a bad roster is a hard stop) -----
    try:
        roster_model: FleetRoster = (
            roster if isinstance(roster, FleetRoster) else FleetRoster.model_validate(roster)
        )
    except PydanticValidationError as exc:
        for e in _pydantic_errors_to_validation_errors(exc):
            e.path = ["<roster>", *e.path]
            errors.append(e)
        return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    # ----- program (Pass 1) -----
    try:
        program_model: URMLProgram = (
            program if isinstance(program, URMLProgram) else URMLProgram.model_validate(program)
        )
    except PydanticValidationError as exc:
        errors.extend(_pydantic_errors_to_validation_errors(exc))
        return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    # ----- member manifests -----
    members: dict[str, CapabilityManifest] = {}
    for name, raw in member_manifests.items():
        try:
            members[name] = (
                raw if isinstance(raw, CapabilityManifest) else CapabilityManifest.model_validate(raw)
            )
        except PydanticValidationError as exc:
            for e in _pydantic_errors_to_validation_errors(exc):
                e.path = ["<manifest>", name, *e.path]
                errors.append(e)
    # Every declared member needs a resolved manifest.
    for member_name in sorted(roster_model.member_names):
        if member_name not in members:
            errors.append(
                ValidationError(
                    code=ErrorCode.FLEET_UNDECLARED_MEMBER,
                    primitive=None,
                    path=["<roster>", "members"],
                    field="manifest",
                    message=(
                        f"roster declares member {member_name!r} but no manifest was "
                        f"resolved for it."
                    ),
                    suggestion=f"Provide member_manifests[{member_name!r}].",
                    detail={"member": member_name},
                )
            )
    # RFC-0290: each member's frame graph must be well-formed.
    for member_name in sorted(members):
        for err in _check_frame_graph(members[member_name]):
            err.detail = {**(err.detail or {}), "member": member_name}
            errors.append(err)
    if errors:
        return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    # ----- member envelopes (optional) -----
    envelopes: dict[str, SafetyEnvelope] = {}
    if member_envelopes:
        for name, raw_env in member_envelopes.items():
            if raw_env is None:
                continue
            try:
                envelopes[name] = (
                    raw_env
                    if isinstance(raw_env, SafetyEnvelope)
                    else SafetyEnvelope.model_validate(raw_env)
                )
            except PydanticValidationError as exc:
                for e in _pydantic_errors_to_validation_errors(exc):
                    e.path = ["<envelope>", name, *e.path]
                    errors.append(e)
        if errors:
            return ValidationResult(accepted=False, errors=errors, warnings=warnings)

    declared = roster_model.member_names
    sole_member = next(iter(declared)) if len(declared) == 1 else None

    # ----- Pass 2/3 per step, re-keyed by member -----
    for path, step, member in walk_program_scoped(program_model):
        effective = member if member is not None else sole_member
        if effective is None or effective not in declared:
            errors.append(_fleet_undeclared_member_error(path, member, declared))
            continue
        manifest = members[effective]
        for cap_err in _check_capabilities(step, manifest, path):
            errors.append(_rekey_capability_to_member(cap_err, effective))
        env = envelopes.get(effective)
        for env_err in _check_envelope(step, manifest, env, path):
            env_err.detail = {**(env_err.detail or {}), "member": effective}
            errors.append(env_err)

    # ----- Barriers: declared-membership + peer_link role -----
    for path, barrier in _iter_barriers(program_model):
        for member_name in barrier.members:
            if member_name not in declared:
                errors.append(_fleet_undeclared_member_error(path, member_name, declared))
                continue
            manifest = members[member_name]
            link = (
                manifest.connectivity.link_for(LinkRole.PEER_LINK)
                if manifest.connectivity is not None
                else None
            )
            if link is None:
                errors.append(_fleet_barrier_peer_link_error(path, member_name))

    # ----- Cross-robot workspace collision (RFC-0291/0288 strategic deconfliction) -----
    shared_frames = roster_model.shared_frame_set
    declared_frames = {f.name for m in members.values() for f in m.frames}
    errors.extend(_check_concurrent_workspace(program_model, sole_member, members, roster_model))
    # A shared_frame no member declares silently disables the geometric check for it.
    for frame in sorted(shared_frames - declared_frames):
        warnings.append(
            ValidationError(
                code=ErrorCode.FLEET_SHARED_FRAME_UNDECLARED,
                primitive=None,
                severity="warning",
                path=["<roster>", "shared_frames"],
                field="shared_frames",
                message=(
                    f"roster declares shared frame {frame!r}, but no member's manifest "
                    f"declares a frame by that name; the geometric collision check will "
                    f"not compare any targets in it."
                ),
                suggestion=f"Remove {frame!r} from shared_frames, or declare it in a member's frames.",
                detail={"frame": frame},
            )
        )
    # RFC-0290: a world-anchor whose frame the member does not declare silently
    # disables resolution for that member.
    for rmember in roster_model.members:
        if rmember.anchor is not None and rmember.anchor.frame not in {
            f.name for f in members[rmember.name].frames
        }:
            warnings.append(
                ValidationError(
                    code=ErrorCode.FLEET_ANCHOR_FRAME_UNDECLARED,
                    primitive=None,
                    severity="warning",
                    path=["<roster>", "members"],
                    field="anchor",
                    message=(
                        f"member {rmember.name!r} anchors frame {rmember.anchor.frame!r} to the "
                        f"world, but its manifest declares no frame by that name; its targets "
                        f"will not resolve to the world."
                    ),
                    suggestion=f"Anchor a frame {rmember.name!r} actually declares.",
                    detail={"member": rmember.name, "frame": rmember.anchor.frame},
                )
            )

    # ----- Pass 4: bindings across the whole fleet tree -----
    errors.extend(_check_bindings(program_model))

    # ----- Pass 5: compliance policy, per member manifest -----
    policy_model = _resolve_policy(policy, errors)
    if policy_model is not None:
        for member_name in sorted(members):
            for issue in evaluate_policy(members[member_name], policy_model):
                issue.detail = {**(issue.detail or {}), "member": member_name}
                if issue.severity == "warning":
                    warnings.append(issue)
                else:
                    errors.append(issue)

    return ValidationResult(accepted=not errors, errors=errors, warnings=warnings)


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
    "bimanual",
    "detect",
    "scan",
    "measure",
    "capture",
    "report",
    "speak",
    "listen",
    "take_off",
    "land",
    "return_to_home",
    "pick_from",
    "place_at",
    "swap_tool",
    "plan_path",
    "follow_trajectory",
    "set_output",
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
    if name == "bimanual":
        return _check_bimanual_caps(args, manifest, path)
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
    if name == "take_off":
        return _check_take_off_caps(args, manifest, path)
    if name == "land":
        return _check_land_caps(args, manifest, path)
    if name == "return_to_home":
        return _check_return_to_home_caps(args, manifest, path)
    if name == "pick_from":
        return _check_pick_from_caps(args, manifest, path)
    if name == "place_at":
        return _check_place_at_caps(args, manifest, path)
    if name == "swap_tool":
        return _check_swap_tool_caps(args, manifest, path)
    if name == "call_program":
        return _check_call_program_caps(args, manifest, path)
    if name == "plan_path":
        return _check_plan_path_caps(args, manifest, path)
    if name == "follow_trajectory":
        return _check_follow_trajectory_caps(args, manifest, path)
    if name == "set_output":
        return _check_set_output_caps(args, manifest, path)
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


def _check_minimal_node(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0018: minimal sensor/actuator MCU-node declaration coherence.

    Manifest-static checks (no per-program enforcement in v0.1, which is deferred):
    `minimal_node` and `mobility` are mutually exclusive (a thing either drives or
    declares it does not); `has_locomotion` must be False; declared outputs must be
    real `outputs.lines[]` (the RFC-0017 lines a minimal node's `set_output`
    targets); declared sensors must exist in `perception.sensors` when that block
    is present.
    """
    out: list[ValidationError] = []
    mn = manifest.minimal_node
    if mn is None:
        return out

    if manifest.mobility is not None:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_MINIMAL_NODE_WITH_MOBILITY,
                primitive=None,
                path=["<manifest>", "minimal_node"],
                field="minimal_node",
                message=(
                    "manifest declares both `minimal_node` and `mobility`; they are "
                    "mutually exclusive (a minimal node does not move)."
                ),
                suggestion="Remove `mobility` for a minimal node, or remove `minimal_node` if the robot drives.",
            )
        )
    if mn.has_locomotion:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_MINIMAL_NODE_LOCOMOTION_INCONSISTENT,
                primitive=None,
                path=["<manifest>", "minimal_node", "has_locomotion"],
                field="has_locomotion",
                message="`minimal_node.has_locomotion` must be False; declare a `mobility` block instead if the node moves.",
                suggestion="Set has_locomotion: false and (if it drives) declare `mobility`.",
            )
        )
    line_names = {ln.name for ln in manifest.outputs.lines}
    for output in mn.declared_outputs:
        if output not in line_names:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_MINIMAL_NODE_UNDECLARED_OUTPUT,
                    primitive=None,
                    path=["<manifest>", "minimal_node", "declared_outputs"],
                    field="declared_outputs",
                    message=(
                        f"minimal_node.declared_outputs names {output!r}, which is not a "
                        f"declared `outputs.lines[]` line."
                    ),
                    suggestion=f"Declare an output line named {output!r} in outputs.lines (RFC-0017), or fix the name.",
                    detail={"output": output},
                )
            )
    if manifest.perception is not None:
        sensor_names = {s.name for s in manifest.perception.sensors}
        for sensor in mn.declared_sensors:
            if sensor not in sensor_names:
                out.append(
                    ValidationError(
                        code=ErrorCode.CAPABILITY_MINIMAL_NODE_UNDECLARED_SENSOR,
                        primitive=None,
                        path=["<manifest>", "minimal_node", "declared_sensors"],
                        field="declared_sensors",
                        message=(
                            f"minimal_node.declared_sensors names {sensor!r}, which is not in "
                            f"`perception.sensors`."
                        ),
                        suggestion=f"Add a sensor named {sensor!r} to perception.sensors, or fix the name.",
                        detail={"sensor": sensor},
                    )
                )
    return out


# US-federal default policy id (RFC-0004). The vosk origin gate (RFC-0260)
# fires only when this exact policy is in effect, not under a custom policy.
_US_FEDERAL_DEFAULT_POLICY_ID = "urml_us_federal_default"

# Declared engine classes that carry a license shape worth a human's attention.
# Advisory only (warning); URML records the declaration, it does not adjudicate
# the license. The commercial-eligibility mechanism is a separate RFC (0262/0304).
_ENGINE_LICENSE_ADVISORIES = {
    ("tts_engine_class", "piper"): "piper is GPL-3.0; integrate it across a subprocess boundary.",
    (
        "translation_engine_class",
        "nllb",
    ): "NLLB-200 weights are CC-BY-NC 4.0 (non-commercial); declared for cross-citation, not a URML default.",
    (
        "translation_engine_class",
        "libretranslate",
    ): "LibreTranslate is AGPL-3.0; integrate it across a network (REST) boundary.",
}


def _check_language_static(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0260: manifest-static `language` checks (advisories + consistency).

    All warnings: a translation block whose `target_languages` is empty (a
    translation engine that emits no language is incoherent), and license-shape
    advisories for copyleft / non-commercial engine declarations. Schema-level
    coherence (`custom` requires a `_note`, closed enums) is enforced by the
    pydantic model; the origin gate (vosk) is policy-dependent and lives in
    `_check_language_origin_gate`.
    """
    out: list[ValidationError] = []
    lang = manifest.language
    if lang is None:
        return out

    for field, value in (
        ("stt_engine_class", lang.stt_engine_class),
        ("tts_engine_class", lang.tts_engine_class),
        ("translation_engine_class", lang.translation_engine_class),
    ):
        advisory = _ENGINE_LICENSE_ADVISORIES.get((field, value))
        if advisory is not None:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_ENGINE_LICENSE_ADVISORY,
                    severity="warning",
                    primitive=None,
                    path=["<manifest>", "language", field],
                    field=field,
                    message=f"language.{field} {value!r}: {advisory}",
                    detail={"engine_class": value, "field": field},
                )
            )

    opts = lang.engine_options
    if (
        lang.translation_engine_class is not None
        and opts is not None
        and opts.translation is not None
        and not opts.translation.target_languages
    ):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_TRANSLATION_LANGUAGES_INCONSISTENT,
                severity="warning",
                primitive=None,
                path=["<manifest>", "language", "engine_options", "translation"],
                field="target_languages",
                message=(
                    "a translation engine is declared but engine_options.translation."
                    "target_languages is empty; declare at least one target language."
                ),
            )
        )
    return out


def _check_language_primitives(
    program: URMLProgram, manifest: CapabilityManifest
) -> list[ValidationError]:
    """RFC-0260: a program that uses `listen`/`speak` should declare the engine.

    Soft suggestion (warning): if any active step is `listen` and no
    `language.stt_engine_class` is declared (same for `speak` <-> tts), the
    pipeline cannot be reasoned about. Recommended, not required.
    """
    out: list[ValidationError] = []
    lang = manifest.language
    uses_listen = any(step.primitive_name == "listen" for _, step in walk_program(program))
    uses_speak = any(step.primitive_name == "speak" for _, step in walk_program(program))

    if uses_listen and (lang is None or lang.stt_engine_class is None):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_STT_ENGINE_UNDECLARED,
                severity="warning",
                primitive="listen",
                path=["<manifest>", "language", "stt_engine_class"],
                field="stt_engine_class",
                message=(
                    "program uses `listen` but the manifest declares no "
                    "language.stt_engine_class; the speech-to-text substrate is undeclared."
                ),
                suggestion="Declare language.stt_engine_class (e.g. whisper, whisper_cpp).",
            )
        )
    if uses_speak and (lang is None or lang.tts_engine_class is None):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_TTS_ENGINE_UNDECLARED,
                severity="warning",
                primitive="speak",
                path=["<manifest>", "language", "tts_engine_class"],
                field="tts_engine_class",
                message=(
                    "program uses `speak` but the manifest declares no "
                    "language.tts_engine_class; the text-to-speech substrate is undeclared."
                ),
                suggestion="Declare language.tts_engine_class (e.g. piper, espeak).",
            )
        )
    return out


def _check_language_origin_gate(
    manifest: CapabilityManifest, policy_model: Policy
) -> list[ValidationError]:
    """RFC-0260: refuse a Russian-origin STT engine under the US-federal default.

    Two-layer split: the schema accepts `stt_engine_class: vosk`, but the bundled
    default compliance policy (and only that policy) refuses it on US-federal
    origin grounds. A custom policy or `--no-policy` accepts it.
    """
    lang = manifest.language
    if (
        lang is None
        or lang.stt_engine_class != "vosk"
        or policy_model.policy_id != _US_FEDERAL_DEFAULT_POLICY_ID
    ):
        return []
    return [
        ValidationError(
            code=ErrorCode.POLICY_STT_ENGINE_ORIGIN_DENIED,
            primitive=None,
            path=["<manifest>", "language", "stt_engine_class"],
            field="stt_engine_class",
            message=(
                "language.stt_engine_class 'vosk' is Russian-origin and refused under the "
                "US-federal default compliance policy. Accepted under --no-policy or a custom policy."
            ),
            suggestion="Use a non-covered STT engine (e.g. whisper, whisper_cpp), or run without the default policy.",
            detail={"engine_class": "vosk", "policy_id": policy_model.policy_id},
        )
    ]


def _check_licensing(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0262: license-boundary coherence (manifest-static, policy-independent).

    Vendoring a non-Apache-2.0-compatible (copyleft / non-commercial) license is
    a hard error: URML's Apache-2.0 source may not pull in such source. The legal
    integration shapes for those licenses are subprocess, network, or
    cross-citation. (`network_rest` requiring an endpoint is enforced at parse by
    the LicenseComponent model.)
    """
    out: list[ValidationError] = []
    if manifest.licensing is None:
        return out
    for comp in manifest.licensing.components:
        if comp.boundary == "vendored" and comp.license not in VENDORABLE_LICENSES:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_LICENSE_VENDORED_COPYLEFT,
                    primitive=None,
                    path=["<manifest>", "licensing", "components", comp.name],
                    field="boundary",
                    message=(
                        f"licensing component {comp.name!r} declares boundary 'vendored' for "
                        f"license {comp.license!r}, which is not Apache-2.0-compatible. URML may "
                        f"not vendor copyleft / non-commercial source."
                    ),
                    suggestion="Use boundary: subprocess, network_rest, or cross_citation for this license.",
                    detail={"component": comp.name, "license": comp.license},
                )
            )
    return out


def _check_licensing_policy(
    manifest: CapabilityManifest, policy_model: Policy
) -> list[ValidationError]:
    """RFC-0262: refuse a component more restrictive than the declared cap.

    When `licensing.policy_required_max_restrictiveness` is set and a compliance
    policy is enforced, every component's license must be at or below the cap on
    the restrictiveness ordering. Policy-independent of which policy: any active
    policy enforces the manifest's own declared cap.
    """
    out: list[ValidationError] = []
    licensing = manifest.licensing
    if licensing is None or licensing.policy_required_max_restrictiveness is None:
        return out
    cap = licensing.policy_required_max_restrictiveness
    cap_rank = LICENSE_RESTRICTIVENESS.index(cap)
    for comp in licensing.components:
        if LICENSE_RESTRICTIVENESS.index(comp.license) > cap_rank:
            out.append(
                ValidationError(
                    code=ErrorCode.POLICY_LICENSE_TOO_RESTRICTIVE,
                    primitive=None,
                    path=["<manifest>", "licensing", "components", comp.name],
                    field="license",
                    message=(
                        f"licensing component {comp.name!r} license {comp.license!r} is more "
                        f"restrictive than the declared policy_required_max_restrictiveness {cap!r}."
                    ),
                    suggestion=f"Use a component at or below {cap!r}, or raise the declared cap.",
                    detail={"component": comp.name, "license": comp.license, "max": cap},
                )
            )
    return out


# Deployment classes whose conventional posture is non-commercial (RFC-0268).
_NONCOMMERCIAL_CLASSES = frozenset({"research", "education", "hobby"})


def _deployment_is_commercial(manifest: CapabilityManifest) -> bool:
    """Effective commercial posture: true unless explicitly declared false.

    A missing `deployment` block defaults to commercial (most-restrictive); a
    present block uses its `commercial_use` field (itself defaulting to true).
    """
    return manifest.deployment.commercial_use if manifest.deployment is not None else True


def _check_deployment_consistency(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0268: a non-commercial-looking class declared commercial draws a warning.

    `deployment_class: research` (or education / hobby) together with
    `commercial_use: true` is allowed but surfaced, so the deliberate choice is
    visible rather than a copy-paste slip.
    """
    out: list[ValidationError] = []
    dep = manifest.deployment
    if dep is None or dep.deployment_class is None:
        return out
    if dep.deployment_class in _NONCOMMERCIAL_CLASSES and dep.commercial_use:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_COMMERCIAL_USE_CLASS_INCONSISTENT,
                severity="warning",
                primitive=None,
                path=["<manifest>", "deployment", "commercial_use"],
                field="commercial_use",
                message=(
                    f"deployment_class {dep.deployment_class!r} is conventionally non-commercial "
                    f"but commercial_use is true; confirm this is deliberate."
                ),
                detail={"deployment_class": dep.deployment_class, "commercial_use": True},
            )
        )
    return out


def _permissive_translation_alternative(manifest: CapabilityManifest):
    """RFC-0304: the first declared commercial-eligible translation alternative, if any.

    Returns the `TranslationAlternative` a commercial deployment may fall back to
    (Qwen / Gemma open LLM, a permissive opus_mt, ...), or None. The
    `commercial_eligible` flag is a declaration (RFC-0268 stance); the deployer
    pairs it with a permissive `licensing.components[]` entry.
    """
    lang = manifest.language
    if lang is None:
        return None
    for alt in lang.translation_alternatives:
        if alt.commercial_eligible:
            return alt
    return None


def _is_translation_substrate(comp, manifest: CapabilityManifest) -> bool:
    """RFC-0304: is this gated component the (CC-BY-NC) translation substrate?

    Scoped to the case RFC-0304 is built around: a declared translation engine
    whose weights are CC-BY-NC (NLLB-200). A permissive translation alternative
    excuses this gate; it does not excuse an unrelated gated component.
    """
    lang = manifest.language
    return (
        lang is not None
        and lang.translation_engine_class is not None
        and comp.license == "cc_by_nc_4_0"
    )


def _check_commercial_gate(
    manifest: CapabilityManifest, policy_active: bool
) -> list[ValidationError]:
    """RFC-0268: a commercial deployment may not declare a gated component.

    Closes RFC-0262's loop. When the deployment is commercial (declared, or the
    most-restrictive default) and a `licensing.components[]` entry sets
    `commercial_use_gate: true` (NLLB-200 CC-BY-NC weights, an AGPL surface),
    that is a violation. Under a compliance policy it is an error; in default
    mode it is a soft advisory naming the component. A `commercial_use: false`
    deployment satisfies the gate.

    RFC-0304: a gated *translation* substrate (a CC-BY-NC translation engine,
    the NLLB case) is excused when the deployment declares a commercial-eligible
    `language.translation_alternatives` entry. The hard failure becomes a fork:
    the validator records (informational) that the commercial deployment must
    use the declared permissive alternative, instead of refusing the manifest.
    """
    out: list[ValidationError] = []
    if not _deployment_is_commercial(manifest) or manifest.licensing is None:
        return out

    # RFC-0304: a declared commercial-eligible translation alternative satisfies
    # the gate for a CC-BY-NC translation substrate (the NLLB-plus-permissive-LLM
    # path the NLLB maintainer recommended on RFC-0167).
    permissive_alt = _permissive_translation_alternative(manifest)

    for comp in manifest.licensing.components:
        if not comp.commercial_use_gate:
            continue
        if permissive_alt is not None and _is_translation_substrate(comp, manifest):
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_COMMERCIAL_GATE_SATISFIED_BY_ALTERNATIVE,
                    severity="warning",
                    primitive=None,
                    path=["<manifest>", "language", "translation_alternatives"],
                    field="commercial_eligible",
                    message=(
                        f"commercial deployment's gated translation substrate {comp.name!r} "
                        f"({comp.license!r}) is satisfied by the declared commercial-eligible "
                        f"alternative {permissive_alt.engine_class!r}"
                        + (f" ({permissive_alt.engine_class_note})" if permissive_alt.engine_class_note else "")
                        + "; the commercial deployment must use that alternative."
                    ),
                    detail={
                        "gated_component": comp.name,
                        "gated_license": comp.license,
                        "alternative_engine_class": permissive_alt.engine_class,
                        "alternative_note": permissive_alt.engine_class_note,
                    },
                )
            )
            continue
        if policy_active:
            out.append(
                ValidationError(
                    code=ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED,
                    primitive=None,
                    path=["<manifest>", "licensing", "components", comp.name],
                    field="commercial_use_gate",
                    message=(
                        f"commercial deployment declares component {comp.name!r} with "
                        f"commercial_use_gate (license {comp.license!r}); a commercial deployment "
                        f"may not use a non-commercial component."
                    ),
                    suggestion="Declare deployment.commercial_use: false (if non-commercial), or replace the gated component.",
                    detail={"component": comp.name, "license": comp.license},
                )
            )
        else:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_COMMERCIAL_GATE_ADVISORY,
                    severity="warning",
                    primitive=None,
                    path=["<manifest>", "licensing", "components", comp.name],
                    field="commercial_use_gate",
                    message=(
                        f"deployment is commercial (declared or defaulted) and component "
                        f"{comp.name!r} is commercial-use-gated; under --policy this would fail. "
                        f"Declare deployment.commercial_use explicitly to resolve."
                    ),
                    detail={"component": comp.name, "license": comp.license},
                )
            )
    return out


def _check_frame_graph(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0290: the frame graph must be a forest — every `parent` declared, no cycle."""
    out: list[ValidationError] = []
    by_name = {f.name: f for f in manifest.frames}
    for frame in manifest.frames:
        if frame.parent is not None and frame.parent not in by_name:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_FRAME_PARENT_UNDECLARED,
                    primitive=None,
                    path=["<manifest>", "frames"],
                    field="parent",
                    message=(
                        f"frame {frame.name!r} declares parent {frame.parent!r}, which is "
                        f"not a declared frame."
                    ),
                    suggestion=f"Declare a frame named {frame.parent!r}, or fix the parent.",
                    detail={"frame": frame.name, "parent": frame.parent},
                )
            )
    # Cycle detection: walk each frame to its root; report the first cycle once.
    cycle: list[str] = []
    for frame in manifest.frames:
        seen: list[str] = []
        current: Frame | None = frame
        while current is not None and current.parent is not None:
            if current.name in seen:
                cycle = [*seen[seen.index(current.name):], current.name]
                break
            seen.append(current.name)
            current = by_name.get(current.parent)
        if cycle:
            break
    if cycle:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_FRAME_CYCLE,
                primitive=None,
                path=["<manifest>", "frames"],
                field="parent",
                message=f"frame graph has a cycle: {' -> '.join(cycle)}. Frames must form a tree.",
                suggestion="Break the parent cycle so the frame graph is acyclic.",
                detail={"cycle": cycle},
            )
        )
    return out


def _xy_in_polygon(x: float, y: float, polygon: list) -> bool:
    """Ray-casting point-in-polygon test (even-odd rule).

    `polygon` is a list of objects with `.x` / `.y`. Used by RFC-0384 to check a
    declared center of mass against a declared support polygon. Boundary points
    are not guaranteed inside; that edge case is the manifest author's call.
    (Distinct from `_point_in_polygon`, the geofence helper, which takes tuples.)
    """
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i].x, polygon[i].y
        xj, yj = polygon[j].x, polygon[j].y
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _check_whole_body_caps(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0384: validate the whole-body declaration against the rest of the manifest.

    - leg-chain count matches a legged `drive_type` (biped=2, quadruped=4);
    - each arm chain's `arm_ref` resolves to a declared `manipulation.arms[].name`;
    - a declared center of mass lies within the declared support polygon.

    All checks are skipped when `whole_body` is absent (the block is optional).
    """
    wb = manifest.whole_body
    if wb is None:
        return []
    out: list[ValidationError] = []
    path = ["<manifest>", "whole_body"]

    # Leg-chain count vs drive_type (only when legs are declared and drive_type is legged).
    legs = [c for c in wb.chains if c.kind == "leg"]
    if legs and manifest.mobility is not None:
        expected = {"biped": 2, "quadruped": 4}.get(manifest.mobility.drive_type)
        if expected is not None and len(legs) != expected:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_WHOLE_BODY_INCONSISTENT,
                    "whole_body",
                    path + ["chains"],
                    f"drive_type {manifest.mobility.drive_type!r} expects {expected} leg "
                    f"chains but whole_body declares {len(legs)}.",
                    field="chains",
                    suggestion=f"Declare exactly {expected} chains of kind 'leg', or correct drive_type.",
                )
            )

    # Arm chains must reference a declared arm (when manipulation.arms is declared).
    declared_arms = (
        {a.name for a in manifest.manipulation.arms}
        if manifest.manipulation is not None
        else set()
    )
    for chain in wb.chains:
        if chain.kind == "arm" and chain.arm_ref is not None and chain.arm_ref not in declared_arms:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_WHOLE_BODY_INCONSISTENT,
                    "whole_body",
                    path + ["chains"],
                    f"whole_body arm chain {chain.name!r} references arm {chain.arm_ref!r}, "
                    f"not declared in manipulation.arms (declared: {sorted(declared_arms)!r}).",
                    field="arm_ref",
                    suggestion="Add the arm to manipulation.arms, or fix the arm_ref.",
                )
            )

    # Static stability: a declared CoM must lie within the declared support polygon.
    if wb.center_of_mass is not None and wb.support_polygon is not None:
        if not _xy_in_polygon(wb.center_of_mass.x, wb.center_of_mass.y, wb.support_polygon):
            out.append(
                _err(
                    ErrorCode.CAPABILITY_WHOLE_BODY_UNSTABLE_COM,
                    "whole_body",
                    path + ["center_of_mass"],
                    "declared center_of_mass (x, y) lies outside the declared support_polygon; "
                    "the static-stability declaration is inconsistent.",
                    field="center_of_mass",
                    suggestion="Move the CoM within the support polygon, or correct the polygon vertices.",
                )
            )
    return out


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
    # RFC-0384: a legged platform that cannot carry while moving rejects move_to(carrying=...).
    if (
        args.carrying is not None
        and manifest.mobility is not None
        and manifest.mobility.drive_type in ("biped", "quadruped")
        and manifest.whole_body is not None
        and not manifest.whole_body.can_carry_while_moving
    ):
        out.append(
            _err(
                ErrorCode.CAPABILITY_CANNOT_CARRY_WHILE_MOVING,
                "move_to",
                path,
                "move_to carries a payload, but the manifest declares the legged platform "
                "cannot carry while moving (whole_body.can_carry_while_moving = false).",
                field="carrying",
                suggestion="Set whole_body.can_carry_while_moving: true, or stage the carry "
                "as a stationary handoff.",
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


def _check_arm_addressable(
    arm: str, manifest: CapabilityManifest, primitive: str, path: list[str]
) -> list[ValidationError]:
    """RFC-0010: an addressed arm must exist.

    `any` (the default) always resolves. `left`/`right` resolve when
    `arm_count >= 2` or a declared arm carries that name. A named arm must
    appear in `manipulation.arms`. Assumes the caller has already confirmed
    `manipulation` is present.
    """
    if arm == "any":
        return []
    manip = manifest.manipulation
    if manip is None:
        return []  # missing-manipulation already reported by the caller
    declared = {a.name for a in manip.arms}
    if arm in declared:
        return []
    if arm in ("left", "right") and manip.arm_count >= 2:
        return []
    return [
        _err(
            ErrorCode.CAPABILITY_ARM_NOT_DECLARED,
            primitive,
            path,
            f"{primitive} addresses arm {arm!r} but the manifest does not declare it "
            f"(arm_count={manip.arm_count}, declared arms={sorted(declared)!r}).",
            field="arm",
            suggestion="Use arm: any, set arm_count >= 2 for left/right addressing, "
            "or declare the arm in manipulation.arms.",
        )
    ]


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
    out += _check_arm_addressable(args.arm, manifest, "grasp", path)
    return out


def _check_release_caps(
    args: ReleaseArgs, manifest: CapabilityManifest, path: list[str]
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
    out += _check_arm_addressable(args.arm, manifest, "release", path)
    return out


def _check_bimanual_caps(
    args: BimanualArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """RFC-0010: `bimanual` requires two arms; each side is a grasp/release
    sub-intent validated exactly like its single-arm form."""
    out: list[ValidationError] = []
    manip = manifest.manipulation
    if manip is None or not manip.grippers:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MANIPULATION,
                "bimanual",
                path,
                "bimanual requires the manifest to declare `manipulation` with at least one gripper.",
                suggestion="Add a `manipulation` block with grippers and two arms.",
            )
        )
        return out
    if manip.arm_count < 2 and len(manip.arms) < 2:
        out.append(
            _err(
                ErrorCode.CAPABILITY_BIMANUAL_REQUIRES_TWO_ARMS,
                "bimanual",
                path,
                f"bimanual requires two arms (arm_count >= 2 or two declared arms); "
                f"manifest declares arm_count={manip.arm_count}, "
                f"arms={[a.name for a in manip.arms]!r}.",
                suggestion="Declare arm_count >= 2, or two entries in manipulation.arms.",
            )
        )
    for side, sub in (("left", args.left), ("right", args.right)):
        sub_path = path + [side]
        if isinstance(sub, GraspArgs):
            out += _check_grasp_caps(sub, manifest, sub_path)
        else:
            out += _check_release_caps(sub, manifest, sub_path)
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


# ---- Industrial-profile capability checks (RFC-0013) -----------------------


def _check_pick_from_caps(
    args: PickFromArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """pick_from = navigate(source) + detect(object) + grasp(force).

    Composes the move_to / detect / grasp capability requirements, with
    errors attributed to `pick_from`.
    """
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "pick_from",
                path,
                "pick_from requires the manifest to declare `mobility` (to reach the source station).",
                suggestion="Add a `mobility` block to the manifest.",
            )
        )
    if not _location_declared(manifest, args.source):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_LOCATION,
                "pick_from",
                path,
                f"pick_from references undeclared source station {args.source!r}.",
                field="source",
                suggestion=f"Add {args.source!r} to manifest.declared_locations.",
            )
        )
    perception = manifest.perception
    if perception is None or (not perception.cameras and not perception.sensors):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_PERCEPTION,
                "pick_from",
                path,
                "pick_from requires the manifest to declare `perception` with at least "
                "one camera or sensor (to detect the object).",
            )
        )
    elif args.object not in perception.object_vocabulary:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_OBJECT_CLASS,
                "pick_from",
                path,
                f"pick_from references object class {args.object!r} which is not in the "
                "manifest's perception.object_vocabulary.",
                field="object",
                suggestion=f"Add {args.object!r} to manifest.perception.object_vocabulary, "
                "or pick a declared class.",
            )
        )
    if manifest.manipulation is None or not manifest.manipulation.grippers:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MANIPULATION,
                "pick_from",
                path,
                "pick_from requires the manifest to declare `manipulation` with at least one gripper.",
                suggestion="Add a `manipulation.grippers` list with at least one gripper.",
            )
        )
    else:
        force_val = _resolve_force(args.force)
        if force_val is not None:
            usable = [
                g for g in manifest.manipulation.grippers if _gripper_in_range(g, force_val)
            ]
            if not usable:
                out.append(
                    _err(
                        ErrorCode.CAPABILITY_MISSING_GRIPPER,
                        "pick_from",
                        path,
                        f"no declared gripper supports the requested force ({force_val} N). "
                        f"Declared ranges: "
                        f"{[(g.name, g.force_min_n, g.force_max_n) for g in manifest.manipulation.grippers]!r}.",
                        field="force",
                        suggestion="Pick a softer/firmer level, or declare a gripper covering the range.",
                    )
                )
    return out


def _check_place_at_caps(
    args: PlaceAtArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """place_at = navigate(target) + release. Composes move_to + release caps."""
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "place_at",
                path,
                "place_at requires the manifest to declare `mobility` (to reach the target station).",
                suggestion="Add a `mobility` block to the manifest.",
            )
        )
    if not _location_declared(manifest, args.target):
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_LOCATION,
                "place_at",
                path,
                f"place_at references undeclared target station {args.target!r}.",
                field="target",
                suggestion=f"Add {args.target!r} to manifest.declared_locations.",
            )
        )
    if manifest.manipulation is None or not manifest.manipulation.grippers:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MANIPULATION,
                "place_at",
                path,
                "place_at requires the manifest to declare `manipulation` with at least one gripper.",
                suggestion="Add a `manipulation.grippers` list with at least one gripper.",
            )
        )
    return out


def _check_swap_tool_caps(
    args: SwapToolArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """swap_tool rides the docking-station service mechanism.

    The station named by `at` must be declared and must offer the
    `swap_tool` service. Unlike `dock`, `at` is required (no default-station
    fallback). The `to` tool name is not validated against an accepted-tool
    list in v0.1 — the `accepted_tools` manifest field is deferred (RFC-0013).
    """
    out: list[ValidationError] = []
    target = next((s for s in manifest.docking_stations if s.name == args.at), None)
    if target is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_DOCKING_STATION,
                "swap_tool",
                path,
                f"swap_tool references docking station {args.at!r}, which is not "
                "declared in manifest.docking_stations.",
                field="at",
                suggestion=f"Declare a docking station named {args.at!r} with a "
                "'swap_tool' service in manifest.docking_stations.",
            )
        )
    elif "swap_tool" not in target.services:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_DOCKING_SERVICE,
                "swap_tool",
                path,
                f"docking station {target.name!r} does not declare the 'swap_tool' service.",
                field="at",
                suggestion=f"Add 'swap_tool' to manifest.docking_stations[{target.name!r}].services "
                f"(declared services: {target.services!r}).",
            )
        )
    return out


# Python value-type -> declared ProgramArg.type token, for arg-signature checks.
_PROGRAM_ARG_TYPE = {bool: "boolean", int: "number", float: "number", str: "string"}


def _check_call_program_caps(
    args: CallProgramArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """call_program is gated by the manifest's `programs:` declaration (RFC-0015).

    The named program must be declared. If the call passes `args`, each one must
    match a declared argument by name and scalar type. The program body itself is
    opaque to URML; the signature is all the validator can check before execution.
    """
    out: list[ValidationError] = []
    program = next((p for p in manifest.programs if p.name == args.name), None)
    if program is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_PROGRAM,
                "call_program",
                path,
                f"call_program references undeclared program {args.name!r}.",
                field="name",
                suggestion=f"Declare a program named {args.name!r} in manifest.programs, "
                "or model the behavior with real primitives instead of call_program.",
            )
        )
        return out
    declared = {a.name: a.type for a in program.args}
    for key, value in (args.args or {}).items():
        # bool is a subclass of int — check it first.
        actual = next(
            (token for py_type, token in _PROGRAM_ARG_TYPE.items() if isinstance(value, py_type)),
            "string",
        )
        if key not in declared:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_PROGRAM_ARG_MISMATCH,
                    "call_program",
                    path,
                    f"call_program passes argument {key!r}, which program {args.name!r} "
                    "does not declare.",
                    field="args",
                    suggestion=f"Declared arguments: {sorted(declared)!r}.",
                )
            )
        elif declared[key] != actual:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_PROGRAM_ARG_MISMATCH,
                    "call_program",
                    path,
                    f"call_program argument {key!r} is {actual!r}, but program "
                    f"{args.name!r} declares it as {declared[key]!r}.",
                    field="args",
                )
            )
    return out


def _check_plan_path_caps(
    args: object, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """RFC-0020: `plan_path` requires a declared HD map to plan against.

    The trajectory is computed in a cost-map bound to the manifest's
    `av.hd_map`; without a declared map there is nothing to plan against, so the
    program is not expressible under this manifest.
    """
    out: list[ValidationError] = []
    av = manifest.av
    if av is None or av.hd_map is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_HD_MAP,
                "plan_path",
                path,
                "plan_path requires the manifest to declare `av.hd_map` (the HD map "
                "the planner cost-maps against).",
                suggestion="Add an `av: { hd_map: { format, uri } }` block to the manifest.",
            )
        )
    return out


def _check_follow_trajectory_caps(
    args: object, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """RFC-0020: `follow_trajectory` actuates, so it requires `mobility`.

    The trajectory reference is type-checked in the binding pass (it must be a
    `trajectory` bound by `plan_path`); the ODD speed cap is a Pass-3 envelope
    check.
    """
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                "follow_trajectory",
                path,
                "follow_trajectory requires the manifest to declare `mobility`.",
                suggestion="Add a `mobility` block with at least `drive_type` and `max_velocity`.",
            )
        )
    return out


def _check_set_output_caps(
    args: object, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """RFC-0017: `set_output` writes a manifest-declared output line.

    Pass-2 capability checks, all manifest-derived: the line must be declared in
    `outputs.lines`; a digital line rejects a non-bool value; an analog value
    must be a number within the line's declared `range`. Bounded by design — the
    effect is a single typed line write, never an opaque escape hatch.
    """
    out: list[ValidationError] = []
    line = next((ln for ln in manifest.outputs.lines if ln.name == args.output), None)
    if line is None:
        declared = [ln.name for ln in manifest.outputs.lines]
        out.append(
            _err(
                ErrorCode.CAPABILITY_OUTPUT_LINE_NOT_DECLARED,
                "set_output",
                path,
                f"set_output references undeclared output line {args.output!r}.",
                field="output",
                suggestion=(
                    f"Declare it in manifest.outputs.lines. Declared lines: {sorted(declared)!r}."
                    if declared
                    else "Declare an `outputs: { lines: [...] }` block in the manifest."
                ),
            )
        )
        return out
    # bool is a subclass of int/float — test it first.
    value_is_bool = isinstance(args.value, bool)
    if line.kind == "digital":
        if not value_is_bool:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_OUTPUT_VALUE_TYPE_MISMATCH,
                    "set_output",
                    path,
                    f"output line {args.output!r} is digital, but set_output passes a "
                    f"non-boolean value {args.value!r}.",
                    field="value",
                    suggestion="Use a boolean value (true/false) for a digital line.",
                )
            )
    else:  # analog
        if value_is_bool:
            out.append(
                _err(
                    ErrorCode.CAPABILITY_OUTPUT_VALUE_TYPE_MISMATCH,
                    "set_output",
                    path,
                    f"output line {args.output!r} is analog, but set_output passes a "
                    f"boolean value {args.value!r}.",
                    field="value",
                    suggestion="Use a numeric setpoint within the declared range for an analog line.",
                )
            )
        elif line.range is not None:
            lo, hi = line.range
            if not (lo <= float(args.value) <= hi):
                out.append(
                    _err(
                        ErrorCode.CAPABILITY_OUTPUT_VALUE_OUT_OF_RANGE,
                        "set_output",
                        path,
                        f"set_output value {args.value!r} is outside the declared range "
                        f"[{lo}, {hi}] of analog line {args.output!r}.",
                        field="value",
                        suggestion=f"Pass a value within [{lo}, {hi}].",
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


_AERIAL_DRIVE_TYPES = {"multirotor", "fixed_wing", "vtol"}


def _check_base_mobility_bounds(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0518): base-level mobility-bounds coherence.

    The base bounds (angular velocity, accelerations, traversable slope, obstacle
    height) are declarations a velocity-controlled-base runtime or an intermediary
    node validates incoming intent against before emitting a command; field
    validity (non-negative, slope in (0, 90]) is enforced by the schema. The one
    cross-field coherence rule: terrain bounds are meaningless for an aerial
    drive, which does not traverse ground, so declaring `max_traversable_slope_deg`
    or `max_obstacle_height_m` on a multirotor / fixed_wing / vtol is incoherent.

    Optional: a manifest without these fields is unaffected.
    """
    out: list[ValidationError] = []
    mob = manifest.mobility
    if mob is None or mob.drive_type not in _AERIAL_DRIVE_TYPES:
        return out
    for field in ("max_traversable_slope_deg", "max_obstacle_height_m"):
        if getattr(mob, field) is not None:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_TERRAIN_BOUND_NOT_APPLICABLE,
                    primitive=None,
                    path=["<manifest>", "mobility", field],
                    field=field,
                    message=(
                        f"mobility.{field} is declared but drive_type is "
                        f"{mob.drive_type!r} (aerial); an aerial platform does not "
                        "traverse ground terrain."
                    ),
                    suggestion=(
                        "Remove the terrain bound, or set a ground drive_type. Per RFC-0518."
                    ),
                )
            )
    return out


def _check_aerial_caps(
    primitive: str, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Shared drone-profile capability check: drive_type must be aerial."""
    out: list[ValidationError] = []
    if manifest.mobility is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_MOBILITY,
                primitive,
                path,
                f"{primitive} requires the manifest to declare `mobility`.",
            )
        )
        return out
    if manifest.mobility.drive_type not in _AERIAL_DRIVE_TYPES:
        out.append(
            _err(
                ErrorCode.CAPABILITY_DRIVE_TYPE_NOT_AERIAL,
                primitive,
                path,
                f"{primitive} requires an aerial drive_type "
                f"(multirotor / fixed_wing / vtol); manifest declares "
                f"{manifest.mobility.drive_type!r}.",
                suggestion=f"Use {primitive} only on a drone manifest; this manifest "
                "appears to declare a ground or manipulator platform.",
            )
        )
    return out


def _check_take_off_caps(
    args: TakeOffArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Drone profile: take_off requires aerial drive_type AND declared service_ceiling."""
    out: list[ValidationError] = _check_aerial_caps("take_off", manifest, path)
    if manifest.mobility is None:
        return out
    if manifest.mobility.service_ceiling is None:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_SERVICE_CEILING,
                "take_off",
                path,
                "take_off requires manifest.mobility.service_ceiling to be declared.",
                suggestion="Add `service_ceiling: <max altitude in m>` to manifest.mobility.",
            )
        )
        return out
    if args.altitude > manifest.mobility.service_ceiling:
        out.append(
            _err(
                ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                "take_off",
                path,
                f"take_off.altitude ({args.altitude} m) exceeds "
                f"manifest.mobility.service_ceiling ({manifest.mobility.service_ceiling} m).",
                field="altitude",
            )
        )
    return out


def _check_land_caps(
    _args: LandArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Drone profile: land requires aerial drive_type."""
    return _check_aerial_caps("land", manifest, path)


def _check_return_to_home_caps(
    args: ReturnToHomeArgs, manifest: CapabilityManifest, path: list[str]
) -> list[ValidationError]:
    """Drone profile: return_to_home requires aerial drive_type AND a declared 'home' location."""
    out: list[ValidationError] = _check_aerial_caps("return_to_home", manifest, path)
    has_home = any(loc.name == "home" for loc in manifest.declared_locations)
    if not has_home:
        out.append(
            _err(
                ErrorCode.CAPABILITY_MISSING_HOME_LOCATION,
                "return_to_home",
                path,
                "return_to_home requires a declared location named 'home' in "
                "manifest.declared_locations.",
                suggestion="Add a declared_locations entry named 'home' with the "
                "intended takeoff/landing pose.",
            )
        )
    if manifest.mobility is not None and manifest.mobility.service_ceiling is not None:
        if args.altitude is not None and args.altitude > manifest.mobility.service_ceiling:
            out.append(
                _err(
                    ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                    "return_to_home",
                    path,
                    f"return_to_home.altitude ({args.altitude} m) exceeds "
                    f"manifest.mobility.service_ceiling ({manifest.mobility.service_ceiling} m).",
                    field="altitude",
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
    elif name == "take_off":
        out.extend(_check_envelope_take_off(args, manifest, envelope, path))
    elif name == "return_to_home":
        out.extend(_check_envelope_return_to_home(args, manifest, envelope, path))
    elif name == "follow_trajectory":
        out.extend(_check_envelope_follow_trajectory(args, manifest, envelope, path))

    # Geofence containment + occupancy-zone intrusion run for every
    # spatial primitive. Each helper returns no errors when the envelope
    # declares no zones of its kind (the common case for home /
    # industrial deployments).
    if name in {"move_to", "scan"}:
        out.extend(_check_envelope_geofence(step, manifest, envelope, path))
        out.extend(_check_envelope_occupancy_zones(step, manifest, envelope, path))

    return out


def _strictest(*values: float | None) -> float | None:
    """Return the smallest non-None of the given numbers, or None if all are None."""
    finite = [v for v in values if v is not None]
    return min(finite) if finite else None


def _check_envelope_follow_trajectory(
    args: object,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    """RFC-0020: a trajectory's declared max speed must not exceed the strictest
    of the ODD speed cap (`av.odd.max_velocity_mps`), the mobility max, and the
    envelope max."""
    out: list[ValidationError] = []
    se = getattr(args, "speed_envelope", None)
    declared = getattr(se, "max_velocity_mps", None) if se is not None else None
    if declared is None:
        return out
    manifest_max = manifest.mobility.max_velocity if manifest.mobility else None
    envelope_max = envelope.max_velocity if envelope else None
    odd_cap = (
        manifest.av.odd.max_velocity_mps
        if manifest.av is not None and manifest.av.odd is not None
        else None
    )
    cap = _strictest(manifest_max, envelope_max, odd_cap)
    if cap is not None and declared > cap:
        out.append(
            _err(
                ErrorCode.ENVELOPE_VELOCITY_EXCEEDED,
                "follow_trajectory",
                path,
                f"follow_trajectory.speed_envelope.max_velocity_mps ({declared}) exceeds "
                f"the strictest cap ({cap} m/s) of the ODD / mobility / envelope.",
                field="speed_envelope",
                suggestion=f"Reduce max_velocity_mps to at most {cap} m/s.",
            )
        )
    return out


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


def _check_envelope_take_off(
    args: TakeOffArgs,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    """Drone profile: take_off altitude must be at or below the strictest envelope cap."""
    out: list[ValidationError] = []
    manifest_ceiling = manifest.mobility.service_ceiling if manifest.mobility else None
    envelope_max = envelope.max_altitude if envelope else None
    cap = _strictest(manifest_ceiling, envelope_max)
    if cap is not None and args.altitude > cap:
        out.append(
            _err(
                ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                "take_off",
                path,
                f"take_off.altitude ({args.altitude} m) exceeds the strictest "
                f"declared altitude cap ({cap} m).",
                field="altitude",
                suggestion=f"Reduce altitude to at most {cap} m, or relax the cap "
                "if the deployment allows.",
            )
        )
    return out


def _check_envelope_return_to_home(
    args: ReturnToHomeArgs,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    """Drone profile: declared RTH altitude (if set) must be at or below the cap."""
    out: list[ValidationError] = []
    if args.altitude is None:
        return out  # substrate default; nothing to check statically
    manifest_ceiling = manifest.mobility.service_ceiling if manifest.mobility else None
    envelope_max = envelope.max_altitude if envelope else None
    cap = _strictest(manifest_ceiling, envelope_max)
    if cap is not None and args.altitude > cap:
        out.append(
            _err(
                ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED,
                "return_to_home",
                path,
                f"return_to_home.altitude ({args.altitude} m) exceeds the strictest "
                f"declared altitude cap ({cap} m).",
                field="altitude",
            )
        )
    return out


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
# Geofence containment (Pass 3, spatial)
#
# Semantics: when the envelope declares one or more `geofences`, every
# spatial target a program names (move_to.pose, scan.area, named
# locations resolved via the manifest) must lie inside at least one
# declared geofence whose `frame` matches the target's frame. Geofences
# are *allowlist* zones — the robot must stay inside one of them.
#
# Frame-mismatched geofences are silently skipped; a future RFC may add
# tf-style frame resolution. Named locations whose frame doesn't match
# any declared geofence are accepted (no applicable check).
# =============================================================================


def _point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    """Standard ray-casting point-in-polygon test.

    A point on the boundary is considered inside (the < / >= asymmetry
    in the test handles this). Polygon vertices are 2D tuples in the
    same frame as the point.
    """
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        # Ray from (x, y) crossing edge (i, j)?
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _altitude_in_band(z: float | None, geofence: Any) -> bool:
    """True iff ``z`` satisfies the geofence's altitude band (if any).

    Returns True when ``z`` is None (caller has no altitude information —
    treat as "altitude unconstrained at this site"). Returns True when
    the geofence declares no altitude bounds. Otherwise enforces
    ``min_altitude <= z <= max_altitude`` inclusively, with either bound
    treated as -inf / +inf when omitted.
    """
    if z is None:
        return True
    min_alt = getattr(geofence, "min_altitude", None)
    max_alt = getattr(geofence, "max_altitude", None)
    if min_alt is not None and z < min_alt:
        return False
    if max_alt is not None and z > max_alt:
        return False
    return True


def _check_point_in_any_geofence(
    point: tuple[float, float],
    frame: str,
    envelope: SafetyEnvelope | None,
    frames: Mapping[str, Frame],
    z: float | None = None,
) -> tuple[bool, list[str], str | None]:
    """Check ``point`` (in ``frame``) against every declared geofence.

    A geofence applies when it is in the same frame OR the point can be resolved
    into the geofence's frame through the manifest's frame graph (RFC-0290). When
    no geofence applies (frame mismatch with no connecting transform) the check
    abstains. ``failure_reason`` is ``"footprint"`` or ``"altitude"`` as before.
    """
    if envelope is None or not envelope.geofences:
        return True, [], None
    # (geofence, point-in-its-frame, z-in-its-frame).
    applicable: list[tuple[Any, tuple[float, float], float | None]] = []
    for g in envelope.geofences:
        if g.frame == frame:
            applicable.append((g, point, z))
            continue
        resolved = transform_point_between(
            (point[0], point[1], z if z is not None else 0.0), frame, g.frame, frames
        )
        if resolved is not None:
            applicable.append((g, (resolved[0], resolved[1]), resolved[2]))
    if not applicable:
        # No geofence in this frame and none reachable — the check abstains.
        return True, [], None
    footprint_match = False
    for g, gpoint, gz in applicable:
        if _point_in_polygon(gpoint, g.vertices):
            footprint_match = True
            if _altitude_in_band(gz, g):
                return True, [g.name], None
    reason = "altitude" if footprint_match else "footprint"
    return False, [g.name for g, _, _ in applicable], reason


def _check_point_in_any_occupancy_zone(
    point: tuple[float, float],
    frame: str,
    envelope: SafetyEnvelope | None,
    frames: Mapping[str, Frame],
) -> tuple[bool, str | None]:
    """Check ``point`` against people-occupancy zones.

    A zone applies when it is in the same frame OR the point resolves into the
    zone's frame (RFC-0290). **Denylist** semantics: ``ok`` is False iff the point
    lies inside at least one applicable zone whose ``allow_override`` is False.
    """
    if envelope is None or not envelope.people_occupancy_zones:
        return True, None
    for zone in envelope.people_occupancy_zones:
        if zone.allow_override:
            continue
        if zone.frame == frame:
            zpoint: tuple[float, float] = point
        else:
            resolved = transform_point_between((point[0], point[1], 0.0), frame, zone.frame, frames)
            if resolved is None:
                continue
            zpoint = (resolved[0], resolved[1])
        if _point_in_polygon(zpoint, zone.vertices):
            return False, zone.name
    return True, None


def _location_pose_in_manifest(
    name: str, manifest: CapabilityManifest
) -> tuple[float, float, float | None, str] | None:
    """Look up a declared location and return (x, y, z_or_None, frame), or None."""
    for loc in manifest.declared_locations or []:
        if loc.name == name:
            z = float(loc.pose.z) if loc.pose.z is not None else None
            return float(loc.pose.x), float(loc.pose.y), z, loc.frame
    return None


def _collect_spatial_targets(
    step: Step,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope,
) -> list[tuple[tuple[float, float], float | None, str, str]]:
    """Return spatial targets a step exposes for geofence/occupancy checks.

    Each entry: ``((x, y), z_or_None, frame, field_label)``. Shared
    between the geofence and occupancy-zone checks so a primitive whose
    target violates both surfaces produces both errors with consistent
    field labels.
    """
    name = step.primitive_name
    args = getattr(step, name)
    targets: list[tuple[tuple[float, float], float | None, str, str]] = []

    if name == "move_to":
        if args.pose is not None and args.frame is not None:
            z = float(args.pose.z) if args.pose.z is not None else None
            targets.append(((args.pose.x, args.pose.y), z, args.frame, "pose"))
        elif isinstance(args.location, str):
            resolved = _location_pose_in_manifest(args.location, manifest)
            if resolved is not None:
                rx, ry, rz, rframe = resolved
                targets.append(((rx, ry), rz, rframe, "location"))
    elif name == "scan":
        bbox = args.area.bounding_box
        polygon = args.area.polygon
        # scan.altitude applies to the whole surveyed area; same z for every corner/vertex.
        scan_z = float(args.altitude) if args.altitude is not None else None
        # Pick the first applicable frame from whichever envelope surface
        # has zones declared. Geofence frame first; fall back to
        # occupancy-zone frame; finally the literal "map" sentinel.
        frame = (
            envelope.geofences[0].frame
            if envelope.geofences
            else (
                envelope.people_occupancy_zones[0].frame
                if envelope.people_occupancy_zones
                else "map"
            )
        )
        if bbox is not None:
            for label, corner in (
                ("min_x,min_y", (bbox["min_x"], bbox["min_y"])),
                ("max_x,min_y", (bbox["max_x"], bbox["min_y"])),
                ("max_x,max_y", (bbox["max_x"], bbox["max_y"])),
                ("min_x,max_y", (bbox["min_x"], bbox["max_y"])),
            ):
                targets.append((corner, scan_z, frame, f"area.bounding_box[{label}]"))
        elif polygon is not None and polygon:
            for idx, vertex in enumerate(polygon):
                targets.append(((vertex.x, vertex.y), scan_z, frame, f"area.polygon[{idx}]"))
    return targets


def _check_envelope_geofence(
    step: Step,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    """Reject spatial primitives whose target lies outside all declared geofences.

    No-op when the envelope declares no geofences (the common case for
    home / industrial deployments). When a geofence declares an altitude
    band (``min_altitude`` / ``max_altitude``), targets whose footprint
    is inside but altitude is outside the band also reject — with a
    distinct ``failure_reason`` of ``"altitude"`` so authors know whether
    to move the target in plan, in altitude, or both.
    """
    if envelope is None or not envelope.geofences:
        return []
    name = step.primitive_name
    out: list[ValidationError] = []

    frames_by_name = {f.name: f for f in manifest.frames}
    for point, z, frame, field_label in _collect_spatial_targets(step, manifest, envelope):
        ok, applicable, reason = _check_point_in_any_geofence(point, frame, envelope, frames_by_name, z=z)
        if not ok:
            if reason == "altitude":
                # Footprint matched, altitude band did not.
                message = (
                    f"{name}.{field_label} ({point[0]}, {point[1]}, alt={z}) is inside "
                    f"the footprint of a declared geofence but outside its altitude "
                    f"band ({applicable!r})."
                )
                suggestion = (
                    "Choose an altitude within the geofence's "
                    "[min_altitude, max_altitude] band, widen the band, or remove "
                    "the band entirely."
                )
            else:
                message = (
                    f"{name}.{field_label} ({point[0]}, {point[1]}) in frame "
                    f"{frame!r} lies outside every declared geofence "
                    f"({applicable!r})."
                )
                suggestion = (
                    "Move the target inside a declared geofence, "
                    "add a geofence that covers this point, or remove "
                    "the geofence restriction from the envelope."
                )
            out.append(
                _err(
                    ErrorCode.ENVELOPE_GEOFENCE_VIOLATION,
                    name,
                    path,
                    message,
                    field=field_label,
                    suggestion=suggestion,
                )
            )
    return out


def _check_envelope_occupancy_zones(
    step: Step,
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
    path: list[str],
) -> list[ValidationError]:
    """Reject spatial primitives that enter declared people-occupancy zones.

    Denylist semantics: a target inside *any* declared occupancy zone
    (whose ``allow_override`` is False) rejects the program. Zones with
    ``allow_override: true`` are deployer-acknowledged risks and the
    validator abstains on them.

    No-op when the envelope declares no occupancy zones.
    """
    if envelope is None or not envelope.people_occupancy_zones:
        return []
    name = step.primitive_name
    out: list[ValidationError] = []

    frames_by_name = {f.name: f for f in manifest.frames}
    for point, _z, frame, field_label in _collect_spatial_targets(step, manifest, envelope):
        ok, zone_name = _check_point_in_any_occupancy_zone(point, frame, envelope, frames_by_name)
        if not ok:
            out.append(
                _err(
                    ErrorCode.ENVELOPE_OCCUPANCY_ZONE_INTRUSION,
                    name,
                    path,
                    f"{name}.{field_label} ({point[0]}, {point[1]}) in frame "
                    f"{frame!r} enters the declared people-occupancy zone "
                    f"{zone_name!r}. Programs that route the robot through "
                    "people-occupancy zones are rejected by default.",
                    field=field_label,
                    suggestion=(
                        "Re-route the target around the occupancy zone, OR "
                        "mark the zone with `allow_override: true` in the "
                        "envelope if the deployment has explicitly accepted "
                        "the risk."
                    ),
                )
            )
    return out


# =============================================================================
# RFC-0006: connectivity capability (Pass 2) + link-loss coherence (Pass 3)
# =============================================================================
#
# These are whole-program checks, not per-step: they reason over the manifest's
# abstract `connectivity` block and the envelope's structured `link_loss_policy`.
# They are appended after the existing Pass-2 and Pass-3 step loops in
# `validate()`. Both are no-ops when the envelope declares no link-loss rules
# (the feature is opt-in at both ends, exactly like `provenance`/Pass 5).
#
# Role-existence is owned by Pass 2; action/outage coherence is owned by Pass 3.
# The two are mutually exclusive by construction (Pass 3 skips a rule whose role
# is undeclared), so a single root cause never produces two reports:
#   - `capability.missing_link_role`        : manifest declares no `connectivity`
#                                             block at all, but a rule needs one.
#   - `envelope.link_loss_undeclared_role`  : `connectivity` exists but omits the
#                                             specific role a rule governs.


def _link_loss_envelope_error(
    code: ErrorCode,
    rule_index: int,
    message: str,
    suggestion: str,
) -> ValidationError:
    """Build an envelope-scoped (non-primitive) link-loss error.

    Uses the same shape as `_err` so the LLM-bridge revision contract is
    unchanged; `primitive` is None because link-loss is a deployment concern,
    not a program step.
    """
    return ValidationError(
        code=code,
        primitive=None,
        path=["<envelope>", "link_loss_policy", str(rule_index)],
        field="action",
        message=message,
        suggestion=suggestion,
    )


#: RFC-0382: built-in runtime quantities a monitorable property may reference
#: without declaring a sensor. The envelope's own numeric quantities plus the
#: people-distance quantity an occupancy zone implies.
_MONITORABLE_BUILTIN_SIGNALS = frozenset(
    {"speed", "altitude", "payload", "grip_force", "person_distance"}
)


def _monitorable_declared_signals(manifest: CapabilityManifest) -> set[str]:
    """The signal names a monitorable property may reference (RFC-0382).

    Built-in runtime quantities, plus every declared sensor name and declared
    event. A property that references anything outside this set is rejected:
    you cannot monitor what the manifest never said the robot can sense.
    """
    declared: set[str] = set(_MONITORABLE_BUILTIN_SIGNALS)
    declared |= {str(event) for event in manifest.declared_events}
    if manifest.perception is not None:
        declared |= {str(sensor.name) for sensor in manifest.perception.sensors}
    return declared


def _check_monitorable_properties(
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
) -> list[ValidationError]:
    """Pass 3 (RFC-0382): each monitorable property parses and resolves signals.

    For every property: parse the expression against its dialect (``custom`` is
    not parsed, only scanned for identifiers); then resolve every referenced
    signal, plus any explicitly listed ``signals``, against the declared set.
    Unparseable expressions and undeclared signals are errors. The validator
    does not evaluate the property (it has no runtime trace); a monitor backend
    compiles and runs it.
    """
    out: list[ValidationError] = []
    if envelope is None or not envelope.monitorable_properties:
        return out
    declared = _monitorable_declared_signals(manifest)
    for idx, prop in enumerate(envelope.monitorable_properties):
        base_path = ["<envelope>", "monitorable_properties", str(idx)]
        if prop.dialect == "custom":
            refs = referenced_signals_custom(prop.expression)
        else:
            try:
                ast = parse_property(prop.expression, dialect=prop.dialect)
            except MonitorableParseError as exc:
                out.append(
                    ValidationError(
                        code=ErrorCode.ENVELOPE_MONITORABLE_PARSE_ERROR,
                        primitive=None,
                        path=[*base_path, "expression"],
                        field="expression",
                        message=f"monitorable property {str(prop.name)!r} failed to parse: {exc}",
                        suggestion="Fix the expression syntax. See RFC-0382 for the core grammar.",
                    )
                )
                continue
            refs = referenced_signals(ast)
        to_resolve = refs | {str(sig) for sig in prop.signals}
        for sig in sorted(s for s in to_resolve if s not in declared):
            out.append(
                ValidationError(
                    code=ErrorCode.ENVELOPE_MONITORABLE_UNDECLARED_SIGNAL,
                    primitive=None,
                    path=[*base_path, "expression"],
                    field="expression",
                    message=(
                        f"monitorable property {str(prop.name)!r} references undeclared "
                        f"signal {sig!r}."
                    ),
                    suggestion=(
                        "Reference only a declared sensor, a declared event, or a built-in "
                        "quantity (speed, altitude, payload, grip_force, person_distance). "
                        "Per RFC-0382."
                    ),
                )
            )
    return out


def _min_non_none(*values: float | None) -> float | None:
    """The strictest (smallest) non-None ceiling, or None if all are None."""
    present = [v for v in values if v is not None]
    return min(present) if present else None


def _check_learned_policy(
    manifest: CapabilityManifest,
    envelope: SafetyEnvelope | None,
) -> list[ValidationError]:
    """Pass 2/3 (RFC-0383): a deployment must stay inside a learned policy's training envelope.

    When the manifest declares ``learned_policy``, the validator checks that the
    deployment's admissible ceiling (the strictest of the mechanical ``mobility``
    limit and the safety-envelope cap) does not exceed what the policy was
    trained for, and that the declared terrain is within the trained terrain
    classes. Severity follows ``enforcement`` (``reject`` -> error, ``warn`` ->
    warning). The validator does not load or run the policy; ``policy_ref`` is
    opaque. Per-primitive intent-to-command inference is a documented follow-on.
    """
    out: list[ValidationError] = []
    lp = manifest.learned_policy
    if lp is None:
        return out
    severity: Literal["error", "warning"] = "error" if lp.enforcement == "reject" else "warning"

    # Terrain coherence: the validated terrain must be one the policy trained on.
    vc = manifest.validation
    if vc is not None and vc.terrain_fidelity is not None and lp.terrain_classes:
        if vc.terrain_fidelity not in lp.terrain_classes:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_LEARNED_POLICY_TERRAIN_MISMATCH,
                    severity=severity,
                    primitive=None,
                    path=["<manifest>", "learned_policy", "terrain_classes"],
                    field="terrain_classes",
                    message=(
                        f"deployment terrain_fidelity {vc.terrain_fidelity!r} is not among the "
                        f"policy's trained terrain_classes {list(lp.terrain_classes)}."
                    ),
                    suggestion=(
                        "Run the policy only on terrain it was trained for, or widen "
                        "learned_policy.terrain_classes. Per RFC-0383."
                    ),
                )
            )

    # Velocity ceiling vs the trained command range.
    trained_velocity = [cr.max for cr in lp.command_ranges if cr.quantity in ("linear_velocity_x", "linear_velocity_y")]
    if trained_velocity:
        trained_max = max(trained_velocity)
        mob_v = manifest.mobility.max_velocity if manifest.mobility is not None else None
        env_v = envelope.max_velocity if envelope is not None else None
        ceiling = _min_non_none(mob_v, env_v)
        if ceiling is not None and ceiling > trained_max:
            out.append(
                _learned_policy_exceeds(
                    severity,
                    "velocity",
                    f"the admissible velocity ceiling {ceiling} (strictest of mobility/envelope) "
                    f"exceeds the policy's trained max {trained_max} m/s.",
                )
            )

    # Payload ceiling vs the trained payload range.
    if lp.payload_range is not None:
        mob_p = manifest.mobility.max_payload if manifest.mobility is not None else None
        env_p = envelope.max_payload if envelope is not None else None
        ceiling_p = _min_non_none(mob_p, env_p)
        if ceiling_p is not None and ceiling_p > lp.payload_range.max:
            out.append(
                _learned_policy_exceeds(
                    severity,
                    "payload",
                    f"the admissible payload ceiling {ceiling_p} kg (strictest of mobility/envelope) "
                    f"exceeds the policy's trained max {lp.payload_range.max} kg.",
                )
            )
    return out


def _learned_policy_exceeds(
    severity: Literal["error", "warning"],
    quantity: str,
    detail: str,
) -> ValidationError:
    return ValidationError(
        code=ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING,
        severity=severity,
        primitive=None,
        path=["<manifest>", "learned_policy", "command_ranges"],
        field=quantity,
        message=f"learned_policy training envelope exceeded: {detail}",
        suggestion=(
            "Tighten the mechanical limit or the safety-envelope cap to the trained range, "
            "or retrain/redeclare the policy for the wider range. Per RFC-0383."
        ),
    )


_DRONE_DRIVE_TYPES = {"multirotor", "fixed_wing", "vtol"}


def _check_substrate_rmw_options(
    manifest: CapabilityManifest,
) -> list[ValidationError]:
    """Pass 2 (RFC-0251): substrate.rmw_implementation + qos_profile rules.

    - When `rmw_implementation` is `'custom'`, `rmw_implementation_note`
      must be non-empty.
    - When `rmw_options.qos_profile.history` is `'keep_last'`,
      `history_depth` must be declared. (QosProfile's own constraint also
      gates `history_depth >= 1` at parse time; this pass adds the
      cross-field check.)

    Optional throughout: deployments without a `substrate.rmw_implementation`
    or `rmw_options` block are unaffected.
    """
    out: list[ValidationError] = []
    sub = manifest.substrate
    if sub is None:
        return out

    if sub.rmw_implementation == "custom" and not (
        sub.rmw_implementation_note and sub.rmw_implementation_note.strip()
    ):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_RMW_IMPLEMENTATION_NOTE_REQUIRED,
                primitive=None,
                path=["<manifest>", "substrate", "rmw_implementation_note"],
                field="rmw_implementation_note",
                message=(
                    "substrate.rmw_implementation is 'custom', but "
                    "substrate.rmw_implementation_note is missing or empty."
                ),
                suggestion=(
                    "Provide a non-empty `rmw_implementation_note` describing "
                    "the custom RMW stack. Per RFC-0251."
                ),
            )
        )

    if sub.rmw_options is not None and sub.rmw_options.qos_profile is not None:
        qp = sub.rmw_options.qos_profile
        if qp.history == "keep_last" and qp.history_depth is None:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_QOS_KEEP_LAST_REQUIRES_DEPTH,
                    primitive=None,
                    path=[
                        "<manifest>",
                        "substrate",
                        "rmw_options",
                        "qos_profile",
                        "history_depth",
                    ],
                    field="history_depth",
                    message=(
                        "substrate.rmw_options.qos_profile.history is "
                        "'keep_last', but history_depth is not declared."
                    ),
                    suggestion=(
                        "Declare `history_depth` (>= 1) alongside "
                        "`history: keep_last`. Per RFC-0251."
                    ),
                )
            )
    return out


def _check_substrate_ipc(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0385): substrate.ipc generation coherence.

    - `iceoryx1` is RouDi-daemon based and requires `runtime_name`.
    - `iceoryx2` is decentralized: it requires `config_path` and MUST NOT set
      `runtime_name` (the RouDi daemon is gone).
    - `custom` requires `generation_note`.

    Optional: a deployment without `substrate.ipc` is unaffected.
    """
    out: list[ValidationError] = []
    sub = manifest.substrate
    if sub is None or sub.ipc is None:
        return out
    ipc = sub.ipc
    base = ["<manifest>", "substrate", "ipc"]

    def _e(code: ErrorCode, leaf: str, message: str, suggestion: str) -> ValidationError:
        return ValidationError(
            code=code,
            primitive=None,
            path=base + [leaf],
            field=leaf,
            message=message,
            suggestion=suggestion,
        )

    if ipc.generation == "iceoryx1":
        if not (ipc.runtime_name and ipc.runtime_name.strip()):
            out.append(
                _e(
                    ErrorCode.CAPABILITY_IPC_RUNTIME_NAME_REQUIRED,
                    "runtime_name",
                    "substrate.ipc.generation is 'iceoryx1' (RouDi-based), but "
                    "runtime_name is missing or empty.",
                    "Name the RouDi daemon in `runtime_name`, or move to generation "
                    "'iceoryx2' and declare `config_path`. Per RFC-0385.",
                )
            )
    elif ipc.generation == "iceoryx2":
        if not (ipc.config_path and ipc.config_path.strip()):
            out.append(
                _e(
                    ErrorCode.CAPABILITY_IPC_CONFIG_PATH_REQUIRED,
                    "config_path",
                    "substrate.ipc.generation is 'iceoryx2' (decentralized), but "
                    "config_path is missing or empty.",
                    "Declare the global `config_path`; iceoryx2 has no RouDi daemon. "
                    "Per RFC-0385.",
                )
            )
        if ipc.runtime_name is not None:
            out.append(
                _e(
                    ErrorCode.CAPABILITY_IPC_RUNTIME_NAME_NOT_APPLICABLE,
                    "runtime_name",
                    "substrate.ipc.generation is 'iceoryx2', but runtime_name is set; "
                    "iceoryx2 is decentralized and has no RouDi daemon to name.",
                    "Remove `runtime_name` and declare `config_path` instead. Per RFC-0385.",
                )
            )
    elif ipc.generation == "custom":
        if not (ipc.generation_note and ipc.generation_note.strip()):
            out.append(
                _e(
                    ErrorCode.CAPABILITY_IPC_GENERATION_NOTE_REQUIRED,
                    "generation_note",
                    "substrate.ipc.generation is 'custom', but generation_note is "
                    "missing or empty.",
                    "Provide a non-empty `generation_note` describing the IPC stack. "
                    "Per RFC-0385.",
                )
            )
    return out


def _check_substrate_clock(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0477): substrate.clock time-synchronization coherence.

    Two coherence rules, neither a timing guarantee:

    - `master_synced` cannot synchronize the bus to the user clock without a
      mechanism, so it requires a `sync_protocol` other than `none`.
    - `user_clock_max_offset_ms` bounds the user clock's drift from the
      reference; it is meaningless when the bus clock *is* the reference, so it
      is only applicable when `reference == master_synced`.

    Optional: a manifest without `substrate.clock` is unaffected.
    """
    out: list[ValidationError] = []
    sub = manifest.substrate
    if sub is None or sub.clock is None:
        return out
    clock = sub.clock
    if clock.reference == "master_synced" and (
        clock.sync_protocol is None or clock.sync_protocol == "none"
    ):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_CLOCK_SYNC_PROTOCOL_REQUIRED,
                primitive=None,
                path=["<manifest>", "substrate", "clock", "sync_protocol"],
                field="sync_protocol",
                message=(
                    "substrate.clock.reference is 'master_synced' but no sync_protocol "
                    "is declared; the bus cannot be synchronized to the user clock "
                    "without a mechanism."
                ),
                suggestion=(
                    "Declare a sync_protocol (ieee1588 / gptp / ethercat_dc / ptp / gps), "
                    "or set reference to 'bus'. Per RFC-0477."
                ),
            )
        )
    if clock.reference == "bus" and clock.user_clock_max_offset_ms is not None:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_CLOCK_OFFSET_NOT_APPLICABLE,
                primitive=None,
                path=["<manifest>", "substrate", "clock", "user_clock_max_offset_ms"],
                field="user_clock_max_offset_ms",
                message=(
                    "substrate.clock.user_clock_max_offset_ms is set but reference is "
                    "'bus'; the bus clock is the reference, so there is no user-clock "
                    "offset to bound."
                ),
                suggestion=(
                    "Remove user_clock_max_offset_ms, or set reference to 'master_synced'. "
                    "Per RFC-0477."
                ),
            )
        )
    return out


def _check_substrate_bringup(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0478): substrate.bringup ordered-sequence coherence.

    The bring-up and recovery dependency declarations must be self-consistent:
    element ids are unique, every `depends_on` / `recovery_after` references a
    declared element, and neither dependency graph contains a cycle (a circular
    bring-up or recovery order can never be satisfied). The validator checks the
    declaration; it does not execute or schedule the sequence.

    Optional: a manifest without `substrate.bringup` is unaffected.
    """
    out: list[ValidationError] = []
    sub = manifest.substrate
    if sub is None or sub.bringup is None:
        return out
    elements = sub.bringup.elements

    ids: list[str] = [e.id for e in elements]
    declared = set(ids)
    seen_ids: set[str] = set()
    for eid in ids:
        if eid in seen_ids:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_BRINGUP_DUPLICATE_ELEMENT,
                    primitive=None,
                    path=["<manifest>", "substrate", "bringup", "elements"],
                    field="id",
                    message=f"substrate.bringup declares element id {eid!r} more than once.",
                    suggestion="Give each bring-up element a unique id. Per RFC-0478.",
                    detail={"id": eid},
                )
            )
        seen_ids.add(eid)

    for element in elements:
        for relation, deps in (
            ("depends_on", element.depends_on),
            ("recovery_after", element.recovery_after),
        ):
            for dep in deps:
                if dep not in declared:
                    out.append(
                        ValidationError(
                            code=ErrorCode.CAPABILITY_BRINGUP_DEPENDENCY_UNDECLARED,
                            primitive=None,
                            path=["<manifest>", "substrate", "bringup", "elements"],
                            field=relation,
                            message=(
                                f"substrate.bringup element {element.id!r} {relation} "
                                f"{dep!r}, which is not a declared element."
                            ),
                            suggestion=f"Declare an element {dep!r}, or fix the dependency. Per RFC-0478.",
                            detail={"element": element.id, relation: dep},
                        )
                    )

    # Cycle detection on each dependency graph (depends_on, recovery_after).
    for relation in ("depends_on", "recovery_after"):
        graph = {
            e.id: [d for d in getattr(e, relation) if d in declared] for e in elements
        }
        cycle = _first_cycle(graph)
        if cycle:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_BRINGUP_DEPENDENCY_CYCLE,
                    primitive=None,
                    path=["<manifest>", "substrate", "bringup", "elements"],
                    field=relation,
                    message=(
                        f"substrate.bringup has a {relation} cycle: {' -> '.join(cycle)}. "
                        "An ordering dependency cannot be circular."
                    ),
                    suggestion=f"Break the {relation} cycle so the order is satisfiable. Per RFC-0478.",
                    detail={"relation": relation, "cycle": cycle},
                )
            )
    return out


def _first_cycle(graph: dict[str, list[str]]) -> list[str]:
    """Return the first dependency cycle found in a DAG-candidate graph, or []."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)
    stack: list[str] = []

    def visit(node: str) -> list[str]:
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, []):
            if color.get(nxt, BLACK) == GRAY:
                return [*stack[stack.index(nxt):], nxt]
            if color.get(nxt, BLACK) == WHITE:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return []

    for start in graph:
        if color[start] == WHITE:
            found = visit(start)
            if found:
                return found
    return []


def _check_realtime(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0016): realtime timing-block internal coherence.

    Two v0.1 coherence rules, neither a real-time guarantee:

    - RFC-0016: the watchdog deadline must be at least one control cycle
      (`watchdog_ms >= cyclic_period_ms`); a watchdog shorter than the period
      would fault before a single cycle completes.
    - RFC-0469: when an `acyclic` (SDO / mailbox) regime is declared, its
      `timeout_ms` must be at least one control cycle. An async command meant to
      return inside a single cycle is not acyclic traffic; it belongs on the
      cyclic path. The envelope-dwell Pass-3 rule is deferred.

    Optional: a manifest without `realtime` is unaffected.
    """
    out: list[ValidationError] = []
    rt = manifest.realtime
    if rt is None:
        return out
    if rt.watchdog_ms < rt.cyclic_period_ms:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_WATCHDOG_SHORTER_THAN_CYCLE,
                primitive=None,
                path=["<manifest>", "realtime", "watchdog_ms"],
                field="watchdog_ms",
                message=(
                    f"realtime.watchdog_ms ({rt.watchdog_ms}) is shorter than "
                    f"realtime.cyclic_period_ms ({rt.cyclic_period_ms}); the watchdog "
                    "would fault before one control cycle completes."
                ),
                suggestion=(
                    "Set watchdog_ms >= cyclic_period_ms (the watchdog must allow at "
                    "least one cycle). Per RFC-0016."
                ),
            )
        )
    if rt.acyclic is not None and rt.acyclic.timeout_ms < rt.cyclic_period_ms:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_ACYCLIC_TIMEOUT_SHORTER_THAN_CYCLE,
                primitive=None,
                path=["<manifest>", "realtime", "acyclic", "timeout_ms"],
                field="timeout_ms",
                message=(
                    f"realtime.acyclic.timeout_ms ({rt.acyclic.timeout_ms}) is shorter "
                    f"than realtime.cyclic_period_ms ({rt.cyclic_period_ms}); an acyclic "
                    "(SDO / mailbox) command that must return inside one control cycle "
                    "is cyclic traffic, not acyclic."
                ),
                suggestion=(
                    "Set acyclic.timeout_ms >= cyclic_period_ms, or move the command to "
                    "the cyclic path. Per RFC-0469."
                ),
            )
        )
    return out


def _check_program_bindings(manifest: CapabilityManifest) -> list[ValidationError]:
    """Pass 2 (RFC-0019): a program's `ara_com` binding must be complete.

    AUTOSAR rides `call_program` (RFC-0015) rather than a new primitive; the
    binding only adds the routing triple. When a program declares
    `binding: { kind: ara_com }`, all of `service_id`, `instance_id`, and
    `method_id` must be present, so the runtime can resolve the service-method
    call. Programs without a binding (or with no `programs:` at all) are
    unaffected. AUTOSAR Execution Management timing rides the `realtime` block
    (RFC-0016); no separate field here.
    """
    out: list[ValidationError] = []
    for i, program in enumerate(manifest.programs):
        binding = program.binding
        if binding is None or binding.kind != "ara_com":
            continue
        missing = [
            name
            for name in ("service_id", "instance_id", "method_id")
            if getattr(binding, name) is None
        ]
        if missing:
            out.append(
                ValidationError(
                    code=ErrorCode.CAPABILITY_ARA_COM_BINDING_INCOMPLETE,
                    primitive=None,
                    path=["<manifest>", "programs", str(i), "binding"],
                    field="binding",
                    message=(
                        f"program {program.name!r} declares an ara_com binding but is "
                        f"missing {missing!r}; the full service/instance/method id triple "
                        "is required to resolve the call."
                    ),
                    suggestion="Declare service_id, instance_id, and method_id on the "
                    "ara_com binding. Per RFC-0019.",
                )
            )
    return out


def _check_substrate_required_for_drone(
    manifest: CapabilityManifest,
) -> list[ValidationError]:
    """Pass 2 (RFC-0250): drone deployments must declare substrate.autopilot_class.

    When the manifest declares `mobility.drive_type` as one of the drone-class
    values (multirotor, fixed_wing, vtol), the manifest must also declare
    `substrate.autopilot_class`. Production drone deployments compose against
    PX4 or Ardupilot or a custom autopilot; URML's manifest validator-as-static-
    gate posture requires the substrate identity to be declarable.

    Also enforces the `autopilot_class: custom` requires `autopilot_class_note`
    rule.

    Non-drone manifests are unaffected.
    """
    out: list[ValidationError] = []
    if manifest.mobility is None:
        return out
    if manifest.mobility.drive_type not in _DRONE_DRIVE_TYPES:
        return out

    if manifest.substrate is None or manifest.substrate.autopilot_class is None:
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_MISSING_AUTOPILOT_CLASS,
                primitive=None,
                path=["<manifest>", "substrate", "autopilot_class"],
                field="autopilot_class",
                message=(
                    f"mobility.drive_type is "
                    f"{manifest.mobility.drive_type!r} (drone class), but the "
                    "manifest does not declare substrate.autopilot_class."
                ),
                suggestion=(
                    "Add a `substrate` block declaring autopilot_class as one "
                    "of: 'px4', 'ardupilot', 'pixhawk_classic', or 'custom'. "
                    "Per RFC-0250."
                ),
            )
        )
        return out

    if manifest.substrate.autopilot_class == "custom" and not (
        manifest.substrate.autopilot_class_note
        and manifest.substrate.autopilot_class_note.strip()
    ):
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_AUTOPILOT_CLASS_NOTE_REQUIRED,
                primitive=None,
                path=["<manifest>", "substrate", "autopilot_class_note"],
                field="autopilot_class_note",
                message=(
                    "substrate.autopilot_class is 'custom', but "
                    "substrate.autopilot_class_note is missing or empty."
                ),
                suggestion=(
                    "Provide a non-empty `autopilot_class_note` describing the "
                    "custom autopilot stack. Per RFC-0250."
                ),
            )
        )
    return out


def _check_connectivity_caps(
    manifest: CapabilityManifest, envelope: SafetyEnvelope | None
) -> list[ValidationError]:
    """Pass 2: a manifest with no `connectivity` block cannot honor a policy.

    Fires once (deduped by role) when the envelope declares a link-loss rule
    but the manifest declares no connectivity at all. The narrower
    "connectivity present but this role missing" case is owned by Pass 3.
    """
    out: list[ValidationError] = []
    if envelope is None or not envelope.link_loss_policy:
        return out
    if manifest.connectivity is not None:
        return out  # role-level coherence is Pass 3's job
    seen: set[str] = set()
    for rule in envelope.link_loss_policy:
        if rule.role.value in seen:
            continue
        seen.add(rule.role.value)
        out.append(
            ValidationError(
                code=ErrorCode.CAPABILITY_MISSING_LINK_ROLE,
                primitive=None,
                path=["<manifest>", "connectivity"],
                field="connectivity",
                message=(
                    f"envelope.link_loss_policy governs link role "
                    f"{rule.role.value!r}, but the manifest declares no "
                    f"`connectivity` block."
                ),
                suggestion=(
                    "Add a `connectivity` block to the manifest declaring the "
                    f"{rule.role.value!r} link (and any other links the "
                    "deployment's link-loss policy governs)."
                ),
            )
        )
    return out


def _check_link_loss_coherence(
    manifest: CapabilityManifest, envelope: SafetyEnvelope | None
) -> list[ValidationError]:
    """Pass 3: each link-loss rule's action must be satisfiable by the manifest.

    Reuses the same predicates the drone/hover capability checks use so the
    contract is consistent: `return_to_home` needs a declared `home` and an
    aerial drive_type, `hover` needs station-keeping, etc. A rule may only
    *tighten* the manifest's declared outage tolerance, never relax it.
    """
    out: list[ValidationError] = []
    if envelope is None or not envelope.link_loss_policy:
        return out
    connectivity = manifest.connectivity
    mobility = manifest.mobility

    for idx, rule in enumerate(envelope.link_loss_policy):
        declared = connectivity.link_for(rule.role) if connectivity is not None else None

        # Role-existence within an existing connectivity block (Pass 2 owns the
        # "no connectivity block at all" case; skip the rest if undeclared).
        if connectivity is not None and declared is None:
            out.append(
                _link_loss_envelope_error(
                    ErrorCode.ENVELOPE_LINK_LOSS_UNDECLARED_ROLE,
                    idx,
                    f"link_loss_policy rule governs link role {rule.role.value!r}, "
                    f"which the manifest's `connectivity` block does not declare.",
                    f"Add a {rule.role.value!r} link to manifest.connectivity.links, "
                    "or remove the rule.",
                )
            )
            continue
        if declared is None:
            # No connectivity block at all — reported by Pass 2; nothing more
            # this rule can be checked against.
            continue

        action = rule.action
        if action == LinkLossAction.RETURN_TO_HOME:
            if not _location_declared(manifest, "home"):
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        "link_loss_policy action 'return_to_home' requires a "
                        "declared location named 'home' in manifest.declared_locations.",
                        "Declare a 'home' location, or choose an action the "
                        "manifest can satisfy (e.g. 'halt_and_report').",
                    )
                )
            if mobility is None or mobility.drive_type not in _AERIAL_DRIVE_TYPES:
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        "link_loss_policy action 'return_to_home' requires an "
                        "aerial drive_type (multirotor / fixed_wing / vtol).",
                        "Use 'return_to_home' only on an aerial manifest, or "
                        "choose a ground-appropriate action like 'halt_and_report'.",
                    )
                )
        elif action == LinkLossAction.LAND_NOW:
            if mobility is None or mobility.drive_type not in _AERIAL_DRIVE_TYPES:
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        "link_loss_policy action 'land_now' requires an aerial "
                        "drive_type (multirotor / fixed_wing / vtol).",
                        "Choose a ground-appropriate action like 'halt_and_report'.",
                    )
                )
        elif action == LinkLossAction.HOVER:
            if mobility is None or not mobility.station_keeping:
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        "link_loss_policy action 'hover' requires "
                        "manifest.mobility.station_keeping: true.",
                        "Set mobility.station_keeping: true if the robot can "
                        "hold position, or choose another action.",
                    )
                )
        elif action == LinkLossAction.HALT_AND_REPORT:
            # Deliberately weak in v0.1: requires only that the robot has
            # mobility (something able to stop). Documented limitation.
            if mobility is None:
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        "link_loss_policy action 'halt_and_report' requires the "
                        "manifest to declare `mobility`.",
                        "Add a `mobility` block, or remove the link-loss rule.",
                    )
                )
        elif action == LinkLossAction.CONTINUE_AUTONOMOUS:
            if not declared.autonomous_when_lost:
                out.append(
                    _link_loss_envelope_error(
                        ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT,
                        idx,
                        f"link_loss_policy action 'continue_autonomous' for link "
                        f"{rule.role.value!r} requires that link to declare "
                        f"`autonomous_when_lost: true`, but the manifest declares "
                        f"it false.",
                        "Set autonomous_when_lost: true on the declared link if "
                        "the robot can truly continue without it, or choose a "
                        "fail-safe action like 'return_to_home' / 'halt_and_report'.",
                    )
                )

        # Outage tightening: a rule may only tighten the manifest's declared
        # tolerance, never relax it (the invariant the envelope module exists for).
        if (
            rule.max_outage_seconds is not None
            and declared.max_outage_seconds is not None
            and rule.max_outage_seconds > declared.max_outage_seconds
        ):
            out.append(
                _link_loss_envelope_error(
                    ErrorCode.ENVELOPE_LINK_OUTAGE_EXCEEDS_DECLARED,
                    idx,
                    f"link_loss_policy rule allows a {rule.max_outage_seconds}s "
                    f"outage for {rule.role.value!r}, looser than the manifest's "
                    f"declared {declared.max_outage_seconds}s tolerance. An "
                    f"envelope may only tighten, never relax.",
                    f"Set the rule's max_outage_seconds to at most "
                    f"{declared.max_outage_seconds}, or relax the manifest if the "
                    "robot truly tolerates a longer outage.",
                )
            )
    return out


# =============================================================================
# Pass 4: variable bindings
# =============================================================================


def _check_bindings(program: URMLProgram) -> list[ValidationError]:
    """Name uniqueness + reference resolution + cross-primitive type check.

    Conservative semantics in this milestone:

      * `store_as` names must be unique across the program (no shadowing).
      * `$var` references are resolved iff the same name is bound *anywhere
        earlier in the linear walk order*. Branch / Parallel / Retry boundaries
        are treated permissively; a future milestone tightens this to proper
        definite-assignment analysis.
      * When a consumer dereferences a ``$ref``, the producer's binding
        type must match the consumer's expected type. ``$ref.field``
        chains are accepted whenever the producer is a structured
        payload (object / survey_result / measurement / media_handle /
        transcription / wait_result) — field-level type checking is a
        future RFC.
    """
    out: list[ValidationError] = []
    # name -> (path-where-bound, producer-type)
    bound: dict[str, tuple[list[str], str]] = {}

    for path, step in walk_program(program):
        name = step.primitive_name
        args = getattr(step, name)

        # Collect references this step consumes.
        for ref, expected_type in _references_used_with_type(name, args):
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
                continue
            producer_type = bound[head][1]
            if expected_type is not None and producer_type not in expected_type:
                out.append(
                    _err(
                        ErrorCode.BINDING_TYPE_MISMATCH,
                        name,
                        path,
                        f"{ref} resolves to a {producer_type!r}, but {name} "
                        f"expects one of {sorted(expected_type)!r}.",
                        suggestion=(
                            f"Bind {head!r} with a primitive that produces "
                            f"{sorted(expected_type)!r}, or change {name} to a "
                            "primitive that accepts the bound type."
                        ),
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
                        f"{'/'.join(bound[store_as][0])}).",
                        field="store_as",
                        suggestion=f"Pick a different name (e.g., {store_as!r}_2).",
                    )
                )
            else:
                bound[store_as] = (path, _producer_type(name, args))

        # plan_path optionally binds a Minimum-Risk fallback trajectory too
        # (RFC-0020); register it with the same `trajectory` type.
        store_alt_as = getattr(args, "store_alt_as", None)
        if store_alt_as is not None:
            if store_alt_as in bound:
                out.append(
                    _err(
                        ErrorCode.BINDING_DUPLICATE_STORE_AS,
                        name,
                        path,
                        f"duplicate `store_alt_as: {store_alt_as!r}` (first bound at "
                        f"{'/'.join(bound[store_alt_as][0])}).",
                        field="store_alt_as",
                        suggestion=f"Pick a different name (e.g., {store_alt_as!r}_2).",
                    )
                )
            else:
                bound[store_alt_as] = (path, "trajectory")
    return out


# Producer-type table: maps each binding-producing primitive to the
# type-tag the binding carries downstream. Stable; downstream consumers
# match against these strings.
_PRODUCER_TYPES: dict[str, str] = {
    "detect": "object",
    # pick_from binds the picked object — same payload shape as detect, so
    # place_at.held / grasp.target / move_to.carrying interoperate (RFC-0013).
    "pick_from": "object",
    "scan": "survey_result",
    "measure": "measurement",
    "capture": "media_handle",
    "listen": "transcription",
    # wait_for stores a generic wait_result; the payload shape varies by
    # condition.kind but the consumer surface that uses it (report.facts)
    # is permissive, so a single tag is enough for v0.1.
    "wait_for": "wait_result",
    # call_program (expect: value) stores an opaque program_result. No
    # consumer primitive accepts this type, so a returned value cannot be
    # fed to grasp/move_to/etc. — only the permissive report.attachments /
    # report.facts surface may reference it (RFC-0015).
    "call_program": "program_result",
    # plan_path binds a planned trajectory; follow_trajectory consumes it
    # (RFC-0020). The AV analog of detect -> object -> grasp.
    "plan_path": "trajectory",
}


def _producer_type(primitive_name: str, _args: object) -> str:
    """Return the type tag the primitive's `store_as` binding carries."""
    return _PRODUCER_TYPES.get(primitive_name, "unknown")


def _store_as_of(args: object) -> str | None:
    return getattr(args, "store_as", None)


def _references_used_with_type(
    name: str, args: object
) -> list[tuple[str, set[str] | None]]:
    """Return every `$ref` the args carry, paired with the producer-type
    the consuming primitive expects.

    ``None`` for ``expected_type`` means "accept any producer type"
    (currently only ``report.attachments`` — its semantics are
    intentionally permissive for diagnostics).
    """
    refs: list[tuple[str, set[str] | None]] = []

    def _maybe(value: Any, expected: set[str] | None) -> None:
        if isinstance(value, str) and value.startswith("$"):
            refs.append((value, expected))

    # move_to.carrying: must be an object (something the robot can carry).
    if name == "move_to":
        _maybe(getattr(args, "carrying", None), {"object"})
    # grasp.target: must be an object (something the gripper can grasp).
    if name == "grasp":
        _maybe(getattr(args, "target", None), {"object"})
    # release.at: when a $ref, it's the object to place at; literal names
    # are location names handled by the capability check.
    if name == "release":
        _maybe(getattr(args, "at", None), {"object"})
    # place_at.held: always a $ref to the held object (from a prior
    # pick_from / detect). RFC-0013.
    if name == "place_at":
        _maybe(getattr(args, "held", None), {"object"})
    # detect.where.near: when a $ref, an object to search near.
    if name == "detect":
        where = getattr(args, "where", None)
        if where is not None:
            _maybe(getattr(where, "near", None), {"object"})
    # hover.over: when a $ref, an object to station-keep over.
    if name == "hover":
        _maybe(getattr(args, "over", None), {"object"})
    # capture.target: when a $ref, an object to frame the capture on.
    if name == "capture":
        _maybe(getattr(args, "target", None), {"object"})
    # measure.target: when a $ref, an object to point the sensor at.
    if name == "measure":
        _maybe(getattr(args, "target", None), {"object"})
    # report.attachments: payload references attached to the report.
    # Loose: any binding type is allowed. The runtime serializes whatever
    # the substrate returned.
    if name == "report":
        attachments = getattr(args, "attachments", None) or []
        for a in attachments:
            _maybe(a, None)
        # report.facts may contain $ref values too; those are also loose.
        facts = getattr(args, "facts", None) or {}
        for v in facts.values():
            _maybe(v, None)
    # follow_trajectory.trajectory: must be a trajectory bound by plan_path
    # (RFC-0020).
    if name == "follow_trajectory":
        _maybe(getattr(args, "trajectory", None), {"trajectory"})
    return refs
