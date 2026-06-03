---
rfc: 0357
title: LEAP Hand (open dexterous hand) integration, request for comment from the LEAP Hand maintainers
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

# RFC-0357: LEAP Hand integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`leap-hand/LEAP_Hand_API`](https://github.com/leap-hand/LEAP_Hand_API), the API
for the LEAP Hand: a low-cost, open-source, anthropomorphic dexterous hand from
Carnegie Mellon University. It **requests review and feedback from the LEAP Hand
maintainers**.

The LEAP Hand is a 16-DoF dexterous hand, and this is exactly where URML's
gripper model is too coarse. URML's `manipulation.grippers` declares a single
force range plus a list of accepted object classes. That describes a parallel-jaw
gripper well; it does not describe a multi-fingered hand. This RFC is honest about
that: it is partly a request to understand what a dexterous-hand capability
declaration should contain.

URML composes **above** the LEAP Hand: URML `grasp` and `release` intent ->
validated gripper capability and object class -> the LEAP API executes the finger
commands -> `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)) or the
LEAP driver drives the joints. URML declares the hand as a single-force-range
gripper **today, as a deliberate lower-bound**, and the differentiator stays the
same: a static admissibility check before the grasp runs. The richer
dexterous-hand declaration is the key queued Spec RFC.

## Motivation

The LEAP Hand is a leading open dexterous hand, and a 16-DoF hand is the cleanest
case for showing where URML's gripper model needs to grow:

1. **It is honestly out of model.** URML's gripper declaration is a single
   `[force_min_n, force_max_n]` window and a class list. A 16-DoF anthropomorphic
   hand has per-finger force, named grasp types, and synergies the model cannot
   express. URML can declare the hand as a coarse lower-bound gripper today, and
   it should say so plainly rather than pretend the model fits.
2. **It surfaces the dexterous-hand declaration gap concretely.** Mapping the
   LEAP Hand is the forcing function for the queued Spec RFC: what a
   minimal-but-honest dexterous-hand capability declaration should contain. The
   mapping turns an abstract gap into a specific question to the people who built
   the hand.
3. **The intent / driver boundary stays clean.** Even with the coarse model,
   the seam holds: URML declares intent (`grasp` a target object class) and the
   admissible envelope, the LEAP API executes the finger-level commands. URML
   never issues per-joint commands itself.
4. **It keeps the stack substrate-neutral.** A `grasp` primitive that targets the
   LEAP Hand must also target a parallel-jaw gripper or another hand with no
   change to the program. The LEAP Hand is one gripper among many; execution
   still routes through MoveIt 2 ([RFC-0202](0202-moveit2-outreach.md)) and the
   joint-level driver.

Repo at [`leap-hand/LEAP_Hand_API`](https://github.com/leap-hand/LEAP_Hand_API)
(about 163 stars, Issues enabled, not archived, last push 2025-10-20). Origin:
Carnegie Mellon University (United States); open hardware.

## Detailed design

### URML v0.1 mapping (planned `leap_hand_cell.yaml` fixture)

| URML field or primitive | Maps to LEAP Hand attribute |
|---|---|
| `manipulation.grippers[].kind` | Declared `servo_electric` (lower-bound; a multi-fingered hand is coarser than the enum admits) |
| `manipulation.grippers[].force_min_n` / `force_max_n` | A conservative whole-hand closing-force window the requested `grasp` force is checked against |
| `manipulation.grippers[].accepted_classes` | The object classes the hand is declared to service; an out-of-set target is rejected before the grasp |
| `manipulation.grippers[].movable` | Whether the hand is on a movable arm or fixed; carried for the validator |
| `manipulation.arm_count` / `reachable_workspace_m` | The arm the hand is mounted on, if any, and its workspace |
| `perception.object_vocabulary` | The object classes `detect` may name as the `grasp` target |
| `grasp` / `release` (target object) | The intent the LEAP API turns into finger-level commands |
| LEAP per-finger joint commands | The driver-level execution URML stays above and never issues directly |
| Safety envelope limits (Pass 3) | Conjoined with the declared force window; URML applies strictest-wins before the grasp |

### What URML v0.1 does not yet express for the LEAP Hand

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Dexterous / multi-DoF gripper declaration.** This is the key gap. URML's
   gripper model is a single force range plus a class list, too coarse for a
   16-DoF hand. A future Spec RFC could add a dexterous-hand capability
   declaration carrying degrees of freedom, per-finger force, and a vocabulary of
   named grasp types or synergies, so a hand is declared honestly rather than as
   a lower-bound gripper.
2. **Named grasp-type vocabulary.** A dexterous hand grasps differently for a
   power grasp, a pinch, or a tripod. A future Spec RFC could let `grasp` name a
   grasp type from a small vocabulary, validated against the hand's declared
   repertoire, instead of leaving the grasp shape implicit.

### Compatibility notes

- **Vendor org.** [`leap-hand`](https://github.com/leap-hand) (Carnegie Mellon
  University; open hardware, open-source API).
- **Engagement repo.** [`leap-hand/LEAP_Hand_API`](https://github.com/leap-hand/LEAP_Hand_API):
  the control API for the LEAP Hand.
- **Origin / policy.** United States (Carnegie Mellon University). Passes
  US-federal default policy (open-source hardware API, no provenance gate at the
  hand-driver layer; URML composes above it and validates before motion).
- **License note.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring.
- **Substrate-neutrality.** The LEAP Hand is one gripper among many; the same
  `grasp` / `release` primitive targets a parallel-jaw gripper or another
  dexterous hand with no change to the program, and execution still routes
  through MoveIt 2 and the joint-level driver.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The dexterous / multi-DoF gripper
  declaration and the named grasp-type vocabulary are queued Spec RFCs.
- Reference runtime: no change in this RFC. A LEAP mapping would route a
  validated `grasp` / `release` intent to the LEAP API's finger commands; the
  planned `leap_hand_cell.yaml` fixture would document the honest lower-bound
  gripper declaration and prove the admissibility check hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lower-bound capability.** URML can only declare the LEAP Hand as a coarse
  single-force-range gripper today. That under-describes a 16-DoF hand, and the
  RFC says so plainly rather than over-promising; the richer declaration is
  queued, not present.
- **Model-shaped question.** Part of this RFC is a question, not a finished
  mapping: what a dexterous-hand declaration should contain. That is honest but it
  means the mapping table is a lower-bound sketch, not a settled contract.

## Alternatives considered

1. **Declare per-joint commands in the URML manifest.** Rejected. Per-finger
   joint control is a driver / substrate concern; URML declares intent and
   capability, not joint trajectories. Modeling joints would fail the
   substrate-neutrality acid test and duplicate the LEAP API.
2. **Force the 16-DoF hand into the parallel-jaw gripper model and say nothing.**
   Rejected. It would over-promise and hide the gap. The honest-substrate-limit
   norm ([RFC-0014](0014-substrate-conformance.md)) requires declaring the coarse
   lower-bound openly and queuing the richer model as a Spec RFC.
3. **Block the engagement until the dexterous-hand Spec RFC lands.** Rejected.
   The mapping is the forcing function for that Spec RFC; engaging the people who
   built the hand is how URML learns what the declaration should contain.

## Prior art

- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the manipulation spec surface the gripper capability lives under, and the
  closest home for a richer dexterous-hand model.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the motion-planning
  layer a validated grasp is executed through.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer the finger commands ultimately drive.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  surface the hand and its target object are resolved against.
- Sibling Move #27 RFCs: RFC-0352 (TRAC-IK, the inverse-kinematics anchor),
  RFC-0356 (GraspNet grasp-pose detection), and RFC-0358 (Shadow Robot dexterous
  hand, the closest sibling for the dexterous-hand model gap).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  `grasp` / `release` primitives and the gripper-capability surface this
  engagement exercises and stretches.

## Unresolved questions

For the LEAP Hand maintainers:

1. **Minimal dexterous-hand declaration.** What should a minimal-but-honest
   dexterous-hand capability declaration contain: degrees of freedom, per-finger
   force, a set of grasp primitives or synergies, anything else? This is the core
   question this RFC asks.
2. **Named grasp types vs per-joint commands.** Should URML model named grasp
   types (power, pinch, tripod) validated against the hand's repertoire, rather
   than per-joint commands, as the intent surface for a dexterous hand?
3. **Intent / API boundary.** Is "URML declares `grasp` / `release` intent and
   the admissible envelope, the LEAP API executes finger-level commands" the
   right boundary, with URML never issuing per-joint commands itself?
4. **Lower-bound declaration today.** Is declaring the hand as a coarse
   single-force-range gripper an acceptable honest lower-bound for a first
   mapping, until the dexterous-hand Spec RFC lands?
5. **Conformance listing.** Would the LEAP Hand project consider a project link
   to URML's compatible-runtimes registry
   ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0357 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`leap-hand/LEAP_Hand_API`](https://github.com/leap-hand/LEAP_Hand_API) pointing
at this RFC (the repo has Issues enabled). If the maintainers prefer another
channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 163 stars, not archived, Issues enabled,
      last push 2025-10-20).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lower-bound capability, model-shaped
      question).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs (the
      dexterous-hand declaration is the key one), not proposed here.
- [x] Provenance: US (Carnegie Mellon University); default policy passes at the
      hand-driver layer (URML composes above and validates before motion).
- [x] CLAUDE.md compliance check passed (substrate-neutral; the LEAP Hand is one
      gripper among many, the coarse declaration is declared honestly, the same
      primitive runs on a parallel-jaw gripper, composed-above not assumed).
