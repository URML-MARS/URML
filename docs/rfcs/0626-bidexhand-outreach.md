---
rfc: 0626
title: BiDexHand integration — request for comment
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

# RFC-0626: BiDexHand integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robotic-end-effector wave (Move #60).

## Summary

[`wengmister/BiDexHand`](https://github.com/wengmister/BiDexHand) (MIT) is a 16-DoF cable-driven dexterous hand with ROS 2 control (joint PID, Cartesian, and shadowing modes) and fingertip force sensing. The fingertip force sensing makes it a particularly clean target for URML, whose contribution here is the grasp envelope: URML declares the hand as a `dexterous` gripper with its DoF and supported grasp types (RFC-0586), declares a grasp-force envelope, validates a grasp intent against both, and leaves the cable-level control to BiDexHand. This is a request for comment.

## The relationship (URML beside BiDexHand)

- **A force envelope that the hand can actually sense.** URML validates that a grasp intent stays inside a declared grasp-force envelope before dispatch; BiDexHand's fingertip force sensing is the runtime side of the same property. The static check refuses an over-force grasp intent before the cables move; the sensors remain the hand's. A declared envelope plus a hand that measures force is a natural pairing.
- **The dexterity declaration fits a 16-DoF hand.** A single-DoF gripper abstraction cannot describe a cable-driven 16-DoF hand, which is why URML added the dexterity block. BiDexHand's joint structure and its control modes map onto the dexterous declaration directly.

## What is asked

1. Is a typed grasp-intent layer (declare the hand as dexterous, validate a grasp against a force envelope, then call BiDexHand's control) useful above the ROS 2 control modes?
2. Does the hand's DoF and grasp-type set map onto URML's dexterity declaration cleanly, and does its fingertip force sensing line up with a declared grasp-force envelope?
3. Which control mode (PID, Cartesian, shadowing) would be the most natural first to sit a validated intent above?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `dexterous` gripper kind, the dexterity declaration, the optional grasp-type on grasp, and the grasp-force envelope (RFC-0586), with the static-check-complements-runtime-sensing framing from URML's runtime-verification outreach (Move #28). Companion to RFC-0624 and RFC-0625 in the dexterous-hand part of Move #60.

## Implementation note

Outreach only. The post is a GitHub Issue on `wengmister/BiDexHand` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is MIT; stated, not asked. Tracked in `examples/lighthouses/outreach-move60.yaml`.
