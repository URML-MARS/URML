---
rfc: 0462
title: urchin (urdfpy successor) integration — request for comment
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

# RFC-0462: urchin (urdfpy successor) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats. Tier B.

## Summary

[`fishbotics/urchin`](https://github.com/fishbotics/urchin) (MIT, ~78 stars) is the actively-maintained successor to urdfpy — a Python URDF parser with lazy mesh loading and forward kinematics. As a clean, modern Python URDF library, it is a natural building block for an adapter that derives or cross-checks URML capability-manifest fields from a URDF. This RFC asks whether that adapter is worth building.

## The mapping (URML manifest via urchin)

URML's manifest sits alongside the parsed URDF:

- urchin parses a URDF and computes forward kinematics in Python; a URML manifest declares capabilities and a safety envelope. An adapter could read reach/DOF/joint limits from an urchin model into a URML manifest skeleton, leaving payload, graspable classes, and the safety envelope to explicit declaration.
- URML's Python validator could use urchin to keep a manifest consistent with the robot's URDF.
- The split: urchin gives the URDF + FK; the URML manifest gives capability + safety.

## What is asked

Request for comment from the urchin maintainer:

1. Would a thin urchin → URML manifest-skeleton adapter be useful, and what URDF/FK fields map cleanly?
2. Which capability-manifest fields are genuinely outside URDF (payload, graspable classes, safety envelope)?
3. Where should the boundary sit between URDF parsing / FK and capability + safety declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL) and Python reference tooling; the robot-description anchor (RFC-0455); the sibling yourdfpy engagement (RFC-0460). urchin is the maintained-urdfpy-successor vertex of the robot-description wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `fishbotics/urchin` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move39.yaml`.
