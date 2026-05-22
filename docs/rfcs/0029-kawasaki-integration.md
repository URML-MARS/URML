---
rfc: 0029
title: Kawasaki integration — request for comment from Kawasaki-Robotics/khi_ros2 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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

# RFC-0029: Kawasaki integration — request for comment from Kawasaki-Robotics/khi_ros2 maintainers

## Summary

URML ships `KawasakiAdapter` compiling URML programs onto Kawasaki Heavy Industries arms via `Kawasaki-Robotics/khi_ros2` + MoveIt 2. This RFC documents the v0.1 primitive-to-driver mapping and **requests review and feedback from the Kawasaki-Robotics GitHub maintainers**. No spec change.

## Motivation

Kawasaki is one of the long-established industrial-arm vendors in Asia with strong presence in automotive welding, semiconductor handling, and clean-room pharma applications. The `Kawasaki-Robotics/khi_ros2` repo is **vendor-direct** (not community-only) with Issues open. The E series controllers + K-Roset offline programming + AS programming language make Kawasaki a distinct lighthouse from the FANUC/Yaskawa/KUKA mainline.

## Detailed design

Descriptive of existing URML artifacts. No spec text changes.

### URML v0.1 → Kawasaki driver primitive mapping

`KawasakiAdapter` composes `RclpyAdapter`. Gripper-server default: `_BRAND_GRIPPER_SERVER["kawasaki"]` = `/kawasaki/gripper/gripper_cmd`. Mapping shape identical to the industrial-arm pattern; `move_to` / `grasp` / `release` / `measure` / `wait_for` / `wait` / `report` → Protocol methods; `dock` / `detect` / `scan` / `capture` / `speak` / `listen` → `not_supported_on_industrial_arm[kawasaki]` sentinels; RFC-0013 industrial primitives compose Layer-3 sequences.

The Kawasaki-specific routing: MoveIt 2 plans a trajectory; the `khi_ros2` driver translates `control_msgs/FollowJointTrajectory` to the E-series controller; the controller's AS-language program executes the motion. Gripper commands route to `/kawasaki/gripper/gripper_cmd`.

A Kawasaki cell (RS series / BX series with a 2-finger gripper + wrist RGB) with RFC-0013 industrial primitives is expressible today through `KawasakiAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Japan (JP) is allied; `kawasaki` is not on the denylist.

### Compatibility notes

- **Controller line.** `Kawasaki-Robotics/khi_ros2` targets the E-series controllers. Legacy D / C controllers may not be covered.
- **AS-language invocation.** Kawasaki's on-controller programming language is AS (BASIC-derived). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding.
- **K-Roset.** Kawasaki's PC-side simulation/offline-programming environment; the `KawasakiAdapter` does not depend on K-Roset — only the runtime driver path is required.
- **Origin.** Kawasaki Heavy Industries, Ltd., Tokyo, Japan; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `kawasaki_cell.yaml` + `conformance/fixtures/industrial/09_kawasaki_cell_positive.yaml` already shipping from Track A.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **No Discussions venue.** `Kawasaki-Robotics/khi_ros2` has Issues but not Discussions; same fallback as FANUC (Issue-based outreach).
- **AS-language niche.** Same general property as VAL 3 / KRL / INFORM / MELFA-BASIC V — vendor-specific on-controller language not portable; `call_program` (Draft RFC-0015) is the binding-layer answer.

## Alternatives considered

1. **Wait for Discussions to be enabled.** Rejected: Issues are sufficient for the warm-touch hook.
2. **Combine with FANUC / Yaskawa / Mitsubishi into a "Japanese big-four" omnibus RFC.** Rejected: per-vendor RFCs remain individually citable.

## Prior art

- `Kawasaki-Robotics/khi_ros2` — the upstream driver.
- Kawasaki's AS programming reference + K-Roset documentation.
- ROS-Industrial Consortium per-vendor driver tracks.
- RFC-0023..0028 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending Kawasaki-Robotics/khi_ros2 maintainer feedback:

1. **Discussions enablement.** Would Kawasaki-Robotics consider enabling Discussions on the driver repo?
2. **AS-language invocation.** Should [RFC-0015](0015-control-program-invocation.md) `call_program` bind to an AS program launch?
3. **Legacy-controller support.** Is there interest in extending the driver to legacy D / C controllers?
4. **Conformance listing.** Would Kawasaki Heavy Industries list `KawasakiAdapter` per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0029 ships as a single RFC document PR. No code / manifest / fixture change (Track A covered both). Draft state.

## Requested feedback (from Kawasaki-Robotics/khi_ros2 maintainers)

1. **Correctness of the mapping description.**
2. **Discussions enablement.**
3. **AS-language binding for Draft [RFC-0015](0015-control-program-invocation.md).**
4. **Legacy-controller support.**
5. **Conformance listing per [RFC-0014](0014-substrate-conformance.md).**
6. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `Kawasaki-Robotics/khi_ros2`. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in vendor-direct GitHub presence + distinct market segment.
- [x] Detailed design names every affected component (none changed; Track A artifacts referenced).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (no Discussions; AS-language niche).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
