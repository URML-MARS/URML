---
rfc: 0378
title: DIAL-MPC (training-free legged whole-body control via diffusion) integration, request for comment from the DIAL-MPC maintainers
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

# RFC-0378: DIAL-MPC integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robot wave, round two. This RFC
reaches [`LeCAR-Lab/dial-mpc`](https://github.com/LeCAR-Lab/dial-mpc), a
training-free, real-time legged-robot whole-body controller that realizes
locomotion with diffusion-style sampling-based MPC. It **requests review and
feedback from the DIAL-MPC maintainers**.

DIAL-MPC is a legged whole-body controller. URML is not. URML describes robot
intent and declares capability: a navigation or task-level intent (`move_to`,
`scan`, `report`), a declared platform capability, and an active safety
envelope. DIAL-MPC realizes the whole-body motion that satisfies that intent on
a real legged robot in real time. URML composes **above** it: URML validates
admissibility (the target is reachable, the request is within the declared
envelope) before any motion, and does not do control.

This RFC is honest about the headline gap up front. URML's Layer-1 manifest has
no legged mobility-class `drive_type` and no whole-body capability declaration,
so a legged platform cannot yet be declared at its real altitude. That gap is
the headline *queued Spec RFC*, tied to
[RFC-0010](0010-whole-body-bimanual-manipulation.md), and is **not proposed
here**.

## Motivation

DIAL-MPC is a training-free legged whole-body controller, which makes it a clean
contrast to the learned-policy stacks in this same wave and a clean test of
URML's "declare and validate, do not control" boundary:

1. **It realizes locomotion that URML only describes.** URML stops at intent and
   capability. A whole-body MPC turns "go to the kitchen" into joint-level
   torques that keep a legged robot upright while it moves. DIAL-MPC is exactly
   the realizing layer URML is designed to sit above, never inside.
2. **It is training-free, which sharpens the boundary.** Unlike a learned policy,
   DIAL-MPC needs no policy artifact. From URML's declaration point of view the
   controller is opaque either way: URML declares what the platform can do and
   validates the request against it, and the controller's internals (sampling
   MPC or a learned network) stay below the line.
3. **It exposes the honest legged gap.** Mapping a legged platform onto URML's
   manifest shows immediately that `drive_type` has no legged class and there is
   no whole-body capability block. Naming that gap (queued Spec RFC, tied to
   RFC-0010) is more useful than papering a quadruped into `differential`.
4. **It grounds substrate-neutrality across realizing layers.** A URML intent
   that a DIAL-MPC controller realizes must also be realizable by a different
   legged controller, learned or model-based, with no change to the program.
   DIAL-MPC is one realizing layer among several engaged in this wave.

Repo at [`LeCAR-Lab/dial-mpc`](https://github.com/LeCAR-Lab/dial-mpc) (about 975
stars, Issues enabled, not archived, last push 2025-05-28). Origin: CMU LeCAR
Lab (United States); passes US-federal default policy (open-source academic
controller, no provenance gate at the control layer).

## Detailed design

### URML v0.1 capability and intent mapping (planned `dial_mpc_legged_cell.yaml` fixture)

| URML field or primitive | Maps to DIAL-MPC role |
|---|---|
| `robot_id`, `description` | The legged platform's identity (carried at the manifest envelope) |
| `frames`, `declared_locations` | The world frame and named targets a `move_to` resolves against |
| `mobility.drive_type` | The platform's locomotion class; **no legged class exists in v0.1** (see queued gap below; today declared at a coarser approximation) |
| `mobility.max_velocity` | The base velocity bound, passed down as an MPC velocity constraint |
| `mobility.max_payload` | The declared carry limit, passed down as a load bound the controller respects |
| `move_to` (Layer-2 primitive) | A navigation-level goal the DIAL-MPC controller realizes as whole-body motion in real time |
| `scan`, `report` | Perception and reporting intents issued around a realized locomotion goal |
| Safety envelope limits (Pass 3) | Conjoined with the platform's declared limits before any motion; URML applies strictest-wins, the controller treats them as constraints |

### What URML v0.1 does not yet express for DIAL-MPC

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Legged mobility-class `drive_type` and a whole-body capability declaration.**
   URML's `mobility.drive_type` enumerates wheeled, tracked, and aerial classes,
   with no legged or whole-body class, so a quadruped or humanoid cannot be
   declared at its real altitude. This is the **headline** gap. A future Spec
   RFC, tied to [RFC-0010](0010-whole-body-bimanual-manipulation.md), would add a
   legged mobility class and a whole-body capability block so the manifest can
   describe a legged platform honestly.
