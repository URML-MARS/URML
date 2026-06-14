---
rfc: 0580
title: FreeRTOS integration — request for comment
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

# RFC-0580: FreeRTOS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). A note on altitude up front: URML sits far above an RTOS, so the seam here is deliberately narrow.

## Summary

[`FreeRTOS/FreeRTOS`](https://github.com/FreeRTOS/FreeRTOS) (MIT) is the most widely deployed real-time operating system for microcontrollers. URML is a robot-intent language that lives well above an RTOS; it is not a competitor to FreeRTOS and not a layer FreeRTOS needs. The one concrete place the two touch is execution: URML has a minimal MCU execution shape (RFC-0018 minimal_node) for constrained targets, and FreeRTOS is the canonical substrate such an executor would run on.

## The relationship (URML beside FreeRTOS)

- **The narrow seam: a URML executor as an RTOS task.** URML validates intent (mostly off the MCU, ahead of time) and dispatches. On a constrained target the dispatched, already-validated plan runs in a small executor. The honest question is whether that executor sits naturally as a FreeRTOS task and uses FreeRTOS primitives, not whether FreeRTOS should know anything about URML.
- **No upward dependency.** Nothing here asks FreeRTOS to change. The relationship is URML-targets-FreeRTOS, not the reverse.

## What is asked

1. For a constrained MCU target, is a small, pre-validated intent executor a sensible thing to run as a FreeRTOS task, and are there primitives or patterns you would point such an executor toward?
2. Is the "validate ahead of time off the MCU, execute a checked plan on it" split a reasonable way to keep an intent layer honest about RTOS constraints?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's minimal_node MCU execution shape (RFC-0018), the substrate-neutral dispatch model, and the decide-then-do split (RFC-0002). Part of Move #53; the canonical general-purpose RTOS of the wave (with NuttX RFC-0581, RIOT RFC-0582).

## Implementation note

Outreach only. The post is a GitHub Issue on `FreeRTOS/FreeRTOS` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move53.yaml`.
