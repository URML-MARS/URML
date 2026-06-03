---
rfc: 0358
title: Shadow Robot (dexterous hand ROS interface) integration, request for comment from the Shadow Robot maintainers
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

# RFC-0358: Shadow Robot dexterous hand integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`shadow-robot/sr_interface`](https://github.com/shadow-robot/sr_interface), the
ROS interface for the Shadow Dexterous Hand, a 20+ actuated-degree-of-freedom
anthropomorphic hand from the Shadow Robot Company. It **requests review and
feedback from the Shadow Robot maintainers**.

URML's manipulation primitives (`grasp`, `release`, `move_to`) declare intent
plus a target and the gripper capability the action needs. The capability lives
in the manifest: `manipulation.grippers` carries `kind`, `force_min_n`,
`force_max_n`, and `accepted_classes`, alongside `arm_count` and
`reachable_workspace_m`. URML statically validates that the declared hand admits
the requested grasp before any motion, then `sr_interface` executes the hand.

URML composes **above** the hand driver: URML intent -> validated capability and
target -> the Shadow Hand driver in `sr_interface` -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes the joints. The
differentiator is static admissibility (force range, accepted classes,
reachability) checked before the hand moves. This RFC is honest up front: a
20-DoF dexterous hand is the richest case for the gap that
[RFC-0357 (LEAP Hand)](0357-leap-hand-outreach.md) already raises, and URML's
single-force-range gripper model is a lower-bound description of it today.

## Motivation

The Shadow Dexterous Hand is among the most capable open-source-driven
anthropomorphic hands in robotics, and it is exactly where URML's gripper model
meets its honest limit:

1. **It is the richest dexterous-hand case.** A 20+ DoF anthropomorphic hand has
   per-finger actuation, named grasp synergies, and tactile sensing. URML's
   `manipulation.grippers` block today describes a single force range and a set
   of accepted object classes. That is a faithful lower bound for a parallel-jaw
   gripper and a deliberate under-description for a Shadow Hand. The dexterous
   case forces the question of what a high-DoF hand capability declaration should
   contain.
2. **The intent and the execution split cleanly.** URML declares `grasp object`
   with a target and the capability the grasp needs; `sr_interface` owns the
   joint-level execution of the hand. URML stays above the driver. The acid test
   holds: the same `grasp` primitive drives a parallel-jaw gripper or a
   zero-ROS runtime, so the Shadow Hand is one more Layer-1 target at a richer
   altitude.
3. **Static admissibility is where URML adds value.** Before the hand moves,
   URML checks the declared force range, the accepted object classes, and the
   reachable workspace against the requested grasp. A program that asks for a
   grasp the declared hand cannot admit is rejected before `ros2_control` issues
   a command.
4. **It grounds the dexterous-hand gap with a real vendor stack.** LEAP Hand
   ([RFC-0357](0357-leap-hand-outreach.md)) raises the multi-DoF gripper
   question from the research-hardware side. Shadow raises it from a commercial
   open-source vendor's production ROS stack. Two independent dexterous hands
   asking for the same declaration shape is the evidence the gap is real and not
   hardware-specific.

