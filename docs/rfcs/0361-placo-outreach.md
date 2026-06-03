---
rfc: 0361
title: PlaCo (whole-body inverse kinematics and control) integration, request for comment from the PlaCo maintainers
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

# RFC-0361: PlaCo integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`Rhoban/placo`](https://github.com/Rhoban/placo), a quadratic-programming-based
whole-body kinematics and control library that solves for a configuration over a
set of tasks and constraints, with a whole-body and humanoid emphasis. It
**requests review and feedback from the PlaCo maintainers**.

URML's manipulation primitives (`move_to` to a pose, `grasp`, `release`) declare
**intent** plus a target and the arm's capability: the gripper kind and force
bounds, and `manipulation.reachable_workspace_m`. PlaCo solves whole-body IK and
control as a QP over tasks (a frame or position task for the target) and
constraints (joint limits, posture, contacts). A target pose becomes a task; the
declared limits become constraints; the QP yields the whole-body configuration.
URML does not solve the QP. It declares the target (a task) and the capability,
statically validates that the request is admissible (the target lies within the
declared reachable workspace and the active safety envelope) **before** PlaCo
runs, then consumes the configuration PlaCo returns.

The stack is: URML intent -> validated target plus capability -> PlaCo solves a QP
over tasks and constraints -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes. The differentiator is
**static admissibility and envelope checking before the solve**. PlaCo is a
sibling to Pink ([RFC-0353](0353-pink-outreach.md)) and mink
([RFC-0354](0354-mink-outreach.md)) in the task-based-QP family, distinguished by
its whole-body and humanoid focus, which ties it to URML's whole-body
manipulation surface ([RFC-0010](0010-whole-body-bimanual-manipulation.md)).

## Motivation

PlaCo is an actively maintained whole-body QP kinematics and control library, and
a whole-body task-and-constraint solver is a sharp place to draw URML's "validate
the target before you compute the motion" line:

1. **The task and constraint set is where URML's intent lands.** PlaCo composes
   motion from tasks (drive a frame or position toward a target) and constraints
   (joint limits, posture, contacts). URML's `move_to` target maps onto a task
   directly, so the intent has a precise home in PlaCo's formulation.
2. **It is exactly the layer URML does not own.** URML declares a target pose and
   the arm's reachable workspace; PlaCo computes the whole-body configuration that
   realizes the target while respecting its constraints. URML never assembles or
   solves the QP.
3. **Admissibility is cheap and early at this seam.** Before PlaCo builds and
   solves the QP, URML can statically reject a target outside the declared
   `reachable_workspace_m` or the safety envelope. A target that cannot be admitted
   never becomes a task.
4. **It grounds substrate-neutrality.** The same `move_to` target maps onto a Pink
   QP task ([RFC-0353](0353-pink-outreach.md)), a mink MuJoCo task
   ([RFC-0354](0354-mink-outreach.md)), or a TRAC-IK pose query
   ([RFC-0352](0352-trac-ik-outreach.md)). PlaCo is one solver among several,
   distinguished by its whole-body scope; the URML intent is unchanged across them.

Repo at [`Rhoban/placo`](https://github.com/Rhoban/placo) (about 326 stars, Issues
enabled, not archived, active, last push 2026-05-21). Origin: the Rhoban team,
University of Bordeaux (France, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `placo_arm_cell.yaml` fixture)

| URML field | Maps to PlaCo attribute |
|---|---|
| `robot_id`, `description` | The robot identity (carried at the manifest envelope; not a solver concept) |
| `frames` | The model frames a PlaCo frame or position task targets; the pose target is expressed in these frames |
| `declared_locations` | Named target poses a `move_to` resolves against before the pose becomes a task |
| `manipulation.arm_count` | The arm chains the whole-body QP optimizes over, one task group per arm |
| `manipulation.reachable_workspace_m` | The declared reachable volume; the static admissibility bound URML checks before the QP is built |
| `manipulation.grippers[].kind` / `force_min_n` / `force_max_n` | The gripper capability a `grasp` / `release` consumes; force bound checked statically, not by the QP |
| `manipulation.grippers[].accepted_classes` | The object classes a `grasp` may target; validated against the perception manifest |
| `mobility` | The mobile base or legged platform a whole-body solve coordinates with the arm task (the whole-body distinction from single-arm IK) |
| Safety envelope limits (Pass 3) | Conjoined with PlaCo's joint-limit and posture constraints; URML applies strictest-wins before the QP is assembled |

