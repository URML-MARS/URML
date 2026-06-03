---
rfc: 0352
title: TRAC-IK (inverse kinematics solver) integration, request for comment from the TRAC-IK maintainers
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

# RFC-0352: TRAC-IK integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's solver, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 opens URML's engagement with the manipulation and grasping layer. This
RFC anchors the wave on [`traclabs/trac_ik`](https://github.com/traclabs/trac_ik),
the de-facto fast inverse-kinematics solver across ROS manipulation: a KDL plus
nonlinear-optimization hybrid that a great many ROS manipulators rely on. It
**requests review and feedback from the TRAC-IK maintainers**.

URML's manipulation primitives (`move_to` to a pose, `grasp`, `release`) declare
**intent** plus a target and the arm's capability: the gripper kind and force
bounds, and `manipulation.reachable_workspace_m`. A manipulation substrate, here
an IK solver, computes the joint configuration that realizes the target pose.
URML does not solve IK. It declares the target pose and the capability,
statically validates that the request is admissible (the target lies within the
declared reachable workspace and the active safety envelope) **before** the
solver runs, then consumes the joint configuration TRAC-IK returns.

The stack is: URML intent -> validated target plus capability -> TRAC-IK
computes a joint solution -> `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md))
executes. The differentiator is **static admissibility and envelope checking
before the solve**, so an out-of-workspace or out-of-envelope target is rejected
before TRAC-IK is ever queried.

## Motivation

TRAC-IK is the IK workhorse under ROS manipulation, and a solver is the cleanest
place to draw URML's "validate the target before you compute the motion" line:

1. **It is the solver most ROS arms already use.** TRAC-IK is the default fast
   IK plugin across a large body of MoveIt and bespoke manipulation stacks.
   Meeting URML's manipulation intent at the TRAC-IK boundary reaches that
   installed base without asking anyone to change solvers.
2. **It is exactly the layer URML does not own.** URML declares a target pose and
   the arm's reachable workspace; TRAC-IK turns that pose into joint angles. The
   division of labor is clean: URML states the admissible intent, the solver
   realizes it. URML never reimplements kinematics.
3. **Admissibility is cheap and early at this seam.** Before TRAC-IK runs its KDL
   plus optimization passes, URML can statically reject a target that falls
   outside the declared `reachable_workspace_m` or violates the safety envelope.
   A solve that cannot succeed within the declared capability never starts.
4. **It grounds substrate-neutrality.** The same `move_to` pose target maps onto
   a Pink QP task ([RFC-0353](0353-pink-outreach.md)), a mink MuJoCo task
   ([RFC-0354](0354-mink-outreach.md)), or an OMPL planning query
   ([RFC-0342](0342-ompl-outreach.md)). TRAC-IK is one solver among several; the
   URML intent is unchanged across them.

Repo at [`traclabs/trac_ik`](https://github.com/traclabs/trac_ik), the canonical
TRACLabs repository (Issues enabled, not archived, actively maintained, last push
2026-06-02). Origin: TRACLabs (United States); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `trac_ik_arm_cell.yaml` fixture)

| URML field | Maps to TRAC-IK attribute |
|---|---|
| `robot_id`, `description` | The manipulator identity (carried at the manifest envelope; not a solver concept) |
| `frames` | The base and tip frames a TRAC-IK chain is constructed over; the pose target is expressed in these frames |
| `declared_locations` | Named target poses a `move_to` resolves against before the pose enters a TRAC-IK query |
| `manipulation.arm_count` | The number of independent kinematic chains, one TRAC-IK solver instance per arm |
| `manipulation.reachable_workspace_m` | The declared reachable volume; the static admissibility bound URML checks before a solve is requested |
| `manipulation.grippers[].kind` / `force_min_n` / `force_max_n` | The gripper capability a `grasp` / `release` consumes; force bound checked statically, not by the IK solve |
| `manipulation.grippers[].accepted_classes` | The object classes a `grasp` may target; validated against the perception manifest |
| Safety envelope limits (Pass 3) | Conjoined with the chain's reach; URML applies strictest-wins before the pose is handed to TRAC-IK |

### What URML v0.1 does not yet express for TRAC-IK

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **IK-target and joint-configuration declaration.** URML declares a target pose
   and reachable workspace, but has no first-class way to declare the IK target
   contract (base frame, tip frame, seed configuration, solve type) or to receive
   the returned joint configuration as a typed artifact. A future Spec RFC could
   add an IK-target / joint-configuration declaration so the query is well-posed
   from the manifest.
2. **Redundancy / nullspace-preference hint.** For redundant arms, the same pose
   admits many joint solutions. URML has no way to express a preference (stay near
   a seed, minimize joint travel, avoid a region). A future Spec RFC could add an
   optional redundancy / nullspace-preference hint.
3. **Explicit joint-limit declaration.** URML defers joint limits to the safety
   envelope today. A future Spec RFC could let the manifest declare per-joint
   limits explicitly so the admissibility check and the solver agree on bounds
   without round-tripping through the envelope.

### Compatibility notes

- **Vendor org.** [`traclabs`](https://github.com/traclabs) (TRACLabs, a US
  robotics research and software organization).
- **Engagement repo.** [`traclabs/trac_ik`](https://github.com/traclabs/trac_ik),
  the canonical TRACLabs solver: a KDL plus nonlinear-optimization hybrid,
  actively maintained.
- **Origin / policy.** United States (TRACLabs). Passes US-federal default policy
  (open-source solver, no provenance gate at the kinematics layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  runtime composition, not code vendoring.
- **Substrate-neutrality.** TRAC-IK is one IK solver among several; the same URML
  pose target maps onto Pink ([RFC-0353](0353-pink-outreach.md)), mink
  ([RFC-0354](0354-mink-outreach.md)), or OMPL ([RFC-0342](0342-ompl-outreach.md))
  with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The IK-target / joint-configuration
  declaration, the redundancy / nullspace hint, and explicit joint-limit
  declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A TRAC-IK mapping would route a
  validated pose target into a TRAC-IK query and consume the returned joint
  configuration for `ros2_control` to execute; the planned `trac_ik_arm_cell.yaml`
  fixture would document the admissibility check and the boundary hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Boundary depends on a well-posed query.** A useful TRAC-IK call needs base
  and tip frames, a seed, and a solve type. URML declares the target and
  reachability but not yet the full query contract, so the first mapping carries
  a small amount of glue until the queued IK-target Spec RFC lands.
- **Admissibility is necessary, not sufficient.** A target inside the declared
  workspace and envelope can still have no IK solution (a self-collision pose, a
  singular configuration). URML's static check narrows the failure surface; it
  does not replace the solver's own no-solution result.

## Alternatives considered

1. **Have URML solve IK itself.** Rejected. Kinematics is a substrate concern and
   a deep, well-served field. URML declares intent and admissibility and consumes
   a solution; reimplementing IK would couple the language to one solver's
   numerics and fail the substrate-neutrality acid test.
2. **Skip the static admissibility check and let the solver report failure.**
   Rejected. The whole value URML adds at this seam is rejecting an inadmissible
   target before the solve, against the declared capability and the safety
   envelope. Deferring everything to the solver discards that contribution.
3. **Anchor the manipulation wave on MoveIt instead of a bare solver.** Rejected
   as the anchor. MoveIt is engaged separately ([RFC-0202](0202-moveit2-outreach.md))
   at the planning-framework altitude. TRAC-IK is the narrower, more widely reused
   primitive (the solver itself), which is the cleanest place to draw the
   target-pose-to-joint-configuration boundary.

## Prior art

- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the planning-framework
  engagement above the solver; TRAC-IK is one of MoveIt's IK plugins.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the planning sibling from
  Move #26; OMPL plans paths, TRAC-IK solves poses, URML declares the intent over
  both.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics and kinematics library several differential-IK solvers build on.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that consumes the joint configuration TRAC-IK returns.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML manipulation surface this engagement exercises.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  model the base and tip poses are expressed in.
- Sibling Move #27 RFCs: RFC-0353 (Pink), RFC-0354 (mink), RFC-0355 (MPlib).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the TRAC-IK maintainers:

1. **Target-to-query boundary.** What is the cleanest seam for "URML target pose
   plus declared reachability -> a TRAC-IK query"? Should URML produce the pose in
   the chain's base frame and hand it directly, or is there an intermediate
   contract you would prefer?
2. **Well-posed-query contract.** What should URML declare so a TRAC-IK query is
   well-posed: base and tip frames, the seed configuration, and the solve type
   (Speed, Distance, Manipulation, or another)? Which of these belong in the
   manifest versus the call site?
3. **No-solution feedback.** When TRAC-IK returns no solution within its time and
   tolerance budget, how should that result feed back as a URML validation
   signal? Is a no-solution result best surfaced as a runtime rejection distinct
   from the static admissibility failure?
4. **Reachability versus reach.** URML declares a coarse `reachable_workspace_m`.
   Is matching the target against that declared volume a useful pre-solve check
   from your perspective, or would you anchor admissibility on something else (a
   reachability map, a manipulability threshold)?
5. **Conformance listing.** Would TRACLabs consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0352 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`traclabs/trac_ik`](https://github.com/traclabs/trac_ik) pointing at this RFC
(Issues are enabled on the repo). If the maintainers prefer another channel, URML
will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (canonical TRACLabs repo, not archived, Issues
      enabled, actively maintained, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, well-posed-query glue, admissibility not
      sufficient).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (TRACLabs); default policy passes at the kinematics layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; TRAC-IK is one IK
      solver among several, URML declares the target and admissibility and does
      not solve IK).
