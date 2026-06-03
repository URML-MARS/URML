---
rfc: 0343
title: Ruckig (online jerk-limited trajectory generation) integration, request for comment from the Ruckig maintainers
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

# RFC-0343: Ruckig integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #26 is URML's motion-planning and trajectory-generation wave. This RFC
reaches [`pantor/ruckig`](https://github.com/pantor/ruckig): online, time-optimal,
jerk-limited trajectory generation between motion states in real time. Ruckig is
used inside MoveIt ([RFC-0202](0202-moveit2-outreach.md)) for time
parameterization. It **requests review and feedback from the Ruckig
maintainers**.

The seam between URML and ruckig is the kinematic-limit declaration. URML's
Layer-2 primitives (`move_to`, `dock`, `grasp`, `scan`, `take_off`) describe an
intent plus a goal. Ruckig generates the time-optimal, jerk-limited trajectory
that moves the robot toward that goal under per-axis velocity, acceleration, and
jerk limits. URML does not generate trajectories. It declares the limits (today
via the safety envelope), statically validates that the motion is admissible
before any motion runs, then consumes ruckig's trajectory.

URML composes **above** ruckig: URML intent -> validated goal plus per-axis
limits -> ruckig generates the online trajectory -> ros2_control
([RFC-0319](0319-ros2-control-outreach.md)) executes it -> SLAM and state
estimation ([RFC-0332](0332-robot-localization-outreach.md)) supply the world
model. The differentiator is **static envelope checking before a single
trajectory is generated**. URML's declared velocity, acceleration, and jerk
limits are ruckig's input constraints: URML validates the limits before motion,
ruckig generates the trajectory inside them.

This RFC sits alongside toppra (RFC-0344) on purpose. toppra parameterizes a
fixed path offline; ruckig generates trajectories online between states in real
time. The online-versus-offline boundary is one of the open questions below.

## Motivation

Ruckig is the online trajectory generator the rest of the stack reaches for when
motion must respect jerk limits in real time. Aligning URML's declared limit
surface with ruckig's input constraints makes "validate the limits before you
move" concrete:

1. **URML's declared limits are ruckig's input constraints.** Ruckig takes
   current state, target state, and per-axis velocity, acceleration, and jerk
   limits, and returns a time-optimal trajectory. URML already declares motion
   limits (today through the safety envelope). Those limits are exactly ruckig's
   constraint inputs, which makes the seam a direct mapping rather than a
   translation.
2. **Validation before motion is cheaper than discovering an infeasible limit
   late.** Ruckig computes a trajectory online, per control cycle. URML's
   contribution sits one layer up and earlier: a static check, before any motion,
   that the declared limits are internally consistent and that the envelope admits
   the requested motion. An inadmissible request never reaches the generator.
3. **It is the online complement to offline parameterization.** toppra (RFC-0344)
   parameterizes a fixed geometric path once, offline. Ruckig regenerates a
   jerk-limited trajectory online as states change. Engaging both makes the
   offline and online halves of the trajectory-generation layer explicit, and lets
   the maintainers tell URML where the boundary actually sits.
4. **It grounds substrate-neutrality.** A URML limit declaration that maps onto
   ruckig's inputs must also map onto any other trajectory generator that consumes
   per-axis limits. Ruckig is one generator among several in this wave; the same
   limit declaration feeds OMPL (RFC-0342), toppra (RFC-0344), Crocoddyl
   (RFC-0346), and OCS2 (RFC-0347) without changing the URML program.

Repo at [`pantor/ruckig`](https://github.com/pantor/ruckig) (about 1,243 stars,
Issues enabled, Discussions disabled, not archived, last push 2026-05-31,
active). License is asked as a question below (the GitHub API did not surface an
SPDX id at verification time; understood to be MIT). Origin: Germany (Lars
Berscheid / pantor); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ruckig_otg_cell.yaml` fixture)

| URML field | Maps to Ruckig input |
|---|---|
| `robot_id`, `description` | Trajectory-generation identity (not a ruckig concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | The frame and named target the goal state is resolved against before a trajectory is requested |
| `manipulation.arm_count` + joints | The per-axis degrees of freedom ruckig generates a trajectory across (the input dimension count) |
| `manipulation.reachable_workspace_m` | The workspace bound the target state is checked against statically before generation |
| `mobility.max_velocity` | The per-axis velocity limit, conjoined with the envelope, fed as a ruckig input constraint |
| Safety envelope limits (Pass 3) | The per-axis velocity, acceleration, and jerk limits; URML applies strictest-wins, and these become ruckig's input constraints |
| `connectivity` | Cycle-time and online-update expectations the generator runs under, surfaced at the manifest envelope |

### What URML v0.1 does not yet express for Ruckig

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Explicit joint and dynamic-limit declaration.** URML declares velocity at a
   coarse altitude and pushes acceleration and jerk through the safety envelope.
   Ruckig wants explicit per-axis velocity, acceleration, and jerk limits. A future
   Spec RFC could add explicit per-axis kinematic limits so they map onto ruckig's
   inputs directly. Shared with OMPL (RFC-0342) and ros2_control (RFC-0319).
2. **Trajectory and constraint-feasibility hint.** URML validates that the limits
   are admissible, not that a feasible trajectory result is asserted back. A future
   Spec RFC could add an optional feasibility hint so ruckig's feasibility result
   (whether a trajectory exists inside the limits) can be carried as a validation
   signal a downstream consumer reads.
3. **Planner-class declaration.** URML's manifest does not declare whether a
   deployment expects online generation (ruckig) or offline parameterization
   (toppra). A future Spec RFC could add an optional planner-class hint that
   captures the online-versus-offline distinction. Shared across this wave.

### Compatibility notes

- **Vendor org.** [`pantor`](https://github.com/pantor) (Lars Berscheid; ruckig is
  the flagship open-source project, with a separately licensed commercial Pro
  tier noted upstream).
- **Engagement repo.** [`pantor/ruckig`](https://github.com/pantor/ruckig): online
  jerk-limited trajectory generation; active, and used inside MoveIt for time
  parameterization.
- **Origin / policy.** Germany (Lars Berscheid / pantor). Treated as INTL; passes
  US-federal default policy (open-source library, no provenance gate at the
  trajectory-generation layer).
- **License fit.** Understood to be MIT for the open core; not SPDX-detected at
  verification time, so asked below as a question (the Pro tier license is
  separate and out of scope).
- **Substrate-neutrality.** Ruckig is one trajectory generator among several; the
  same URML limit declaration feeds OMPL (RFC-0342), toppra (RFC-0344), Crocoddyl
  (RFC-0346), or OCS2 (RFC-0347) with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The explicit joint and dynamic-limit
  declaration, the trajectory and constraint-feasibility hint, and the
  planner-class declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A ruckig mapping would feed a validated
  primitive's goal state and per-axis limits to ruckig as input constraints; the
  planned `ruckig_otg_cell.yaml` fixture would document the per-axis limit surface
  a well-formed generation request needs.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse limit declaration today.** URML v0.1 declares velocity coarsely and
  routes acceleration and jerk through the envelope. Ruckig wants explicit per-axis
  limits, which is exactly the joint and dynamic-limit gap queued above. The
  mapping is honest that the declaration is coarser than ruckig ideally consumes
  today.
- **Library, not service.** Ruckig is a generation library other stacks embed
  (MoveIt being the largest). URML's value to ruckig is mostly as a validated-limit
  producer upstream, not as something ruckig itself needs. The engagement is honest
  about that asymmetry.

## Alternatives considered

1. **Engage only toppra and treat trajectory generation as one target.** Rejected.
   toppra (RFC-0344) parameterizes a fixed path offline; ruckig generates online
   between states in real time. They occupy different halves of the layer, and
   collapsing them would hide the online-versus-offline boundary that the
   maintainers are best placed to settle.
2. **Have URML emit ruckig parameters directly (control cycle, tuning).** Rejected.
   Cycle time and generator tuning are substrate-and-integrator concerns below
   URML's altitude. URML declares the goal and the per-axis limits that constrain
   generation; it does not configure the generator's internals.
3. **Model jerk and acceleration limits as a new Layer-1 manifest block now.**
   Rejected for this RFC. That is exactly the explicit joint and dynamic-limit Spec
   RFC queued above, and it is not proposed here. URML routes the limits through
   the envelope today and flags the explicit-declaration gap rather than smuggling
   a spec change into an Outreach RFC.

## Prior art

- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the integrator that
  uses ruckig for time parameterization; the closest precedent for this seam.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the trajectory ruckig generates.
- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the state-estimation layer that supplies the world model around the motion.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the multi-axis manipulation surface a per-axis jerk-limited trajectory exercises.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  resolution a target state depends on before generation.
- Sibling Move #26 RFCs: RFC-0342 (OMPL, the wave anchor), RFC-0344 (toppra, the
  offline complement), RFC-0346 (Crocoddyl), RFC-0347 (OCS2), RFC-0350
  (teb_local_planner).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the Ruckig maintainers:

1. **Limit-declaration mapping.** How should URML declare per-axis kinematic limits
   (velocity, acceleration, jerk) so they map onto ruckig's input constraints
   directly? Is per-axis the right granularity, and is there a preferred shape?
2. **Feasibility as a validation signal.** Ruckig returns whether a trajectory
   exists inside the given limits. Is that feasibility result a useful signal for
   URML to surface at validation time, before motion, or is it strictly a runtime
   result?
3. **Online versus offline boundary.** Where does the boundary sit between
   ruckig's online generation and offline path parameterization (toppra,
   RFC-0344)? Should a URML manifest distinguish the two (the planner-class gap
   queued above), and which target owns which goal shape?
4. **Goal-state versus path input.** Ruckig generates between motion states. Is
   "URML goal plus current state -> ruckig target" the right input boundary, or
   does ruckig expect a fuller waypoint structure URML should declare?
5. **License.** What is the current license of `pantor/ruckig` open core (the
   GitHub API did not surface an SPDX id at verification time; understood to be
   MIT), and is the Pro tier correctly understood as out of scope for this open
   mapping?
6. **Conformance listing.** Would ruckig consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0343 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue on
[`pantor/ruckig`](https://github.com/pantor/ruckig) pointing at this RFC
(Discussions are disabled on the repo). If the maintainers prefer another venue,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,243 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-31).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse limit declaration, library not
      service).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (explicit joint and dynamic
      limits, feasibility hint, planner-class) flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Germany (Lars Berscheid / pantor); default policy passes at the
      trajectory-generation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; ruckig is one
      generator among many, URML declares the limits and validates admissibility,
      composed above not assumed).
