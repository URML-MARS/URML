---
rfc: 0678
title: Safe-ROS (dianabenjumea/Safe-ROS) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-18
updated: 2026-08-18
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

# RFC-0678: Safe-ROS (dianabenjumea/Safe-ROS) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the nuclear / hazmat remote-handling wave (Move #70).

## Summary

[`dianabenjumea/Safe-ROS`](https://github.com/dianabenjumea/Safe-ROS) (University of Manchester) is an architecture for autonomous robots in safety-critical domains: it composes FRET (formal requirements), MCAPL (verified agent reasoning), and Dafny (formal verification) so that a Safety System stops the robot before an unsafe move, demonstrated in a radiation-store Gazebo simulation. That "refuse before the unsafe move" contract is the same idea at the center of URML, reached by a different route. This is a request for comment on whether the two are complementary.

## The relationship (URML beside Safe-ROS)

- **Same goal, different weight class.** Safe-ROS derives strong guarantees through formal verification. URML does a lightweight, declarative, static admissibility check: a robot declares a capability manifest and a safety envelope, and URML refuses an action that falls outside them before dispatch. The URML check is cheap and portable across substrates; it is necessary, not sufficient, and does not replace formal verification.
- **A possible portable front-end.** A declarative capability + envelope manifest could act as a portable, human-readable front-end declaration that a formally-verified safety system like Safe-ROS enforces underneath, so the same declared intent travels across robots and toolchains.
- **Neutral by construction.** URML is substrate- and model-neutral; it composes above the action rather than depending on any one verification stack.

## What is asked

1. Is a lightweight, declarative capability + envelope check a useful complement to a formally-verified safety system, or does the formal layer already subsume it in your view?
2. Would a small worked example expressing one Safe-ROS safety requirement as a URML envelope (validated, no execution) be worth comparing notes on?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #70 nuclear / hazmat remote-handling wave; the closest conceptual sibling in the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `dianabenjumea/Safe-ROS` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move70.yaml`.
