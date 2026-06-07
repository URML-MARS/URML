---
rfc: 0461
title: Orocos KDL integration — request for comment
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

# RFC-0461: Orocos KDL integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats. Tier B.

## Summary

[`orocos/orocos_kinematics_dynamics`](https://github.com/orocos/orocos_kinematics_dynamics) (LGPL-2.1-or-later, ~881 stars, active) is the Orocos Kinematics and Dynamics Library (KDL), one of the classic kinematics libraries in the ROS ecosystem, building chains from URDF. A widely-used kinematics library is well placed to advise which URML capability-manifest fields (reach, joint limits, reachable workspace) are computable from a chain and which must be declared. This RFC asks that.

## The mapping (URML manifest informed by KDL)

URML's manifest sits alongside the kinematic model:

- KDL builds kinematic chains from a URDF and computes FK/IK and joint limits; a URML manifest declares capabilities (reach, DOF, workspace bounds) and a safety envelope. Some manifest fields could be derived from a KDL chain.
- URML's validator could use KDL-computed reach / joint limits to sanity-check a manifest's declared workspace.
- The split: KDL gives the kinematics; the URML manifest gives capability + safety.

## What is asked

Request for comment from the Orocos KDL maintainers:

1. Which URML capability-manifest fields (reach, joint limits, reachable workspace) can be derived honestly from a KDL chain, and which are genuinely separate?
2. Would cross-checking a manifest's declared workspace against KDL-computed reach be useful?
3. Where should the boundary sit between kinematics computation and capability + safety declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the manipulation primitive family (Move #27); the robot-description anchor (RFC-0455). Orocos KDL is the classic-kinematics-library vertex of the robot-description wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `orocos/orocos_kinematics_dynamics` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front. The library is LGPL-2.1-or-later; URML interoperates above it, vendors none of its code, and proposes no license change. Tracked in `examples/lighthouses/outreach-move39.yaml`.
