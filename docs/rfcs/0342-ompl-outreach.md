---
rfc: 0342
title: OMPL (Open Motion Planning Library) integration, request for comment from the OMPL maintainers
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

# RFC-0342: OMPL integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and trajectory-generation wave. This RFC is
the wave anchor. It reaches [`ompl/ompl`](https://github.com/ompl/ompl), the
Open Motion Planning Library: the de-facto sampling-based motion-planning core
(geometric and kinodynamic) that MoveIt ([RFC-0202](0202-moveit2-outreach.md))
builds on. It **requests review and feedback from the OMPL maintainers**.

URML and OMPL sit at adjacent layers, and the seam between them is clean. URML's
Layer-2 primitives (`move_to`, `dock`, `grasp`, `scan`, `take_off`) describe an
intent plus a goal. OMPL computes a collision-free, kinodynamically-feasible path
that realizes that goal under the robot's state space and constraints. URML does
not plan. It declares the goal and the capability constraints
(`reachable_workspace_m`, `max_velocity`, `max_payload`, with hard limits via the
safety envelope), statically validates that the query is admissible before the
planner runs, then consumes the resulting path.

URML composes **above** OMPL: URML intent -> validated goal plus constraints ->
an OMPL planning query -> ros2_control ([RFC-0319](0319-ros2-control-outreach.md))
executes the trajectory -> SLAM and state estimation
([RFC-0332](0332-robot-localization-outreach.md)) supply the world model the
planner checks against. The differentiator is **static admissibility and
envelope checking before a single OMPL planner is instantiated**: a goal outside
the declared reachable workspace, or one that the envelope forbids, is rejected
before any planning effort is spent.

## Motivation

OMPL is the planning library the rest of the stack stands on. Aligning URML's
declared goal-and-constraint surface with an OMPL query is the cleanest way to
make "validate before you plan" concrete:

1. **It is the planning core under MoveIt.** URML already engages MoveIt 2
   ([RFC-0202](0202-moveit2-outreach.md)) at the motion-group altitude. OMPL is
   the planner MoveIt drives underneath. Documenting the URML-to-OMPL seam
   directly clarifies what URML must declare so a query is well-posed regardless
   of whether MoveIt or a bare OMPL setup issues it.
2. **A URML goal is a planning query, minus the planner.** A `move_to` to a named
   pose, with the manipulation reachable workspace and the envelope limits, is
   exactly the goal region, state-space bounds, and validity constraints an OMPL
   query needs. URML supplies the well-posed query; OMPL supplies the path.
3. **Admissibility is cheap to check and expensive to discover late.** OMPL spends
   real compute sampling and connecting states. URML's contribution sits one layer
   up and earlier: a static check, before any planner runs, that the goal lies
   within the declared reachable workspace and that the envelope admits the motion.
   An inadmissible query never reaches the sampler.
4. **It grounds substrate-neutrality.** A URML goal that maps onto an OMPL query
   must also map onto any other planner that consumes a goal and constraints.
   OMPL is one planner target among several in this wave; the same goal declaration
   feeds toppra (RFC-0344), Crocoddyl (RFC-0346), OCS2 (RFC-0347), and
   teb_local_planner (RFC-0350) without changing the URML program.

Repo at [`ompl/ompl`](https://github.com/ompl/ompl) (about 2,070 stars, Issues
enabled, Discussions disabled, not archived, last push 2026-05-31, active).
License is asked as a question below (the GitHub API did not surface an SPDX id
at verification time; understood to be BSD-3-Clause). Origin: Rice University
(Kavraki Lab) lineage and community (United States); passes US-federal default
policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ompl_query_cell.yaml` fixture)

| URML field | Maps to OMPL query input |
|---|---|
| `robot_id`, `description` | Query identity (not an OMPL concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | The planning frame and named goal poses a `move_to` resolves against, fed as start and goal states |
| `mobility.drive_type` / `max_velocity` | The state-space class (for a mobile base) and the kinodynamic velocity bound on a control-space query |
| `manipulation.arm_count` + joints | The joint state space dimensionality for an arm query (the configuration space OMPL samples) |
| `manipulation.reachable_workspace_m` | The workspace bound the goal pose is checked against statically before the query is built |
| `perception` (occupancy / world model) | The collision world the OMPL state validity checker reads, supplied by SLAM and estimation (RFC-0332) |
| Safety envelope limits (Pass 3) | Conjoined with the state-space bounds and velocity limits; URML applies strictest-wins before the query is issued |

### What URML v0.1 does not yet express for OMPL

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Planner-class declaration.** URML's manifest does not declare which class of
   planner a deployment expects (geometric versus kinodynamic, sampling-based
   versus optimization-based). A future Spec RFC could add an optional
   planner-class hint so the validator and tooling can reason about the planning
   contract explicitly. Shared across this wave.
2. **Explicit joint and dynamic-limit declaration.** URML declares velocity and
   payload at a coarse altitude and pushes hard limits through the safety
   envelope. A future Spec RFC could add explicit per-joint position, velocity,
   and acceleration limits so an OMPL state space and control space can be bounded
   directly from the manifest. Shared with ros2_control (RFC-0319) and ruckig
   (RFC-0343).
3. **Trajectory and constraint-feasibility hint.** URML validates that a goal is
   admissible, not that a feasible path provably exists under the full constraint
   set. A future Spec RFC could add an optional feasibility hint carrying what the
   query asserts (for example, a maximum planning-time budget or a path-clearance
   requirement) so a downstream consumer can reason about planning success.

### Compatibility notes

- **Vendor org.** [`ompl`](https://github.com/ompl) (Open Motion Planning
  Library, Rice University Kavraki Lab lineage and open-source community).
- **Engagement repo.** [`ompl/ompl`](https://github.com/ompl/ompl): the
  sampling-based motion-planning library (geometric and kinodynamic); active.
- **Origin / policy.** United States (Rice University lineage, open-source
  community). Passes US-federal default policy (open-source library, no
  provenance gate at the planning layer).
- **License fit.** Understood to be BSD-3-Clause; not SPDX-detected at
  verification time, so asked below as a question.
- **Substrate-neutrality.** OMPL is one planner among several; the same URML goal
  and constraint declaration feeds toppra (RFC-0344), Crocoddyl (RFC-0346), OCS2
  (RFC-0347), or teb_local_planner (RFC-0350) with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The planner-class declaration, the
  explicit joint and dynamic-limit declaration, and the trajectory and
  constraint-feasibility hint are queued Spec RFCs.
- Reference runtime: no change in this RFC. An OMPL mapping would translate a
  validated primitive's goal and constraints into an OMPL planning query; the
  planned `ompl_query_cell.yaml` fixture would document the start, goal, and
  state-space bounds a well-posed query needs.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse constraint declaration today.** URML v0.1 declares velocity and payload
  coarsely and routes hard limits through the envelope. A well-posed OMPL query
  wants explicit state-space and control-space bounds, which is exactly the
  joint and dynamic-limit gap queued above. The mapping is honest that the
  declaration is coarser than OMPL ideally consumes today.
- **Library, not service.** OMPL is a planning library other stacks embed (MoveIt
  being the largest). URML's value to OMPL is mostly as a well-posed-query producer
  upstream, not as something OMPL itself needs. The engagement is honest about
  that asymmetry.

## Alternatives considered

1. **Engage only MoveIt and skip OMPL.** Rejected. MoveIt (RFC-0202) is the
   integrator altitude, but OMPL is where the planning contract actually lives. A
   URML goal must be a well-posed query whether MoveIt or a bare OMPL setup issues
   it; documenting the seam at the library clarifies what the manifest must
   declare independent of the integrator.
2. **Have URML emit OMPL planner configuration directly.** Rejected. Choosing a
   planner and tuning its parameters is a substrate-and-integrator concern below
   URML's altitude. URML declares the goal and constraints that make a query
   well-posed; it does not select RRT versus PRM. The planner-class hint queued
   above is the boundary URML would carry, not full planner configuration.
3. **Model OMPL's state space inside the URML manifest.** Rejected. The state
   space is a Layer-0 and substrate concern. URML declares capability over the
   robot (reachable workspace, limits) and lets the planner derive the state
   space. Modelling it in the manifest would fail the substrate-neutrality acid
   test.

## Prior art

- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the integrator that
  drives OMPL; the closest precedent for a planning-group manifest mapping.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the trajectory an OMPL query produces.
- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the state-estimation and world-model layer the OMPL validity checker reads.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the manipulation surface a kinodynamic arm query exercises.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  resolution a planning query's start and goal states depend on.
- Sibling Move #26 RFCs: RFC-0343 (ruckig), RFC-0344 (toppra), RFC-0346
  (Crocoddyl), RFC-0347 (OCS2), RFC-0350 (teb_local_planner).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the OMPL maintainers:

1. **Query boundary.** Is "URML goal plus constraints -> an OMPL planning query"
   the right seam, with URML producing a well-posed query and staying entirely
   above the planner, and OMPL owning the path computation?
2. **Well-posed-query inputs.** What does URML need to declare so a query is
   well-posed: state-space bounds, the validity-checker inputs (collision world,
   clearance), the goal region specification? Which of these belong in the
   manifest versus being supplied by the integrator?
3. **Geometric versus kinodynamic.** Should a URML manifest distinguish a
   geometric query from a kinodynamic one (the planner-class gap queued above), or
   is that better left entirely to the integrator?
4. **Validity-checker source.** URML expects the collision world to come from the
   estimation layer (RFC-0332). Is reading the world model from there the right
   alignment, or does OMPL expect the validity checker wired differently?
5. **Link-loss and replanning.** URML treats link loss and replanning at the
   behavior layer ([RFC-0006](0006-connectivity-and-link-loss.md)). Is there an
   OMPL-side expectation about replanning that a URML manifest should carry?
6. **License.** What is the current license of `ompl/ompl` (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD-3-Clause)?
7. **Conformance listing.** Would OMPL consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0342 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue on
[`ompl/ompl`](https://github.com/ompl/ompl) pointing at this RFC (Discussions are
disabled on the repo). If the maintainers prefer another venue, URML will move
the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 2,070 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-31).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse constraint declaration, library not
      service).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (planner-class, explicit joint
      and dynamic limits, feasibility hint) flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (Rice University lineage, open-source community); default
      policy passes at the planning layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; OMPL is one planner
      among many, URML declares the goal and validates admissibility, composed
      above not assumed).
