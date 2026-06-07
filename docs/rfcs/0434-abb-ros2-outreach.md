---
rfc: 0434
title: ABB ROS 2 driver (PickNik) integration — request for comment
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

# RFC-0434: ABB ROS 2 driver (PickNik) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile.

## Summary

[`PickNikRobotics/abb_ros2`](https://github.com/PickNikRobotics/abb_ros2) (Apache-2.0, ~159 stars, active) is the community-maintained ROS 2 driver for ABB industrial robots (maintained by PickNik). ABB is one of the largest industrial-robot makers, and a permissively-licensed ROS 2 driver for its arms is a strong home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above abb_ros2)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `abb_ros2` on its ROS 2 action/service surface (and `ros2_control` controllers); a `pick_from` / `place_at` / `grasp` lowers onto the ABB driver interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.
- The ABB manifest (reach, payload, joint/speed limits, end-effector, graspable classes) is a clean test of URML's industrial-profile model on production hardware.

## What is asked

Request for comment from the abb_ros2 maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above abb_ros2?
2. What should a URML capability manifest declare to describe an ABB-class industrial arm honestly (reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds)?
3. Is a validated natural-language layer interesting for the ABB ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). abb_ros2 is the community-maintained-major-OEM vertex of the arm-driver wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `PickNikRobotics/abb_ros2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move36.yaml`.
