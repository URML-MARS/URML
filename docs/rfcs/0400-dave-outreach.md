---
rfc: 0400
title: DAVE (IOES-Lab) integration — request for comment
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

# RFC-0400: DAVE (IOES-Lab) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[DAVE](https://github.com/IOES-Lab/dave) (IOES-Lab, Apache-2.0, ~43 stars, Issues enabled, active — the ROS 2 / Gazebo Harmonic continuation of Project DAVE) is an open underwater simulation and test environment for AUVs and manipulators. It is a permissively-licensed underwater sim where a URML-validated command can drive a vehicle via the ROS 2 bridge. This RFC asks whether a URML demonstration on DAVE is interesting and what an underwater deployment should declare.

## The mapping (URML above DAVE)

URML sits above the sim's ROS 2 interface as a validated intent layer:

- A URML program drives a DAVE vehicle through its ROS 2 / Gazebo interface — the same ROS 2 surface URML's runtime already targets. The sim-first, hermetic posture matches URML's own.
- URML's `validation` block (RFC-0381) records the simulation-fidelity context; DAVE's underwater environment and sensor models make that concrete.
- Validate-before-actuate behaves identically in sim and on hardware, so a DAVE scenario faithfully rehearses the real validation path.

## What is asked

Request for comment from the IOES-Lab DAVE maintainers:

1. Is a validated natural-language intent layer above DAVE interesting as a demonstration / test surface for underwater scenarios?
2. What should a URML manifest declare to describe an underwater deployment honestly (depth rating, buoyancy, thruster configuration, current/visibility limits)?
3. Where is the cleanest seam for a URML → DAVE demonstration via the ROS 2 / Gazebo bridge?

Nothing here asks DAVE to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints); the active IOES-Lab fork is the live continuation of Project DAVE (the original Field-Robotics-Lab repo is stale). Sibling marine sims in this wave: Stonefish (RFC-0399), HoloOcean (RFC-0401), MARUS (RFC-0402).

## Implementation note

Outreach only. The post is a GitHub Issue on `IOES-Lab/dave` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move32.yaml`.
