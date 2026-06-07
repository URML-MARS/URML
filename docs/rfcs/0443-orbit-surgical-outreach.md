---
rfc: 0443
title: ORBIT-Surgical integration — request for comment
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

# RFC-0443: ORBIT-Surgical integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the pattern of wrapping a learned policy in a validated envelope. **Scope: research and simulation only. URML makes no clinical claim.**

## Summary

[`orbit-surgical/orbit-surgical`](https://github.com/orbit-surgical/orbit-surgical) (BSD-3-Clause, ~174 stars) is a surgical reinforcement-learning and imitation-learning simulation framework built on NVIDIA Isaac Lab / Omniverse, from the University of Toronto. It trains policies for dVRK-style surgical subtasks in a high-fidelity GPU sim, which makes it a clean place to show URML wrapping a learned surgical-research policy in a validated envelope. This RFC asks whether that is interesting.

## The mapping (URML above ORBIT-Surgical)

URML sits above the learned controller as a validated research intent layer:

- A URML research intent declares the subtask goal and the envelope; a learned policy in ORBIT-Surgical produces the low-level control, and URML validates the request against the declared research constraints before the policy acts.
- This is the decide-then-do split applied to learning: the policy is the actuator, URML is the typed, validated intent and the research safety envelope around it.
- The surgical-sim manifest (arms/instruments, reach/DOF, workspace, observation/action assumptions) is a rich research test of URML's model.

## What is asked

Request for comment from the ORBIT-Surgical maintainers:

1. Is wrapping a learned surgical-research policy in a validated intent layer + envelope interesting in the RL/IL-sim context?
2. What should a URML capability manifest declare to describe a simulated surgical robot honestly (arms/instruments, reach/DOF, workspace bounds, observation/action assumptions)?
3. Is the Isaac Lab env interface the right seam, or a higher-level task wrapper?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417, RFC-0424); the simulation-engagement pattern (RFC-0381); the surgical-research anchor (RFC-0440). ORBIT-Surgical is the surgical-RL vertex of the medical / surgical research wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `orbit-surgical/orbit-surgical` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). Research/sim framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
