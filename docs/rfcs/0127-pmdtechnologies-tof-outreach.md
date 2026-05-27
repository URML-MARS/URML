---
rfc: 0127
title: pmdtechnologies (Royale ToF) integration, request for comment from pmdtechnologies maintainers
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

# RFC-0127: pmdtechnologies (Royale ToF) integration, request for comment from pmdtechnologies maintainers

## Summary

URML does not yet ship a pmdtechnologies manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for pmdtechnologies' Royale ToF cameras over [`pmdtechnologies/pmd-royale-ros`](https://github.com/pmdtechnologies/pmd-royale-ros) (BSD-3-Clause), and **requests review and feedback from the pmdtechnologies maintainers**. No spec change.

This RFC complements [RFC-0115 (ifm Effector O3R)](0115-ifm-effector-outreach.md), URML's other ToF-camera RFC. Where ifm targets industrial multi-head perception, pmdtechnologies' Royale is the upstream ToF-pixel technology under several OEM front-ends.

## Motivation

pmdtechnologies AG (Siegen, Germany) makes the time-of-flight pixel technology that powered several flagship ToF cameras (Microsoft Azure Kinect's underlying pixel, Sony DepthSense IMX556, multiple Royale-based modules). Their `pmd-royale-ros` repository is the vendor-direct ROS 1 bridge over the closed Royale SDK; URML benefits from documenting the manifest mapping even when adapter-grade reuse depends on Royale SDK licensing.

**Repository staleness is the gating fact.** Last commit `2023-12-13` (`>2 years` from cutoff 2026-05-27); the maintainer (Martin Plagens, vendor email behind pmdtec.com) has gone dormant on this repo. ROS 1 only; no ROS 2 driver has surfaced on the vendor org. This RFC engages with explicit acknowledgement of staleness; the RFC may itself be the nudge that reactivates the repository, or it may yield a vendor-redirect to a different channel.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `pmd_royale_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to pmdtechnologies product attribute |
|---|---|
| `name` | Deployment handle (`pmd_pico_flexx`, `pmd_camboard_pico_monstar`) |
| `supports_photo` | `true` |
| `supports_video` | `true` (per-frame depth + amplitude) |
| `supports_stream` | `true` |
| `max_resolution` | Per-module (PicoFlexx 224x171; CamBoard pico monstar 352x287) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: depth` | Per-pixel depth (mm range) — native v0.1 type (clean fit) |
| `measurement_type: custom` (amplitude) | Per-pixel return amplitude (signal-quality indicator) |
| `measurement_type: point_cloud` | Optional rasterized cloud per RFC-0039 — native v0.1 type |

### What URML v0.1 does not yet express for pmdtechnologies

1. **Amplitude / SNR per-pixel scalar.** ToF cameras emit per-pixel amplitude alongside depth (a confidence proxy); v0.1 has no `amplitude` measurement_type. Same gap RFC-0115 ifm flagged; one Spec RFC could cover both.
2. **Modulation-frequency declaration.** Royale supports multi-frequency operation to extend unambiguous range; URML's manifest cannot today declare which frequencies are available.
3. **Closed-SDK declaration.** `pmd-royale-ros` is BSD-3-Clause but wraps the closed Royale SDK binary; URML's adapter would need a runtime declaration of "depends-on-closed-SDK". Same closed-core / open-wrapper pattern as RFC-0073 Marty.

### Compatibility notes

- **Vendor org.** [`pmdtechnologies`](https://github.com/pmdtechnologies) — vendor-direct, Siegen DE.
- **Repo state.** [`pmd-royale-ros`](https://github.com/pmdtechnologies/pmd-royale-ros) — BSD-3-Clause, 9 stars, Issues enabled, last commit 2023-12-13 (>2 years stale).
- **Origin.** Germany (DE). Passes US-federal default policy (NATO allied).
- **License fit.** Open wrapper (BSD-3-Clause); underlying Royale SDK closed. Adapter-grade reuse depends on Royale SDK licensing the operator accepts.
- **Maintainer signal.** Dormant on GitHub for `>2 years`; vendor org may have moved engagement elsewhere.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; amplitude / depth-class Spec RFC queued in parallel (shared with RFC-0115).
- Reference runtime: future `reference/perception-runtime/` `PmdRoyaleAdapter` is a candidate **only** after vendor confirms either a reactivated repo or a new engagement surface.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Repo staleness (>2 years).** Engagement may yield no response or a vendor-redirect.
- **Closed Royale SDK.** Open-wrapper BSD-3-Clause is honest about its dependency on a closed binary; URML's adapter pattern reasons about the wrapper, not the closed core.
- **ROS 1 only.** No ROS 2 driver surfaced on the vendor org — adopters today bridge or rebuild.

## Alternatives considered

1. **Defer pmdtechnologies until repo reactivates.** Rejected. RFC engagement may itself be the reactivating nudge; deferring guarantees zero signal.
2. **Engage via OEM downstream (e.g., a Royale-based Pico-line vendor).** Rejected. URML's outreach is vendor-direct first; OEM-only engagement is fallback.
3. **Cross-citation only (no manifest mapping).** Rejected. The manifest mapping is the artifact maintainers can evaluate; cross-citation alone provides no decision surface.

## Prior art

- [`pmdtechnologies/pmd-royale-ros`](https://github.com/pmdtechnologies/pmd-royale-ros) — the upstream ROS 1 driver.
- [RFC-0115 (ifm Effector O3R)](0115-ifm-effector-outreach.md) — sibling ToF-camera RFC; complementary industrial-class.
- [RFC-0039 (point_cloud)](0039-point-cloud-measurement-type.md) — native point_cloud type for rasterized output.

## Unresolved questions

For the pmdtechnologies maintainers:

1. **Repository status.** Is `pmd-royale-ros` actively maintained, dormant-but-supported, or fully retired? Where does vendor-direct engagement live in 2026?
2. **ROS 2 driver.** Is a ROS 2 driver planned, or has the vendor consolidated on a non-ROS surface?
3. **Amplitude / depth-class manifest fields.** ToF cameras emit per-pixel amplitude alongside depth; URML's v0.1 has no `amplitude` type. A Spec RFC adding it (parallel to RFC-0115) is queued. Manifest-field expectations?
4. **Closed-SDK declaration.** Should URML's manifest declare "depends-on-closed-Royale-SDK" and at what granularity (Royale version, fingerprint, license-class)?
5. **Adapter home.** URML repo (`reference/perception-runtime/`), pmdtechnologies-maintained `pmdtechnologies/pmd-royale-urml` repo, or cross-citation only?
6. **Conformance listing.** Would pmdtechnologies consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0127 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`pmdtechnologies/pmd-royale-ros` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of staleness and an offer to take the conversation off-issue if a different channel is preferred.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (BSD-3-Clause wrapper, 9 stars, last commit 2023-12-13 stale).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, closed Royale SDK, ROS 1 only).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: pmdtechnologies DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
