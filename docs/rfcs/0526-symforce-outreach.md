---
rfc: 0526
title: SymForce integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0526: SymForce integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`symforce-org/symforce`](https://github.com/symforce-org/symforce) (Apache-2.0, ~1.6k stars, active, Skydio-originated) is a library for symbolic computation, code generation, and nonlinear optimization — the factor-graph engine behind state estimators and SLAM back-ends. URML consumes the estimate such an engine produces; it does not estimate. A SymForce-powered estimator gives the pose URML's frames and constraints resolve against. This RFC asks whether the seam is useful.

## The mapping (URML beside SymForce)

- **The estimate, consumed.** SymForce optimizes the factor graph that yields a robot's state estimate. URML resolves its frames (RFC-0290) and validates intent against the active safety envelope using that estimate. URML is the declarative intent + envelope layer above the estimator; SymForce is the optimization that produces the estimate.

## What is asked

Request for comment from the SymForce maintainers:

1. Is "a SymForce-powered estimator produces the state estimate, URML consumes it to resolve frames and validate intent" a sensible layering?
2. Is this the right altitude to engage (an optimization library), or is the seam better at a SLAM / estimator that wraps SymForce?
3. Which first seam, if any, is worth pursuing?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's frame-transform graph (RFC-0290), the safety envelope, and the "URML consumes your estimate" posture (Move #25). Part of Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `symforce-org/symforce` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
