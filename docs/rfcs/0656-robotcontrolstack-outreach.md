---
rfc: 0656
title: RobotControlStack (RobotControlStack/robot-control-stack) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-03
updated: 2026-07-03
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

# RFC-0656: RobotControlStack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #67.

## Summary

[`RobotControlStack/robot-control-stack`](https://github.com/RobotControlStack/robot-control-stack) is a lean, ROS-free framework for training and deploying vision-language-action models and RL agents, with sim-to-real support for Franka, UR5e, xArm, and SO-101. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. The deploy step of a sim-to-real stack is exactly where that check earns its place, because a policy trained in simulation can command an action that is fine in sim and out of bounds on the real arm.

## The relationship (URML beside RobotControlStack)

The framework takes a trained policy and runs it on real hardware. URML can declare the specific arm's reach, payload, joint limits, and the active keep-out and speed envelope, and validate a commanded action against that declaration at the moment before it leaves for the real robot. It is a static admissibility check at the sim-to-real boundary, not a controller and not part of training.

URML does not train, simulate, or drive the arm. It declares the real arm's envelope and confirms a commanded action is inside it before deployment dispatches it.

## What is asked

1. At the sim-to-real deploy boundary, is a declared-capability and envelope check on the policy's commanded action a useful guardrail before it reaches the real Franka / UR5e / xArm, or is that already covered by the deploy path?
2. Would a small worked example mapping a deployed action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a sim-to-real VLA/RL deployment framework. AGPL-3.0, so this is a cross-reference, not a code-reuse proposal; Ai2 (Seattle) with EU co-authors, US/allied. Part of Move #67.

## Implementation note

Outreach only. The post is a GitHub Issue on `RobotControlStack/robot-control-stack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move67.yaml`.
