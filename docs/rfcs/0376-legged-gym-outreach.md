---
rfc: 0376
title: legged_gym (massively-parallel legged-locomotion RL training) integration, request for comment from the legged_gym maintainers
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

# RFC-0376: legged_gym integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robots wave, round two. This RFC
reaches [`leggedrobotics/legged_gym`](https://github.com/leggedrobotics/legged_gym),
the reference Isaac-Gym-based environment for training legged-locomotion policies
with massively-parallel reinforcement learning. It **requests review and feedback
from the legged_gym maintainers**.

A great many quadruped and humanoid walk policies are trained in legged_gym. For
URML, the trained policy is the **locomotion substrate**: a learned controller
that tracks a velocity or pose command and keeps the body upright. URML composes
**above** that controller. A URML navigation-level intent (go to a named place,
walk at a declared velocity) plus the platform's declared capability and the
active safety envelope **bound what the learned locomotion policy is asked to
do**. URML does not train the policy and does not run the policy. It declares the
platform, statically validates that the requested intent is admissible against
the declared capability and the envelope **before** the controller is engaged,
then hands the controller a bounded command.

The stack is: URML intent -> validated navigation goal plus declared capability
-> a legged_gym-trained locomotion policy realizes the gait -> the platform
moves. The differentiator is **static admissibility and envelope checking before
the policy acts**, and a declared capability that **bounds the command a learned
locomotion controller is asked to satisfy**. This is the same
learned-policy-as-substrate framing URML used for robomimic
([RFC-0360](0360-robomimic-outreach.md)) and the safe-RL wave, applied to legged
locomotion.

## Motivation

legged_gym is where a large share of the field's quadruped and humanoid
locomotion policies are trained, and a learned locomotion controller is a sharp
test of URML's "declare the capability, bound what the substrate may attempt"
line:

1. **A trained locomotion policy is a substrate URML can dispatch to.** Like a
   base-velocity controller or a planner, a legged_gym-trained policy turns a
   command into motion: it tracks a target velocity or pose and stabilizes the
   body. URML treats it as one more mobility substrate. The language declares the
   admissible navigation goal and the platform capability; the policy realizes
   the gait.
2. **The declared capability can bound the command a policy is asked to track.**
   A locomotion policy was trained to track commands inside a velocity range. The
   manifest's `mobility.max_velocity` and the active envelope give a static,
   inspectable boundary the requested command is checked against before the
   controller is engaged, so URML does not ask a policy to track a command
   outside the envelope it was trained and bounded for.
3. **Admissibility is cheap and early at this seam.** Before the controller runs,
   URML can statically reject a navigation goal that exceeds the declared velocity
   bound or violates the active envelope. A command that cannot be admitted within
   the declared capability is never issued to the policy.
4. **It grounds substrate-neutrality.** The same `move_to` intent maps onto a
   wheeled base controller, a model-based whole-body controller
   ([RFC-0347](0347-ocs2-outreach.md)), or a legged_gym-trained learned policy.
   The learned locomotion controller is one mobility substrate among several; the
   URML navigation intent is unchanged across them.

Repo at [`leggedrobotics/legged_gym`](https://github.com/leggedrobotics/legged_gym)
(about 2,994 stars, Issues enabled, not archived, last push 2025-05-29). Built on
the Isaac stack (cross-reference [RFC-0050](0050-nvidia-isaac-lab-integration.md)).
Origin: the Robotic Systems Lab at ETH Zurich (Switzerland, NATO-allied); passes
US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `legged_gym_cell.yaml` fixture)

| URML field | Maps to legged_gym attribute |
|---|---|
| `robot_id`, `description` | The legged platform's identity (carried at the manifest envelope; not a policy concept) |
| `frames` | The frames the navigation goal and the policy's command are expressed in; a `move_to` pose is resolved here before a command is issued |
| `declared_locations` | Named target places a `move_to` resolves against before the goal is reduced to a velocity or pose command |
| `mobility.drive_type` | The locomotion mode of the platform; today URML has no legged-mobility class, so this is the headline queued gap below |
| `mobility.max_velocity` | The declared velocity ceiling; the static admissibility bound and the box the requested command is checked against before the policy tracks it |
| `manipulation` | Declared only for a loco-manipulation platform that carries an arm; absent for a locomotion-only body, per the honest-subset norm |
| `perception.cameras[]` / `sensors[]` | The platform's exteroception a `scan` / `detect` reads from, where present; locomotion policies are often proprioceptive and may declare none |
| Safety envelope limits (Pass 3) | Conjoined with the declared mobility limits; URML applies strictest-wins as the bound on the command the locomotion policy is asked to track |

### What URML v0.1 does not yet express for legged_gym

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Legged-mobility drive-type class (headline gap).** URML's
   `mobility.drive_type` enum
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) has no
   legged class: a quadruped or biped has no honest value to declare today. A
   future Spec RFC, tied to
   [RFC-0010](0010-whole-body-bimanual-manipulation.md), would add a legged
   drive-type class so a walking platform can declare its locomotion mode. **It is
   not proposed here.**
2. **Learned-locomotion-policy substrate declaration (headline gap).** URML has no
   first-class way to declare that locomotion is a learned policy with a bounded
   command space (the velocity or pose command range it tracks, and the training
   provenance), distinct from an analytic controller. A future Spec RFC could add
   a learned-policy substrate declaration so the manifest records what kind of
   locomotion controller is below the boundary and what command space the
   admissibility check bounds. **It is not proposed here.**

