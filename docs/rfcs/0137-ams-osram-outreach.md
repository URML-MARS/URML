---
rfc: 0137
title: AMS-OSRAM (TMF ToF + Mira image-sensor) integration, request for comment from ams-OSRAM maintainers
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

# RFC-0137: AMS-OSRAM (TMF ToF + Mira image-sensor) integration, request for comment from ams-OSRAM maintainers

## Summary

URML does not yet ship an AMS-OSRAM manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for ams-OSRAM's chip-class ToF (TMF8829) and image-sensor (Mira220) catalog over the [`ams-OSRAM`](https://github.com/ams-OSRAM) GitHub organization (49 public repos), and **requests review and feedback from the ams-OSRAM maintainers**. No spec change. **This RFC completes the 12 Tier B RFCs and the full 29 engageable Move-10 wave.**

This RFC complements [RFC-0115 (ifm Effector O3R)](0115-ifm-effector-outreach.md) at the chip-class ToF layer. ifm targets industrial integrated ToF cameras; ams-OSRAM is the upstream ToF-chip vendor whose parts appear inside several OEMs' integrated cameras.

## Motivation

ams-OSRAM AG (Premstätten, Austria) makes the TMF-series time-of-flight chips (TMF8801, TMF8828, TMF8829) and the Mira-series global-shutter image sensors. These parts appear in many integrated cameras and depth modules across multiple OEMs — including some flagship consumer-electronics depth sensors and industrial-vision pipelines.

The vendor org has 49 public repos. Notable for URML:

- `tmf8829_driver_linux` (GPL-3.0, 1 star, 2 open issues, last commit `2026-05-19` active).
- `tmf8829_driver_python` (NOASSERTION, license clarification needed).
- `mira220_v4l2_driver` (GPL-2.0).

