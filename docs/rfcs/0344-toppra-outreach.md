---
rfc: 0344
title: TOPP-RA (time-optimal path parameterization) integration, request for comment from the toppra maintainers
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

# RFC-0344: TOPP-RA integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`hungpham2511/toppra`](https://github.com/hungpham2511/toppra), TOPP-RA, a
library that computes the time-optimal parameterization of a given geometric
path subject to velocity, acceleration, and torque limits. It **requests review
and feedback from the toppra maintainers**.

URML's Layer-2 primitives describe an intent plus a goal. They do not compute a
trajectory. A time-parameterization library does: given a geometric path and a
set of kinematic and dynamic limits, toppra produces the timing that realizes
that path as fast as the limits allow. URML declares the limits, statically
checks that they are coherent and admissible before anything runs, then consumes
the timed trajectory toppra returns.

URML composes **above** toppra: URML intent -> a validated goal plus declared
velocity / acceleration / torque limits -> a geometric planner produces the path
-> toppra adds the optimal timing under those limits -> [ros2_control](0319-ros2-control-outreach.md)
executes it. The differentiator is **static admissibility and envelope checking
before the parameterization runs**: a program whose declared limits are
incoherent, or whose goal lies outside the reachable workspace, is rejected
before toppra is asked to time a path that could never be executed.

## Motivation

toppra is the standard offline answer to "given this path, time it optimally
under these limits," and it sits exactly at URML's intent / trajectory seam:

1. **It is the timing half of motion, and URML declares the limits it times
   against.** A geometric planner (OMPL, [RFC-0342](0342-ompl-outreach.md))
   produces a path; toppra parameterizes it under velocity, acceleration, and
   torque bounds. URML's manifest and safety envelope are where those bounds are
   declared. The library and the manifest describe the same limit set from two
   sides.
2. **It is the offline counterpart to online generation.** toppra parameterizes
   a known path offline; Ruckig ([RFC-0343](0343-ruckig-outreach.md)) generates
   limit-respecting motion online. URML's contract is the same for both: declare
   the limits, validate coherence, consume the trajectory. Engaging both in one
   wave keeps the offline and online surfaces aligned under a single intent
   model.
3. **It is where static admissibility pays off early.** toppra will faithfully
   time a path toward a goal that the robot cannot reach, or under a limit set
   that contradicts the safety envelope. URML's contribution is one layer up and
   earlier: a static check, before the parameterization runs, that the goal is
   in the reachable workspace and the declared limits are coherent with the
   envelope. A rejected program never reaches the solver.
4. **It grounds substrate-neutrality.** A limit declaration that maps onto a
   toppra constraint set must also map onto Ruckig, onto a vendor controller's
   own parameterizer, onto a planner with zero ROS dependency. toppra is one
   parameterization target among several; the same declared limits drive each.

Repo at [`hungpham2511/toppra`](https://github.com/hungpham2511/toppra) (about
886 stars, Issues **and** Discussions enabled, not archived, last push
2026-05-14, active). License is asked as a question below (the GitHub API did not
surface an SPDX id at verification time; understood to be MIT). Origin: academic
(Hung Pham); treated as INTL; passes US-federal default policy (open-source
library, no provenance gate at the parameterization layer).

## Detailed design

### URML v0.1 limit-declaration mapping (planned `toppra_path_cell.yaml` fixture)

| URML field | Maps to toppra concept |
|---|---|
| `robot_id`, `description` | The robot the path is timed for (carried at the manifest envelope) |
| `frames`, `declared_locations` | The frame the geometric path and its waypoints are expressed in; named goals a `move_to` resolves against |
| `mobility.max_velocity` | A velocity-bound term in toppra's `JointVelocityConstraint` set for a mobile base |
| `manipulation.reachable_workspace_m` | The reachable region a path's goal is statically checked against before parameterization |
| Safety-envelope velocity limits (Pass 3) | toppra `JointVelocityConstraint`; URML applies strictest-wins before the path is timed |
| Safety-envelope acceleration limits (Pass 3) | toppra `JointAccelerationConstraint`; conjoined with the envelope |
| Declared torque / effort limits (see gaps) | toppra `JointTorqueConstraint`; the limit set toppra parameterizes under |
| Geometric path (planner output) | The `SplineInterpolator` / waypoint path toppra parameterizes; URML supplies the goal, not the path |

### What URML v0.1 does not yet express for toppra

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Explicit joint and dynamic limit declaration.** URML's manifest carries a
   coarse `max_velocity` and the safety envelope's bounds, but it does not yet
   declare per-joint velocity, acceleration, and torque limits in the form a
   parameterization library consumes. A future Spec RFC could add an explicit
   joint and dynamic limit block so a toppra constraint set maps from the
   manifest cleanly rather than from convention.
