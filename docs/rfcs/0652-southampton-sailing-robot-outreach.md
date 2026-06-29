---
rfc: 0652
title: Southampton sailing-robot (Maritime-Robotics-Student-Society/sailing-robot) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-29
updated: 2026-06-29
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

# RFC-0652: Southampton sailing-robot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #65 (domain-vertical lane).

## Summary

[`Maritime-Robotics-Student-Society/sailing-robot`](https://github.com/Maritime-Robotics-Student-Society/sailing-robot) (University of Southampton) is the autonomy stack for an autonomous sailing vessel: it reads wind and sea state and commands helm and sail trim to hold a course. URML is a small Apache-2.0 language for declaring what a vehicle can do and checking an intended action against that declaration before it runs. A sailing robot is an unusual and instructive case, because the admissible action depends heavily on a declared operating envelope (sea state, no-go zones, sail limits) that changes with conditions.

## The relationship (URML beside sailing-robot)

The autonomy decides a helm and trim command to make progress; URML can check that command against a declared envelope: the platform's sail and rudder limits, and a mission-declared operating boundary or sea-state ceiling. The check sits between the control decision and the actuators, and does not touch the wind estimation or the course logic.

URML does not sail, estimate wind, or steer. It declares the vessel's envelope and confirms a commanded helm-and-trim action is inside it before dispatch.

## What is asked

1. For a sailing-vessel autonomy stack, is a declared envelope check (sail and rudder limits, operating boundary, sea-state ceiling) on a helm-and-trim command useful before dispatch, or is that already handled inside the controller?
2. Would a small worked example mapping a sailing command onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to an autonomous sailing-vessel stack. The repository does not carry a recognized license file, so this is a cross-reference, not a code-reuse proposal; University of Southampton (student maritime robotics society), UK. Part of Move #65.

## Implementation note

Outreach only. The post is a GitHub Issue on `Maritime-Robotics-Student-Society/sailing-robot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move65.yaml`.
