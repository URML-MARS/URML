---
rfc: 0541
title: AutoAPMS integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0541: AutoAPMS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. **Completes** the domain / standards / conceptual-peer wave (Move #48), and the entire 2026-06-13 free-GitHub candidate slate.

## Summary

[`AutoAPMS/auto-apms`](https://github.com/AutoAPMS/auto-apms) (Apache-2.0, active, Germany) is a framework for building robot behaviors via behavior trees in ROS 2, with skill-based BT composition and a deliberation layer. URML's Layer-3 composition is a peer to a behavior tree, so URML and AutoAPMS compose in either direction: URML intent above an AutoAPMS skill/BT layer, or an AutoAPMS skill that dispatches a validated URML primitive. This RFC asks which direction is useful.

## The mapping (URML beside AutoAPMS)

- **Intent above skills, or a skill dispatches a validated primitive.** A URML program can lower onto an AutoAPMS behavior tree, or an AutoAPMS skill-leaf can call a single URML primitive validated against the robot's capability manifest and envelope before it executes. URML adds the typed, statically-validated intent; AutoAPMS stays the deliberation / BT executor.
- **Skill declarations toward a manifest.** AutoAPMS's skill registrations describe what the robot can do, which lines up with a URML capability manifest the validator checks against.

## What is asked

Request for comment from the AutoAPMS maintainers:

1. Is lowering URML composition onto an AutoAPMS BT the more natural direction, or is a skill-dispatches-a-validated-URML-primitive cleaner?
2. Could AutoAPMS skill declarations inform a URML capability manifest?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition and the behavior-tree / FSM interop engagements (Move #41: BehaviorTree.CPP, py_trees, SMACC2, FlexBE, plus ros2_ros_bt_py in Move #45). Completes Move #48 and the candidate slate.

## Implementation note

Outreach only. The post is a GitHub Issue on `AutoAPMS/auto-apms` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
