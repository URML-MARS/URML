---
rfc: 0470
title: BehaviorTree.CPP integration — request for comment
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

# RFC-0470: BehaviorTree.CPP integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition. It is the anchor of the behavior-tree / orchestration wave (Move #41).

## Summary

[`BehaviorTree/BehaviorTree.CPP`](https://github.com/BehaviorTree/BehaviorTree.CPP) (MIT, ~4.1k stars, active) is the dominant C++ behavior-tree library in robotics (it is what Nav2 runs on), with [`BehaviorTree.ROS2`](https://github.com/BehaviorTree/BehaviorTree.ROS2) wrapping action/service/topic leaf nodes. URML has a Layer-3 of its own — programs are trees of `sequence` / `parallel` / `branch` / retry over *typed, validated* primitives. The two meet cleanly: URML is the validated-intent layer, a behavior tree is the execution engine. This RFC asks how they should interop.

## The mapping (URML above / beside BehaviorTree.CPP)

Two complementary seams, both honest:

- **URML lowers to a tree.** A validated URML program (its sequence/parallel/branch/retry structure) compiles to a BehaviorTree.CPP tree; each URML primitive becomes a leaf. URML's contribution is what BT leaves do not check on their own: the typed args, the capability match, and the safety envelope, all verified *before* the tree runs.
- **A leaf dispatches a validated primitive.** Alternatively a custom BT.CPP/BT.ROS2 node wraps a single URML primitive (`move_to`, `grasp`, `set_output`), so a hand-authored tree gets validate-before-actuate per leaf.

The acid test holds: a behavior tree is control flow; URML is the typed, capability-checked intent the flow carries.

## What is asked

Request for comment from the BehaviorTree.CPP maintainers:

1. Which seam is more natural — URML compiling to a BT.CPP tree, or a BT leaf node that dispatches a validated URML primitive?
2. Does URML's sequence/parallel/branch/retry map cleanly onto BT.CPP control nodes (Sequence/Parallel/Fallback/RetryUntilSuccessful), or are there mismatches?
3. Is a validated-intent leaf node interesting for the BT.ROS2 node set?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (sequence/parallel/branch/retry, RFC-0002); the manipulation/mobility primitive families. BehaviorTree.CPP is the anchor of the behavior-tree / orchestration wave; the sibling `BehaviorTree.ROS2` is referenced, not posted to separately (org-anchor).

## Implementation note

Outreach only. The post is a GitHub Discussion on `BehaviorTree/BehaviorTree.CPP` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). `BehaviorTree.ROS2` is referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move41.yaml`.
