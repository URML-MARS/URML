---
rfc: 0680
title: SenseGlove ROS (Adjuvo/senseglove_ros) integration — request for comment
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

# RFC-0680: SenseGlove ROS (Adjuvo/senseglove_ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Anchors the haptic teleoperation sub-lane of the nuclear / hazmat wave (Move #70).

## Summary

[`Adjuvo/senseglove_ros`](https://github.com/Adjuvo/senseglove_ros) (SenseGlove) integrates the SenseGlove force-feedback glove into ROS 2 (Jazzy) through `ros2_control`. Force-feedback gloves are a common way to teleoperate a robot hand, and that teleoperation loop is where URML's validate-before-actuate gate has a surface twice over: the robot side (the grasp or motion the glove commands on the remote hand) is checked against the robot's capability manifest and envelope before dispatch, and the operator side (the commanded fingertip-force render) has a declared safe range the command must stay within. This is a request for comment.

## The relationship (URML beside senseglove_ros)

- **The glove commands, the validator gates.** When the glove teleoperates a remote gripper, URML checks the commanded grasp is admissible on the declared robot (within its force, reach, mobility, inside the envelope) before dispatch. The `ros2_control` boundary this stack uses is exactly URML's Layer-1 seam (RFC-0319).
- **A declared render envelope.** The commanded fingertip-force render is itself a bounded quantity with a declared safe maximum; URML can check a render command against that declaration, the same way it checks any actuation output (RFC-0017).
- **Neutral by construction.** URML is substrate- and model-neutral; it composes above the command rather than depending on the driver's internals.

## What is asked

1. In a glove-teleoperation loop, would a declared capability + envelope on the robot side (and a declared render envelope on the glove side) be a useful pre-dispatch guard?
2. Would a small worked example mapping a teleoperated grasp onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, the `ros2_control` Layer-1 seam (RFC-0319), and `set_output` range checks (RFC-0017). Haptic-teleoperation anchor of the Move #70 wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `Adjuvo/senseglove_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move70.yaml`.
