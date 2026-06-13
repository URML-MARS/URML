---
rfc: 0497
title: Zeroth Bot integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0497: Zeroth Bot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`zeroth-robotics/zeroth-bot`](https://github.com/zeroth-robotics/zeroth-bot) (MIT, ~790 stars, active) is a low-cost open 3D-printed humanoid platform built for sim-to-real and reinforcement learning. URML is interesting to Zeroth Bot as the validated-intent layer above its control stack and as the place an RL policy declares the envelope it was trained in. This RFC asks whether either is useful.

## The mapping (URML beside Zeroth Bot)

- **Capability manifest + validated intent.** The humanoid's kinematic structure and stability limits map onto a URML `whole_body` declaration (RFC-0384); a command is validated against that envelope before dispatch (the decide-then-do split). URML is the typed gate above the control stack.
- **Learned-policy envelope.** Zeroth Bot is RL- and sim-to-real-oriented. A trained policy can carry its observation/action spaces and training-domain bounds as a URML `LearnedPolicy` declaration (RFC-0383), so the validator refuses to dispatch the policy outside the domain it learned — the out-of-distribution action caught before it reaches a low-cost humanoid's joints.

## What is asked

Request for comment from the Zeroth Bot maintainers:

1. Does a URML `whole_body` manifest for the humanoid read right?
2. For the RL / sim-to-real side, is a declared training envelope on a deployed policy useful?
3. Which is the cleaner first seam — the validated-intent layer, or the learned-policy envelope?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `whole_body` declaration (RFC-0384), the `LearnedPolicy` training envelope (RFC-0383), and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `zeroth-robotics/zeroth-bot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