### Compatibility notes

- **Vendor org.** [`leggedrobotics`](https://github.com/leggedrobotics) (the
  Robotic Systems Lab at ETH Zurich).
- **Engagement repo.** [`leggedrobotics/legged_gym`](https://github.com/leggedrobotics/legged_gym):
  the reference Isaac-Gym-based environment for massively-parallel legged-
  locomotion RL training.
- **Origin / policy.** Switzerland (ETH Zurich, NATO-allied). Passes US-federal
  default policy (open-source research framework, no provenance gate at the
  training layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** A legged_gym-trained policy is one mobility substrate
  among several; the same URML `move_to` intent maps onto a wheeled base
  controller or a model-based whole-body controller
  ([RFC-0347](0347-ocs2-outreach.md)) with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility drive-type class and
  the learned-locomotion-policy substrate declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A legged_gym mapping would route a
  validated navigation goal plus the declared capability to a trained locomotion
  policy, bound the requested command against the declared velocity limit and the
  envelope, and let the policy track it; the planned `legged_gym_cell.yaml`
  fixture would document the admissibility check and the boundary hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Learned-controller-as-substrate is newer ground.** A learned locomotion policy
  is statistical, not closed-form. URML's static admissibility bound is honest
  about what it can promise: it bounds the command issued to the policy, it does
  not make the policy stable or correct inside that bound. The contribution is a
  hard outer guardrail, not a guarantee about the policy's gait.
- **The legged-mobility gap is real today.** URML cannot honestly declare a walking
  platform's drive type in v0.1. The mapping names this as the headline queued
  Spec RFC rather than papering over it, and the engagement is candid that the
  clean mapping waits on that class landing.

## Alternatives considered

1. **Have URML train or shape the locomotion policy itself.** Rejected.
   Massively-parallel RL for legged locomotion is a substrate concern and a deep,
   well-served field. URML declares intent, capability, and admissibility and
   issues a bounded command; reimplementing the training loop would couple the
   language to one framework and fail the substrate-neutrality acid test.
2. **Skip the static admissibility bound and trust the learned policy.** Rejected.
   The whole value URML adds at this seam is a hard, inspectable bound on the
   command a learned locomotion controller is asked to track before the platform
   moves. Trusting the policy unbounded discards URML's contribution and its
   safety posture.
3. **Wait for the legged-mobility drive-type class before engaging at all.**
   Rejected. The gap is real, but the right altitude and the right command
   boundary are exactly what this conversation with locomotion-RL researchers
   settles. Engaging now informs the queued Spec RFC rather than guessing at it.

## Prior art

- [RFC-0360 (robomimic outreach)](0360-robomimic-outreach.md): the
  learned-policy-as-substrate framing this RFC applies to legged locomotion.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md):
  the Isaac stack legged_gym builds on; the simulation substrate the policies are
  trained against.
- [RFC-0049 (ANYbotics ANYmal integration)](0049-anybotics-anymal-integration.md):
  the quadruped platform whose locomotion these policies most directly target.
- [RFC-0347 (OCS2 outreach)](0347-ocs2-outreach.md): the model-based whole-body
  control contrast to a learned locomotion policy.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer a deployed locomotion controller is wired through.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML surface the legged-mobility-class follow-up is tied to.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0377
  (rsl_rl), RFC-0378 (dial-mpc).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the legged_gym maintainers:

1. **Declaring a learned-locomotion platform.** How should URML declare a platform
   whose locomotion is a legged_gym-trained policy: as a capability the platform
   carries (a velocity range, a body the controller stabilizes), with the policy's
   internal behavior left as the substrate's responsibility? Where is the honest
   line between what the manifest declares and what the policy owns?
2. **Navigation-level granularity.** Is a navigation-level command (go to a place,
   walk at a velocity) the right URML altitude above a velocity-tracking
   locomotion policy, or should URML target the velocity or pose command the
   policy consumes directly?
3. **The legged-mobility-class gap.** URML has no legged `drive_type` today. What
   would a useful legged-mobility declaration record for a walking platform
   (modes, command space, the body's stability assumptions), so the queued Spec
   RFC is grounded in what locomotion-RL practitioners actually need?
4. **Bounding the command.** Can URML's declared `max_velocity` and the active
   envelope usefully bound the command a trained policy is asked to track before
   the platform moves? Is clamping or rejecting an out-of-bound command the right
   treatment at this seam?
5. **Conformance listing.** Would the legged_gym project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0376 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`leggedrobotics/legged_gym`](https://github.com/leggedrobotics/legged_gym)
pointing at this RFC (Issues are enabled on the repo). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 2,994 stars, not archived, Issues
      enabled, last push 2025-05-29; built on the Isaac stack).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, learned-controller newer ground, legged-
      mobility gap today).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs
      (legged-mobility class and learned-locomotion-policy declaration), not
      proposed here.
- [x] Provenance: Switzerland (ETH Zurich, NATO-allied); default policy passes at
      the training layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; a legged_gym-trained
      policy is one mobility substrate among several, URML declares the capability
      and bounds the command and does not train or run the policy).
