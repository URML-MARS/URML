---
rfc: 0525
title: MRPT integration — request for comment
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

# RFC-0525: MRPT integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`MRPT/mrpt`](https://github.com/MRPT/mrpt) (BSD-3-Clause, ~2.1k stars, active) is the Mobile Robot Programming Toolkit: mapping, localization, and sensor-fusion libraries with a long robotics history. URML consumes the localization and maps MRPT produces as the world a deployment validates intent against. This RFC asks whether the seam is useful.

## The mapping (URML beside MRPT)

- **Localization and maps as consumed input.** MRPT yields a pose estimate and occupancy / metric maps. URML resolves its frames (RFC-0290) and validates its geofence / occupancy constraints (RFC-0291) against that. URML consumes the estimate; MRPT does the localization and mapping.

## What is asked

Request for comment from the MRPT maintainers:

1. Is "MRPT localizes and maps, URML resolves frames and validates constraints against it" a sensible consumer relationship?
2. Is there a clean output (pose, occupancy grid, map frame) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's frame-transform graph (RFC-0290), geofence / occupancy model (RFC-0291), and the "URML consumes your estimate" posture (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `MRPT/mrpt` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
