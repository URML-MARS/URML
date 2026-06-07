---
rfc: 0446
title: Raven-II (UW Biorobotics) integration — request for comment
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

# RFC-0446: Raven-II (UW Biorobotics) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the bimanual work (RFC-0010). Tier B. **Scope: research only. URML makes no clinical claim.**

## Summary

[`uw-biorobotics/raven2`](https://github.com/uw-biorobotics/raven2) (LGPL-3.0, ~59 stars) is the control software for Raven-II, the open-hardware surgical-research robot from the University of Washington Biorobotics Lab — one of the few genuinely open surgical-robot hardware platforms. Although the repo is dormant, Raven-II remains a reference open dual-arm surgical-research platform, and a validated research intent layer above it is a natural fit. This RFC asks whether that is interesting.

## The mapping (URML above Raven-II)

URML sits above the research robot as a validated intent layer:

- URML's ROS runtime meets Raven-II on its control/ROS surface; a research subtask lowers onto the two arms as typed primitives, and URML's `arm` selector + `bimanual` primitive (RFC-0010) address the dual-arm platform.
- Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion — a research safety boundary.
- The Raven-II manifest (two arms, instruments, reach/DOF, workspace) exercises URML's bimanual capability model on open surgical hardware.

## What is asked

Request for comment from the UW Biorobotics / Raven-II maintainers:

1. Is a validated research intent layer above Raven-II interesting for the lab's surgical-robotics research?
2. What should a URML capability manifest declare to describe Raven-II honestly (two arms, instruments, reach/DOF, workspace bounds)?
3. Does URML's `arm` selector + `bimanual` primitive map cleanly onto Raven-II's two arms?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's ROS runtime; the manipulation family (Move #27) and the bimanual work (RFC-0010); the surgical-research anchor (RFC-0440). Raven-II is the open-surgical-hardware vertex of the medical / surgical research wave (Tier B; the repo is dormant, but the platform is a reference).

## Implementation note

Outreach only. The post is a GitHub Issue on `uw-biorobotics/raven2` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front. The repo is LGPL-3.0; URML proposes nothing under it and asks no license change. Research framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
