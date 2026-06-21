---
rfc: 0628
title: OnRobot ROS 2 controller (onrobot-ros2) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-21
updated: 2026-06-21
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

# RFC-0628: OnRobot ROS 2 controller (onrobot-ros2) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robotic-end-effector wave (Move #60).

## Summary

[`ABC-iRobotics/onrobot-ros2`](https://github.com/ABC-iRobotics/onrobot-ros2) (MIT, Obuda University, Hungary) is a ROS 2 controller for the OnRobot RG2 and RG6 parallel grippers, including Isaac Sim support. These are width-and-force grippers, the base case URML's grasp model handles: URML declares the gripper's width range and force limit in a capability manifest, validates a grasp intent against that envelope, and leaves the command path to the controller. This is a request for comment.

## The relationship (URML beside onrobot-ros2)

- **Declare width and force, check the grasp first.** A grasp on an RG2 or RG6 is a typed intent: a target width and a force not to exceed. URML validates that against a manifest declaring the gripper's width range and maximum force, then leaves the actual command to the controller. The controller keeps the actuation; URML is the static check in front of it.
- **Sim and real on the same declaration.** Because the controller supports both Isaac Sim and hardware, the same URML manifest and the same validated grasp intent apply to the simulated and the real gripper, which is the kind of substrate neutrality URML is built around: declare once, validate everywhere the manifest holds.

## What is asked

1. Is a typed grasp-intent layer (declare the gripper's width and force, validate, then command the controller) useful above an OnRobot ROS 2 controller?
2. Does an RG2 or RG6 envelope (width range, force limit, speed) map onto a URML capability manifest and safety envelope cleanly?
3. Would the sim path (Isaac Sim) be a good place to demonstrate a validated grasp before running it on hardware?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's gripper model, the grasp primitive, the grasp-force safety envelope, and the declare-once-validate-everywhere substrate neutrality. Companion to RFC-0627 (Robotiq Hand-E) and RFC-0629 (Robotiq 2F on UR) in the parallel-gripper part of Move #60.

## Implementation note

Outreach only. The post is a GitHub Issue on `ABC-iRobotics/onrobot-ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is MIT; stated, not asked. Tracked in `examples/lighthouses/outreach-move60.yaml`.
