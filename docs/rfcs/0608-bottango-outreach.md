---
rfc: 0608
title: Bottango integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0608: Bottango integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the soft-robotics / assistive wave (Move #57); the animatronics corner.

## Summary

[`EvanBottango/Bottango`](https://github.com/EvanBottango/Bottango) (BSD-3-Clause) is an animation tool for animatronics and performance robots: it drives servos and effectors with hand-authored or live motion, and exposes a REST API plus open drivers. An animatronic is an articulated robot, and the actions it performs (move this joint, run this effector, hold this pose) are the kind of typed, capability-checkable intent URML declares. This RFC asks whether a portable intent layer above Bottango is useful.

## The relationship (URML beside Bottango)

- **A portable typed-intent layer over per-effector control.** Bottango owns the authoring, the timeline, and the device drivers. URML's candidate role is a portable, typed declaration of an animatronic action, validated against the rig's declared effectors and their limits, then dispatched through Bottango's REST API. For an installation that mixes hand-authored animation with triggered or generated behavior, a typed intent layer makes "what is this rig allowed to do" explicit and checkable.
- **An English-friendly path.** URML's Layer 4 means a triggered behavior could start from a plain-language description and become a checked, runnable animatronic action.

## What is asked

1. Is a typed, validated intent layer (an animatronic action checked against the rig's declared effectors and limits, then dispatched over the REST API) useful above Bottango?
2. Does a rig's effector configuration map onto a URML capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the set_output / actuation primitives, and the Layer-4 natural-language grammar. Part of Move #57; the animatronics / performance-robot target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `EvanBottango/Bottango` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move57.yaml`.
