---
rfc: 0441
title: AMBF (WPI) integration — request for comment
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

# RFC-0441: AMBF (WPI) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the simulation-engagement pattern (RFC-0381). **Scope: research and simulation only. URML makes no clinical claim and is not for patient use.**

## Summary

[`WPI-AIM/ambf`](https://github.com/WPI-AIM/ambf) (custom permissive academic license, ~215 stars, active, Discussions on) is the Asynchronous Multi-Body Framework, a real-time soft-body and haptic simulation framework from the WPI AIM Lab, widely used for surgical-robotics research (it underpins the Surgical Robotics Challenge). A high-fidelity research surgical simulator is a clean place to drive a research robot from validated intent before any hardware. This RFC asks whether that is interesting.

## The mapping (URML above AMBF)

URML sits above the simulated research robot as a validated intent layer:

- A URML research program drives an AMBF-simulated manipulator through the AMBF ROS interface; URML's optional validation block records the simulation-fidelity context a run was checked in, which AMBF's soft-body realism makes concrete.
- Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before the simulated robot moves — a research-grade safety seam consistent with the "not for clinical use" norm.
- The sim-first posture matches URML's own (the reference runtime ships a mock substrate).

## What is asked

Request for comment from the AMBF maintainers:

1. Is a validated intent layer above AMBF interesting as a research surface for surgical and multi-body robot scenarios?
2. What should a URML capability manifest declare to describe an AMBF-simulated research robot honestly (bodies/arms, reach/DOF, instrument set, workspace bounds)?
3. Is the AMBF ROS interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's ROS 2 runtime; the simulation-engagement pattern (RFC-0381); the surgical-research anchor (RFC-0440). AMBF is the soft-body-simulation vertex of the medical / surgical research wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `WPI-AIM/ambf` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (custom permissive academic license). Research/sim framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
