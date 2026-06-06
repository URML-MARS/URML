---
rfc: 0405
title: farm-ng Amiga integration — request for comment from the farm-ng community
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0405: farm-ng Amiga integration — request for comment from the farm-ng community

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its community for feedback. It builds on URML's ROS 2 runtime and validate-before-actuate discipline.

## Summary

[farm-ng's Amiga dev kit](https://github.com/farm-ng/amiga-dev-kit) (~24 stars, Issues + Discussions enabled, active) is the open developer surface for the Amiga, a rugged commercial agricultural micro-tractor / rover, exposing gRPC and ROS bridges. It is a commercial-but-open ag mobile platform — exactly the kind of substrate a validated natural-language intent layer should sit above. This RFC asks the farm-ng community whether that is interesting and what an ag-rover manifest should declare.

## The mapping (URML above Amiga)

URML sits above the Amiga as a validated intent layer; the Amiga executes:

- A URML drive / navigation intent ("drive the east row at 1 m/s and record") lowers onto the Amiga's gRPC + ROS bridge — the ROS side meets URML's ROS 2 runtime directly, and the gRPC side is a clean binding target.
- Validate-before-actuate refuses a request outside the declared speed, area, or implement envelope before the rover moves — useful on a heavy outdoor platform.
- The capability-manifest question (what a field rover must declare: drive type, speed/turn limits, implement/PTO interfaces, GNSS/positioning, field boundaries) is a genuine design question for the farm-ng team.

## What is asked

Request for comment from the farm-ng community:

1. Is the ROS bridge or the gRPC surface the better seam for an external validated-intent layer above the Amiga?
2. What should a URML capability manifest declare to describe an Amiga-class ag rover honestly (drive type, speed/turn limits, implement interfaces, GNSS/positioning, field-boundary / geofence constraints)?
3. Is a validated natural-language intent layer interesting for Amiga developers?

Nothing here asks farm-ng to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime and the Nav2 engagement (Move #16) for outdoor navigation; the `call_program` binding (RFC-0015) for the gRPC side. The Amiga is the commercial-open mobile-platform vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `farm-ng/amiga-dev-kit` (Discussions enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask. Tracked in `examples/lighthouses/outreach-move33.yaml`.
