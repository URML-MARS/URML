---
rfc: 0119
title: Septentrio (Mosaic / AsteRx GNSS) integration, request for comment from septentrio-gnss maintainers
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

# RFC-0119: Septentrio (Mosaic / AsteRx GNSS) integration, request for comment from septentrio-gnss maintainers

## Summary

URML does not yet ship a Septentrio manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Septentrio's Mosaic-class and AsteRx-class high-precision GNSS receivers over [`septentrio-gnss/septentrio_gnss_driver`](https://github.com/septentrio-gnss/septentrio_gnss_driver) (BSD-3-Clause ROS 1 + ROS 2 driver), and **requests review and feedback from the septentrio-gnss maintainers**. No spec change.

## Motivation

`septentrio-gnss/septentrio_gnss_driver` is the highest-precision-GNSS Tier-A vendor surface in URML's Move #10 verification: BSD-3-Clause, 125 stars, 43 open issues, active maintenance, 21 vendor public repos, BE origin (NATO allied; US-federal default policy passes). The Mosaic / AsteRx line covers RTK-grade ground robotics + survey + heading applications.

URML's manifest provenance block records vendor + origin facts that compose with GNSS-class capability — but URML's v0.1 schema has no GNSS-specific declarations (constellation set, frequency bands, RTK / NTRIP correction acceptance, dual-antenna heading). All four Move-10 GNSS Tier-A vendors (Septentrio, NovAtel, MicroStrain, SBG) surface the same schema-extension question; engaging Septentrio first reflects that they have the cleanest standalone-GNSS surface (vs MicroStrain/SBG which are primarily INS).

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `septentrio_mosaic_cell.yaml` fixture)

`Sensor` block, GNSS-class:

| URML field | Maps to Septentrio product attribute |
|---|---|
| `name: gnss` (Sensor) | Mosaic-X5, Mosaic-H, AsteRx-i3 etc. |
| `measurement_type: custom` (gnss_position) | Latitude / longitude / altitude fix |
| `measurement_type: custom` (gnss_heading) | Mosaic-H dual-antenna heading |
| `measurement_type: custom` (rtk_status) | RTK fix state (fixed / float / standalone) |
| `units` | `degrees` (lat/lon), `m` (alt), `degrees` (heading) per channel |

### What URML v0.1 does not yet express for Septentrio

The GNSS-class schema gaps are the same across all four Move-10 GNSS vendors:

1. **Constellation declaration.** GPS / GLONASS / Galileo / BeiDou / QZSS / SBAS — Mosaic supports multi-constellation; URML's manifest has no declaration for which constellations a deployment uses.
2. **Frequency-band declaration.** L1 / L2 / L5 multi-band coverage is a Mosaic feature; manifest has no band declaration.
3. **RTK / NTRIP-correction declaration.** Septentrio receivers accept NTRIP corrections; manifest has no NTRIP block.
4. **Dual-antenna heading.** Mosaic-H emits heading from two-antenna baseline; URML's manifest currently models position but not antenna topology.
5. **Position accuracy declaration.** RTK-grade nominal accuracy (1cm + 1ppm) is a vendor spec; manifest has no `accuracy_m` for position (same anti-pattern URML chose to avoid for Zivid per RFC-0035 — accuracy is multi-dimensional).

### Compatibility notes

- **Vendor org.** [`septentrio-gnss/septentrio_gnss_driver`](https://github.com/septentrio-gnss/septentrio_gnss_driver), 21 public vendor repos.
- **Origin.** Septentrio NV, Leuven, BE. Passes US-federal default policy (NATO allied).
- **License fit.** BSD-3-Clause; cleanly composes with URML's Apache-2.0 stance.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: a future `reference/perception-runtime/` or `reference/sensor-runtime/` package with `SeptentrioGnssAdapter`. Out of scope here.
- Conformance: a future `septentrio_mosaic_cell.yaml` manifest fixture + positive conformance case after the GNSS-class Spec RFC clarifies the constellation / band / RTK declarations.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Five GNSS-schema gaps surfaced.** All queued as a future GNSS-class Spec RFC, parallel to RFC-0039 (lidar).
- **Per-constellation policy alignment.** US-federal default policy may have positions on specific constellation use (BeiDou is the obvious example); URML's manifest declaration should compose with that policy lane rather than fighting it.

## Alternatives considered

1. **Bundle Septentrio + NovAtel + u-blox into one GNSS RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor; u-blox (RFC-0133) has a different surface posture (community ROS driver at KumarRobotics).
2. **Wait for the GNSS-class Spec RFC.** Rejected. Septentrio's feedback informs that Spec RFC.
3. **Use `voltage` measurement_type for GNSS outputs.** Rejected (same reasoning as MicroStrain RFC-0117).

## Prior art

- [`septentrio-gnss/septentrio_gnss_driver`](https://github.com/septentrio-gnss/septentrio_gnss_driver) — the upstream driver.
- [RFC-0120 (NovAtel)](0120-novatel-hexagon-outreach.md) — parallel GNSS RFC, CA origin.
- [RFC-0117 (MicroStrain)](0117-microstrain-hbk-outreach.md) — IMU/INS RFC with INS-aided GNSS.
- [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — IMU/INS RFC with INS-aided GNSS.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — established the "multi-dimensional accuracy, no single scalar" precedent that URML's GNSS manifest will follow.

## Unresolved questions

For the `septentrio-gnss/septentrio_gnss_driver` maintainers:

1. **Constellation declaration.** Should URML's manifest declare which constellations (GPS / GLONASS / Galileo / BeiDou / QZSS / SBAS) a deployment uses? This is partly a policy-fit question (BeiDou as a US-federal-policy lane) and partly a capability declaration.
2. **Frequency-band declaration.** L1 / L2 / L5 multi-band — manifest declaration or runtime parameter?
3. **RTK / NTRIP-correction declaration.** Septentrio receivers accept NTRIP. Is "this receiver accepts NTRIP corrections from network X" something the manifest should carry?
4. **Dual-antenna heading.** Mosaic-H's heading-from-baseline output — how should URML's manifest declare antenna topology?
5. **Accuracy declaration.** URML accepted Zivid's framing (RFC-0035 Q2) that single-scalar accuracy misrepresents multi-dimensional reality. Does the same framing apply to GNSS? Per-mode accuracy figures (standalone vs RTK-float vs RTK-fixed) in the manifest, or out-of-band per datasheet?
6. **Adapter home.** When the URML-side `SeptentrioGnssAdapter` ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `septentrio-gnss/septentrio-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
7. **Conformance listing.** Would the Septentrio team consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0119 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## Requested feedback (from septentrio-gnss maintainers)

Items 1–8 from Unresolved questions above.

## How to respond

`septentrio-gnss/septentrio_gnss_driver` has Issues enabled. URML's planned channel: open a single Issue labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `septentrio-gnss/septentrio_gnss_driver` surface (BSD-3-Clause, 125 stars, 43 open issues, Issues enabled, last commit 2025-12-20).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, five GNSS-schema gaps, constellation-policy alignment).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: Septentrio BE; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
