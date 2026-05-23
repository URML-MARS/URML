---
rfc: 0032
title: Ouster integration — request for comment from ouster-lidar/ouster-sdk maintainers
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

# RFC-0032: Ouster integration — request for comment from ouster-lidar/ouster-sdk maintainers

## Summary

URML ships a brand-named Ouster manifest (`ouster_3d_lidar_cell.yaml`) and conformance fixture (`industrial/30_ouster_3d_lidar_cell_positive.yaml`) covering Ouster's 3D lidar product line via the existing v0.1 capability-manifest `Sensor` schema. This RFC documents the URML manifest mapping and **requests review and feedback from the ouster-lidar/ouster-sdk GitHub maintainers**. No spec change.

## Motivation

Ouster (Velodyne-merged 2023) is the dominant publicly-traded compliant 3D lidar vendor with the most active SDK on GitHub among the lighthouse parts vendors — `ouster-lidar/ouster-sdk` carries 511★ as of 2026-05-22 with 55+ open issues, multiple recent releases, and an active maintainer team. URML's manifest already declares Ouster's OS-series lidars under `Sensor.measurement_type: distance` for the URML-compliant warehouse / mobile / drone profiles.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for Ouster lidars

URML's manifest schema declares lidars under the `Sensor` block:

| URML field | Type | Maps to Ouster product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `os1_64`, `os2_128`) |
| `measurement_type` | enum incl. `distance` | All Ouster OS-series and REV7 lidars report `distance` (point-cloud range data) |
| `range_min` / `range_max` | float (units field) | Ouster's minimum and maximum range (OS-1: 0.25m–120m; OS-2: 0.5m–240m; etc.) |
| `units` | string | `m` for range |

The shipping `ouster_3d_lidar_cell.yaml` fixture declares an Ouster lidar on a mobile-base cell with `vendor: ouster` (US origin); the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) ACCEPTS with no flagging.

### What URML v0.1 *does not yet* express for Ouster lidars

The v0.1 `Sensor` schema is intentionally minimal. The following Ouster capabilities are **not currently expressible**:

1. **3D point-cloud structure.** URML's `Sensor.measurement_type: distance` reads as 1D distance; Ouster lidars produce full 3D point clouds (`x`, `y`, `z` per beam × per rev). The shape is implicit in `measurement_type: distance` for now — a future RFC could add a `point_cloud` measurement type or a `dimensionality: 3` modifier.
2. **Beam count / vertical resolution.** OS-0 (32 beams), OS-1 (32 / 64 / 128 beams), OS-2 (32 / 64 / 128 beams) — URML's manifest doesn't capture beam count, which matters for downstream perception.
3. **Frame rate / scan rate.** Ouster lidars run 10–20 Hz typically; URML's `Sensor` has no `rate_hz` field.
4. **Multi-return / intensity / reflectivity / near-IR channels.** Ouster's data structure includes more than range; URML's v0.1 `Sensor` is single-channel.
5. **Time synchronization (PTP / NMEA / IEEE 1588).** Ouster lidars are typically PTP grandmaster-synchronized in production AV deployments. URML has no time-sync manifest field.

These are not bugs — they are intentional v0.1 boundaries. Ouster's feedback could promote any of them to a future RFC, especially in the context of [RFC-0020](0020-autoware-av-substrate.md) (Autoware AV substrate Draft) which would benefit from richer lidar manifest fields.

### Compatibility notes

- **Vendor org.** `ouster-lidar/ouster-sdk` is the canonical repo. Vehicle / Velodyne legacy lidars are also accessible through it post-merger.
- **Origin.** Ouster, Inc., San Francisco, CA, USA; passes the US-federal default policy without flagging.
- **Cross-reference to AV substrate work.** [RFC-0020](0020-autoware-av-substrate.md) (Autoware AV) is the most likely consumer of richer Ouster manifest fields if the spec-gap loop promotes them.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `ouster_3d_lidar_cell.yaml` + `conformance/fixtures/industrial/30_ouster_3d_lidar_cell_positive.yaml` already shipping from Track I-C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Five v0.1 gaps is more than the SCHUNK RFC's four.** Lidars exercise more of the manifest's expressibility boundary than grippers; honest framing matters. The gaps are documented as RFC candidates, not failure modes.
- **No URML adapter drives Ouster.** Same posture as SCHUNK — parts are declared, not driven. The credibility lead-in is the manifest + AV-substrate alignment, not a runtime.

