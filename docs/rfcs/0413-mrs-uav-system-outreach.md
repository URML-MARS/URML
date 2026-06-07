---
rfc: 0413
title: MRS UAV System (CTU Prague) integration — request for comment
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

# RFC-0413: MRS UAV System (CTU Prague) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type, the PX4 reference runtime, and the ROS 2 runtime.

## Summary

[`ctu-mrs/mrs_uav_system`](https://github.com/ctu-mrs/mrs_uav_system) (BSD-3-Clause, ~605 stars, active) is a full multi-UAV control, estimation, and simulation platform from the CTU Prague Multi-Robot Systems group — one of the most complete open aerial-autonomy stacks, deployed on real outdoor multi-drone experiments. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above the MRS UAV System)

URML sits above the aerial stack as a validated intent layer:

- URML's `aerial` drive type and ROS 2 runtime meet the MRS UAV manager on its ROS 2 control/tracker surface; "fly to this GPS point at 3 m/s and hold" lowers onto the trajectory/reference interface.
- Validate-before-actuate refuses a request outside the declared altitude/speed/area envelope before the drone arms.
- The MRS system's strength is real multi-UAV deployment, which ties URML's fleet model (RFC-0286): a roster with per-drone intent and a barrier for coordinated maneuvers.

## What is asked

Request for comment from the MRS UAV System maintainers:

1. Is the ROS 2 control/tracker surface the right seam for an external validated-intent layer, or is the mission/manager level a better fit?
2. What should a URML capability manifest declare to describe an MRS-class UAV honestly (drive type, control modes, altitude/speed limits, geofence, estimator/positioning, single vs multi)?
3. Is a validated natural-language layer interesting for the group's outdoor multi-UAV work?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and PX4 runtime (Move #16); the multi-robot fleet model (RFC-0286); the aerial-autonomy anchor (RFC-0412). The MRS UAV System is the full-platform vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `ctu-mrs/mrs_uav_system` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move34.yaml`.
