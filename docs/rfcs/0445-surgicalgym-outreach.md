---
rfc: 0445
title: SurgicalGym integration — request for comment
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

# RFC-0445: SurgicalGym integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the wrap-a-learned-policy pattern. Tier B. **Scope: research and simulation only. URML makes no clinical claim.**

## Summary

[`SamuelSchmidgall/SurgicalGym`](https://github.com/SamuelSchmidgall/SurgicalGym) (MIT, ~102 stars) is a GPU-accelerated Isaac-Sim reinforcement-learning environment for da Vinci PSM/ECM and STAR surgical-research robots. A permissively-licensed, high-throughput surgical RL sandbox is a clean place to wrap a learned research policy in a validated envelope. This RFC asks whether that is interesting.

## The mapping (URML above SurgicalGym)

URML sits above the learned controller as a validated research intent layer:

- A URML research intent declares the subtask goal and the envelope; a learned policy in SurgicalGym produces the low-level control, and URML validates the request against the declared research constraints before the policy acts (decide-then-do applied to learning).
- Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before the simulated robot moves.
- The surgical-sim manifest (arms/instruments, reach/DOF, workspace, observation/action assumptions) is a research test of URML's model.

## What is asked

Request for comment from the SurgicalGym maintainer:

1. Is wrapping a learned surgical-research policy in a validated intent layer + envelope interesting in the GPU-RL-sim context?
2. What should a URML capability manifest declare to describe a simulated PSM/ECM or STAR research robot honestly (arms/instruments, reach/DOF, workspace bounds, observation/action assumptions)?
3. Is the env interface the right seam, or a higher-level task wrapper?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the simulation-engagement pattern (RFC-0381); the surgical-research anchor (RFC-0440). SurgicalGym is the GPU-RL vertex of the medical / surgical research wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `SamuelSchmidgall/SurgicalGym` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Research/sim framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
