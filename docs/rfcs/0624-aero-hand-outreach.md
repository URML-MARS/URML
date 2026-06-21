---
rfc: 0624
title: Aero Hand Open (aero-hand-open) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-21
updated: 2026-06-21
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

# RFC-0624: Aero Hand Open (aero-hand-open) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the robotic-end-effector wave (Move #60).

## Summary

[`TetherIA/aero-hand-open`](https://github.com/TetherIA/aero-hand-open) (Apache-2.0 firmware and SDK, CC-BY-NC-SA on the hardware files; TetherIA, US) is a tendon-driven multi-fingered robot hand with a Python SDK, ESP32 firmware, and ROS 2 support. A multi-DoF hand is exactly the case URML extended its grasp model to cover: URML already has a `dexterous` gripper kind with a dexterity declaration (degrees of freedom, finger count, grasp types, in-hand support) and an optional grasp-type on the grasp primitive (RFC-0586). URML declares the hand's capabilities and a grasp envelope, validates a grasp intent against them, and leaves the tendon control to the Aero Hand SDK. This is a request for comment.

## The relationship (URML beside Aero Hand)

- **Declare the hand, validate the grasp, leave the control to the SDK.** A grasp on a dexterous hand is a typed intent: which grasp type, on which object class, within which force limits. URML validates that against a capability manifest that declares the hand as `dexterous` (its DoF, finger count, and supported grasp types) and a safety envelope on grasp force, then leaves the tendon-level control to the Aero Hand SDK. The SDK keeps the actuation; URML is the pre-dispatch check.
- **A fit URML built for on purpose.** The single-DoF gripper abstraction cannot describe a tendon-driven multi-fingered hand, which is why URML added the dexterity declaration. The Aero Hand is a clean target for it: a real, affordable, open multi-DoF hand whose declared capabilities map onto the manifest directly.

## What is asked

1. Is a typed grasp-intent layer (declare the hand as dexterous with its DoF and grasp types, validate a grasp against a force envelope, then call the SDK) useful above the Aero Hand SDK?
2. Does the hand's capability set (degrees of freedom, finger count, the grasp types it supports, whether it does in-hand manipulation) map onto URML's dexterity declaration cleanly, or is something missing?
3. Which grasp type would be the most natural first to model end to end?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `dexterous` gripper kind and dexterity declaration, the optional grasp-type on the grasp primitive, and the grasp-force safety envelope (RFC-0586). Anchor of Move #60; the strongest open multi-DoF hand target in the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `TetherIA/aero-hand-open` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The firmware and SDK are Apache-2.0 (the hardware files are CC-BY-NC-SA 4.0); stated, not asked, and the relationship concerns the SDK. Tracked in `examples/lighthouses/outreach-move60.yaml`.
