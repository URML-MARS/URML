---
rfc: 0427
title: TidyBot ROS (ROAHM Lab) integration — request for comment
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

# RFC-0427: TidyBot ROS (ROAHM Lab) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families. Tier B.

## Summary

[`roahmlab/tidybot_ros`](https://github.com/roahmlab/tidybot_ros) (MIT, ~29 stars, active) is a ROS 2 interface and imitation-learning pipeline for the TidyBot++ mobile manipulator, from the ROAHM Lab at the University of Michigan. Where the upstream TidyBot++ (RFC-0424) is the hardware + learning project, this is its ROS 2 stack — the exact surface URML's runtime targets. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above TidyBot ROS)

URML sits above the ROS 2 stack as a validated intent layer:

- URML's ROS 2 runtime meets `tidybot_ros` on its ROS 2 action/service surface; a "tidy this area" intent lowers onto a `move_to` (holonomic base) plus `grasp`/`release` cycles, the decide-then-do split made concrete.
- Where the pipeline trains/deploys a learned policy, URML wraps it in a validated envelope (decide-then-do applied to learning).
- Validate-before-actuate refuses an out-of-capability request before dispatch.

## What is asked

Request for comment from the TidyBot ROS maintainers:

1. Does URML's typed intent map cleanly onto the `tidybot_ros` ROS 2 surface, and where should it target it?
2. What should a URML capability manifest declare to describe a holonomic mobile manipulator in ROS 2 honestly (drive type, arm reach/DOF, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the lab's mobile-manipulation work?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the upstream TidyBot++ engagement (RFC-0424); the decide-then-do split applied to learned control; the mobile-manipulation anchor (RFC-0422). TidyBot ROS is the ROS 2 + university-lab vertex of the mobile-manipulation wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `roahmlab/tidybot_ros` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move35.yaml`.
