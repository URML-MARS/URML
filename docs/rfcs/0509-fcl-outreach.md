---
rfc: 0509
title: FCL (Flexible Collision Library) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0509: FCL (Flexible Collision Library) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. **Completes** the middleware / control / drivers wave (Move #45).

## Summary

[`flexible-collision-library/fcl`](https://github.com/flexible-collision-library/fcl) (BSD-3-Clause, ~1.7k stars, active, Willow Garage / OSRF heritage) is a widely-used collision and distance-query library. URML declares clearances and spatial constraints in its safety envelope; it does not compute geometry. FCL is exactly the kind of library a runtime uses downstream to *check* the constraints URML declares. This RFC asks whether describing that relationship is useful.

## The mapping (URML beside FCL)

- **URML declares, FCL checks.** A URML safety envelope declares clearance volumes and spatial constraints (lateral footprint, vertical band; the deconfliction model in RFC-0291). When a runtime needs to verify a motion or a fleet separation against actual geometry, FCL's collision/distance queries are the computation behind that check. URML is the declarative constraint; FCL is the geometric test.
- **A clean division of labor.** URML stays a static, auditable declaration layer; the heavy geometric query stays in a dedicated library. Naming the seam lets a runtime author know where each half lives.

## What is asked

Request for comment from the FCL maintainers:

1. Is "URML declares the clearance / spatial constraint, FCL is the geometric query that enforces it" an accurate and useful division of labor?
2. Is this the right altitude to describe (a collision library), or is the seam better drawn at a planner / MoveIt-style layer that already wraps FCL?
3. Which first seam, if any, is worth pursuing?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's safety-envelope clearance / deconfliction model (RFC-0291, geometric cross-robot separation) and the motion-planning engagements (Move #26). FCL is the geometric-query layer beneath much of that ecosystem. Completes Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `flexible-collision-library/fcl` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
