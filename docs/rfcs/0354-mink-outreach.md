---
rfc: 0354
title: mink (MuJoCo differential inverse kinematics) integration, request for comment from the mink maintainers
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

# RFC-0354: mink integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`kevinzakka/mink`](https://github.com/kevinzakka/mink), a task-based
differential inverse-kinematics library for MuJoCo that solves each control step
as a quadratic program. It **requests review and feedback from the mink
maintainers**.

URML and mink sit at adjacent layers, and the seam between them is clean. URML's
manipulation primitives (`move_to` a pose, `grasp`, `release`) declare an intent
plus a target and the arm and gripper capability (`manipulation.grippers`,
`manipulation.reachable_workspace_m`). mink computes the joint velocities that
drive a frame task toward that target inside its QP. URML does not solve. It
declares the target and the capability, statically validates that the target lies
within the declared reachable workspace and within the active safety envelope
before mink runs, then consumes the resulting motion.

URML composes **above** mink: URML intent -> validated target plus capability ->
a mink task set and QP solve -> ros2_control
([RFC-0319](0319-ros2-control-outreach.md)) executes the result. mink is the
MuJoCo-native sibling of Pink ([RFC-0353](0353-pink-outreach.md), built on
Pinocchio). The differentiator is **static admissibility and envelope checking
before a single QP is assembled**: a target outside the declared reachable
workspace, or one the envelope forbids, is rejected before any solve effort is
spent.

## Motivation

mink is the MuJoCo-native expression of task-based differential IK, and aligning
URML's declared target-and-capability surface with a mink task set is a clean way
to make "validate before you solve" concrete:

1. **It is the MuJoCo-native differential-IK sibling of Pink.** URML engages Pink
   ([RFC-0353](0353-pink-outreach.md)) at the same task-based-QP altitude on the
   Pinocchio side. mink is the same idea on MuJoCo ([RFC-0060](0060-mujoco-integration.md)).
   Documenting the URML-to-mink seam directly clarifies what URML must declare so
   a frame task is well-posed regardless of which backend solves it.
2. **A URML target is a frame task, minus the solver.** A `move_to` to a named
   pose, with the manipulation reachable workspace and the envelope limits, is
   exactly the frame-task target and the bound set a mink configuration needs.
   URML supplies the well-posed target; mink supplies the joint velocities.
3. **Admissibility is cheap to check and expensive to discover late.** mink
   assembles and solves a QP every control step. URML's contribution sits one
   layer up and earlier: a static check, before the first solve, that the target
   lies within the declared reachable workspace and that the envelope admits the
   motion. An inadmissible target never reaches the QP.
4. **It grounds substrate-neutrality.** A URML target that maps onto a mink frame
   task must also map onto Pink, onto a global IK solver like TRAC-IK
   ([RFC-0352](0352-trac-ik-outreach.md)), and onto a full motion planner. mink is
   one manipulation backend among several in this wave; the same target
   declaration feeds them without changing the URML program.

