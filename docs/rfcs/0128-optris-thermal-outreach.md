---
rfc: 0128
title: Optris (industrial thermal imaging) integration, request for comment from Optris maintainers
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

# RFC-0128: Optris (industrial thermal imaging) integration, request for comment from Optris maintainers

## Summary

URML does not yet ship an Optris manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Optris' Xi / PI thermal imagers over [`Optris/otcsdk_downloads`](https://github.com/Optris/otcsdk_downloads) and [`Optris/optris_drivers2`](https://github.com/Optris/optris_drivers2), and **requests review and feedback from the Optris maintainers**. No spec change.

This RFC complements [RFC-0116 (Teledyne FLIR)](0116-teledyne-flir-outreach.md). Optris covers industrial pyrometer + compact thermal camera in the same thermal-array Spec-RFC slot.

## Motivation

Optris GmbH (Berlin, Germany) makes industrial thermal imagers and pyrometers. Vendor-direct GitHub presence exists ([`Optris`](https://github.com/Optris)) with two relevant repos: `otcsdk_downloads` (binary SDK distribution, active 2026-05-06 for releases) and `optris_drivers2` (ROS 2 driver, NOASSERTION license, last commit 2025-02-19 stale). Maintainers Denis T. and Waldemar Haag carry vendor-email signatures behind optris.com.

License clarification is the gating fact. `optris_drivers2` lists license as NOASSERTION on GitHub; this blocks Apache-2.0 downstream bundling. A community fork [`evocortex/optris_drivers2`](https://github.com/evocortex/optris_drivers2) is the practical ROS 2 path today and exposes the same license question. URML's RFC engagement is partly a license-clarification ask: explicit upstream license declaration unblocks adapter-grade integration.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `optris_xi_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to Optris product attribute |
|---|---|
| `name` | Deployment handle (`optris_xi400`, `optris_pi_640`) |
| `supports_photo` | `true` |
| `supports_video` | `true` (per-frame thermal raster) |
| `supports_stream` | `true` |
| `max_resolution` | Per-model (Xi 400: 382x288; PI 640i: 640x480) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: temperature` | Per-pixel calibrated temperature (°C / K) — native v0.1 type (clean fit for scalar, gap for thermal-array) |

### What URML v0.1 does not yet express for Optris

1. **Thermal-array measurement_type.** Same gap RFC-0116 (Teledyne FLIR) flagged; one Spec RFC adding `thermal_array` (parallel to `point_cloud` via RFC-0039) covers both.
2. **Calibration declaration.** Industrial thermal cameras ship with NUC (non-uniformity correction) and emissivity-calibration state; URML's manifest cannot today express the calibration provenance / state.
3. **License clarification needed.** ROS 2 driver license is unclear; adapter-grade reuse depends on explicit upstream license.

### Compatibility notes

- **Vendor org.** [`Optris`](https://github.com/Optris) — vendor-direct.
- **Active repo.** [`otcsdk_downloads`](https://github.com/Optris/otcsdk_downloads) — binary SDK distribution; license-undeclared on GitHub; last commit 2026-05-06.
- **ROS 2 driver.** [`optris_drivers2`](https://github.com/Optris/optris_drivers2) — NOASSERTION, last commit 2025-02-19 (stale ~3 mo from cutoff).
- **Community ROS 2 driver.** [`evocortex/optris_drivers2`](https://github.com/evocortex/optris_drivers2) — practical-use fork.
- **Origin.** Berlin, Germany (DE). Passes US-federal default policy (NATO allied).
- **License fit.** Unclear (NOASSERTION on the ROS driver, no license on the SDK download repo). This RFC's engagement is partly a license clarification ask.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; thermal-array Spec RFC queued in parallel (shared with RFC-0116).
- Reference runtime: future `reference/perception-runtime/` `OptrisThermalAdapter` is a candidate after license clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License clarification needed** on both `otcsdk_downloads` and `optris_drivers2`. Adapter-grade reuse blocked until explicit OSI license declared upstream.
- **ROS 2 driver staleness** (~3 mo from cutoff; community fork is the practical path).
- **Thermal-array Spec RFC prerequisite.** Same as RFC-0116.

## Alternatives considered

1. **Engage via the community evocortex fork.** Rejected. URML's outreach is vendor-direct first; evocortex is downstream consumer not upstream maintainer.
2. **Defer Optris until license clears.** Rejected. The RFC engagement is itself the license clarification ask; deferral guarantees no clarification.
3. **Treat Optris as cross-citation only.** Considered. Vendor activity on the SDK download repo argues for adapter-eligible engagement once license clears.

## Prior art

- [`Optris/otcsdk_downloads`](https://github.com/Optris/otcsdk_downloads) — vendor SDK distribution.
- [`Optris/optris_drivers2`](https://github.com/Optris/optris_drivers2) — vendor ROS 2 driver.
- [RFC-0116 (Teledyne FLIR)](0116-teledyne-flir-outreach.md) — sibling thermal-camera RFC sharing the thermal-array Spec-RFC gap.

## Unresolved questions

For the Optris maintainers:

1. **License clarification.** Can `otcsdk_downloads` and `optris_drivers2` get explicit OSI license declarations (Apache-2.0 / BSD-3-Clause / MIT)?
2. **Thermal-array measurement_type shape.** Same question as RFC-0116. Manifest-field expectations for calibrated thermal raster?
3. **Calibration state declaration.** Should URML's manifest declare NUC / emissivity calibration state, and how?
4. **Vendor vs community ROS 2 driver.** Should URML adapter target `Optris/optris_drivers2` (vendor) or `evocortex/optris_drivers2` (community-practical)? Vendor preference matters.
5. **Adapter home.** URML repo (`reference/perception-runtime/`), Optris-maintained `Optris/optris-urml` repo, or cross-citation only?
6. **Conformance listing.** Would Optris consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0128 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`Optris/otcsdk_downloads` has Issues enabled and is the active surface. URML's planned channel: open a single Issue there (or `optris_drivers2` if maintainers prefer ROS-scope), labelled `enhancement` or `question`, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (vendor org confirmed, SDK download repo active, ROS 2 driver stale, license-unclear).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license unclear, ROS 2 driver staleness, thermal-array Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Optris DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
