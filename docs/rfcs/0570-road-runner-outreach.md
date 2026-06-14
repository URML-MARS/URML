---
rfc: 0570
title: Road Runner integration — request for comment
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

# RFC-0570: Road Runner integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`acmerobotics/road-runner`](https://github.com/acmerobotics/road-runner) (MIT) is a motion-planning library for FIRST Tech Challenge robots, widely used for autonomous routines. URML sits above a motion-planning library at the intent layer: it declares the goal and constraints, validates them against the robot's capabilities and a safety envelope, then consumes the trajectory Road Runner produces (RFC-0020). URML does not plan; it declares, validates, and consumes. This RFC asks whether the mapping is useful.

## The mapping (URML beside Road Runner)

- **Declare the goal, validate, consume the trajectory.** An autonomous routine is a goal plus constraints. URML expresses it, validates against the robot's declared capabilities and an envelope, then consumes the planned trajectory (RFC-0020 follow_trajectory). Road Runner keeps full ownership of trajectory generation and following.
- **A typed, English-friendly front door for students.** Because URML's Layer 4 turns an instruction into validated intent, a student could state an autonomous routine in plain language and have it become a checked goal handed to Road Runner.

## What is asked

Request for comment from the Road Runner maintainers:

1. Is a typed, validated intent layer (declare goal + constraints, validate, consume the trajectory) useful above Road Runner?
2. Does URML's capability + safety-envelope model fit how an FTC robot's limits are described?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the Layer-4 natural-language grammar, and the educational profile (RFC-0011). Part of Move #52; the FTC motion cluster (with the FTC SDK RFC-0566).

## Implementation note

Outreach only. The post is a GitHub Issue on `acmerobotics/road-runner` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move52.yaml`.
