---
rfc: 0450
title: LIBERO integration — request for comment
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

# RFC-0450: LIBERO integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and the wrap-a-learned-policy pattern.

## Summary

[`Lifelong-Robot-Learning/LIBERO`](https://github.com/Lifelong-Robot-Learning/LIBERO) (MIT, ~1,911 stars) is a lifelong robot-learning benchmark from UT Austin (Yuke Zhu), a standard evaluation suite for VLAs and manipulation policies (OpenVLA, π0, and others report on it). A widely-used policy benchmark is a clean place to evaluate validated-intent dispatch and to express task intent that a learned policy then executes. This RFC asks whether that is interesting.

## The mapping (URML above LIBERO)

URML sits above the benchmarked policy as a validated intent layer:

- A URML intent declares the goal and the envelope for a LIBERO task; a learned policy produces the low-level action, and URML validates the request against the declared task capabilities before the policy acts.
- This is the decide-then-do split applied to learning, evaluated on a standard benchmark.
- Validate-before-actuate refuses an out-of-capability request before motion — a measurable safety/consistency signal alongside task success.

## What is asked

Request for comment from the LIBERO maintainers:

1. Is a validated intent layer + envelope above LIBERO-benchmarked policies interesting for the lifelong-learning community?
2. What should a URML capability manifest declare to describe a LIBERO task robot honestly (arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the benchmark task interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the earlier VLA wave (Move #11). LIBERO is the policy-benchmark vertex of the round-2 wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `Lifelong-Robot-Learning/LIBERO` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move38.yaml`.
