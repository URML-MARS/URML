---
rfc: 0521
title: Point Cloud Library (PCL) integration — request for comment
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

# RFC-0521: Point Cloud Library (PCL) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`PointCloudLibrary/pcl`](https://github.com/PointCloudLibrary/pcl) (BSD, ~11k stars, active) is the canonical library for point-cloud processing in robotics: filtering, segmentation, registration, surface reconstruction. URML consumes the products of that pipeline: the segmented obstacles, surfaces, and occupancy a robot's intent is validated against. This RFC asks whether the seam is useful.

## The mapping (URML beside PCL)

- **Processed point clouds feed the declared world.** PCL turns raw sensor returns into segmented, registered geometry. A URML deployment declares its occupancy / geofence constraints (RFC-0291) and its frames (RFC-0290) against that geometry. URML consumes the processed result as input; the heavy point-cloud math stays in PCL.

## What is asked

Request for comment from the PCL maintainers:

1. Is "PCL processes the point cloud, URML declares intent / constraints against the result" a sensible consumer relationship?
2. Is there a clean product (segmented obstacles, an occupancy proxy) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's occupancy / geofence model (RFC-0291), the frame-transform graph (RFC-0290), and the consume-the-estimate posture (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `PointCloudLibrary/pcl` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
