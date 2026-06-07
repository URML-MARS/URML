---
rfc: 0456
title: SDFormat integration — request for comment
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

# RFC-0456: SDFormat integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats.

## Summary

[`gazebosim/sdformat`](https://github.com/gazebosim/sdformat) (Apache-2.0, ~214 stars) is the parser and specification for SDFormat, the XML description format for robots and worlds used across the Gazebo ecosystem. SDFormat describes a robot's structure; URML's *capability manifest* describes what a robot is allowed and able to do, plus a safety envelope. These are adjacent, and the boundary between them is a genuine design question. This RFC asks the SDFormat maintainers where that boundary should sit.

## The mapping (URML manifest alongside SDFormat)

URML's manifest sits alongside the SDFormat description:

- An SDFormat file carries links, joints, limits, sensors, physics; a URML manifest carries capabilities (drive type, reach, payload, gripper, graspable classes) and a safety envelope. Some manifest fields could be derived or cross-checked from SDFormat.
- URML's validator could consume an SDFormat model to bootstrap or sanity-check a manifest.
- The split: SDFormat says what the robot and world *are*; the URML manifest says what the robot is *allowed and able to do*.

## What is asked

Request for comment from the SDFormat maintainers:

1. Which URML capability-manifest fields map cleanly onto SDFormat elements, and which are genuinely outside SDFormat's scope (payload limits, graspable classes, safety envelope)?
2. Is there appetite for a capability/safety layer that references an SDFormat model rather than duplicating it?
3. Where should the boundary sit between robot *description* (SDFormat) and robot *capability + safety* declaration (URML)?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the robot-description anchor (RFC-0455). SDFormat is the SDF-format vertex of the robot-description wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `gazebosim/sdformat` (Discussions via Gazebo Discourse; engaging the repo Issue here) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move39.yaml`.