**Copyleft license posture is the gating fact.** GPL-2.0 and GPL-3.0 limit Apache-2.0 bundling; URML's adapter-grade reuse is blocked at the driver level. Cross-citation / manifest-component framing is the right shape — URML's manifest declares which TMF / Mira chip is present and what measurement_types it produces, without claiming an Apache-2.0-compatible bundled adapter.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ams_osram_tmf_cell.yaml` fixture)

`Sensor` block (ToF chip):

| URML field | Maps to ams-OSRAM TMF product attribute |
|---|---|
| `name: distance` (Sensor) | TMF8828 / TMF8829 multi-zone ToF chip |
| `measurement_type: distance` | Per-zone distance (mm) — native v0.1 type (clean fit for single-zone scalar) |
| `measurement_type: custom` (depth_per_zone) | Multi-zone (e.g. 3x3 / 4x4) per-zone distance vector |
| `measurement_type: custom` (histogram_per_zone) | Per-zone histogram-of-photons (advanced output) |

`Camera` block (Mira image sensor) — when manifest-declared at the module level:

| URML field | Maps to ams-OSRAM Mira product attribute |
|---|---|
| `name` | Deployment handle (`ams_mira220_module`) |
| `supports_photo` / `supports_video` / `supports_stream` | Per integrator module config |
| `max_resolution` | Mira220: 1600x1200 |

### What URML v0.1 does not yet express for AMS-OSRAM

1. **Multi-zone ToF declaration.** TMF chips emit per-zone distance (3x3 / 4x4 grid); URML's `distance` measurement_type is a single scalar. Spec RFC for multi-zone-ToF queued (could be merged with the amplitude / depth-class Spec RFC shared with RFC-0115 / RFC-0127).
2. **Histogram-of-photons declaration.** TMF8829 emits per-zone histograms (advanced operation mode); URML's manifest cannot today declare this.
3. **Chip-class vs camera-class engagement boundary.** ams-OSRAM ships chips; integrators ship cameras. URML's adapter pattern composes at the camera / module level; the chip-level engagement here is more cross-citation than adapter.

### Compatibility notes

- **Vendor org.** [`ams-OSRAM`](https://github.com/ams-OSRAM) — 49 public repos.
- **Active driver.** [`tmf8829_driver_linux`](https://github.com/ams-OSRAM/tmf8829_driver_linux) — GPL-3.0, last commit 2026-05-19 active.
- **Companion repos.** `tmf8829_driver_python` (NOASSERTION), `mira220_v4l2_driver` (GPL-2.0).
- **Origin.** ams-OSRAM AG, Premstätten, Austria (AT). Passes US-federal default policy (NATO allied; AT EU member).
- **License fit.** Copyleft (GPL-2.0 / GPL-3.0). Limits Apache-2.0 bundling; cross-citation / manifest-component framing is the right shape.
- **Maintainer signal.** Active development; vendor org real (49 repos including utility forks but vendor-direct).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; multi-zone-ToF / amplitude / depth-class Spec RFC queued in parallel (shared with RFC-0115 / RFC-0127).
- Reference runtime: cross-citation recommended over adapter; if engagement settles on adapter, target should be the camera-module integrator level, not the chip-level driver.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Copyleft license posture** (GPL-2.0 / GPL-3.0). Limits Apache-2.0 bundling; cross-citation is the honest fit.
- **Chip-level engagement vs camera-level URML adapter pattern.** URML adapters compose above this layer; engagement here is closer to cross-citation than adapter-shipping.
- **NOASSERTION license on Python driver** blocks downstream reuse without clarification.
- **Multi-zone-ToF Spec RFC prerequisite.** Same gap as RFC-0115 / RFC-0127.

## Alternatives considered

1. **Engage ams-OSRAM at the camera-module-integrator level (find the integrators).** Considered. Out of scope for this RFC — that would be one RFC per integrator. ams-OSRAM as the chip vendor is the cleaner single engagement.
2. **Defer until copyleft posture changes.** Rejected. The copyleft posture is the deliberate vendor choice; cross-citation framing is honest about this.
3. **Bundle ams-OSRAM + pmdtechnologies + ifm into one ToF-chip-class RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.

## Prior art

- [`ams-OSRAM`](https://github.com/ams-OSRAM) — the upstream organization.
- [RFC-0115 (ifm Effector O3R)](0115-ifm-effector-outreach.md) — sibling integrated-ToF camera RFC.
- [RFC-0127 (pmdtechnologies)](0127-pmdtechnologies-tof-outreach.md) — sibling ToF-pixel-class RFC.

## Unresolved questions

For the ams-OSRAM maintainers:

1. **Engagement-level preference.** Chip-vendor level (here) or module-integrator level (recommend specific OEMs)?
2. **License clarification on tmf8829_driver_python.** Can the NOASSERTION repo get an explicit OSI license declaration?
3. **Multi-zone ToF manifest fields.** Same question as RFC-0115 / RFC-0127. Manifest-field expectations for per-zone distance arrays (zone-count, range, accuracy, histogram-mode availability)?
4. **Histogram-of-photons declaration.** Should URML's manifest declare which histogram modes (resolution / bin-count / photon-counting) the integrator has configured?
5. **Adapter home.** Cross-citation only (recommended given GPL posture), URML repo, or ams-OSRAM-maintained?
6. **Conformance listing.** Would ams-OSRAM consider a README link to URML's compatible-runtimes registry once a working integration ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0137 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml). **Completes the 12 Tier B and the full 29 engageable Move-10 RFCs.**

## How to respond

`ams-OSRAM/tmf8829_driver_linux` has Issues enabled and is the active surface. URML's planned channel: open a single Issue there labelled `enhancement` or `question`, pointing to this RFC, with cross-citation framing explicit due to GPL posture.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (49-repo vendor org, tmf8829_driver_linux GPL-3.0 active 2026-05-19, mira220 GPL-2.0).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (copyleft GPL-2/3, NOASSERTION on Python driver, chip-vs-camera engagement-level mismatch, multi-zone-ToF Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: ams-OSRAM AT; default policy passes.
- [x] CLAUDE.md compliance check passed.
