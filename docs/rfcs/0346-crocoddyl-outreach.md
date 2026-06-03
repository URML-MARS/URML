---
rfc: 0346
title: Crocoddyl (differential dynamic programming optimal control) integration, request for comment from the Crocoddyl maintainers
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

# RFC-0346: Crocoddyl integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's solver, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`loco-3d/crocoddyl`](https://github.com/loco-3d/crocoddyl), a fast differential
dynamic programming (DDP) optimal-control library for multi-contact dynamic
motion (legged locomotion, dynamic manipulation), and **requests review and
feedback from the Crocoddyl maintainers**.

URML describes intent plus a goal; it does not optimize. A URML dynamic-motion
primitive (a legged `move_to`, a dynamic `grasp`) declares the goal and the
capability constraints the motion must respect. Crocoddyl computes the
dynamically feasible trajectory that realizes that intent under the robot's
dynamics and contact model. URML validates admissibility against the declared
capability and the active safety envelope **before the solver runs**, then
consumes the optimized trajectory.

URML composes **above** Crocoddyl. The stack is: URML intent -> a validated goal
plus constraints -> a Crocoddyl optimal-control problem -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes the result -> a SLAM /
estimation world model ([RFC-0332](0332-robot-localization-outreach.md)) the
motion is grounded against. Crocoddyl is built directly on Pinocchio (sibling
[RFC-0345](0345-pinocchio-outreach.md)); URML talks to the solver, not to the
dynamics backend underneath it. The differentiator is **static admissibility
plus envelope check before optimization and before motion**.

## Motivation

Crocoddyl is one of the fastest DDP-based optimal-control libraries for
multi-contact dynamic motion, and it sits exactly at the seam URML wants drawn:
the layer that turns a declared intent into a dynamically feasible trajectory.

1. **URML declares the intent; Crocoddyl computes the motion.** URML's headline
   path is one English sentence moving a robot. For a legged or dynamic platform,
   the sentence becomes a primitive with a goal (`move_to` a pose, a dynamic
   `grasp`) and the capability constraints it must hold. Crocoddyl solves the
   optimal-control problem that realizes the goal under the robot's dynamics.
   URML never writes the cost or the constraints of the OCP; it declares the goal
   and the admissible envelope the solver works inside.
2. **Static admissibility is URML's contribution, one step earlier.** Crocoddyl
   optimizes a trajectory given a problem. URML's value sits one layer up and
   before the solve: a static check that the declared capability
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) and the
   safety envelope admit the requested intent. A program that asks for a motion
   outside the declared workspace or velocity bound is rejected before a single
   DDP iteration runs.
3. **It is the dynamic-motion case for the wave.** Several Move #26 targets plan
   under kinematic or quasi-static assumptions. Crocoddyl is where dynamic
   feasibility (contact forces, momentum, the full rigid-body dynamics) decides
   whether an intent is realizable. URML's whole-body manipulation surface
   ([RFC-0010](0010-whole-body-bimanual-manipulation.md)) is exactly where that
   bites: a bimanual or legged intent is admissible only if the dynamics close.
4. **It grounds the consume-the-trajectory boundary.** Crocoddyl returns a state
   and control trajectory. URML consumes it and hands it to the execution layer;
   it does not re-plan, re-optimize, or reach into the solver's internals. The
   same boundary holds on a zero-ROS runtime that drives a different executor.

