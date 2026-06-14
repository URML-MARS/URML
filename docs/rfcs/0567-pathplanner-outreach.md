---
rfc: 0567
title: PathPlanner integration — request for comment
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

# RFC-0567: PathPlanner integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`mjansen4857/pathplanner`](https://github.com/mjansen4857/pathplanner) (MIT) is a widely-used path-planning and path-following library for FIRST Robotics Competition robots. URML sits above a planner like this at the intent layer: it declares the goal and constraints, validates them against the robot's capabilities and a safety envelope, then consumes the path PathPlanner produces. URML does not plan; it declares, validates, and consumes (RFC-0020). This RFC asks whether the mapping is useful.

## The mapping (URML beside PathPlanner)

- **Declare the goal, validate, consume the path.** A driving task is a goal plus constraints. URML expresses it, validates against the robot's declared capabilities and an envelope, then consumes the planned path (RFC-0020 follow_trajectory). PathPlanner keeps full ownership of how the path is generated and followed.
- **A typed front door, optionally from English.** Because URML's Layer 4 turns an instruction into validated intent, a student could express a routine in plain language and have it become a checked goal handed to PathPlanner.

## What is asked

Request for comment from the PathPlanner maintainer:

1. Is a typed, validated intent layer (declare goal + constraints, validate, consume the path) useful above PathPlanner?
2. Does URML's capability + safety-envelope model fit how an FRC robot's limits are described?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the Layer-4 natural-language grammar, and the educational profile (RFC-0011). Part of Move #52; the FRC trajectory cluster (with Choreo RFC-0569).

## Implementation note

Outreach only. The post is a GitHub Issue on `mjansen4857/pathplanner` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move52.yaml`.