2. **Trajectory / constraint-feasibility hint.** URML validates that a goal is
   admissible, but it does not yet carry a hint that the declared limit set is
   expected to be feasible for a given path class. A future Spec RFC could add an
   optional constraint-feasibility hint so the validator can flag a limit set
   that is coherent in isolation but cannot time a path within the envelope.

### Compatibility notes

- **Vendor org.** [`hungpham2511`](https://github.com/hungpham2511) (academic,
  Hung Pham; international).
- **Engagement repo.** [`hungpham2511/toppra`](https://github.com/hungpham2511/toppra):
  time-optimal path parameterization library; active.
- **Origin / policy.** International (academic). Treated as INTL; passes
  US-federal default policy (open-source library, no provenance gate at the
  parameterization layer).
- **License fit.** Understood to be MIT; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** toppra is one parameterization target among several;
  the same declared limits map onto Ruckig ([RFC-0343](0343-ruckig-outreach.md)),
  a vendor controller's own parameterizer, or a zero-ROS planner with no change
  to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The explicit joint and dynamic limit
  declaration and the constraint-feasibility hint are queued Spec RFCs.
- Reference runtime: no change in this RFC. A toppra mapping would supply the
  validated goal and the declared limit set, hand the geometric path to toppra
  for parameterization, and consume the timed trajectory for execution via
  [ros2_control](0319-ros2-control-outreach.md); the planned
  `toppra_path_cell.yaml` fixture would document the limit-declaration mapping.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Limit-declaration gap is real today.** The clean mapping depends on the
  queued explicit joint and dynamic limit block; until that lands, a toppra
  constraint set maps from the coarse manifest and the envelope by convention,
  not from a first-class declaration.
- **Path boundary is a handoff, not a contract.** URML declares the goal and the
  limits; the geometric path is the planner's output. The seam between "URML
  goal" and "path toppra times" depends on the planner in front, so the mapping
  is described at the goal and limit altitude rather than at a fixed path format.

## Alternatives considered

1. **Have URML model the geometric path itself.** Rejected. Computing a path is
   the planner's job and timing it is toppra's; URML declares intent, a goal, and
   the limits, and validates admissibility. Modelling the path in URML would fail
   the substrate-neutrality acid test and duplicate the planner.
2. **Engage only an online generator and skip offline parameterization.**
   Rejected. Offline time-optimal parameterization of a known path is a distinct
   and widely used surface; Ruckig ([RFC-0343](0343-ruckig-outreach.md)) covers
   the online case and toppra covers the offline one, and URML's limit-declaration
   contract should be shown to fit both.
3. **Push velocity and acceleration limits into the runtime only.** Rejected.
   The limits are a declared property of the robot and the safety envelope, not a
   runtime detail. Declaring them at the manifest layer is what lets URML check
   admissibility before the parameterization runs, which is the whole point.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the geometric planner whose path output toppra parameterizes.
- [RFC-0343 (Ruckig outreach)](0343-ruckig-outreach.md): the online
  motion-generation counterpart; the same limit-declaration contract.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the manipulation
  planning framework that orchestrates planning and parameterization.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the timed trajectory.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the toppra maintainers:

1. **Limit-declaration mapping.** How should URML declare velocity,
   acceleration, and torque limits so they map cleanly onto a toppra constraint
   set (`JointVelocityConstraint`, `JointAccelerationConstraint`,
   `JointTorqueConstraint`)? Is a per-joint limit block the right altitude?
2. **Path-source boundary.** toppra parameterizes a given geometric path. Is the
   right seam "URML supplies the validated goal and limits, the planner supplies
   the path, toppra times it," or is there a richer path representation URML
   should be aware of?
3. **Offline vs online relationship.** Is the offline-toppra / online-Ruckig
   split the way the maintainers see the two surfaces, and does one limit-set
   declaration sensibly serve both?
4. **Reachability check placement.** URML checks a goal against
   `reachable_workspace_m` before parameterization. Is there value in toppra
   surfacing an early infeasibility signal URML could consume, or does that stay
   entirely on URML's side?
5. **License.** What is the current license of `toppra` (the GitHub API did not
   surface an SPDX id at verification time; understood to be MIT)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0344 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`hungpham2511/toppra`](https://github.com/hungpham2511/toppra) pointing at this
RFC (the repo has both enabled). If the maintainers prefer another channel, URML
will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 886 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-14).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, limit-declaration gap, path-boundary
      handoff).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international academic; default policy passes at the
      parameterization layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; toppra is one
      parameterization target among several, URML declares limits and consumes
      the trajectory rather than planning).
