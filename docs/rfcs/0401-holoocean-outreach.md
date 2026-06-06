---
rfc: 0401
title: HoloOcean integration — request for comment from the HoloOcean maintainers
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

# RFC-0401: HoloOcean integration — request for comment from the HoloOcean maintainers

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-fidelity manifest hints ([RFC-0381](0381-simulation-fidelity-manifest-hints.md)).

## Summary

[`holoocean-ros`](https://github.com/byu-holoocean/holoocean-ros) (BYU, MIT, ~40 stars, Issues enabled, fresh release) is the ROS 2 bridge for HoloOcean, a UE5-based underwater robotics simulator (HoloOcean 2.0 adds ROS 2 and Fossen vehicle dynamics). It is the permissively-licensed, engageable seam onto a high-fidelity underwater sim where a URML-validated command can drive a simulated AUV. This RFC asks whether a URML demonstration via the bridge is interesting.

## The mapping (URML above HoloOcean)

URML sits above the bridge as a validated intent layer:

- A URML program drives a HoloOcean AUV through `holoocean-ros` — the same ROS 2 surface URML's runtime already targets; the UE5 sim core stays where it is.
- URML's `validation` block (RFC-0381) records the simulation-fidelity context the deployment was checked in; HoloOcean's Fossen dynamics and sonar/imaging models make the underwater context concrete.
- Validate-before-actuate behaves identically in sim and on hardware, so the bridge is a faithful rehearsal of the real validation path.

## What is asked

Request for comment from the HoloOcean maintainers:

1. Is a validated natural-language intent layer above HoloOcean interesting as a demonstration / teaching surface for underwater scenarios?
2. What should a URML manifest declare to describe a HoloOcean AUV honestly (depth rating, dynamics class, sensor suite, current limits)?
3. Where is the cleanest seam for a URML → HoloOcean demonstration via `holoocean-ros`?

Nothing here asks HoloOcean to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; RFC-0381 (`validation` simulation-fidelity hints); sibling marine sims Stonefish (RFC-0399), DAVE (RFC-0400), MARUS (RFC-0402). HoloOcean is the UE5-fidelity underwater-sim vertex of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `byu-holoocean/holoocean-ros` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move32.yaml`.
