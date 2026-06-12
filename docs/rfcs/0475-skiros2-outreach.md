---
rfc: 0475
title: SkiROS2 integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0475: SkiROS2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition and capability manifest. Tier B.

## Summary

[`RVMI/skiros2`](https://github.com/RVMI/skiros2) (open, BSD-style, ~225 stars, active) is a skill-based platform for ROS 2 from the Aalborg University RVMI lab — robots are programmed as parameterized *skills* with pre/post-conditions over a world model, composed and planned over. This is the closest match in the wave to URML's own posture: a skill with declared parameters and conditions is very near a URML primitive with a typed signature and a capability/envelope precondition. This RFC asks how they should interop.

## The mapping (URML and SkiROS2 skills)

URML's typed intent and a SkiROS2 skill are two views of the same thing:

- **A URML primitive ↔ a SkiROS2 skill.** URML's `move_to` / `grasp` / `set_output` with their capability preconditions line up with SkiROS2 parameterized skills with world-model pre/post-conditions; a validated URML program could populate or drive a SkiROS2 skill sequence.
- **URML's capability + envelope as skill preconditions.** URML's manifest checks (capability match, workspace bounds) are exactly the kind of precondition SkiROS2 reasons over before executing a skill — a place URML's static gate complements SkiROS2's world-model gate.

## What is asked

Request for comment from the SkiROS2 maintainers:

1. How close is a URML primitive (typed args + capability/envelope precondition) to a SkiROS2 skill (parameters + world-model conditions) — and could one drive the other?
2. Could URML's capability/envelope checks serve as (or feed) SkiROS2 skill preconditions?
3. Where is the cleanest seam — URML lowering to a skill sequence, or a SkiROS2 skill that dispatches a validated URML primitive?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002), capability manifest, and safety envelope; the behavior-tree anchor (RFC-0470). SkiROS2 is the skill-based-platform vertex of the orchestration wave (Tier B) and the closest peer to URML's typed-primitive posture.

## Implementation note

Outreach only. The post is a GitHub Issue on `RVMI/skiros2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask. Tracked in `examples/lighthouses/outreach-move41.yaml`.
