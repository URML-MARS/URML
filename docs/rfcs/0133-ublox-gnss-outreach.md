---
rfc: 0133
title: u-blox (ubxlib + community KumarRobotics ROS driver) integration, request for comment from u-blox + KumarRobotics maintainers
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

# RFC-0133: u-blox (GNSS / RTK) integration, request for comment from u-blox + KumarRobotics maintainers

## Summary

URML does not yet ship a u-blox manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for u-blox's GNSS / RTK receivers (ZED-F9P, NEO-M9N, LEA-F9R, MAX series) over [`u-blox/ubxlib`](https://github.com/u-blox/ubxlib) (Apache-2.0, the vendor-direct embedded UBX-protocol library) and [`KumarRobotics/ublox`](https://github.com/KumarRobotics/ublox) (BSD-3-Clause, the community-maintained ROS driver), and **requests review and feedback from both maintainer groups**. No spec change.

This RFC complements [RFC-0119 (Septentrio)](0119-septentrio-outreach.md), [RFC-0120 (NovAtel / Hexagon)](0120-novatel-hexagon-outreach.md), and [RFC-0134 (Emlid)](0134-emlid-rtk-outreach.md). u-blox is the high-volume mass-market GNSS / RTK vendor; the four together cover the GNSS slice of Move-10.

## Motivation

u-blox AG (Thalwil, Switzerland) ships GNSS / RTK modules in volumes that no other vendor on URML's Move-10 list matches. ZED-F9P is the de facto cm-class RTK module under most hobby / consumer / micro-class robot fleets. URML's drone (RFC-0008), agriculture (RFC-0011 / RFC-0058), and field-mobile (RFC-0042) profiles all depend on u-blox modules in practice.

**Dual-surface engagement is the design point.** Two distinct GitHub presences matter:

