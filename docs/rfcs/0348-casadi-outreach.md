---
rfc: 0348
title: CasADi (symbolic optimization / optimal-control framework) integration, request for comment from the CasADi maintainers
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

# RFC-0348: CasADi integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
conceptual touch between URML v0.1 and an existing target's backend, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`casadi/casadi`](https://github.com/casadi/casadi), the general symbolic
optimization and optimal-control framework that model-predictive-control tools
build on, and **requests review and feedback from the CasADi maintainers**.

This is the lowest-direct-fit target in the wave, and the RFC is honest about
that up front. CasADi is general-purpose math, not robotics-specific, and it sits
well below URML's altitude. URML does not map onto it, has no symbolic surface,
and benefits from it only indirectly: the trajectory a CasADi-based MPC tool
returns is one the robot then executes, and URML validated the goal that tool
solved for. URML never calls CasADi.

URML composes **above** the controllers built on CasADi, not above CasADi itself.
A URML primitive declares intent plus a goal; an MPC tool such as acados (sibling
RFC-0349) or do-mpc, built on CasADi, formulates and solves the optimal-control
problem; `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)) executes the
result. This RFC is an ecosystem-acknowledgement plus a boundary clarification,
mirroring the Ceres Solver framing, and expects that confirmation more than an
integration.

## Motivation

CasADi is the symbolic-optimization engine under a large fraction of modern MPC
and trajectory-optimization stacks, including acados (sibling RFC-0349) and
do-mpc. That makes a boundary clarification with its maintainers worthwhile even
though the direct fit is the smallest in the wave:

1. **It realizes a goal URML declared, at a great distance.** URML's Layer-2
   primitives ([`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md))
   declare intent plus a goal and constraints. A CasADi-based MPC tool formulates
   that as an optimal-control problem and solves for the trajectory. URML never
   sees CasADi; it sees the trajectory the tool returns. Naming that chain is the
   point of the touch.
2. **It is a general-purpose backend, not an intent layer.** CasADi builds and
   differentiates symbolic expressions and dispatches them to nonlinear-program
   and integrator solvers. It is not robotics-specific. URML's contribution is
   many layers up and unrelated to that math: given the resulting trajectory,
   does the declared capability and the safety envelope admit the requested
   intent before the robot moves. URML declares and validates; it does not
   formulate or optimize.
3. **It clarifies a boundary the wave needs drawn.** Several Move #26 targets are
   MPC tools that build optimal-control problems with CasADi. Drawing the line
   once, with the backend's maintainers, keeps the rest of the wave honest: URML
   talks to the controller, not to CasADi, and consumes a trajectory, not a
   solver invocation.

Repo at [`casadi/casadi`](https://github.com/casadi/casadi) (about 2,222 stars,
Issues **and** Discussions enabled, not archived, last push 2026-06-02, active).
Originated at KU Leuven. License is asked as a question below (the GitHub API did
not surface an SPDX id at verification time; understood to be LGPL-3.0, which is
relevant only as a runtime and cross-citation matter, not vendoring, since URML
ships no CasADi code). Origin: Belgium (KU Leuven, NATO-allied); passes
US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is deliberately thin, the thinnest in the wave. CasADi is a
general-purpose symbolic-optimization backend, so the alignment is at the level
of "the trajectory a CasADi-based controller returns is one URML validated the
goal for," not a field-by-field control mapping.

| URML field | Relation to CasADi |
|---|---|
| Layer-2 goal and constraints | A CasADi-based MPC tool formulates these as an optimal-control problem; URML declares the goal, the tool solves it, URML never sees the symbolic problem |
| `mobility.max_velocity` / `max_payload` | Platform bounds that, in an MPC formulation, become constraints in a CasADi problem; declared at URML's altitude as manifest inputs, far above the formulation |
| `manipulation.reachable_workspace_m` | A coarse bound the realizing controller respects; URML declares it, the CasADi-based solver enforces its own constraints, the two never meet directly |
| Joint / dynamic limits (deferred) | Constraints in a CasADi optimal-control problem; URML defers these to the safety envelope today, with a queued declaration below |
| Safety envelope limits (Pass 3) | Unrelated to CasADi; conjoined strictest-wins against platform limits before dispatch, applied to the trajectory the controller returns, not the solver |

### What URML v0.1 does not yet express for CasADi

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Planner / solver-class declaration.** URML's manifest does not record which
   class of solver realizes a goal (an MPC tool built on CasADi, a sampling
   planner, a direct controller). A future Spec RFC could add an optional
   planner-class declaration so the validator can reason about the realizing layer
   explicitly, shared with the wave anchor (RFC-0342).
2. **Feasibility hint.** URML validates admissibility against a declared
   capability before a solver runs, but it carries no hint about whether a goal is
   likely solvable under the robot's dynamics. A future Spec RFC could add an
   optional feasibility hint so the validator can flag a goal an optimal-control
   solver would reject before the solver is even invoked.

