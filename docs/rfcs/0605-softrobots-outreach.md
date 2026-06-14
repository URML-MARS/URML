---
rfc: 0605
title: SOFA SoftRobots integration — request for comment
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

# RFC-0605: SOFA SoftRobots integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the soft-robotics / assistive wave (Move #57).

## Summary

[`SofaDefrost/SoftRobots`](https://github.com/SofaDefrost/SoftRobots) (LGPL-3.0, INRIA Defrost) is the SOFA plugin for modeling and controlling soft robots: FEM models of pneumatic and cable-driven soft structures, with inverse control that computes the actuation to reach a target. URML is a validated-intent layer that sits above a controller like this: it declares the soft-robot subtask goal and its operating envelope, and consumes the actuation the SOFA model computes. URML does not model deformation or compute control; it declares and checks. This is a consume note (cross-citation only, since SoftRobots is LGPL-3.0).

## The relationship (URML beside SoftRobots)

- **Declare the goal and envelope, consume the computed actuation.** A soft-robot subtask (reach this tip pose, within these pressure and curvature limits) is a goal plus constraints. URML expresses that, validates it against the soft robot's declared capabilities and operating envelope, then consumes the actuation SoftRobots' inverse control produces (RFC-0020). The FEM modeling and the inverse control stay entirely with SoftRobots.
- **An honest fit.** Soft robots are not rigid manipulators, and URML's value here is narrow: a typed statement of the subtask goal and the admissible envelope, checked before the computed actuation is trusted. Given the LGPL-3.0 license this proposes no shared code, only a layering relationship.

## What is asked

1. Is a typed, validated subtask-intent layer (declare goal + envelope, validate, consume the computed actuation) useful above SoftRobots' inverse control?
2. Does a soft robot's operating envelope (pressure, curvature, tip-pose limits) map onto a URML capability manifest + safety envelope cleanly enough to be worth sharing?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the capability manifest, and the safety-envelope validation. Anchor of Move #57; the soft-robot FEM-control target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `SofaDefrost/SoftRobots` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is LGPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move57.yaml`.
