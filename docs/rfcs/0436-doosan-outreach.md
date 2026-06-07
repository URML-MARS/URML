---
rfc: 0436
title: Doosan Robotics ROS 2 integration — request for comment
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

# RFC-0436: Doosan Robotics ROS 2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile. Tier B.

## Summary

[`doosan-robotics/doosan-robot2`](https://github.com/doosan-robotics/doosan-robot2) (BSD-3-Clause, ~157 stars, active) is the official ROS 2 stack for Doosan's collaborative arms. Doosan is a fast-growing cobot maker, and a permissively-licensed vendor-maintained ROS 2 driver is a clean home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above doosan-robot2)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `doosan-robot2` on its ROS 2 action/service surface (and `ros2_control` controllers); a `pick_from` / `place_at` / `grasp` lowers onto the Doosan driver interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.
- The Doosan manifest (reach, payload, joint/speed limits, gripper, graspable classes) is a clean test of URML's industrial-profile model.

## What is asked

Request for comment from the Doosan ROS 2 maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above doosan-robot2?
2. What should a URML capability manifest declare to describe a Doosan-class cobot honestly (reach/DOF, payload, joint/speed limits, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the Doosan ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). Doosan is the growing-cobot-OEM vertex of the arm-driver wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `doosan-robotics/doosan-robot2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move36.yaml`.
