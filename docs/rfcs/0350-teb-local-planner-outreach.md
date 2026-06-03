---
rfc: 0350
title: teb_local_planner (Timed-Elastic-Band local navigation planning) integration, request for comment from the teb_local_planner maintainers
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

# RFC-0350: teb_local_planner integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`rst-tu-dortmund/teb_local_planner`](https://github.com/rst-tu-dortmund/teb_local_planner),
a local navigation planner that uses the Timed Elastic Band method to produce a
locally optimal trajectory for a mobile base under its kinematic and dynamic
constraints. It **requests review and feedback from the teb_local_planner
maintainers**.

URML's Layer-2 primitives describe an intent plus a goal. They do not plan a
trajectory. A local planner does: given a navigation goal, a kinematic model, a
footprint, and velocity limits, teb_local_planner computes the local trajectory
that realizes the goal while avoiding obstacles. URML's `move_to` intent plus
the manifest's mobility constraints feed the planner; URML statically validates
that the navigation goal is admissible before the planner runs, then consumes
the local trajectory.

URML composes **above** teb_local_planner: URML intent -> a validated `move_to`
goal plus declared mobility constraints (drive_type, max_velocity, footprint) ->
the local planner produces the local trajectory -> [ros2_control](0319-ros2-control-outreach.md)
executes it -> localization ([RFC-0332](0332-robot-localization-outreach.md))
supplies the world model. The differentiator is **static admissibility checking
of the navigation goal against the declared mobility model and the safety
envelope before the planner is invoked**. This planner is one of Nav2's
([RFC-0201](0201-nav2-outreach.md)) local-planner options; URML stays above the
choice.

## Motivation

teb_local_planner is a widely deployed local planner for differential, car-like,
and holonomic bases, and it sits exactly at URML's intent / trajectory seam for
mobile navigation:

1. **It is the local-trajectory half of navigation, and URML declares the
   constraints it plans against.** A global planner sets a route; the local
   planner produces the executable local trajectory under the base's kinematic
   model, footprint, and velocity limits. URML's `mobility` block is where those
   constraints are declared. The planner and the manifest describe the same
   mobile base from two sides.
2. **`move_to` is the intent the planner realizes.** URML's `move_to` plus a
   `declared_locations` goal is precisely a navigation goal. The acid test holds:
   the same `move_to` drives a real differential base, an Ackermann base, or a
   zero-ROS runtime, so teb_local_planner is one local-planning target among
   several.
3. **It is where static admissibility pays off early.** A local planner will try
   to realize a goal that lies outside the navigable region, or for a base whose
   declared drive type cannot achieve it. URML's contribution is one layer up and
   earlier: a static check, before the planner runs, that the goal is admissible
   under the declared mobility model and the safety envelope. A rejected program
   never reaches the planner.
4. **It grounds substrate-neutrality.** A mobility-constraint declaration that
   maps onto a Timed-Elastic-Band planner must also map onto an MPC local
   planner, onto Nav2's other controllers, onto a planner with zero ROS
   dependency. teb_local_planner is one local-planning target among several; the
   same declared constraints drive each.

