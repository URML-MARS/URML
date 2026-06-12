---
rfc: 0472
title: SMACC2 integration — request for comment
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

# RFC-0472: SMACC2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition.

## Summary

[`robosoft-ai/SMACC2`](https://github.com/robosoft-ai/SMACC2) (Apache-2.0, ~364 stars, active — v3.1.0) is an event-driven, asynchronous behavioral state-machine library for ROS 2 (C++). Where a behavior tree is the tree shape of URML's Layer-3, a state machine is the other shape; SMACC2's event-driven states are a natural execution target for a validated URML program, and its state/orthogonal-line model is a place URML's typed, capability-checked intent can ride. This RFC asks how they should interop.

## The mapping (URML on SMACC2)

Two complementary seams:

- **URML lowers to states/transitions.** A validated URML program's control flow (sequence → states in series, branch → guarded transitions, retry → a self-transition) maps onto a SMACC2 state machine, with URML primitives dispatched from state `onEntry`. URML supplies the typed args + capability + envelope check before the machine runs.
- **A state action dispatches a validated primitive.** A SMACC2 client-behavior wraps one URML primitive so a hand-authored state machine gets validate-before-actuate per action.

A state machine is control flow; URML is the typed, capability-checked intent the states carry.

## What is asked

Request for comment from the SMACC2 maintainers:

1. Which seam is more natural — URML lowering to a SMACC2 state machine, or a SMACC2 client-behavior that dispatches a validated URML primitive?
2. Does URML's sequence/parallel/branch/retry map onto SMACC2 states, orthogonal lines, and transitions?
3. Is a validated-intent client-behavior interesting for SMACC2 users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002); the behavior-tree anchor (RFC-0470). SMACC2 is the event-driven-state-machine vertex of the orchestration wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `robosoft-ai/SMACC2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move41.yaml`.
