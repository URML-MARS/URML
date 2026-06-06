---
rfc: 0399
title: Stonefish integration — request for comment from the Stonefish maintainer
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

# RFC-0399: Stonefish integration — request for comment from the Stonefish maintainer

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainer for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[Stonefish](https://github.com/patrykcieslak/stonefish) (GPL-3.0, ~256 stars, Issues enabled, active — ICRA 2025 release) is an advanced C++ marine-robotics simulation library with a ROS 2 package (`stonefish_ros`). It is a high-fidelity underwater environment where a URML-validated command can drive a vehicle before any hardware is involved. This RFC asks whether a URML demonstration on Stonefish is interesting and what an underwater deployment should declare.

## The mapping (URML above Stonefish)

URML sits above the sim's ROS 2 interface as a validated intent layer:

- A URML program drives a Stonefish vehicle through `stonefish_ros` — the same ROS 2 surface URML's runtime already targets. The hermetic, sim-first posture matches URML's own (its mock substrate proves the language end to end with no hardware).
- URML's `validation` block (RFC-0381) records the simulation-fidelity context a deployment was checked in; Stonefish's hydrodynamics make the underwater context concrete (buoyancy, drag, currents).
- Validate-before-actuate refuses an out-of-envelope request in sim exactly as it would on hardware, so the sim is a faithful rehearsal of the real validation path.

## What is asked

Request for comment from the Stonefish maintainer:

1. Is a validated natural-language intent layer above Stonefish interesting as a demonstration / teaching surface for underwater scenarios?
2. What should a URML manifest declare to describe an underwater deployment honestly (depth rating, buoyancy/ballast, thruster configuration, current and visibility limits)?
3. Where is the cleanest seam for a URML → Stonefish demonstration via `stonefish_ros`?

Nothing here asks Stonefish to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints, from the Move #24 sim wave); the marine vehicle stacks `blue` (RFC-0396) and orca4 (RFC-0397) that a Stonefish scenario would exercise.

## Implementation note

Outreach only. The post is a GitHub Issue on `patrykcieslak/stonefish` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (the repo is GPL-3.0; URML integrates over the ROS 2 surface and ships nothing under that license). Tracked in `examples/lighthouses/outreach-move32.yaml`.
