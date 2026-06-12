---
rfc: 0483
title: Universal Manipulation Interface (UMI) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0483: Universal Manipulation Interface (UMI) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validated-intent layer and the decide-then-do split.

## Summary

[`real-stanford/universal_manipulation_interface`](https://github.com/real-stanford/universal_manipulation_interface) (MIT, ~1.4k stars, active) is UMI, a handheld-gripper data-collection interface that captures in-the-wild manipulation demonstrations without a robot in the loop. URML is interesting to it as a typed schema for the *intent* of each captured demonstration: a UMI episode labelled with the URML primitive it realizes (`grasp($obj)`, `place_at(...)`) carries validatable, capability-checkable intent next to the visual + gripper trajectory. (For context: URML engaged the sibling `diffusion_policy` earlier; this is a separate thought on UMI's data-collection side, not a repeat.)

## The mapping (URML as typed labels on UMI data)

URML sits beside UMI as a typed-intent annotation layer:

- Each UMI demonstration is labelled with the URML primitive(s) it realizes; the label is a typed, validatable intent — a downstream policy gets structured supervision, and the label can be checked against a target robot's manifest (is this demonstrated grasp something *this* robot could do?).
- At deployment, a policy trained on UMI data can be wrapped in URML's validate-before-actuate envelope (the decide-then-do split applied to learning), so the in-the-wild-collected behavior is capability- and envelope-checked before it runs on hardware.

## What is asked

Request for comment from the UMI maintainers:

1. Is labelling UMI demonstrations with a typed URML primitive useful — as structured supervision and as a manifest-checkable record?
2. Is wrapping a UMI-trained policy in a validated intent + envelope at deployment interesting?
3. Where is the cleanest seam — annotation at collection time, or a validation wrapper at deployment?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's validated-intent layer (RFC-0002), the decide-then-do split applied to learned control (RFC-0417), and the VLA / robot-learning engagements (Moves #11, #38); the GELLO anchor (RFC-0479). UMI is the handheld-data-collection vertex of the teleop / data-collection wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `real-stanford/universal_manipulation_interface` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). The reply acknowledges the prior `diffusion_policy` (same lab) engagement so it does not read as a cold repeat. Tracked in `examples/lighthouses/outreach-move42.yaml`.
