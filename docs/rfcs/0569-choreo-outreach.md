---
rfc: 0569
title: Choreo integration — request for comment
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

# RFC-0569: Choreo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52).

## Summary

[`SleipnirGroup/Choreo`](https://github.com/SleipnirGroup/Choreo) (BSD-3-Clause) is a trajectory-optimization tool for FRC: it generates time-optimal trajectories subject to a robot's dynamic constraints. URML sits above a trajectory tool at the intent layer: it declares the goal and constraints, validates admissibility against the robot's capabilities and a safety envelope, then consumes the optimized trajectory. URML does not optimize trajectories; it declares, validates, and consumes (RFC-0020). This RFC asks whether the mapping is useful.

## The mapping (URML beside Choreo)

- **Declare and validate, then consume the optimized trajectory.** URML expresses the goal plus constraints, validates them against the robot's declared capabilities and an envelope, then consumes the trajectory Choreo optimizes (RFC-0020 follow_trajectory). Choreo keeps full ownership of the optimization.
- **A typed admissibility statement.** The contribution is a typed, checkable statement of what is allowed before the optimizer runs, not a competing optimizer.

## What is asked

Request for comment from the Choreo maintainers:

1. Is a typed, validated intent layer (declare goal + constraints, validate admissibility, consume the optimized trajectory) useful above Choreo?
2. Does URML's capability + safety-envelope model align with the dynamic constraints Choreo already takes?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the safety-envelope validation, and the "URML declares and validates, it does not plan" framing (Move #26). Part of Move #52; the FRC trajectory cluster (with PathPlanner RFC-0567).

## Implementation note

Outreach only. The post is a GitHub Issue on `SleipnirGroup/Choreo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move52.yaml`.
