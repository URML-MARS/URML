---
rfc: 0439
title: ROS-Industrial (kuka_experimental) integration — request for comment
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

# RFC-0439: ROS-Industrial (kuka_experimental) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile. It anchors one engagement on the ROS-Industrial community via the `kuka_experimental` repo. Tier B. This complements the prior ROS-Industrial contact (RFC-0038).

## Summary

[`ros-industrial/kuka_experimental`](https://github.com/ros-industrial/kuka_experimental) (Apache-2.0, ~336 stars, Discussions enabled) hosts experimental KUKA packages under the ROS-Industrial consortium — the community that brought industrial robots to ROS. ROS-Industrial maintains support packages for many OEM arms, and is the natural community to discuss a validated intent layer that targets standard industrial interfaces rather than inventing parallel ones. This RFC anchors on `kuka_experimental` and references the consortium's broader vendor support.

## The mapping (URML above ROS-Industrial drivers)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets ROS-Industrial driver packages on their ROS surface (and `ros2_control` controllers); a `pick_from` / `place_at` / `grasp` lowers onto the standard interface, the decide-then-do split made concrete.
- URML prefers to target the standard interfaces ROS-Industrial defines rather than per-vendor parallel ones (the same posture URML takes toward Nav2 and ros2_control).
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object, or an over-payload request before the arm moves.

## What is asked

Request for comment from the ROS-Industrial community:

1. Where should URML target standard ROS-Industrial interfaces rather than a generic or per-vendor ROS surface?
2. What should a URML capability manifest declare to describe an industrial arm honestly across vendors (reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds)?
3. Is a validated natural-language layer over ROS-Industrial drivers interesting for the consortium's users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23); the prior ROS-Industrial contact (RFC-0038). ROS-Industrial is the standards-community vertex of the arm-driver wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Discussion on `ros-industrial/kuka_experimental` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). The consortium's other vendor packages are referenced, not posted to separately (org-anchor). Tracked in `examples/lighthouses/outreach-move36.yaml`.
