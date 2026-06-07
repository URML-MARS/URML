---
rfc: 0433
title: Yaskawa motoros2 integration — request for comment
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

# RFC-0433: Yaskawa motoros2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile.

## Summary

[`Yaskawa-Global/motoros2`](https://github.com/Yaskawa-Global/motoros2) (permissive; REUSE-compliant Apache-2.0 / BSD / MIT code, ~157 stars, active) is Yaskawa's official micro-ROS node for Motoman robot controllers — a first-party ROS 2 driver for one of the largest industrial-arm makers. A high-volume industrial arm with a vendor-maintained ROS 2 surface is a strong home for URML's validated manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above motoros2)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets `motoros2` on its ROS 2 action/service surface; a `pick_from` / `place_at` / `grasp` lowers onto the Motoman controller interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves — a meaningful safety boundary on industrial-cell hardware.
- The Motoman manifest (reach, payload, joint/speed limits, gripper/EOAT, graspable classes) is a clean test of URML's industrial-profile model on production hardware.

## What is asked

Request for comment from the motoros2 maintainers:

1. Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above motoros2?
2. What should a URML capability manifest declare to describe a Motoman-class industrial arm honestly (reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds)?
3. Is a validated natural-language layer interesting for the Motoman ROS 2 community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). Yaskawa motoros2 is the high-volume-industrial vertex of the arm-driver wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `Yaskawa-Global/motoros2` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (permissive; REUSE-compliant). Tracked in `examples/lighthouses/outreach-move36.yaml`.
