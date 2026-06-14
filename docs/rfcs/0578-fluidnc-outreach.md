---
rfc: 0578
title: FluidNC integration — request for comment
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

# RFC-0578: FluidNC integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53); the CNC / motion-control corner.

## Summary

[`bdring/FluidNC`](https://github.com/bdring/FluidNC) is a CNC firmware for the ESP32 that drives multi-axis motion machines. URML is a small, Apache-2.0 language for robot intent, and a machining or motion job is a goal plus hard machine limits, which is exactly what URML declares and validates before dispatch. FluidNC is the firmware that executes the motion.

## The mapping (URML beside FluidNC)

- **A job, checked against machine limits, then executed.** A motion job has hard bounds: axis travel, feed and acceleration limits, work envelope. URML expresses the job intent plus those bounds as a safety envelope, validates it against the machine's declared capabilities, then dispatches to FluidNC. FluidNC keeps ownership of step generation and motion.
- **Machine config as a manifest.** FluidNC's per-machine configuration (axes, limits) is close in spirit to a URML capability manifest, so an out-of-envelope job can be caught before it runs.

## What is asked

1. Is a typed, validated job-intent layer (declare the job + machine bounds, validate, then dispatch) useful above FluidNC?
2. Does FluidNC's machine configuration map onto a URML capability manifest closely enough to share?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's industrial profile, the capability manifest, the safety-envelope validation, and the plan_path / follow_trajectory consume model (RFC-0020). Part of Move #53; the CNC / motion-control target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `bdring/FluidNC` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the license is non-standard / unrecognized by GitHub; state that, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move53.yaml`.
