---
rfc: 0681
title: WEART Python SDK (WEARTHaptics/WEART-SDK-Python) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-18
updated: 2026-08-18
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

# RFC-0681: WEART Python SDK (WEARTHaptics/WEART-SDK-Python) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the haptic teleoperation sub-lane of the nuclear / hazmat wave (Move #70).

## Summary

[`WEARTHaptics/WEART-SDK-Python`](https://github.com/WEARTHaptics/WEART-SDK-Python) (WEART, Milan) is the low-level SDK for the TouchDIVER haptic gloves: it sends haptic effects (force, texture, and thermal) to the devices and reads tracking and sensor data, and the vendor markets the devices for teleoperation. That gives URML's validate-before-actuate gate a surface on both sides of a teleoperation loop: the robot side (the grasp or motion the glove teleoperates) is checked against the robot's capability manifest and envelope before dispatch, and the render side (a commanded force or thermal effect) has a declared safe range the command must stay within, so an out-of-range render is refused before it reaches the operator's hand. This is a request for comment.

## The relationship (URML beside the WEART SDK)

- **The glove commands, the validator gates.** When TouchDIVER teleoperates a remote hand, URML checks the commanded grasp is admissible on the declared robot before dispatch. URML does the check; the SDK keeps the device I/O.
- **A declared render envelope, including thermal.** A commanded force or thermal effect is a bounded quantity with a declared safe maximum; URML can check a render command against that declaration the same way it checks any actuation output (RFC-0017). Thermal is a natural fit for an envelope: a declared safe range the render may not exceed.
- **Neutral by construction.** URML is substrate- and model-neutral; it composes above the command rather than depending on the SDK's internals.

## What is asked

1. In a TouchDIVER teleoperation loop, would a declared capability + envelope on the robot side (and a declared force/thermal render envelope on the glove side) be a useful pre-dispatch guard?
2. Would a small worked example mapping a teleoperated grasp, or a thermal render envelope, onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and `set_output` range checks (RFC-0017). Part of the Move #70 haptic-teleoperation sub-lane.

## Implementation note

Outreach only. The post is a GitHub Issue on `WEARTHaptics/WEART-SDK-Python` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move70.yaml`.
