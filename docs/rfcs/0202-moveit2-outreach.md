---
rfc: 0202
title: MoveIt 2 (ROS 2 manipulation Working Group manipulation substrate) integration, request for comment from MoveIt 2 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0202: MoveIt 2 (ROS 2 manipulation Working Group manipulation substrate) integration

## Summary

URML's manipulation primitives (`pick_from`, `place_at`, `grasp`, `release`, `swap_tool`) dispatch via MoveIt 2 in ROS 2 manipulator deployments. This RFC documents the proposed URML v0.1 capability-manifest mapping for MoveIt 2 as URML's canonical ROS 2 manipulation substrate, engaged via [`moveit/moveit2`](https://github.com/moveit/moveit2) (BSD-3-Clause), and **requests review and feedback from the MoveIt 2 maintainers**. No spec change.

## Motivation

MoveIt 2 is the canonical ROS 2 manipulation framework. URML's existing industrial profile ([RFC-0013](0013-industrial-profile.md)) defines `pick_from`, `place_at`, and `swap_tool`; the natural dispatcher for ROS 2 manipulator deployments is MoveIt 2. URML's cobot, industrial-arm, and humanoid runtime tracks all converge on MoveIt 2 as the planning substrate.

Repo at [`moveit/moveit2`](https://github.com/moveit/moveit2) (BSD-3-Clause, 1.8k stars, Issues enabled, last commit `2026-05-28`, **not archived**). MoveIt Working Group governance, OSRF-adjacent / community.

URML benefits from documenting the engagement because:

1. **Manipulation-primitive dispatch is MoveIt-shaped.** URML's `pick_from(object, from_location)` becomes a MoveIt 2 pickup action; `place_at` becomes a place action; `grasp` and `release` become end-effector controller actions. The semantic surface is MoveIt 2-aligned today.
2. **Planning-pipeline declaration.** MoveIt 2 supports multiple planning pipelines (OMPL / CHOMP / STOMP / Pilz Industrial Motion); URML's manifest could declare per-deployment pipeline selection.
3. **Collision-and-constraint semantics.** MoveIt 2's collision-checking and constraint-set are degrees of freedom URML's manifest should be able to declare for envelope-binding.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_moveit2_ur5_cell.yaml` fixture)

| URML field | Maps to MoveIt 2 attribute |
|---|---|
| `name` | Deployment handle (`moveit2_humble_ur5`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `manipulation.dispatch: moveit2` | MoveIt 2 as manipulation dispatcher |
| `manipulation.planning_pipeline` | OMPL / CHOMP / STOMP / Pilz |
| `manipulation.planner_id` | RRTConnect / PRM / BiTRRT |
| `manipulation.robot_description` | SRDF / URDF reference |
| `manipulation.move_group_name` | MoveGroup name (e.g. `manipulator`, `gripper`) |
| `manipulation.collision_objects` | Static + dynamic collision scene declaration |
| `manipulation.constraints` | Position / orientation / joint constraints |
| `manipulation.controller_set` | Trajectory + gripper controllers |

### What URML v0.1 does not yet express for MoveIt 2

1. **Planning-pipeline manifest field.** URML's `manipulation.dispatch` declares dispatcher class only; planning-pipeline + planner-id are downstream choices.
2. **SRDF / URDF reference convention.** MoveIt 2 requires both URDF (kinematics) and SRDF (groups, end-effectors, virtual joints); URML's manifest could declare the reference path.
3. **Constraint-set declaration.** Position / orientation / joint constraints for envelope-binding; URML's `safety_envelope` does not today bind to MoveIt-side constraints.
4. **Multi-controller dispatch.** Trajectory + gripper controllers per primitive; URML's manifest field shape pending.

### Compatibility notes

- **Vendor org.** [`moveit`](https://github.com/moveit) — MoveIt Working Group governance, OSRF-adjacent / community.
- **Engagement repo.** [`moveit/moveit2`](https://github.com/moveit/moveit2) — BSD-3-Clause, 1.8k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `moveit/moveit_resources`, `moveit/moveit2_tutorials`, `moveit/moveit_task_constructor` — the MoveIt 2 ecosystem.
- **Origin.** MoveIt Working Group US / community (OSRF-adjacent). Passes US-federal default policy.
- **License fit.** BSD-3-Clause. Clean fit.
- **Maintainer signal.** Daily-cadence commits; the canonical ROS 2 manipulation stack.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; planning-pipeline + SRDF reference + constraint-set + multi-controller dispatch Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter targets MoveIt 2 in industrial-arm / cobot tracks; manifest-side MoveIt 2-specific fields are the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Pipeline enumeration risk** — MoveIt 2 planning pipelines evolve; URML's manifest must remain stable across MoveIt release cuts.
- **SRDF + URDF dependency surface** — two upstream description formats URML's manifest indirectly depends on.
- **Constraint-set semantic complexity** — bridging URML's envelope to MoveIt's constraint set is a real semantic-modeling task.

## Alternatives considered

1. **Skip MoveIt-specific manifest fields; let URML stay dispatcher-class-only.** Rejected. Planning-pipeline selection is a real per-deployment choice production users make; URML's manifest should declare it.
2. **Engage MoveIt Task Constructor (higher-level composition) instead of MoveIt 2 core.** Rejected. Task Constructor is downstream of MoveIt 2 core; foundation-direct engagement at the core layer reaches both surfaces.
3. **Bundle MoveIt 2 with Nav2 in a single dispatch-substrate RFC.** Rejected. Different Working Groups, different primitive shapes (manipulation vs mobility); per-WG RFCs let conversation thread per group.

## Prior art

- [`moveit/moveit2`](https://github.com/moveit/moveit2) — the upstream MoveIt 2 stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0201 (Nav2 outreach)](0201-nav2-outreach.md) — sibling Move-16 batch-2 RFC; navigation Working Group.
- [RFC-0013 (industrial profile)](0013-industrial-profile.md) — URML's industrial profile (`pick_from`, `place_at`, `swap_tool`).

## Unresolved questions

For the MoveIt 2 / MoveIt Working Group maintainers:

1. **Planning-pipeline manifest field.** OMPL / CHOMP / STOMP / Pilz selection — manifest-level declaration, or always launch-param?
2. **SRDF + URDF reference convention.** Should URML's manifest declare both reference paths, or canonicalize via `robot_description` topic?
3. **Constraint-set envelope binding.** Should URML's `safety_envelope` bind to MoveIt 2 position / orientation / joint constraints at validate time?
4. **Multi-controller dispatch.** Trajectory + gripper controllers per primitive — URML's manifest field shape preference?
5. **Adapter home.** `reference/ros2-runtime/` (URML-maintained) targets MoveIt 2 today; should MoveIt 2-specific manifest mapping live in a MoveIt-adjacent companion package?
6. **MoveIt Task Constructor relationship.** Should URML compose against MoveIt 2 core or Task Constructor for high-level industrial primitives?
7. **Conformance listing.** Would MoveIt / the MoveIt Working Group consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0202 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`moveit/moveit2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the manipulation-dispatch + Working-Group framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (BSD-3-Clause, 1.8k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (pipeline enumeration risk, SRDF+URDF dependency surface, constraint-set complexity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: MoveIt Working Group US / community (OSRF-adjacent); default policy passes.
- [x] CLAUDE.md compliance check passed.
