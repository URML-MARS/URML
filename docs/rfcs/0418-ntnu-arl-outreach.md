---
rfc: 0418
title: NTNU ARL unified autonomy stack integration — request for comment
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

# RFC-0418: NTNU ARL unified autonomy stack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type and ROS 2 runtime. It anchors one engagement on the NTNU Autonomous Robots Lab org.

## Summary

[`ntnu-arl/unified_autonomy_stack`](https://github.com/ntnu-arl/unified_autonomy_stack) (BSD-3-Clause, ~182 stars, active) is a generalizable robot-autonomy blueprint from the NTNU Autonomous Robots Lab, a group with a strong record in aerial exploration. The lab also maintains [`aerial_gym_simulator`](https://github.com/ntnu-arl/aerial_gym_simulator) (BSD-3-Clause, ~724 stars), an Isaac-Gym aerial RL simulator. This RFC anchors one engagement on the autonomy stack and references the simulator, rather than posting to each. It asks whether a validated intent layer above the lab's autonomy work is interesting.

## The mapping (URML above the autonomy stack)

URML sits above the autonomy stack as a validated intent layer:

- URML's `aerial` drive type and ROS 2 runtime meet the unified autonomy stack on its ROS 2 surface; a "explore this volume and return" intent lowers onto the stack's planning/behavior layer.
- The `aerial_gym_simulator` is where a learned policy is trained; URML wraps the deployed controller in a validated envelope (the decide-then-do split applied to learning).
- Validate-before-actuate refuses an out-of-envelope request before the drone acts.

## What is asked

Request for comment from the NTNU ARL maintainers:

1. Where is the cleanest seam for an external validated-intent layer — above the unified autonomy stack's behavior/planning layer, or wrapping a policy trained in `aerial_gym_simulator`?
2. What should a URML capability manifest declare to describe an exploration-class aerial robot honestly (drive type, altitude/speed limits, sensor suite, exploration bounds)?
3. Is a validated natural-language layer interesting for the lab's aerial-autonomy research?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type and ROS 2 runtime; the decide-then-do split; the aerial-autonomy anchor (RFC-0412). NTNU ARL is the exploration-autonomy + aerial-RL-sim vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ntnu-arl/unified_autonomy_stack` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-3-Clause). The `aerial_gym_simulator` repo is referenced, not posted to separately (org-anchor). Tracked in `examples/lighthouses/outreach-move34.yaml`.
