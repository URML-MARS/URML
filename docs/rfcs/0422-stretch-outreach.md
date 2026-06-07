---
rfc: 0422
title: Hello Robot Stretch integration — request for comment
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

# RFC-0422: Hello Robot Stretch integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its two core primitive families — navigation (`move_to`) and manipulation (`grasp`). It is the anchor of the mobile-manipulation wave (Move #35).

## Summary

[`hello-robot/stretch_ros2`](https://github.com/hello-robot/stretch_ros2) (Apache-2.0, ~122 stars, active) is the ROS 2 stack for the Stretch mobile manipulator — a lightweight, single-arm mobile robot built for in-home and research use. A mobile manipulator is the cleanest possible exercise of URML: "go to the kitchen and pick up the mug" combines URML's two core primitive families, navigation and manipulation, in one sentence. This RFC asks whether a validated intent layer above Stretch is interesting.

## The mapping (URML above Stretch)

URML sits above the robot as a validated intent layer:

- URML's ROS 2 runtime meets Stretch on its ROS 2 action/service surface; "go to the kitchen and pick up the mug" lowers onto a `move_to` (base navigation) followed by a `grasp` (the arm), the decide-then-do split made concrete.
- Validate-before-actuate refuses an undeclared object class or an out-of-reach grasp before the arm moves.
- The combined nav + manipulation manifest is a rich, honest test of URML's capability model on one platform.

## What is asked

Request for comment from the Stretch maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above Stretch?
2. What should a URML capability manifest declare to describe a Stretch-class mobile manipulator honestly (drive type, arm reach/DOF, gripper + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting for Stretch's in-home and research users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) primitive families; the `detect`-then-act split. Stretch is the anchor of the mobile-manipulation wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `hello-robot/stretch_ros2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move35.yaml`.
