---
rfc: 0349
title: acados (embedded nonlinear MPC) integration, request for comment from the acados maintainers
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

# RFC-0349: acados integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's solver, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`acados/acados`](https://github.com/acados/acados), the framework that generates
fast embedded solvers for real-time nonlinear model-predictive control, and
**requests review and feedback from the acados maintainers**.

acados sits below URML, but a notch more directly than the general optimization
backend it builds on. acados generates the embedded NMPC solver that runs the
optimal-control problem in real time, and it is built on CasADi (sibling
[RFC-0348](0348-casadi-outreach.md)). The direct contact point is constraints. A
URML primitive declares intent plus a goal, and it declares the capability and
the safety limits the realizing controller must respect. An acados NMPC is
exactly where those limits become hard constraints in the optimal-control
problem. URML declares the constraints and the goal, validates admissibility
before anything runs, and consumes the result. URML talks to the controller or
the integration around the acados solver, not the hand-written OCP.

URML composes **above** the acados-based controller: URML intent -> validated
goal plus constraints -> an acados NMPC formulates and solves the OCP ->
`ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)) executes the result.
The differentiator is **static admissibility and envelope checking before the
NMPC solver is invoked**: a goal outside the declared capability, or one the
envelope forbids, is rejected before any control horizon is solved.

## Motivation

acados is the embedded-NMPC solver under a growing share of real-time control
stacks, and constraints are the one place where URML's declared limits and the
solver's formulation meet, so the engagement is more direct than the CasADi touch
it sits next to:

1. **Constraints are the contact point.** URML's Layer-2 primitives
   ([`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md))
   declare a goal plus the capability and safety limits the controller must
   respect. In an acados NMPC those limits are hard constraints in the OCP. URML
   declares them at a coarse altitude; the acados formulation enforces them as
   bounds. Naming that correspondence is the point of the touch.
2. **It realizes the goal in real time, and URML validated it first.** acados
   generates a solver that runs the control horizon at hardware rates. URML's
   contribution sits one layer up and earlier: a static check, before the solver
   is invoked, that the declared capability and the safety envelope admit the
   requested intent. An inadmissible goal never enters the control loop.
3. **It is a solver backend, not an intent layer.** acados builds and solves the
   OCP and generates C for embedded targets. URML does not write the OCP, does not
   tune the solver, and has no symbolic surface. URML talks to the controller node
   or the integration around the solver, declares the goal and the limits, and
   consumes the trajectory or the control the controller produces.

