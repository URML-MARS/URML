---
rfc: 0468
title: rviz_visual_tools integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0468: rviz_visual_tools integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail and its capability/envelope manifest. Tier B.

## Summary

[`PickNikRobotics/rviz_visual_tools`](https://github.com/PickNikRobotics/rviz_visual_tools) (BSD-3-Clause, ~814 stars, active) is a C++ helper API to publish shapes, meshes, and markers to RViz. URML is interesting to it as a *thing worth drawing*: a validated intent and its declared safety envelope are spatial (a target pose, a workspace bound, a geofence, a no-go region), and rviz_visual_tools is the standard way to render exactly those as markers next to the robot. This RFC asks whether visualizing validated intent + envelope is interesting.

## The mapping (URML intent + envelope drawn via rviz_visual_tools)

URML sits beside, not below, the marker helper:

- A URML runtime could use rviz_visual_tools to draw what it just validated: the target pose of a `move_to`, the declared workspace bounds, a geofence polygon, the planned trajectory of a `plan_path` — the spatial side of the audit trail.
- A refused intent could be drawn distinctly (e.g. the out-of-envelope pose in red), making validate-before-actuate visible in the same RViz scene as the robot.

## What is asked

Request for comment from the rviz_visual_tools maintainers:

1. Is drawing a validated intent's target/envelope (pose, workspace bound, geofence, trajectory) a natural use of rviz_visual_tools?
2. Are the existing marker primitives sufficient, or would a small "intent/envelope" helper layer be worth it?
3. Any conventions for distinguishing accepted vs. refused intent visually?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability/envelope manifest (geofences, workspace bounds) and the `plan_path` trajectory (RFC-0020); the audit trail; the Lichtblick anchor (RFC-0463). rviz_visual_tools is the in-RViz spatial-marker vertex of the developer-tooling wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `PickNikRobotics/rviz_visual_tools` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move40.yaml`.
