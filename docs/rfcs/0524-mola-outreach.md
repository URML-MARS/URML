---
rfc: 0524
title: MOLA integration — request for comment
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

# RFC-0524: MOLA integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`MOLAorg/mola`](https://github.com/MOLAorg/mola) (GPL-3.0 core / BSD foundations, ~945 stars, active, University of Almería) is a modular framework for localization and mapping — LiDAR-inertial SLAM that produces a pose estimate and a map. URML's posture toward SLAM is fixed: it consumes the estimate, it does not compute it. A MOLA estimate is the localized pose and map a URML deployment's frames and constraints are resolved against. This RFC asks whether the seam is useful.

## The mapping (URML beside MOLA)

- **Estimate and map as consumed input.** MOLA produces the robot's pose in a map. URML resolves its frames (RFC-0290) and validates its geofence / occupancy constraints (RFC-0291) against that estimate and map. URML consumes the SLAM output; it does not run the optimization.

## What is asked

Request for comment from the MOLA maintainers:

1. Is "MOLA produces the pose estimate + map, URML resolves frames and validates constraints against it" a sensible consumer relationship?
2. Is there a clean output (pose, map frame, occupancy) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything. (MOLA's core is GPL-3.0; this RFC proposes no code reuse, only a consumer relationship.)

## Prior art / context

URML's frame-transform graph (RFC-0290), geofence / occupancy model (RFC-0291), and the "URML consumes your estimate" posture of the SLAM engagements (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `MOLAorg/mola` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the core is GPL-3.0; state it, do not ask). Tracked in `examples/lighthouses/outreach-move47.yaml`.
