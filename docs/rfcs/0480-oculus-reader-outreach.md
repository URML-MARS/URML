---
rfc: 0480
title: oculus_reader integration — request for comment
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

# RFC-0480: oculus_reader integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validated-intent layer.

## Summary

[`rail-berkeley/oculus_reader`](https://github.com/rail-berkeley/oculus_reader) (Apache-2.0, ~161 stars, active) reads Oculus / Quest controller pose + button input for VR teleoperation, the input front-end many manipulation teleop rigs build on. URML is interesting to it as the validated layer a button-press can trigger: instead of (or alongside) streaming raw pose, a controller gesture maps to a high-level URML intent that is capability- and envelope-checked before it actuates. This RFC asks whether that is useful.

## The mapping (URML behind an oculus_reader button)

URML sits behind the VR input as a validated-intent layer:

- A mapped controller action ("grip button → grasp the detected object", "A → return home") becomes a high-level URML primitive; URML validates it against the robot's declared capabilities and safety envelope, then dispatches. Continuous pose teleop remains the direct path; the buttons gain validated, named intents.
- The recorded session can carry the typed intent each button triggered, so a VR-collected demonstration is labelled with validatable URML primitives next to the pose stream.

## What is asked

Request for comment from the oculus_reader maintainers:

1. Is mapping a controller action to a validated URML intent (vs. raw pose streaming) interesting for VR teleop built on oculus_reader?
2. What is the cleanest seam — a thin layer above the reader's button events?
3. Is recording the typed intent per button useful for the demonstrations collected through it?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's validated-intent layer (RFC-0002); the VLA / robot-learning engagements (Moves #11, #38); the GELLO anchor (RFC-0479). oculus_reader is the VR-input vertex of the teleop / data-collection wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `rail-berkeley/oculus_reader` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move42.yaml`.
