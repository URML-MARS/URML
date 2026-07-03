---
rfc: 0660
title: RT Corporation CRANE-X7 (rt-net/crane_x7_ros) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-03
updated: 2026-07-03
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

# RFC-0660: RT Corporation CRANE-X7 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #68 (Japan lane).

## Summary

[`rt-net/crane_x7_ros`](https://github.com/rt-net/crane_x7_ros) (RT Corporation, Tokyo) is the ROS control stack for CRANE-X7, a 7-DoF desktop research and education arm. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A teaching arm with a real gripper is a clean, contained place to see whether a typed pre-dispatch check adds anything, because the arm's reach, payload, and gripper force are small, well-defined numbers.

## The relationship (URML beside CRANE-X7)

A motion or a grasp commanded to CRANE-X7 is a concrete action with a concrete envelope: this reach, this payload, this gripper force. URML can declare those in a manifest and validate a commanded motion or grasp against them before the ROS stack drives the servos. The check sits between the program that decides the motion and the controller that runs it, and it does not touch the kinematics or the drivers.

URML does not plan, control, or move the arm. It declares the arm's envelope and confirms a commanded action is inside it before dispatch. On a teaching arm, that also makes the boundary legible to a student: the validator says, in plain terms, why a motion is or is not allowed.

## What is asked

1. For an education and research arm, is a typed declared-capability and envelope check (reach, payload, gripper force) on a commanded motion useful before dispatch, or is that already covered by the ROS stack and MoveIt limits in practice?
2. Would a small worked example mapping a CRANE-X7 motion or grasp onto a URML manifest (validated, no execution) be worth having, perhaps as teaching material?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a 7-DoF education and research arm. Apache-2.0; RT Corporation, Tokyo, Japan. Part of Move #68.

## Implementation note

Outreach only. The post is a GitHub Issue on `rt-net/crane_x7_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move68.yaml`.
