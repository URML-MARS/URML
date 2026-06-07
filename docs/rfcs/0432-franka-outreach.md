---
rfc: 0432
title: Franka ROS 2 integration — request for comment
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

# RFC-0432: Franka ROS 2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile.

## Summary

[`frankarobotics/franka_ros2`](https://github.com/frankarobotics/franka_ros2) (Apache-2.0, ~340 stars, active) is the official ROS 2 integration for Franka's research robots — the most widely-used research manipulator in robot-learning and manipulation labs. A precise, research-focused arm with a permissive vendor-maintained ROS 2 stack is a natural home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above franka_ros2)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `franka_ros2` on its ROS 2 action/service surface (and `ros2_control` controllers); a `grasp` / `pick_from` / `place_at` lowers onto the arm interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.
- The Franka manifest (reach, payload, joint limits, force thresholds, gripper, graspable classes) exercises URML's force-aware industrial-profile capability model.

## What is asked

Request for comment from the Franka ROS 2 maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above franka_ros2?
2. What should a URML capability manifest declare to describe a Franka-class research arm honestly (reach/DOF, payload, joint/force limits, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for Franka's research community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). Franka is the research-arm vertex of the arm-driver wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `frankarobotics/franka_ros2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move36.yaml`.
