---
rfc: 0115
title: ifm Effector (O3X / O3R / O3D) integration, request for comment from ifm/ifm3d maintainers
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

# RFC-0115: ifm Effector (O3X / O3R / O3D) integration, request for comment from ifm/ifm3d maintainers

## Summary

URML does not yet ship an ifm Effector manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for ifm's O3X / O3R / O3D 3D-ToF perception line over [`ifm/ifm3d`](https://github.com/ifm/ifm3d) (Apache-2.0 C++ SDK + Python bindings) and the sibling [`ifm/ifm3d-ros2`](https://github.com/ifm/ifm3d-ros2) ROS 2 driver, and **requests review and feedback from the ifm/ifm3d maintainers**. No spec change.

## Motivation

`ifm/ifm3d` is one of the cleanest perception-vendor surfaces URML's Move #10 verification pass identified: Apache-2.0 top to bottom (SDK + ROS 2 driver both), Issues + **Discussions** both enabled on the SDK repo, active maintenance with commits days ago. The vendor-org maintainership pattern (Suraj Patil, Rasheed Khan Pathan and others) is exactly what URML's "no blind posts" outreach rule looks for: vendor-direct, OSI top to bottom, dialogue surfaces open.

ifm's O3R platform is also distinctive in the perception slice because it ships a vendor-native perception pipeline (segmentation, ODS-style obstacle detection) on the camera itself, not only raw depth + amplitude. URML's `query_detection` primitive maps cleanly to that native surface — assuming the manifest can declare what classes / outputs ifm's on-camera pipeline exposes. That declaration is the design question this RFC surfaces.

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `ifm_o3r_cell.yaml` fixture)

`Camera` block:

