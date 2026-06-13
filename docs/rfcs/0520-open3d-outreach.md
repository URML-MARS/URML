---
rfc: 0520
title: Open3D integration — request for comment
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

# RFC-0520: Open3D integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`isl-org/Open3D`](https://github.com/isl-org/Open3D) (MIT-style, ~13.7k stars, active, Intel Intelligent Systems Lab) is a modern library for 3D data processing (point clouds, meshes, registration, reconstruction). URML consumes the spatial products such a library yields: the occupancy, surfaces, and registered point clouds that define the world a robot's intent is validated against. This RFC asks whether the seam is useful.

## The mapping (URML beside Open3D)

- **3D products feed the declared world.** Open3D's point clouds / meshes / reconstructions are the geometry a URML deployment declares its occupancy and geofence constraints against (RFC-0291), and its frames against (RFC-0290). URML consumes that geometry as input; it does not process the point clouds itself.

## What is asked

Request for comment from the Open3D maintainers:

1. Is "Open3D produces the 3D geometry, URML declares intent / constraints against it" a sensible consumer relationship?
2. Is there a clean product (an occupancy grid, a mesh, scene bounds) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's occupancy / geofence safety-envelope model (RFC-0291), the frame-transform graph (RFC-0290), and the consume-the-estimate posture (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `isl-org/Open3D` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
