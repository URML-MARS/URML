---
rfc: 0444
title: LapGym / sofa_env integration — request for comment
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

# RFC-0444: LapGym / sofa_env integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the wrap-a-learned-policy pattern. **Scope: research and simulation only. URML makes no clinical claim.**

## Summary

[`ScheiklP/sofa_env`](https://github.com/ScheiklP/sofa_env) (MIT, ~75 stars, active) is the SOFA-based reinforcement-learning environment suite behind LapGym, for robot-assisted laparoscopic surgery research (TU Dresden / Heidelberg). A permissively-licensed, deformable-tissue laparoscopic sim is a clean place to drive a research robot from validated intent and to wrap a learned policy in a validated envelope. This RFC asks whether that is interesting.

## The mapping (URML above sofa_env)

URML sits above the simulated research robot / learned controller as a validated intent layer:

- A URML research subtask intent drives a sofa_env laparoscopic scenario, or declares the goal + envelope around a learned policy that produces the low-level control (decide-then-do applied to learning).
- Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before motion — a research safety seam.
- URML's optional validation block records the simulation-fidelity context (SOFA deformable tissue) a run was checked in.

## What is asked

Request for comment from the LapGym / sofa_env maintainers:

1. Is a validated research intent layer above sofa_env interesting for laparoscopic-surgery RL/research?
2. What should a URML capability manifest declare to describe a laparoscopic research robot honestly (instruments, reach/DOF, workspace bounds, observation/action assumptions)?
3. Is the Gym env interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the simulation-engagement pattern (RFC-0381); the surgical-research anchor (RFC-0440). LapGym is the deformable-tissue laparoscopic-sim vertex of the medical / surgical research wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ScheiklP/sofa_env` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Research/sim framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
