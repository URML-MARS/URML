---
rfc: 0123
title: Cubert (hyperspectral imaging) integration, request for comment from cubert-hyperspectral maintainers
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

# RFC-0123: Cubert (hyperspectral imaging) integration, request for comment from cubert-hyperspectral maintainers

## Summary

URML does not yet ship a Cubert manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Cubert's Ultris-series snapshot hyperspectral cameras over [`cubert-hyperspectral/cuvis.sdk`](https://github.com/cubert-hyperspectral/cuvis.sdk) (Apache-2.0) and the broader Cuvis ecosystem (cuvis-ai, cuvis-ai-agentic-skills, cuvis.python.examples), and **requests review and feedback from the cubert-hyperspectral maintainers**. No spec change.

**This is URML's first hyperspectral-imaging RFC.** Hyperspectral cameras emit per-pixel spectral signatures (tens to hundreds of bands), enabling classification of materials and conditions that visible-spectrum cameras cannot resolve. The Move-10 wave queues a spectral-data measurement_type Spec RFC.

## Motivation

`cubert-hyperspectral/cuvis.sdk` is the strongest single specialty-perception vendor surface in URML's Move-10 verification: **35 public vendor repos**, Apache-2.0 across the entire org (uniform license posture — rare), daily commits (last commit 2026-05-26 / 27 active today). Cubert GmbH (Ulm, DE) covers snapshot hyperspectral cameras for industrial / agricultural / medical / military / mining applications.

**Cubert is the only Move-10 candidate with an already-public LLM-tool surface.** Their `cuvis-ai-agentic-skills` repo exposes spectral classification as agentic skills that an LLM agent can invoke directly. This is the same surface URML's natural-language-bridge layer + `query_detection` primitive compose with. The URML-Cubert engagement may have the highest semantic overlap of any Tier-A target in Move #10.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `cubert_ultris_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to Cubert product attribute |
|---|---|
| `name` | Deployment handle (`cubert_ultris_x20`, `cubert_ultris_q5`) |
| `supports_photo` | `true` — Ultris snapshots full hyperspectral cubes per frame |
| `supports_video` | `true` (per cube cadence) |
| `supports_stream` | `true` |
| `max_resolution` | Per-model (Ultris X20: 410x410 spatial × 164 bands) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: custom` (spectral_cube) | Per-pixel multi-band spectral signature; v0.1 has no `spectral_cube` type |
| `measurement_type: custom` (spectral_classification) | Cuvis-AI classification output |

### What URML v0.1 does not yet express for Cubert

1. **Spectral / hyperspectral measurement_type.** Per-pixel multi-band cubes are not in v0.1. Spec RFC queued.
2. **Spectral-classification capability declaration.** Cuvis-AI ships material / vegetation / condition classifiers; URML's `query_detection` can dispatch but manifest needs richer declaration of which classification surfaces are present.
3. **Agentic-skills surface.** `cuvis-ai-agentic-skills` exposes spectral primitives at the LLM-tool level; URML's natural-language-bridge composes with this surface directly (the rare case of two NL-tool surfaces meeting). Manifest declaration of "this camera ships an LLM-tool surface" is interesting but not in v0.1.

### Compatibility notes

- **Vendor org.** [`cubert-hyperspectral/cuvis.sdk`](https://github.com/cubert-hyperspectral/cuvis.sdk); 35 public vendor repos uniformly Apache-2.0.
- **Origin.** Cubert GmbH, Ulm DE. Passes US-federal default policy (NATO allied).
- **License fit.** Apache-2.0 uniformly across the org; cleanest license posture in the Move-10 specialty slice.
- **Maintainer signal.** Daily commits; active engineering; explicit AI / agentic-skills posture already public — uncommonly aligned with URML's natural-language story.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; spectral-cube measurement_type Spec RFC queued in parallel.
- Reference runtime: a future `reference/perception-runtime/` package with `CubertAdapter` is a strong candidate given license-fit cleanness; the `cuvis-ai-agentic-skills` bridge is the highest-leverage URML-side integration point.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Spectral-cube measurement_type Spec RFC is a prerequisite.** v0.1 `custom` escape-hatch is honest but not adapter-grade.
- **Agentic-skills bridge is novel design territory.** URML's natural-language-bridge meets Cubert's agentic-skills surface; the integration shape is genuinely new and the manifest declaration question is unresolved.

## Alternatives considered

1. **Defer Cubert until spectral-cube Spec RFC lands.** Rejected. Cubert's feedback informs that Spec RFC; their existing AI-tool posture means engaging now is unusually high-yield.
2. **Bundle Cubert + Specim (Tier C — no GitHub surface) into one hyperspectral RFC.** Rejected. Specim is excluded with cause; no per-vendor combination is appropriate.
3. **Treat `cuvis-ai-agentic-skills` as the primary engagement surface (skip the SDK).** Considered. The SDK is the runtime substrate; engaging with the SDK maintainers covers both surfaces. RFC asks the maintainers about both.

## Prior art

- [`cubert-hyperspectral/cuvis.sdk`](https://github.com/cubert-hyperspectral/cuvis.sdk) — the upstream SDK.
- [`cubert-hyperspectral/cuvis-ai`](https://github.com/cubert-hyperspectral/cuvis-ai) — spectral-classification + agentic-skills.
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — parallel LLM-tool / NL-bridge engagement.
- [RFC-0021 (NL layer)](0021-on-device-llm-bridge.md) — URML's NL layer that composes with Cuvis-AI agentic-skills.

## Unresolved questions

For the `cubert-hyperspectral` maintainers:

1. **Spectral-cube measurement_type shape.** URML's v0.1 enum has no `spectral_cube`; a Spec RFC adding it (parallel to RFC-0039's `point_cloud`) is queued. What manifest fields would a Cubert deployment expect (spatial_resolution, spectral_bands, wavelength_range)?
2. **Spectral-classification capability declaration.** Cuvis-AI ships classifiers. How should URML's manifest declare supported classes so `query_detection` validates against actual capability?
3. **Agentic-skills bridge.** `cuvis-ai-agentic-skills` exposes spectral primitives as LLM-tool calls. URML's natural-language layer (RFC-0021) composes with this. What integration shape would Cubert prefer — bundled bridge, contributed example in `cuvis-ai-agentic-skills`, or cross-citation only?
4. **Adapter home.** URML repo (`reference/perception-runtime/`), Cubert-maintained `cubert-hyperspectral/cubert-urml` repo, or both?
5. **Conformance listing.** Would Cubert consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0123 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`cubert-hyperspectral/cuvis.sdk` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (Apache-2.0 uniform across 35-repo org, daily commits, last commit 2026-05-26 / 27 active today).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (spectral-cube Spec-RFC prerequisite, agentic-skills bridge novel territory).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Cubert DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
