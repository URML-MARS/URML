---
rfc: 0694
title: pyrobosim (sea-bass/pyrobosim) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-03
updated: 2026-09-03
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

# RFC-0694: pyrobosim (sea-bass/pyrobosim) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the manipulation/control wave (Move #73).

## Summary

[`sea-bass/pyrobosim`](https://github.com/sea-bass/pyrobosim) is a lightweight 2D mobile-robot behavior-prototyping framework with a world/entity model, task-and-motion actions (navigate, pick, place), and an optional ROS 2 action/service interface. Because it is the place where a planned action sequence is assembled before it is dispatched, URML's validate-before-actuate gate has a natural home: the robot declares a capability manifest and the world declares its constraints, and URML checks a planned sequence is admissible before it runs. This is a request for comment.

## The relationship (URML beside pyrobosim)

- **Decide, then check, then do.** A planner (or a person) assembles a navigate/pick/place sequence in pyrobosim; URML checks each step is admissible against the declared robot capabilities and the world model (a location exists, an object class is graspable, a motion is within reach) before dispatch. URML does the check; pyrobosim keeps the simulation and the ROS 2 dispatch.
- **A clean sandbox for the gate.** Because pyrobosim already models the robot and the world as declared entities, mapping them onto a URML manifest + envelope is close to one-to-one, and the check is legible in a lightweight, ROS 2-connected sandbox.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the action interface rather than depending on internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared capability manifest + world/safety envelope, checked before a planned action sequence is dispatched, be a useful guard in a prototyping sandbox like pyrobosim?
2. Would a small worked example mapping a pyrobosim task sequence onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, Layer-3 behavior composition, and the static validate-before-actuate gate. Part of the Move #73 manipulation/control wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `sea-bass/pyrobosim` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move73.yaml`.
