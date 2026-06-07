---
rfc: 0423
title: PAL TIAGo integration — request for comment
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

# RFC-0423: PAL TIAGo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families. It anchors one engagement on the PAL TIAGo robot stack.

## Summary

[`pal-robotics/tiago_robot`](https://github.com/pal-robotics/tiago_robot) (Apache-2.0, ~68 stars, active) is the description and bringup driver stack for PAL Robotics' TIAGo, a widely-used research mobile manipulator (mobile base, lift torso, single arm). PAL also maintains [`tiago_simulation`](https://github.com/pal-robotics/tiago_simulation) (Apache-2.0). This RFC anchors on the robot stack and references the simulation package. A research mobile manipulator is an ideal home for a validated nav + manipulation intent layer.

## The mapping (URML above TIAGo)

URML sits above the robot as a validated intent layer:

- URML's ROS 2 runtime meets TIAGo on its ROS 2 action/service surface; "go to the table and hand me the bottle" lowers onto a `move_to` (base) plus a `grasp` (the arm), the decide-then-do split made concrete.
- Validate-before-actuate refuses an undeclared object or out-of-reach grasp before the arm moves.
- The combined base + torso + arm manifest exercises URML's capability model honestly on a standard research platform.

## What is asked

Request for comment from the TIAGo maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above TIAGo?
2. What should a URML capability manifest declare to describe a TIAGo-class mobile manipulator honestly (drive type, torso lift, arm reach/DOF, gripper + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting for TIAGo's research and education users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) families; the mobile-manipulation anchor (RFC-0422). TIAGo is the standard-research-platform vertex of the mobile-manipulation wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `pal-robotics/tiago_robot` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). The `tiago_simulation` repo is referenced, not posted to separately (org-anchor). Tracked in `examples/lighthouses/outreach-move35.yaml`.
