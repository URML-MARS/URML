---
rfc: 0240
title: Reachy 2 integration, request for comment from Pollen Robotics maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0240: Reachy 2 integration, request for comment from Pollen Robotics maintainers

## Summary

URML is a small open language for robot intent that compiles to whatever runtime sits below. Reachy 2 is Pollen Robotics' commercial-OSS humanoid platform (bimanual, mobile-base variants), with the `reachy2-sdk` shipped Apache-2.0 and actively maintained (last commit 2025-11-26). This is a commercial-OSS hybrid, noted up front. This RFC asks Pollen Robotics one question. No spec change proposed, nothing for you to maintain.

## Concrete example

An English sentence:

> Hand me the red mug.

becomes a URML program:

```yaml
program:
  - pick_from: { object: red_mug_location }
  - move_to: { pose: operator_pose }
```

`reachy2-sdk` dispatches the pick into Reachy 2's bimanual arms via its MoveIt-derived planning and grasping stack (`reachy_sdk.parts.r_arm.goto(...)` for the reach, the gripper for the close), then drives the mobile base to the operator pose. URML's pre-flight `validate` step reads a manifest naming `reachy2-sdk` as the bridge and the Reachy 2 variant (bimanual fixed, or bimanual mobile) as the platform, so the English plan is checked against the right capability set before any motion command is issued.

## Why URML on this target

Reachy 2 is one of the cleaner commercial-OSS humanoid targets for URML: the SDK is Apache-2.0, the platform is bimanual with optional mobile base, and the manifest layer is exactly the place to declare which Reachy variant is in front of the runtime so the same English plan composes against either. The ask here is light: tell us whether `reachy2-sdk` is the right adapter target or whether the underlying ROS 2 stack is the cleaner integration layer.

## Capability-manifest mapping

| URML primitive       | reachy2-sdk surface                                     |
| -------------------- | ------------------------------------------------------- |
| `pick_from(object)`  | `reachy_sdk.parts.r_arm.goto(target)` plus gripper close|
| `place_at(pose)`     | `reachy_sdk.parts.r_arm.goto(target)` plus gripper open |
| `move_to(pose)`      | `reachy_sdk.parts.mobile_base.goto(x, y, theta)` (mobile variant) |
| `gesture(name)`      | named joint trajectory on head plus arms                |
| `read_sensor(camera)`| `reachy_sdk.parts.head.cameras` stream                  |

## Drawbacks

- Commercial-OSS hybrid: Pollen Robotics ships the hardware commercially, which constrains how much the SDK can absorb into a third-party validator.
- The bimanual fixed and mobile variants have different capability sets; one manifest per variant is unavoidable.
- URML's static validator cannot reason about live grasp feasibility; pick primitives stay best-effort.

## Unresolved questions

Does Pollen Robotics see `reachy2-sdk` as the right URML adapter target, or is the underlying ROS 2 stack the cleaner integration layer (cross-link to RFC-0200 on ROS 2)?

## How to respond

Best channel is a GitHub Issue on `pollen-robotics/reachy2-sdk` (Issues are enabled). The commercial-OSS hybrid framing is acknowledged in the issue's opening lines. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Apache-2.0 compatibility verified (reachy2-sdk is Apache-2.0).
- [x] Repo is not archived; last commit 2025-11-26.
- [x] No spec change proposed; manifest-mapping only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Cross-links noted: RFC-0202 (MoveIt 2), RFC-0239 (Poppy), RFC-0200 (ROS 2).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
