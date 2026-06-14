---
rfc: 0561
title: ForzaETH race_stack integration — request for comment
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

# RFC-0561: ForzaETH race_stack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51).

## Summary

[`ForzaETH/race_stack`](https://github.com/ForzaETH/race_stack) (MIT, ETH Zurich) is a full autonomous-racing software stack (perception, estimation, planning, control) for scaled racing. URML sits above a stack like this at the intent layer: it declares the racing goal and constraints, validates admissibility against the car's capabilities and a safety envelope, and consumes the trajectory the stack plans. URML does not plan; it declares and validates. This RFC asks whether the mapping is useful.

## The mapping (URML beside race_stack)

- **URML declares and validates; race_stack plans and drives.** A racing objective is a goal plus constraints (stay on track, respect dynamic limits, overtake only where admissible). URML expresses that, validates it against the car's declared capabilities and an envelope, then consumes the planned trajectory (RFC-0020). The stack keeps full ownership of how the line is computed and followed.
- **A typed admissibility check.** The value URML adds is a typed, statically-checkable statement of what is allowed before the planner runs, not a competing planner.

## What is asked

Request for comment from the ForzaETH maintainers:

1. Is a typed, validated intent layer (declare goal + constraints, validate admissibility, consume the trajectory) useful above a full racing stack?
2. Does URML's capability + safety-envelope model fit how race_stack bounds a maneuver?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the safety-envelope validation, and the "URML declares and validates, it does not plan" framing (Move #26). Part of Move #51; sibling to F1TENTH (RFC-0560).

## Implementation note

Outreach only. The post is a GitHub Issue on `ForzaETH/race_stack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move51.yaml`.
