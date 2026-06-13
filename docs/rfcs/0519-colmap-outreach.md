---
rfc: 0519
title: COLMAP integration — request for comment
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

# RFC-0519: COLMAP integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`colmap/colmap`](https://github.com/colmap/colmap) (BSD, ~11.9k stars, active, ETH Zurich + UNC) is a Structure-from-Motion and Multi-View Stereo pipeline. It produces camera poses and 3D reconstructions. URML is a consumer of that output: the reconstruction and its frames are the spatial model a robot's capability manifest and safety envelope are defined against. This RFC asks whether the seam is useful.

## The mapping (URML beside COLMAP)

- **Poses and reconstruction as declared geometry.** A COLMAP reconstruction gives camera poses and a 3D model. A URML deployment declares its frames (RFC-0290) and geofence / occupancy constraints against geometry that can come from exactly such a reconstruction. URML consumes the reconstruction as the world an intent is validated in; it does not compute the structure.

## What is asked

Request for comment from the COLMAP maintainers:

1. Is "a COLMAP reconstruction is the declared geometry a URML deployment validates intent against" a sensible consumer relationship?
2. Is there a clean output (poses, model bounds) a robot deployment would feed a capability manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's frame-transform graph (RFC-0290), the safety-envelope geofence model (RFC-0291), and the consume-the-estimate posture of the SLAM engagements (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `colmap/colmap` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
