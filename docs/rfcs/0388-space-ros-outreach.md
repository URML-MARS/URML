---
rfc: 0388
title: Space-ROS integration — request for comment from the Space-ROS community
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0388: Space-ROS integration — request for comment from the Space-ROS community

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment that proposes how URML v0.1 maps onto an existing target and asks that target's maintainers for feedback. URML's shipped ROS 2 reference runtime and its five-pass validate-before-actuate discipline are the artifacts it builds on.

## Summary

[Space-ROS](https://github.com/space-ros/space-ros) (NASA, Open Robotics, and Blue Origin; BSD-3-Clause; a safety-hardened ROS 2 distribution for spaceflight) is the bullseye target for a substrate-neutral robot-intent layer: it is ROS 2, which URML already runs against, but with the safety and process rigor space demands. This RFC proposes URML as the natural-language, validated intent layer that sits one level above Space-ROS, and asks the maintainers whether that is useful and what a space-robot capability declaration should carry.

## The mapping (URML above Space-ROS)

URML does not replace any Space-ROS component. A person writes an English sentence; URML turns it into a typed primitive, validates it against the robot's declared capability manifest and a safety envelope, and only then dispatches to the Space-ROS nodes below:

- URML's existing ROS 2 runtime targets Space-ROS directly (Space-ROS is ROS 2). `move_to`, `detect`, `measure`, `report`, and the rest map onto the same action/service surface.
- The validate-before-actuate guarantee is a natural fit for the Space-ROS safety posture: a command that is not expressible under the declared manifest, or that violates the envelope, never reaches an actuator.
- The Space-ROS reference demos (the Curiosity rover, Canadarm2, the space-robots Nav2 demo in [`space-ros/demos`](https://github.com/space-ros/demos)) are the concrete proof surface: a "one English sentence moves the rover" loop maps directly onto them.

## What is asked

Request for comment from Space-ROS maintainers:

1. Is a validated, human-readable intent layer above Space-ROS interesting to the community, or does the existing tooling already cover that need?
2. What should a URML capability manifest declare to honestly describe a space robot beyond the terrestrial fields (mobility, manipulation, perception) — radiation or thermal limits, comms-window / light-time constraints, power budgets?
3. Where is the right seam for a URML → Space-ROS demonstration: one of the `space-ros/demos` robots (Curiosity / Canadarm2), or a fresh minimal manifest?

Nothing here asks Space-ROS to adopt, host, or maintain anything. The integration is URML's to build.

## Prior art / context

URML's ROS 2 reference runtime (`reference/ros2-runtime/`); the substrate-conformance contract ([RFC-0014](0014-substrate-conformance.md)) URML holds itself to; the AV runtime work ([RFC-0020](0020-autoware-av-substrate.md), Autoware) as a sibling ROS-2 substrate engagement. Space-ROS is part of URML's "works everywhere" thesis: if it runs on ROS 2, it should run on the space-hardened ROS 2 too.

## Implementation note

Outreach only. The post is a GitHub Discussion on `space-ros/space-ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move31.yaml`.
