---
rfc: 0597
title: UNav-Sim integration — request for comment
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

# RFC-0597: UNav-Sim integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the inspection-robotics wave (Move #55).

## Summary

[`open-airlab/UNav-Sim`](https://github.com/open-airlab/UNav-Sim) (Aalborg University) is an underwater robotics simulator with a controller and a trained planner for pipe-following inspection on a BlueROV2 Heavy. A subsea inspection task is a goal plus constraints (follow this pipe, hold standoff, respect the operating envelope), which is what URML declares and validates. This RFC asks whether the mapping is useful.

## The mapping (URML beside UNav-Sim)

- **Declare the inspection intent, validate, consume the plan.** URML expresses the underwater-inspection goal plus its operating envelope, validates it against the vehicle's declared capabilities, then consumes the trajectory UNav-Sim's controller and planner produce (RFC-0020). URML does not plan or control; it declares and checks.
- **A trained planner that declares its envelope.** UNav-Sim uses a learned planner. URML's LearnedPolicy direction (RFC-0383) is exactly the idea that a trained policy can declare the operating envelope it was trained for, so an intent can be validated against it before the policy is trusted to drive. That is the more interesting of the two seams here.

## What is asked

1. Is a typed, validated inspection-intent layer (declare goal + envelope, validate, consume the plan) useful above UNav-Sim?
2. Could the trained planner declare a training/operating envelope a URML intent is checked against (RFC-0383)?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's marine runtime, the plan_path / follow_trajectory consume model (RFC-0020), the LearnedPolicy envelope (RFC-0383), and the safety-envelope validation. Part of Move #55; the underwater-inspection target of the wave (with the BlueROV2 stack RFC-0598).

## Implementation note

Outreach only. The post is a GitHub Issue on `open-airlab/UNav-Sim` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The repository's license is non-standard (unrecognized by GitHub), so the post states that, makes no licensing request, and proposes no code reuse. Tracked in `examples/lighthouses/outreach-move55.yaml`.
