---
rfc: 0373
title: Open Duck Mini (open bipedal robot) integration, request for comment from the Open Duck Mini maintainers
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

# RFC-0373: Open Duck Mini integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's platform, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's second wave into open humanoid and legged robots. This RFC
reaches [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini),
an open-source miniature BDX-style bipedal robot with a learned walk policy and a
full build. It **requests review and feedback from the Open Duck Mini
maintainers**.

Open Duck Mini is a small open biped whose locomotion is a reinforcement-learning
walk controller. URML's fit is to declare the platform's capability and bound a
navigation-level intent over it, while the learned walk policy is the substrate
that realizes stepping. URML composes **above** the platform: validated intent
(go to X, turn) -> the RL walk policy -> joints. URML's `move_to`, `scan`, and
`report` map onto that intent-level surface.

This RFC is honest about altitude. URML can only describe Open Duck Mini coarsely
today. A small biped fits none of the classes in URML's `mobility.drive_type`
enum, and URML has no whole-body capability shape. This is the same
legged-mobility gap surfaced by the wave anchor,
[RFC-0372 (ToddlerBot)](0372-toddlerbot-outreach.md). The headline gap is a queued
Spec RFC for a legged-mobility class and a whole-body capability declaration,
**not proposed here**.

## Motivation

Open Duck Mini sharpens one nuance the wave anchor raises: its locomotion is a
learned policy, which is the cleanest case for the learned-policy-as-substrate
framing:

1. **Learned locomotion is a clean substrate boundary.** The RL walk policy turns
   a navigation-level command into stepping. That is exactly the seam URML wants:
   URML declares capability and validates intent, the policy realizes it. The
   policy is the substrate; URML is the validated intent above it. A small biped
   with a learned controller makes that boundary easy to reason about.
2. **It exposes the legged-mobility gap directly.** URML's `mobility.drive_type`
   enum is `{ differential, omnidirectional, ackermann, tracked, multirotor,
   fixed_wing, vtol, manipulator_base, underwater_thrusters }`. A bipedal robot
   fits none of these. There is no legged class and no whole-body capability shape.
   Open Duck Mini hits the same gap as ToddlerBot from the locomotion side.
3. **It tests intent granularity.** For a biped whose walk is learned, the right
   question is whether URML should bound a navigation-level intent (go to X, turn)
   or descend toward gait-level commands. The navigation altitude keeps URML above
   the policy and substrate-neutral; the gait altitude would couple URML to one
   controller. This RFC asks the maintainers to confirm the altitude.
4. **It grounds substrate-neutrality.** A `move_to` that resolves to an Open Duck
   Mini navigation goal must also resolve on a wheeled base or another biped.
   Engaging a learned-walk biped is evidence the abstraction is not shaped by one
   controller by accident.

Repo at [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini)
(about 3,046 stars, Issues enabled, not archived, active, last push 2026-01-31).
Origin: Antoine Pirrone and community (France-lineage, NATO-allied).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `open_duck_mini_cell.yaml` fixture)

| URML field | Maps to Open Duck Mini attribute |
|---|---|
| `robot_id`, `description` | The platform's identity, carried at the manifest envelope |
| `frames`, `declared_locations` | The robot's base frame and named target poses a `move_to` resolves against |
| `mobility.drive_type` | **No honest fit today.** A biped is not any wheeled class; declared coarsely pending the queued legged-mobility class |
| `mobility.max_velocity` | The walk policy's commanded forward / turn velocity bound, conjoined with the envelope |
| `mobility.max_payload` | The platform's rated carry mass, if declared |
| `manipulation.arm_count` | Zero or coarse, if the platform carries no manipulators |
| `manipulation.grippers[]` / `reachable_workspace_m` | Declared only if the build adds a manipulator; otherwise empty |
| `perception.cameras[]` / `sensors[]` | The onboard camera and sensors a `scan` reads from |
| Safety envelope limits (Pass 3) | Conjoined with velocity and balance limits; URML applies strictest-wins before motion |

### What URML v0.1 does not yet express for Open Duck Mini

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Legged-mobility class and whole-body capability shape.** The headline gap,
   shared with [RFC-0372 (ToddlerBot)](0372-toddlerbot-outreach.md). URML's
   `drive_type` enum has no legged / bipedal / quadruped class, and no whole-body
   shape for a platform whose legs (and any arms) share kinematics and a balance
   constraint. A future Spec RFC, tied to
   [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md),
   would add a legged-mobility class and a whole-body capability declaration. **Not
   proposed here.**
2. **Learned-policy substrate marker.** A platform whose locomotion is a learned
   policy is a distinct substrate kind from a classical controller. URML's manifest
   has no marker for declaring that the intent is realized by a learned policy. A
   future Spec RFC could add an optional marker so tooling can reason about the
   policy boundary explicitly. **Not proposed here.**

