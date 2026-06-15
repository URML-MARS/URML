---
rfc: 0610
title: embodied-agents (and emos) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0610: embodied-agents (and emos) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the edge-AI / on-robot-inference wave (Move #58); it is the closest fit in the wave. One RFC for the Automatika stack, covering embodied-agents and the related emos.

## Summary

[`automatika-robotics/embodied-agents`](https://github.com/automatika-robotics/embodied-agents) (MIT) is a ROS 2 framework for running local LLM, VLM, and VLA models on a robot, with a component that maps a model's output onto ros2_control / MoveIt Servo actions. That handoff, where a model proposes an action and something turns it into actuation, is exactly the seam URML is built to gate. The related [`automatika-robotics/emos`](https://github.com/automatika-robotics/emos) (MIT, "Embodied OS") orchestrates such on-robot model components. This RFC asks whether a validation gate at that handoff is useful.

## The relationship (URML beside embodied-agents)

- **The model proposes; URML validates; then it actuates.** A local LLM/VLM/VLA is creative and occasionally wrong. embodied-agents already turns model output into ros2_control / MoveIt Servo actions. URML's candidate role is the typed gate in between: the proposed action becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope (five passes: argument typing, capability, envelope, bindings, policy), and only an admissible action is dispatched. The model stays free to propose; the validator refuses what the robot cannot safely do.
- **A natural home for a validated-intent representation.** Because URML is a small, typed, runtime-neutral intent language, it is a good target for a model to emit and a validator to check, which is precisely the "VLA output to safe action" problem embodied-agents is solving.

## What is asked

1. Is a typed, statically-validated gate between a model's proposed action and ros2_control / MoveIt Servo useful in embodied-agents, or does the action-mapping component already carry that safety reasoning?
2. Could a local VLA/VLM emit URML intent as its action representation, so the capability + envelope check comes for free?
3. Which boundary, embodied-agents or emos, is the cleaner first place to look?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator, the Layer-4 natural-language grammar, the LLM bridge, and the LearnedPolicy envelope (RFC-0383). Anchor of Move #58; the on-robot model-to-action target of the wave.

## Implementation note

Outreach only. The post is a single GitHub Issue on `automatika-robotics/embodied-agents` (referencing emos) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move58.yaml`.
