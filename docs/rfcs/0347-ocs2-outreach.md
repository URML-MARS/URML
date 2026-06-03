---
rfc: 0347
title: OCS2 (optimal control for switched systems / MPC) integration, request for comment from the OCS2 maintainers
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

# RFC-0347: OCS2 integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's solver, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`leggedrobotics/ocs2`](https://github.com/leggedrobotics/ocs2), a toolbox for
real-time model predictive control (MPC) and optimal control of switched systems
(legged locomotion, mobile manipulation), and **requests review and feedback from
the OCS2 maintainers**.

URML describes intent plus a goal; it does not optimize. A URML continuous-motion
primitive declares the goal and the capability constraints the motion must
respect. OCS2 runs the receding-horizon MPC that realizes that intent under the
robot's dynamics and the switched-system structure. URML validates admissibility
against the declared capability and the active safety envelope **before the
controller engages**, then lets the MPC track the goal.

URML composes **above** OCS2. The stack is: URML intent -> a validated goal plus
constraints -> an OCS2 MPC problem -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes the commanded effort -> a
SLAM / estimation world model ([RFC-0332](0332-robot-localization-outreach.md))
the MPC tracks against. OCS2 contrasts with the sibling Crocoddyl engagement
([RFC-0346](0346-crocoddyl-outreach.md)): where Crocoddyl emphasizes DDP
trajectory optimization, OCS2 emphasizes real-time receding-horizon MPC. The
differentiator is the same one for both: **static admissibility plus envelope
check before optimization and before motion**.

## Motivation

OCS2 is a mature toolbox for real-time MPC on switched systems, and it occupies
the running-controller end of the same seam URML wants drawn: the layer that
continuously realizes a declared goal under the robot's dynamics.

1. **URML declares the intent; OCS2 runs the controller that holds it.** URML's
   headline path is one English sentence moving a robot. For a legged platform or
   a mobile manipulator, the sentence becomes a primitive with a goal and the
   capability constraints it must hold. OCS2's MPC tracks that goal over a
   receding horizon under the system's dynamics and mode schedule. URML never
   writes the MPC cost or the constraints; it declares the goal and the
   admissible envelope the controller runs inside.
2. **Static admissibility is URML's contribution, before the controller engages.**
   OCS2 solves an MPC problem repeatedly at control rate. URML's value sits one
   layer up and before the controller starts: a static check that the declared
   capability ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
   and the safety envelope admit the requested intent. A program that asks for a
   motion outside the declared workspace or velocity bound is rejected before the
   MPC ever engages.
3. **It is the real-time, receding-horizon case for the wave.** Crocoddyl
   (RFC-0346) solves a trajectory-optimization problem; OCS2 emphasizes a
   controller that re-solves continuously and tracks a moving world model. URML's
   whole-body manipulation surface
   ([RFC-0010](0010-whole-body-bimanual-manipulation.md)) is exactly where a
   continuously tracked intent matters: a mobile-manipulation goal is held by the
   MPC, not solved once and replayed.
4. **It grounds the declare-and-track boundary.** OCS2 consumes a goal and a world
   model and commands effort. URML declares the goal and the constraints and lets
   the controller track; it does not run the MPC, re-derive the cost, or reach
   into the solver's internals. The same boundary holds on a zero-ROS runtime
   that drives a different executor.

