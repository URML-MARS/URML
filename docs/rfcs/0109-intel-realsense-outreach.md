---
rfc: 0109
title: Intel RealSense / RealSenseAI integration, request for comment from realsenseai/librealsense maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-27
updated: 2026-05-27
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

# RFC-0109: Intel RealSense / RealSenseAI integration, request for comment from realsenseai/librealsense maintainers

## Summary

URML does not yet ship a RealSense-specific manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Intel / RealSenseAI depth-camera line (D400, L515, T265, D435i and successors) over [`realsenseai/librealsense`](https://github.com/realsenseai/librealsense) and the sibling `realsense-ros` ROS 2 wrapper, and **requests review and feedback from the realsenseai/librealsense maintainers**. No spec change.

This is the first Move #10 RFC. Move #10 is URML's perception-vendor wave — 29 engageable cameras and sensors candidates verified 2026-05-27 across 15 sub-categories. RealSense leads as the flagship reference depth-camera SDK on GitHub.

## Motivation

`realsenseai/librealsense` is Apache-2.0, 8,800+ stars, 521 open issues, committed daily, and maintained by RealSenseAI engineers (the team that spun out from Intel; the historical `IntelRealSense/librealsense` namespace now redirects to `realsenseai/librealsense`). The repo carries Issues + Discussions both enabled and a CONTRIBUTING.md. That combination is what URML's perception-component outreach looks for first — vendor-direct, open license, daily cadence, dialogue surfaces open.

URML's v0.1 perception schema treats cameras as 2D image producers, with the 3D structure surfaced through the `Sensor` block (`measurement_type: point_cloud`, introduced by [RFC-0039](0039-3d-lidar.md) on the lidar side). RealSense produces both: RGB + depth + IMU + (in T265) tracking pose in a single device. The interesting URML-side question for the maintainer is whether the v0.1 schema cleanly expresses "RGB-D camera" or whether a future Spec RFC (parallel to RFC-0039's lidar `point_cloud`) is needed to model color + per-point attributes in one declaration. RFC-0035 (Zivid) flagged the same gap; RealSense reinforces it.

## Detailed design

Descriptive of an existing manifest-mapping plan plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `realsense_d435i_cell.yaml` fixture)

`Camera` block:

| URML field | Type | Maps to RealSense product attribute |
|---|---|---|
| `name` | Identifier | A deployment-chosen handle (`d435i`, `d455`, `t265`, `l515`) |
| `movable` | bool | Wrist-mounted vs fixed-mount per deployment |
| `supports_photo` | bool | `true` — RealSense streams RGB color frames |
| `supports_video` | bool | `true` — `pyrealsense2.pipeline()` exposes live streams |
| `supports_stream` | bool | `true` — multi-modality streams (color + depth + IMU) |
| `max_resolution` | string | Per-model: `1920x1080` (D435i), `1280x720` (D455), etc. |

`Sensor` block (per-device, for the structured measurements RealSense surfaces alongside RGB):

| URML field | Maps to |
|---|---|
| `measurement_type: point_cloud` | `pyrealsense2.pointcloud().calculate(depth_frame)` |
| `measurement_type: acceleration` (custom) | D435i / D455 / T265 internal IMU; URML's v0.1 enum has no `acceleration`, the `custom` escape-hatch carries it (same as RFC-0073 Marty) |
| `measurement_type: voltage` | Aux power readouts where available |

### What URML v0.1 does not yet express for RealSense

1. **RGB + per-point color on the same point cloud.** Same gap as RFC-0035 (Zivid) Q1: URML's `Sensor.point_cloud` is structurally scalar; per-point color + per-point attributes (SNR, normals) need a future Spec RFC.
2. **Inertial fusion semantics.** D435i and T265 emit fused pose/orientation; URML's manifest currently models the raw IMU outputs but not the fusion declaration.
3. **Stream synchronization timestamps.** RealSense's hardware-synced multi-stream timing is the kind of capability declaration that a manifest could carry but v0.1 does not.

### Compatibility notes

