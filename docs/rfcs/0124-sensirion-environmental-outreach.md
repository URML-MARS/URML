---
rfc: 0124
title: Sensirion (environmental sensors) integration, request for comment from Sensirion maintainers
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

# RFC-0124: Sensirion (environmental sensors) integration, request for comment from Sensirion maintainers

## Summary

URML does not yet ship a Sensirion manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Sensirion's environmental sensor catalog (SHT humidity, SCD30 / SCD40 CO2, SEN66 multi-parameter air-quality, SPS particulate, and the broader BSD-3-Clause embedded-i2c-* / arduino-i2c-* family) over the [`Sensirion`](https://github.com/Sensirion) GitHub organization (252 public vendor repos), and **requests review and feedback from the Sensirion maintainers**. No spec change.

**This is URML's first environmental / chemical-sensor RFC.** Environmental sensing opens HVAC, agriculture (RFC-0093 Sentera precedent), air-quality safety, leak detection, and indoor-mobile-robot deployment lanes that visible / depth / IMU perception don't reach.

## Motivation

The Sensirion GitHub org is the exemplary vendor surface in URML's Move-10 verification: **252 public repos**, BSD-3-Clause uniformly across the per-sensor `arduino-i2c-*` + `embedded-i2c-*` driver pairs, multi-week activity cadence (SCD30 / SHT4x / SEN66 all pushed within May 2026), 343 followers. Sensirion AG (Switzerland) covers humidity, CO2, particulate, VOC, formaldehyde, air-quality multi-parameter sensors. The vendor org behaves structurally like an established software-OSS project — uncommonly aligned with URML's open-core stance.

URML's existing sensor coverage is mobility / perception / actuation-focused (lidar, RGB-D, IMU, F/T). Environmental measurements compose with safety-envelope primitives (RFC-0004 compliance policy, RFC-0012 safety-envelope semantics) — a robot operating in a CO2-above-threshold zone may need to refuse navigation; a humidity-out-of-range manifest can refuse warm-up. These are URML-side gates that Sensirion's data enables.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `sensirion_sen66_cell.yaml` fixture)

`Sensor` block, multi-parameter:

| URML field | Maps to Sensirion product attribute |
|---|---|
| `name: co2` (Sensor) | SCD30 / SCD40 CO2 reading |
| `measurement_type: custom` (co2_ppm) | Parts-per-million CO2 — v0.1 has no `co2` type |
| `name: humidity` (Sensor) | SHT3x / SHT4x relative humidity |
| `measurement_type: humidity` | Native v0.1 type (rare clean fit in Sensirion's range) |
| `name: temperature` (Sensor) | SHT3x / SHT4x temperature |
| `measurement_type: temperature` | Native v0.1 type |
| `name: particulate` (Sensor) | SPS30 particulate matter |
| `measurement_type: custom` (pm25_pm10) | PM2.5 / PM10 micrograms per cubic meter |
| `name: voc` (Sensor) | SGP4x VOC index |
| `measurement_type: custom` (voc_index) | Air-quality VOC index |

### What URML v0.1 does not yet express for Sensirion

1. **Environmental scalar-array measurement_types.** v0.1 has `temperature` and `humidity` (clean fits) but no native `co2`, `voc`, `particulate`, `formaldehyde`, `nox`. Spec RFC queued for an env-scalar-array extension; Sensirion is the natural vendor input.
2. **Safety-envelope cross-link.** Environmental thresholds (CO2 > 1000 ppm, humidity outside operating range) can gate URML primitive execution — the manifest could declare safety thresholds alongside the measurement declaration. Not in v0.1.
3. **Multi-parameter sensor topology.** SEN66 combines multiple sensors in one package; URML's manifest currently declares each as a separate `name` but doesn't express the shared-housing relationship.

### Compatibility notes

- **Vendor org.** [`Sensirion`](https://github.com/Sensirion) — 252 public repos uniformly BSD-3-Clause.
- **Origin.** Sensirion AG, Switzerland (CH). Passes US-federal default policy (NATO-aligned).
- **License fit.** BSD-3-Clause across the per-sensor driver catalog; cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Multi-week cadence across many sensor lines; exemplary vendor-OSS posture.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; env-scalar-array Spec RFC queued in parallel.
- Reference runtime: future `reference/sensor-runtime/` package with `SensirionMultiSensorAdapter` (and per-sensor adapters where useful).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Env-scalar-array Spec RFC is a prerequisite for clean manifest declaration of co2 / voc / particulate.** v0.1 `custom` escape-hatch is honest but limits validator depth.
- **Multi-parameter sensor topology gap** for products like SEN66.

## Alternatives considered

1. **Per-sensor RFC.** Considered (RFC-0124a SCD30, RFC-0124b SHT4x, etc.). Rejected. Sensirion's vendor-org pattern is uniform; one outreach RFC covers the org cleanly.
2. **Defer Sensirion until env-scalar-array Spec RFC lands.** Rejected. Sensirion's feedback informs that Spec RFC.

## Prior art

- [`Sensirion`](https://github.com/Sensirion) — the upstream organization.
- [RFC-0093 (Sentera)](0093-sentera-outreach.md) — agriculture multispectral payload precedent (humidity / temperature relevance).
- [RFC-0125 (Bosch Sensortec)](0125-bosch-sensortec-outreach.md) — sibling MEMS-environmental vendor RFC; partial product-line overlap (BME680 / BME690 vs Sensirion's SGP catalog).
- [RFC-0004 (compliance policy)](0004-compliance-policy.md) + [RFC-0012 (safety envelopes)](0012-safety-envelopes.md) — URML's envelope primitives that environmental measurements gate.

## Unresolved questions

For the Sensirion maintainers:

1. **Env-scalar-array measurement_type shape.** URML's v0.1 has `temperature` and `humidity` but no `co2` / `voc` / `particulate` / `formaldehyde` / `nox`. A Spec RFC adding these is queued; what manifest fields would a Sensirion deployment expect (range_min, range_max, units, calibration_state)?
2. **Multi-parameter sensor topology.** SEN66 combines multiple sensors in one package. Should URML's manifest express shared-housing relationships?
3. **Safety-envelope thresholds.** Environmental measurements gate URML primitive execution (RFC-0012). Should the manifest declare thresholds (CO2 > 1000 ppm refuses navigation) or is that always envelope-side?
4. **Per-sensor vs catalog-level engagement.** Should URML draft per-sensor RFCs (RFC-0124a SCD30, RFC-0124b SHT4x, ...), or is one catalog-level RFC the right shape from Sensirion's perspective?
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Sensirion-maintained `Sensirion/sensirion-urml` repo, or both?
6. **Conformance listing.** Would Sensirion consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0124 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

The Sensirion org has 252 public repos; URML's planned channel: open a single Issue on the most-engagement-active per-sensor repo (`Sensirion/arduino-i2c-scd30` or similar) labelled `enhancement` or `question`, pointing to this RFC, with a request for the maintainers to redirect if a different repo is preferred for catalog-level discussions.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (BSD-3-Clause across 252 repos, multi-week activity cadence).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, env-scalar-array Spec-RFC prerequisite, multi-parameter topology gap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Sensirion CH; default policy passes.
- [x] CLAUDE.md compliance check passed.
