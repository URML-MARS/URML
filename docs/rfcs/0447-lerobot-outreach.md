---
rfc: 0447
title: LeRobot (Hugging Face) integration — request for comment
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

# RFC-0447: LeRobot (Hugging Face) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and the pattern of wrapping a learned policy in a validated envelope (the decide-then-do split applied to learning). It is the anchor of the VLA / robot-learning round-2 wave (Move #38).

## Summary

[`huggingface/lerobot`](https://github.com/huggingface/lerobot) (Apache-2.0, ~24,750 stars, active daily) is Hugging Face's end-to-end robot-learning hub — models (including SmolVLA), datasets, and training/eval for real and simulated robots. It is the most-starred open robot-learning project, and a learned policy needs exactly what URML provides above it: a typed, validated intent and a safety envelope. This RFC asks whether that is interesting.

## The mapping (URML above LeRobot)

URML sits above the learned policy as a validated intent layer:

- A URML intent declares the goal and the envelope; a LeRobot policy (e.g. SmolVLA) produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts.
- This is the decide-then-do split applied to learning: the policy is the actuator, URML is the typed intent and the safety envelope around it.
- Validate-before-actuate refuses an out-of-capability request (undeclared object, out-of-reach pose, over-limit speed) before motion — a safety seam a learned policy does not provide on its own.

## What is asked

Request for comment from the LeRobot maintainers:

1. Is wrapping a LeRobot policy in a validated intent layer + safety envelope interesting in the robot-learning context?
2. What should a URML capability manifest declare to describe a LeRobot-driven robot honestly (drive/arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the policy/inference interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417 drone-RL, RFC-0424 TidyBot++); the earlier VLA wave (Move #11). LeRobot is the anchor of the VLA / robot-learning round-2 wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `huggingface/lerobot` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Distinct from the prior `huggingface/smolagents` engagement (Move #11). Tracked in `examples/lighthouses/outreach-move38.yaml`.
