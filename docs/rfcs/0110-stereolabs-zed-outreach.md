---
rfc: 0110
title: StereoLabs ZED integration, request for comment from stereolabs/zed-ros2-wrapper maintainers
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

# RFC-0110: StereoLabs ZED integration, request for comment from stereolabs/zed-ros2-wrapper maintainers

## Summary

URML does not yet ship a StereoLabs ZED manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the ZED stereo + RGB-D camera line (ZED 2i, ZED X, ZED Mini, ZED One) over [`stereolabs/zed-ros2-wrapper`](https://github.com/stereolabs/zed-ros2-wrapper) (Apache-2.0 ROS 2 wrapper) and the underlying closed-binary ZED SDK, and **requests review and feedback from the stereolabs/zed-ros2-wrapper maintainers**. No spec change.

## Motivation

`stereolabs/zed-ros2-wrapper` is an Apache-2.0 vendor-maintained ROS 2 wrapper (313 stars, 21 open issues, last commit 2026-05-27 active, maintainer Walter Lucetti / Myzhar — Stereolabs employee). It sits above a closed-binary ZED SDK distributed by Stereolabs (Paris FR + SF). URML's manifest will describe the wrapper interface honestly; the underlying SDK is a closed substrate detail the manifest cannot reason about. This is the same closed-core / open-wrapper pattern Robotical Marty (RFC-0073) navigates with `martypy` + closed firmware.

URML's Move #10 verification pass identified ZED as the strongest RGB-D vendor presence on GitHub after Intel RealSense (RFC-0109). Stereolabs also ships native vision-AI (object detection, body tracking, spatial mapping, fusion) inside the ZED SDK — which makes the object-detection capability-declaration question (raised in RFC-0109 and RFC-0115) particularly concrete here.

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `zed_2i_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to ZED product attribute |
|---|---|
| `name` | Deployment handle (`zed_2i`, `zed_x`, `zed_mini`) |
| `movable` | Wrist-mount vs fixed-mount per deployment |
| `supports_photo` | `true` — ZED streams left+right RGB |
| `supports_video` | `true` — continuous stereo |
| `supports_stream` | `true` — RGB + depth + IMU (where present) + pose tracking |
| `max_resolution` | Per-model: ZED 2i `2208x1242` (2.2K), ZED X `1920x1200` (HD1200) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: point_cloud` (custom for color attributes) | ZED SDK `sl::Mat` point cloud with RGBA |
| `measurement_type: custom` (acceleration) | ZED 2i / Mini internal IMU |
| `measurement_type: custom` (orientation) | ZED SDK positional-tracking pose quaternion |

### What URML v0.1 does not yet express for ZED

1. **Native detection / body-tracking / spatial-mapping declarations.** ZED SDK ships built-in object detection, body tracking, spatial mapping, fusion. URML's `query_detection` primitive maps onto this; the manifest needs richer declaration of which classes ZED's bundled models cover.
2. **Per-point color on point clouds.** Same gap as RFC-0035 (Zivid) and RFC-0109 (RealSense); the queued color-attribute Spec RFC closes this.
3. **Closed-SDK substrate boundary.** Manifest can describe the open wrapper surface; the closed binary's behavior is out of URML's reasoning scope.

### Compatibility notes

- **Vendor org.** [`stereolabs/zed-ros2-wrapper`](https://github.com/stereolabs/zed-ros2-wrapper) (Apache-2.0), [`stereolabs/zed-sdk`](https://github.com/stereolabs/zed-sdk) (samples + headers; closed binary at runtime).
- **Origin.** Stereolabs SAS, HQ Paris FR + SF office. Passes US-federal default policy (NATO allied).
- **License fit.** Open wrapper / closed SDK; URML's manifest reasons about the open layer only.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: future `reference/perception-runtime/` package with `ZedAdapter`. Out of scope here.
- Conformance: future `zed_2i_cell.yaml` fixture + positive conformance case after the detection-declaration + point-cloud-attribute Spec RFCs resolve.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Closed-SDK reasoning gap.** URML's adapter can call into the SDK but cannot reason about its internal behavior; same constraint as any closed-core vendor.
- **Detection-class declaration question is unresolved.** Bundled ZED detection models cover specific class taxonomies (custom + COCO-style); the manifest declaration shape is a vendor-feedback question.

## Alternatives considered

1. **Bundle ZED + RealSense + Roboception into one RGB-D RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor.
2. **Wait for the detection-declaration + point-cloud-attribute Spec RFCs.** Rejected. ZED's feedback informs both.
3. **Skip ZED because the core SDK is closed.** Rejected. Other closed-core vendors (Marty firmware in RFC-0073) work fine; URML's manifest reasons about the open wrapper.

## Prior art

- [`stereolabs/zed-ros2-wrapper`](https://github.com/stereolabs/zed-ros2-wrapper) — the upstream wrapper.
- [RFC-0109 (Intel RealSense)](0109-intel-realsense-outreach.md) — parallel RGB-D RFC, US origin.
- [RFC-0115 (ifm Effector)](0115-ifm-effector-outreach.md) — parallel ToF / native-detection RFC.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — color-on-point-cloud schema-extension precedent.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) — engagement-driven adapter-ship + closed-core / open-wrapper pattern.

## Unresolved questions

For the `stereolabs/zed-ros2-wrapper` maintainers:

1. **Native detection / body-tracking / spatial-mapping declaration.** ZED SDK ships bundled vision-AI. How should URML's manifest declare the supported detection classes + tracking modes so URML's `query_detection` primitive validates against the camera's actual capability set?
2. **Color + per-point attributes on point clouds.** Same question raised by RFC-0035 (Zivid) and RFC-0109 (RealSense). What's the right manifest shape from Stereolabs's perspective?
3. **Closed-SDK substrate boundary.** URML's manifest reasons about the open wrapper only. Is there a way the manifest could carry version pinning of the underlying SDK binary, or is that better left out?
4. **Adapter home.** When the URML-side `ZedAdapter` ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `stereolabs/zed-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
5. **Conformance listing.** Would the Stereolabs team consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0110 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`stereolabs/zed-ros2-wrapper` has Issues enabled with CONTRIBUTING.md. URML's planned channel: open a single Issue labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (Apache-2.0, 313 stars, 21 open issues, Issues enabled, CONTRIBUTING present, last commit 2026-05-27 active).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, closed-SDK gap, detection-declaration unresolved).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Stereolabs FR/US; default policy passes.
- [x] CLAUDE.md compliance check passed.