### What URML v0.1 does not yet express for PlaCo

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **IK-target and joint-configuration declaration.** URML declares a target pose
   and reachable workspace, but has no first-class way to declare the IK target
   contract (the task's target frame and weight) or to receive the returned
   whole-body configuration as a typed artifact. A future Spec RFC could add an
   IK-target / joint-configuration declaration so the task and constraint set is
   well-posed from the manifest.
2. **Whole-body / multi-task coordination declaration.** A whole-body solve
   coordinates an arm task with a base, posture, and contact constraints at once.
   URML declares a single target and capability today. A future Spec RFC could let
   the manifest declare a coordinated whole-body task group (arm plus base plus
   posture) so the intent matches PlaCo's whole-body scope.
3. **Explicit joint-limit declaration.** URML defers joint limits to the safety
   envelope today, while PlaCo expresses them as constraints. A future Spec RFC
   could let the manifest declare per-joint limits explicitly so the admissibility
   check and PlaCo's constraints agree on bounds.

### Compatibility notes

- **Vendor org.** [`Rhoban`](https://github.com/Rhoban) (the Rhoban team,
  University of Bordeaux).
- **Engagement repo.** [`Rhoban/placo`](https://github.com/Rhoban/placo):
  quadratic-programming-based whole-body kinematics and control, with a whole-body
  and humanoid emphasis; active.
- **Origin / policy.** France, NATO-allied (Rhoban, University of Bordeaux). Passes
  US-federal default policy (open-source library, no provenance gate at the
  kinematics layer).
- **License note.** Open-source; URML's relationship is cross-citation and runtime
  composition, not code vendoring.
- **Substrate-neutrality.** PlaCo is one whole-body solver among several; the same
  URML target maps onto Pink ([RFC-0353](0353-pink-outreach.md)), mink
  ([RFC-0354](0354-mink-outreach.md)), or TRAC-IK
  ([RFC-0352](0352-trac-ik-outreach.md)) with no change to the URML program. Its
  whole-body scope ties it to RFC-0010 above the URML boundary.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The IK-target / joint-configuration
  declaration, the whole-body / multi-task coordination declaration, and explicit
  joint-limit declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A PlaCo mapping would route a validated
  target into a task, let PlaCo solve the whole-body QP under its constraints, and
  consume the returned configuration for `ros2_control` to execute; the planned
  `placo_arm_cell.yaml` fixture would document the admissibility check and the
  boundary hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Whole-body scope exceeds URML's single-target intent.** PlaCo coordinates an
  arm task with base, posture, and contact constraints at once. URML declares one
  target and capability today, so a whole-body solve carries glue until the queued
  whole-body coordination Spec RFC lands. Question 3 below asks how to draw that
  line.
- **Admissibility is necessary, not sufficient.** A target inside the declared
  workspace and envelope can still have no feasible whole-body configuration (a
  conflicting constraint, a contact that cannot be held). URML's static check
  narrows the failure surface; it does not replace PlaCo's own infeasibility
  result.

## Alternatives considered

1. **Have URML solve the whole-body IK itself.** Rejected. The QP formulation, task
   weighting, and constraint handling are a substrate concern and a deep,
   well-served field. URML declares intent and admissibility and consumes a
   solution; reimplementing the solver would couple the language to one library's
   numerics and fail the substrate-neutrality acid test.
2. **Engage PlaCo only as a single-arm IK solver like Pink.** Rejected. PlaCo's
   distinguishing value is its whole-body scope (arm coordinated with base,
   posture, and contacts). Treating it as a single-arm solver would discard the
   whole-body tie to RFC-0010 that makes it a distinct sibling to Pink and mink.
3. **Anchor the manipulation wave on PlaCo instead of TRAC-IK.** Rejected. TRAC-IK
   ([RFC-0352](0352-trac-ik-outreach.md)) is the more widely reused pose-to-config
   solver across ROS manipulation and the natural wave anchor. PlaCo is engaged
   alongside it as the whole-body, task-and-constraint contrast, not the anchor.

## Prior art

- [RFC-0352 (TRAC-IK outreach)](0352-trac-ik-outreach.md): the Move #27 wave
  anchor; the pose-to-configuration contrast to PlaCo's whole-body QP solve.
- [RFC-0353 (Pink outreach)](0353-pink-outreach.md): the differential-IK sibling
  in the same task-based-QP family, single-arm where PlaCo is whole-body.
- [RFC-0354 (mink outreach)](0354-mink-outreach.md): the MuJoCo-based task-based-QP
  sibling, the same posture on a different model backend.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics and kinematics library underneath the task-based solvers in this wave.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the planning-framework
  engagement above the solver layer.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that consumes the configuration PlaCo returns.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): the physics
  substrate a whole-body solve is commonly validated against.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML whole-body manipulation surface this engagement exercises most directly.
- Sibling Move #27 RFCs: RFC-0352 (TRAC-IK), RFC-0353 (Pink), RFC-0359 (RLBench).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the PlaCo maintainers:

1. **Target-to-task boundary.** What is the cleanest seam for "URML target plus
   declared capability -> a PlaCo task and constraint set"? Should a `move_to`
   target become a single frame or position task, or do you expect a richer task
   group per request?
2. **Limit-to-constraint mapping.** URML declares limits through its safety
   envelope today. How should those declared limits map onto PlaCo's constraints
   (joint limits, posture, contacts), and which belong in the manifest versus the
   solver setup?
3. **Whole-body versus single-arm IK.** PlaCo coordinates an arm task with base,
   posture, and contacts. Relative to a single-arm solver like Pink
   ([RFC-0353](0353-pink-outreach.md)), how should URML express the whole-body
   distinction so a user knows the solve coordinates more than one chain?
4. **Infeasibility feedback.** When PlaCo finds no feasible configuration within
   its constraints, how should that feed back as a URML signal, distinct from the
   static admissibility rejection that happens before the solve?
5. **Conformance listing.** Would the PlaCo project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0361 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`Rhoban/placo`](https://github.com/Rhoban/placo) pointing at this RFC (Issues are
enabled on the repo). If the maintainers prefer another channel, URML will move the
thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 326 stars, not archived, Issues enabled,
      active, last push 2026-05-21).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, whole-body scope exceeds single-target intent,
      admissibility not sufficient).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: France, NATO-allied (Rhoban, University of Bordeaux); default
      policy passes at the kinematics layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; PlaCo is one whole-body
      solver among several, URML declares the target and admissibility and does not
      solve the QP).
