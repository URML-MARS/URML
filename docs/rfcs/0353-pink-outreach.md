---
rfc: 0353
title: Pink (differential inverse kinematics) integration, request for comment from the Pink maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-03
updated: 2026-06-03
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

# RFC-0353: Pink integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's solver, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`stephane-caron/pink`](https://github.com/stephane-caron/pink), a differential
inverse-kinematics solver that frames IK as a quadratic program over tasks (frame
tasks, posture, limits) and is built on Pinocchio
([RFC-0345](0345-pinocchio-outreach.md)). It **requests review and feedback from
the Pink maintainers**.

URML's manipulation primitives (`move_to` to a pose, `grasp`, `release`) declare
**intent** plus a target and the arm's capability: the gripper kind and force
bounds, and `manipulation.reachable_workspace_m`. Pink solves the IK as a QP: a
target pose becomes a frame task, joint limits and posture become further tasks,
and the QP yields the joint velocities and configuration. URML does not solve the
QP. It declares the target (a frame task) and the capability, statically
validates that the request is admissible (the target lies within the declared
reachable workspace and the active safety envelope) **before** Pink runs, then
consumes the configuration Pink returns.

The stack is: URML intent -> validated target plus capability -> Pink solves a QP
over tasks -> `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)) executes.
The differentiator is **static admissibility and envelope checking before the
solve**.

## Motivation

Pink is a clean, actively used differential-IK solver, and a task-based QP solver
is a sharp place to draw URML's "validate the target before you compute the
motion" line:

1. **The QP task set is where URML's intent lands.** Pink composes IK from tasks:
   a frame task drives an end-effector toward a target pose, posture and limit
   tasks shape the rest. URML's `move_to` target maps onto a frame task directly,
   so the intent has a precise home in Pink's formulation.
2. **It is exactly the layer URML does not own.** URML declares a target pose and
   the arm's reachable workspace; Pink computes the joint velocities and
   configuration that realize it. URML never assembles or solves the QP.
3. **Admissibility is cheap and early at this seam.** Before Pink builds and
   solves the QP, URML can statically reject a target outside the declared
   `reachable_workspace_m` or the safety envelope. A target that cannot be
   admitted never becomes a frame task.
4. **It grounds substrate-neutrality.** The same `move_to` target maps onto a
   TRAC-IK pose query ([RFC-0352](0352-trac-ik-outreach.md), pose-to-config), a
   mink MuJoCo task ([RFC-0354](0354-mink-outreach.md)), or an OMPL planning
   query ([RFC-0342](0342-ompl-outreach.md)). Pink is one solver among several;
   the URML intent is unchanged across them.

Repo at [`stephane-caron/pink`](https://github.com/stephane-caron/pink) (about
769 stars, Issues enabled, not archived, active, last push 2026-04-20). Built on
Pinocchio ([RFC-0345](0345-pinocchio-outreach.md)). Origin: Stephane Caron
(France-lineage, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `pink_arm_cell.yaml` fixture)

| URML field | Maps to Pink attribute |
|---|---|
| `robot_id`, `description` | The manipulator identity (carried at the manifest envelope; not a solver concept) |
| `frames` | The Pinocchio model frames a Pink frame task targets; the pose target is expressed in these frames |
| `declared_locations` | Named target poses a `move_to` resolves against before the pose becomes a frame task |
| `manipulation.arm_count` | The kinematic chains the QP optimizes over, one task group per arm |
| `manipulation.reachable_workspace_m` | The declared reachable volume; the static admissibility bound URML checks before the QP is built |
| `manipulation.grippers[].kind` / `force_min_n` / `force_max_n` | The gripper capability a `grasp` / `release` consumes; force bound checked statically, not by the QP |
| `manipulation.grippers[].accepted_classes` | The object classes a `grasp` may target; validated against the perception manifest |
| Safety envelope limits (Pass 3) | Conjoined with Pink's limit tasks; URML applies strictest-wins before the QP is assembled |

### What URML v0.1 does not yet express for Pink

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **IK-target and joint-configuration declaration.** URML declares a target pose
   and reachable workspace, but has no first-class way to declare the IK target
   contract (the frame task's target frame and gain) or to receive the returned
   joint configuration as a typed artifact. A future Spec RFC could add an
   IK-target / joint-configuration declaration so the task set is well-posed from
   the manifest.
2. **Redundancy / nullspace-preference hint.** Pink expresses preference through
   posture and weighted tasks. URML has no way to declare such a preference (stay
   near a posture, weight one task over another). A future Spec RFC could add an
   optional redundancy / nullspace-preference hint that maps onto Pink's posture
   and task weights.
3. **Explicit joint-limit declaration.** URML defers joint limits to the safety
   envelope today, while Pink expresses them as limit tasks. A future Spec RFC
   could let the manifest declare per-joint limits explicitly so the
   admissibility check and Pink's limit tasks agree on bounds.

### Compatibility notes

- **Vendor org.** Maintained by Stephane Caron at
  [`stephane-caron/pink`](https://github.com/stephane-caron/pink) (an individual
  maintainer in the Pinocchio ecosystem).
- **Engagement repo.** [`stephane-caron/pink`](https://github.com/stephane-caron/pink):
  differential IK via quadratic programming, built on Pinocchio; active.
- **Origin / policy.** France-lineage (NATO-allied). Passes US-federal default
  policy (open-source solver, no provenance gate at the kinematics layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  runtime composition, not code vendoring.
- **Substrate-neutrality.** Pink is one IK solver among several; the same URML
  target maps onto TRAC-IK ([RFC-0352](0352-trac-ik-outreach.md)), mink
  ([RFC-0354](0354-mink-outreach.md)), or OMPL ([RFC-0342](0342-ompl-outreach.md))
  with no change to the URML program. Its Pinocchio coupling
  ([RFC-0345](0345-pinocchio-outreach.md)) is a substrate detail below the URML
  boundary.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The IK-target / joint-configuration
  declaration, the redundancy / nullspace hint, and explicit joint-limit
  declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A Pink mapping would route a validated
  target into a frame task, let Pink solve the QP, and consume the returned
  configuration for `ros2_control` to execute; the planned `pink_arm_cell.yaml`
  fixture would document the admissibility check and the boundary hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Differential, not global.** Pink solves IK differentially: it tracks a target
  from the current configuration rather than searching the whole solution space.
  A target reachable in principle may not be tracked from a given start. URML's
  admissibility check bounds the target; it does not guarantee Pink converges to
  it from every seed. Question 3 below asks how to surface that distinction.
- **Pinocchio coupling.** Pink depends on Pinocchio for kinematics and dynamics.
  That coupling is below URML's boundary, but a deployment that adopts Pink
  inherits the Pinocchio dependency, which a TRAC-IK deployment does not.

## Alternatives considered

1. **Have URML solve the differential IK itself.** Rejected. The QP formulation,
   task weighting, and Pinocchio-backed Jacobians are a substrate concern and a
   deep, well-served field. URML declares intent and admissibility and consumes a
   solution; reimplementing the solver would fail the substrate-neutrality acid
   test.
2. **Map URML intent onto raw Pinocchio instead of Pink.** Rejected for this RFC.
   Pinocchio is the dynamics and kinematics library ([RFC-0345](0345-pinocchio-outreach.md));
   Pink is the solver that turns a target into a task-based QP. The task seam is
   the cleaner home for a `move_to` target, so the engagement meets Pink at the
   solver altitude and cross-links Pinocchio below it.
3. **Anchor the manipulation wave on Pink instead of TRAC-IK.** Rejected. TRAC-IK
   ([RFC-0352](0352-trac-ik-outreach.md)) is the more widely reused pose-to-config
   solver across ROS manipulation and the natural wave anchor. Pink is engaged
   alongside it as the differential, task-based contrast, not the anchor.

## Prior art

- [RFC-0352 (TRAC-IK outreach)](0352-trac-ik-outreach.md): the wave anchor; the
  pose-to-configuration contrast to Pink's differential, task-based solve.
- [RFC-0354 (mink outreach)](0354-mink-outreach.md): the MuJoCo-based
  differential-IK sibling, the same task-based posture on a different model
  backend.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics and kinematics library Pink is built on.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the planning-framework
  engagement above the solver layer.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the planning sibling from
  Move #26; URML declares the intent over both planning and IK.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that consumes the configuration Pink returns.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML manipulation surface this engagement exercises.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  model a Pink frame task targets.
- Sibling Move #27 RFCs: RFC-0352 (TRAC-IK), RFC-0354 (mink), RFC-0355 (MPlib).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the Pink maintainers:

1. **Target-to-task boundary.** What is the cleanest seam for "URML target plus
   declared capability -> a Pink task set"? Should a `move_to` target become a
   single frame task on the end-effector, or do you expect a richer task group
   (frame plus posture plus limits) per request?
2. **Limit mapping.** URML declares limits through its safety envelope today. How
   should those declared limits map onto Pink's task and limit configuration
   (limit tasks, configuration bounds, velocity bounds), and which belong in the
   manifest versus the solver setup?
3. **Differential versus global IK.** Pink tracks a target differentially from the
   current configuration. Relative to a global solver like TRAC-IK
   ([RFC-0352](0352-trac-ik-outreach.md)), how should URML express and surface
   that distinction so a user knows a target is being tracked, not searched
   globally?
4. **No-convergence feedback.** When Pink does not converge to a target within its
   iteration or tolerance budget, how should that feed back as a URML signal,
   distinct from the static admissibility rejection that happens before the solve?
5. **Conformance listing.** Would the Pink project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0353 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`stephane-caron/pink`](https://github.com/stephane-caron/pink) pointing at this
RFC (Issues are enabled on the repo). If the maintainer prefers another channel,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 769 stars, not archived, Issues enabled,
      active, last push 2026-04-20; built on Pinocchio).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, differential-not-global, Pinocchio coupling).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: France-lineage (NATO-allied); default policy passes at the
      kinematics layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Pink is one IK solver
      among several, URML declares the target and admissibility and does not solve
      the QP).