- **Vendor org.** [`realsenseai/librealsense`](https://github.com/realsenseai/librealsense) (cross-platform C++ SDK + `pyrealsense2`), [`realsenseai/realsense-ros`](https://github.com/realsenseai/realsense-ros) (ROS 2 wrapper, Apache-2.0).
- **Origin.** RealSenseAI, Santa Clara CA (US). Passes the US-federal default policy without flagging.
- **License fit.** Apache-2.0 inbound = outbound; URML's open-core stance composes cleanly. No CLA observed.
- **Cross-link.** Same color-on-point-cloud schema-extension question as [RFC-0035](0035-zivid-integration.md) (Zivid, engaged). When the Spec RFC for color-attributed point clouds lands, both Zivid and RealSense benefit.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: a future `reference/perception-runtime/` package with `RealSenseAdapter` is a natural target, but not in scope for this Outreach RFC. Adapter ships engagement-driven (the RFC-0073 Marty precedent).
- Conformance: a future `realsense_d435i_cell.yaml` manifest fixture + matching positive conformance case once the schema-extension question (Q1 above) lands.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code in this RFC. Adapter ships engagement-driven per RFC-0073 precedent.
- **Color-on-point-cloud schema gap.** v0.1 forces the RFC to use the `custom` measurement_type escape-hatch for RGB-D fusion claims; the Spec RFC that closes this gap is queued but not yet drafted.
- **Closed firmware on the cameras themselves.** Like Stereolabs ZED (RFC-0110), the camera firmware is closed; URML's manifest can describe the open SDK surface but not the underlying device behavior.

## Alternatives considered

1. **Ship the adapter first.** Rejected. URML's outreach posture is engagement-driven: RFCs surface the design questions, adapters ship after maintainer review.
2. **Combine RealSense + ZED + Roboception into a "depth-camera consortium" RFC.** Rejected. Each vendor has different licensing and surface posture; per-vendor RFCs let the conversation thread per vendor.
3. **Wait for the Spec RFC that resolves color-on-point-cloud.** Rejected. RealSense feedback is what informs that Spec RFC; engaging now provides the input.

## Prior art

- [`realsenseai/librealsense`](https://github.com/realsenseai/librealsense) — the upstream SDK.
- [`realsenseai/realsense-ros`](https://github.com/realsenseai/realsense-ros) — the ROS 2 wrapper.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — engaged 2026-05-27; same color-on-point-cloud schema-extension question surfaced.
- [RFC-0039 (3D lidar)](0039-3d-lidar.md) — introduced `measurement_type: point_cloud` for the Sensor block; the parallel for RGB-D cameras is the queued Spec RFC.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) — the engagement-driven adapter-ship pattern this RFC follows.

## Unresolved questions

For the `realsenseai/librealsense` maintainers:

1. **Color-on-point-cloud declaration.** URML's `Sensor.point_cloud` is structurally scalar today; how would you model the RGBA + per-point attribute combination that RealSense produces? Is a separate `measurement_type: color_point_cloud` the right shape, or a per-point attribute list on the existing `point_cloud` type, or something else?
2. **Inertial fusion semantics.** URML's manifest can declare the raw IMU outputs but not the fused-pose declaration that D435i / T265 emit. Is a `fusion` capability declaration something the manifest should carry, or is that better left to the application layer?
3. **Cross-stream synchronization.** Hardware-synced multi-stream timing is a real RealSense feature; should URML's manifest carry a `hw_sync: true` declaration so a downstream program can rely on it?
4. **Adapter home.** When the URML-side `RealSenseAdapter` ships, should it live in URML's `reference/perception-runtime/` (URML repo), in a separately-maintained `realsenseai/realsense-urml` repo under your org, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
5. **Conformance listing.** Would the realsenseai team consider a README or wiki link to URML's compatible-runtimes registry once a working `RealSenseAdapter` ships, basic tests pass, and a real-hardware demonstration is recorded? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Object-detection capability declaration.** URML has `query_detection` as a v0.1 primitive (`object_class`, `attributes`, `where_near`, `where_within` → `DetectionResult`). For RealSense specifically: does the librealsense SDK ship a native detection / segmentation / tracking surface that URML's manifest should declare (extending the existing `perception.object_vocabulary` field), or is detection always an application-layer concern (ML model layered on top of the depth + RGB streams)? Confidence-score semantics also worth pinning if there is a native surface.
7. **Anything else.**

## Implementation note

RFC-0109 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml). First Move #10 RFC.

## Requested feedback (from realsenseai/librealsense maintainers)

Items 1–6 from Unresolved questions above.

## How to respond

`realsenseai/librealsense` has both Issues and Discussions enabled with a CONTRIBUTING.md present. URML's planned channel: open a single Issue on `realsenseai/librealsense` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `realsenseai/librealsense` surface (Apache-2.0, 8788 stars, 521 open issues, Issues + Discussions enabled, CONTRIBUTING present, last commit 2026-05-27).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, schema gap, closed firmware).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: RealSenseAI, US; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