| URML field | Type | Maps to ifm product attribute |
|---|---|---|
| `name` | Identifier | Deployment handle (`ifm_o3r`, `ifm_o3d303`, `ifm_o3x101`) |
| `movable` | bool | Cell-mounted typical for industrial cells; `false` for fixed stations |
| `supports_photo` | bool | `true` — ifm emits amplitude + RGB (where present) frames |
| `supports_video` | bool | `true` — streams are continuous |
| `supports_stream` | bool | `true` — multi-port (O3R streams up to 6 head ports + IMU) |
| `max_resolution` | string | Per-model: O3R `1280x800` (RGB head), O3D `352x264` (depth) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: point_cloud` | `ifm3d.FrameGrabber` XYZ image (`ifm3d::Image::XYZ`) |
| `measurement_type: distance` | Raw radial-distance frame |
| `measurement_type: custom` (intensity / amplitude) | Reflectance-amplitude frame; v0.1 enum has no `amplitude` |
| `measurement_type: acceleration` (custom) | O3R IMU; v0.1 enum has no `acceleration` |

### What URML v0.1 does not yet express for ifm

1. **On-camera detection / segmentation outputs.** O3R's ODS (Obstacle Detection System) and segmentation are vendor-native; URML's `query_detection` is the primitive that calls them, but the manifest has no first-class declaration for "this camera ships a detection model with classes X / Y / Z." Same gap as RealSense (RFC-0109) but ifm has more native pipeline.
2. **Per-point intensity / amplitude alongside XYZ.** Same color-attribute gap as RFC-0035 (Zivid) and RFC-0109 (RealSense): the `point_cloud` measurement_type is scalar, not attributed.
3. **Multi-port topology.** O3R can mount up to 6 perception heads on one VPU; URML's manifest treats each as a separate Camera entry but does not express the shared-VPU topology.

### Compatibility notes

- **Vendor org.** [`ifm/ifm3d`](https://github.com/ifm/ifm3d) (core C++ + Python, Apache-2.0), [`ifm/ifm3d-ros2`](https://github.com/ifm/ifm3d-ros2) (ROS 2 driver, Apache-2.0).
- **Origin.** ifm electronic GmbH, Essen, Germany (DE). Passes the US-federal default policy without flagging (NATO allied origin).
- **License fit.** Apache-2.0 inbound = outbound on both layers; URML's open-core stance composes cleanly. Best Apache-2.0-top-to-bottom posture in the optical-perception slice.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: a future `reference/perception-runtime/` package with `IfmO3RAdapter` is the natural target. Out of scope for this Outreach RFC.
- Conformance: a future `ifm_o3r_cell.yaml` manifest fixture + matching positive conformance case once the on-camera-detection declaration question (Q1 below) is resolved.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven adoption per RFC-0073 precedent.
- **Two schema-extension gaps surfaced.** On-camera detection declaration + per-point attributes on point clouds. Both are queued Spec RFCs, not closed here.
- **VPU topology not modeled.** O3R's multi-head perception cluster is structurally different from the single-camera assumption URML's manifest currently makes.

## Alternatives considered

1. **Bundle on-camera detection into the URML adapter's `query_detection` implementation without a manifest declaration.** Rejected. Without a manifest declaration, the validator can't surface which classes the camera supports; programs would fail at runtime instead of at validation time. Validate-before-actuate is the URML invariant.
2. **Wait for the schema-extension Spec RFCs before engaging ifm.** Rejected. ifm's feedback is part of what informs those Spec RFCs; engaging now gets the input.
3. **Combine ifm + Roboception + Zivid into a single "industrial 3D vision" RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor; Roboception (RFC-0112) and Zivid (RFC-0035, already engaged) are separate threads.

## Prior art

- [`ifm/ifm3d`](https://github.com/ifm/ifm3d) — the upstream SDK.
- [`ifm/ifm3d-ros2`](https://github.com/ifm/ifm3d-ros2) — the ROS 2 driver.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — engaged 2026-05-27; surfaces the parallel point-cloud-attributes question.
- [RFC-0109 (Intel RealSense)](0109-intel-realsense-outreach.md) — same depth-camera class, parallel detection-declaration question.
- [RFC-0039 (3D lidar)](0039-3d-lidar.md) — introduced `measurement_type: point_cloud` for the Sensor block.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) — engagement-driven adapter-ship pattern.

## Unresolved questions

For the `ifm/ifm3d` maintainers:

1. **On-camera detection / segmentation declaration.** O3R's ODS and per-port perception pipelines emit class labels and obstacle masks. How should URML's manifest declare that a given O3R deployment supports detection classes X / Y / Z, so URML's `query_detection` validates against the camera's actual capability set?
2. **Per-point intensity / amplitude on point clouds.** URML's `point_cloud` is scalar today; ifm emits XYZ + amplitude per point and (with RGB heads) XYZ + RGB. What's the right manifest shape?
3. **VPU multi-port topology.** O3R can host 6 heads on one VPU; URML's manifest treats each as a separate Camera entry. Is a shared-VPU declaration something the manifest should carry?
4. **Adapter home.** When the URML-side `IfmO3RAdapter` ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `ifm/ifm3d-urml` repo under your org, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
5. **Conformance listing.** Would the ifm team consider a README or Discussions link to URML's compatible-runtimes registry once a working adapter ships and a real-hardware demonstration is recorded? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Cross-link to RFC-0109 / RFC-0035.** The detection-declaration and point-cloud-attributes questions surface across RealSense, Zivid, and now ifm. Is there an industrial-3D-vision consortium-style design pattern you'd suggest, or are vendor-specific manifest blocks the right shape?
7. **Anything else.**

## Implementation note

RFC-0115 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## Requested feedback (from ifm/ifm3d maintainers)

Items 1–7 from Unresolved questions above.

## How to respond

`ifm/ifm3d` has both Issues and Discussions enabled. URML's planned channel: open a single Discussion on `ifm/ifm3d` (per the repo's preference for design conversations over Issues), pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `ifm/ifm3d` surface (Apache-2.0, 116 stars, 4 open issues, Issues + Discussions both enabled, last commit 2026-05-13).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two schema gaps, VPU topology gap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: ifm DE; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
