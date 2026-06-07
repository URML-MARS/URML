---
rfc: 0429
title: PR2 (community) integration — request for comment
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

# RFC-0429: PR2 (community) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and its navigation + manipulation primitive families. Tier B.

## Summary

[`PR2/pr2_robot`](https://github.com/PR2/pr2_robot) (BSD, per-package, ~59 stars) is the community-maintained bringup/robot stack for the PR2, the dual-arm mobile manipulator that defined the "go fetch the mug" demo and seeded much of the modern ROS manipulation ecosystem. PR2 is the canonical reference for exactly the task URML describes: a natural-language request that combines navigation and manipulation. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above PR2)

URML sits above the robot as a validated intent layer:

- URML's ROS runtime meets the `pr2` stack on its ROS surface; "go to the table and pick up the mug" lowers onto a `move_to` (the base) plus a `grasp` (an arm), the decide-then-do split — the very demo PR2 is known for.
- A two-armed platform exercises URML's bimanual manipulation work (RFC-0010): an `arm` selector and a `bimanual` primitive.
- Validate-before-actuate refuses an out-of-reach grasp or undeclared object before an arm moves.

## What is asked

Request for comment from the PR2 community maintainers:

1. Is URML's ROS surface the right seam for a validated-intent layer above PR2?
2. What should a URML capability manifest declare to describe a PR2-class dual-arm mobile manipulator honestly (drive type, two arms + reach/DOF, grippers + graspable classes, navigation bounds)?
3. Is a validated natural-language layer interesting for the platforms still running PR2 in research and teaching?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS runtime; the `move_to` (Move #16) and `grasp` / manipulation (Move #27) families; the bimanual manipulation work (RFC-0010); the mobile-manipulation anchor (RFC-0422). PR2 is the canonical-reference vertex of the mobile-manipulation wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `PR2/pr2_robot` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD). Tracked in `examples/lighthouses/outreach-move35.yaml`.
