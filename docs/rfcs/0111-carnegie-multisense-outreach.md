---
rfc: 0111
title: Carnegie Robotics MultiSense integration, request for comment from carnegierobotics maintainers
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

# RFC-0111: Carnegie Robotics MultiSense integration, request for comment from carnegierobotics maintainers

## Summary

URML does not yet ship a Carnegie Robotics MultiSense manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the MultiSense stereo-sensor family over [`carnegierobotics/multisense_ros2`](https://github.com/carnegierobotics/multisense_ros2) (MIT ROS 2 driver) and the sibling [`carnegierobotics/LibMultiSense`](https://github.com/carnegierobotics/LibMultiSense) C++ library, and **requests review and feedback from the carnegierobotics maintainers**. No spec change.

## Motivation

Carnegie Robotics MultiSense is a defense / space-grade stereo perception platform from Carnegie Robotics LLC (Pittsburgh PA, US-domiciled). The vendor org maintains the ROS 2 driver under MIT with active commits (last commit 2026-05-08); historical contributors include Heiko Hirschmueller and Daniel Scharstein, the same stereo-vision lineage that maintains RFC-0112 (Roboception). Low GitHub star count (6) reflects defense / space deployment focus rather than community-maker reach — but the vendor-direct presence + NDAA-friendly origin compensate fully.

URML's Move #10 perception wave includes MultiSense as one of three Tier A RGB-D / stereo Tier-A vendors (alongside RealSense RFC-0109 and ZED RFC-0110). MultiSense covers the defense / space niche the other two don't.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `carnegie_multisense_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to MultiSense product attribute |
|---|---|
| `name` | Deployment handle (`multisense_s30`, `multisense_sl`, etc.) |
| `supports_photo` | `true` — stereo left + right RGB |
| `supports_video` | `true` |
| `supports_stream` | `true` — multi-stream (RGB + disparity + point cloud + IMU where present) |
| `max_resolution` | Per-model |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: point_cloud` | MultiSense disparity-derived point cloud |
| `measurement_type: distance` | Disparity / depth frame |
| `measurement_type: custom` (acceleration) | Internal IMU where present |

### What URML v0.1 does not yet express for MultiSense

1. **Per-point attributes** — same point-cloud-color gap as RFC-0035 / RFC-0109 / RFC-0110 / RFC-0115.
2. **Defense / space-grade environmental envelope declaration** — MultiSense is rated for harsh environments; URML's manifest has no environmental-rating block today.

### Compatibility notes

- **Vendor org.** [`carnegierobotics/multisense_ros2`](https://github.com/carnegierobotics/multisense_ros2) (MIT), [`carnegierobotics/LibMultiSense`](https://github.com/carnegierobotics/LibMultiSense) (C++ library).
- **Origin.** Carnegie Robotics LLC, Pittsburgh PA, US. NDAA-friendly origin; passes US-federal default policy without flagging.
- **License fit.** MIT; cleanly composes with URML's Apache-2.0 stance.

### Spec / validator / reference-runtime / conformance changes

- None in this RFC. Future `reference/perception-runtime/` would host `MultiSenseAdapter` if engagement produces a green light.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Low GitHub stars.** 6 stars on the ROS 2 driver reflects deployment focus, not engagement risk; vendor-direct maintainership compensates.
- **Defense / space environmental envelope declaration is a v0.1 schema gap.**

## Alternatives considered

1. **Bundle MultiSense + Roboception into one stereo-vision RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor even when the maintainership lineage overlaps.
2. **Skip MultiSense because the star count is low.** Rejected. Star count doesn't reflect deployment scale in defense / space.

## Prior art

- [`carnegierobotics/multisense_ros2`](https://github.com/carnegierobotics/multisense_ros2) — the upstream driver.
- [RFC-0109 (Intel RealSense)](0109-intel-realsense-outreach.md) — parallel RGB-D RFC.
- [RFC-0110 (Stereolabs ZED)](0110-stereolabs-zed-outreach.md) — parallel stereo RFC.
- [RFC-0112 (Roboception)](0112-roboception-outreach.md) — sibling stereo-vision RFC with overlapping maintainer pedigree.

## Unresolved questions

For the `carnegierobotics/multisense_ros2` maintainers:

1. **Per-point attributes on point clouds.** Color + intensity per-point; same question raised by RFC-0035 (Zivid), RFC-0109 (RealSense), RFC-0110 (ZED), RFC-0115 (ifm).
2. **Defense / space environmental envelope declaration.** Should URML's manifest carry an environmental-rating block (operating temperature, IP rating, radiation tolerance) for MultiSense's deployment niche? If so, what fields would be useful?
3. **Detection-capability declaration.** Does MultiSense ship native detection / segmentation, or is detection always application-layer?
4. **Adapter home.** URML repo (`reference/perception-runtime/`), Carnegie Robotics-hosted, or both? URML's default assumption is the URML repo.
5. **Conformance listing.** Would Carnegie Robotics consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0111 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`carnegierobotics/multisense_ros2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (MIT, 6 stars, 5 open issues, Issues enabled, last commit 2026-05-08 active).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, low stars, environmental-rating gap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Carnegie Robotics US; default policy passes.
- [x] CLAUDE.md compliance check passed.
