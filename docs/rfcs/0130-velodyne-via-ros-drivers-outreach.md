---
rfc: 0130
title: Velodyne legacy-lidar (via ros-drivers) integration, request for comment from ros-drivers maintainers
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

# RFC-0130: Velodyne (legacy VLP/HDL via ros-drivers) integration, request for comment from ros-drivers maintainers

## Summary

URML does not yet ship a Velodyne legacy-lidar manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the legacy Velodyne VLP / HDL family (VLP-16, VLP-32C, HDL-32E, HDL-64E) over [`ros-drivers/velodyne`](https://github.com/ros-drivers/velodyne) (BSD-3-Clause, the community-maintained de facto driver), and **requests review and feedback from the ros-drivers maintainers**. No spec change.

**Routing question is the primary design point.** The Velodyne brand is now Ouster-owned (post-2023 merger). URML's outreach ledger already lists Ouster as engaged (RFC-0032, Samahu reply received). This RFC explicitly asks whether RFC-0130 should be (a) a community-maintained-driver engagement with ros-drivers, (b) a courtesy cross-link on the existing Ouster thread, or (c) both.

## Motivation

The Velodyne VLP-16 was the most-deployed mid-class lidar of the 2015-2022 era and persists in field-deployed fleets long after the OEM merged into Ouster. URML's perception coverage benefits from documenting the legacy-VLP manifest mapping because legacy-fleet operators are a real audience even after brand consolidation.

[`ros-drivers/velodyne`](https://github.com/ros-drivers/velodyne) is the canonical community-maintained ROS driver: BSD-3-Clause, 715 stars, 102 open issues, Issues + CONTRIBUTING enabled, last commit `2025-08-28` (active within URML's 6-month recency window). Recent committers include `jack-oquin` and `clalancette` — Open Robotics / ROS community names; not Velodyne-employed.

**Brand-consolidation overlap matters.** Ouster acquired Velodyne in 2023; the Velodyne product lines are Ouster-supported but legacy. URML already engaged Ouster (RFC-0032). Engaging ros-drivers for the *legacy* VLP/HDL surface is not a duplicate engagement; it covers the community-driver-maintained fork specifically, where Ouster's RFC-0032 covered the Ouster-OS family.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `velodyne_vlp16_legacy_cell.yaml` fixture)

`Sensor` block (lidar):

| URML field | Maps to Velodyne legacy product attribute |
|---|---|
| `name` | Deployment handle (`velodyne_vlp16`, `velodyne_hdl32e`) |
| `measurement_type: point_cloud` | Per-revolution 360° scan, native v0.1 type (clean fit) |
| `frame_rate` | 5-20 Hz (configurable per VLP family) |

### What URML v0.1 does not yet express for legacy Velodyne

1. **Per-point return-intensity declaration.** Same gap shared with already-engaged Ouster (RFC-0032) and SICK (RFC-0033); the color-on-point-cloud / per-point-attributes Spec RFC covers this once it lands.
2. **Dual-return mode declaration.** Velodyne VLP supports dual-return (strongest + last) per shot; URML's manifest cannot today declare this mode.
3. **Brand-consolidation declaration.** Legacy Velodyne is Ouster-owned; URML's manifest cannot today express vendor-of-record ≠ brand-of-record (interesting future question, not v0.1).

### Compatibility notes

- **Maintainer org.** [`ros-drivers`](https://github.com/ros-drivers) — community-org, not vendor-org.
- **Repo state.** [`ros-drivers/velodyne`](https://github.com/ros-drivers/velodyne) — BSD-3-Clause, 715 stars, 102 open issues, last commit 2025-08-28 active.
- **Origin.** Velodyne (acquired by Ouster, US). Passes US-federal default policy cleanly (Ouster-owned).
- **License fit.** BSD-3-Clause; cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Multi-maintainer ROS-community org; not OEM-maintained.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; per-point-attributes Spec RFC queued in parallel (shared with RFC-0032 Ouster, RFC-0033 SICK, RFC-0035 Zivid Q1).
- Reference runtime: future `reference/perception-runtime/` `VelodyneLegacyAdapter` is a candidate **only** if engagement settles on adapter shape vs cross-citation; community-driver wrapping is the more likely outcome.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Brand consolidation creates a routing overlap.** URML already engaged Ouster (RFC-0032); this RFC must explicitly disambiguate scope to avoid noise on the existing thread.
- **Community-org engagement, not vendor.** ros-drivers maintainers do not speak for Ouster on roadmap decisions; URML's adapter request lands on a community surface.
- **Legacy-only.** Modern Velodyne / Ouster product lines belong in the Ouster (RFC-0032) thread.

## Alternatives considered

1. **No separate RFC; cross-link on the Ouster thread (RFC-0032).** Considered seriously. Risk: legacy-VLP audience and community-driver maintainers (jack-oquin, clalancette) are not the same audience as Ouster engineering; the Ouster thread does not naturally route community-driver questions.
2. **Engage the ros-drivers org as the routing surface for all community-maintained lidar drivers.** Considered. Out of scope for this RFC; a separate operational RFC for community-driver outreach could centralize this question.
3. **Skip Velodyne legacy entirely as duplicate with Ouster.** Rejected. Legacy-fleet audience is real, distinct, and ros-drivers community is the de facto maintenance surface.

## Prior art

- [`ros-drivers/velodyne`](https://github.com/ros-drivers/velodyne) — the upstream community driver.
- [RFC-0032 (Ouster)](0032-ouster-lidar-outreach.md) — already-engaged Ouster thread; primary engagement for current product lines.
- [RFC-0033 (SICK)](0033-sick-safety-lidar-outreach.md) — sibling lidar RFC sharing the per-point-attributes Spec-RFC gap.
- [RFC-0039 (point_cloud)](0039-point-cloud-measurement-type.md) — native point_cloud type.

## Unresolved questions

For the ros-drivers maintainers:

1. **Routing.** Should this engagement live as an Issue on `ros-drivers/velodyne`, as a cross-link on the existing Ouster thread (RFC-0032), or both?
2. **Per-point-attributes Spec RFC shape.** URML's v0.1 `point_cloud` is a single measurement_type; intensity / dual-return / time-of-flight per-point are not yet first-class. What manifest fields would the community driver expect?
3. **Dual-return mode declaration.** Velodyne VLP supports dual-return; should URML's manifest declare this as a per-sensor capability?
4. **Maintenance posture.** Is `ros-drivers/velodyne` planned for long-term legacy support, or does the community expect users to migrate to Ouster-OS drivers as legacy hardware ages out?
5. **Adapter home.** URML repo (`reference/perception-runtime/`), `ros-drivers/velodyne_urml` contributed branch, or cross-citation only?
6. **Anything else.**

## Implementation note

RFC-0130 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml). A courtesy reference on the Ouster thread (RFC-0032) is appropriate once this RFC lands on `main`.

## How to respond

`ros-drivers/velodyne` has Issues enabled and CONTRIBUTING present. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the routing question front and centre.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (community-driver active, 715 stars, last commit 2025-08-28).
- [x] At least one alternative considered (three; brand-consolidation routing is the primary design point).
- [x] Drawbacks real (brand overlap with Ouster, community-not-vendor engagement, legacy-only scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Velodyne / Ouster US; default policy passes.
- [x] CLAUDE.md compliance check passed.