Repo at [`rst-tu-dortmund/teb_local_planner`](https://github.com/rst-tu-dortmund/teb_local_planner)
(about 1,314 stars, Issues enabled, Discussions disabled, not archived, last
push 2026-01-09). The last push is a few months back; the project is maintained
and still the reference Timed-Elastic-Band implementation. The same lab also
publishes the MPC successor
[`rst-tu-dortmund/mpc_local_planner`](https://github.com/rst-tu-dortmund/mpc_local_planner)
(about 653 stars, older), folded into this thread below. License is asked as a
question below (the GitHub API did not surface an SPDX id at verification time;
understood to be GPL-3.0 for teb). Origin: TU Dortmund, Institute of Control
Theory and Systems Engineering (RST), Germany; treated as INTL; passes
US-federal default policy.

## Detailed design

### URML v0.1 mobility-constraint mapping (planned `teb_base_cell.yaml` fixture)

| URML field | Maps to teb_local_planner concept |
|---|---|
| `robot_id`, `description` | The mobile base the planner runs for (carried at the manifest envelope) |
| `frames`, `declared_locations` | The planning frame and the named goal poses a `move_to` resolves against |
| `mobility.drive_type` (differential / omnidirectional / ackermann / tracked) | The planner's kinematic model selection (differential, holonomic, car-like) |
| `mobility.max_velocity` | The planner's max velocity limit term |
| `mobility.max_payload` | A declared property checked against the envelope; not a planner term directly |
| Robot footprint (see gaps) | The planner's footprint model used for obstacle clearance |
| Safety-envelope velocity / acceleration limits (Pass 3) | The planner's velocity and acceleration bounds; URML applies strictest-wins before planning |
| `move_to` goal | The navigation goal the local planner produces a trajectory toward |

### What URML v0.1 does not yet express for teb_local_planner

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Planner-class declaration.** URML's manifest does not declare which
   planner class (local vs global, sampling vs optimization vs MPC) a deployment
   targets. A future Spec RFC could add an optional planner-class hint so the
   validator and tooling can reason about the planning surface explicitly.
2. **Explicit mobile-base constraint declaration.** URML carries `drive_type`
   and a coarse `max_velocity`, but it does not yet declare the robot footprint
   or per-axis velocity and acceleration limits in the form a local planner
   consumes. A future Spec RFC could add an explicit mobile-base constraint block
   (footprint, kinematic model parameters, per-axis limits) so the planner
   configuration maps from the manifest cleanly rather than from convention.

### Compatibility notes

- **Vendor org.** [`rst-tu-dortmund`](https://github.com/rst-tu-dortmund) (TU
  Dortmund, Institute of Control Theory and Systems Engineering, RST; Germany).
- **Engagement repo.** [`rst-tu-dortmund/teb_local_planner`](https://github.com/rst-tu-dortmund/teb_local_planner):
  Timed-Elastic-Band local navigation planner; maintained.
- **Sibling repo (folded into this thread).**
  [`rst-tu-dortmund/mpc_local_planner`](https://github.com/rst-tu-dortmund/mpc_local_planner),
  the MPC successor from the same lab (older). Which is the right integration
  surface is an open question below.
- **Origin / policy.** International (TU Dortmund / RST, Germany). Treated as
  INTL; passes US-federal default policy (open-source planner, no provenance gate
  at the planning layer).
- **License fit.** Understood to be GPL-3.0 for teb; not SPDX-detected at
  verification time, so asked below as a question. The relationship is
  runtime consumption and cross-citation, not vendoring: URML composes above the
  planner and links to it as a separate process / package, so a copyleft license
  on the planner does not propagate to URML's Apache-2.0 surface. URML asks the
  maintainers to confirm the license and the boundary.
- **Substrate-neutrality.** teb_local_planner is one local-planning target among
  several; the same declared mobility constraints map onto mpc_local_planner,
  onto Nav2's other controllers ([RFC-0201](0201-nav2-outreach.md)), or onto a
  zero-ROS planner with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The planner-class declaration and the
  explicit mobile-base constraint declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A teb_local_planner mapping would
  supply the validated `move_to` goal and the declared mobility constraints,
  invoke the local planner, and consume the local trajectory for execution via
  [ros2_control](0319-ros2-control-outreach.md); the planned `teb_base_cell.yaml`
  fixture would document the mobility-constraint mapping.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Constraint-declaration gap is real today.** The clean mapping depends on the
  queued explicit mobile-base constraint block (footprint, kinematic parameters,
  per-axis limits); until that lands, a planner configuration maps from
  `drive_type`, the coarse `max_velocity`, and the envelope by convention.
- **Two-repo ambiguity.** teb_local_planner and mpc_local_planner come from the
  same lab and overlap in purpose. Anchoring on teb and folding mpc into one
  thread risks under-serving whichever the maintainers consider the forward
  surface; question 2 below asks them to settle it.

## Alternatives considered

1. **Engage Nav2 only and skip the individual local planners.** Rejected. Nav2
   ([RFC-0201](0201-nav2-outreach.md)) was engaged earlier as the navigation
   framework, but the local planner is a distinct surface with its own kinematic
   model and constraint set, and is where URML's mobility-constraint declaration
   actually binds. Engaging the planner directly tests that binding.
2. **Have URML model the local trajectory itself.** Rejected. Producing the
   local trajectory is the planner's job; URML declares the `move_to` intent, the
   goal, and the mobility constraints, and validates admissibility. Modelling the
   trajectory in URML would fail the substrate-neutrality acid test and duplicate
   the planner.
3. **Open two separate RFCs, one per repo.** Rejected. teb_local_planner and
   mpc_local_planner share a lab and a maintainer community; two Issues in a day
   to one org is the pattern that has drawn AI-content closes elsewhere. One
   anchor thread that names both is more respectful and just as discoverable.

## Prior art

- [RFC-0201 (Nav2 outreach)](0201-nav2-outreach.md): the navigation framework
  that orchestrates global and local planning; this planner is one of its
  controller options.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the geometric planning surface for manipulation, the counterpart to mobile
  local planning here.
- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the estimation layer that supplies the world model the planner navigates in.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the local trajectory.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  surface the planning frame and goal poses resolve against.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the teb_local_planner maintainers:

1. **Mobile-base constraint mapping.** How should URML declare mobile-base
   constraints (kinematic model, footprint, velocity and acceleration limits) so
   they map cleanly onto a teb_local_planner configuration? Is a `drive_type`
   plus an explicit constraint block the right altitude?
2. **teb vs mpc_local_planner surface.** Which repo is the right integration
   surface going forward: the Timed-Elastic-Band planner (teb_local_planner) or
   the MPC successor (mpc_local_planner)? Should the engagement stay one thread or
   fork?
3. **Goal-admissibility seam.** URML checks a navigation goal for admissibility
   under the declared mobility model before the planner runs. Is there value in
   the planner surfacing an early infeasibility signal URML could consume, or does
   that stay entirely on URML's side?
4. **Link-loss behavior.** For a mobile base, loss of the world-model feed or the
   command link matters. Does the planner have a defined behavior URML's link-loss
   policy ([RFC-0006](0006-connectivity-and-link-loss.md)) should align with?
5. **License and copyleft boundary.** What is the current license of
   teb_local_planner and mpc_local_planner (understood to be GPL-3.0 for teb; not
   SPDX-detected at verification time)? Does the maintainers' reading of the
   boundary agree that URML composing above the planner as a separate process /
   package is runtime consumption, not a derivative work?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0350 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).
The `mpc_local_planner` row in the ledger shares this RFC; a dedicated row is
added only if the engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`rst-tu-dortmund/teb_local_planner`](https://github.com/rst-tu-dortmund/teb_local_planner)
pointing at this RFC (Discussions are disabled on the repo). If the maintainers
prefer mpc_local_planner or another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,314 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-01-09; mpc_local_planner
      named and folded in).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, constraint-declaration gap, two-repo
      ambiguity).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international (TU Dortmund / RST, Germany); default policy
      passes at the planning layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; teb_local_planner is
      one local-planning target among several, URML declares the goal and mobility
      constraints and consumes the trajectory rather than planning; copyleft
      boundary noted as runtime consumption, not vendoring).
