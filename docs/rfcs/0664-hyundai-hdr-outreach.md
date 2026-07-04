---
rfc: 0664
title: HD Hyundai Robotics (hyundai-robotics/hdr_ros2_driver) integration — request for comment
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

# RFC-0664: HD Hyundai Robotics hdr_ros2_driver integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #69 (South Korea lane).

## Summary

[`hyundai-robotics/hdr_ros2_driver`](https://github.com/hyundai-robotics/hdr_ros2_driver) (HD Hyundai Robotics) is the ROS 2 driver for HD Hyundai industrial robot arms, providing the communication nodes that interface with the robot controllers. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A driver that carries motion commands to an industrial controller is a place where a pre-dispatch check can sit, one layer above the wire.

## The relationship (URML beside hdr_ros2_driver)

Code that uses the driver decides a motion and sends it to the HD Hyundai controller. URML can declare the arm's reach, payload, and speed envelope and validate a commanded motion against that declaration before the driver sends it. It is a static admissibility check on the outgoing command, not a controller and not a re-implementation of the arm's motion planning.

To be honest about the fit: the industrial controller holds the real motion planning and safety logic, and this repo is the ROS 2 driver to it, so URML's role here is narrower than for an autonomy layer that generates actions. HD Hyundai Robotics is also a member of the ROS-Industrial Consortium, which URML noted in RFC-0038; this is a per-repo request for comment, complementary to that broader consortium context rather than a substitute for it.

## What is asked

1. For a ROS 2 driver to an industrial arm, is a declared-capability and envelope check on the outgoing motion command a useful addition for the integrations built on it, or does that belong inside the controller?
2. Would a small worked example mapping a command sent through the driver onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied in front of an industrial-arm ROS 2 driver. BSD-3-Clause; HD Hyundai Robotics, South Korea; ROS-Industrial Consortium member (cf. RFC-0038). Part of Move #69.

## Implementation note

Outreach only. The post is a GitHub Issue on `hyundai-robotics/hdr_ros2_driver` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move69.yaml`.
