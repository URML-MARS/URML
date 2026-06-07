---
rfc: 0424
title: TidyBot++ (tidybot2) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0424: TidyBot++ (tidybot2) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's navigation + manipulation primitive families and the pattern of wrapping a learned policy in a validated envelope.

## Summary

[`jimmyyhwu/tidybot2`](https://github.com/jimmyyhwu/tidybot2) (MIT, ~594 stars, active) is TidyBot++, an open-source holonomic mobile manipulator designed for robot learning (Princeton). It is a low-cost, open hardware + software mobile manipulator built specifically for imitation-learning and household tidying tasks, which makes it a clean place to show URML wrapping a learned policy in a validated intent layer. This RFC asks whether that is interesting.

## The mapping (URML above TidyBot++)

URML sits above the mobile manipulator as a validated intent layer:

- A URML intent ("tidy this table: put the cups in the bin") declares the goal and the envelope; a learned policy on TidyBot++ produces the low-level holonomic base + arm control, and URML validates the request against the declared capabilities before the policy acts.
- This is the decide-then-do split applied to learning: the policy is the actuator, URML is the typed, validated intent and the safety envelope around it.
- A holonomic mobile manipulator is a rich manifest case (omnidirectional base + arm + gripper + object vocabulary).

## What is asked

Request for comment from the TidyBot++ maintainers:

1. Is wrapping a learned mobile-manipulation policy in a validated intent layer + envelope interesting in the robot-learning context?
2. What should a URML capability manifest declare to describe a holonomic mobile manipulator honestly (drive type, arm reach/DOF, gripper + graspable classes, workspace bounds)?
3. Is the policy/control interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's navigation + manipulation families; the decide-then-do split applied to learned control (the drone-RL engagement, RFC-0417); the mobile-manipulation anchor (RFC-0422). TidyBot++ is the robot-learning vertex of the mobile-manipulation wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `jimmyyhwu/tidybot2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move35.yaml`.
