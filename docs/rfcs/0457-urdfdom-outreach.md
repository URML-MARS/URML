---
rfc: 0457
title: URDF tooling (urdfdom) integration — request for comment
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

# RFC-0457: URDF tooling (urdfdom) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats. It anchors one engagement on the URDF tooling cluster via `urdfdom`.

## Summary

[`ros/urdfdom`](https://github.com/ros/urdfdom) (BSD-3-Clause, ~130 stars) is the core C++ parser and data structures for URDF, the most widely-used robot description format, with sibling tooling ([`urdfdom_headers`](https://github.com/ros/urdfdom_headers), [`xacro`](https://github.com/ros/xacro), [`robot_state_publisher`](https://github.com/ros/robot_state_publisher)). URDF describes a robot's structure; URML's *capability manifest* describes what a robot is allowed and able to do, plus a safety envelope. This RFC anchors on urdfdom and references the sibling tooling, asking how a capability+safety manifest should relate to URDF.

## The mapping (URML manifest alongside URDF)

URML's manifest sits alongside the URDF description:

- A URDF (parsed by urdfdom, generated via xacro) carries links, joints, limits, geometry; a URML manifest carries capabilities and a safety envelope. Some manifest fields (reach, DOF, joint/speed limits) could be derived or cross-checked from URDF.
- URML's validator could consume a urdfdom-parsed model to bootstrap or sanity-check a manifest, keeping description and capability declaration from drifting.
- The split: URDF says what the robot *is*; the URML manifest says what it is *allowed and able to do*.

## What is asked

Request for comment from the URDF tooling maintainers:

1. Which URML capability-manifest fields can be derived honestly from URDF, and which are genuinely separate (payload limits, graspable classes, safety envelope)?
2. Would a thin adapter from a urdfdom-parsed model to a URML manifest skeleton be useful?
3. Where should the boundary sit between robot *description* (URDF) and robot *capability + safety* declaration (URML)?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the robot-description anchor (RFC-0455). URDF tooling (urdfdom) is the URDF-format vertex of the robot-description wave; the sibling repos are referenced, not posted to separately (anchor-plus-fold).

## Implementation note

Outreach only. The post is a GitHub Issue on `ros/urdfdom` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). `urdfdom_headers`, `xacro`, and `robot_state_publisher` are referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move39.yaml`.
