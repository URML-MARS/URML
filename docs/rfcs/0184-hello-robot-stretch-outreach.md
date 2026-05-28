---
rfc: 0184
title: Hello Robot Stretch (mobile manipulator) integration, request for comment from hello-robot maintainers — license-clarification ask
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0184: Hello Robot Stretch (mobile manipulator) integration — license-clarification ask

## Summary

URML does not yet ship a Stretch manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Hello Robot Stretch mobile manipulator over [`hello-robot/stretch_ros2`](https://github.com/hello-robot/stretch_ros2), and **requests review and feedback from the hello-robot maintainers**. **License-clarification ask:** the repo has no SPDX license visible to the GitHub API; an explicit OSI declaration would unlock URML's adapter-grade reuse boundaries. No spec change.

**This is URML's first Move-14 RFC** (Theme B: mobile manipulators + commercial humanoids).

## Motivation

Hello Robot (US, MIT spin-off) is the most open-source-friendly mobile-manipulator OEM in URML's research surface. Stretch is a mobile-base + telescoping-arm + pan-tilt-camera composition designed for indoor / home-assistance / research deployments. Repo at [`hello-robot/stretch_ros2`](https://github.com/hello-robot/stretch_ros2) (no SPDX visible, 120 stars, Issues enabled, last commit `2026-05-26` very active — 2 days from cutoff, **not archived**).

URML benefits from documenting the Stretch manifest mapping because:

1. **Mobile-manipulator topology is a structural URML manifest gap.** Stretch's mobile-base + arm + head composition exercises URML's `mobility` + `actuators` + `cameras` blocks simultaneously — a cross-block boundary URML's existing fixtures (cobot-only or mobile-base-only) don't fully test.
2. **MIT-spinoff posture aligns with URML's open-core stance.** Hello Robot ships hardware, but their software ecosystem (`stretch_ros2`, `stretch_body`, `stretch_funmap`) is the vendor-direct engagement surface.
3. **License-clarification ask** is the gating fact: no SPDX upstream blocks Apache-2.0 downstream bundling. URML's adapter pattern compose at the ROS 2 interface boundary regardless, but per-surface OSI clarity unlocks deeper integration.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `hello_robot_stretch_cell.yaml` fixture)

| URML field | Maps to Stretch attribute |
|---|---|
| `name` | Specific configuration (`stretch_3`, `stretch_re1`, etc.) |
| `mobility.drive_type: differential` | Stretch differential mobile base — native v0.1 class (clean fit) |
| `actuators` | Telescoping arm + lift + wrist (revolute-prismatic mixed) |
| `cameras` | Head pan-tilt RGB-D (Intel RealSense D435i typical) — composes with RFC-0109 RealSense |
| `topology: custom` (`mobile_base_plus_arm_plus_head`) | Declares the composite topology |

### What URML v0.1 does not yet express for Stretch

1. **Mobile-manipulator topology declaration.** URML's v0.1 manifest declares mobility + actuators + cameras as separate blocks; the cross-block composite topology (mobile base + arm + head as a single integrated platform) is not first-class. Spec RFC queued — shared with RFC-0188 Fetch Robotics.
2. **Telescoping-arm kinematics.** Stretch's lift + telescope is a non-standard kinematic chain compared to the 6-DoF revolute pattern URML's cobot fixtures cover.
3. **Pan-tilt-head perception declaration.** URML's `cameras` block currently treats cameras as fixed; pan-tilt mounted cameras are a non-fixed configuration URML's manifest cannot today declare cleanly.

### Compatibility notes

- **Vendor org.** [`hello-robot`](https://github.com/hello-robot) — Hello Robot Inc., US (MIT spinoff).
- **Flagship repo.** [`hello-robot/stretch_ros2`](https://github.com/hello-robot/stretch_ros2) — license: none visible (clarification ask), 120 stars, Issues enabled, last commit 2026-05-26 very active, **not archived**.
- **Companion repos.** `hello-robot/stretch_body` (Python control library), `hello-robot/stretch_funmap` (functional mapping).
- **Origin.** Hello Robot Inc., US (Cambridge MA, MIT spinoff). Passes US-federal default policy.
- **License fit.** Pending clarification. URML's adapter composes at the ROS 2 interface regardless.
- **Maintainer signal.** Daily activity; MIT spinoff governance; the most open-source-friendly mobile-manipulator OEM URML's research surface identified.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; mobile-manipulator topology + telescoping-arm kinematics + pan-tilt-head perception Spec RFCs queued.
- Reference runtime: future `reference/mobile-manipulator-runtime/StretchAdapter` is a candidate — composes with the existing `reference/ros2-runtime/` adapter.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.** No SPDX upstream blocks Apache-2.0 downstream bundling.
- **Multiple Spec-RFC prerequisites** (mobile-manipulator topology, telescoping-arm kinematics, pan-tilt-head perception).
- **First Move-14 RFC** in a smaller wave (7 engageable targets reflecting closed-humanoid market reality).

## Alternatives considered

1. **Engage at `hello-robot/stretch_body` (Python control library) instead.** Considered. `stretch_ros2` is the ROS 2 entry point URML's adapter pattern targets first; `stretch_body` is the underlying Python layer for a future deeper engagement.
2. **Bundle Stretch + Fetch (sibling mobile-manipulator) into one RFC.** Rejected. Per-vendor RFCs let conversation thread per maintainer group; topology Spec RFC is the shared piece.
3. **Cross-citation only.** Rejected. Vendor-direct + very active + URML-fit is high enough for full manifest mapping.

## Prior art

- [`hello-robot/stretch_ros2`](https://github.com/hello-robot/stretch_ros2) — the upstream ROS 2 interface.
- URML's existing cobot-runtime fixtures (`kinova_cobot_cell.yaml`, `ur_cell.yaml`, `kassow_cobot_cell.yaml`) — the cobot-only pattern Stretch extends with a mobile base + head.
- URML's existing mobile-base fixtures (`clearpath_husky.yaml`, `turtlebot4_home_*`) — the mobile-base-only pattern Stretch extends with an arm + head.
- [RFC-0188 (Fetch Robotics)](0188-fetchrobotics-fetch-ros-outreach.md) — sibling mobile-manipulator RFC sharing the topology Spec-RFC gap.
- [RFC-0109 (Intel RealSense)](0109-intel-realsense-outreach.md) — Move-10 RGB-D camera RFC; Stretch's head-mounted RealSense composes naturally.

## Unresolved questions

For the hello-robot maintainers:

1. **License clarification.** Can `hello-robot/stretch_ros2` get an explicit OSI license declaration?
2. **Mobile-manipulator topology manifest fields.** URML's v0.1 has no `topology: mobile_base_plus_arm_plus_head` declaration. Spec RFC queued. Manifest field expectations from the Stretch perspective?
3. **Telescoping-arm kinematics.** Stretch's lift + telescope is a non-standard kinematic chain. Manifest field expectations?
4. **Pan-tilt-head perception declaration.** Should URML's manifest declare pan-tilt-mounted cameras as a distinct class vs fixed-mounted?
5. **Adapter home.** URML repo (`reference/mobile-manipulator-runtime/StretchAdapter`), Hello-Robot-maintained `hello-robot/stretch-urml-bridge`, or both?
6. **Conformance listing.** Would Hello Robot consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0184 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`hello-robot/stretch_ros2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license none visible, 120 stars, Issues enabled, last commit 2026-05-26 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, multiple Spec-RFC prerequisites, first Move-14 RFC).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Hello Robot Inc. US (MIT spinoff); default policy passes.
- [x] CLAUDE.md compliance check passed.
