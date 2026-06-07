---
rfc: 0412
title: Aerostack2 integration — request for comment
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

# RFC-0412: Aerostack2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's shipped `aerial` drive type, the PX4 reference runtime, and the ROS 2 runtime. It is the anchor of the aerial-autonomy wave (Move #34).

## Summary

[`aerostack2/aerostack2`](https://github.com/aerostack2/aerostack2) (BSD-3-Clause, ~351 stars, active) is a ROS 2 framework for autonomous multi-aerial-robot systems from CVAR-UPM. It sits at exactly the altitude URML targets: above the flight controller (PX4, already a URML substrate from Move #16), composing behaviors for one or many drones. This RFC asks whether a validated intent layer above Aerostack2 is interesting.

## The mapping (URML above Aerostack2)

URML sits above the aerial stack as a validated intent layer:

- URML's `aerial` drive type and ROS 2 runtime meet Aerostack2 on its ROS 2 behavior/action surface; "take off, fly the perimeter at 5 m, and inspect" lowers onto Aerostack2 behaviors.
- Validate-before-actuate refuses a request outside the declared flight envelope (altitude ceiling, geofence, speed) before the drone arms.
- Multi-aerial coordination ties URML's fleet model (RFC-0286): a roster of drones with per-agent intent.

## What is asked

Request for comment from the Aerostack2 maintainers:

1. Is URML's ROS 2 behavior-surface mapping the right seam for an external validated-intent layer above Aerostack2?
2. What should a URML capability manifest declare to describe an Aerostack2 aerial platform honestly (drive type, altitude/speed limits, geofence, sensor/payload set, single vs multi-robot)?
3. Is a validated natural-language layer interesting for single-drone and swarm missions?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and PX4 runtime (Move #16 substrate spine); the multi-robot fleet model (RFC-0286). Aerostack2 is the anchor of the aerial-autonomy wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `aerostack2/aerostack2` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move34.yaml`.
