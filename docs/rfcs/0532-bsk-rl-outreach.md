---
rfc: 0532
title: bsk_rl integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0532: bsk_rl integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48).

## Summary

[`AVSLab/bsk_rl`](https://github.com/AVSLab/bsk_rl) (MIT, active, CU Boulder Autonomous Vehicle Systems Lab) provides reinforcement-learning environments and tools for spacecraft autonomy (planning and scheduling) on the Basilisk astrodynamics engine. URML extends URML's robot-intent frame to a spacecraft: a high-level task is validated against the spacecraft's declared capabilities and operating constraints, and a policy trained in bsk_rl can declare the envelope it was trained in. This RFC asks whether the mapping is useful.

## The mapping (URML beside bsk_rl)

- **Spacecraft task intent + constraints.** A spacecraft tasking intent (image this target, downlink, recharge) maps onto typed URML primitives validated against a manifest of the spacecraft's capabilities and a constraint envelope (power, attitude, keep-out). The decide-then-do split applies: validate the plan, then execute.
- **Learned scheduling envelope.** A bsk_rl-trained scheduling policy can declare, via URML's `LearnedPolicy` declaration (RFC-0383), the observation/action spaces and domain it learned, so a deployment is validated against it.

## What is asked

Request for comment from the bsk_rl maintainers:

1. Does URML's capability-manifest + safety-envelope frame extend sensibly to spacecraft tasking / scheduling?
2. Is declaring a trained scheduling policy's envelope (RFC-0383) useful for the deployment side?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest + safety envelope, the `LearnedPolicy` declaration (RFC-0383), and the space engagements (Move #31: Space-ROS, F`, cFS, Astrobee). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `AVSLab/bsk_rl` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