### Compatibility notes

- **Vendor org.** [`casadi`](https://github.com/casadi) (the CasADi project,
  originated at KU Leuven).
- **Engagement repo.** [`casadi/casadi`](https://github.com/casadi/casadi), the
  symbolic optimization and optimal-control framework.
- **Origin / policy.** Belgium (KU Leuven, NATO-allied). Passes US-federal
  default policy (open-source academic backend, no provenance gate at the
  optimization layer).
- **License fit.** Understood to be LGPL-3.0; not SPDX-detected at verification
  time, so asked below as a question. URML ships no CasADi code, so the license
  is a runtime and cross-citation matter, not a vendoring one.
- **Substrate-neutrality.** CasADi is a backend many controllers share; URML's
  consume-the-trajectory posture is independent of which optimization framework a
  controller runs on, so the boundary holds on a zero-ROS, zero-CasADi runtime
  equally.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The planner / solver-class declaration
  and the feasibility hint are queued Spec RFCs, shared with the wave anchor.
- Reference runtime: no change. There is no CasADi adapter to build; URML declares
  a goal and consumes the trajectory a controller returns, not the solver
  invocation. No in-repo fixture is planned for CasADi specifically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lowest direct fit in the wave.** This is stated plainly: URML does not map
  onto CasADi, there is no adapter, no in-repo fixture is planned, and CasADi is
  general-purpose math well below URML's altitude. The value is a boundary
  clarification and an ecosystem touch, not an integration. URML benefits far more
  from the conceptual clarity than CasADi benefits from the engagement.
- **Indirection.** URML's relation to CasADi runs through an MPC tool and then
  through the execution layer, so the touch is two layers removed. A maintainer
  could reasonably ask why URML reaches them at all; the answer is the boundary
  clarification the wave needs and the confirmation that no direct contact point
  exists.

## Alternatives considered

1. **Skip CasADi and engage only the MPC tools built on it.** Rejected. The wave
   draws a boundary (URML declares a goal and consumes a trajectory, not the solver
   invocation). Naming that boundary once with the backend's maintainers keeps the
   MPC-tool engagements honest and avoids implying URML reaches into the optimizer
   in any of them.
2. **Claim a direct URML-to-CasADi mapping.** Rejected. It would over-promise.
   URML has no symbolic expression, no nonlinear program, no solver surface;
   pretending otherwise would fail the substrate-neutrality acid test and
   misrepresent the altitude.
3. **Model the optimal-control problem in the URML manifest.** Rejected. The
   symbolic problem, its constraints, and the solver are Layer 0. URML declares a
   goal and the capability the realizing controller must respect, not the
   formulation that solves it.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the planner boundary and the goal-declaration contract this RFC defers to.
- [RFC-0349 (acados outreach)](0349-acados-outreach.md): sibling MPC engagement
  built on CasADi; the closest coupling to this backend.
- [RFC-0347 (OCS2 outreach)](0347-ocs2-outreach.md): sibling optimal-control
  engagement in this wave.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the trajectory a CasADi-based controller produces.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the planning
  framework the realizing layer often sits inside.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  URML's whole-body manipulation surface, a goal an optimal-control tool realizes.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement touches.

## Unresolved questions

For the CasADi maintainers:

1. **Any meaningful contact point.** Is there any meaningful contact point between
   URML and CasADi, or is the only honest relation "CasADi is a backend below the
   boundary, URML talks to the controller built on it and CasADi stays invisible"?
2. **Backend-vs-intent boundary.** Is "URML talks to the controller, not to
   CasADi, and consumes a trajectory, not a solver invocation" the right boundary
   statement from your side, or does it mischaracterize where CasADi sits?
3. **Feasibility direction.** URML validates admissibility before a solver runs.
   Is a coarse feasibility signal (whether a declared goal is likely solvable
   under stated constraints) something a downstream consumer like URML could
   reasonably read, or is that better left entirely to the tool that wraps CasADi?
4. **acados coupling.** acados (RFC-0349) and several MPC tools build on CasADi.
   Is engaging the optimization framework and the MPC tools as separate, clearly
   bounded touches the right shape, or would you prefer one consolidated thread?
5. **License.** What is the current license of CasADi (the GitHub API did not
   surface an SPDX id at verification time; understood to be LGPL-3.0)? URML ships
   no CasADi code, so the question is about runtime and cross-citation, not
   vendoring.
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0348 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`casadi/casadi`](https://github.com/casadi/casadi) pointing at this RFC (the repo
has both enabled). If the maintainers prefer another channel, URML will move the
thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 2,222 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lowest direct fit in the wave, indirection).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Belgium (KU Leuven, NATO-allied); default policy passes at the
      optimization layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; CasADi is a
      general-purpose backend URML never touches directly, the boundary holds on a
      zero-CasADi runtime, composed-above and honest about the lowest-fit
      altitude).
