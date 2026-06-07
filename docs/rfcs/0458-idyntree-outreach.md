---
rfc: 0458
title: iDynTree integration — request for comment
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

# RFC-0458: iDynTree integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats.

## Summary

[`gbionics/idyntree`](https://github.com/gbionics/idyntree) (BSD-3-Clause, ~230 stars, active; formerly robotology/idyntree) is a multibody kinematics and dynamics library for floating-base robots (IIT / gBionics), which parses both URDF and SDF. A library that already computes reachable workspace, joint limits, and dynamics from a description is well placed to advise which URML capability-manifest fields can be derived from a description and which must be declared separately. This RFC asks that.

## The mapping (URML manifest informed by iDynTree)

URML's manifest sits alongside the robot description and the dynamics model:

- iDynTree computes kinematics/dynamics from a URDF/SDF model; a URML manifest declares capabilities (reach, DOF, payload, gripper, workspace bounds) and a safety envelope. Some manifest fields could be derived from iDynTree's computed model (e.g. reachable workspace, joint limits).
- URML's validator could consume iDynTree-computed properties to bootstrap or sanity-check a manifest.
- The split: iDynTree says what the robot's physics *are*; the URML manifest says what it is *allowed and able to do*.

## What is asked

Request for comment from the iDynTree maintainers:

1. Which URML capability-manifest fields (reachable workspace, joint/velocity limits, payload) can be derived honestly from an iDynTree model, and which are genuinely separate?
2. Would a thin adapter from an iDynTree model to a URML manifest skeleton be useful for floating-base / humanoid robots?
3. Where should the boundary sit between dynamics model and capability + safety declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the whole-body / legged work (RFC-0010, RFC-0384) for floating-base robots; the robot-description anchor (RFC-0455). iDynTree is the dynamics-from-description vertex of the robot-description wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `gbionics/idyntree` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move39.yaml`.
