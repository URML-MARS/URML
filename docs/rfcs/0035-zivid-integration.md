---
rfc: 0035
title: Zivid integration — request for comment from zivid/zivid-python maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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
