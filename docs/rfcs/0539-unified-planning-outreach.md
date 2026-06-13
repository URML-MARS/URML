---
rfc: 0539
title: AIPlan4EU Unified Planning integration — request for comment
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

# RFC-0539: AIPlan4EU Unified Planning integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48). This is the closest **conceptual language peer** in the wave.

## Summary

[`aiplan4eu/unified-planning`](https://github.com/aiplan4eu/unified-planning) (Apache-2.0, active, AIPlan4EU EU consortium) is the Unified Planning Library: one declarative API over many planners, with PDDL / ANML / HDDL frontends. URML and Unified Planning are both declarative languages for what a system should do, at different layers: URML declares *robot intent* validated against a physical capability manifest; Unified Planning declares a *planning problem* solved by a planner. This RFC asks how they compose.

## The mapping (URML beside Unified Planning)

- **Intent to planning problem, and back.** A URML program's goal and constraints could compile to a Unified Planning problem (the planner then produces a plan), and the resulting plan steps could be lowered back to validated URML primitives for dispatch. URML contributes the physical-capability and safety-envelope validation that a pure planning formalism does not carry; Unified Planning contributes the solver abstraction.
- **Two declarative layers, cleanly divided.** URML is grounded in a robot's declared capabilities; Unified Planning is grounded in a domain/problem model. Naming the seam lets each stay in its lane.

## What is asked

Request for comment from the Unified Planning maintainers:

1. Is a URML-intent-to-Unified-Planning-problem (and plan-back-to-validated-primitives) composition sensible?
2. Is the physical-capability / safety-envelope validation URML adds a useful complement to a planning formalism for robot deployment?
3. Which direction is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition, the `plan_path` / `follow_trajectory` consume-the-plan model (RFC-0020), the planner engagements (Move #26: PlanSys2 and others), and the decide-then-do split (RFC-0002). Part of Move #48; the closest language peer of the candidate slate.

## Implementation note

Outreach only. The post is a GitHub Issue on `aiplan4eu/unified-planning` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