### Compatibility notes

- **Vendor org.** [`apirrone`](https://github.com/apirrone) (Antoine Pirrone) and
  the Open Duck Mini community.
- **Engagement repo.** [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini):
  a miniature BDX-style open bipedal robot with an RL walk policy and a full build.
- **Origin / policy.** France-lineage, NATO-allied. Passes US-federal default
  policy (open-source platform, no provenance gate at the platform layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** Open Duck Mini is one legged platform among many; the
  same URML primitives map onto a wheeled base, another biped, or a quadruped with
  no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility class, the
  whole-body capability shape, and the learned-policy substrate marker are queued
  Spec RFCs.
- Reference runtime: no change. An Open Duck Mini mapping would route a validated
  navigation intent to the RL walk policy, which realizes stepping; the planned
  `open_duck_mini_cell.yaml` fixture would document the coarse manifest honestly,
  declaring the legged-mobility gap rather than papering over it.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse description today.** URML cannot declare a bipedal robot honestly yet.
  The mapping is explicit that `drive_type` has no legged fit and that the
  whole-body shape is missing. This is the honest altitude, but it narrows what
  URML can express for Open Duck Mini until the queued Spec RFC lands.
- **Policy-boundary and granularity uncertainty.** Whether navigation-level intent
  is the right altitude over a learned walk policy, versus gait-level, is exactly
  the seam this RFC asks the maintainers to confirm; documented wrong, it would
  couple URML to one controller.

## Alternatives considered

1. **Descend to gait-level intent.** Rejected as the default. Expressing intent at
   gait level (step timing, foot placement) would couple URML to one learned
   controller and break substrate-neutrality. Navigation-level intent keeps URML
   above the policy; the altitude is confirmed with the maintainers, not assumed.
2. **Propose the legged-mobility class inside this RFC.** Rejected. Adding to
   URML's normative surface is a Spec RFC tied to
   [RFC-0010](0010-whole-body-bimanual-manipulation.md), with its own review. An
   Outreach RFC requests comment; it does not expand the spec quietly.
3. **Model the RL walk policy's internals in the manifest.** Rejected. The policy
   is a substrate concern owned by the platform. URML declares capability at intent
   altitude and bounds the intent; modelling the policy would fail the
   substrate-neutrality acid test.

## Prior art

- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline legged-mobility / whole-body gap is tied to.
- [RFC-0372 (ToddlerBot outreach)](0372-toddlerbot-outreach.md): the Move #29 wave
  anchor, which surfaces the same legged-mobility gap from the platform side.
- [RFC-0069 (Berkeley Humanoid Lite outreach)](0069-berkeley-humanoid-lite-outreach.md):
  the prior open-humanoid engagement that hit the same enum limit.
- [RFC-0075 (Stanford Pupper outreach)](0075-stanford-pupper-outreach.md): a prior
  open-legged-platform engagement (quadruped) with a learned controller.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  joint-level control layer below an intent, relevant to the policy / intent seam.
- Sibling Move #29 RFCs: RFC-0374 (K-Scale), RFC-0375 (PAL TALOS),
  RFC-0376 (legged_gym).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the Open Duck Mini maintainers:

1. **Capability vs policy.** For a small biped whose locomotion is a learned walk
   policy, what belongs in a URML capability declaration and what is the policy's
   job? Where should the line sit so URML neither over-claims nor under-declares?
2. **Intent granularity.** Is navigation-level intent (go to X, turn) the right
   granularity to bound over the learned controller, or would gait-level intent be
   more useful, accepting the coupling that brings?
3. **Legged-mobility-class declaration.** What does a minimal but honest
   legged-mobility class need for a small biped: a velocity bound, a balance
   constraint, a learned-policy marker, or more?
4. **Sensing surface.** Is matching URML's `perception` block against the onboard
   camera and sensors the right alignment for `scan` and `report`?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0373 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini) pointing
at this RFC. If the maintainers prefer another channel, URML will move the thread
there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 3,046 stars, not archived, Issues
      enabled, active, last push 2026-01-31).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse description today, policy-boundary and
      granularity uncertainty).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the legged-mobility class, whole-body shape, and
      learned-policy marker are flagged as queued Spec RFCs tied to RFC-0010, not
      proposed here.
- [x] Provenance: France-lineage, NATO-allied; default policy passes at the
      platform layer.
- [x] No license question asked; compatibility note states composition not
      vendoring without asserting an SPDX id.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Open Duck Mini is one
      legged platform among many, learned policy treated as substrate,
      composed-above not assumed, gap declared honestly).
