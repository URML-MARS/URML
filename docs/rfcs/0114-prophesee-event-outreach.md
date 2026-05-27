---
rfc: 0114
title: Prophesee (Metavision event cameras) integration, request for comment from prophesee-ai maintainers
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

# RFC-0114: Prophesee (Metavision event cameras) integration, request for comment from prophesee-ai maintainers

## Summary

URML does not yet ship a Prophesee manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Prophesee's Metavision event-camera line over [`prophesee-ai/openeb`](https://github.com/prophesee-ai/openeb) (open-sourced Metavision SDK, project docs indicate Apache-2.0 with module-level variation — SPDX classifier confirmation pending), and **requests review and feedback from the prophesee-ai maintainers**. No spec change.

**This is URML's first event-camera RFC.** Event cameras emit asynchronous per-pixel brightness-change events rather than synchronous frames; URML's v0.1 perception schema does not have a first-class measurement_type for event streams. The Move-10 wave queues an event-stream Spec RFC; this Outreach RFC uses the `custom` measurement_type escape-hatch in the interim.

## Motivation

`prophesee-ai/openeb` is the strongest event-camera vendor surface on GitHub: vendor-org maintained (Nicolas Martin / nmartin-psee), active commits (last commit 2026-05-15), Issues enabled, ~284 stars. Prophesee (Paris FR) is the canonical event-camera vendor commercially; their Metavision SDK exposes recordings, real-time streaming, and event-based algorithms (optical flow, tracking, detection-from-events).

URML's perception story has been frame-based to date (RGB, depth, point cloud). Event cameras are structurally different: bandwidth scales with scene activity, latency is sub-millisecond, dynamic range is >120dB. The Layer-1 manifest can describe an event camera's existence today via `custom` measurement_type, but a first-class declaration is queued as a Spec RFC.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `prophesee_evk4_cell.yaml` fixture)

`Camera` block (uses Camera block even though event cameras aren't strictly frame-based; treating as a future schema-extension question):

| URML field | Maps to Prophesee product attribute |
|---|---|
| `name` | Deployment handle (`prophesee_evk4_hd`, `prophesee_genx320`) |
| `supports_photo` | `false` — event cameras do not emit frames natively |
| `supports_video` | `false` (or `custom` once event-stream measurement_type lands) |
| `supports_stream` | `true` — asynchronous event stream |
| `max_resolution` | Pixel count (EVK4 HD: 1280x720; GenX320: 320x320) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: custom` (event_stream) | Async per-pixel brightness-change events; v0.1 has no event-stream type |

### What URML v0.1 does not yet express for Prophesee

1. **Event-stream as a first-class measurement_type.** Queued as a Spec RFC; outreach RFC uses `custom` in the interim.
2. **Event-based algorithm outputs.** Metavision SDK ships optical flow, tracking, event-domain detection; URML's `query_detection` primitive can dispatch but manifest needs richer declaration of which event-algorithms are present + their output shape.
3. **Asynchronous timing semantics.** Frame-based cameras have a `frame_rate`; event cameras have a `time_resolution` (microsecond-class). Manifest declaration shape is a vendor-feedback question.

### Compatibility notes

- **Vendor org.** [`prophesee-ai/openeb`](https://github.com/prophesee-ai/openeb).
- **Origin.** Prophesee SA, Paris FR. Passes US-federal default policy (NATO allied).
- **License fit.** Project documentation indicates Apache-2.0 with per-module variation; SPDX classifier did not surface cleanly. URML's first outreach question asks for license confirmation before any adapter code reuse.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; event-stream measurement_type Spec RFC is queued in parallel.
- Reference runtime: future `reference/perception-runtime/` package with `PropheseeAdapter`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License SPDX uncertainty.** Confirmation gate before adapter code reuse.
- **Event-stream measurement_type Spec RFC is a hard prerequisite for clean manifest declaration.** v0.1 `custom` escape-hatch is honest but not adapter-grade.

## Alternatives considered

1. **Defer Prophesee until event-stream Spec RFC lands.** Rejected. Prophesee's feedback informs that Spec RFC.
2. **Use `voltage` measurement_type for event streams.** Rejected (same `custom`-preferred reasoning as RFC-0117 / RFC-0118).
3. **Bundle Prophesee + iniVation (RFC-0126 Tier B) into one event-camera RFC.** Rejected. iniVation development lives on GitLab not GitHub; engagement-surface mismatch warrants separate RFCs.

## Prior art

- [`prophesee-ai/openeb`](https://github.com/prophesee-ai/openeb) — the upstream open Metavision SDK release.
- [RFC-0126 (iniVation)](0126-inivation-outreach.md) — parallel event-camera RFC, Tier B (GitLab-vs-GitHub engagement gap).
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — established the "schema-extension Spec RFC queued in parallel" pattern.

## Unresolved questions

For the `prophesee-ai/openeb` maintainers:

1. **License confirmation.** Project docs indicate Apache-2.0 with module-level variation; could you confirm SPDX at repo level + per-module deltas so URML's adapter code reuse posture is unambiguous?
2. **Event-stream measurement_type shape.** URML's v0.1 enum has no `event_stream`; a Spec RFC adding it (parallel to RFC-0039's `point_cloud`) is queued. What manifest fields would a Prophesee deployment expect (time_resolution, dynamic_range, pixel_count)?
3. **Event-domain algorithm declaration.** Metavision SDK ships optical flow / tracking / detection. How should URML's manifest declare these so `query_detection` validates against actual capability?
4. **Asynchronous timing semantics.** Frame cameras have `frame_rate`; event cameras have time_resolution. Manifest-declaration shape?
5. **Adapter home.** URML repo, Prophesee-hosted, or both?
6. **Conformance listing.** Would Prophesee consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0114 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`prophesee-ai/openeb` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (license classifier ambiguous — Apache-2.0 per project docs; 284 stars, 18 open issues, Issues enabled, last commit 2026-05-15 active).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, license SPDX uncertainty, Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Prophesee FR; default policy passes.
- [x] CLAUDE.md compliance check passed.
