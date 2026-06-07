---
rfc: 0435
title: KUKA LBR iiwa (lbr-stack) integration — request for comment
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

# RFC-0435: KUKA LBR iiwa (lbr-stack) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the industrial profile.

## Summary

[`lbr-stack/lbr_fri_ros2_stack`](https://github.com/lbr-stack/lbr_fri_ros2_stack) (Apache-2.0, ~251 stars, active) is the community ROS 2 stack for KUKA LBR iiwa 7/14 and Med 7/14 arms (over the Fast Robot Interface). The LBR iiwa is a leading torque-sensitive collaborative arm, widely used in research and medical robotics, and a permissively-licensed ROS 2 stack for it is a strong home for URML's validated, force-aware manipulation intent. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above the lbr-stack)

URML sits above the arm as a validated intent layer:

- URML's ROS 2 runtime meets the stack on its ROS 2 / FRI surface (and `ros2_control` controllers); a `grasp` / `pick_from` / `place_at` lowers onto the arm interface, the decide-then-do split made concrete.
- Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload/force over the declared limit before the arm moves — meaningful on a torque-sensitive cobot.
- The iiwa manifest (reach, payload, joint/force limits, gripper, graspable classes) exercises URML's force-aware industrial-profile model.

## What is asked

Request for comment from the lbr-stack maintainers:

1. Is URML's ROS 2 / FRI surface the right seam for an external validated-intent layer above the LBR iiwa stack?
2. What should a URML capability manifest declare to describe an LBR iiwa honestly (reach/DOF, payload, joint/force limits, gripper + graspable classes, workspace bounds)?
3. Is a validated natural-language layer interesting for the LBR iiwa research community?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and `pick_from`/`place_at` (industrial profile, RFC-0013); the `ros2_control` engagement (Move #23). The lbr-stack is the torque-sensitive-cobot vertex of the arm-driver wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `lbr-stack/lbr_fri_ros2_stack` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move36.yaml`.
