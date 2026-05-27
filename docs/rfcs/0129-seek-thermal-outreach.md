---
rfc: 0129
title: Seek Thermal (compact USB thermal imagers) integration, request for comment from Seek Thermal maintainers
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

# RFC-0129: Seek Thermal (compact USB thermal imagers) integration, request for comment from Seek Thermal maintainers

## Summary

URML does not yet ship a Seek Thermal manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Seek Thermal's compact USB thermal imagers over [`seekthermal/seekcamera-python`](https://github.com/seekthermal/seekcamera-python) (Apache-2.0), and **requests review and feedback from the Seek Thermal maintainers**. No spec change.

This RFC complements [RFC-0116 (Teledyne FLIR)](0116-teledyne-flir-outreach.md) and [RFC-0128 (Optris)](0128-optris-thermal-outreach.md) at the compact-class end of the thermal-imager slice. Where FLIR / Optris target industrial mounts, Seek Thermal's compact / mobile-USB form-factor opens classroom / portable / micro-class robot deployments.

## Motivation

Seek Thermal (Santa Barbara, CA) makes some of the most compact USB thermal imagers on the market (Compact, CompactPRO, MicroCore series). Their vendor-direct GitHub presence is small but real: a single repo, [`seekcamera-python`](https://github.com/seekthermal/seekcamera-python), Apache-2.0, 64 stars, 13 open issues, last commit `2024-03-08` (>14 months stale from 2026-05-27 cutoff).

US origin (passes US-federal default policy cleanly without any caveat), Apache-2.0 (cleanly composes with URML's Apache-2.0 stance), single-repo vendor presence (fragility signal — one maintainer, one library, one engagement surface). The compact-class thermal complement to industrial-class FLIR is the URML-fit case.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `seek_compact_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to Seek Thermal product attribute |
|---|---|
| `name` | Deployment handle (`seek_compact_pro`, `seek_microcore_206`) |
| `supports_photo` | `true` |
| `supports_video` | `true` (per-frame thermal raster) |
| `supports_stream` | `true` |
| `max_resolution` | Per-model (Compact: 206x156; CompactPRO: 320x240) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: temperature` | Per-pixel calibrated temperature (°C / K) — native v0.1 type (clean fit for scalar, gap for thermal-array) |

### What URML v0.1 does not yet express for Seek Thermal

1. **Thermal-array measurement_type.** Same gap shared with RFC-0116 (Teledyne FLIR) and RFC-0128 (Optris); one Spec RFC adding `thermal_array` covers all three.
2. **USB-class compact-camera declaration.** Seek's compact form-factor connects via USB-C / Lightning rather than industrial mount; URML's manifest cannot today express physical-connection class (relevant for portable / micro-class robot fit).
3. **Single-library wrapper over closed Seek SDK.** `seekcamera-python` is Apache-2.0 but wraps the closed Seek SDK binary; same closed-core / open-wrapper pattern as RFC-0073 Marty and RFC-0127 pmdtechnologies.

### Compatibility notes

- **Vendor org.** [`seekthermal`](https://github.com/seekthermal) — single public repo.
- **Repo state.** Apache-2.0, 64 stars, 13 open issues, last commit 2024-03-08 (`>14 months` stale).
- **Origin.** Santa Barbara, CA, USA. Passes US-federal default policy cleanly (no allied caveat).
- **License fit.** Apache-2.0 wrapper; underlying Seek SDK closed binary.
- **Maintainer signal.** Vendor org real but quiet on GitHub; one-repo presence is a fragility signal.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; thermal-array Spec RFC queued in parallel (shared with RFC-0116 / RFC-0128).
- Reference runtime: future `reference/perception-runtime/` `SeekThermalAdapter` is a candidate; the small surface keeps adapter scope tight.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Repository staleness** (`>14 months`). Engagement may yield slow or no response.
- **Closed Seek SDK** — adapter reasons about the open Python wrapper, not the closed core. Same shape as RFC-0073 / RFC-0127.
- **Thermal-array Spec RFC prerequisite.** Same gap as RFC-0116 / RFC-0128.

## Alternatives considered

1. **Defer Seek Thermal until repo reactivates.** Rejected. RFC engagement may itself be the reactivating nudge.
2. **Engage via downstream OEM integration.** Rejected. URML's outreach is vendor-direct first.
3. **Bundle Seek + Optris + FLIR into one thermal RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; thermal-array Spec RFC is the shared piece.

## Prior art

- [`seekthermal/seekcamera-python`](https://github.com/seekthermal/seekcamera-python) — the upstream Python wrapper.
- [RFC-0116 (Teledyne FLIR)](0116-teledyne-flir-outreach.md) + [RFC-0128 (Optris)](0128-optris-thermal-outreach.md) — sibling thermal-camera RFCs sharing the thermal-array Spec-RFC gap.

## Unresolved questions

For the Seek Thermal maintainers:

1. **Repository status.** Is `seekcamera-python` actively maintained, dormant-but-supported, or fully retired? Where does vendor engagement live in 2026?
2. **Thermal-array measurement_type shape.** Same question as RFC-0116 / RFC-0128. Manifest-field expectations for calibrated thermal raster?
3. **Compact / USB-class declaration.** Should URML's manifest declare physical-connection class (USB / USB-C / Lightning) for portable form-factor cameras?
4. **Adapter home.** URML repo (`reference/perception-runtime/`), Seek-maintained `seekthermal/seek-urml` repo, or both?
5. **Conformance listing.** Would Seek Thermal consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0129 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`seekthermal/seekcamera-python` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of staleness.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (Apache-2.0, 64 stars, single repo, last commit 2024-03-08 stale).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, closed Seek SDK, single-repo fragility, thermal-array Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Seek Thermal US; default policy passes.
- [x] CLAUDE.md compliance check passed.
