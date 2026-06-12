---
rfc: 0484
title: DexCap integration — request for comment
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

# RFC-0484: DexCap integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validated-intent layer and manipulation primitive family. Tier B.

## Summary

[`j96w/DexCap`](https://github.com/j96w/DexCap) (MIT, ~380 stars; RSS 2024, Stanford) is a portable hand-motion-capture system for collecting dexterous manipulation demonstrations in the wild. URML is interesting to it as a typed schema for the captured intent: a DexCap episode labelled with the URML primitive it realizes carries validatable, manifest-checkable intent next to the hand-pose trajectory, and a policy trained on it can be wrapped in URML's validate-before-actuate envelope at deployment. This RFC asks whether that is useful.

## The mapping (URML as typed labels on DexCap data)

URML sits beside DexCap as a typed-intent annotation layer:

- Each DexCap demonstration is labelled with the URML primitive(s) it realizes (`grasp` with the addressed hand, dexterous-hand parameters); the label is typed and checkable against a target dexterous-hand manifest (DOF, joint limits, graspable classes).
- A policy trained on DexCap data is wrapped in URML's validate-before-actuate envelope at deployment (the decide-then-do split applied to learning), so the captured dexterous behavior is capability- and envelope-checked before it runs.

## What is asked

Request for comment from the DexCap maintainers:

1. Is labelling DexCap demonstrations with a typed URML primitive useful as structured, manifest-checkable supervision?
2. What should a URML capability manifest declare to describe the target dexterous hand so a captured grasp can be checked?
3. Is a validate-before-actuate wrapper at deployment interesting?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's validated-intent layer (RFC-0002), the manipulation family + dexterous-hand manifest questions (Move #27, LEAP/Shadow), and the decide-then-do split applied to learned control (RFC-0417); the GELLO anchor (RFC-0479). DexCap is the portable-hand-mocap vertex of the teleop / data-collection wave (Tier B; repo is dormant but the rig is a reference).

## Implementation note

Outreach only. The post is a GitHub Issue on `j96w/DexCap` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move42.yaml`.
