---
rfc: 0116
title: Teledyne FLIR (Boson thermal cameras) integration, request for comment from FLIR maintainers
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

# RFC-0116: Teledyne FLIR (Boson thermal cameras) integration, request for comment from FLIR maintainers

## Summary

URML does not yet ship a Teledyne FLIR manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Teledyne FLIR's Boson thermal-camera line over [`FLIR/BosonUSB`](https://github.com/FLIR/BosonUSB) (MIT, USB Video Class utility for the Boson 320 / 640 thermal compact line), and **requests review and feedback from the FLIR maintainers**. No spec change.

**This is URML's first thermal / IR-camera RFC.** Thermal cameras emit per-pixel temperature (or radiometric) values; URML's v0.1 perception schema has `measurement_type: temperature` (scalar) but not a thermal-array per-pixel type. The Move-10 wave queues a thermal-array Spec RFC; this Outreach RFC uses `custom` in the interim.

## Motivation

`FLIR/BosonUSB` is Teledyne FLIR's open utility for streaming Boson thermal cameras over UVC: MIT-licensed, 70 stars, vendor-org maintained, last commit 2026-03-31 active. Teledyne FLIR (Wilsonville OR, Teledyne is US-domiciled) is the canonical robotics-thermal vendor; their flagship Spinnaker SDK for machine-vision cameras is closed binary distributed off-GitHub, but the Boson UVC utility is open and the natural URML engagement surface.

URML's perception story has been visible-spectrum focused to date (RGB, depth, point cloud); adding thermal coverage opens search-and-rescue, agriculture (RFC-0093 Sentera precedent), industrial-inspection, and human-safety lanes that the visible spectrum doesn't reach.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `flir_boson_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to FLIR Boson product attribute |
|---|---|
| `name` | Deployment handle (`flir_boson_320`, `flir_boson_640`) |
| `supports_photo` | `true` — Boson streams UVC frames |
| `supports_video` | `true` |
| `supports_stream` | `true` |
| `max_resolution` | `640x512` (Boson 640) or `320x256` (Boson 320) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: custom` (thermal_array) | Per-pixel temperature array; v0.1 enum has no `thermal_array` |
| `measurement_type: temperature` | Scene-aggregate or spot-temperature reading (scalar; partial fit) |

### What URML v0.1 does not yet express for FLIR Boson

1. **Per-pixel thermal arrays.** URML's `temperature` measurement_type is scalar; thermal cameras emit 2D temperature arrays. Spec RFC queued (parallel to RFC-0039 `point_cloud`).
2. **Radiometric vs non-radiometric mode.** Boson supports both; URML's manifest has no radiometric-mode declaration.
3. **Closed Spinnaker SDK for non-Boson machine-vision lines.** URML's RFC scopes to the Boson UVC surface; Teledyne FLIR's broader machine-vision SDK is closed binary off-GitHub.

### Compatibility notes

- **Vendor org.** [`FLIR/BosonUSB`](https://github.com/FLIR/BosonUSB) (MIT). 26 public vendor repos (mixed activity).
- **Origin.** Teledyne FLIR, Wilsonville OR / Teledyne Technologies US. Passes US-federal default policy.
- **License fit.** MIT on `BosonUSB`; cleanly composes with URML's Apache-2.0 stance.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; thermal-array measurement_type Spec RFC queued in parallel.
- Reference runtime: future `reference/perception-runtime/` package with `FlirBosonAdapter`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Thermal-array measurement_type Spec RFC is a prerequisite for clean manifest declaration.** v0.1 `custom` escape-hatch is honest but not adapter-grade.
- **Scope limited to Boson UVC surface.** Teledyne FLIR's broader machine-vision Spinnaker SDK is closed binary; URML's RFC does not pretend to cover it.

## Alternatives considered

1. **Bundle FLIR + Optris + Seek Thermal (all thermal-IR) into one RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor; Optris (RFC-0128 Tier B) and Seek Thermal (RFC-0129 Tier B) have different surface posture.
2. **Defer FLIR until thermal-array Spec RFC lands.** Rejected. FLIR's feedback informs that Spec RFC.

## Prior art

- [`FLIR/BosonUSB`](https://github.com/FLIR/BosonUSB) — the upstream utility.
- [RFC-0093 (Sentera)](0093-sentera-outreach.md) — agriculture-multispectral-payload precedent.
- [RFC-0128 (Optris)](0128-optris-outreach.md) — parallel thermal RFC, Tier B.
- [RFC-0129 (Seek Thermal)](0129-seek-thermal-outreach.md) — parallel thermal RFC, Tier B (compact-class US).

## Unresolved questions

For the `FLIR/BosonUSB` maintainers:

1. **Thermal-array measurement_type shape.** URML's v0.1 has only scalar `temperature`. A Spec RFC adding `thermal_array` (per-pixel) is queued. What manifest fields would a FLIR deployment expect (resolution, radiometric_mode, dynamic_range)?
2. **Radiometric vs non-radiometric mode.** Boson supports both. Manifest declaration or runtime parameter?
3. **Beyond Boson.** Is `BosonUSB` the right URML engagement surface for the broader FLIR product family, or are there other open-license repos (e.g., for Lepton via Spinnaker subset) URML should target?
4. **Detection / target-tracking declaration.** Some FLIR products ship target-tracking; how should URML's manifest declare this for `query_detection` validation?
5. **Adapter home.** URML repo, FLIR-hosted, or both?
6. **Conformance listing.** Would Teledyne FLIR consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0116 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`FLIR/BosonUSB` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (MIT, 70 stars, 4 open issues, Issues enabled, last commit 2026-03-31).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, thermal-array Spec-RFC prerequisite, Boson scope only).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Teledyne FLIR US; default policy passes.
- [x] CLAUDE.md compliance check passed.
