---
rfc: 0498
title: quadruped_ros2_control integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0498: quadruped_ros2_control integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`legubiao/quadruped_ros2_control`](https://github.com/legubiao/quadruped_ros2_control) (Apache-2.0, ~525 stars, active) provides `ros2_control` implementations for quadruped robots, including a sim-to-real path. URML is interesting one layer above: a locomotion intent for a quadruped becomes a typed primitive, validated against the robot's declared legged structure and stability limits, then dispatched onto the `ros2_control` controllers this project provides. This RFC asks whether the mapping is useful.

## The mapping (URML beside quadruped_ros2_control)

- **Capability manifest.** The quadruped's legged `drive_type` and its `whole_body` stability limits (center-of-mass / support polygon, RFC-0384) map onto a URML manifest. A locomotion intent is validated against that envelope before dispatch.
- **The ros2_control seam.** URML validates and emits the goal; `quadruped_ros2_control`'s controllers execute it. URML already treats `ros2_control` as a Layer-1 HAL seam (RFC-0319), so this is a concrete quadruped instance of that mapping, not a new mechanism.

## What is asked

Request for comment from the maintainer:

1. Does a URML manifest for a quadruped (legged `drive_type` + `whole_body` limits) read right for the robots this stack targets?
2. Is a validated-intent layer that emits goals onto the `ros2_control` controllers interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's legged `drive_type`, the `whole_body` declaration (RFC-0384), the `ros2_control` HAL seam (RFC-0319), and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `legubiao/quadruped_ros2_control` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
