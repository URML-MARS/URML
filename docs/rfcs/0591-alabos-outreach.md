---
rfc: 0591
title: AlabOS (CederGroupHub) integration — request for comment
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

# RFC-0591: AlabOS (CederGroupHub) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54).

## Summary

[`CederGroupHub/alabos`](https://github.com/CederGroupHub/alabos) (MIT, Lawrence Berkeley National Laboratory) is the task and device orchestration system behind the A-Lab autonomous materials lab: it maps task graphs onto physical devices and runs synthesis-and-characterization campaigns end to end. URML is a peer at the per-device granularity, the typed validated step a task graph dispatches. This RFC asks where the two meet.

## The relationship (URML beside AlabOS)

- **Task graph above, validated device step below.** AlabOS schedules a task graph across the lab's devices. URML's candidate role is the typed, pre-dispatch validation of each device-facing task: checked against that device's declared capabilities and limits before AlabOS sends it. The orchestration, recovery, and campaign logic stay with AlabOS.
- **Device definitions toward a manifest.** AlabOS already describes its devices and their tasks; that description maps toward a URML capability manifest, which is what a per-task validation would check against.

## What is asked

1. Is a typed, per-task validation step (task checked against the device's declared capabilities before dispatch) useful in the AlabOS scheduling model?
2. Do AlabOS device/task definitions map toward a URML capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the multi-robot roster (RFC-0286), and the decide-then-do split (RFC-0002). Part of Move #54; the autonomous-materials-lab orchestration peer of the wave (with AD-SDL RFC-0588).

## Implementation note

Outreach only. The post is a GitHub Issue on `CederGroupHub/alabos` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
