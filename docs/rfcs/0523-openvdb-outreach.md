---
rfc: 0523
title: OpenVDB integration — request for comment
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

# RFC-0523: OpenVDB integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`AcademySoftwareFoundation/openvdb`](https://github.com/AcademySoftwareFoundation/openvdb) (Apache-2.0, ~3.3k stars, active, Academy Software Foundation / Linux Foundation) is a sparse-volume data structure and toolset, increasingly used in robotics for volumetric / occupancy maps. URML consumes an occupancy representation as the world its safety envelope is defined against. This RFC asks whether the seam is useful.

## The mapping (URML beside OpenVDB)

- **A sparse volume as the declared occupancy.** An OpenVDB grid is a memory-efficient occupancy / distance-field representation of an environment. URML's safety envelope declares occupancy and geofence constraints (RFC-0291); an OpenVDB grid is exactly the kind of map those constraints can be checked against. URML consumes the volume as the declared world; OpenVDB is the volumetric data structure.

## What is asked

Request for comment from the OpenVDB maintainers:

1. Is "an OpenVDB grid is the declared occupancy a URML deployment validates intent against" a sensible consumer relationship for the robotics use of OpenVDB?
2. Is there a clean way a robot deployment would reference a VDB occupancy / distance field from a URML safety envelope?
3. Which is the cleaner first seam, and is robotics-occupancy the right framing for OpenVDB's audience (vs VFX)?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's occupancy / geofence safety-envelope model (RFC-0291) and the frame-transform graph (RFC-0290). Part of Move #47. (OpenVDB is an ASF / Linux Foundation project, foundation-home altitude.)

## Implementation note

Outreach only. The post is a GitHub Issue on `AcademySoftwareFoundation/openvdb` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
