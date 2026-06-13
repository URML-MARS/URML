---
rfc: 0514
title: robo-gym integration — request for comment
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

# RFC-0514: robo-gym integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`jr-robotics/robo-gym`](https://github.com/jr-robotics/robo-gym) (MIT, ~480 stars, active, JOANNEUM RESEARCH) is a toolkit for distributed deep reinforcement learning on real and simulated robots, with environments for real hardware (Universal Robots, MiR). URML is interesting at the deployment boundary: a policy trained against a robo-gym environment can declare the env's observation/action spaces and domain, so a real-robot deployment is validated against the bounds it was trained for. This RFC asks whether the mapping is useful.

## The mapping (URML beside robo-gym)

- **Env to envelope.** A robo-gym environment defines the observation/action spaces and the (real or simulated) domain a policy trains against. Emitting those as a URML `LearnedPolicy` envelope (RFC-0383) makes the training domain a typed, checkable artifact.
- **Validated deployment.** robo-gym already spans sim and real hardware; URML's gate sits at that boundary, checking each proposed action against the robot's declared capabilities and the active safety envelope before dispatch (the decide-then-do split). On a sim-to-real transfer, that gate catches an out-of-distribution action before it reaches a UR or MiR.

## What is asked

Request for comment from the robo-gym maintainers:

1. Does exporting a robo-gym env's spaces (plus domain bounds) as a URML deployment envelope make sense for the real-robot side?
2. Is a validated-intent gate at the sim-to-real boundary interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The general-purpose RL-framework wave (Move #43) asked the related envelope-export question; robo-gym's explicit real-hardware envs make the deployment boundary concrete. Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `jr-robotics/robo-gym` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
