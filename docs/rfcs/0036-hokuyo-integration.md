---
rfc: 0036
title: Hokuyo integration — request for comment from Hokuyo-aut/urg_node2 maintainers
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

# RFC-0036: Hokuyo integration — request for comment from Hokuyo-aut/urg_node2 maintainers

## Summary

URML ships a brand-named Hokuyo manifest (`hokuyo_lidar_cell.yaml`) and conformance fixture (`industrial/29_hokuyo_lidar_cell_positive.yaml`) covering Hokuyo's 2D lidar product line (URG / UST / UTM series) via the existing v0.1 `Sensor` schema. This RFC documents the URML manifest mapping and **requests review and feedback from the Hokuyo-aut GitHub maintainers**. No spec change.

This is the **last parts-vendor RFC in the Move #1 lighthouse program** (RFC-0031..0036 complete the parts tier).

## Motivation

Hokuyo Automatic Co., Ltd. is the long-established Japanese leader in 2D safety lidars and short-range scanning rangefinders, particularly strong in mobile-robot navigation (Husky / TurtleBot / AGV platforms) and lower-cost-of-deployment safety lanes. The URG-04LX, UST-10LX, UST-20LX, and UTM-30LX are among the most widely deployed 2D lidars in academic robotics and industrial AMR fleets.

The `Hokuyo-aut/urg_node2` repo is **vendor-direct**, active, with Issues open.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for Hokuyo lidars

URML's manifest schema declares lidars under the `Sensor` block:

| URML field | Type | Maps to Hokuyo product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `urg_04lx`, `ust_10lx`) |
| `measurement_type` | enum incl. `distance` | All Hokuyo lidars report ranged distance |
| `range_min` / `range_max` | float | Hokuyo's published min/max scan range |
| `units` | string | `m` |

The shipping `hokuyo_lidar_cell.yaml` fixture declares a Hokuyo URG-04LX with `vendor: hokuyo` (JP origin); the bundled US-federal default policy ACCEPTS with no flagging.

### What URML v0.1 *does not yet* express for Hokuyo lidars

1. **2D scan plane vs 3D point cloud.** Hokuyo 2D lidars (URG / UST / UTM) produce a single planar scan; this matches `measurement_type: distance` better than Ouster's 3D point clouds do. The gap is therefore smaller — but URML still doesn't capture scan-plane orientation or scan-angular-range explicitly.
2. **Frame rate** (same as RFC-0032 Ouster).
3. **Safety-rated subset.** Some Hokuyo models (UAM-05LP, UST-05LX) are SIL2 / Type 3 safety-rated; URML doesn't distinguish safety-rated from general-purpose (same gap as RFC-0033 SICK).
4. **Mobile-robot integration.** Hokuyo lidars are most often used on AMRs via ROS / Nav2 navigation stacks — URML's `mobile-runtime` already handles this via the existing Protocol. No URML-side gap, just a deployment integration note.

The gap list for Hokuyo is the smallest among the lighthouse parts vendors (4 vs 5 for Ouster / SICK / Festo / Zivid; SCHUNK had 4 too). 2D lidars genuinely fit URML's v0.1 `Sensor` schema cleanly.

### Compatibility notes

- **Vendor org.** `Hokuyo-aut` is the canonical GitHub presence. `urg_node2` is the ROS 2 driver; `urg_node` (legacy ROS 1) is also under the same org.
- **Origin.** Hokuyo Automatic Co., Ltd., Osaka, Japan; passes the US-federal default policy without flagging.
- **AMR / TurtleBot ecosystem.** Hokuyo lidars ship as default on many TurtleBot / Husky / Jackal configurations URML's `mobile-runtime` already supports.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `hokuyo_lidar_cell.yaml` + `conformance/fixtures/industrial/29_hokuyo_lidar_cell_positive.yaml` already shipping from Track I-C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Smallest gap list of the parts RFCs.** Could be read as Hokuyo being "less interesting" than Ouster / SICK / Festo / Zivid. More accurate framing: 2D lidars are exactly what URML v0.1 was designed to accommodate cleanly, and Hokuyo's product line is the canonical fit.

## Alternatives considered

1. **Combine with Ouster (3D lidar) and SICK (safety lidar) into one "lidar" RFC.** Rejected: per-vendor framing keeps the conversations distinct; each vendor has different segment focus (2D-general / 3D-AV / safety-industrial).
2. **Defer until the URG vs UST vs UTM product-line distinctions matter to URML.** Rejected: Hokuyo is part of the lighthouse Tier-1 set; the manifest is shipping; the RFC asks Hokuyo whether such distinctions should be promoted to URML.

## Prior art

- `Hokuyo-aut/urg_node2`, `Hokuyo-aut/urg_node` — upstream drivers (ROS 2 and ROS 1).
- Hokuyo's product datasheets (URG-04LX / UST-10LX / UST-20LX / UTM-30LX / UAM-05LP).
- RFC-0032 (Ouster) and RFC-0033 (SICK) for the parallel lidar RFCs.
- RFC-0023..0035 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending Hokuyo-aut/urg_node2 maintainer feedback:

1. **Scan-plane / angular-range declaration.** Should URML's `Sensor` capture scan-plane orientation and angular-range (e.g. `scan_angle_deg: 270`)?
2. **Frame rate** (same as RFC-0032 Ouster).
3. **Safety-rated subset.** Should URML have a safety-rating field (same as RFC-0033 SICK)?
4. **Conformance / directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**

## Implementation note

RFC-0036 ships as a single RFC document PR. Draft state.

## Requested feedback (from Hokuyo-aut/urg_node2 maintainers)

1. **Correctness of the mapping description.**
2. **The four v0.1 gaps.**
3. **Conformance / manufacturer-directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**
4. **Anything else.**

## How to respond

URML public Discussions:

> https://github.com/URML-MARS/URML/discussions

Or Issue on `Hokuyo-aut/urg_node2`. Private via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is the last parts RFC).
- [x] Motivation grounded in vendor-direct presence + AMR ecosystem fit.
- [x] Detailed design names every affected component.
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (smallest gap list could be misread).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md); compliant.
