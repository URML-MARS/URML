---
rfc: 0406
title: CropCraft (Romea) integration — request for comment
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

# RFC-0406: CropCraft (Romea) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[CropCraft](https://github.com/Romea/cropcraft) (Apache-2.0, ~106 stars, Issues enabled, active) is a procedural 3D crop-field world generator for robotics simulation (Blender backend, LiDAR/camera ground truth). It is the strongest open ag-sim target by stars and license, and the Romea group is an active French ag-robotics middleware community. It is a sim environment a URML-validated command can drive a field robot into before any hardware. This RFC asks whether a URML demonstration on CropCraft fields is interesting.

## The mapping (URML above a CropCraft world)

URML sits above the sim as a validated intent layer:

- A URML field-robot program (drive rows, detect, measure, report) runs against a CropCraft-generated world through the ROS 2 surface URML's runtime already targets.
- URML's `validation` block (RFC-0381) records the simulation-fidelity context a deployment was checked in; CropCraft's procedural crop fields and ground-truth sensors make the agricultural context concrete.
- The hermetic, sim-first posture matches URML's own (its mock substrate proves the language end to end with no hardware); CropCraft is the high-fidelity field counterpart.

## What is asked

Request for comment from the Romea / CropCraft maintainers:

1. Is a validated natural-language intent layer above CropCraft interesting as a demonstration / teaching surface for field-robot scenarios?
2. What should a URML manifest declare to describe a field-robot deployment honestly (drive type, row/area geometry, implement set, crop vocabulary, GNSS)?
3. Where is the cleanest seam for a URML → CropCraft demonstration via ROS 2, and is the broader Romea middleware a natural integration point?

Nothing here asks CropCraft to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints, from the Move #24 sim wave); the agriculture platforms (FarmBot RFC-0404, Amiga RFC-0405) a CropCraft scenario would exercise. CropCraft is the field-simulation vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `Romea/cropcraft` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move33.yaml`.
