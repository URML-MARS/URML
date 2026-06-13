---
rfc: 0510
title: RoboHive integration — request for comment
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

# RFC-0510: RoboHive integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split. It is the anchor of the AI / robot-learning wave (Move #46): a trained policy declares the capability envelope it was trained in, so URML can validate that a deployment stays inside it.

## Summary

[`vikashplus/robohive`](https://github.com/vikashplus/robohive) (Apache-2.0, ~630 stars, active) is a unified framework for robot learning: environments, teleoperation, and policy training under one roof. URML is interesting to a learning framework at the deployment boundary: a policy trained in RoboHive carries observation/action spaces and a training domain, and URML's `LearnedPolicy` declaration lets that policy publish those bounds so a deployment is validated against the domain it was actually trained for. This RFC asks whether the mapping is useful.

## The mapping (URML beside RoboHive)

- **Envelope export.** A RoboHive environment defines the observation/action spaces and the domain a policy is trained against. Emitting those as a URML `LearnedPolicy` envelope (obs/action ranges + training-domain bounds) makes "what was this policy trained for" a typed, checkable artifact next to the trained weights.
- **Validated deployment.** With the envelope declared, URML sits between the trained policy and the robot: each proposed action is validated against the robot's declared capabilities and the active safety envelope before dispatch (the decide-then-do split). The policy decides; URML is the typed gate that does.

## What is asked

Request for comment from the RoboHive maintainers:

1. Does exporting a trained policy's observation/action spaces (and training-domain bounds) as a declared deployment envelope make sense as an optional artifact?
2. Is a validated-intent gate between a RoboHive policy and a real robot interesting?
3. Which is the cleaner first seam — the envelope export, or the deployment gate?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The general-purpose RL-framework wave (Move #43: stable-baselines3, cleanrl, skrl, torchrl and others) asked a closely related question; this wave is the robot-learning-framework / eval layer. Anchor of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `vikashplus/robohive` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
