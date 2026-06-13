---
rfc: 0518
title: Nerfstudio integration — request for comment
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

# RFC-0518: Nerfstudio integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It is the anchor of the perception / SLAM / mapping / reconstruction wave (Move #47). The wave's posture is consistent: URML *consumes* a map or estimate as input to its capability manifest and safety envelope; it does not produce one.

## Summary

[`nerfstudio-project/nerfstudio`](https://github.com/nerfstudio-project/nerfstudio) (Apache-2.0, ~11.7k stars, UC Berkeley collaborative) is a studio for NeRFs, and its sibling [`nerfstudio-project/gsplat`](https://github.com/nerfstudio-project/gsplat) (Apache-2.0, ~5.2k stars) is a CUDA gaussian-splatting rasterizer. They produce dense 3D scene reconstructions. URML is interesting as a consumer of such a reconstruction: a map asset a robot navigates and is geofenced against. This RFC (one note for the org, covering both repos) asks whether the seam is useful.

## The mapping (URML beside Nerfstudio / gsplat)

- **A reconstruction as a declared map.** A nerfstudio / gsplat reconstruction of an environment is the spatial model a URML deployment can declare as its map: named locations and frames (RFC-0290) and geofence / occupancy constraints in the safety envelope reference geometry that came from the reconstruction. URML does not build the scene; it consumes it as the declared world a validated intent is checked against.
- **Clean division.** URML stays the declarative intent + envelope layer; nerfstudio / gsplat stay the reconstruction tooling.

## What is asked

Request for comment from the Nerfstudio maintainers:

1. Is "a nerfstudio / gsplat reconstruction is the declared map a URML deployment validates intent against" a sensible consumer relationship?
2. Is there a clean export (poses, scene bounds, a mesh / occupancy proxy) a robot deployment would want to feed a capability manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's frame-transform graph and named locations (RFC-0290), the safety-envelope geofence / occupancy model (RFC-0291), and the consume-the-estimate posture of the SLAM engagements (Move #25). Anchor of Move #47.

## Implementation note

Outreach only. The post is a single GitHub Issue on `nerfstudio-project/nerfstudio` (referencing gsplat) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