## Alternatives considered

1. **Defer to RFC-0020 AV-substrate maturation.** Rejected: Ouster fits the lighthouse Tier-1 set today; the gaps would be informed by Ouster's review.
2. **Add a `point_cloud` measurement type as part of this RFC.** Rejected: spec changes require their own RFC (per RFC-0014 spec-gap loop); this RFC is the *request* for feedback, not the spec change itself.

## Prior art

- `ouster-lidar/ouster-sdk` — the upstream SDK (511★, very active).
- Ouster's OS-series datasheet documentation.
- Ouster ROS 2 driver (`ouster-lidar/ouster-ros`).
- [RFC-0020](0020-autoware-av-substrate.md) (Autoware AV substrate Draft).
- RFC-0023..0031 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending ouster-lidar/ouster-sdk maintainer feedback:

1. **Point-cloud declaration.** Should URML's `Sensor` schema add a `point_cloud` measurement type, a `dimensionality` modifier, or both?
2. **Beam count / vertical resolution.** Should URML's manifest capture beam count, or is that purely deployment-side?
3. **Frame rate.** Should `Sensor.rate_hz` be added?
4. **Multi-channel data.** Should the `Sensor` block be extended with `channels: [range, intensity, reflectivity, near_ir, ...]`?
5. **Time synchronization.** Should URML have a manifest-level `time_sync: { method: ptp / nmea / ieee_1588 }` block, and if so where (top-level, per-`Sensor`)?
6. **AV substrate alignment.** Would Ouster review [RFC-0020](0020-autoware-av-substrate.md) (Autoware AV) for lidar-specific feedback?
7. **Conformance / directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**

## Implementation note

RFC-0032 ships as a single RFC document PR. No code / manifest / fixture change (Track I-C covered both). Draft state.

## Requested feedback (from ouster-lidar/ouster-sdk maintainers)

1. **Correctness of the mapping description.**
2. **The five v0.1 gaps** — which should be promoted to URML RFCs?
3. **AV substrate RFC-0020 review** — does Ouster see the right primitives in the proposal?
4. **Conformance / manufacturer-directory listing interest.**
5. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `ouster-lidar/ouster-sdk`. Private channel via `MAINTAINERS.md`.

## Maintainer feedback (2026-05-22)

[@Samahu](https://github.com/Samahu) replied substantively to all five questions on [`ouster-lidar/ouster-sdk#711`](https://github.com/ouster-lidar/ouster-sdk/issues/711#issuecomment-4520792253) within ~7 hours of the issue going up. Reply quoted verbatim by gap:

1. **Point-cloud declaration / units.**
   > Depends on how you choose to represent the data, in some interactions I had with the ROS community they prefer using standard unit [meters] to represent the data .. that will of course require you to use floating point representation ... however, if you want to preserve the original millimeter integer representation then I would think you have to include units as part of the schema.
2. **Beam count.**
   > I think it should capture the beam count.. each beam configuration is a different hardware. You can't change the beam count of a given sensor.
3. **Multi-channel and frame rate.**
   > These can be configured using the LidarMode and UDPLidarProfile include rate_hz.
4. **Time synchronization.**
   > Ouster sensor have support for 3 timestamps mode, it really depends whether the URML is setup as a configuration schema that the node would have to read and configure the sensor based on that.. if so then the answer is yes.
5. **AV substrate alignment (RFC-0020 review).**
   > Will try to take a look.

The most architecturally consequential point is (4): Samahu's pushback forced URML to take a stance on the *capability schema vs configuration schema* line. URML's stance is the former. The manifest declares what the sensor can do; the substrate driver picks the active mode at deployment time.

The five points (1)–(4) are resolved by [RFC-0039](0039-sensor-schema-v0-2-iteration.md), which adds `point_cloud` as a `measurement_type`, plus four additive optional Sensor capability fields (`beam_count`, `channels`, `time_sync_methods`, `rate_hz_max`), and formalizes the capability-vs-configuration stance in the Layer-1 HAL normative text. Point (5) remains open pending Samahu's RFC-0020 review.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in active SDK + concrete AV-substrate downstream consumer.
- [x] Detailed design names every affected component (Track I-C manifest / fixture; existing v0.1 schema).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (5 gaps; no runtime).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
