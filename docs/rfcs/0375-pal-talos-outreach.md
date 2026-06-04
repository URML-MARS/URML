---
rfc: 0375
title: PAL Robotics TALOS (full-size humanoid) integration, request for comment from the PAL Robotics maintainers
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

# RFC-0375: PAL Robotics TALOS integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robots wave, round two. This RFC
reaches PAL Robotics TALOS, a full-size torque-controlled humanoid with an open
ROS stack at [`pal-robotics/talos_robot`](https://github.com/pal-robotics/talos_robot).
It **requests review and feedback from the PAL Robotics maintainers**.

TALOS is the OEM counterpart to the hobby and research bipeds in this wave: a
commercial full-size humanoid whose ROS packages are public. URML composes
**above** that stack. A validated English sentence becomes a URML primitive
(`move_to`, `grasp`, `release`); the primitive carries an intent and a declared
capability into TALOS's ROS controllers (ros2_control,
[RFC-0319](0319-ros2-control-outreach.md)), which own the whole-body control and
the joints. The differentiator is **static validation of the intent against the
declared capability and the active safety envelope before TALOS moves**.

This RFC is honest about altitude. URML describes a humanoid coarsely today. Its
mobility `drive_type` enum has no legged or bipedal class, and it has no
whole-body (legs plus arms) capability shape. The headline gap below is the
queued Spec RFC that would close that, tied to
[RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md).
It is not proposed here.

PAL's TIAGo, a wheeled mobile manipulator, was engaged earlier as
[RFC-0068](0068-pal-robotics-outreach.md). TALOS is the legged humanoid sibling
and surfaces the same legged-mobility gap at OEM scale.

## Motivation

TALOS is a full-size commercial humanoid with an open ROS stack, which makes it
the OEM-scale place to test URML's humanoid story:

1. **It is a commercial humanoid with an open stack.** TALOS ships real ROS
   packages. URML's reason to exist is to sit above that stack and decide, before
   the robot moves, whether the declared capability and the safety envelope admit
   the requested intent. An OEM with an open stack is the place to show that at
   production scale.
2. **Its robot description is what URML's manifest declares over.** TALOS has a
   defined joint set, torque-controlled actuators, and limits in its ROS
   description. URML's Layer-1 capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares the
   same surface at a coarser altitude. The two describe the same robot from two
   sides.
3. **It surfaces the legged-mobility gap at OEM scale.** TALOS is a full-size
   biped. URML describes a humanoid worst today. Engaging a commercial humanoid
   OEM is the right place to ask what a legged-mobility class and a whole-body
   declaration should express for a real torque-controlled platform.
4. **It extends an existing PAL engagement.** TIAGo (RFC-0068) is a wheeled
   mobile manipulator already engaged. TALOS asks whether the same
   mobile-manipulator declaration shape extends to a legged humanoid, or whether
   the legged body needs a different one.

Repo at [`pal-robotics/talos_robot`](https://github.com/pal-robotics/talos_robot)
(about 25 stars, Issues enabled, not archived, active, last push 2026-02-20).
Origin: PAL Robotics (Barcelona, Spain, NATO-allied), a commercial humanoid OEM
with an open ROS stack; passes US-federal default policy (allied origin,
open-source stack, no provenance gate at this layer).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `talos_humanoid_cell.yaml` fixture)

| URML field | Maps to TALOS attribute |
|---|---|
| `robot_id`, `description` | The TALOS robot's identity, carried at the manifest envelope |
| `frames`, `declared_locations` | TALOS base and named target poses a `move_to` resolves against |
| `mobility.drive_type` | The bipedal legged base, declared coarsely today (no legged class exists yet; see gap below) |
| `mobility.max_velocity` / `max_payload` | TALOS commanded base velocity bound and carry limit, conjoined with the envelope |
| `manipulation.arm_count` + `grippers` | TALOS dual arms and end-effectors, as declared in its ROS description |
| `manipulation.reachable_workspace_m` | TALOS arm reach, checked statically before a `grasp` |
| `programs` | Substrate-declared TALOS behaviors a URML program may invoke by name |
| Primitives `move_to` / `grasp` / `release` | Intent goals handed to TALOS ROS controllers (ros2_control), which own whole-body control and the joints |
| Safety envelope limits (Pass 3) | Conjoined with TALOS joint, torque, and velocity limits; URML applies strictest-wins before TALOS moves |

### What URML v0.1 does not yet express for TALOS

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed here.**

1. **Legged-mobility class and whole-body capability shape (headline gap).**
   URML's `mobility.drive_type` enum lists wheeled, tracked, aerial, and
   underwater classes, but no legged or bipedal class, and there is no shape that
   declares a coordinated whole-body (legs plus arms) capability. A future Spec
   RFC, tied to
   [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md),
   would add a legged-mobility class and a whole-body declaration so URML can
   describe a full-size torque-controlled humanoid honestly. **Not proposed here.**
