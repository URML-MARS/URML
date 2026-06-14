---
rfc: 0560
title: F1TENTH (system + gym) integration — request for comment
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

# RFC-0560: F1TENTH (system + gym) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51). One RFC for the F1TENTH platform, covering both the on-car system and the gym.

## Summary

F1TENTH (University of Pennsylvania) is a widely-used 1/10-scale autonomous racing platform for research and teaching: [`f1tenth/f1tenth_system`](https://github.com/f1tenth/f1tenth_system) (the on-car stack) and [`f1tenth/f1tenth_gym`](https://github.com/f1tenth/f1tenth_gym) (the simulation environment), both MIT. URML is interesting at the intent layer: it declares a racing goal and its constraints, validates them against the car's capabilities and a safety envelope, and consumes the planned trajectory. URML does not plan a racing line; it declares the goal and validates admissibility. This RFC asks whether the mapping is useful.

## The mapping (URML beside F1TENTH)

- **Declare the goal, validate, consume the trajectory.** A racing task (follow the line, overtake within limits) is a goal plus constraints. URML expresses that goal, validates it against the car's declared capabilities and a safety envelope, then consumes the trajectory the planner produces (RFC-0020 follow_trajectory). The planner stays the planner; URML is the typed declaration and the admissibility check.
- **Same intent, car and gym.** Because URML is runtime-neutral, the same declared-and-validated intent applies whether the target is `f1tenth_system` on the car or `f1tenth_gym` in simulation, which is a natural fit for a teaching loop that moves between the two.

## What is asked

Request for comment from the F1TENTH maintainers:

1. Is a typed, validated intent layer (declare goal + constraints, validate, consume the trajectory) useful on the F1TENTH platform?
2. Does a runtime-neutral intent that targets both the car and the gym fit how F1TENTH is taught and researched?
3. Which boundary, system or gym, is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the safety-envelope validation, and the educational profile (RFC-0011). Part of Move #51; F1TENTH is the academic-racing platform of the wave.

## Implementation note

Outreach only. The post is a single GitHub Issue on `f1tenth/f1tenth_system` (referencing the gym) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move51.yaml`.
