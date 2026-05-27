---
rfc: 0125
title: Bosch Sensortec (MEMS IMU / pressure / environment) integration, request for comment from boschsensortec maintainers
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

# RFC-0125: Bosch Sensortec (MEMS IMU / pressure / environment) integration, request for comment from boschsensortec maintainers

## Summary

URML does not yet ship a Bosch Sensortec manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Bosch Sensortec's MEMS catalog (BMI / BHI IMU + Sensor Fusion, BMP / BMP3 barometric pressure, BME680 / BME690 gas, BMM350 magnetometer) over the [`boschsensortec`](https://github.com/boschsensortec) GitHub organization (33 public vendor repos), and **requests review and feedback from the boschsensortec maintainers**. No spec change.

This RFC pairs with RFC-0124 (Sensirion environmental) as URML's two-vendor coverage of the MEMS / environmental sensor layer — the layer that sits below mobility / perception / actuation and gates safety-envelope semantics. Bosch and Sensirion together cover the embedded-IMU and environmental measurement surfaces URML's micro-class robots (RFC-0018 `microbit_edu` pattern) and home / agriculture / industrial deployments rely on.

## Motivation

`boschsensortec` is a vendor-direct GitHub org with 33 public repos covering BHI385 (Sensor Fusion + BSEC + BSX algorithms), BME690 (gas / environment), BMM350 (magnetometer), and the broader per-sensor `*_SensorAPI` pattern. License posture is BSD-3-Clause on the per-sensor APIs (clean OSI fit); COINES_SDK and a few fusion-firmware repos are NOASSERTION (mixed posture — closed binaries for some Bosch fusion firmware like BSEC and BHy2). Vendor email `github@bosch-sensortec.com` and 495 followers reflect a real engineering org behind the public surface.

Bosch Sensortec's dominant low-power MEMS catalog covers the embedded IMU layer where URML's micro-class robotics (microbit_edu manifest pattern, RFC-0018) live. The catalog also extends to environmental gas + pressure sensing where it overlaps with Sensirion (RFC-0124). URML benefits from both vendors; their catalogs are complementary not duplicative.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `bosch_bhi385_cell.yaml` fixture)

`Sensor` block, multi-parameter MEMS:

| URML field | Maps to Bosch Sensortec product attribute |
|---|---|
| `name: imu` (Sensor) | BMI / BHI series IMU (accel + gyro + mag, optionally fused on-chip) |
| `measurement_type: custom` (acceleration) | Linear acceleration — v0.1 has no native `acceleration` |
| `measurement_type: custom` (angular_velocity) | Angular velocity |
| `measurement_type: custom` (orientation) | BHI fused-orientation output (where present) |
| `name: pressure` (Sensor) | BMP / BMP3 barometric pressure |
| `measurement_type: pressure` | Native v0.1 type (clean fit) |
| `name: gas` (Sensor) | BME680 / BME690 multi-gas sensor |
| `measurement_type: custom` (gas_resistance + voc_iaq) | Gas resistance + indoor-air-quality index |
| `name: magnetometer` (Sensor) | BMM350 3-axis magnetic |
| `measurement_type: custom` (magnetic_field) | Tri-axis magnetic field |

### What URML v0.1 does not yet express for Bosch Sensortec

1. **IMU measurement_types (`acceleration` / `angular_velocity` / `orientation`)** — same gap shared with RFC-0117 / RFC-0118 (MicroStrain / SBG); Spec RFC queued.
2. **Environmental scalar-array measurement_types (`gas_resistance` / `voc_iaq` / `magnetic_field`)** — same gap shared with RFC-0124 (Sensirion); Spec RFC queued.
3. **On-chip fusion firmware declaration.** BHI series ships closed binary fusion firmware (BSEC, BHy2, BSX) that the open per-sensor APIs invoke. URML's manifest can declare presence but cannot reason about behavior; same closed-core / open-API pattern as RFC-0073 Marty.

### Compatibility notes

