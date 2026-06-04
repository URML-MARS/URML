---
rfc: 0372
title: ToddlerBot (open-source low-cost humanoid) integration, request for comment from the ToddlerBot maintainers
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

# RFC-0372: ToddlerBot integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's platform, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's second wave into open humanoid and legged robots. This RFC is
the wave anchor. It reaches [`hshi74/toddlerbot`](https://github.com/hshi74/toddlerbot),
an open-source, low-cost, 3D-printable bipedal humanoid with a full sim-to-real
learning stack. It **requests review and feedback from the ToddlerBot
maintainers**.

ToddlerBot is exactly the accessible open humanoid URML wants to describe: an
English sentence becomes a typed intent, the intent is validated against a
declared platform capability, and the validated intent drives the platform.
URML's `move_to`, `grasp`, `release`, `scan`, and `report` map onto the
intent-level commands a humanoid accepts, and URML composes **above** the
platform: validated intent -> ToddlerBot's locomotion and policy stack ->
joints.

This RFC is honest about altitude up front. URML can only describe ToddlerBot
coarsely today. A biped with arms is neither a `manipulator_base` nor any wheeled
class in URML's `mobility.drive_type` enum, and URML has no whole-body capability
shape. So this engagement is partly a design conversation: the headline gap is a
queued Spec RFC for a legged-mobility class and a whole-body capability
declaration, **not proposed here**.

## Motivation

ToddlerBot is the clearest motivation in the whole wave for the legged-mobility
gap. It is a real, buildable, low-cost biped with arms, and it is exactly the
robot URML should be able to declare and command honestly:

1. **It is the accessible open humanoid URML aims at.** The headline URML path is
   one English sentence moving a robot, reproducible by a developer. A low-cost,
   3D-printable biped is the most reachable hardware for that loop: validated
   intent -> declared capability -> ToddlerBot's stack -> motion.
2. **It exposes the legged-mobility gap directly.** URML's `mobility.drive_type`
   enum is `{ differential, omnidirectional, ackermann, tracked, multirotor,
   fixed_wing, vtol, manipulator_base, underwater_thrusters }`. A bipedal humanoid
   fits none of these. There is no legged class and no whole-body (legs plus arms)
   capability shape. ToddlerBot is the platform that makes the gap concrete rather
   than theoretical.
3. **It separates intent from policy cleanly.** ToddlerBot has a sim-to-real
   learning stack that realizes locomotion and manipulation. URML's contribution
   sits above and earlier: a static check that the declared capability and the
   safety envelope admit the requested intent, before the policy stack runs. The
   policy is the substrate; URML is the validated intent over it.
4. **It grounds substrate-neutrality.** A `move_to` that maps onto a ToddlerBot
   navigation goal must also map onto a wheeled base or a quadruped. Engaging an
   open biped is the evidence that the abstraction is not shaped by one body plan
   by accident.

Repo at [`hshi74/toddlerbot`](https://github.com/hshi74/toddlerbot) (about 692
stars, Issues enabled, not archived, active, last push 2026-04-19). Origin:
Stanford (United States), open hardware.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `toddlerbot_cell.yaml` fixture)

| URML field | Maps to ToddlerBot attribute |
|---|---|
| `robot_id`, `description` | The platform's identity, carried at the manifest envelope |
| `frames`, `declared_locations` | The robot's base frame and named target poses a `move_to` resolves against |
| `mobility.drive_type` | **No honest fit today.** A biped is not `manipulator_base` or any wheeled class; declared coarsely pending the queued legged-mobility class |
| `mobility.max_velocity` | The walk controller's commanded forward / turn velocity bound, conjoined with the envelope |
| `mobility.max_payload` | The platform's rated carry mass, if declared |
| `manipulation.arm_count` | ToddlerBot's arm count |
| `manipulation.grippers[].kind` / `force_max_n` | The hand / gripper DOF and its force bound, checked statically before a `grasp` |
| `manipulation.reachable_workspace_m` | The arms' reachable workspace, coarsely bounded |
| `perception.cameras[]` / `sensors[]` | The head camera and onboard sensors a `scan` reads from |
| Safety envelope limits (Pass 3) | Conjoined with joint, velocity, and balance limits; URML applies strictest-wins before motion |

### What URML v0.1 does not yet express for ToddlerBot

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Legged-mobility class and whole-body capability shape.** The headline gap.
   URML's `drive_type` enum has no legged / bipedal / quadruped class, and no way
   to declare a whole-body platform whose legs and arms share kinematics and a
   balance constraint. A future Spec RFC, tied to
   [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md),
   would add a legged-mobility class and a whole-body capability declaration so a
   biped with arms can be described honestly rather than coarsely. **Not proposed
   here.**
