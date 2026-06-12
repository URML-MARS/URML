---
rfc: 0489
title: MushroomRL integration — request for comment
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

# RFC-0489: MushroomRL integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). Part of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`MushroomRL/mushroom-rl`](https://github.com/MushroomRL/mushroom-rl) (MIT, ~0.9k stars, active, TU Darmstadt / IIT academic lineage) is a Python RL library with a clean `MDPInfo` that names the observation and action spaces of every environment. That explicit structure is the input a URML `LearnedPolicy` deployment envelope (RFC-0383) needs: when a MushroomRL-trained policy is deployed on a robot, its `MDPInfo` spaces and training-domain bounds are exactly what URML wants to carry and check. This RFC asks for comment.

## The mapping (URML beside MushroomRL)

- **MDPInfo to envelope.** A MushroomRL agent's `MDPInfo` declares the observation and action spaces it was trained against. Emitting those (plus the training-domain bounds) as a URML `LearnedPolicy` envelope makes "what was this policy trained for" a typed, checkable artifact rather than tacit knowledge.
- **Validated deployment.** With the envelope declared, URML is the typed gate between the trained policy and the robot: each proposed action is validated against the robot's declared capabilities and the active safety envelope before dispatch (decide-then-do). The policy decides; URML does.

## What is asked

Request for comment from the MushroomRL maintainers:

1. Does exporting an agent's `MDPInfo` spaces (plus training-domain bounds) as a declared deployment envelope make sense as an optional artifact?
2. Is the validated-deployment gate (action checked against declared capabilities + envelope before dispatch) interesting, or already covered elsewhere?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) at the foundation-model layer; this is the general-purpose RL layer below. Sibling RFC-0485 anchors Move #43.

## Implementation note

Outreach only. The post is a GitHub Issue on `MushroomRL/mushroom-rl` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move43.yaml`.
