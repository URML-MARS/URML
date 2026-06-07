---
rfc: 0421
title: XTDrone integration — request for comment
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

# RFC-0421: XTDrone integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type, the PX4 reference runtime, and the sim-engagement pattern (RFC-0381). Tier B.

## Summary

[`robin-shaun/XTDrone`](https://github.com/robin-shaun/XTDrone) (MIT, ~1.7k stars) is a PX4 + ROS + Gazebo UAV simulation platform from Peking University, widely used as a teaching and prototyping sandbox. It pairs ROS and the exact flight controller URML targets, which makes it a convenient sim home for a validated aerial intent layer. This RFC asks whether that is interesting.

## The mapping (URML above XTDrone)

URML sits above the simulated platform as a validated intent layer:

- URML's `aerial` drive type and PX4 runtime drive an XTDrone vehicle through PX4 / the ROS bridge in Gazebo; "take off, fly the waypoints, and land" lowers onto the same PX4 seam URML uses on hardware.
- URML's optional validation block records the simulation-fidelity context a run was checked in.
- Validate-before-actuate refuses an out-of-envelope request before the simulated drone arms.

## What is asked

Request for comment from the XTDrone maintainers:

1. Is the PX4 / ROS bridge the right seam for an external validated-intent layer above XTDrone?
2. What should a URML capability manifest declare to describe an XTDrone aerial platform honestly (drive type, altitude/speed limits, sensor set, single vs multi)?
3. Is a validated natural-language layer interesting as a teaching surface?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and PX4 runtime (Move #16); the simulation-engagement pattern (RFC-0381); the aerial-autonomy anchor (RFC-0412). XTDrone is the PX4 + Gazebo teaching-sim vertex of the aerial wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `robin-shaun/XTDrone` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move34.yaml`.