2. **Balance / stability constraint surface.** A standing biped has a balance
   constraint that a wheeled base does not. URML's safety envelope has no shape for
   declaring a stability margin a validated intent must respect. A future Spec RFC
   could add one so the validator can reason about tipping bounds. **Not proposed
   here.**

### Compatibility notes

- **Vendor org.** [`hshi74`](https://github.com/hshi74) and the ToddlerBot
  community (Stanford-origin open hardware).
- **Engagement repo.** [`hshi74/toddlerbot`](https://github.com/hshi74/toddlerbot):
  a low-cost, 3D-printable bipedal humanoid with a sim-to-real learning stack.
- **Origin / policy.** United States (Stanford). Passes US-federal default policy
  (open-source platform, no provenance gate at the platform layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** ToddlerBot is one legged platform among many; the same
  URML primitives map onto a wheeled base, a quadruped, or another biped with no
  change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility class, the
  whole-body capability shape, and the balance-constraint surface are queued Spec
  RFCs.
- Reference runtime: no change. A ToddlerBot mapping would route a validated
  intent's navigation or manipulation goal to the platform's locomotion and policy
  stack; the planned `toddlerbot_cell.yaml` fixture would document the coarse
  manifest honestly, declaring the legged-mobility gap rather than papering over
  it.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse description today.** URML cannot declare a bipedal humanoid honestly
  yet. The mapping is explicit that `drive_type` has no legged fit and that the
  whole-body shape is missing. This is the honest altitude, but it does narrow what
  URML can usefully express for ToddlerBot until the queued Spec RFC lands.
- **Policy-boundary uncertainty.** Where a URML intent ends and ToddlerBot's
  learned policy begins is exactly the seam this RFC asks the maintainers to help
  draw; documented wrong, it would over-claim.

## Alternatives considered

1. **Force a biped into `manipulator_base` or a wheeled class.** Rejected. It
   would be dishonest. A bipedal humanoid is neither a fixed manipulator base nor a
   wheeled platform, and pretending otherwise would mislead the validator and the
   reader. The honest move is to declare the gap and queue the Spec RFC.
2. **Propose the legged-mobility class inside this RFC.** Rejected. Adding to
   URML's normative surface is a Spec RFC tied to
   [RFC-0010](0010-whole-body-bimanual-manipulation.md), with its own review. An
   Outreach RFC requests comment; it does not expand the spec quietly.
3. **Model ToddlerBot's full joint tree in the manifest.** Rejected. Per-joint
   kinematics are a substrate concern owned by the platform's stack. URML declares
   capability at intent altitude; modelling the joint tree would fail the
   substrate-neutrality acid test.

## Prior art

- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline legged-mobility / whole-body gap is tied to.
- [RFC-0069 (Berkeley Humanoid Lite outreach)](0069-berkeley-humanoid-lite-outreach.md):
  the prior open-humanoid engagement, the closest precedent for the same gap.
- [RFC-0075 (Stanford Pupper outreach)](0075-stanford-pupper-outreach.md): a prior
  open-legged-platform engagement (quadruped) that hit the same enum limit.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  joint-level control layer below an intent, relevant to the intent / policy seam.
- Sibling Move #29 RFCs: RFC-0373 (Open Duck Mini), RFC-0374 (K-Scale),
  RFC-0375 (PAL TALOS), RFC-0376 (legged_gym).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the ToddlerBot maintainers:

1. **Minimal honest bipedal-humanoid declaration.** What does a minimal but honest
   capability declaration for a bipedal humanoid need: a legged-mobility class,
   whole-body kinematics linking legs and arms, a balance constraint, or more? What
   would you not want URML to over-claim?
2. **Intent / policy boundary.** Where should a URML intent end and ToddlerBot's
   learned policy stack begin? Is "validated navigation or manipulation goal ->
   ToddlerBot policy" the right seam, with URML staying entirely above the
   controller?
3. **How a maintainer wants intent expressed.** For a low-cost humanoid, is
   navigation-level intent (go to X, turn) plus coarse manipulation (`grasp`,
   `release`) the right granularity, or would you want intent expressed differently?
4. **Sensing surface.** Is matching URML's `perception` block against the head
   camera and onboard sensors the right alignment for `scan` and `report`?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0372 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`hshi74/toddlerbot`](https://github.com/hshi74/toddlerbot) pointing at this RFC.
If the maintainers prefer another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 692 stars, not archived, Issues enabled,
      active, last push 2026-04-19).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse description today, policy-boundary
      uncertainty).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the legged-mobility class and whole-body shape
      are flagged as queued Spec RFCs tied to RFC-0010, not proposed here.
- [x] Provenance: US (Stanford); default policy passes at the platform layer.
- [x] No license question asked; compatibility note states composition not
      vendoring without asserting an SPDX id.
- [x] CLAUDE.md compliance check passed (substrate-neutral; ToddlerBot is one
      legged platform among many, composed-above not assumed, gap declared
      honestly).
