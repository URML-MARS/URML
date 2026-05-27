---
rfc: 0122
title: GelSight (vision-based tactile sensors) integration, request for comment from gelsightinc maintainers
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

# RFC-0122: GelSight (vision-based tactile sensors) integration, request for comment from gelsightinc maintainers

## Summary

URML does not yet ship a GelSight manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for GelSight's vision-based tactile-sensor line (Mini, R1.5, Wedge, DIGIT-successor) over [`gelsightinc/gsrobotics`](https://github.com/gelsightinc/gsrobotics) (GPL-3.0), and **requests review and feedback from the gelsightinc maintainers**. No spec change.

**This is URML's first tactile-sensing RFC.** Tactile sensing is structurally distinct from frame / depth / event cameras: spatial contact-force arrays + slip-detection metadata, not optical brightness. The Move-10 wave queues a tactile / pressure-array measurement_type Spec RFC; this Outreach RFC uses the `custom` escape-hatch in the interim.

## Motivation

`gelsightinc/gsrobotics` is the only commercially-viable tactile-sensor vendor with an active GitHub presence in URML's Move-10 verification: GPL-3.0, 187 stars, 20 open issues, last commit 2025-06-25 (marginally stale 11 months but still the canonical surface). GelSight, Inc. (Waltham MA, MIT spin-off) covers vision-based tactile sensors and inherited the DIGIT product line after Meta archived `facebookresearch/digit-*` in 2026.

GPL-3.0 copyleft limits URML's Apache-2.0 inbound-equals-outbound posture for bundled adapter code — so the URML-GelSight pattern leans toward **cross-citation / manifest-component framing** rather than a bundled `GelSightAdapter`. The manifest declaration is what URML can ship cleanly; the runtime call into `gsrobotics` happens through user-side application code that the user licenses appropriately.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `gelsight_mini_cell.yaml` fixture)

`Sensor` block:

| URML field | Maps to GelSight product attribute |
|---|---|
| `name: tactile` (Sensor) | GelSight Mini / R1.5 / Wedge tactile sensor |
| `measurement_type: custom` (tactile_array) | Per-pixel contact deformation map; v0.1 enum has no `tactile_array` |
| `measurement_type: custom` (slip_event) | Slip detection state (transient event-like signal) |
| `units` | `mm` (deformation), boolean (slip), per channel |

### What URML v0.1 does not yet express for GelSight

1. **Tactile / pressure-array first-class measurement_type.** Spatially-organized contact-force arrays are not in v0.1. Spec RFC queued.
2. **Slip-detection event-class output.** Slip is closer to an event than a continuous measurement; URML's manifest has no slip-event declaration.
3. **Per-sensor calibration declaration.** GelSight surfaces depend on per-unit calibration (light pattern, gel deformation profile); manifest could declare calibration-state.

### Compatibility notes

- **Vendor org.** [`gelsightinc/gsrobotics`](https://github.com/gelsightinc/gsrobotics) (GPL-3.0); siblings `gssim` (Apache-2.0 simulator), `gsmatlab` (MIT MATLAB samples).
- **Origin.** GelSight Inc., Waltham MA, US. Passes US-federal default policy.
- **License fit.** GPL-3.0 copyleft on the flagship; URML adapter cross-citation framing rather than bundled. User-side application code carries the GPL obligation; URML's manifest declaration is license-neutral.

### Spec / validator / reference-runtime / conformance changes

- None in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 copyleft on flagship.** Limits URML's Apache-2.0 inbound-equals-outbound bundling; cross-citation framing is honest but reduces adapter integration depth.
- **Tactile measurement_type Spec RFC is a prerequisite for clean manifest declaration.** v0.1 `custom` is honest but not adapter-grade.

## Alternatives considered

1. **Bundle a GelSightAdapter directly in `reference/perception-runtime/`.** Rejected. GPL-3.0 + URML Apache-2.0 in the same compilation unit triggers copyleft propagation; cross-citation keeps URML's open-core stance clean.
2. **Defer GelSight until tactile measurement_type Spec RFC lands.** Rejected. GelSight feedback informs that Spec RFC; engaging now provides input.
3. **Bundle GelSight + Contactile (RFC-0136 Tier B, also GPL-3.0) into one tactile RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.

## Prior art

- [`gelsightinc/gsrobotics`](https://github.com/gelsightinc/gsrobotics) — the upstream library.
- [RFC-0136 (Contactile)](0136-contactile-outreach.md) — parallel tactile RFC, Tier B (AU, GPL-3.0).
- [RFC-0013 (industrial primitives)](0013-industrial-layer2-primitives.md) — `grasp` / `release` semantics that tactile feedback informs.

## Unresolved questions

For the `gelsightinc/gsrobotics` maintainers:

1. **Tactile / pressure-array measurement_type shape.** URML's v0.1 enum has no `tactile_array`; would a Spec RFC adding it (parallel to RFC-0039's `point_cloud`) be useful from GelSight's perspective? What manifest fields (sensor area, taxel resolution, deformation_range) would a GelSight deployment expect?
2. **Slip-detection event declaration.** Slip is event-like rather than continuous. Manifest declaration or runtime-event semantics?
3. **Per-sensor calibration declaration.** GelSight depends on per-unit calibration. Should URML's manifest declare calibration-state, or is that always out-of-band?
4. **GPL-3.0 cross-citation framing.** URML's Apache-2.0 stance means bundled adapter code with GPL-3.0 propagates copyleft; URML defaults to cross-citation. Is that acceptable to GelSight, or would GelSight prefer dual-licensing for the URML adapter path?
5. **DIGIT-successor product status.** Meta archived `facebookresearch/digit-*` in 2026; GelSight is the commercial successor. How should URML reference the DIGIT lineage in the manifest / RFC?
6. **Conformance listing.** Would GelSight consider a README link to URML's compatible-runtimes registry once a working adapter / cross-citation example ships?
7. **Anything else.**

## Implementation note

RFC-0122 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`gelsightinc/gsrobotics` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (GPL-3.0, 187 stars, 20 open issues, Issues enabled, last commit 2025-06-25).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, GPL copyleft, tactile-type Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: GelSight US; default policy passes.
- [x] CLAUDE.md compliance check passed.
