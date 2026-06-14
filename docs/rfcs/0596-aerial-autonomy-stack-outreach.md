---
rfc: 0596
title: aerial-autonomy-stack integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0596: aerial-autonomy-stack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the inspection-robotics wave (Move #55).

## Summary

[`JacopoPan/aerial-autonomy-stack`](https://github.com/JacopoPan/aerial-autonomy-stack) (MIT) is a framework to simulate and deploy perception-based autonomous drones and drone swarms on PX4/ArduPilot with ROS 2 (object detection, LiDAR, Jetson). Aerial inspection is one of its central use cases, and an inspection mission is a goal plus constraints: survey this structure, hold this standoff and geofence, return on this condition. That is what URML declares and validates. This RFC asks whether the mapping is useful.

## The mapping (URML beside aerial-autonomy-stack)

- **Declare the inspection mission, validate, consume the trajectory.** URML expresses the mission as intent plus an operating envelope (standoff, geofence, altitude), validates it against the craft's declared capabilities, then consumes the trajectory the stack plans and flies (RFC-0020). The stack keeps full ownership of perception, planning, and control. URML stays substrate-neutral and already maps onto PX4.
- **Swarm as a fleet.** Because the stack runs swarms, a multi-drone inspection maps onto URML's multi-robot roster and cross-vehicle deconfliction (RFC-0286 / RFC-0291): declare the fleet and its separation constraints, validate the multi-vehicle intent, then drive it through the stack.

## What is asked

1. Is a typed, validated mission-intent layer (declare goal + inspection envelope, validate, consume the trajectory) useful above the stack?
2. Does a multi-drone inspection map onto a fleet roster + cross-vehicle deconfliction in a way that fits how the stack runs swarms?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's drone profile, the plan_path / follow_trajectory consume model (RFC-0020), the multi-robot roster (RFC-0286), and the PX4 reference-runtime mapping. Anchor of Move #55; the aerial-inspection target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `JacopoPan/aerial-autonomy-stack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move55.yaml`.