1. **`u-blox/ubxlib` (vendor-direct, Apache-2.0)** — the embedded UBX-protocol library for MCU integration. 357 stars, Issues + CONTRIBUTING enabled, last commit 2024-11-11 (stale ~6 months from cutoff 2026-05-27, but still maintained on a slower cadence).
2. **`KumarRobotics/ublox` (community-maintained, BSD-3-Clause)** — the ROS / ROS 2 driver. 529 stars, last commit 2025-09-26 (active within URML's recency window). KumarRobotics is the UPenn GRASP / academic-research community fork; the de facto ROS-side u-blox driver in 2026.

URML-fit is via UBX protocol mapping more than driver adoption. Engagement asks both surfaces simultaneously.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ublox_zed_f9p_cell.yaml` fixture)

`Sensor` block, multi-measurement GNSS:

| URML field | Maps to u-blox product attribute |
|---|---|
| `name: gnss` (Sensor) | u-blox ZED-F9P / NEO-M9N / LEA-F9R receiver |
| `measurement_type: custom` (gnss_position) | NAV-PVT position fix (lat / lon / alt) |
| `measurement_type: custom` (gnss_velocity) | NAV-PVT velocity NED |
| `measurement_type: custom` (gnss_quality) | Fix-type + RTK status (no-fix / 3D / RTK-float / RTK-fixed) |
| `measurement_type: custom` (heading) | LEA-F9R dual-antenna heading |

### What URML v0.1 does not yet express for u-blox

1. **GNSS-class measurement_types** — same gap shared with RFC-0119 / RFC-0120 / RFC-0134; one Spec RFC adding `gnss_position` / `gnss_velocity` / `gnss_quality` / `heading` covers all.
2. **Multi-constellation declaration** (GPS / Galileo / GLONASS / BeiDou / QZSS / NavIC). u-blox modules vary by constellation support; URML's manifest cannot today declare this.
3. **Multi-frequency declaration** (L1 / L2 / L5). ZED-F9P is dual-frequency; NEO-M9N is single-frequency. URML's manifest cannot today declare frequency-band coverage.
4. **RTK correction-source declaration.** RTK requires an RTCM correction stream (NTRIP, base station, satellite-based correction). URML's manifest cannot today declare the correction-source pattern.

### Compatibility notes

- **Vendor org.** [`u-blox`](https://github.com/u-blox) — vendor-direct.
- **Vendor library.** [`u-blox/ubxlib`](https://github.com/u-blox/ubxlib) — Apache-2.0, 357 stars, Issues + CONTRIBUTING yes, last commit 2024-11-11.
- **Community ROS driver.** [`KumarRobotics/ublox`](https://github.com/KumarRobotics/ublox) — BSD-3-Clause, 529 stars, last commit 2025-09-26 active.
- **Origin.** u-blox AG, Thalwil, Switzerland. Passes US-federal default policy (NATO allied; CH).
- **License fit.** Apache-2.0 (ubxlib) + BSD-3-Clause (KumarRobotics/ublox); both cleanly compose with URML's stance.
- **Maintainer signal.** ubxlib actively maintained on slower cadence; KumarRobotics/ublox actively maintained on faster cadence; community trust signal strong.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; GNSS-class Spec RFC queued in parallel (shared with RFC-0119 / RFC-0120 / RFC-0134).
- Reference runtime: future `reference/sensor-runtime/UbloxAdapter` is a strong candidate; engagement clarifies whether to target ubxlib (embedded) or KumarRobotics/ublox (ROS-side) or both.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Dual-surface engagement** requires two issue posts (u-blox/ubxlib + KumarRobotics/ublox) — operational overhead but appropriate for the dual-surface fact.
- **ubxlib staleness** at ~6 months from cutoff is borderline; cadence is slower than the community driver.
- **GNSS-class Spec RFC prerequisite.** Same gap as RFC-0119 / RFC-0120 / RFC-0134.

## Alternatives considered

1. **Engage only u-blox (vendor) and ignore the community driver.** Rejected. KumarRobotics/ublox is the de facto ROS u-blox surface; ignoring it leaves URML's ROS-side path underspecified.
2. **Engage only KumarRobotics (community) and ignore the vendor.** Rejected. URML's outreach is vendor-direct first; ubxlib is the vendor surface and the right primary engagement.
3. **Bundle u-blox + Septentrio + NovAtel + Emlid into one GNSS RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; the GNSS-class Spec RFC is the shared piece.

## Prior art

- [`u-blox/ubxlib`](https://github.com/u-blox/ubxlib) — vendor-direct UBX-protocol library.
- [`KumarRobotics/ublox`](https://github.com/KumarRobotics/ublox) — community-maintained ROS / ROS 2 driver.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) + [RFC-0120 (NovAtel / Hexagon)](0120-novatel-hexagon-outreach.md) + [RFC-0134 (Emlid)](0134-emlid-rtk-outreach.md) — sibling GNSS / RTK RFCs sharing the GNSS-class Spec-RFC gap.

## Unresolved questions

For the u-blox maintainers:

1. **Vendor-vs-community engagement boundary.** Should URML treat `ubxlib` as the canonical vendor surface and `KumarRobotics/ublox` as a community add-on, or both as first-class?
2. **GNSS-class measurement_type shape.** URML's v0.1 has no native `gnss_position` etc. Spec RFC queued. Manifest-field expectations from u-blox's perspective (datum / WGS84 vs ITRF, fix-type granularity, constellation/frequency declaration)?
3. **RTK correction-source declaration.** Should URML's manifest declare the RTCM correction-source pattern (NTRIP, base-station, SBAS, PPP)?
4. **Adapter home.** URML repo (`reference/sensor-runtime/`), u-blox-maintained, or both?
5. **Conformance listing.** Would u-blox consider a README link to URML's compatible-runtimes registry once a working adapter ships?

For the KumarRobotics maintainers:

6. **Driver maintenance posture.** Is `KumarRobotics/ublox` planned for long-term ROS 2 support, or is it research-fork only?
7. **Cross-citation vs co-maintenance.** Would KumarRobotics accept a contributed URML-bridge example in the repo, or is cross-citation the right shape?
8. **Anything else.**

## Implementation note

RFC-0133 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

Dual-surface engagement: open two Issues, one on `u-blox/ubxlib` (vendor) and one on `KumarRobotics/ublox` (community), cross-referencing each other. Both labelled `enhancement` or `question`.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (ubxlib Apache-2.0 357 stars; KumarRobotics/ublox BSD-3-Clause 529 stars; both active).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (dual-surface engagement, ubxlib slower cadence, GNSS-class Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: u-blox CH; default policy passes.
- [x] CLAUDE.md compliance check passed.
