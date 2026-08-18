---
rfc: 0679
title: Closed-Chain Affordance ROS 2 (UTNuclearRoboticsPublic/closed-chain-affordance-ros) integration — request for comment
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

# RFC-0679: Closed-Chain Affordance ROS 2 (UTNuclearRoboticsPublic/closed-chain-affordance-ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the nuclear / hazmat remote-handling wave (Move #70).

## Summary

[`UTNuclearRoboticsPublic/closed-chain-affordance-ros`](https://github.com/UTNuclearRoboticsPublic/closed-chain-affordance-ros) (UT Austin Nuclear Robotics Group) is a robot-agnostic ROS 2 interface to the Closed-Chain Affordance planner, which plans joint trajectories for manipulation tasks expressed as linear, rotational, or screw motions and runs them on real arms (Spot arm, Kinova Gen3), with MoveIt self-collision checking. Because it emits a concrete joint trajectory to a real arm, URML's validate-before-actuate gate has a surface: URML declares the goal, then checks the planned trajectory is admissible on the specific arm (reach, joint limits, envelope) before execution. This is a request for comment.

## The relationship (URML beside the CCA planner)

- **URML consumes the trajectory, it does not constrain the planner.** The CCA planner decides the motion; URML checks the resulting trajectory is admissible on the declared arm, inside the declared safety envelope, before dispatch. URML is not a source of planning constraints; it is the admissibility check after planning.
- **Robot-agnostic meets robot-specific.** The interface is deliberately robot-agnostic; a per-robot capability manifest is the declaration the planned trajectory can be checked against when it lands on a particular Spot or Kinova arm.
- **Neutral by construction.** URML is substrate- and model-neutral; it composes above the trajectory rather than depending on the planner's internals.

## What is asked

1. Would checking a CCA-planned trajectory against a declared per-robot capability + safety envelope be a useful pre-dispatch guard, given the interface already targets multiple real arms?
2. Would a small worked example validating one CCA trajectory against a URML manifest (no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Consume-the-trajectory-and-validate framing (RFC-0020). Part of the Move #70 nuclear / hazmat remote-handling wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `UTNuclearRoboticsPublic/closed-chain-affordance-ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move70.yaml`.
