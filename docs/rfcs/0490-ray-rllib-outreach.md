---
rfc: 0490
title: Ray RLlib integration — request for comment
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

# RFC-0490: Ray RLlib integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). Part of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`ray-project/ray`](https://github.com/ray-project/ray) (Apache-2.0, ~42.8k stars, very active, originated at UC Berkeley RISELab / stewarded by Anyscale) includes **RLlib**, a scalable RL library. This RFC is scoped narrowly to RLlib and its deployment story, not to Ray's distributed-compute core. An RLlib-trained policy is deployed to act on a system, and URML's question is the same one this wave asks everywhere: what declares the bounds the policy was trained inside, and what validates that a deployment stays within them? URML's `LearnedPolicy` declaration (RFC-0383) is built for that. This is a request for comment.

## The mapping (URML beside RLlib)

- **Policy to envelope.** An RLlib `Policy` knows its observation and action spaces and the environment domain it trained against. Emitting those as a URML `LearnedPolicy` envelope (obs/action ranges + training-domain bounds) makes the deployment boundary a typed, checkable artifact.
- **Validated deployment.** When an RLlib policy is served to control a robot, URML is the typed gate between the policy and the hardware: each proposed action is checked against the robot's declared capabilities and the active safety envelope before dispatch (decide-then-do). The policy decides; URML does. This complements a serving layer; it does not replace it.

## What is asked

Request for comment from the RLlib maintainers:

1. Does exporting an RLlib policy's observation/action spaces (plus training-domain bounds) as a declared deployment envelope make sense?
2. For an RLlib policy serving a robot, is a validated-intent gate (action checked against declared capabilities + envelope before dispatch) interesting, or already addressed by a pattern you recommend?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything. The ask is scoped to RLlib, not Ray core.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) at the foundation-model layer; this is the general-purpose RL layer below. Sibling RFC-0485 (Stable-Baselines3) anchors Move #43.

## Implementation note

Outreach only. The post is a GitHub Issue on `ray-project/ray` (Discussions not enabled), scoped explicitly to RLlib, under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move43.yaml`.
