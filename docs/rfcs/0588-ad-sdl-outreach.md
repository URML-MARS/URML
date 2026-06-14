---
rfc: 0588
title: AD-SDL (MADSci / WEI) integration — request for comment
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

# RFC-0588: AD-SDL (MADSci / WEI) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54). One RFC for the AD-SDL toolchain, covering MADSci and its predecessor WEI.

## Summary

The Argonne Self-Driving Laboratory project builds open orchestration for autonomous labs: [`AD-SDL/MADSci`](https://github.com/AD-SDL/MADSci) (Modular Autonomous Discovery for Science Instrumentation) and its predecessor [`AD-SDL/wei`](https://github.com/AD-SDL/wei) (Workcell Execution Interface), both MIT. They give a workcell a common interface to its instruments and robots and a scheduler that runs workflows across them. URML is a conceptual peer at a different granularity: it declares a typed, validated intent for a single device and addresses many through a roster. This RFC asks where the two layers meet.

## The relationship (URML beside AD-SDL)

- **Workcell orchestration above, per-device validated intent below.** MADSci/WEI orchestrate a workflow across the instruments of a workcell. URML's contribution would be the typed, statically-checkable per-device step: each node action validated against that node's declared capabilities and operating limits before the orchestrator dispatches it. The scheduler stays the scheduler; URML is the gate on each step.
- **Node descriptions toward a manifest.** A MADSci/WEI node advertises what it can do. That advertisement maps toward a URML capability manifest, which is what makes the per-step validation possible. And a workcell of many nodes maps onto URML's multi-robot roster (RFC-0286).

## What is asked

1. Does a typed, per-node validation step (action checked against the node's advertised capabilities before dispatch) fit how MADSci/WEI schedule a workflow?
2. Does a node's capability advertisement map cleanly toward a URML capability manifest, and does a workcell map onto a fleet roster?
3. Which boundary, MADSci or WEI, is the cleaner first place to look?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the multi-robot roster (RFC-0286), the five-pass validator, and the decide-then-do split (RFC-0002). Part of Move #54; the workcell-orchestration peer of the wave.

## Implementation note

Outreach only. The post is a single GitHub Issue on `AD-SDL/MADSci` (referencing WEI) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
