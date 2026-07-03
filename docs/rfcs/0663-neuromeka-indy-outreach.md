---
rfc: 0663
title: Neuromeka Indy (neuromeka-robotics/indy-ros2) integration — request for comment
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

# RFC-0663: Neuromeka Indy integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #69 (South Korea lane).

## Summary

[`neuromeka-robotics/indy-ros2`](https://github.com/neuromeka-robotics/indy-ros2) (Neuromeka) is the ROS 2 package for the Indy collaborative arm. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A collaborative arm working near people is a natural place for a static pre-dispatch check, because the arm's reach, payload, and speed limits are exactly what a shared workspace depends on.

## The relationship (URML beside indy-ros2)

A motion or a grasp commanded to Indy is a concrete action with a concrete envelope. URML can declare the arm's reach, payload, gripper force, and a collaborative speed limit, and validate a commanded motion against that declaration before the ROS 2 package drives the arm. The check sits between the program that decides the motion and the controller that runs it, and touches neither the kinematics nor the drivers.

URML does not plan, control, or move the arm. It declares the arm's envelope and confirms a commanded action is inside it before dispatch.

## What is asked

1. For a collaborative arm, is a typed declared-capability and envelope check (reach, payload, gripper force, collaborative speed) on a commanded motion useful before dispatch, or is that already enforced by the Indy controller and its safety functions?
2. Would a small worked example mapping an Indy motion or grasp onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a collaborative-arm ROS 2 package. The repository does not carry a recognized license file, so this is a cross-reference, not a code-reuse proposal; Neuromeka, South Korea. Part of Move #69.

## Implementation note

Outreach only. The post is a GitHub Issue on `neuromeka-robotics/indy-ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move69.yaml`.
