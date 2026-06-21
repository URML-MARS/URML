---
rfc: 0625
title: ORCA Hand (orca_core) integration — request for comment
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

# RFC-0625: ORCA Hand (orca_core) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robotic-end-effector wave (Move #60).

## Summary

[`orcahand/orca_core`](https://github.com/orcahand/orca_core) (MIT, ETH Zurich Soft Robotics Lab) is the Python control core for the ORCA hand, a 17-DoF tendon-driven dexterous hand: high-level joint-space commands, calibration, and tendon tensioning. URML extended its grasp model to describe exactly this kind of hand: a `dexterous` gripper kind carrying a dexterity declaration (DoF, finger count, supported grasp types, in-hand support) plus an optional grasp-type on the grasp primitive (RFC-0586). URML declares the hand's capabilities and a grasp envelope, validates a grasp intent against them, and leaves the joint and tendon control to orca_core. This is a request for comment.

## The relationship (URML beside orca_core)

- **Declare the 17 DoF once, check every grasp against them.** A grasp intent on the ORCA hand carries a grasp type, a target, and force limits. URML validates that against a manifest that declares the hand's degrees of freedom and the grasp types it supports, and against a safety envelope on grasp force, before orca_core is asked to move joints. orca_core keeps the joint-space control, calibration, and tensioning; URML is the static check in front of it.
- **The dexterity declaration earns its keep here.** A 17-DoF hand is well past what a single-DoF gripper abstraction can express, which is the reason URML added the dexterity block. orca_core's declared joint structure is a direct input to that declaration.

## What is asked

1. Is a typed grasp-intent layer (declare the hand as dexterous with its DoF and grasp types, validate against a force envelope, then call orca_core) useful above the control core?
2. Does the ORCA hand's joint structure and grasp-type set map onto URML's dexterity declaration cleanly, or do the tendon-coupling details need something the manifest does not yet express?
3. Would a single grasp type be the right first end-to-end mapping?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `dexterous` gripper kind, the dexterity declaration, the optional grasp-type on grasp, and the grasp-force envelope (RFC-0586). Companion to RFC-0624 (Aero Hand) and RFC-0626 (BiDexHand) in the dexterous-hand part of Move #60.

## Implementation note

Outreach only. The post is a GitHub Issue on `orcahand/orca_core` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is MIT; stated, not asked. Tracked in `examples/lighthouses/outreach-move60.yaml`.