Repo at [`kevinzakka/mink`](https://github.com/kevinzakka/mink) (about 1,370
stars, Issues enabled, not archived, last push 2026-05-15, active). Origin: Kevin
Zakka (United States); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mink_task_cell.yaml` fixture)

| URML field | Maps to mink input |
|---|---|
| `robot_id`, `description` | Solve identity (not a mink concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | The frame a `move_to` resolves against and the target pose fed to a mink frame task |
| `manipulation.arm_count` + joints | The configuration the mink solve drives (the joint DOF of the MuJoCo model) |
| `manipulation.reachable_workspace_m` | The workspace bound the target pose is checked against statically before a task is built |
| `manipulation.grippers[].kind` / `force_max_n` | The gripper DOF a `grasp` actuates; force bound checked statically before the command is issued |
| Safety envelope limits (Pass 3) | Conjoined with mink's configuration and velocity limits; URML applies strictest-wins before the solve |

### What URML v0.1 does not yet express for mink

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **IK-target / joint-configuration declaration.** URML declares a target pose
   and the reachable workspace, not an explicit IK target or the joint
   configuration a solve resolves to. A future Spec RFC could add an optional
   IK-target declaration so a frame task is well-posed directly from the manifest.
   Shared across this wave (anchored at RFC-0352).
2. **Explicit joint-limit declaration.** URML pushes hard limits through the
   safety envelope at a coarse altitude. A future Spec RFC could add explicit
   per-joint position and velocity limits so a mink configuration and velocity
   limit can be bounded directly from the manifest. Shared with ros2_control
   ([RFC-0319](0319-ros2-control-outreach.md)).
3. **Manipulation-planner-class hint.** URML's manifest does not declare which
   class of manipulation backend a deployment expects (differential IK versus
   global IK versus a full planner). A future Spec RFC could add an optional
   planner-class hint so the validator and tooling can reason about the
   manipulation contract explicitly.

### Compatibility notes

- **Vendor org.** [`kevinzakka`](https://github.com/kevinzakka) (Kevin Zakka,
  individual maintainer, robotics-research lineage).
- **Engagement repo.** [`kevinzakka/mink`](https://github.com/kevinzakka/mink):
  task-based differential inverse kinematics for MuJoCo, solved as a QP; active.
- **Origin / policy.** United States. Passes US-federal default policy
  (open-source library, no provenance gate at the IK layer).
- **License note.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring.
- **Substrate-neutrality.** mink is one manipulation backend among several, and it
  is MuJoCo-coupled ([RFC-0060](0060-mujoco-integration.md)); the same URML target
  and capability declaration feeds Pink (RFC-0353), TRAC-IK (RFC-0352), or a full
  planner with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The IK-target declaration, the explicit
  joint-limit declaration, and the manipulation-planner-class hint are queued Spec
  RFCs.
- Reference runtime: no change in this RFC. A mink mapping would translate a
  validated primitive's target and capability into a mink frame task and QP solve;
  the planned `mink_task_cell.yaml` fixture would document the target and bound
  set a well-posed task needs.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse target declaration today.** URML v0.1 declares a target pose and the
  reachable workspace, and routes hard limits through the envelope. A well-posed
  mink frame task wants an explicit IK target and joint and velocity bounds, which
  is exactly the gap queued above. The mapping is honest that the declaration is
  coarser than mink ideally consumes today.
- **MuJoCo coupling.** mink is built on MuJoCo, so the target declaration has to
  stay model-agnostic to keep the URML program portable. The mapping is described
  at the target and capability altitude so it does not bake in a MuJoCo model.

## Alternatives considered

1. **Engage only Pink and skip mink.** Rejected. Pink (RFC-0353) covers the
   Pinocchio side of task-based differential IK, but mink is the MuJoCo-native
   expression of the same contract. A URML target must map onto either backend;
   documenting the mink seam keeps the manifest honest for MuJoCo-based stacks.
2. **Have URML emit mink task weights and gains directly.** Rejected. Choosing
   task weights, gains, and solver parameters is a substrate-and-integrator
   concern below URML's altitude. URML declares the target and the capability that
   make a frame task well-posed; it does not tune the QP. The manipulation-
   planner-class hint queued above is the boundary URML would carry.
3. **Model the MuJoCo configuration inside the URML manifest.** Rejected. The
   MuJoCo model and its configuration space are a Layer-0 and substrate concern.
   URML declares capability over the robot (reachable workspace, grippers, limits)
   and lets mink derive the configuration. Modelling it in the manifest would fail
   the substrate-neutrality acid test.

## Prior art

- [RFC-0353 (Pink outreach)](0353-pink-outreach.md): the Pinocchio-based sibling
  of mink; the same task-based differential-IK contract on a different backend.
- [RFC-0352 (TRAC-IK outreach)](0352-trac-ik-outreach.md): the Move #27 anchor; a
  global pose-to-configuration IK solver, the contrast to differential IK.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): the simulator and
  model layer mink is built on.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics library underneath the Pinocchio-side differential-IK sibling.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the manipulation
  integrator altitude above the solver.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 planning sibling
  at the sampling-based-planner altitude.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the manipulation surface a frame-task solve exercises.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the motion a mink solve produces.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the mink maintainers:

1. **Task boundary.** Is "URML target plus capability -> a mink task set" the
   right seam, with URML producing a well-posed frame-task target and staying
   entirely above the solver, and mink owning the joint-velocity computation?
2. **Limit mapping.** How should URML's declared limits map to mink's
   configuration and velocity limits? Which belong in the manifest versus being
   supplied by the mink configuration directly?
3. **MuJoCo-model dependence.** mink is built on a MuJoCo model. Does that
   dependence affect how URML should declare the target (frame, pose convention)
   so the declaration stays model-agnostic and portable?
4. **Differential versus global IK.** mink solves differentially per step. Is
   there a useful place for URML to carry the differential-versus-global
   distinction (the manipulation-planner-class hint queued above), or is that
   better left to the integrator?
5. **Conformance listing.** Would mink consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0354 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`kevinzakka/mink`](https://github.com/kevinzakka/mink) pointing at this RFC. If
the maintainers prefer another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,370 stars, not archived, Issues
      enabled, last push 2026-05-15).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse target declaration, MuJoCo coupling).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (IK-target declaration, explicit
      joint limits, manipulation-planner-class hint) flagged as queued Spec RFCs,
      not proposed here.
- [x] Provenance: US (Kevin Zakka); default policy passes at the IK layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; mink is one
      manipulation backend among many, URML declares the target and validates
      admissibility, composed above not assumed).
