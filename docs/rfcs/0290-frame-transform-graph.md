---
rfc: 0290
title: Frame-transform graph — SE(3) transforms for cross-frame geometry
author: Ido Yahalomi (ido@jacob-ai.com)
state: Accepted
created: 2026-05-31
updated: 2026-05-31
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0290: Frame-transform graph — SE(3) transforms for cross-frame geometry

## Summary

URML's spatial checks compare poses only when their **frame names are string-equal**.
RFC-0291 made the fleet collision check geometric but inherited that limit: a drone's
`agl` target and a rover's `site` target — physically in the same place — could not be
compared, and a geofence in `site` was silently ignored for a `move_to` pose expressed
in `base_link`. Every manifest already declares `Frame.parent`, but the field was
**completely dormant** — no transform data, nothing composed it.

This RFC activates it. A `Frame` gains an optional **`transform`** (a full SE(3) rigid
transform: translation + roll/pitch/yaw) expressing the frame's pose in its parent, so a
manifest's frames form a tree and any pose can be resolved into any connected frame. A
roster gains a **`world_frame`** and per-member **`anchor`s** (each member's frame placed
in that world) so the per-robot trees connect into one fleet graph. A pure-Python SE(3)
resolver composes transforms along any path. All four frame-comparison sites become
transform-aware: fleet deconfliction *and* single-robot geofence/occupancy. This resolves
RFC-0291's #1 unresolved question.

It is strictly additive: a manifest with no `transform` and a roster with no anchors
behaves exactly as before (unrelated frames → the check abstains; same-frame → identity).

## Motivation

The fleet spans ground, air, and water robots, each with its own frame vocabulary
(`agl→wgs84`, `water→body`, `floor→chassis`, `site→base_link`). Comparing them in one
physical space — a drone flying over a rover, two robots sharing a site — requires
relating those frames, which string-name equality cannot do. The same gap shows up
single-robot: a geofence in the world frame cannot govern a target named in the robot's
body frame.

There is a subtlety the transform alone does not fix. RFC-0291's medium gate exempts
**any** two different media, so a drone (`air`) and a rover (`ground`) are never compared
regardless of position. Once transforms place them in one world, that gate would still
exempt them — adding nothing. So this RFC also **refines the medium gate**: only
**air ↔ water** stays exempt (truly disjoint media); **air ↔ ground** becomes geometric,
so a low-flying drone over a ground robot is caught. No existing fixture pairs air with
ground, so nothing regresses.

## Detailed design

### Schema (additive, optional)

**`Transform`** (`schemas/common.py`): `translation: {x, y, z}` + `rotation: {roll, pitch,
yaw}` (radians, ZYX order: `R = Rz(yaw)·Ry(pitch)·Rx(roll)`). Identity default.

**`Frame.transform: Transform | None`** (`schemas/manifest.py`) — the frame's pose **in its
parent**: a point `p` here maps to the parent as `R·p + t`. A frame with a `parent` but no
`transform` is *not numerically related* to it — checks that need the relation abstain. New
manifest validation: the frame graph must be **acyclic** with **declared parents** (codes
`capability.frame_cycle`, `capability.frame_parent_undeclared`), run per manifest and per
fleet member.

**Roster world-anchors** (`schemas/roster.py`): `FleetRoster.world_frame: Identifier | None`
and `RosterMember.anchor: FrameAnchor | None` where `FrameAnchor = {frame, transform}` places
one of the member's frames in the world. This is the deployment's extrinsic site survey.
`shared_frames` (RFC-0291) is retained and unified as the **identity special case**: a frame
listed there is treated as the world directly.

### The SE(3) resolver (`transforms.py`, pure Python, no numpy)

`rpy_to_matrix`, `compose`, `invert`, `apply` on `(R, t)` pairs; `frame_to_root` (compose up
the `parent` chain); `transform_point_between(point, src, dst, frames)` (compose along
`src → LCA → dst`, `None` if disconnected or a transform is missing);
`resolve_to_world(point, frame, frames, anchor, world_frame, shared_frames) → (point, world_id)`.

### The four sites become transform-aware

