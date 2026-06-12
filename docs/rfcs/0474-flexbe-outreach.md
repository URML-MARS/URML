---
rfc: 0474
title: FlexBE integration — request for comment
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

# RFC-0474: FlexBE integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition. Tier B.

## Summary

[`FlexBE/flexbe_behavior_engine`](https://github.com/FlexBE/flexbe_behavior_engine) (BSD, ~72 stars, active) is a hierarchical finite-state-machine engine for ROS 2 with an operator-in-the-loop model — a human can supervise, pause, and intervene mid-behavior. URML's validate-before-actuate is a natural complement to that supervisory model: a validated typed intent is exactly what an operator wants to see and approve before a state actuates. This RFC asks how they should interop.

## The mapping (URML on FlexBE)

Two complementary seams:

- **URML lowers to a FlexBE state machine.** A validated URML program's control flow maps to FlexBE states + outcomes; URML primitives are dispatched from state execution, with the typed args + capability + envelope check verified before the behavior is started.
- **A FlexBE state dispatches a validated primitive.** A FlexBE state wraps one URML primitive so the operator-in-the-loop engine gets validate-before-actuate per state, and the validation verdict is something the operator UI can surface.

The operator-supervision model and validate-before-actuate reinforce each other: one is a human gate, the other a static gate.

## What is asked

Request for comment from the FlexBE maintainers:

1. Which seam is more natural — URML lowering to a FlexBE state machine, or a FlexBE state that dispatches a validated URML primitive?
2. Could the validation verdict (accepted / refused + reason) surface in the FlexBE operator UI before a state runs?
3. Does URML's sequence/parallel/branch/retry map cleanly onto FlexBE's hierarchical states + outcomes?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002) and its validate-before-actuate audit trail; the behavior-tree anchor (RFC-0470). FlexBE is the operator-in-the-loop-FSM vertex of the orchestration wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `FlexBE/flexbe_behavior_engine` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD). Tracked in `examples/lighthouses/outreach-move41.yaml`.
