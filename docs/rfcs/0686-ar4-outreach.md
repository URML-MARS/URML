---
rfc: 0686
title: AR4 ROS driver (ycheng517/ar4_ros_driver) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-01
updated: 2026-09-01
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

# RFC-0686: AR4 ROS driver (ycheng517/ar4_ros_driver) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the small-open-robot wave (Move #72).

## Summary

[`ycheng517/ar4_ros_driver`](https://github.com/ycheng517/ar4_ros_driver) is a ROS 2 driver (with MoveIt 2) for the AR4, an affordable open 6-axis desktop arm from Annin Robotics (MK1/MK2/MK3, plus a servo gripper). Because the driver takes a MoveIt goal or servo command and sends it to the arm's Teensy firmware, it sits exactly where URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (joint limits, reachable workspace, gripper force) and a safety envelope, and URML checks a motion or grasp is admissible before the command reaches the firmware. This is a request for comment.

## The relationship (URML beside the AR4 driver)

- **The planner proposes, the validator gates.** MoveIt (or whatever produces the goal) decides the motion; URML checks the concrete joint goal or grasp is admissible on the declared AR4 (within its joint limits, reachable workspace, and gripper force, inside the safety envelope) before the driver dispatches it. URML does the check; the driver keeps the actuation.
- **A DIY desktop arm is exactly where a static gate earns its keep.** On a low-cost 3D-printed arm, a command outside the reachable workspace or a grasp beyond the servo gripper is cheap to refuse on paper and expensive to discover on hardware.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the driver rather than depending on its internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared capability manifest + safety envelope, checked before a goal reaches the AR4 firmware, be a useful guard on top of the driver?
2. Would a small worked example mapping an AR4 motion or grasp onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Anchor of the Move #72 small-open-robot wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ycheng517/ar4_ros_driver` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move72.yaml`.
