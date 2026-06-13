---
rfc: 0527
title: Patchwork++ integration — request for comment
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

# RFC-0527: Patchwork++ integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`url-kaist/patchwork-plusplus`](https://github.com/url-kaist/patchwork-plusplus) (BSD-2-Clause, ~1k stars, active, KAIST Urban Robotics Lab) is a fast, robust ground-segmentation method for 3D LiDAR scans. It is a perception pre-processing step: separating ground from obstacles feeds the occupancy a robot reasons about. URML consumes that occupancy as the world its constraints are checked against. This RFC asks whether the seam is useful.

## The mapping (URML beside Patchwork++)

- **Segmentation feeds the declared occupancy.** Patchwork++ turns a raw LiDAR scan into ground vs non-ground, which downstream becomes the obstacle / occupancy model. URML's geofence / occupancy constraints (RFC-0291) are validated against that model. URML consumes the result; Patchwork++ does the segmentation.

## What is asked

Request for comment from the Patchwork++ maintainers:

1. Is "Patchwork++ segments the scan, URML validates intent against the resulting occupancy" a sensible (if indirect) consumer relationship?
2. Is this the right altitude to engage (a segmentation step), or is the seam better at a mapping layer that consumes Patchwork++?
3. Which first seam, if any, is worth pursuing?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's geofence / occupancy safety-envelope model (RFC-0291) and the "URML consumes your estimate" posture (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `url-kaist/patchwork-plusplus` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
