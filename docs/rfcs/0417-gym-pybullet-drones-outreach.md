---
rfc: 0417
title: gym-pybullet-drones integration — request for comment
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

# RFC-0417: gym-pybullet-drones integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `aerial` drive type and the pattern of consuming a learned policy behind a validated envelope.

## Summary

[`learnsyslab/gym-pybullet-drones`](https://github.com/learnsyslab/gym-pybullet-drones) (MIT, ~2.0k stars, active) is a PyBullet Gymnasium suite of reinforcement-learning environments for quadcopter control (UTIAS / Cambridge). It is the most-starred open drone-RL sandbox, which makes it an ideal place to show URML wrapping a learned controller in a validated intent layer. This RFC asks whether that is interesting.

## The mapping (URML above gym-pybullet-drones)

URML sits above the learned controller as a validated intent layer:

- A URML `aerial` intent declares the goal and the envelope; a learned policy in a gym-pybullet-drones environment produces the low-level control, and URML validates the request against the declared limits before it is allowed to act.
- This is the decide-then-do split applied to learning: the policy is the actuator, URML is the typed, validated intent and the safety envelope around it.
- The RL sandbox is a clean demonstrator for "a natural-language goal, a learned controller, and a validator that refuses out-of-envelope requests."

## What is asked

Request for comment from the gym-pybullet-drones maintainers:

1. Is wrapping a learned drone controller in a validated intent layer + envelope interesting in the RL-sandbox context?
2. What should a URML capability manifest declare to describe a learned-controller drone honestly (drive type, altitude/speed limits, observation/action assumptions)?
3. Is the Gymnasium env interface the right seam, or a higher-level mission wrapper?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `aerial` drive type; the decide-then-do split; the safety/runtime-verification engagement (Move #28) on declared properties a monitor enforces. gym-pybullet-drones is the drone-RL vertex of the aerial wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `learnsyslab/gym-pybullet-drones` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move34.yaml`.
