---
rfc: 0677
title: Comau CRCOpen ROS 2 Driver (ukaea/CRCOpenROS2Driver) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-18
updated: 2026-08-18
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

# RFC-0677: Comau CRCOpen ROS 2 Driver (ukaea/CRCOpenROS2Driver) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the nuclear / hazmat remote-handling wave (Move #70).

## Summary

[`ukaea/CRCOpenROS2Driver`](https://github.com/ukaea/CRCOpenROS2Driver) (UK Atomic Energy Authority / RACE) is a `ros2_control` hardware component that commands real Comau industrial arms (the NJ130-2.6 today) through Comau's CRCOpen interface, to unlock the ROS 2 ecosystem for nuclear research and development. That is exactly where URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (reach, payload, joint limits, gripper force) and a safety envelope, and URML checks a motion or grasp is admissible before the command reaches the driver and the arm. In a remote-handling cell you cannot try-and-see, so a static pre-dispatch check is worth more, not less. This is a request for comment.

## The relationship (URML beside the driver)

- **The plan proposes, the validator gates.** Whatever produces the motion (a planner, an operator, an LLM) decides the command; URML checks the command is admissible on the declared arm, inside the declared envelope, before the `ros2_control` hardware component sends it. URML does the check, the driver keeps the actuation.
- **A clean Layer-1 seam.** URML's Layer-1 hardware-abstraction seam is exactly the `ros2_control` boundary this driver implements (see RFC-0319), so the capability manifest maps onto the same interfaces the hardware component already exposes.
- **Neutral, no vendoring.** URML is substrate- and model-neutral. It cross-cites and does not vendor the Comau-provided `orl_driver` binary or depend on it; it composes above the command.

## What is asked

1. In a nuclear remote-handling context, would a declared capability + safety envelope, checked before a command reaches the arm, be a useful guard on top of the driver?
2. Would a small worked example mapping a Comau NJ130 motion or grasp onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, the `ros2_control` Layer-1 seam (RFC-0319), and the static validate-before-actuate gate. Anchor of the Move #70 nuclear / hazmat remote-handling wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ukaea/CRCOpenROS2Driver` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move70.yaml`.
