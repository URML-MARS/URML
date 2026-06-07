---
rfc: 0420
title: CERLAB UAV Autonomy (CMU) integration — request for comment
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

# RFC-0420: CERLAB UAV Autonomy (CMU) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type and ROS 2 runtime. Tier B.

## Summary

[`Zhefan-Xu/CERLAB-UAV-Autonomy`](https://github.com/Zhefan-Xu/CERLAB-UAV-Autonomy) (MIT, ~837 stars) is a modular UAV autonomy framework from CMU's CERLAB, spanning perception, mapping, planning, and control as composable ROS modules. A clean modular autonomy framework is a natural place to align URML's typed intent with each layer. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above CERLAB UAV Autonomy)

URML sits above the framework as a validated intent layer:

- URML's `aerial` drive type and ROS 2 runtime meet the framework on its ROS module surface; "navigate to the target and avoid obstacles" lowers onto the planning/control modules.
- The framework's perception/mapping modules are the kind of `detect` source URML consumes: a detection binds a target a downstream action consumes (decide-then-do).
- Validate-before-actuate refuses an out-of-envelope request before dispatch.

## What is asked

Request for comment from the CERLAB UAV Autonomy maintainers:

1. Does URML's typed intent map cleanly onto the framework's modular ROS surface, and where should it target it?
2. What should a URML capability manifest declare to describe a modular autonomy UAV honestly (drive type, altitude/speed limits, sensor suite, operating bounds)?
3. Is a validated natural-language layer interesting for the framework's users?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and ROS 2 runtime; the `detect`-then-act split; the aerial-autonomy anchor (RFC-0412). CERLAB UAV Autonomy is the modular-framework vertex of the aerial wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `Zhefan-Xu/CERLAB-UAV-Autonomy` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move34.yaml`.
