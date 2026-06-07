---
rfc: 0431
title: Universal Robots ROS 2 Driver integration — request for comment
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

# RFC-0431: Universal Robots ROS 2 Driver integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile. It is the anchor of the industrial / collaborative arm-driver wave (Move #36).

## Summary

[`UniversalRobots/Universal_Robots_ROS2_Driver`](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver) (BSD-3-Clause, ~781 stars, active) is the official ROS 2 driver for UR's CB3 and e-Series collaborative arms — the most widely-deployed cobot family in the world, and the most-starred open vendor arm driver. A real industrial arm with a clean, vendor-maintained ROS 2 driver is the ideal home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above the UR driver)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets the driver on its ROS 2 action/service surface (and `ros2_control` controllers); a `pick_from` / `place_at` / `grasp` lowers onto the arm interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves — a real safety and liability boundary on industrial hardware.
- The UR manifest (reach, payload, joint limits, gripper, graspable classes) is a clean test of URML's industrial-profile capability model.

## What is asked

Request for comment from the UR ROS 2 Driver maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above the UR driver?
2. What should a URML capability manifest declare to describe a UR-class cobot honestly (reach/DOF, payload, joint/speed limits, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the UR ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). The UR driver is the anchor of the arm-driver wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `UniversalRobots/Universal_Robots_ROS2_Driver` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move36.yaml`.
