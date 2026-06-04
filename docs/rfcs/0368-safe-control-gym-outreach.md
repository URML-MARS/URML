---
rfc: 0368
title: safe-control-gym (safe control and safe-RL benchmark) integration, request for comment from the safe-control-gym maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-04
updated: 2026-06-04
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

# RFC-0368: safe-control-gym integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`utiasDSL/safe-control-gym`](https://github.com/utiasDSL/safe-control-gym)
(the safe-control-gym benchmark suite for safe control and safe reinforcement
learning with constraints, supporting CBF, MPC, and RL controllers on quadrotor
and cartpole systems), and **requests review and feedback from the
safe-control-gym maintainers**.

URML and safe-control-gym sit at two different altitudes, and the honest fit is
the seam between them. URML declares capability and safety limits at the
**intent** level: a capability manifest plus a safety envelope (geofence,
occupancy, velocity and altitude limits, link-loss behavior), statically
checked at validator Pass 3 before a request is dispatched. safe-control-gym
sits at the **control** level: it is where those limits become control-theoretic
constraints (state and input constraints, control barrier functions) and a
controller is evaluated for satisfying them under a benchmark.

The composition: URML declares a portable, intent-level constraint set and
validates a request before dispatch; safe-control-gym is where a controller is
measured for whether it honors that constraint set during execution. URML does
not do control and does not synthesize a controller. It bounds and validates
what is dispatched; safe-control-gym evaluates whether the controller that
executes the dispatched intent stays inside the bound.

## Motivation

safe-control-gym is a focused benchmark for safe control and safe RL, and it is
exactly the layer where URML's declared limits would have to become enforceable
control-theoretic guarantees:

1. **It is the constraint-evaluation layer URML stops short of.** URML's safety
   envelope declares intent-level limits (geofence, velocity and altitude
   ceilings, occupancy). safe-control-gym is where state and input constraints
   and control barrier functions are expressed and a controller is scored on
   satisfying them. The two describe the same limit from two sides: a
   declaration above and an enforcement evaluation below.
2. **It makes URML's altitude claim concrete.** URML claims it bounds and
   validates intent, not that it controls. safe-control-gym is the cleanest
   place to show the boundary: URML rejects a request whose declared intent
   exceeds the envelope; safe-control-gym measures whether the controller that
   runs an admitted request keeps the system inside the constraints.
3. **Its systems are URML-shaped targets.** Quadrotor and cartpole are concrete
   Layer-1 bodies. A quadrotor's velocity and altitude limits map onto URML
   mobility fields and envelope limits; the gym is where those same numbers are
   evaluated as control constraints rather than declared as intent bounds.
4. **It is substrate-neutral evidence.** A constraint set that maps onto
   safe-control-gym's constraint specification, and also onto a real controller,
   is evidence that URML's envelope is a portable declaration and not a
   benchmark-shaped artifact.

