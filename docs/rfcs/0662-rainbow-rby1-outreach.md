---
rfc: 0662
title: Rainbow Robotics RB-Y1 (RainbowRobotics/rby1-sdk) integration — request for comment
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

# RFC-0662: Rainbow Robotics RB-Y1 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #69 (South Korea lane).

## Summary

[`RainbowRobotics/rby1-sdk`](https://github.com/RainbowRobotics/rby1-sdk) (Rainbow Robotics) is the official Python and C++ SDK for the RB-Y1, a wheeled bimanual mobile manipulator. URML is a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capability manifest and safety envelope before it runs. A platform that combines a mobile base, two arms, and a body is a good fit for that check, because a command spans several subsystems each with its own limits.

## The relationship (URML beside the RB-Y1 SDK)

Code built on the SDK decides a motion and commands the RB-Y1. URML can declare the platform's envelope, per arm reach and payload, gripper force, base velocity, and (for coordinated body motion) the whole-body stability bounds from URML's RFC-0384 block, and validate a commanded motion against that declaration before the SDK dispatches it. The check sits above the SDK, between the program that decides the motion and the SDK that sends it.

URML does not plan, control, or move the robot. It declares the RB-Y1's envelope and confirms a commanded action is inside it before dispatch. For a bimanual mobile manipulator, that single check covers arm, gripper, base, and whole-body limits in one place.

## What is asked

1. For a bimanual mobile manipulator, is a declared-capability and envelope check spanning arms, grippers, base, and whole-body stability useful before the SDK dispatches a command, or is that coverage already spread across the SDK's own limits?
2. Would a small worked example mapping an RB-Y1 command onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, the RFC-0384 whole-body block, and the validate-before-actuate gate, applied to a bimanual mobile-manipulator SDK. Apache-2.0; Rainbow Robotics, South Korea. Part of Move #69.

## Implementation note

Outreach only. The post is a GitHub Issue on `RainbowRobotics/rby1-sdk` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move69.yaml`.
