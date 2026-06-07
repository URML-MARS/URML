---
rfc: 0449
title: ManiSkill integration — request for comment
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

# RFC-0449: ManiSkill integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family, the simulation-engagement pattern (RFC-0381), and the wrap-a-learned-policy pattern.

## Summary

[`mani-skill/ManiSkill`](https://github.com/mani-skill/ManiSkill) (Apache-2.0, ~2,962 stars, active, Discussions on) is a GPU-parallel manipulation simulation and benchmark suite from UC San Diego / Hillbot, widely used to train and evaluate manipulation policies. A high-throughput manipulation benchmark is a clean place to show URML wrapping a learned policy in a validated envelope, and to evaluate validated-intent dispatch at scale. This RFC asks whether that is interesting.

## The mapping (URML above ManiSkill)

URML sits above the simulated robot / learned policy as a validated intent layer:

- A URML intent declares the goal and the envelope; a policy trained in ManiSkill produces the low-level action, and URML validates the request against the declared task capabilities before the policy acts.
- URML's ROS / Python interface drives a ManiSkill task; URML's optional validation block records the simulation-fidelity context a run was checked in.
- Validate-before-actuate refuses an out-of-capability request before the simulated robot moves (decide-then-do applied to learning).

## What is asked

Request for comment from the ManiSkill maintainers:

1. Is a validated intent layer + envelope above ManiSkill policies interesting for the manipulation-learning community?
2. What should a URML capability manifest declare to describe a ManiSkill task robot honestly (arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the env interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the simulation-engagement pattern (RFC-0381); the earlier VLA wave (Move #11). ManiSkill is the manipulation-benchmark vertex of the round-2 wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `mani-skill/ManiSkill` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move38.yaml`.
