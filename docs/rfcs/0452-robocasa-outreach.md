---
rfc: 0452
title: RoboCasa integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0452: RoboCasa integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the wrap-a-learned-policy pattern. Tier B.

## Summary

[`robocasa/robocasa`](https://github.com/robocasa/robocasa) (MIT, ~1,446 stars, active) is a large-scale simulation framework of everyday household tasks for training generalist robots (UT Austin / NVIDIA). A rich everyday-task sim is a natural place to express household intent that a learned policy executes, and to validate that intent against the robot's declared capabilities first. This RFC asks whether that is interesting.

## The mapping (URML above RoboCasa)

URML sits above the simulated robot / learned policy as a validated intent layer:

- A URML household intent ("put the mug in the sink") drives a RoboCasa task, or declares the goal + envelope around a learned policy that produces the low-level action.
- URML's optional validation block records the simulation-fidelity context a run was checked in.
- Validate-before-actuate refuses an out-of-capability request before the simulated robot moves (decide-then-do applied to learning).

## What is asked

Request for comment from the RoboCasa maintainers:

1. Is a validated household-intent layer + envelope above RoboCasa interesting for generalist-robot research?
2. What should a URML capability manifest declare to describe a RoboCasa task robot honestly (arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, object/task vocabulary)?
3. Is the env interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the simulation-engagement pattern (RFC-0381); the earlier VLA wave (Move #11). RoboCasa is the everyday-task-sim vertex of the round-2 wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `robocasa/robocasa` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move38.yaml`.
