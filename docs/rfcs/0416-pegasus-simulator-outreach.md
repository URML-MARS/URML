---
rfc: 0416
title: Pegasus Simulator integration — request for comment
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

# RFC-0416: Pegasus Simulator integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type, the PX4 reference runtime, and the sim-engagement pattern (RFC-0381).

## Summary

[`PegasusSimulator/PegasusSimulator`](https://github.com/PegasusSimulator/PegasusSimulator) (BSD-3-Clause, ~807 stars, active) is an NVIDIA Isaac Sim framework for multirotor simulation with PX4 integration, from IST Lisbon. It pairs a high-fidelity simulator with the exact flight controller URML already targets, which makes it a natural sim-side home for a validated aerial intent layer. This RFC asks whether a URML layer above Pegasus is interesting.

## The mapping (URML above Pegasus)

URML sits above the simulated aerial platform as a validated intent layer:

- URML's `aerial` drive type and PX4 runtime drive a Pegasus vehicle through PX4 / the ROS 2 bridge inside Isaac Sim; "fly the survey grid at 10 m and return" lowers onto the same PX4 seam URML uses on hardware.
- URML's optional validation block records the simulation-fidelity context concretely (Isaac Sim + Pegasus dynamics).
- Validate-before-actuate refuses an out-of-envelope request before the simulated drone arms.

## What is asked

Request for comment from the Pegasus Simulator maintainers:

1. Is the PX4 / ROS 2 bridge the right seam for an external validated-intent layer above Pegasus, given URML already targets PX4?
2. What should a URML capability manifest declare to describe a Pegasus aerial platform honestly (drive type, altitude/speed limits, geofence, payload/sensor set)?
3. Is a validated natural-language layer interesting as a sim-to-real demonstration surface?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and PX4 runtime (Move #16); the simulation-engagement pattern (RFC-0381); the aerial-autonomy anchor (RFC-0412). Pegasus is the Isaac-Sim + PX4 vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `PegasusSimulator/PegasusSimulator` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move34.yaml`.
