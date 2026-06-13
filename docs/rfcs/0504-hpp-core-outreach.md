---
rfc: 0504
title: Humanoid Path Planner (hpp-core) integration — request for comment
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

# RFC-0504: Humanoid Path Planner (hpp-core) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`humanoid-path-planner/hpp-core`](https://github.com/humanoid-path-planner/hpp-core) (BSD-2-Clause, ~43 stars, active, LAAS-CNRS) is the core of the Humanoid Path Planner framework. URML's relationship to a motion planner is consistent: URML does not plan; it declares the goal and the constraints, validates them against the robot's capabilities and a safety envelope, hands them to the planner, and consumes the trajectory the planner returns. This RFC asks whether that mapping onto HPP is useful.

## The mapping (URML beside hpp-core)

- **Declare goal + constraints, consume trajectory.** A URML program declares a goal and the constraints it must satisfy; the validator confirms they are within the robot's declared capabilities and envelope; hpp-core computes the path; URML consumes the resulting trajectory (the same shape as URML's `plan_path` / `follow_trajectory` split, RFC-0020). URML never re-implements planning.
- **Capability manifest as the constraint source.** The robot's reach, joint limits, and declared geometry feed both the URML manifest and the planning problem, so the validated goal and the planner's problem definition agree.

## What is asked

Request for comment from the HPP maintainers:

1. Does the declare-goal-plus-constraints / consume-trajectory split fit how a caller drives hpp-core?
2. Could a URML capability manifest be a useful, validatable source for the planning constraints?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `plan_path` / `follow_trajectory` primitives (RFC-0020), the motion-planning engagements (Move #26: OMPL / Ruckig / TOPP-RA / Pinocchio and others — "URML declares goal + constraints, validates, consumes the trajectory"), and the decide-then-do split (RFC-0002). hpp-core is in the broader LAAS-CNRS planning ecosystem URML has engaged before. Part of Move #45.

## Implementation note

Outreach only. The post is a GitHub Issue on `humanoid-path-planner/hpp-core` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
