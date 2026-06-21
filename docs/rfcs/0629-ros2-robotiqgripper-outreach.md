---
rfc: 0629
title: ros2_RobotiqGripper (IFRA-Cranfield) integration — request for comment
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

# RFC-0629: ros2_RobotiqGripper (IFRA-Cranfield) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Completes the robotic-end-effector wave (Move #60).

## Summary

[`IFRA-Cranfield/ros2_RobotiqGripper`](https://github.com/IFRA-Cranfield/ros2_RobotiqGripper) (Apache-2.0, Cranfield University, UK) is a ROS 2 service interface to open and close Robotiq 2F grippers mounted on Universal Robots arms, reporting the opening ratio. It sits at the application altitude, where a grasp is a service call. URML declares the gripper's aperture and force envelope in a capability manifest, validates a grasp intent against it, and leaves the service call and the UR integration to the package. This is a request for comment.

## The relationship (URML beside ros2_RobotiqGripper)

- **A validated grasp above a service call.** Opening or closing a 2F gripper through this package is a grasp intent expressed as a service call. URML's contribution is to validate that intent against a declared aperture-and-force envelope before the call is made, so an out-of-envelope grasp is refused with a typed reason. The package keeps the service interface and the UR integration; URML is the pre-dispatch check.
- **A cell-level manifest.** A Robotiq 2F on a UR arm is a small, well-defined cell. URML declares the gripper alongside the arm in one capability manifest, so a grasp validates against the gripper while a motion validates against the arm, in the same typed model.

## What is asked

1. Is a typed grasp-intent layer (declare the gripper's aperture and force, validate, then call the service) useful above a service-level gripper interface?
2. Does a Robotiq 2F envelope (aperture range, force, the reported opening ratio) map onto a URML capability manifest and safety envelope cleanly?
3. Would a combined arm-and-gripper manifest (UR motion plus a 2F grasp) be a useful first example to write together?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's gripper model, the grasp primitive, the grasp-force safety envelope, and the single-manifest arm-plus-gripper modeling used in the industrial profile. Completes Move #60.

## Implementation note

Outreach only. The post is a GitHub Issue on `IFRA-Cranfield/ros2_RobotiqGripper` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is Apache-2.0; stated, not asked. Tracked in `examples/lighthouses/outreach-move60.yaml`.
