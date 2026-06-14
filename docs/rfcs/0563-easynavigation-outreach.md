---
rfc: 0563
title: EasyNavigation integration — request for comment
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

# RFC-0563: EasyNavigation integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51).

## Summary

[`EasyNavigation/EasyNavigation`](https://github.com/EasyNavigation/EasyNavigation) (Apache-2.0) is a navigation framework for mobile robots, designed as a lighter, modular alternative in the autonomous-navigation space. URML sits above a navigation framework at the intent layer: it declares a navigation goal and its constraints, validates them against the robot's capabilities and a safety envelope, and lets the framework plan and execute. URML does not navigate; it declares and validates. This RFC asks whether the mapping is useful.

## The mapping (URML beside EasyNavigation)

- **Declare the goal, validate, the framework navigates.** A navigation task is a goal plus constraints (reach the pose, respect keep-out zones and speed limits). URML expresses that, validates it against the robot's declared capabilities and a safety envelope, then hands off to EasyNavigation to plan and execute (RFC-0020). The framework keeps full ownership of planning and control.
- **A typed front door.** URML gives a navigation framework a typed, declarative, runtime-neutral way to state a goal and have it checked before planning, including from a natural-language instruction.

## What is asked

Request for comment from the EasyNavigation maintainers:

1. Is a typed, validated intent layer (declare goal + constraints, validate, then navigate) a useful front door to EasyNavigation?
2. Does URML's capability + safety-envelope model fit how EasyNavigation bounds a navigation task?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the Layer-4 natural-language grammar, and the safety-envelope validation. Part of Move #51; the general mobile-navigation framework of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `EasyNavigation/EasyNavigation` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move51.yaml`.
