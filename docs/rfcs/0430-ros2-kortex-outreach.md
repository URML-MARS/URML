---
rfc: 0430
title: Kinova ros2_kortex integration — request for comment
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

# RFC-0430: Kinova ros2_kortex integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its manipulation primitive family. Tier B.

## Summary

[`Kinovarobotics/ros2_kortex`](https://github.com/Kinovarobotics/ros2_kortex) (BSD-3-Clause, ~118 stars, active) is the ROS 2 driver for Kinova's Gen3 arm — the manipulation half of Kinova's mobile-manipulation platforms (the arm rides the MOVO mobile base). A vendor-maintained, permissively-licensed arm driver is a clean place to align URML's manipulation intent with a real robot's interface, and to discuss the mobile-manipulator manifest when the arm is mounted on a base. This RFC asks whether that is interesting.

## The mapping (URML above ros2_kortex)

URML sits above the arm driver as a validated intent layer:

- URML's ROS 2 runtime meets `ros2_kortex` on its ROS 2 action/service surface; a `grasp` / `release` (and, on a mobile base, a preceding `move_to`) lowers onto the Kinova arm interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach grasp or an undeclared object class before the arm moves.
- When the Gen3 is mounted on a mobile base (MOVO), the combined manifest is the natural mobile-manipulation case.

## What is asked

Request for comment from the Kinova maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for a validated manipulation-intent layer above the Gen3 arm?
2. What should a URML capability manifest declare to describe a Kinova arm honestly (reach/DOF, gripper + graspable classes, force limits), and how should that extend when the arm rides a mobile base?
3. Is a validated natural-language layer interesting for Kinova's research and integrator users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `grasp` / manipulation family (Move #27); the dexterous-hand manifest questions (LEAP / Shadow, Move #27); the mobile-manipulation anchor (RFC-0422). Kinova ros2_kortex is the vendor-arm vertex of the mobile-manipulation wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `Kinovarobotics/ros2_kortex` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move35.yaml`.
