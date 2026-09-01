---
rfc: 0689
title: xArm Python SDK (xArm-Developer/xArm-Python-SDK) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-01
updated: 2026-09-01
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

# RFC-0689: xArm Python SDK (xArm-Developer/xArm-Python-SDK) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the small-open-robot wave (Move #72).

## Summary

[`xArm-Developer/xArm-Python-SDK`](https://github.com/xArm-Developer/xArm-Python-SDK) (UFACTORY) is the open Python SDK (`XArmAPI`) for the xArm 5/6/7 and Lite 6 desktop arms, with a companion `xarm_ros2` (ROS 2 + MoveIt) surface. Because a joint or Cartesian move, with speed and force parameters, becomes a real actuation, URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (joint limits, reachable workspace, payload, gripper force) and a safety envelope, and URML checks a move is admissible before `set_servo_angle` / `set_position` reaches the controller. This is a request for comment.

## The relationship (URML beside the xArm SDK)

- **The program proposes, the validator gates.** Whatever produces the command decides the move; URML checks the concrete joint/Cartesian target and its speed/force parameters are admissible on the declared xArm (within its limits and payload, inside the safety envelope) before the SDK dispatches. URML does the check; the SDK keeps the actuation.
- **The SDK is a clean seam.** Because `XArmAPI` (and `xarm_ros2`) is the single programmatic surface, a per-arm capability manifest is the natural declaration a command is checked against before the call.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the SDK rather than depending on its internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared capability manifest + safety envelope, checked before `set_servo_angle` / `set_position` reaches the controller, be a useful guard on top of the SDK?
2. Would a small worked example mapping an xArm move onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #72 small-open-robot wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `xArm-Developer/xArm-Python-SDK` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move72.yaml`.