2. **Balance and torque limits.** A full-size torque-controlled biped has
   balance, stability, and per-joint torque constraints with no manifest
   expression today. A future Spec RFC could add an optional balance-and-torque
   limit block the validator conjoins with the envelope.

### Compatibility notes

- **Vendor org.** [`pal-robotics`](https://github.com/pal-robotics) (PAL
  Robotics, Barcelona, Spain), a commercial humanoid OEM.
- **Engagement repo.**
  [`pal-robotics/talos_robot`](https://github.com/pal-robotics/talos_robot), the
  ROS packages for the TALOS full-size torque-controlled humanoid.
- **Origin / policy.** Spain (NATO-allied). Passes US-federal default policy
  (allied origin, open-source stack, no provenance gate at this layer).
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** TALOS is one Layer-1 humanoid target; URML composes
  above its ROS controllers (ros2_control,
  [RFC-0319](0319-ros2-control-outreach.md)) and the same primitives map onto a
  non-ROS humanoid runtime unchanged.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility class plus
  whole-body declaration and the balance-and-torque limit block are queued Spec
  RFCs.
- Reference runtime: no change in this RFC. A TALOS mapping would route a
  validated primitive's goal to TALOS ROS controllers; the planned
  `talos_humanoid_cell.yaml` fixture would document the coarse humanoid manifest
  honestly, naming the legged-class gap rather than papering over it.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse humanoid fit today.** URML describes a humanoid coarsely until the
  legged-mobility and whole-body Spec RFC lands. This RFC is honest that the
  current manifest is a lower bound on what TALOS can do.
- **Boundary-drawing burden.** TALOS has a sophisticated whole-body controller.
  Drawing the line between URML's validated intent and PAL's controller cleanly
  is the work, and it is real; question 2 asks the maintainers to help place it.

## Alternatives considered

1. **Engage TALOS through the existing TIAGo thread (RFC-0068).** Rejected. TIAGo
   is a wheeled mobile manipulator and TALOS is a legged humanoid; they surface
   different gaps. Folding them into one thread would blur the legged-mobility
   question this RFC exists to raise. The TIAGo precedent is cited, not merged.
2. **Wait for the legged-mobility Spec RFC before engaging.** Rejected. A
   full-size commercial humanoid OEM is exactly the vantage that should inform the
   legged-mobility class. Engaging first and queuing the Spec RFC openly is more
   honest than designing the class in isolation.
3. **Model TALOS's whole-body controller in the URML manifest.** Rejected. The
   controller is a Layer 0 / substrate concern; URML declares capability over the
   robot, not the controller. Modelling it would fail the substrate-neutrality
   acid test.

## Prior art

- [RFC-0068 (PAL Robotics outreach)](0068-pal-robotics-outreach.md): the earlier
  PAL engagement on TIAGo, a wheeled mobile manipulator; TALOS is the legged
  sibling.
- [RFC-0069 (Berkeley Humanoid Lite outreach)](0069-berkeley-humanoid-lite-outreach.md):
  an open humanoid engagement that surfaced the same legged-mobility gap.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  controller-boundary engagement TALOS's ROS stack sits on.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md):
  related humanoid simulation and training engagement.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline whole-body gap is tied to.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0373 (Open
  Duck Mini), RFC-0374 (K-Scale Labs), RFC-0376 (legged_gym).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the PAL Robotics maintainers:

1. **Manifest declaration for a full-size humanoid.** How should a URML manifest
   declare a full-size torque-controlled humanoid: a legged-mobility class, a
   whole-body (legs plus arms) shape, and balance and torque limits the validator
   can conjoin with the envelope?
2. **Boundary vs the whole-body controller.** Where is the right seam between
   URML's validated intent and PAL's whole-body controller, so URML stays above
   the stack and TALOS's controller owns balance and joint coordination?
3. **TIAGo declaration extending to TALOS.** Does the TIAGo-style
   mobile-manipulator declaration (RFC-0068) extend to TALOS, or does the legged
   humanoid body need a distinct declaration shape?
4. **ros2_control boundary.** Is "URML primitive -> validated goal -> TALOS
   ros2_control controllers" ([RFC-0319](0319-ros2-control-outreach.md)) the
   right control seam for a torque-controlled humanoid?
5. **Conformance listing.** Would PAL Robotics consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0375 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`pal-robotics/talos_robot`](https://github.com/pal-robotics/talos_robot)
pointing at this RFC. If the maintainers prefer another channel, URML will move
the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (talos_robot about 25 stars, Issues enabled,
      not archived, active, last push 2026-02-20).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse humanoid fit, boundary-drawing
      burden).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs
      (legged-mobility class plus whole-body, tied to RFC-0010), not proposed here.
- [x] Provenance: Spain (NATO-allied); default policy passes at this layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; TALOS is one humanoid
      target among many, honest coarse manifest declared, composed-above not
      assumed).