Repo at [`acados/acados`](https://github.com/acados/acados) (about 1,362 stars,
Issues enabled, Discussions disabled, not archived, last push 2026-05-22,
active). Built on CasADi (RFC-0348). License is asked as a question below (the
GitHub API did not surface an SPDX id at verification time; understood to be
BSD-2-Clause, which is relevant only as a runtime and cross-citation matter, not
vendoring, since URML ships no acados code). Origin: University of Freiburg
(syscop, Germany, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is at the constraint altitude: the capability and safety limits URML
declares are the bounds an acados OCP enforces, not a field-by-field control
mapping. URML never writes the OCP.

| URML field | Relation to acados |
|---|---|
| Layer-2 goal | The setpoint or reference an acados NMPC tracks; URML declares the goal, the controller formulates the OCP, URML never sees the solver internals |
| `mobility.max_velocity` / `max_payload` | Platform bounds that become state and input constraints in the acados OCP; declared at URML's altitude as manifest inputs, far above the formulation |
| `manipulation.reachable_workspace_m` | A coarse bound the realizing controller respects; URML declares it, the acados OCP enforces its own constraints, the two meet only at the constraint level |
| Joint / dynamic limits (deferred) | Hard constraints in an acados OCP; URML defers these to the safety envelope today, with a queued declaration below |
| Safety envelope limits (Pass 3) | The hard limits URML conjoins strictest-wins before dispatch; in an acados NMPC these are exactly the constraints the OCP must satisfy at every step |

### What URML v0.1 does not yet express for acados

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Dynamic-limit declaration.** URML declares velocity and payload coarsely and
   routes hard limits through the safety envelope. A future Spec RFC could add
   explicit per-joint position, velocity, and acceleration limits so the
   constraints an acados OCP enforces can be read directly from the manifest.
   Shared with the wave anchor (RFC-0342) and ros2_control (RFC-0319).
2. **Feasibility hint.** URML validates admissibility against a declared
   capability before a solver runs, but it carries no hint about whether a goal is
   likely solvable under the robot's dynamics. A future Spec RFC could add an
   optional feasibility hint so the validator can flag a goal an NMPC would reject
   before the solver is even invoked. Shared across this wave.

### Compatibility notes

- **Vendor org.** [`acados`](https://github.com/acados) (the acados project,
  University of Freiburg syscop lineage).
- **Engagement repo.** [`acados/acados`](https://github.com/acados/acados), the
  embedded nonlinear MPC solver framework.
- **Origin / policy.** Germany (University of Freiburg syscop, NATO-allied).
  Passes US-federal default policy (open-source academic solver, no provenance
  gate at the control layer).
- **License fit.** Understood to be BSD-2-Clause; not SPDX-detected at
  verification time, so asked below as a question. URML ships no acados code, so
  the license is a runtime and cross-citation matter, not a vendoring one.
- **CasADi coupling.** acados is built on CasADi (RFC-0348). URML's relation to
  CasADi is two layers removed and indirect; its relation to acados is the
  constraint touch above. The two engagements are deliberately separate, clearly
  bounded.
- **Substrate-neutrality.** acados is one embedded-NMPC solver among several; the
  same URML goal and constraint declaration feeds OCS2 (RFC-0347) or any other
  optimal-control realizing layer with no change to the URML program, so the
  boundary holds on a zero-ROS, zero-acados runtime equally.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The dynamic-limit declaration and the
  feasibility hint are queued Spec RFCs, shared with the wave anchor.
- Reference runtime: no change in this RFC. An acados mapping would route a
  validated primitive's goal and declared limits to the acados-based controller
  node, where the limits become OCP constraints; no in-repo fixture is planned for
  acados specifically, since URML talks to the controller, not the solver.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Solver-backend altitude.** acados is a solver other controllers embed, not an
  intent layer URML maps onto field by field. The mapping is at the constraint
  level only, and the value to acados is mostly as a well-formed-constraint
  producer upstream, not as something acados itself needs. The engagement is
  honest about that asymmetry.
- **Coarse constraint declaration today.** URML v0.1 declares velocity and payload
  coarsely and routes hard limits through the envelope. An acados OCP wants
  explicit state and input bounds, which is exactly the dynamic-limit gap queued
  above. The mapping is honest that the declaration is coarser than acados ideally
  consumes today.

## Alternatives considered

1. **Skip acados and engage only the controllers built on it.** Rejected. The wave
   draws a boundary (URML declares a goal and constraints, the controller solves
   the OCP). The constraint correspondence is sharpest at the solver that turns
   declared limits into hard bounds, so naming it with the acados maintainers keeps
   the controller engagements honest about where URML's limits land.
2. **Have URML emit the acados OCP directly.** Rejected. Formulating the
   optimal-control problem, choosing the integrator, and tuning the solver are
   substrate-and-integrator concerns below URML's altitude. URML declares the goal
   and the limits the OCP must respect; it does not write the OCP.
3. **Model the OCP and the solver settings in the URML manifest.** Rejected. The
   OCP, its horizon, and the solver configuration are Layer 0. URML declares
   capability over the robot and the limits the realizing controller must honor,
   not the formulation that solves it. Modelling the OCP would fail the
   substrate-neutrality acid test.

## Prior art

- [RFC-0348 (CasADi outreach)](0348-casadi-outreach.md): the symbolic-optimization
  backend acados is built on; the closest coupling to this engagement.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the goal-and-constraint declaration contract this RFC defers to.
- [RFC-0347 (OCS2 outreach)](0347-ocs2-outreach.md): sibling optimal-control
  engagement in this wave.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the result an acados-based controller produces.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  resolution a tracked goal's reference depends on.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement touches.

## Unresolved questions

For the acados maintainers:

1. **Constraint declaration.** How should URML declare the capability and safety
   limits an NMPC must enforce so they map cleanly to OCP constraints (state
   bounds, input bounds, nonlinear path constraints)? Is the coarse manifest
   declaration plus envelope a reasonable upstream source for those bounds?
2. **Controller-vs-solver boundary.** Is "URML talks to the acados-based
   controller node or the integration around the solver, not the OCP itself, and
   consumes the result, not a solver invocation" the right boundary statement from
   your side?
3. **Feasibility direction.** URML validates admissibility before a solver runs.
   Is a coarse feasibility signal (whether a declared goal is likely solvable under
   stated constraints and dynamics) something a downstream consumer like URML could
   reasonably read, or is that better left entirely to the controller that wraps
   acados?
4. **CasADi coupling.** acados is built on CasADi (RFC-0348). Is engaging the
   solver and the optimization backend as separate, clearly bounded touches the
   right shape, or would you prefer one consolidated thread?
5. **License.** What is the current license of `acados/acados` (the GitHub API did
   not surface an SPDX id at verification time; understood to be BSD-2-Clause)?
   URML ships no acados code, so the question is about runtime and cross-citation,
   not vendoring.
6. **Conformance listing.** Would acados consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0349 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue on
[`acados/acados`](https://github.com/acados/acados) pointing at this RFC
(Discussions are disabled on the repo). If the maintainers prefer another venue,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,362 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-22).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, solver-backend altitude, coarse constraint
      declaration).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (dynamic-limit declaration,
      feasibility hint) flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: Germany (University of Freiburg syscop, NATO-allied); default
      policy passes at the control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; acados is one embedded
      NMPC solver among many, URML declares the goal and constraints and validates
      admissibility, talks to the controller not the solver, composed above not
      assumed).
