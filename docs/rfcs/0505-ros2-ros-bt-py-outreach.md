---
rfc: 0505
title: ros2_ros_bt_py integration — request for comment
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

# RFC-0505: ros2_ros_bt_py integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`fzi-forschungszentrum-informatik/ros2_ros_bt_py`](https://github.com/fzi-forschungszentrum-informatik/ros2_ros_bt_py) (BSD-3-Clause, ~110 stars, active, FZI Karlsruhe) is a behavior-tree library with a Vue3 web GUI, an alternative to SMACH / FlexBE for ROS 2. URML's Layer-3 behavior composition is a peer to a behavior tree, so the two compose in either direction. This RFC asks which direction is useful.

## The mapping (URML beside ros2_ros_bt_py)

- **Lower URML to a BT, or dispatch a validated primitive from a BT leaf.** URML composition (sequence / parallel / branch) can lower onto a `ros2_ros_bt_py` tree; or a BT leaf can call a single URML primitive that is validated against the robot's capability manifest and envelope before it executes. Either way, URML adds the typed, statically-validated intent; the BT runtime stays the executor.
- **One validated description, two orchestration styles.** The same declared intent can be expressed as a URML program or driven from a BT, with the capability/envelope check applied once.

## What is asked

Request for comment from the ros2_ros_bt_py maintainers:

1. Is lowering URML composition to a `ros2_ros_bt_py` tree the more natural direction, or is a BT-leaf-dispatches-a-validated-URML-primitive the cleaner one?
2. Is a static capability/envelope check on the actions a tree dispatches useful to your users?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition and the behavior-tree / FSM interop engagements (Move #41: BehaviorTree.CPP, py_trees, SMACC2, FlexBE and others — composition is peer to BT/FSM; lower-to-engine or engine-leaf-dispatches-a-validated-primitive). Part of Move #45.

## Implementation note

Outreach only. The post is a GitHub Issue on `fzi-forschungszentrum-informatik/ros2_ros_bt_py` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
