---
rfc: 0522
title: PDAL integration — request for comment
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

# RFC-0522: PDAL integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`PDAL/PDAL`](https://github.com/PDAL/PDAL) (BSD, ~1.4k stars, active, Hobu Inc. lineage) is the Point Data Abstraction Library, a translation-and-pipeline layer for point-cloud data ("GDAL for point clouds"). For a robot working over a large prior map (a surveyed site, a building scan), PDAL is how that point data is ingested and tiled. URML consumes the resulting spatial model as the declared world a deployment validates intent against. This RFC asks whether the seam is useful.

## The mapping (URML beside PDAL)

- **Ingested point data as the declared site.** PDAL ingests, filters, and tiles large point datasets. A URML deployment over such a site declares its named locations / frames (RFC-0290) and its geofence / occupancy constraints (RFC-0291) against geometry that came through a PDAL pipeline. URML consumes it; PDAL does the ingest.

## What is asked

Request for comment from the PDAL maintainers:

1. Is "PDAL ingests the site point data, URML declares intent / constraints against it" a sensible consumer relationship for robotics over prior maps?
2. Is there a clean product (tiled occupancy, site bounds) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam, and is robotics-over-a-prior-map the right framing for PDAL's audience?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's named locations / frames (RFC-0290) and geofence / occupancy model (RFC-0291). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `PDAL/PDAL` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
