---
rfc: 0598
title: CentraleNantesROV/bluerov2 integration — request for comment
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

# RFC-0598: CentraleNantesROV/bluerov2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the inspection-robotics wave (Move #55).

## Summary

[`CentraleNantesROV/bluerov2`](https://github.com/CentraleNantesROV/bluerov2) (Apache-2.0, Centrale Nantes) is a ROS 2 description, control, and simulation package for the BlueROV2, used for subsea work including hull and pipeline inspection. URML already ships a marine runtime and a BlueROV adapter, and a subsea inspection task is the kind of goal-plus-constraints intent URML declares and validates. This RFC asks whether the mapping is useful. (This is the Centrale Nantes academic ROS 2 stack, distinct from the BlueRobotics BlueOS/ArduSub ecosystem URML reached earlier.)

## The mapping (URML beside CentraleNantesROV/bluerov2)

- **Declare the inspection intent, validate, then the ROS 2 stack executes.** URML expresses an inspection goal plus its operating envelope (depth, standoff, geofence), validates against the vehicle's declared capabilities, then dispatches to the bluerov2 ROS 2 control. URML's marine drive type lowers onto this vehicle; the package keeps control and simulation.
- **A second BlueROV2 path.** URML's existing BlueROV adapter targets the BlueRobotics stack; this Centrale Nantes ROS 2 package is a different, academic route to the same vehicle, and the interesting question is whether one validated-intent layer can sit cleanly above both.

## What is asked

1. Is a typed, validated inspection-intent layer (declare goal + envelope, validate, dispatch) useful above the bluerov2 ROS 2 stack?
2. Does URML's marine vehicle capability model fit how this package describes the BlueROV2?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's marine runtime + BlueROV adapter (Move #32 marine wave), the plan_path / follow_trajectory consume model (RFC-0020), and the safety-envelope validation. Part of Move #55; the subsea-ROV-inspection target of the wave (with UNav-Sim RFC-0597).

## Implementation note

Outreach only. The post is a GitHub Issue on `CentraleNantesROV/bluerov2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move55.yaml`.
