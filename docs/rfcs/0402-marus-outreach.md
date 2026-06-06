---
rfc: 0402
title: MARUS (LABUST) integration — request for comment
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

# RFC-0402: MARUS (LABUST) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[`marus-core`](https://github.com/MARUSimulator/marus-core) (LABUST, University of Zagreb; Apache-2.0, ~27 stars, Issues enabled, active) is the core of MARUS, a Unity-based marine simulator with ROS 2 support via a gRPC adapter. It covers surface and underwater vessels, and it is permissively licensed, so it is a clean seam for a URML demonstration. This RFC asks whether a URML intent layer above MARUS is interesting.

## The mapping (URML above MARUS)

URML sits above the sim's ROS 2 seam as a validated intent layer:

- A URML program drives a MARUS surface or underwater vessel through the ROS 2 (`grpc_ros_adapter`) interface — the same ROS 2 surface URML's runtime already targets.
- URML's `validation` block (RFC-0381) records the simulation-fidelity context; MARUS's marine environment makes the surface/underwater context concrete.
- The hermetic sim-first posture matches URML's own; validate-before-actuate behaves identically in sim and on hardware.

## What is asked

Request for comment from the MARUS / LABUST maintainers:

1. Is a validated natural-language intent layer above MARUS interesting as a demonstration / teaching surface for marine scenarios (surface and underwater)?
2. What should a URML manifest declare to describe a marine vessel honestly (vehicle class, depth rating where applicable, thruster configuration, environmental limits)?
3. Where is the cleanest seam for a URML → MARUS demonstration via the gRPC ROS 2 adapter?

Nothing here asks MARUS to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints); sibling marine sims Stonefish (RFC-0399), DAVE (RFC-0400), HoloOcean (RFC-0401). MARUS is the Unity-based, surface-and-underwater vertex of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `MARUSimulator/marus-core` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move32.yaml`.