1. **Manifest frame-graph validation** — acyclic + parents declared.
2. **Fleet deconfliction** — each target is resolved to **world** at collection
   (`_MemberTarget` carries world coords + a `world_id`); two members conflict only if they
   share a `world_id` and their world volumes are not separated by the **refined medium
   gate**, laterally, or vertically.
3. **Geofence** — a geofence applies if it is in the target's frame *or* the target resolves
   into the geofence's frame; abstain if unreachable.
4. **Occupancy zone** — the same cross-frame resolution.

A `fleet.anchor_frame_undeclared` warning fires when a member anchors a frame it does not
declare (resolution would silently fail otherwise).

## Backward compatibility

Strictly additive. No `transform` anywhere → cross-frame resolution returns `None` → every
check abstains exactly as today; same-frame comparisons are identity and unchanged. The one
deliberate behavior change is the medium-gate refinement (air↔ground now geometric), which no
existing fixture exercises. Existing geofence/occupancy fixtures (target and zone in one
frame) are unchanged.

## Drawbacks

1. **Static placement, not runtime tf** — a deployment-declared survey, not a live transform
   feed. A robot that has actually moved is the runtime's concern.
2. **Per-member single-root anchor** — a member with multiple roots anchors one; targets in
   other trees abstain.
3. **RPY ZYX convention is fixed**; a quaternion input is an additive future field.
4. **Frames must be connected to compare** — disconnected frames abstain. This is safe: the
   check declines to judge rather than guessing.
5. Still a **static, per-`parallel`, endpoint** check (RFC-0291) — no swept trajectories.

## Alternatives considered

**Translation + yaw only.** Rejected for the schema (the founder chose full SE(3)): tilted
mounts and banking/pitching vehicles need full orientation. Matrix-from-RPY has no gimbal-lock
issue in the direction used.

**A flat per-member frame→world map (no per-frame tree).** Rejected: it would not activate the
existing `Frame.parent` hierarchy nor make single-robot geofence/occupancy cross-frame. The
full graph is the complete answer the founder asked for.

**Keep the medium gate as-is.** Rejected: it would leave air↔ground exempt, so transforms would
add nothing for the named drone-over-rover case.

## Prior art

- **ROS tf2** — the canonical robot transform-tree; this is its substrate-neutral, static,
  declaration-only analog (no live broadcast, no dependency).
- RFC-0291 (the geometric deconfliction this extends), RFC-0006 (the optional-block / additive
  pattern), the geofence altitude-band machinery reused for the vertical band.

## Unresolved questions

1. **Runtime / dynamic transforms** — a future minor could accept a live transform feed for
   robots that have moved since the survey.
2. **Quaternion input** and **multi-root anchoring**.
3. **Cross-frame for scan areas** — `scan.area` polygons currently resolve a single frame; do
   multi-vertex areas need per-vertex resolution beyond what `_collect_spatial_targets` does?

## Implementation note

Four DCO-signed PRs on `rfc/0288-frame-transforms`: (1) transform math + `Frame.transform` +
frame-graph validation; (2) roster anchors + fleet cross-frame + refined medium gate; (3)
geofence/occupancy cross-frame; (4) this RFC + spec. Merge commit; the founder runs the
`--admin` merge. Accepted → Implemented when all land.

## Self-review (Phase 1)

- [x] The Summary alone tells a reader what is proposed and why.
- [x] Motivation is grounded in a concrete failure (the three-domain frame gap; the geofence
      body-frame gap; the medium-gate interaction), not a hypothetical.
- [x] Detailed design names every affected schema, the resolver, and the four sites.
- [x] Alternatives considered (yaw-only; flat map; keep-medium-gate).
- [x] Drawbacks honest (static survey; single-root; fixed RPY; abstain-on-disconnect).
- [x] Backward compatibility states the one behavior change and that abstention preserves
      today's results.
- [x] Re-checked against `CLAUDE.md`: substrate-neutral (geometry + frame names, no transport),
      pure Python (no new dependency), the safety boundary is strengthened, no cloud, scope
      stays civilian/industrial/research.
