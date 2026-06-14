---
rfc: 0609
title: o80 (pneumatic-muscle control) integration — request for comment
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

# RFC-0609: o80 (pneumatic-muscle control) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the soft-robotics / assistive wave (Move #57).

## Summary

[`intelligent-soft-robots/o80`](https://github.com/intelligent-soft-robots/o80) (BSD-3-Clause, Max Planck Institute for Intelligent Systems) is a real-time control interface used to drive pneumatic-artificial-muscle (PAM) soft robots. It is a concrete control substrate, the kind URML is designed to declare validated intent above and dispatch to. This RFC asks whether the mapping is useful.

## The relationship (URML beside o80)

- **Declare the goal and envelope, dispatch to the PAM controller.** A PAM soft-robot subtask is a goal plus hard operating bounds (pressure limits, rate limits, reachable range). URML expresses that as a typed intent, validates it against the robot's declared capabilities and a safety envelope, then dispatches to o80's real-time interface. o80 keeps the real-time control; URML adds the typed pre-dispatch check. Pneumatic muscles have sharp safe-operating limits, which is exactly where an explicit envelope check is worth something.
- **A small, honest seam.** o80 is a focused research interface, not a general framework, so the candidate contribution is narrow and specific: the typed admissibility check ahead of the real-time loop.

## What is asked

1. Is a typed, validated intent layer (a subtask checked against the PAM robot's declared limits, then dispatched) useful above o80's real-time interface?
2. Do a PAM robot's operating bounds (pressure, rate, range) map onto a URML safety envelope cleanly?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the safety-envelope validation, and the substrate-neutral dispatch model. Completes Move #57; the pneumatic-muscle real-time-control target of the wave (sibling to the FEM-control SoftRobots RFC-0605).

## Implementation note

Outreach only. The post is a GitHub Issue on `intelligent-soft-robots/o80` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move57.yaml`.
