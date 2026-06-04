---
rfc: 0380
title: rl_games (high-throughput RL training library) integration, request for comment from the rl_games maintainers
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

# RFC-0380: rl_games integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robots wave, round two. This RFC
reaches [`Denys88/rl_games`](https://github.com/Denys88/rl_games), a fast,
high-throughput reinforcement-learning library widely used to train Isaac Gym and
Isaac Lab locomotion and manipulation policies. It **requests review and feedback
from the rl_games maintainers**.

rl_games is a training-infrastructure backend. It runs the high-throughput RL
loop that produces a policy; it is not a robot platform and not a runtime URML
dispatches to. This RFC is honest about that altitude up front, the same boundary
URML drew with rsl_rl ([RFC-0377](0377-rsl-rl-outreach.md)) and with GTSAM and
CasADi in earlier waves: URML composes above the artifact the backend produces,
not against the backend's training loop. For URML, an rl_games-trained policy,
once deployed on a platform, becomes the **locomotion (or manipulation)
substrate**; the language declares the platform capability and the safety
envelope that **bound the command the trained policy is asked to track**, and
statically validates a navigation-level intent **before** the policy is engaged.
URML does not run the training.

The useful conversation is about the boundary itself, and about whether a trained
policy could carry a declared capability and limit envelope URML can consume, so
the manifest URML validates against stays consistent with what the policy was
actually trained and bounded for. The differentiator is unchanged: **static
admissibility and envelope checking before the policy acts**, the same
learned-policy-as-substrate framing URML used for robomimic
([RFC-0360](0360-robomimic-outreach.md)).

## Motivation

rl_games trains many of the legged and humanoid policies that become a URML
locomotion substrate, alongside the Isaac stack ([RFC-0050](0050-nvidia-isaac-lab-integration.md)).
Its position as a training backend, one layer below the deployed policy, is
exactly why the boundary is worth stating carefully:

1. **rl_games produces the artifact, not the runtime URML talks to.** rl_games
   trains a policy at high throughput; the trained policy, deployed on a platform,
   is what URML dispatches to. URML stays above the trained controller and never
   reaches into the training loop. This is the rsl_rl, GTSAM, and CasADi
   backend-boundary framing: URML composes above the produced artifact, not
   against the solver or trainer that produced it.
2. **A trained policy is a substrate URML can dispatch to.** Once a policy is
   trained and deployed, it turns a command into motion: it tracks a target
   velocity or pose and stabilizes the body. URML treats it as one more substrate,
   declares the admissible goal and the platform capability, and lets the policy
   realize the motion.
3. **The declared capability can bound the command a policy is asked to track.**
   A policy was trained to track commands inside a range. URML's
   `mobility.max_velocity` and the active envelope give a static, inspectable
   boundary the requested command is checked against before the controller runs,
   so URML does not ask a policy to track a command outside what it was trained
   and bounded for.
4. **A consistent capability artifact would tighten the boundary.** If a trained
   policy could export the capability and limits it was trained under, URML's
   manifest could be checked against that artifact rather than hand-declared, so
   the admissibility bound and the policy's real command space agree. Whether that
   export is feasible from an rl_games-trained policy is a question this RFC puts
   to the maintainers.

Repo at [`Denys88/rl_games`](https://github.com/Denys88/rl_games) (about 1,350
stars, Issues enabled, not archived, active, last push 2026-05-25). Widely used to
train Isaac Gym and Isaac Lab locomotion and manipulation policies. Origin: Denys
Makoviichuk and contributors (open-source); treated as INTL, passes US-federal
default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `rl_games_policy_cell.yaml` fixture)

| URML field | Maps to an rl_games-trained-policy attribute |
|---|---|
| `robot_id`, `description` | The platform's identity (carried at the manifest envelope; not a library or policy concept) |
| `frames` | The frames the navigation goal and the policy's command are expressed in; a `move_to` pose is resolved here before a command is issued |
| `declared_locations` | Named target places a `move_to` resolves against before the goal is reduced to a velocity or pose command |
| `mobility.drive_type` | The locomotion mode of the platform; today URML has no legged-mobility class, so this is the headline queued gap below |
| `mobility.max_velocity` | The declared velocity ceiling; the static admissibility bound checked against the command the trained policy is asked to track |
| `manipulation` | Declared for a manipulation policy or a loco-manipulation platform that carries an arm; absent for a locomotion-only body, per the honest-subset norm |
| `perception.cameras[]` / `sensors[]` | The platform's exteroception a `scan` / `detect` reads from, where present; proprioceptive policies may declare none |
| Safety envelope limits (Pass 3) | Conjoined with the declared mobility limits; URML applies strictest-wins as the bound on the command the trained policy is asked to track |

### What URML v0.1 does not yet express for rl_games

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
2. **Learned-policy substrate declaration (headline gap).** URML has no
   first-class way to declare that locomotion or manipulation is a learned policy
   with a bounded command space (the command range it tracks, and the training
   provenance), distinct from an analytic controller. A future Spec RFC could add
   a learned-policy substrate declaration so the manifest records what kind of
   controller is below the boundary, and so a capability the policy exports could
   be checked against the declared manifest. **It is not proposed here.**

### Compatibility notes

- **Vendor org.** [`Denys88`](https://github.com/Denys88) (Denys Makoviichuk and
  contributors), the rl_games maintainer.