Repo at [`shadow-robot/sr_interface`](https://github.com/shadow-robot/sr_interface)
(about 32 stars, Issues enabled, not archived, last push 2025-08-26). Origin:
Shadow Robot Company (United Kingdom, NATO-allied); passes US-federal default
policy. The stack is a commercial vendor's open ROS interface.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `shadow_hand_cell.yaml` fixture)

| URML field | Maps to Shadow Hand / sr_interface attribute |
|---|---|
| `robot_id`, `description` | The hand's identity in the manifest envelope (a left or right Shadow Dexterous Hand) |
| `frames`, `declared_locations` | The hand base frame and named target poses a `move_to` resolves against |
| `manipulation.arm_count` | The arm the hand is mounted on (the hand itself is the end effector) |
| `manipulation.reachable_workspace_m` | The reachable workspace of the arm carrying the hand, checked statically before a `move_to` |
| `manipulation.grippers[].kind` | The end effector kind (an anthropomorphic dexterous hand; a lower-bound enum value today) |
| `manipulation.grippers[].force_min_n` / `force_max_n` | A single aggregate force bound, checked before `grasp`; honestly under-describes per-finger actuation |
| `manipulation.grippers[].accepted_classes` | The object classes the declared grasp admits, conjoined with `perception.object_vocabulary` |
| `perception.object_vocabulary` | The object classes a `detect` may name as a `grasp` target |
| Safety envelope limits (Pass 3) | Conjoined with the hand and arm joint limits; URML applies strictest-wins before the driver acts |

### What URML v0.1 does not yet express for the Shadow Hand

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **A dexterous / multi-DoF gripper declaration.** The single force range and
   flat accepted-class list cannot describe per-finger force, joint coupling, or
   the actuated-DoF count of a 20+ DoF hand. A future Spec RFC could add an
   optional dexterous-gripper declaration (per-finger bounds, tactile presence)
   so a manifest can describe a Shadow Hand at its real altitude. This is the
   same gap LEAP Hand raises ([RFC-0357](0357-leap-hand-outreach.md)).
2. **Named grasp-type primitives.** URML expresses `grasp object`, not
   `power_grasp` or `pinch`. A future Spec RFC could add named grasp types or
   grasp synergies so intent can name the grasp class a dexterous hand should
   form, leaving the joint trajectory to the driver.

### Compatibility notes

- **Vendor org.** [`shadow-robot`](https://github.com/shadow-robot) (Shadow
  Robot Company, United Kingdom).
- **Engagement repo.** [`shadow-robot/sr_interface`](https://github.com/shadow-robot/sr_interface),
  the ROS interface for the Shadow Dexterous Hand.
- **Origin / policy.** United Kingdom (NATO-allied). Passes US-federal default
  policy (allied-origin open stack, no provenance gate at the hand-driver layer).
- **Relationship.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring. URML cites `sr_interface` as the execution surface
  for a declared dexterous-hand capability and does not bundle its code.
- **Substrate-neutrality.** The Shadow Hand is one dexterous-hand target; the
  same `grasp` and `release` primitives map onto LEAP Hand
  ([RFC-0357](0357-leap-hand-outreach.md)), a parallel-jaw gripper, or a
  zero-ROS runtime with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The dexterous-gripper declaration and
  named grasp-type primitives are queued Spec RFCs.
- Reference runtime: no change in this RFC. A Shadow mapping would route a
  validated `grasp` to the hand driver in `sr_interface`, which drives the joints
  through `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)); the planned
  `shadow_hand_cell.yaml` fixture would document the lower-bound dexterous-hand
  manifest honestly.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lower-bound capability.** A single force range honestly under-describes a 20+
  DoF hand. URML declares what it can today and names the dexterous-gripper gap
  as the open question rather than papering over it.
- **Open declaration question.** Whether URML should model grasp types or joint
  commands for a dexterous hand is genuinely unsettled. This RFC asks the
  question rather than presuming an answer.

## Alternatives considered

1. **Force the Shadow Hand into the parallel-jaw gripper model and stop there.**
   Rejected. It would silently mislabel a 20-DoF anthropomorphic hand as a simple
   gripper. The honest path declares the lower bound today and names the
   dexterous-gripper gap as a queued Spec RFC.
2. **Propose the dexterous-gripper declaration inside this RFC.** Rejected. A new
   manifest field is a normative spec change and belongs in a Spec RFC with its
   own review, not folded into an outreach thread. The gap is flagged, not
   proposed here.
3. **Map URML directly to hand joint commands.** Rejected. URML declares intent
   and capability, not joint trajectories. Joint-level control is the driver's
   concern in `sr_interface` over `ros2_control`; pushing joints into URML would
   fail the substrate-neutrality acid test.

## Prior art

- [RFC-0357 (LEAP Hand outreach)](0357-leap-hand-outreach.md): the sibling
  dexterous-hand engagement that first raises the multi-DoF gripper gap; the
  closest precedent.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the motion-planning
  engagement a `move_to` for the arm carrying the hand composes with.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the spec lineage for richer manipulation declarations.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that drives the hand joints below `sr_interface`.
- Sibling Move #27 RFCs: [RFC-0352 (TRAC-IK)](0352-trac-ik-outreach.md) (the
  manipulation-wave anchor), [RFC-0357 (LEAP Hand)](0357-leap-hand-outreach.md),
  and [RFC-0360 (robomimic)](0360-robomimic-outreach.md).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the Shadow Robot maintainers:

1. **Dexterous-hand capability declaration.** What should a capability
   declaration for a 20+ DoF Shadow Hand contain to be useful: per-finger force
   bounds, named grasp synergies, tactile-sensor presence, actuated-DoF count, or
   some smaller subset that still buys static admissibility?
2. **Grasp types vs joint commands.** Should URML model named grasp types (a
   power grasp, a pinch) at the intent level and leave the joint trajectory to
   `sr_interface`, or is there a different boundary the maintainers would prefer?
3. **Intent / driver boundary.** Is "URML declares the validated grasp intent and
   capability, `sr_interface` executes the hand" the right seam, with URML staying
   entirely above the driver?
4. **Tactile and force feedback.** The Shadow Hand has tactile sensing. Is there
   a useful place for that in a capability declaration URML validates against, or
   does it belong wholly below the intent layer?
5. **Conformance listing.** Would Shadow Robot consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0358 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`shadow-robot/sr_interface`](https://github.com/shadow-robot/sr_interface)
pointing at this RFC (the repo has Issues enabled). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 32 stars, not archived, Issues enabled,
      last push 2025-08-26).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lower-bound capability, open declaration
      question).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (dexterous-gripper declaration,
      named grasp types) flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: United Kingdom (NATO-allied); default policy passes at the
      hand-driver layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; the Shadow Hand is
      one dexterous-hand target, the same primitive runs on other hands and a
      zero-ROS runtime, composed-above not assumed).
