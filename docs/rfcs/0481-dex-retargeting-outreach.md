---
rfc: 0481
title: dex-retargeting integration — request for comment
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

# RFC-0481: dex-retargeting integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's manipulation primitive family and capability manifest.

## Summary

[`dexsuite/dex-retargeting`](https://github.com/dexsuite/dex-retargeting) (MIT, ~1048 stars, active) is the human-hand → robot-hand retargeting layer behind AnyTeleop, used by many VR/vision teleop rigs to map a tracked human hand onto a dexterous robot hand. URML is interesting to it as the validated bound around the retargeted output: a retargeted grasp still has to be something the declared hand can do (DOF, joint limits, the object's graspable class), and that is exactly URML's capability/envelope check. This RFC asks whether wrapping retargeted intent in that check is useful.

## The mapping (URML around retargeted hand intent)

URML sits above the retargeting output as a validated-intent layer:

- A retargeting result becomes (or is paired with) a URML manipulation intent (`grasp` with the addressed hand/arm); URML validates it against the declared dexterous-hand manifest (DOF, joint limits, gripper/hand kind, graspable classes) before it is sent to hardware.
- This complements the dexterous-hand manifest questions raised in URML's earlier manipulation engagement (LEAP / Shadow): what a multi-DoF hand must declare so a retargeted grasp can be capability-checked.

## What is asked

Request for comment from the dex-retargeting maintainers:

1. Is wrapping a retargeted hand pose in a validated manipulation intent (capability + envelope check before hardware) interesting for AnyTeleop-style rigs?
2. What should a URML capability manifest declare to describe a dexterous hand honestly so a retargeted grasp can be checked (DOF, joint limits, graspable classes)?
3. Where is the cleanest seam — a check after retargeting, before dispatch?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation family (Move #27, incl. the LEAP/Shadow dexterous-hand manifest questions) and capability manifest; the GELLO anchor (RFC-0479). dex-retargeting is the hand-retargeting vertex of the teleop / data-collection wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `dexsuite/dex-retargeting` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move42.yaml`.
