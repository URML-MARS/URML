---
rfc: 0485
title: Stable-Baselines3 integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0485: Stable-Baselines3 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). It is the anchor of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`DLR-RM/stable-baselines3`](https://github.com/DLR-RM/stable-baselines3) (MIT, ~13.4k stars, actively maintained, German Aerospace Center) is the most widely used set of reliable RL algorithm implementations (PPO, SAC, TD3, DQN, ...). A trained SB3 policy is a function from an observation space to an action space, both declared explicitly as Gymnasium spaces, and trained inside a specific domain. URML is interesting to that policy at the moment it is *deployed on a robot*, and in a way that does not compete with SB3: URML can carry the policy's training envelope as a typed, validatable declaration and refuse to dispatch the policy's actions outside it. This RFC asks whether that is useful.

## The mapping (URML beside SB3)

URML's `LearnedPolicy` declaration (RFC-0383) already lets a manifest say "this capability is served by a learned policy trained within these bounds." Two complementary seams for SB3:

- **Envelope export.** A trained SB3 policy already knows its `observation_space` and `action_space` (Gymnasium `Box`/`Discrete`), and a `VecNormalize` wrapper knows the observation/return statistics the policy saw. Those are exactly the bounds a URML `LearnedPolicy` envelope wants: the obs/action ranges and the training-domain limits the policy should not be trusted outside of. The export is a small artifact emitted next to the saved model.
- **Validated deployment.** With the envelope declared, URML sits between the SB3 policy and the robot: each action the policy proposes is checked against the robot's declared capabilities and the active safety envelope before dispatch (the decide-then-do split). The policy decides; URML is the typed gate that does.

## What is asked

Request for comment from the SB3 maintainers:

1. Does exporting a trained policy's observation/action spaces (and `VecNormalize` bounds) as a declared deployment envelope make sense as an optional artifact alongside a saved model?
2. Is a validated-intent gate between an SB3 policy and a real robot (action checked against declared capabilities + envelope before dispatch) interesting, or already covered by something you recommend?
3. Which is the cleaner first seam — the envelope export, or the deployment gate?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` manifest declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) consume learned policies at the foundation-model layer; this wave is the general-purpose RL-training layer one stratum below. SB3 is the anchor of Move #43.

## Implementation note

Outreach only. The post is a GitHub Issue on `DLR-RM/stable-baselines3` (Discussions not enabled) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move43.yaml`.
