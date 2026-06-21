---
rfc: 0627
title: robotiq_hande_driver (AGH-CEAI) integration — request for comment
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

# RFC-0627: robotiq_hande_driver (AGH-CEAI) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robotic-end-effector wave (Move #60).

## Summary

[`AGH-CEAI/robotiq_hande_driver`](https://github.com/AGH-CEAI/robotiq_hande_driver) (Apache-2.0, AGH University of Krakow) is a ros2_control driver for the Robotiq Hand-E parallel gripper, with fake, serial-Modbus, and UR tool-communication backends. A parallel gripper is the original case URML's grasp model handles: a single-DoF gripper with an aperture and a commanded force. URML declares the gripper's aperture range and force limit in a capability manifest, validates a grasp intent against that envelope, and leaves the Modbus and ros2_control plumbing to the driver. This is a request for comment.

## The relationship (URML beside robotiq_hande_driver)

- **Declare the aperture and force, check the grasp before it closes.** A close-with-force command on a Hand-E is a typed grasp intent: a target aperture and a force not to exceed. URML validates that against a manifest declaring the gripper's aperture range and maximum force, then leaves the Modbus command and the ros2_control hardware interface to the driver. The driver keeps the actuation; URML is the pre-dispatch check.
- **The base case, cleanly.** A parallel gripper does not need the dexterity declaration, only the simple gripper model and a grasp-force envelope. That makes this a small, honest mapping: the manifest states two or three numbers, and the validator refuses a grasp that violates them.

## What is asked

1. Is a typed grasp-intent layer (declare the gripper's aperture and force, validate, then command the driver) useful above a ros2_control gripper driver?
2. Does a Robotiq Hand-E's envelope (aperture range, force limit, speed) map onto a URML capability manifest and safety envelope cleanly?
3. Does the multi-backend design (fake, serial, UR tool comm) raise anything a validation layer above it should account for?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's gripper model, the grasp primitive, and the grasp-force safety envelope. Companion to RFC-0628 (OnRobot) and RFC-0629 (Robotiq 2F on UR) in the parallel-gripper part of Move #60.

## Implementation note

Outreach only. The post is a GitHub Issue on `AGH-CEAI/robotiq_hande_driver` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is Apache-2.0; stated, not asked. Tracked in `examples/lighthouses/outreach-move60.yaml`.