2. **Realizing-controller class hint.** URML's manifest does not record that a
   declared platform's motion is realized by a whole-body MPC rather than a
   wheeled base controller. A future Spec RFC could add an optional
   realizing-controller hint so tooling can reason about the control layer
   explicitly. It would not model the controller.

### Compatibility notes

- **Engagement repo.** [`LeCAR-Lab/dial-mpc`](https://github.com/LeCAR-Lab/dial-mpc):
  a training-free, real-time legged whole-body controller using diffusion-style
  sampling-based MPC.
- **Origin / policy.** CMU LeCAR Lab (United States). Passes US-federal default
  policy (open-source academic controller, no provenance gate at the control
  layer).
- **Open-source posture.** Open-source; the relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** DIAL-MPC is one realizing controller among several;
  the same URML intent maps to a learned legged policy or a different model-based
  stack with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged mobility class plus
  whole-body capability block (the headline gap) and the realizing-controller
  hint are queued Spec RFCs.
- Reference runtime: no change in this RFC. A DIAL-MPC mapping would route a
  validated `move_to` goal, with the declared limits attached as constraints, to
  the controller's task interface; the planned `dial_mpc_legged_cell.yaml`
  fixture would document the admissibility check before any motion.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Headline gap is unfilled.** URML cannot yet declare a legged platform at its
  real altitude, so the mapping today leans on a coarse `drive_type`
  approximation. The RFC names this honestly and defers it to a queued Spec RFC
  rather than hiding it.
- **Research-velocity target.** DIAL-MPC is an actively evolving research
  controller; a task-interface boundary documented today may move. The mapping is
  described at the intent and capability altitude to stay robust to internal
  churn.

## Alternatives considered

1. **Declare a legged platform as `differential` or `manipulator_base` today.**
   Rejected. It would misdescribe the platform and fail URML's honesty norm. The
   correct response is to name the missing legged class as a queued Spec RFC, not
   to force a wheeled label.
2. **Push URML down into the control loop.** Rejected. URML declares intent and
   validates admissibility; it does not produce torques. Reaching into the
   whole-body MPC would break the layered design and the substrate-neutrality
   acid test.
3. **Wait for the legged Spec RFC before engaging.** Rejected. The engagement is
   most useful precisely while the gap is open: the maintainers' view of the
   legged capability surface should inform the Spec RFC, not arrive after it.

## Prior art

- [RFC-0347 (OCS2 outreach)](0347-ocs2-outreach.md): the general switched-system
  optimal-control engagement; DIAL-MPC is a legged-specific model-based
  contrast to it.
- [RFC-0376 (legged_gym outreach)](0376-legged-gym-outreach.md): the
  learned-policy legged contrast; DIAL-MPC is training-free where legged_gym
  learns a policy.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline legged-capability gap ties to.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  controller-interface engagement a realized legged stack typically plugs into.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0376
  (legged_gym, learned-policy legged), RFC-0377 (rsl_rl), and RFC-0379
  (legged_control).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the DIAL-MPC maintainers:

1. **Intent-to-task boundary.** Is "URML intent plus declared capability -> a
   DIAL-MPC task or cost specification" the right seam, with URML producing a
   navigation-level goal and staying entirely above the controller?
2. **Limits as constraints.** What is the right way for URML's declared limits
   (velocity, payload, the safety envelope) to become MPC constraints the
   controller respects, so an admissible URML program is also a feasible MPC
   problem?
3. **Training-free vs learned, from the declaration side.** From URML's
   declaration point of view a controller is opaque. Is there anything a
   training-free MPC needs declared differently from a learned policy, or is the
   capability declaration genuinely controller-agnostic?
4. **Legged capability surface.** As URML drafts a legged mobility class and a
   whole-body capability block (the queued Spec RFC tied to RFC-0010), what
   fields would a whole-body MPC most want a manifest to declare?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0378 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`LeCAR-Lab/dial-mpc`](https://github.com/LeCAR-Lab/dial-mpc) pointing at this
RFC (the repo has Issues enabled). If the maintainers prefer another channel,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified (about 975 stars, not archived, Issues enabled, last push
      2025-05-28).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, unfilled headline gap, research-velocity
      target).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs (the
      legged mobility class tied to RFC-0010 is the headline), not proposed here.
- [x] Provenance: US (CMU LeCAR Lab); default policy passes at the control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML composes above
      the controller, declares and validates, does not control).
