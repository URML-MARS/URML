---
rfc: 0623
title: Leo Rover (leo_robot-ros2) integration — request for comment
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

# RFC-0623: Leo Rover (leo_robot-ros2) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Completes the outdoor-mobile sub-lane of Move #59.

## Summary

[`LeoRover/leo_robot-ros2`](https://github.com/LeoRover/leo_robot-ros2) (MIT, Kell Ideas, Poland) is the real-robot ROS 2 driver for the Leo Rover, a four-wheel all-terrain research and education platform. It commands physical motion on a rover used in classrooms and field research. URML is a validated-intent layer that sits above a platform driver like this: it declares the rover's drive type and motion envelope in a capability manifest, expresses a motion subtask as typed intent, and validates that intent against the manifest before the driver moves the wheels. URML does not drive the platform; it declares and checks. This is a request for comment.

## The relationship (URML beside the Leo Rover driver)

- **A teachable manifest plus a checked intent.** On a platform built for learning, a typed capability manifest is also a clear, readable statement of what the rover can and cannot do: its drive type, its speed limits, its motion envelope. URML validates a student's or researcher's motion intent against that manifest before the driver acts, so an out-of-envelope command is refused with a typed reason rather than silently attempted. The driver keeps the motion; URML is the pre-dispatch check.
- **A natural fit for an education platform.** URML's headline path is one plain sentence becoming a validated, executable robot action. A rover used to teach robotics is a good place for that loop to be visible: intent stated, validated against the real platform, then run.

## What is asked

1. Is a typed capability manifest plus a validated motion intent useful above the Leo Rover driver, in research and in teaching?
2. Does the rover's envelope (drive type, speed, motion limits) map onto a URML manifest and safety envelope cleanly?
3. Would a classroom-facing example (a sentence to a validated rover motion) be worth building together?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the drive-type modeling, the safety-envelope validation, and the natural-language-to-validated-action loop (Layer 4). Companion to RFC-0621 (OpenMower) and RFC-0622 (Rover Robotics) in the outdoor-mobile sub-lane of Move #59.

## Implementation note

Outreach only. The post is a GitHub Issue on `LeoRover/leo_robot-ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is MIT; stated, not asked. Tracked in `examples/lighthouses/outreach-move59.yaml`. Distinct from the Leo Rover simulation packages; this is the real-robot driver.
