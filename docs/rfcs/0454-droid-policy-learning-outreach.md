---
rfc: 0454
title: DROID policy learning integration — request for comment
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

# RFC-0454: DROID policy learning integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and the wrap-a-learned-policy pattern. Tier B.

## Summary

[`droid-dataset/droid_policy_learning`](https://github.com/droid-dataset/droid_policy_learning) (MIT, ~287 stars) is the policy-learning and evaluation code for DROID, the large in-the-wild manipulation dataset from a multi-institution consortium (Stanford / Berkeley and others). Policies trained on a large real-world dataset are exactly what URML sits above: a typed intent and a validated envelope around the learned action. This RFC asks whether that is interesting.

## The mapping (URML above DROID policy learning)

URML sits above the learned policy as a validated intent layer:

- A URML intent declares the goal and the envelope; a DROID-trained policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts.
- This is the decide-then-do split applied to learning: the policy is the actuator, URML is the typed intent and the safety envelope around it.
- Validate-before-actuate refuses an out-of-capability request before motion.

## What is asked

Request for comment from the DROID policy-learning maintainers:

1. Is wrapping a DROID-trained policy in a validated intent layer + envelope interesting?
2. What should a URML capability manifest declare to describe a DROID-class manipulation robot honestly (arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions)?
3. Is the policy/eval interface the right seam, or a higher-level task API?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27); the decide-then-do split applied to learned control (RFC-0417); the earlier VLA wave (Move #11). DROID policy learning is the in-the-wild-dataset-policy vertex of the round-2 wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `droid-dataset/droid_policy_learning` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move38.yaml`.
