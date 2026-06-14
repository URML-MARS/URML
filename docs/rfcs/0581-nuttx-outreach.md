---
rfc: 0581
title: Apache NuttX integration — request for comment
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

# RFC-0581: Apache NuttX integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). Same altitude caveat as the rest of the RTOS targets: URML sits well above the OS; the seam is execution.

## Summary

[`apache/nuttx`](https://github.com/apache/nuttx) (Apache-2.0) is a real-time operating system with a strong POSIX-compatible API, used on everything from tiny MCUs to flight controllers (it is the OS under PX4, which URML already maps onto as a substrate). That POSIX surface is interesting: a minimal URML executor (RFC-0018 minimal_node) is easier to host where standard POSIX-like primitives exist.

## The relationship (URML beside NuttX)

- **POSIX eases the executor.** URML validates intent ahead of time and dispatches a checked plan. On a constrained target that plan runs in a small executor; NuttX's POSIX-like API is a friendly host for one. Because PX4 runs on NuttX and URML already targets PX4, there is a concrete existing path here, not just a hypothetical.
- **URML targets NuttX, not the reverse.** Nothing here asks NuttX to depend on or know about URML.

## What is asked

1. Does NuttX's POSIX-compatible surface make it a natural host for a small, pre-validated intent executor on constrained targets?
2. Given that PX4 already runs on NuttX, is the PX4-via-URML path the most sensible first place to look at this seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's minimal_node MCU execution shape (RFC-0018), the PX4 reference-runtime mapping, and the substrate-neutral dispatch model. Part of Move #53; the POSIX-RTOS target of the wave (with FreeRTOS RFC-0580).

## Implementation note

Outreach only. The post is a GitHub Issue on `apache/nuttx` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move53.yaml`.
