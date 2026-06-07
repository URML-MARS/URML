---
rfc: 0425
title: TurtleBot3 Manipulation (ROBOTIS) integration — request for comment
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

# RFC-0425: TurtleBot3 Manipulation (ROBOTIS) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families.

## Summary

[`ROBOTIS-GIT/turtlebot3_manipulation`](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation) (Apache-2.0, ~94 stars, active) is the integrated bringup for a TurtleBot3 mobile base combined with an OpenMANIPULATOR arm, from ROBOTIS. It is one of the most accessible and widely-taught open mobile manipulators, which makes it an ideal teaching surface for a validated nav + manipulation intent layer. This RFC asks whether that is interesting.

## The mapping (URML above TurtleBot3 Manipulation)

URML sits above the robot as a validated intent layer:

- URML's ROS 2 runtime meets the stack on its ROS 2 action/service surface; "drive to the marker and pick up the block" lowers onto a `move_to` (the base) plus a `grasp` (the OpenMANIPULATOR arm), the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach grasp or undeclared object before the arm moves.
- The small, well-documented platform makes the combined nav + manipulation manifest a clean classroom example.

## What is asked

Request for comment from the TurtleBot3 Manipulation maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for a validated-intent layer above this platform?
2. What should a URML capability manifest declare to describe a TurtleBot3 + OpenMANIPULATOR honestly (drive type, arm reach/DOF, gripper + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting as a teaching add-on for the TurtleBot3 ecosystem?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) families; the mobile-manipulation anchor (RFC-0422). TurtleBot3 Manipulation is the accessible-teaching vertex of the mobile-manipulation wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ROBOTIS-GIT/turtlebot3_manipulation` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move35.yaml`.
