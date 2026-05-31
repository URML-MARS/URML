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
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import Camera, CapabilityManifest, Frame, Gripper, Sensor
from urml_validator.schemas.policy import Policy
from urml_validator.schemas.roster import FleetRoster, FrameAnchor
from urml_validator.transforms import resolve_to_world, transform_point_between
from urml_validator.schemas.primitives import (
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
    # RFC-0006: connectivity is a whole-program capability check.
    errors.extend(_check_connectivity_caps(manifest_model, envelope_model))
    # RFC-0250: substrate.autopilot_class is required for drone manifests.
    errors.extend(_check_substrate_required_for_drone(manifest_model))
    # RFC-0251: substrate.rmw_implementation + qos_profile rules.
    errors.extend(_check_substrate_rmw_options(manifest_model))
    # RFC-0288: the frame graph must be acyclic with declared parents.
    errors.extend(_check_frame_graph(manifest_model))

    # ----- Pass 3: envelope checks -----
    for path, step in walk_program(program_model):
        errors.extend(_check_envelope(step, manifest_model, envelope_model, path))
    # RFC-0006: link-loss policy coherence is a whole-envelope check.
    errors.extend(_check_link_loss_coherence(manifest_model, envelope_model))

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


# RFC-0287: medium is derived from drive_type, not declared. Air and water
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
    """One member's spatial target, resolved into the fleet's world (RFC-0287/0288).

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
    # is geometric — a low-flying drone can collide with a ground robot (RFC-0288).
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
    vertically (RFC-0287/0288). When a member declares no `clearance`, the
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
    # RFC-0288: each member's frame graph must be well-formed.
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

    # ----- Cross-robot workspace collision (RFC-0287/0288 strategic deconfliction) -----
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
    # RFC-0288: a world-anchor whose frame the member does not declare silently
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


def _check_frame_graph(manifest: CapabilityManifest) -> list[ValidationError]:
    """RFC-0288: the frame graph must be a forest — every `parent` declared, no cycle."""
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
    into the geofence's frame through the manifest's frame graph (RFC-0288). When
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
    zone's frame (RFC-0288). **Denylist** semantics: ``ok`` is False iff the point
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
    return refs
