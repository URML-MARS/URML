---
rfc: 0414
title: Crazyswarm2 integration — request for comment
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

# RFC-0414: Crazyswarm2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type, the ROS 2 runtime, and the multi-robot fleet model (RFC-0286).

## Summary

[`IMRCLab/crazyswarm2`](https://github.com/IMRCLab/crazyswarm2) (MIT, ~239 stars, active) is a ROS 2 stack for flying swarms of Bitcraze Crazyflie nano-quadcopters, from the TU Berlin IMRC lab. A swarm of tiny drones is the cleanest possible exercise of URML's fleet model: many identical agents, one coordinated intent. This RFC asks whether a validated intent layer above Crazyswarm2 is interesting.

## The mapping (URML above Crazyswarm2)

URML sits above the swarm stack as a validated intent layer:

- URML's fleet model (RFC-0286) declares a roster of Crazyflies; per-agent `aerial` intent lowers onto the Crazyswarm2 ROS 2 surface, and a barrier coordinates a synchronized maneuver.
- Validate-before-actuate refuses a request outside the declared envelope (arena bounds, altitude, count) before any rotor spins.
- The nano-quad swarm is a high-value teaching and research demonstrator for validated multi-robot intent.

## What is asked

Request for comment from the Crazyswarm2 maintainers:

1. Does URML's fleet model (roster + per-agent intent + barrier) map cleanly onto the Crazyswarm2 ROS 2 surface?
2. What should a URML capability manifest declare to describe a Crazyflie swarm honestly (per-drone drive type, arena geometry, altitude/speed limits, swarm size)?
3. Is a validated natural-language layer interesting for swarm research and teaching?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type; the multi-robot fleet model (RFC-0286); the aerial-autonomy anchor (RFC-0412). Crazyswarm2 is the nano-quad swarm vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `IMRCLab/crazyswarm2` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move34.yaml`.
