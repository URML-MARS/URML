---
rfc: 0374
title: K-Scale Labs (open humanoid stack: ksim + kos) integration, request for comment from the K-Scale maintainers
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

# RFC-0374: K-Scale Labs open humanoid stack integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robots wave, round two. This RFC
reaches K-Scale Labs, a US open humanoid startup building a fully open stack:
[`kscalelabs/ksim`](https://github.com/kscalelabs/ksim), a humanoid simulation
and reinforcement-learning training stack, and its sibling
[`kscalelabs/kos`](https://github.com/kscalelabs/kos), the K-Scale robot
operating system that runs onboard. This RFC anchors on ksim, folds kos into the
same thread, and **requests review and feedback from the K-Scale maintainers**.

K-Scale spans the whole arc URML cares about: a training stack in simulation and
an onboard runtime on the robot. URML composes **above** that stack. A validated
English sentence becomes a URML primitive (`move_to`, `grasp`, `release`); the
primitive carries an intent and a declared capability into the K-Scale runtime,
which owns the policy, the controllers, and the joints. The differentiator is
**static validation of the intent against the declared capability and the active
safety envelope before the runtime acts**.

This RFC is honest about altitude. URML describes a humanoid coarsely today. Its
mobility `drive_type` enum has no legged or bipedal class, and it has no
whole-body (legs plus arms) capability shape. The headline gap below is the
queued Spec RFC that would close that, tied to
[RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md).
It is not proposed here.

## Motivation

K-Scale is a clean open target that spans simulation-training to on-robot, which
is exactly the seam where a validated-intent layer earns its place:

1. **It is fully open, sim to robot.** ksim trains policies in simulation; kos
   runs them onboard. URML's whole reason to exist is to sit above a runtime like
   kos and decide, before the robot moves, whether the declared capability and
   the safety envelope admit the requested intent. An open stack is the place to
   show that honestly.
2. **Its robot definition is what URML's manifest declares over.** A K-Scale
   humanoid has a defined joint set, an actuator map, and limits. URML's Layer-1
   capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares the
   same surface at a coarser altitude. The two describe the same robot from two
   sides.
3. **It surfaces the legged-mobility gap precisely.** A humanoid is the body URML
   describes worst today. Engaging an open humanoid stack is the right place to
   ask what a legged-mobility class and a whole-body declaration should look like.
4. **It grounds substrate-neutrality.** A primitive that maps onto a K-Scale
   robot through kos must also map onto a ROS 2 humanoid, a different runtime, or
   real hardware with no ROS dependency. K-Scale is one Layer-1 target among many.

ksim repo at [`kscalelabs/ksim`](https://github.com/kscalelabs/ksim) (about 225
stars, Issues enabled, not archived, active, last push 2025-10-29). Sibling kos
repo at [`kscalelabs/kos`](https://github.com/kscalelabs/kos) (about 73 stars,
same org). Origin: K-Scale Labs (United States); passes US-federal default policy
(open-source framework, no provenance gate at this layer).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `kscale_humanoid_cell.yaml` fixture)

| URML field | Maps to K-Scale attribute |
|---|---|
| `robot_id`, `description` | The K-Scale robot's identity, carried at the manifest envelope |
| `frames`, `declared_locations` | The robot's base and named target poses a `move_to` resolves against |
| `mobility.drive_type` | The legged base, declared coarsely today (no legged class exists yet; see gap below) |
| `mobility.max_velocity` / `max_payload` | The robot's commanded base velocity bound and carry limit, conjoined with the envelope |
| `manipulation.arm_count` + `grippers` | The arm and end-effector DOF the K-Scale robot definition exposes |
| `manipulation.reachable_workspace_m` | The arm reach the robot definition implies, checked statically before a `grasp` |
| `programs` | Substrate-declared K-Scale behaviors a URML program may invoke by name |
| Primitives `move_to` / `grasp` / `release` | Intent goals handed to the kos runtime, which owns the policy and the joints |
| Safety envelope limits (Pass 3) | Conjoined with the robot's joint and velocity limits; URML applies strictest-wins before kos acts |

### What URML v0.1 does not yet express for a K-Scale humanoid

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed here.**

1. **Legged-mobility class and whole-body capability shape (headline gap).**
   URML's `mobility.drive_type` enum lists wheeled, tracked, aerial, and
   underwater classes, but no legged or bipedal class, and there is no shape that
   declares a coordinated whole-body (legs plus arms) capability. A future Spec
   RFC, tied to
   [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md),
   would add a legged-mobility class and a whole-body declaration so URML can
   describe a humanoid honestly instead of coarsely. **Not proposed here.**
2. **Balance and stability limits.** A bipedal humanoid has balance and
   stability constraints with no manifest expression today. A future Spec RFC
   could add an optional balance-limit block the validator conjoins with the
   envelope.

### Compatibility notes

- **Vendor org.** [`kscalelabs`](https://github.com/kscalelabs) (K-Scale Labs,
  United States), an open humanoid startup.
- **Engagement repo.** [`kscalelabs/ksim`](https://github.com/kscalelabs/ksim),
  the humanoid simulation and reinforcement-learning training stack (the anchor).
- **Sibling repo (folded into this thread).**
  [`kscalelabs/kos`](https://github.com/kscalelabs/kos), the K-Scale robot
  operating system that runs onboard. Which repo is the right integration surface
  is an open question below.
- **Origin / policy.** United States (K-Scale Labs). Passes US-federal default
  policy (open-source framework, no provenance gate at this layer).
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** A K-Scale humanoid is one Layer-1 target; the same
  primitives map onto a ROS 2 humanoid (ros2_control,
  [RFC-0319](0319-ros2-control-outreach.md)) or other hardware unchanged.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility class plus
  whole-body declaration and the balance-limit block are queued Spec RFCs.
- Reference runtime: no change in this RFC. A K-Scale mapping would route a
  validated primitive's goal to the kos runtime; the planned
  `kscale_humanoid_cell.yaml` fixture would document the coarse humanoid manifest
  honestly, naming the legged-class gap rather than papering over it.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse humanoid fit today.** URML describes a humanoid coarsely until the
  legged-mobility and whole-body Spec RFC lands. This RFC is honest that the
  current manifest is a lower bound on what a K-Scale humanoid can do.
- **Two-repo ambiguity.** ksim (training) and kos (runtime) split the surface.
  Anchoring on ksim and folding kos into one thread risks under-serving whichever
  the maintainers consider the real integration point; question 3 asks them to
  settle it.

## Alternatives considered

1. **Anchor on kos instead of ksim.** Rejected as the default anchor. kos is the
   onboard runtime URML would compose above, but it is the smaller, more
   operational surface; ksim is the more active research-facing repo and the
   natural first contact. kos is named and folded in, and the anchor moves if the
   maintainers say the runtime is the right surface.
2. **Wait for the legged-mobility Spec RFC before engaging.** Rejected. The gap
   is best characterized with input from people building an open humanoid stack.
   Engaging first and queuing the Spec RFC openly is more honest than designing
   the class in isolation.
3. **Model the K-Scale policy or training loop in the URML manifest.** Rejected.
   The policy and the training loop are Layer 0 / substrate concerns; URML
   declares capability over the robot, not the controller. Modelling them would
   fail the substrate-neutrality acid test.

## Prior art

- [RFC-0069 (Berkeley Humanoid Lite outreach)](0069-berkeley-humanoid-lite-outreach.md):
  the closest precedent, an open humanoid engagement that surfaced the same
  legged-mobility gap.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  controller-boundary engagement a ROS-based humanoid runtime would sit on.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md):
  related humanoid simulation and training engagement.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline whole-body gap is tied to.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0373 (Open
  Duck Mini), RFC-0375 (PAL Robotics TALOS), RFC-0376 (legged_gym).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the K-Scale maintainers:

1. **Where URML intent enters.** Is "URML intent -> validated primitive -> kos
   runtime" the right boundary, with URML staying entirely above kos and kos
   owning the policy, the controllers, and the joints?
2. **Capability-manifest alignment.** A K-Scale robot has a defined joint and
   actuator map. Is matching URML's capability manifest against that definition
   the right alignment, or is there a richer K-Scale robot definition URML should
   read instead?
3. **ksim vs kos as the integration surface.** Which repo is the right one: ksim
   for the simulated and trained body, or kos for the onboard runtime URML would
   compose above? Should the engagement stay one thread or fork?
4. **Legged-mobility and whole-body shape.** From your vantage building an open
   humanoid, what should a legged-mobility class and a whole-body (legs plus arms)
   capability declaration express so URML stops describing a humanoid coarsely?
5. **Conformance listing.** Would K-Scale consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0374 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).
The kos row in the ledger shares this RFC; a dedicated row is added only if the
engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`kscalelabs/ksim`](https://github.com/kscalelabs/ksim) pointing at this RFC. If
the maintainers prefer kos or another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (ksim about 225 stars, Issues enabled, not
      archived, active, last push 2025-10-29; kos about 73 stars, same org, named
      and folded in).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse humanoid fit, two-repo ambiguity).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs
      (legged-mobility class plus whole-body, tied to RFC-0010), not proposed here.
- [x] Provenance: US (K-Scale Labs); default policy passes at this layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; K-Scale is one
      humanoid target among many, honest coarse manifest declared, composed-above
      not assumed).
