---
rfc: 0649
title: Sandia spot_bt_ros (sandialabs/spot_bt_ros) integration — request for comment
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

# RFC-0649: Sandia spot_bt_ros integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #65 (domain-vertical lane).

## Summary

[`sandialabs/spot_bt_ros`](https://github.com/sandialabs/spot_bt_ros) (Sandia National Laboratories) is a ROS 2 behavior-tree layer for driving a Boston Dynamics Spot through inspection missions, with the tree structuring planning and execution. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A behavior tree is a clean place for that check, because each leaf that commands motion is a discrete action the tree is about to dispatch, and that is exactly the granularity URML validates at.

## The relationship (URML beside spot_bt_ros)

A behavior tree decides what to do next; URML answers whether the action that leaf is about to dispatch is admissible on this Spot in this environment. Declare the platform's mobility envelope and the mission's keep-out and standoff constraints, and URML checks a traverse or a manipulation leaf against that declaration before the tree ticks it into motion. In an inspection setting where the environment may be hazardous, a static admissibility check in front of each dispatched action is a natural complement to the tree's own safety conditions.

URML does not replace the tree, the planner, or the Spot SDK. It is the per-action admissibility gate that sits under a leaf that commands motion.

## What is asked

1. For a behavior-tree inspection stack, is a declared-capability and envelope check at the action-leaf boundary a useful layer alongside the tree's own guard conditions, or is that already covered by how the tree is authored?
2. Would a small worked example mapping a Spot inspection action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a behavior-tree inspection stack for a quadruped. The repository does not carry a recognized license file, so this is a cross-reference, not a code-reuse proposal; Sandia National Laboratories, US. Part of Move #65.

## Implementation note

Outreach only. The post is a GitHub Issue on `sandialabs/spot_bt_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move65.yaml`.
