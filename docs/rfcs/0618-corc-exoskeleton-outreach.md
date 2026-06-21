---
rfc: 0618
title: CANOpenRobotController (CORC) integration — request for comment
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

# RFC-0618: CANOpenRobotController (CORC) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the wearable-and-assistive sub-lane of Move #59.

## Summary

[`UniMelbHumanRoboticsLab/CANOpenRobotController`](https://github.com/UniMelbHumanRoboticsLab/CANOpenRobotController) (Apache-2.0, University of Melbourne Human Robotics Lab) is an open C++ control stack that sends CANopen position and torque commands to exoskeletons and rehabilitation devices (the Fourier X2 exo, the ArmMotus M1/M2/M3 rehab robots, and custom hardware). It is the layer that turns a controller's decision into real motion on a device worn by or moving a person. URML is a validated-intent layer that sits one level above a stack like this: it declares the rehab or assist subtask as a typed goal with an explicit envelope of admissible joint torques and positions, validates that envelope against the device's declared capabilities before anything moves, and then leaves the CANopen control to CORC. This is a request for comment.

## The relationship (URML beside CORC)

- **Declare the subtask and its envelope, leave the control to CORC.** An assist or rehab subtask (move this joint to this position, never exceeding this torque, within these limits) is a goal plus hard constraints. URML expresses that as a typed primitive, validates it in five passes against a capability manifest and a safety envelope, and only then is the motion trusted to CORC's CANopen layer. CORC keeps the real-time control loop; URML is the static check that runs before the loop is handed an intent.
- **Why the envelope matters more here.** On a device coupled to a person, the safety envelope is the whole point. A declared ceiling on joint torque and a declared range on position are exactly the things URML is built to state once and check every time, before a command reaches the actuator. That is a narrow, honest role, and it lines up cleanly with what an exo or rehab stack already cares about.

## What is asked

1. Is a typed, statically-validated intent layer (declare the subtask goal and a torque/position envelope, validate against the device's capabilities, then hand control to CORC) useful above a CANopen control stack like this?
2. Does an exoskeleton or rehab device's operating envelope (per-joint torque ceilings, position ranges, mode constraints) map onto a URML capability manifest and safety envelope cleanly enough to be worth sharing?
3. Which device family would be the most natural first place to try the mapping?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest and safety-envelope validation, the plan/consume model where URML declares and checks while the substrate computes and actuates (RFC-0020), and the joint-limit modeling used across the manipulation profiles. Anchor of the wearable-and-assistive sub-lane of Move #59; the actuation-altitude assistive target where the safety envelope is load-bearing.

## Implementation note

Outreach only. The post is a GitHub Issue on `UniMelbHumanRoboticsLab/CANOpenRobotController` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is Apache-2.0; stated, not asked. Tracked in `examples/lighthouses/outreach-move59.yaml`.
