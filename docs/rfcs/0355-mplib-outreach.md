---
rfc: 0355
title: MPlib (manipulation motion-planning library) integration, request for comment from the MPlib maintainers
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

# RFC-0355: MPlib integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`haosulab/MPlib`](https://github.com/haosulab/MPlib), a lightweight
motion-planning library for manipulators used across the SAPIEN ecosystem. MPlib
plans collision-free arm trajectories by wrapping OMPL, FCL, and a kinematics
layer. It **requests review and feedback from the MPlib maintainers**.

URML and MPlib sit at adjacent layers, and the seam between them is clean. URML's
manipulation primitives (`move_to` a pose, `grasp`, `release`) declare an intent
plus a target and the arm and gripper capability (`manipulation.grippers`,
`manipulation.reachable_workspace_m`). MPlib plans the collision-free trajectory
that realizes that intent. URML does not plan. It declares the target and the
capability, statically validates that the target lies within the declared
reachable workspace and within the active safety envelope before MPlib runs, then
consumes the resulting trajectory.

URML composes **above** MPlib: URML intent -> validated target plus capability ->
an MPlib planning call -> ros2_control
([RFC-0319](0319-ros2-control-outreach.md)) executes the trajectory. MPlib is the
manipulation-specific counterpart to the general OMPL engagement
([RFC-0342](0342-ompl-outreach.md), the Move #26 planning sibling), which MPlib
wraps. The differentiator is **static admissibility and envelope checking before
a single plan request is built**: a target outside the declared reachable
workspace, or one the envelope forbids, is rejected before any planning effort is
spent.

## Motivation

MPlib is a focused manipulation-planning library, and aligning URML's declared
target-and-capability surface with an MPlib planning call is a clean way to make
"validate before you plan" concrete:

1. **It is manipulation-specific planning over a shared core.** MPlib wraps OMPL,
   FCL, and a kinematics layer into a planner aimed at manipulators. URML already
   engages OMPL ([RFC-0342](0342-ompl-outreach.md)) at the general
   sampling-based-planner altitude. Documenting the URML-to-MPlib seam directly
   clarifies what URML must declare so a manipulation plan request is well-posed
   at the library MPlib presents, not just at the core it wraps.
2. **A URML target is a plan request, minus the planner.** A `move_to` to a named
   pose, with the manipulation reachable workspace and the envelope limits, is the
   goal, the planning group, and the bound set an MPlib call needs. URML supplies
   the well-posed request; MPlib supplies the collision-free trajectory.
3. **Admissibility is cheap to check and expensive to discover late.** MPlib
   spends real compute sampling and collision-checking a trajectory. URML's
   contribution sits one layer up and earlier: a static check, before the first
   plan, that the target lies within the declared reachable workspace and that the
   envelope admits the motion. An inadmissible target never reaches the planner.
4. **It grounds substrate-neutrality.** A URML target that maps onto an MPlib plan
   request must also map onto bare OMPL, onto MoveIt, and onto an IK solver. MPlib
   is one manipulation backend among several in this wave; the same target
   declaration feeds them without changing the URML program.

Repo at [`haosulab/MPlib`](https://github.com/haosulab/MPlib) (about 266 stars,
Issues enabled, not archived, last push 2026-05-17, active). SAPIEN, from the same
lab, was recorded in Move #24 as a Tier B simulation row; this is a distinct
manipulation-planning repo. Origin: Hao Su Lab, UC San Diego (United States);
passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mplib_plan_cell.yaml` fixture)

| URML field | Maps to MPlib plan input |
|---|---|
| `robot_id`, `description` | Plan identity (not an MPlib concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | The planning frame and the named target pose a `move_to` resolves against, fed as the goal |
| `manipulation.arm_count` + joints | The planning group and joint DOF the MPlib call plans for |
| `manipulation.reachable_workspace_m` | The workspace bound the target pose is checked against statically before the plan request is built |
| `manipulation.grippers[].kind` / `force_max_n` | The gripper DOF a `grasp` actuates; force bound checked statically before the command is issued |
| `perception` (occupancy / world model) | The collision world the MPlib (FCL) collision check reads |
| Safety envelope limits (Pass 3) | Conjoined with the joint and velocity bounds; URML applies strictest-wins before the plan request |

### What URML v0.1 does not yet express for MPlib

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **IK-target / joint-configuration declaration.** URML declares a target pose
   and the reachable workspace, not an explicit IK target or the joint
   configuration a plan resolves to. A future Spec RFC could add an optional
   IK-target declaration so a plan request is well-posed directly from the
   manifest. Shared across this wave (anchored at RFC-0352).
2. **Explicit joint-limit declaration.** URML pushes hard limits through the
   safety envelope at a coarse altitude. A future Spec RFC could add explicit
   per-joint position, velocity, and acceleration limits so an MPlib planning
   group can be bounded directly from the manifest. Shared with ros2_control
   ([RFC-0319](0319-ros2-control-outreach.md)) and OMPL (RFC-0342).
3. **Manipulation-planner-class hint.** URML's manifest does not declare which
   class of manipulation backend a deployment expects (a full collision-free
   planner versus an IK solver versus differential IK). A future Spec RFC could
   add an optional planner-class hint so the validator and tooling can reason
   about the manipulation contract explicitly.

### Compatibility notes

- **Vendor org.** [`haosulab`](https://github.com/haosulab) (Hao Su Lab, UC San
  Diego, robotics and embodied-AI research).
- **Engagement repo.** [`haosulab/MPlib`](https://github.com/haosulab/MPlib): a
  lightweight motion-planning library for manipulators, wrapping OMPL, FCL, and a
  kinematics layer; active.
- **Origin / policy.** United States (UC San Diego). Passes US-federal default
  policy (open-source library, no provenance gate at the planning layer).
- **License note.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring.
- **Substrate-neutrality.** MPlib is one manipulation backend among several, and
  it wraps OMPL ([RFC-0342](0342-ompl-outreach.md)); the same URML target and
  capability declaration feeds bare OMPL, MoveIt (RFC-0202), or an IK solver
  (RFC-0352) with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The IK-target declaration, the explicit
  joint-limit declaration, and the manipulation-planner-class hint are queued Spec
  RFCs.
- Reference runtime: no change in this RFC. An MPlib mapping would translate a
  validated primitive's target and capability into an MPlib planning call; the
  planned `mplib_plan_cell.yaml` fixture would document the planning group, goal,
  and bound set a well-posed request needs.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse target declaration today.** URML v0.1 declares a target pose and the
  reachable workspace, and routes hard limits through the envelope. A well-posed
  MPlib request wants an explicit planning group and joint bounds, which is
  exactly the gap queued above. The mapping is honest that the declaration is
  coarser than MPlib ideally consumes today.
- **Wraps OMPL.** MPlib's planning core is OMPL, which URML engages separately
  (RFC-0342). URML's value to MPlib is mostly as a well-posed-request producer
  upstream, not as something the library needs. The engagement is honest about
  that asymmetry and about the overlap with the OMPL thread.

## Alternatives considered

1. **Engage only OMPL and skip MPlib.** Rejected. OMPL (RFC-0342) is the general
   planning core, but MPlib presents the manipulation-specific library other
   stacks call. A URML target must be a well-posed request whether bare OMPL or
   MPlib issues it; documenting the seam at the manipulation library clarifies
   what the manifest must declare at that altitude.
2. **Have URML emit MPlib planner configuration directly.** Rejected. Choosing a
   planner, its time budget, and its parameters is a substrate-and-integrator
   concern below URML's altitude. URML declares the target and the capability that
   make a plan request well-posed; it does not tune the planner. The
   manipulation-planner-class hint queued above is the boundary URML would carry.
3. **Model the MPlib planning scene inside the URML manifest.** Rejected. The
   planning scene and the collision world are a Layer-0 and substrate concern.
   URML declares capability over the robot (reachable workspace, grippers, limits)
   and lets MPlib derive the planning group and scene. Modelling them in the
   manifest would fail the substrate-neutrality acid test.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the general planning core
  MPlib wraps; the Move #26 sampling-based-planner sibling.
- [RFC-0352 (TRAC-IK outreach)](0352-trac-ik-outreach.md): the Move #27 anchor; a
  global pose-to-configuration IK solver below a full planner.
- [RFC-0353 (Pink outreach)](0353-pink-outreach.md): the differential-IK sibling
  in this wave.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the manipulation
  integrator altitude that also drives a planner.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics and kinematics library in this lineage.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): a related
  model-and-simulation engagement in the manipulation neighborhood.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the manipulation surface a collision-free arm plan exercises.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the trajectory an MPlib plan produces.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the MPlib maintainers:

1. **Plan-call boundary.** Is "URML manipulation intent plus capability -> an
   MPlib planning call" the right seam, with URML producing a well-posed request
   and staying entirely above the planner, and MPlib owning the trajectory
   computation?
2. **Well-posed-request inputs.** What does URML need to declare so a plan request
   is well-posed: the planning group, the collision-world source, the goal pose
   convention? Which belong in the manifest versus being supplied by the
   integrator?
3. **Relationship to OMPL.** MPlib wraps OMPL, which URML engages separately
   (RFC-0342). Should the URML-to-MPlib seam stay at the MPlib library altitude,
   or is there a place where it should defer to the OMPL contract directly?
4. **Collision-world source.** URML expects the collision world to come from the
   perception and estimation layer. Is reading the world model from there the
   right alignment for MPlib's FCL check, or does MPlib expect the planning scene
   wired differently?
5. **Conformance listing.** Would MPlib consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0355 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`haosulab/MPlib`](https://github.com/haosulab/MPlib) pointing at this RFC. If the
maintainers prefer another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 266 stars, not archived, Issues enabled,
      last push 2026-05-17).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse target declaration, wraps OMPL).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (IK-target declaration, explicit
      joint limits, manipulation-planner-class hint) flagged as queued Spec RFCs,
      not proposed here.
- [x] Provenance: US (UC San Diego, Hao Su Lab); default policy passes at the
      planning layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; MPlib is one
      manipulation backend among many, URML declares the target and validates
      admissibility, composed above not assumed).