Repo at [`utiasDSL/safe-control-gym`](https://github.com/utiasDSL/safe-control-gym)
(about 885 stars, Issues enabled, not archived, active, last push 2026-04-29).
Origin: the Learning Systems and Robotics Lab (formerly UTIAS, University of
Toronto, Canada, NATO-allied).

## Detailed design

### URML v0.1 envelope-to-constraint mapping (conceptual; no fixture lands here)

| URML field | Maps to safe-control-gym concept |
|---|---|
| `robot_id`, `description` | The benchmarked system's identity (carried at the manifest envelope; not a gym concept) |
| `mobility.max_velocity` | A velocity state or input constraint on the quadrotor / cartpole system |
| `mobility.service_ceiling` / altitude limits | An altitude state constraint in the quadrotor benchmark |
| Safety envelope geofence / occupancy (Pass 3) | A spatial state constraint set the controller is evaluated against |
| Safety envelope velocity / altitude limits (Pass 3) | State and input constraints, conjoined strictest-wins before dispatch |
| Link-loss behavior ([RFC-0006](0006-connectivity-and-link-loss.md)) | A degraded-mode constraint regime a safe controller must respect on link loss |
| A controller's constraint-satisfaction record | Candidate evidence feeding a URML capability / envelope claim (see queued gap below) |

### What URML v0.1 does not yet express for safe-control-gym

These are **gaps surfaced by the mapping**, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Constraint / safety-specification export.** URML's safety envelope is an
   internal validator artifact; it has no portable export a safe controller or a
   benchmark could consume as a constraint set. A future Spec RFC could define a
   constraint export from the envelope (state and input limits, geofence,
   occupancy) that a tool like safe-control-gym could read directly.
2. **Learned-safe-policy-as-substrate declaration.** A controller measured under
   constraints is a candidate substrate. URML has no manifest declaration for a
   learned or synthesized safe controller as the body a primitive dispatches to.
   A future Spec RFC could add one, cross-referencing the learned-controller
   framing from Brax (Move #24) and robomimic (RFC-0360, Move #27).

### Compatibility notes

- **Origin / policy.** Canada (Learning Systems and Robotics Lab, formerly
  UTIAS, University of Toronto). NATO-allied; passes US-federal default policy
  (open-source academic benchmark, no provenance gate at the control layer).
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring. URML composes above the control layer and would
  cite safe-control-gym as the constraint-evaluation surface, not bundle it.
- **Substrate-neutrality.** safe-control-gym is one constraint-evaluation
  surface among several; the same URML envelope limits map onto a CBF-based
  controller, an MPC controller, or a real safety monitor with no change to the
  declaration.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The constraint export and the
  learned-safe-policy-as-substrate declaration are queued Spec RFCs.
- Reference runtime: no change. A mapping would express a URML envelope's limits
  as a safe-control-gym constraint set for evaluation; URML's contribution stays
  the static Pass 3 check before dispatch, above the controller.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Altitude asymmetry.** URML benefits from a credible constraint-evaluation
  surface more than safe-control-gym benefits from an intent-level declaration
  above it. The engagement is honest about that asymmetry.
- **Boundary risk.** The seam between an intent-level limit and a control-level
  constraint is easy to overstate. URML declares and validates; it does not
  guarantee control-theoretic satisfaction. Question 2 below asks the
  maintainers to help draw that line precisely.

## Alternatives considered

1. **Claim URML enforces the constraints at control time.** Rejected. It would
   be false. URML statically validates intent against a declared envelope before
   dispatch; control-theoretic satisfaction is the controller's job, which is
   exactly what safe-control-gym evaluates. Overstating this would fail the
   honest-substrate-limit norm ([RFC-0014](0014-substrate-conformance.md)).
2. **Model the gym's constraints inside the URML manifest.** Rejected. State and
   input constraints and CBFs are control-layer concerns. URML declares
   intent-level limits over the body, not the controller's constraint
   formulation; modelling them would fail the substrate-neutrality acid test.
3. **Skip the control layer and engage only simulators.** Rejected. The safety
   and runtime-verification wave is precisely about the layer where declared
   limits become enforced guarantees. safe-control-gym is the benchmark that
   makes URML's "validate before dispatch" boundary concrete against a controller.

## Prior art

- [RFC-0362 (RTAMT)](0362-rtamt-outreach.md): the Move #28 wave anchor;
  runtime-verification of temporal-logic specifications, the closest sibling on
  the verification side of this wave.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  control-framework engagement URML's envelope limits dispatch above.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  related work where URML's envelope (geofence, altitude) meets an external
  constraint authority.
- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the link-loss behavior a degraded-mode constraint regime must respect.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  honest-substrate-limit norm this RFC applies to the altitude boundary.
- Sibling Move #28 RFC: RFC-0369 (OmniSafe), the safe-RL framework engaged
  alongside this benchmark.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  capability and safety-envelope surface this engagement exercises.

## Unresolved questions

For the safe-control-gym maintainers:

1. **Constraint-set mapping.** Does a URML safety-envelope constraint set
   (velocity and altitude limits, geofence, occupancy) map cleanly onto
   safe-control-gym's constraint specification (state and input constraints,
   CBFs), or is the abstraction mismatch too large for a direct mapping?
2. **The boundary.** Is "URML declares and validates intent-level limits before
   dispatch; safe-control-gym evaluates control-level constraint satisfaction"
   the right division of labor, with URML staying entirely above the controller?
3. **Constraint-satisfaction record.** Could a benchmarked controller's
   constraint-satisfaction record feed back into a URML capability or envelope
   claim (for example, as declared evidence that a controller honors a given
   limit), or is that outside the benchmark's intended use?
4. **System scope.** Are quadrotor and cartpole the right first systems to anchor
   a mapping on, or is there a different benchmark configuration that would make
   the intent-to-constraint boundary clearest?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0368 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`utiasDSL/safe-control-gym`](https://github.com/utiasDSL/safe-control-gym)
pointing at this RFC (the repo has Issues enabled). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 885 stars, not archived, Issues
      enabled, active, last push 2026-04-29).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, altitude asymmetry, boundary risk).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; envelope-export and learned-safe-policy gaps
      flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: Canada (Learning Systems and Robotics Lab, NATO-allied);
      default policy passes at the control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML composes above
      the control layer, declares and validates intent, does not control).
