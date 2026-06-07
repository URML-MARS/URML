---
rfc: 0437
title: Techman Robot (tmr_ros2) integration — request for comment
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

# RFC-0437: Techman Robot (tmr_ros2) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile. Tier B.

## Summary

[`TechmanRobotInc/tmr_ros2`](https://github.com/TechmanRobotInc/tmr_ros2) (~66 stars, active) is the ROS 2 driver for Techman Robot (TM) collaborative arms, a Taiwan-based, Omron-affiliated cobot maker. TM arms are notable for built-in vision, and a vendor-maintained ROS 2 driver is a clean home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above tmr_ros2)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `tmr_ros2` on its ROS 2 action/service surface; a `pick_from` / `place_at` / `grasp` lowers onto the TM driver interface, the decide-then-do split made concrete.
- TM's built-in vision is the kind of `detect` source URML consumes: a detection binds a target a downstream action consumes (decide-then-do).
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

## What is asked

Request for comment from the Techman ROS 2 maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above tmr_ros2?
2. What should a URML capability manifest declare to describe a TM-class cobot honestly (reach/DOF, payload, joint/speed limits, gripper + graspable classes, integrated-vision detection classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the TM ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `detect`-then-act split. Techman is the vision-integrated-cobot vertex of the arm-driver wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `TechmanRobotInc/tmr_ros2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move36.yaml`.