- **Engagement repo.** [`Denys88/rl_games`](https://github.com/Denys88/rl_games):
  a fast, high-throughput RL training library used to train Isaac Gym and Isaac
  Lab locomotion and manipulation policies; active.
- **Same-wave siblings.** [`leggedrobotics/rsl_rl`](https://github.com/leggedrobotics/rsl_rl)
  ([RFC-0377](0377-rsl-rl-outreach.md)) and
  [`leggedrobotics/legged_gym`](https://github.com/leggedrobotics/legged_gym)
  ([RFC-0376](0376-legged-gym-outreach.md)), the other RL training surfaces in
  this wave; the same backend-boundary framing applies to each.
- **Origin / policy.** International (open-source, Denys Makoviichuk and
  contributors). Treated as INTL; passes US-federal default policy (open-source
  research library, no provenance gate at the training layer).
- **License note.** Open-source; URML's relationship is cross-citation and
  composition, not vendoring.
- **Substrate-neutrality.** An rl_games-trained policy is one substrate among
  several; the same URML `move_to` intent maps onto a wheeled base controller, a
  model-based whole-body controller, or an rsl_rl-trained policy
  ([RFC-0377](0377-rsl-rl-outreach.md)) with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged-mobility drive-type class and
  the learned-policy substrate declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. An rl_games-policy mapping would route
  a validated navigation goal plus the declared capability to a trained policy,
  bound the requested command against the declared velocity limit and the
  envelope, and let the policy track it; the planned `rl_games_policy_cell.yaml`
  fixture would document the admissibility check and the backend boundary
  hermetically. URML talks to the deployed policy, not to the training library.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Backend boundary, lowest direct fit in the wave.** rl_games is a training
  library, one layer below the deployed policy and two below the platform. URML
  talks to the trained policy and the platform, not to the library. The engagement
  is candid that the contact is about a boundary and a possible capability-export
  artifact, not a runtime URML drives. This is the same honest altitude URML drew
  with rsl_rl, GTSAM, and CasADi, and the most indirect fit among the Move #29
  targets.
- **The legged-mobility gap is real today.** URML cannot honestly declare a walking
  platform's drive type in v0.1. The mapping names this as the headline queued
  Spec RFC rather than papering over it.

## Alternatives considered

1. **Engage rl_games as if URML drove the training loop.** Rejected. URML does not
   train and does not run RL; reaching into the library's training loop would
   couple the language to one backend and fail the substrate-neutrality acid test.
   The honest contact is the trained policy and the boundary, not the trainer.
2. **Skip rl_games and engage only the platform repos.** Rejected. The
   capability-export question (could a trained policy carry the limits it was
   trained under) is best understood by the people who build the training library
   that emits the policy artifact, so the boundary is worth stating to the rl_games
   maintainers directly, alongside the platform-facing engagements.
3. **Skip the static admissibility bound and trust the trained policy.** Rejected.
   The value URML adds at this seam is a hard, inspectable bound on the command a
   learned controller is asked to track before the platform moves. Trusting the
   policy unbounded discards URML's contribution and its safety posture.

## Prior art

- [RFC-0377 (rsl_rl outreach)](0377-rsl-rl-outreach.md): the same-wave sibling RL
  library; the closest precedent for this backend-boundary framing applied to a
  trainer.
- [RFC-0376 (legged_gym outreach)](0376-legged-gym-outreach.md): the same-wave
  training environment built on rsl_rl; the platform-facing engagement to this
  library-facing one.
- [RFC-0360 (robomimic outreach)](0360-robomimic-outreach.md): the
  learned-policy-as-substrate framing this RFC applies to rl_games-trained
  policies.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md):
  the Isaac stack rl_games is most widely used to train policies in.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML surface the legged-mobility-class follow-up is tied to.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0376
  (legged_gym), RFC-0377 (rsl_rl).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the capability surface this engagement exercises.

## Unresolved questions

For the rl_games maintainers:

1. **The backend boundary.** Is it right that URML talks to the trained policy and
   the platform that runs it, and stays entirely above the training library? Where
   would you draw the line between what rl_games owns (training, the policy) and
   what a language above the controller declares (intent, capability,
   admissibility)?
2. **Exporting a capability artifact.** Could a trained policy export the
   capability and limits it was trained under (the command range it tracks, the
   body assumptions), so URML's manifest can be checked against that artifact
   rather than hand-declared? Is that feasible from an rl_games-trained policy, or
   is the bound only knowable at deployment?
3. **Navigation-level granularity.** Is a navigation-level command (go to a place,
   walk at a velocity) the right URML altitude above a velocity-tracking policy, or
   should URML target the command the policy consumes directly?
4. **The legged-mobility-class gap.** URML has no legged `drive_type` today. What
   would a useful legged-mobility declaration record for a walking platform, so the
   queued Spec RFC is grounded in what high-throughput-RL practitioners need?
5. **Conformance listing.** Would the rl_games project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0380 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`Denys88/rl_games`](https://github.com/Denys88/rl_games) pointing at this RFC
(Issues are enabled on the repo). If the maintainers prefer another channel, URML
will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 1,350 stars, not archived, Issues
      enabled, active, last push 2026-05-25; used to train Isaac Gym and Isaac Lab
      policies).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, backend boundary and lowest direct fit in the
      wave, legged-mobility gap today).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs
      (legged-mobility class and learned-policy substrate declaration), not
      proposed here.
- [x] Provenance: international (open-source, Denys Makoviichuk and contributors);
      default policy passes at the training layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; an rl_games-trained
      policy is one substrate among several, URML talks to the policy and the
      platform not the training library, declares the capability, and does not
      train or run the policy).