Repo at [`leggedrobotics/ocs2`](https://github.com/leggedrobotics/ocs2) (about
1,416 stars, Issues enabled, Discussions disabled, not archived, last push
2026-05-14, active). Maintained by the Robotic Systems Lab at ETH Zurich. License
is asked as a question below (the GitHub API did not surface an SPDX id at
verification time; understood to be BSD-3-Clause). Origin: Switzerland (ETH
Zurich, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is at the level of "the URML declaration bounds the MPC problem OCS2
runs," not a field-by-field control mapping. URML declares the goal and the
constraints; OCS2 owns the MPC formulation and the real-time solve.

| URML field | Relation to an OCS2 MPC problem |
|---|---|
| `move_to` / `grasp` goal | The tracking reference the receding-horizon MPC steers toward; URML declares it, OCS2 encodes and tracks it |
| `manipulation.arm_count` + joints | The actuated bodies in the dynamic model the MPC optimizes over; declared at a coarse altitude, never read as a model |
| `manipulation.reachable_workspace_m` | A coarse admissibility bound checked before the controller engages; the MPC's reachable set is computed precisely by OCS2 |
| `mobility.drive_type` / `max_velocity` / `max_payload` | Platform-level bounds the MPC's state and input constraints relate to; declared at URML's altitude |
| Dynamic limits / mode schedule (deferred) | Held in the MPC's constraints and the switched-system mode schedule; URML defers these to the safety envelope today, with a queued declaration below |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins before the controller engages; the world model the MPC tracks against is the RFC-0332 estimate |

### What URML v0.1 does not yet express for OCS2

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Explicit dynamic-limit declaration.** URML declares `reachable_workspace_m`
   but not per-joint torque or velocity limits, dynamic parameters, or the
   switched-system mode schedule. Those define the MPC problem OCS2 runs and are
   deferred to the safety envelope today. A future Spec RFC could add an optional
   dynamic-limit declaration, shared with the wave anchor (RFC-0342) and with
   Pinocchio (RFC-0345).
2. **Planner-class declaration.** URML's manifest does not record which class of
   solver realizes a goal. A future Spec RFC could add an optional planner-class
   declaration so the validator can reason about the realizing layer (a real-time
   MPC controller here) explicitly.
3. **Trajectory / constraint-feasibility hint.** URML validates admissibility of
   the goal before the controller engages, but it does not yet carry a
   feasibility hint a running MPC could use. A future Spec RFC could add an
   optional trajectory or constraint-feasibility hint to the validated goal.

### Compatibility notes

- **Vendor org.** [`leggedrobotics`](https://github.com/leggedrobotics) (the
  Robotic Systems Lab at ETH Zurich).
- **Engagement repo.** [`leggedrobotics/ocs2`](https://github.com/leggedrobotics/ocs2),
  the real-time MPC and optimal-control toolbox for switched systems.
- **Origin / policy.** Switzerland (ETH Zurich, NATO-allied). Passes US-federal
  default policy (open-source academic solver, no provenance gate at the
  optimal-control layer).
- **License fit.** Understood to be BSD-3-Clause; not SPDX-detected at
  verification time, so asked below as a question.
- **Substrate-neutrality.** OCS2 is one optimal-control solver among several in
  this wave; URML's declare-the-goal, let-the-controller-track posture is
  independent of which solver realizes it, so the boundary holds on a zero-ROS
  runtime that drives a different executor.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The dynamic-limit declaration, the
  planner-class declaration, and the feasibility hint are queued Spec RFCs,
  shared with the wave anchor.
- Reference runtime: no change. There is no OCS2 adapter to build in this RFC;
  URML declares a validated goal plus constraints and lets the MPC track it, not
  run the controller itself. No in-repo fixture is planned for OCS2 specifically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Indirection through a controller formulation.** URML declares a goal and
  constraints; turning those into a well-posed real-time MPC problem (the cost,
  the horizon, the mode schedule, the solver settings) is squarely OCS2's
  expertise, not URML's. The seam between "declared constraint" and "MPC
  constraint" is the part most likely to need a maintainer's correction.
- **Static-vs-running mismatch.** URML's check is static and one-shot, before the
  controller engages. An MPC re-solves continuously against a changing world
  model; a pre-engage admissibility check cannot catch every infeasibility that
  emerges at runtime. URML rejects the clearly inadmissible, the controller and
  its safety logic handle the rest.

## Alternatives considered

1. **Skip OCS2 and rely on the trajectory-optimization engagement alone.**
   Rejected. Real-time receding-horizon MPC and one-shot trajectory optimization
   are different realizing layers with different boundaries to URML; engaging
   only the trajectory case would leave the running-controller boundary undrawn.
2. **Claim a direct URML-to-OCS2 control mapping.** Rejected. It would
   over-promise. URML has no MPC problem, no cost function, no mode schedule, no
   solver surface; pretending otherwise would fail the substrate-neutrality acid
   test and misrepresent the altitude. URML declares the goal and validates
   admissibility; OCS2 owns the control.
3. **Fold OCS2 and Crocoddyl (RFC-0346) into one optimal-control thread.**
   Rejected. They emphasize different things (real-time receding-horizon MPC
   versus DDP trajectory optimization) and reach URML's boundary differently. Two
   bounded touches that name the contrast are clearer than one merged thread.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the planner boundary and the goal-declaration contract this RFC defers to.
- [RFC-0346 (Crocoddyl outreach)](0346-crocoddyl-outreach.md): the sibling
  optimal-control engagement; Crocoddyl emphasizes DDP trajectory optimization,
  OCS2 emphasizes real-time receding-horizon MPC. The contrast is the reason both
  are engaged.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the effort an OCS2 controller commands.
- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the SLAM / estimation world model the MPC tracks against at control rate.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  URML's whole-body manipulation surface, where a continuously tracked
  mobile-manipulation intent matters.
- [RFC-0290 (frame-transform graph)](0290-frame-transform-graph.md): the frame
  surface a `move_to` goal resolves against before the MPC is posed.
- Sibling Move #26 RFCs: RFC-0345 (Pinocchio), RFC-0348 (CasADi), RFC-0349
  (acados), several of which compute over a Pinocchio or CasADi backend.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the OCS2 maintainers:

1. **Intent-to-MPC boundary.** Is "URML declares a continuous-motion intent plus
   constraints, OCS2 formulates and runs the MPC that realizes it" the right
   boundary from your side, or does it mischaracterize where the MPC formulation
   belongs?
2. **Declaring the constraints the MPC must respect.** How should URML declare
   the dynamic limits and the switched-system constraints an OCS2 MPC must respect
   (state and input bounds, the mode schedule) at a coarse capability altitude,
   without re-encoding the MPC problem URML has no business owning?
3. **MPC versus trajectory optimization.** Crocoddyl (RFC-0346) is engaged as a
   DDP trajectory-optimization touch and OCS2 as a real-time MPC touch. Is that
   the right way to split the optimal-control surface from your side, or does the
   distinction matter less than this framing assumes?
4. **Admissibility before the controller engages.** URML rejects a clearly
   inadmissible intent before the MPC starts. Is a coarse pre-engage admissibility
   check (workspace, velocity, payload) useful to an OCS2-based stack, or does
   feasibility only become knowable once the controller is running?
5. **License.** What is the current license of OCS2 (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD-3-Clause)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0347 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue on
[`leggedrobotics/ocs2`](https://github.com/leggedrobotics/ocs2) pointing at this
RFC (Discussions are disabled on the repo). If the maintainers prefer another
channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,416 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-14).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, indirection through a controller
      formulation, static-vs-running mismatch).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Switzerland (ETH Zurich, NATO-allied); default policy passes at
      the optimal-control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML declares the
      goal and lets the controller track, OCS2 owns the MPC, the boundary holds on
      a zero-ROS runtime, composed-above and honest about the altitude).
