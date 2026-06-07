---
rfc: 0438
title: igus iRC_ROS integration — request for comment
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

# RFC-0438: igus iRC_ROS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile. Tier B.

## Summary

[`CommonplaceRobotics/iRC_ROS`](https://github.com/CommonplaceRobotics/iRC_ROS) (Apache-2.0, ~22 stars, active) is the ROS 2 stack for igus Robot Control, including the low-cost igus ReBeL cobot. A low-cost, permissively-licensed arm with a vendor-maintained ROS 2 stack is an accessible home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above iRC_ROS)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `iRC_ROS` on its ROS 2 action/service surface (and `ros2_control` controllers); a `pick_from` / `place_at` / `grasp` lowers onto the igus driver interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.
- The ReBeL manifest (reach, payload, joint limits, gripper, graspable classes) is a clean, low-cost example of URML's industrial-profile model.

## What is asked

Request for comment from the iRC_ROS maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above iRC_ROS?
2. What should a URML capability manifest declare to describe an igus ReBeL-class arm honestly (reach/DOF, payload, joint limits, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the igus ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). igus iRC_ROS is the low-cost-cobot vertex of the arm-driver wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `CommonplaceRobotics/iRC_ROS` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move36.yaml`.
