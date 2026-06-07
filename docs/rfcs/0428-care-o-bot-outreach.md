---
rfc: 0428
title: Care-O-bot (Fraunhofer IPA) integration — request for comment
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

# RFC-0428: Care-O-bot (Fraunhofer IPA) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families. Tier B.

## Summary

[`ipa320/cob_robots`](https://github.com/ipa320/cob_robots) (Apache-2.0, ~67 stars) is the hardware-configuration and bringup stack for Care-O-bot, Fraunhofer IPA's long-running service mobile manipulator (omnidirectional base, torso, arm(s), sensor head). Care-O-bot is one of the original open service-robot platforms, and its design target — assistive tasks in human environments — is exactly the kind of work a validated intent layer is for. This RFC asks whether that is interesting.

## The mapping (URML above Care-O-bot)

URML sits above the robot as a validated intent layer:

- URML's ROS 2 runtime meets the `cob` stack on its ROS surface; "fetch the bottle from the kitchen and bring it here" lowers onto a `move_to` (the omnidirectional base) plus a `grasp` (the arm), the decide-then-do split made concrete.
- Validate-before-actuate refuses an undeclared object or out-of-reach grasp before the arm moves, which matters for assistive tasks around people.
- The base + torso + arm + head manifest is a thorough test of URML's capability model.

## What is asked

Request for comment from the Care-O-bot / Fraunhofer IPA maintainers:

1. Is URML's ROS surface the right seam for a validated-intent layer above Care-O-bot?
2. What should a URML capability manifest declare to describe a Care-O-bot-class service manipulator honestly (drive type, torso, arm reach/DOF, gripper + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting for assistive / service-robot research?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) families; the mobile-manipulation anchor (RFC-0422). Care-O-bot is the assistive-service-robot vertex of the mobile-manipulation wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `ipa320/cob_robots` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move35.yaml`.
