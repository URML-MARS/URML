---
rfc: 0500
title: magician_ros2 (Dobot Magician) integration — request for comment
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

# RFC-0500: magician_ros2 (Dobot Magician) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44), at the educational tier.

## Summary

[`jkaniuka/magician_ros2`](https://github.com/jkaniuka/magician_ros2) (MIT, active) is a ROS 2 control stack for the Dobot Magician, a common educational desktop manipulator. URML is interesting to a classroom arm as the English front door above the ROS 2 stack: "pick up the block and place it on the stack" becomes a typed `pick_from` / `place_at`, validated against the Magician's declared reach and payload before it moves. The educational tier is exactly where the "one English sentence moves a real arm" path matters. This RFC asks whether the mapping is useful.

## The mapping (URML beside magician_ros2)

- **Capability manifest.** The Magician's reach, payload, and end-effector map onto a URML Layer-1 manifest under the educational profile (RFC-0011). `pick_from` / `place_at` / `grasp` are validated against that workspace.
- **NL front door, then dispatch.** URML turns the classroom-friendly natural-language request into the typed primitive, validates it, and hands the motion to `magician_ros2`. URML adds the capability/envelope gate and the typed intent record above the ROS 2 stack.

## What is asked

Request for comment from the maintainer:

1. Does mapping the Dobot Magician (reach, payload, gripper) onto a URML educational-profile manifest read right?
2. Is an English-to-validated-pick/place front door above `magician_ros2` interesting for classroom use?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's manipulation primitives (`pick_from` / `place_at` / `grasp`), the educational profile and its adoption flywheel (RFC-0011), and the decide-then-do split (RFC-0002). URML already ships an `edu-runtime` with adapters for several classroom platforms. Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `jkaniuka/magician_ros2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
