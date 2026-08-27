---
rfc: 0035
title: Zivid integration — request for comment from zivid/zivid-python maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-22
updated: 2026-08-27
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

# RFC-0035: Zivid integration — request for comment from zivid/zivid-python maintainers

## Maintainer engagement received (2026-05-27)

Espen Holmbakken (Principal Engineering Manager, Zivid) replied via email follow-up to [zivid-ros#163](https://github.com/zivid/zivid-ros/issues/163) on 2026-05-27 with substantive technical guidance, framed as "rather than recommend schema shapes for URML directly (those are decisions for the spec authors), it's probably more useful if we point at where the authoritative descriptions of Zivid's behavior live." Maintainer responses to URML's six unresolved questions:

1. **Point-cloud declaration (Q1).** Zivid cameras output 3D color point clouds (XYZ, RGBA, SNR, normals) as the primary product, not 2D images. The data model is documented in Zivid's *General 3D Topics* and *API Reference*. Whether URML models this as a new `measurement_type` or a modifier is a URML design call. **URML action:** the v0.1 gap stands; RFC-0039 already introduced `measurement_type: point_cloud` for the Sensor block on the 3D-lidar side. A future schema extension to carry color + per-point attributes (SNR, normals) for 3D cameras is the URML design question that should be filed as a separate Spec RFC against Zivid's published documentation, not bundled into this Outreach RFC.

2. **Accuracy declaration (Q2).** A single `accuracy_mm` field misrepresents Zivid cameras. Dimension trueness, point precision, and working distance interact and are documented per-model in Zivid's datasheets (linked from the *Camera index*) plus the *General 3D Topics* and *Calculators*. **URML action:** dropped. The unresolved-question Q2 framing in this RFC ("Should URML's `Camera` carry `accuracy_um` / `accuracy_mm`?") is resolved with a clear no. URML's manifest will not compress multi-dimensional accuracy into a scalar.

3. **Acquisition modes (Q3).** HDR, multi-acquisition, projector settings, and exposure handling are documented in Zivid's *Camera Settings* and are substrate-internal at the v0.1 layer. **URML action:** URML's `take_measurement` returns what Zivid acquires; how Zivid acquires it stays the camera's business. Manifest does not surface acquisition modes for v0.1.

4. **Vision-source metadata for `pick_from` (Q5 in the Unresolved-questions list above).** Surface normals, SNR, and related per-point data are part of Zivid's standard output (*API Reference*, *General 3D Topics*). "Pick-quality score" is an **application-layer construct** built on top of point-cloud data, not a Zivid-side concept. **URML action:** dropped as a manifest construct. RFC-0013 (`pick_from`) does not need vision-source-side enrichment; surface normals + SNR are standard Zivid output, not a separate manifest field.

5. **Manufacturer-directory listing (Q6 in the Unresolved-questions list above).** "We'll pass for now. The project is early and we don't currently participate in third-party conformance registries at this stage." **URML action:** accepted. URML does not re-pitch the directory listing on this surface.

The maintainer did not address Q4 (hand-eye calibration declaration). Calibration remains a v0.1 gap; URML notes it as a deployment-side concern rather than a manifest-level declaration unless a future RFC says otherwise.

**Spec follow-up shipped (2026-08-27).** [RFC-0682](0682-3d-camera-declaration.md) closes both open items from this exchange: `Camera.point_cloud` carries color and per-point attributes (xyz, rgba, snr, normals) for 3D cameras, and `Camera.mount` is the hand-eye decision (eye-in-hand or eye-to-hand against a declared frame, with an opaque `calibration_ref`; the topology rides RFC-0290 frame transforms). It honors the answers above: no scalar accuracy (a `datasheet_ref` pointer instead), no acquisition-mode fields, no `pick_from` vision-source metadata.

## Summary

URML ships a brand-named Zivid manifest (`zivid_two_cell.yaml`) and conformance fixture (`industrial/32_zivid_two_cell_positive.yaml`) covering Zivid's industrial 3D color point-cloud cameras (Zivid Two, Zivid 2+ M / 2+ L) via the existing v0.1 `Camera` schema. This RFC documents the URML manifest mapping and **requests review and feedback from the zivid/zivid-python GitHub maintainers**. No spec change.

## Motivation

Zivid is a Norwegian 3D-vision specialist focused on industrial pick-and-place applications with sub-millimeter accuracy. Their products are deployed in random-bin picking, kitting, and quality-inspection lines — exactly the URML industrial profile + RFC-0013 (`pick_from` / `place_at`) usage pattern. The `zivid/zivid-python` repo is **vendor-direct**, active, with recent Python wheel releases tracked on PyPI.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for Zivid cameras

URML's manifest schema declares vision sensors under the `Camera` block (and 3D-vision-specific extensions through `Sensor` for depth):

| URML field | Type | Maps to Zivid product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `zivid_two`, `zivid_2_plus_m130`) |
| `movable` | bool | Zivid cameras are typically fixed-mount over the workspace; `false` for the canonical setup |
| `supports_photo` | bool | `true` — Zivid captures 2D color + 3D depth in one acquisition |
| `supports_video` | bool | `false` for industrial setups (single-shot acquisition is the production mode) |
| `supports_stream` | bool | `false` (industrial single-shot pattern) |
| `max_resolution` | string | `1944p` for Zivid 2+ (1944 × 1200 native; per the datasheet) |

