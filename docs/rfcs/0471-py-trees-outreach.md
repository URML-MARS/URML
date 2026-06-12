---
rfc: 0471
title: py_trees integration — request for comment
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

# RFC-0471: py_trees integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition and its Python reference tooling.

## Summary

[`splintered-reality/py_trees`](https://github.com/splintered-reality/py_trees) (BSD-3-Clause, ~610 stars, active) is the leading Python behavior-tree library, with [`py_trees_ros`](https://github.com/splintered-reality/py_trees_ros) for ROS 2. URML's Layer-3 composition (sequence/parallel/branch/retry over typed, validated primitives) and URML's Python reference tooling make py_trees the most natural Python target for "validated URML program → a behavior tree you can execute and introspect." This RFC asks how they should interop.

## The mapping (URML lowered to py_trees)

Two complementary seams:

- **URML lowers to a py_trees tree.** A validated URML program compiles to a py_trees composite (Sequence / Parallel / Selector) with URML primitives as leaf behaviours. URML supplies what the tree does not: typed args, capability match, and safety envelope, checked before the tree ticks.
- **A leaf behaviour dispatches a validated primitive.** A hand-authored py_trees tree gets a custom behaviour that wraps one URML primitive, so validate-before-actuate happens per leaf.

Because both URML's reference tooling and py_trees are Python, a thin adapter is small and idiomatic.

## What is asked

Request for comment from the py_trees maintainer:

1. Which seam is more natural — URML compiling to a py_trees composite, or a py_trees behaviour that dispatches a validated URML primitive?
2. Does URML's sequence/parallel/branch/retry map cleanly onto py_trees composites + decorators?
3. Is a validated-intent behaviour interesting for the py_trees_ros node set?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002) and Python reference tooling; the behavior-tree anchor (RFC-0470). py_trees is the Python-behavior-tree vertex of the orchestration wave; the sibling `py_trees_ros` is referenced, not posted to separately.

## Implementation note

Outreach only. The post is a GitHub Discussion on `splintered-reality/py_trees` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). `py_trees_ros` is referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move41.yaml`.
