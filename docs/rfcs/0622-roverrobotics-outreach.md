---
rfc: 0622
title: Rover Robotics (roverrobotics_ros2) integration — request for comment
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

# RFC-0622: Rover Robotics (roverrobotics_ros2) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the outdoor-mobile sub-lane of Move #59.

## Summary

[`RoverRobotics/roverrobotics_ros2`](https://github.com/RoverRobotics/roverrobotics_ros2) (Apache-2.0, Rover Robotics, Minnesota) is the vendor ROS 2 driver for rugged skid-steer rovers (Rover Pro, Rover Zero, OpenRover). It takes velocity commands and drives a real outdoor platform. URML is a validated-intent layer that sits above a platform driver like this: it declares the platform's drive type and motion envelope in a capability manifest, expresses a motion subtask as typed intent, and validates that intent against the manifest before a velocity command reaches the driver. URML does not drive the motors; it declares and checks. This is a request for comment.

## The relationship (URML beside the Rover Robotics driver)

- **A clean vendor-platform manifest.** A vendor driver is the natural place for a URML capability manifest to attach: the platform's drive type (skid-steer), its speed and acceleration limits, and its motion envelope are known quantities. URML lifts those into a typed manifest, validates a motion intent against them, and only then is the command handed to the driver. The driver keeps the motor and protocol handling; URML is the pre-dispatch check.
- **Runtime-neutral by design.** URML is deliberately substrate-agnostic, so the same typed intent that validates against a Rover platform validates against any platform that declares an equivalent manifest. For a vendor, that means a customer's intent is checked against the real limits of the hardware they bought, without coupling the intent to one stack.

## What is asked

1. Is a typed capability manifest plus a validated motion intent (declare the platform's drive type and envelope, validate, then command the driver) useful above a vendor platform driver?
2. Does a skid-steer rover's envelope (speed, acceleration, turning constraints) map onto a URML manifest and safety envelope cleanly?
3. Would a single platform (for example Rover Zero) be the right first manifest to write?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the drive-type modeling used across the mobility profiles, and the safety-envelope validation pass. Companion to RFC-0621 (OpenMower) and RFC-0623 (Leo Rover) in the outdoor-mobile sub-lane of Move #59.

## Implementation note

Outreach only. The post is a GitHub Issue on `RoverRobotics/roverrobotics_ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is Apache-2.0; stated, not asked. Tracked in `examples/lighthouses/outreach-move59.yaml`.