The shipping `zivid_two_cell.yaml` fixture declares a Zivid Two on an industrial cell with `vendor: zivid` (NO origin, requiring the YAML "Norway problem" `country_of_origin: "NO"` quoting); the bundled US-federal default policy ACCEPTS with no flagging.

### What URML v0.1 *does not yet* express for Zivid

1. **3D point-cloud structure.** URML's `Camera.supports_photo` reads as a 2D image; Zivid produces color point clouds (XYZ + RGB per pixel). Same gap as RFC-0032 (Ouster) — URML v0.1's `Camera` is 2D-image-centric.
2. **Sub-millimeter accuracy declaration.** Zivid's claim to fame is sub-millimeter accuracy; URML's manifest has no `accuracy_um` or `accuracy_mm` field.
3. **HDR / structured-light acquisition modes.** Zivid uses structured light + HDR for tough materials (shiny / dark / translucent). URML's manifest has no acquisition-mode field.
4. **Calibration to robot frame.** Hand-eye calibration is critical for Zivid + arm setups. URML has no manifest-level calibration declaration (deployment-side).
5. **Pick-friendly metadata.** Zivid publishes object-pose / surface-normal data optimised for pick planning. URML's [RFC-0013](0013-industrial-layer2-primitives.md) `pick_from` could be enriched with such metadata, but it's not in v0.1.

### Compatibility notes

- **Vendor org.** `zivid/zivid-python` (Python SDK), `zivid/zivid-ros` (ROS 1/2 driver), `zivid/zivid-cpp-samples`.
- **Origin.** Zivid AS, Oslo, Norway; passes the US-federal default policy without flagging.
- **YAML "Norway problem".** Tracked: `NO` parses as boolean `False` in PyYAML 1.1 mode; URML's Zivid manifest uses `country_of_origin: "NO"` quoted to avoid this. Documented for transparency.
- **Pick-and-place alignment.** Zivid is the most aligned parts-vendor in the lighthouse set with the RFC-0013 industrial primitives — random-bin picking is exactly Zivid's marketed use case.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `zivid_two_cell.yaml` + `conformance/fixtures/industrial/32_zivid_two_cell_positive.yaml` already shipping from Track I-C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Five v0.1 gaps overlap with Ouster RFC-0032.** Both vendors surface the point-cloud declaration gap; consolidating via a single future "3D perception" RFC may make sense (but only after Ouster and Zivid review both individual RFCs).

## Alternatives considered

1. **Combine with Photoneo (also 3D structured-light) into a single "3D vision" RFC.** Rejected: Photoneo is in Tier 2 (no public engagement venue today), and per-vendor RFCs let the conversation thread per vendor.
2. **Wait for a unified 3D-perception schema before publishing.** Rejected: Zivid's review is what would inform that schema.

## Prior art

- `zivid/zivid-python`, `zivid/zivid-ros` — upstream SDK + ROS driver.
- Zivid's product datasheets (Zivid Two, Zivid 2+, Zivid One+).
- RFC-0013 (industrial primitives) for the `pick_from` / `place_at` alignment.
- RFC-0032 (Ouster) for the parallel point-cloud expressibility discussion.
- RFC-0023..0034 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending zivid/zivid-python maintainer feedback:

1. **Point-cloud declaration** (same as RFC-0032 Ouster).
2. **Accuracy declaration.** Should URML's `Camera` (or `Sensor`) carry `accuracy_um` / `accuracy_mm`?
3. **Acquisition mode.** Should the manifest capture HDR / structured-light / single-shot modes?
4. **Hand-eye calibration declaration.** Should URML's manifest reference a calibration file or describe the calibration topology?
5. **RFC-0013 enrichment.** Should `pick_from` carry vision-source-specific metadata (surface normals, occlusion confidence)?
6. **Conformance / directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**

## Implementation note

RFC-0035 ships as a single RFC document PR. Draft state.

## Requested feedback (from zivid/zivid-python maintainers)

1. **Correctness of the mapping description.**
2. **The five v0.1 gaps.**
3. **RFC-0013 enrichment for vision-driven `pick_from`.**
4. **Conformance / manufacturer-directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**
5. **Anything else.**

## How to respond

URML public Discussions:

> https://github.com/URML-MARS/URML/discussions

Or Issue on `zivid/zivid-python`. Private via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in vendor-direct presence + RFC-0013 alignment.
- [x] Detailed design names every affected component.
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (overlap with Ouster gap).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md); compliant.