Repo at [`loco-3d/crocoddyl`](https://github.com/loco-3d/crocoddyl) (about 1,225
stars, Issues **and** Discussions enabled, not archived, last push 2026-06-01,
active). Maintained across INRIA / LAAS-CNRS and the University of Edinburgh
(the loco-3d ecosystem). License is asked as a question below (the GitHub API did
not surface an SPDX id at verification time; understood to be BSD-3-Clause).
Origin: France / United Kingdom (NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is at the level of "the URML declaration bounds the optimal-control
problem Crocoddyl solves," not a field-by-field control mapping. URML declares
the goal and the constraints; Crocoddyl owns the OCP formulation and the solve.

| URML field | Relation to a Crocoddyl optimal-control problem |
|---|---|
| `move_to` / `grasp` goal | The terminal or tracking target of the OCP; URML declares it, Crocoddyl encodes and solves it |
| `manipulation.arm_count` + joints | The actuated bodies in the dynamic model the OCP optimizes over; declared at a coarse altitude, never read as a model |
| `manipulation.reachable_workspace_m` | A coarse admissibility bound checked before the solve; the OCP's reachable set is computed precisely by Crocoddyl |
| `mobility.drive_type` / `max_velocity` / `max_payload` | Platform-level bounds the OCP's state and control constraints relate to; declared at URML's altitude |
| Dynamic limits / contact assumptions (deferred) | Held in the OCP's constraints and contact model; URML defers these to the safety envelope today, with a queued declaration below |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins before the solver runs; the trajectory Crocoddyl returns is the artifact URML consumes |

### What URML v0.1 does not yet express for Crocoddyl

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Explicit dynamic-limit and contact-assumption declaration.** URML declares
   `reachable_workspace_m` but not per-joint torque or velocity limits, dynamic
   parameters, or contact assumptions (which feet or hands are in contact, the
   friction model). Those define the OCP Crocoddyl solves and are deferred to the
   safety envelope today. A future Spec RFC could add an optional dynamic-limit
   and contact-assumption declaration, shared with the wave anchor (RFC-0342) and
   with Pinocchio (RFC-0345).
2. **Planner-class declaration.** URML's manifest does not record which class of
   solver realizes a goal. A future Spec RFC could add an optional planner-class
   declaration so the validator can reason about the realizing layer (an
   optimal-control / DDP solver here) explicitly.
3. **Trajectory / constraint-feasibility hint.** URML validates admissibility of
   the goal before the solve, but it does not yet carry a feasibility hint that a
   downstream consumer or a re-solve could use. A future Spec RFC could add an
   optional trajectory or constraint-feasibility hint to the validated goal.

### Compatibility notes

- **Vendor org.** [`loco-3d`](https://github.com/loco-3d) (legged-robotics
  optimal-control ecosystem, INRIA / LAAS-CNRS and the University of Edinburgh).
- **Engagement repo.** [`loco-3d/crocoddyl`](https://github.com/loco-3d/crocoddyl),
  the DDP optimal-control library for multi-contact dynamic motion.
- **Origin / policy.** France / United Kingdom (INRIA / LAAS-CNRS, University of
  Edinburgh, NATO-allied). Passes US-federal default policy (open-source academic
  solver, no provenance gate at the optimal-control layer).
- **License fit.** Understood to be BSD-3-Clause; not SPDX-detected at
  verification time, so asked below as a question.
- **Substrate-neutrality.** Crocoddyl is one optimal-control solver among several
  in this wave; URML's declare-the-goal, consume-the-trajectory posture is
  independent of which solver realizes it, so the boundary holds on a zero-ROS
  runtime that hands the trajectory to a different executor.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The dynamic-limit and
  contact-assumption declaration, the planner-class declaration, and the
  feasibility hint are queued Spec RFCs, shared with the wave anchor.
- Reference runtime: no change. There is no Crocoddyl adapter to build in this
  RFC; URML declares a validated goal plus constraints and consumes the
  trajectory the solver returns, not the optimization itself. No in-repo fixture
  is planned for Crocoddyl specifically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Indirection through a problem formulation.** URML declares a goal and
  constraints; turning those into a well-posed OCP (the cost terms, the contact
  schedule, the horizon) is squarely Crocoddyl's expertise, not URML's. The seam
  between "declared constraint" and "OCP constraint" is the part most likely to
  need a maintainer's correction.
- **Coarse-to-precise gap.** URML declares capability at a coarse altitude while
  Crocoddyl reasons about precise dynamics and contact. A coarse admissibility
  check before the solve cannot catch every infeasibility the dynamics expose;
  URML rejects the clearly inadmissible, the solver decides the rest.

## Alternatives considered

1. **Skip Crocoddyl and engage only the kinematic planners.** Rejected. Dynamic
   feasibility is where a legged or dynamic-manipulation intent is actually
   decided, and engaging only the kinematic layer would leave URML's
   admissibility-before-motion claim untested against the hard case.
2. **Claim a direct URML-to-Crocoddyl control mapping.** Rejected. It would
   over-promise. URML has no OCP, no cost function, no contact schedule, no
   solver surface; pretending otherwise would fail the substrate-neutrality acid
   test and misrepresent the altitude. URML declares the goal and validates
   admissibility; Crocoddyl owns the optimization.
3. **Engage Crocoddyl and Pinocchio (RFC-0345) as one consolidated thread.**
   Rejected. They sit at different altitudes (a dynamics backend versus an
   optimal-control solver built on it) and the boundary the wave needs drawn is
   clearer as two bounded touches. The coupling is named in both RFCs rather than
   merged.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the planner boundary and the goal-declaration contract this RFC defers to.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics backend Crocoddyl is built directly on; the closest coupling to this
  solver, engaged as a separate bounded touch.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the trajectory Crocoddyl returns.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  URML's whole-body manipulation surface, where dynamic feasibility decides
  admissibility.
- [RFC-0290 (frame-transform graph)](0290-frame-transform-graph.md): the frame
  surface a `move_to` goal resolves against before the OCP is posed.
- Sibling Move #26 RFCs: RFC-0347 (OCS2, real-time MPC), RFC-0348 (CasADi),
  RFC-0349 (acados), several of which compute over a Pinocchio backend.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the Crocoddyl maintainers:

1. **Intent-to-OCP boundary.** Is "URML declares a dynamic-motion intent plus
   constraints, Crocoddyl formulates and solves the optimal-control problem that
   realizes it" the right boundary from your side, or does it mischaracterize
   where the OCP formulation belongs?
2. **Declaring dynamic limits and contact assumptions.** How should URML declare
   the dynamic limits and contact assumptions a Crocoddyl OCP must respect (joint
   torque and velocity bounds, the contact schedule, the friction model) at a
   coarse capability altitude, without re-encoding the OCP URML has no business
   owning?
3. **Admissibility before the solve.** URML rejects a clearly inadmissible intent
   before the solver runs. Is a coarse pre-solve admissibility check (workspace,
   velocity, payload) useful to a Crocoddyl-based stack, or does dynamic
   feasibility only become knowable inside the solve?
4. **Pinocchio coupling.** Crocoddyl is built on Pinocchio (RFC-0345). Is engaging
   the dynamics backend and the optimal-control solver as separate, clearly
   bounded touches the right shape, or would you prefer one consolidated thread?
5. **License.** What is the current license of Crocoddyl (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD-3-Clause)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0346 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`loco-3d/crocoddyl`](https://github.com/loco-3d/crocoddyl) pointing at this RFC
(the repo has both enabled). If the maintainers prefer another channel, URML will
move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,225 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, indirection through a problem formulation,
      coarse-to-precise gap).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: France / United Kingdom (INRIA / LAAS-CNRS, University of
      Edinburgh, NATO-allied); default policy passes at the optimal-control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML declares the
      goal and consumes the trajectory, Crocoddyl owns the optimization, the
      boundary holds on a zero-ROS runtime, composed-above and honest about the
      altitude).
