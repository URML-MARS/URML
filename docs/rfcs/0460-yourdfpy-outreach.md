---
rfc: 0460
title: yourdfpy integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0460: yourdfpy integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats. Tier B.

## Summary

[`clemense/yourdfpy`](https://github.com/clemense/yourdfpy) (MIT, ~286 stars, active) is a clean Python URDF parser and visualizer. URML's reference tooling is Python, so a permissive Python URDF parser is the most natural building block for an adapter that derives or cross-checks URML capability-manifest fields against a URDF. This RFC asks whether that adapter is worth building and where the description/capability boundary sits.

## The mapping (URML manifest via yourdfpy)

URML's manifest sits alongside the parsed URDF:

- yourdfpy parses a URDF in Python; a URML manifest declares capabilities and a safety envelope. A small adapter could read reach/DOF/joint limits from a yourdfpy model into a URML manifest skeleton, leaving payload, graspable classes, and the safety envelope to explicit declaration.
- URML's validator (Python) could use yourdfpy to keep a manifest consistent with the robot's URDF.
- The split: yourdfpy gives the URDF; the URML manifest gives capability + safety.

## What is asked

Request for comment from the yourdfpy maintainer:

1. Would a thin yourdfpy → URML manifest-skeleton adapter be useful, and what URDF fields map cleanly?
2. Which capability-manifest fields are genuinely outside URDF (payload, graspable classes, safety envelope)?
3. Where should the boundary sit between URDF parsing and capability + safety declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL) and Python reference tooling; the robot-description anchor (RFC-0455). yourdfpy is the Python-URDF-parser vertex of the robot-description wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `clemense/yourdfpy` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move39.yaml`.
