---
rfc: 0426
title: Interbotix LoCoBot (Trossen) integration — request for comment
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

# RFC-0426: Interbotix LoCoBot (Trossen) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families. Tier B.

## Summary

[`Interbotix/interbotix_ros_rovers`](https://github.com/Interbotix/interbotix_ros_rovers) (BSD-3-Clause, ~46 stars) is the Interbotix ROS stack for LoCoBot-class rovers (a mobile base plus an Interbotix arm), from Trossen Robotics. It is a popular low-cost open mobile manipulator in education and research, which makes it a clean fit for a validated nav + manipulation intent layer. This RFC asks whether that is interesting.

## The mapping (URML above the LoCoBot)

URML sits above the robot as a validated intent layer:

- URML's ROS 2 runtime meets the Interbotix stack on its ROS 2 surface; "drive to the shelf and pick up the item" lowers onto a `move_to` (base) plus a `grasp` (the Interbotix arm), the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach grasp or undeclared object before the arm moves.
- The base + arm manifest is a clean, affordable platform example of URML's capability model.

## What is asked

Request for comment from the Interbotix maintainers:

1. Is URML's ROS 2 surface the right seam for a validated-intent layer above a LoCoBot-class rover?
2. What should a URML capability manifest declare to describe an Interbotix mobile manipulator honestly (drive type, arm reach/DOF, gripper + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting for Interbotix's education and research users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) families; the mobile-manipulation anchor (RFC-0422). The Interbotix LoCoBot is the low-cost-platform vertex of the mobile-manipulation wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `Interbotix/interbotix_ros_rovers` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move35.yaml`.
