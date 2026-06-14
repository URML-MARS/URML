---
rfc: 0566
title: FTC Robot Controller integration — request for comment
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

# RFC-0566: FTC Robot Controller integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the education / competition wave (Move #52). FTC is the largest student-robotics control surface in the wave.

## Summary

[`FIRST-Tech-Challenge/FtcRobotController`](https://github.com/FIRST-Tech-Challenge/FtcRobotController) (BSD-3-Clause-Clear) is the official robot-controller SDK for FIRST Tech Challenge: tens of thousands of students program competition robots with it each season. URML is a small, Apache-2.0 language for robot intent: an instruction (including an English one) becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. This RFC asks whether a typed, validated intent layer is a useful teaching companion above an FTC op-mode.

## The mapping (URML beside the FTC SDK)

- **A typed, English-friendly intent layer for student robots.** Students write op-modes against the SDK. URML adds a small layer at the top: a declared intent (drive here, grab that, within these limits) that is checked against the robot's declared capabilities before it runs, and that can start from an English sentence. The SDK stays the runtime; URML makes "what did we ask the robot to do, and why was that rejected" explicit and checkable, which is exactly the kind of thing that helps a student team reason about their robot.
- **Educational profile fit.** URML already has an educational profile direction (RFC-0011); FTC is a natural place to test whether a validated-intent layer earns its keep in a classroom.

## What is asked

Request for comment from the FTC SDK maintainers:

1. Is a typed, validated intent layer (declare intent, check against the robot's capabilities, optionally from English) a useful teaching companion above an FTC op-mode?
2. Does URML's capability manifest map onto how an FTC robot's configuration is described?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the capability manifest, the five-pass validator, and the educational profile (RFC-0011). Anchor of Move #52; FTC is the largest student-competition control SDK found in the 2026-06-13 candidate search.

## Implementation note

Outreach only. The post is a GitHub Issue on `FIRST-Tech-Challenge/FtcRobotController` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause-Clear). Tracked in `examples/lighthouses/outreach-move52.yaml`.
