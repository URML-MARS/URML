---
rfc: 0448
title: openpi (Physical Intelligence) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0448: openpi (Physical Intelligence) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and the wrap-a-learned-policy pattern.

## Summary

[`Physical-Intelligence/openpi`](https://github.com/Physical-Intelligence/openpi) (Apache-2.0, ~12,210 stars, active, Discussions on) is the open release of the π0 / π0-FAST flow-based vision-language-action models from Physical Intelligence. A state-of-the-art open generalist VLA is exactly the kind of learned policy URML is built to sit above: a typed intent and a validated safety envelope around the model's actions. This RFC asks whether that is interesting.

## The mapping (URML above openpi)

URML sits above the VLA as a validated intent layer:

- A URML intent declares the goal and the envelope; a π0 policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts.
- This is the decide-then-do split applied to learning: the model is the actuator, URML is the typed intent and the safety envelope around it.
- Validate-before-actuate refuses an out-of-capability request before motion — a safety seam that complements, not replaces, the policy.

## What is asked

Request for comment from the openpi maintainers:

1. Is wrapping a π0 policy in a validated intent layer + safety envelope interesting?
2. What should a URML capability manifest declare to describe a π0-driven robot honestly (arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the policy/inference interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417, RFC-0424); the earlier VLA wave (Move #11). openpi is the state-of-the-art-open-VLA vertex of the round-2 wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `Physical-Intelligence/openpi` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move38.yaml`.