- **Vendor org.** [`boschsensortec`](https://github.com/boschsensortec) — 33 public repos. Per-sensor `*_SensorAPI` BSD-3-Clause; COINES_SDK and fusion-firmware repos NOASSERTION (some binaries closed).
- **Origin.** Bosch Sensortec GmbH, Reutlingen DE. Passes US-federal default policy (NATO allied).
- **License fit.** Mixed (BSD-3-Clause + NOASSERTION + closed fusion firmware); per-API license clarification will be a per-RFC item before any adapter code reuse.
- **Maintainer signal.** Multi-week cadence across the per-sensor APIs; engineering org email behind the org.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; IMU + env-scalar Spec RFCs queued in parallel (shared with RFC-0117 / RFC-0118 / RFC-0124).
- Reference runtime: future `reference/sensor-runtime/` package with `BoschBhiAdapter` (IMU + fusion), `BoschBmpAdapter` (pressure), `BoschBmeAdapter` (gas/env), `BoschBmmAdapter` (magnetometer). Or one umbrella `BoschSensortecAdapter` parameterized by product family.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Mixed-license posture.** Per-sensor APIs are clean BSD-3-Clause; fusion firmware (BSEC, BHy2) is closed binary. URML's adapter reasons about the open API surface only.
- **Two Spec-RFC prerequisites.** IMU types + env-scalar-array. Same gaps as RFC-0117 / RFC-0118 / RFC-0124; engaging Bosch helps inform all three.

## Alternatives considered

1. **Per-product-family RFC** (RFC-0125a BMI/BHI, RFC-0125b BMP, ...). Rejected. Bosch Sensortec's catalog has uniform vendor-org maintainership; one outreach RFC covers the org cleanly. Per-family Spec RFCs for measurement_types are a separate matter.
2. **Bundle Bosch + Sensirion (RFC-0124) into one environmental-sensor RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; their catalogs are complementary, not duplicative.
3. **Defer Bosch until measurement_type Spec RFCs land.** Rejected. Bosch's feedback informs them.

## Prior art

- [`boschsensortec`](https://github.com/boschsensortec) — the upstream organization.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) + [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — sibling IMU/INS RFCs sharing the IMU-type Spec-RFC gap.
- [RFC-0124 (Sensirion environmental)](0124-sensirion-environmental-outreach.md) — sibling environmental-sensor RFC sharing the env-scalar-array Spec-RFC gap.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) Draft — the micro-class robot manifest pattern that Bosch MEMS naturally populate.

## Unresolved questions

For the `boschsensortec` maintainers:

1. **IMU measurement_type shape.** URML's v0.1 enum has no `acceleration` / `angular_velocity` / `orientation`; Spec RFC adding these is queued (parallel to RFC-0039's `point_cloud`). Bosch feedback on the shape — particularly for BHI fused-orientation outputs — would shape the Spec RFC.
2. **Environmental scalar-array measurement_type shape.** Gas resistance, VOC IAQ index, magnetic field — what manifest fields would a Bosch deployment expect (range, units, calibration_state, fusion_state)?
3. **On-chip fusion firmware declaration.** BHI ships closed fusion firmware (BSEC, BHy2, BSX). Should URML's manifest declare which fusion configuration is active, and how should it reason about behavior the closed firmware controls?
4. **Adapter shape.** One umbrella `BoschSensortecAdapter` parameterized by product family, or one adapter per product line? Maintenance preference matters.
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Bosch-maintained, or both?
6. **Conformance listing.** Would Bosch Sensortec consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0125 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

The `boschsensortec` org has 33 public repos; URML's planned channel: open a single Issue on the per-sensor repo with the most recent maintainer activity (likely `BHI385_SensorAPI` or `BME690_SensorAPI`) labelled `enhancement` or `question`, pointing to this RFC, with a request for redirect if a different repo is preferred for catalog-level discussions.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (BSD-3-Clause across per-sensor APIs, 33 public repos, 495 followers, multi-week cadence).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (mixed-license posture, two Spec-RFC prerequisites).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Bosch Sensortec DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
