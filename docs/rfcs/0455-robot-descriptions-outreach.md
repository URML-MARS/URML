---
rfc: 0455
title: robot_descriptions.py integration — request for comment
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

# RFC-0455: robot_descriptions.py integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats. It is the anchor of the robot-description / interop-formats wave (Move #39).

## Summary

[`robot-descriptions/robot_descriptions.py`](https://github.com/robot-descriptions/robot_descriptions.py) (Apache-2.0, ~769 stars, active, Discussions on) imports 185+ open robot descriptions (URDF / MJCF / USD) as ready-to-use Python modules. URML has a separate but adjacent artifact — a *capability manifest* (drive type, reach/DOF, payload, gripper, workspace bounds, safety envelope) that its validator checks intent against. A library that already normalizes access to descriptions across formats is the ideal place to ask how a capability+safety manifest should relate to, and where possible derive from, a robot description. This RFC asks exactly that.

## The mapping (URML manifest alongside robot descriptions)

URML's manifest sits alongside the robot description:

- A robot description (URDF/MJCF/USD via robot_descriptions.py) carries kinematics, joint limits, geometry; a URML manifest carries capabilities and a safety envelope. Some manifest fields (reach, DOF, joint/speed limits) could be derived or cross-checked from the description.
- URML's validator could consume a robot_descriptions.py entry to bootstrap or sanity-check a manifest, keeping the two from drifting.
- The clean split: the description says what the robot *is*; the manifest says what it is *allowed and able to do*.

## What is asked

Request for comment from the robot_descriptions.py maintainers:

1. Which capability-manifest fields can be derived honestly from a URDF/MJCF/USD description, and which are genuinely separate (payload limits, graspable classes, safety envelope)?
2. Would a thin adapter from a robot_descriptions.py entry to a URML manifest skeleton be useful?
3. Where should the line sit between robot *description* and robot *capability + safety* declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the manipulation and mobility primitive families. robot_descriptions.py is the anchor of the robot-description wave — the cross-format description aggregator.

## Implementation note

Outreach only. The post is a GitHub Discussion on `robot-descriptions/robot_descriptions.py` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move39.yaml`.
