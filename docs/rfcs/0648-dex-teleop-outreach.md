---
rfc: 0648
title: dex-teleop (GeneralTrajectory/dex-teleop) integration — request for comment
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

# RFC-0648: dex-teleop integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #65 (domain-vertical lane).

## Summary

[`GeneralTrajectory/dex-teleop`](https://github.com/GeneralTrajectory/dex-teleop) is a VR-based dexterous teleoperation system: a human's tracked motion drives an arm plus a multi-fingered hand, and the resulting demonstrations are recorded for imitation learning. URML is a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capability manifest and safety envelope before it executes. Teleoperation is an interesting case for that check, because a human in the loop is not a guarantee the commanded pose is reachable or the commanded grasp force is within the hand's limit.

## The relationship (URML beside dex-teleop)

A VR command is a pose and a grasp the operator intends. URML can declare the arm's reach and the hand's per-finger force and joint limits, and check the relayed command against that declaration before it reaches the actuators. The human decides what to attempt; URML confirms the attempt is admissible on this specific arm and hand. It also means the recorded demonstrations are admissible-by-construction, which matters when they become training data.

URML does not do the tracking, the retargeting, or the recording. It is the admissibility check between the retargeted command and the hardware.

## What is asked

1. In a teleoperation loop with a human driving, is a declared arm-and-hand capability check on the relayed command a useful guardrail, or does the operator plus the retargeting already keep commands in-envelope in practice?
2. Would a small worked example mapping a dex-teleop arm-and-hand command onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a VR dexterous-teleoperation system. The repository does not carry a recognized license file, so this is a cross-reference, not a code-reuse proposal; US. Part of Move #65.

## Implementation note

Outreach only. The post is a GitHub Issue on `GeneralTrajectory/dex-teleop` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move65.yaml`.
