---
rfc: 0135
title: Cerulean Sonar (underwater sonar / echo sounders) integration, request for comment from CeruleanSonar maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-27
updated: 2026-05-28
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

# RFC-0135: Cerulean Sonar (underwater sonar / echo sounders) integration, request for comment from CeruleanSonar maintainers

## Summary

URML does not yet ship a Cerulean Sonar manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Cerulean's S500 sounder, Omniscan side-scan sonar, and ping-protocol family over the [`CeruleanSonar`](https://github.com/CeruleanSonar) GitHub organization (12 public vendor repos), and **requests review and feedback from the CeruleanSonar maintainers**. No spec change.

> **Maintainer-correction note (2026-05-28):** @NickNothom (CONTRIBUTOR on `CeruleanSonar/SonarView`) flagged on [#38](https://github.com/CeruleanSonar/SonarView/issues/38) that the Omniscan is **not** a multibeam (the original RFC draft said it was). Corrected throughout. The SonarView license is published at [ceruleansonar.com/software-license-sonarview/](https://ceruleansonar.com/software-license-sonarview/) (answers Q1). The ping-protocol device-communication docs are at [docs.ceruleansonar.com/c/cerulean-ping-protocol](https://docs.ceruleansonar.com/c/cerulean-ping-protocol) (answers Q3). Q4 (acoustic safety-envelope) and Q5 (adapter home) were flagged incomprehensible and are not pursued further on this thread.

**This is URML's first sonar / underwater-perception RFC.** It complements URML's existing marine-runtime (BlueROV ArduSub via the existing marine demos). Underwater perception sits below the lidar / camera / radar perception layers and is the dominant sensing modality for AUV / ROV / surface-vessel deployments where light does not penetrate.

## Motivation

Cerulean Sonar (US) makes the S500 single-beam sounder and the Omniscan side-scan sonar — both built on the Blue Robotics ping-protocol, which is the de facto open-source underwater-sonar protocol in the BlueROV ecosystem. Cerulean's vendor org has 12 public repos: `SonarView` (flagship visualizer, no license declared), `ping-python` (MIT), `s500_ros2` (MIT, stale 2023-06-28). Last commit on `SonarView` is 2026-05-18 (active).

URML's existing marine-runtime (BlueROV ArduSub) covers the surface-vehicle / ROV mobility primitives but does not today declare underwater-acoustic perception. Cerulean's family complements the existing marine-runtime by adding the sonar-perception layer on the same Blue Robotics open-protocol substrate.

**License clarification is the gating fact** on the SonarView flagship. The `ping-python` and `s500_ros2` repos are MIT (clean fit), but SonarView has no license declared — adapter-grade reuse against SonarView is blocked until upstream license clarifies. URML-fit is via ping-protocol rather than SonarView directly.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `cerulean_s500_cell.yaml` fixture)

`Sensor` block:

| URML field | Maps to Cerulean Sonar product attribute |
|---|---|
| `name: sonar` (Sensor) | Cerulean S500 single-beam echo sounder / Omniscan side-scan sonar |
| `measurement_type: distance` | Distance-to-bottom (m) — native v0.1 type (clean fit for scalar) |
| `measurement_type: custom` (sonar_returns) | Per-bin sonar return intensity for sounder profile / side-scan swath |
| `measurement_type: custom` (water_column_profile) | Multi-bin water-column return for in-water object detection |

### What URML v0.1 does not yet express for Cerulean Sonar

1. **Sonar return-array measurement_type.** v0.1 has `distance` for scalar (clean fit), but no per-bin / per-swath return-array type. Spec RFC queued in parallel; this is the first sonar RFC and the natural place to gather requirements.
2. **Ping-protocol declaration.** Blue Robotics ping-protocol is the de facto open underwater-sonar protocol; URML's manifest cannot today declare which protocol version + extension set is active.
3. **Underwater-acoustic safety-envelope cross-link.** Underwater sonar usage in marine-mammal habitat is regulated (MMPA in US waters); URML's manifest could declare emission-class / frequency-band for envelope-gating, but not in v0.1.

### Compatibility notes

- **Vendor org.** [`CeruleanSonar`](https://github.com/CeruleanSonar) — 12 public repos.
- **Active flagship.** [`SonarView`](https://github.com/CeruleanSonar/SonarView) — **no license declared** (flag), 7 stars, 4 open issues, Issues enabled, last commit 2026-05-18 active.
- **Open-protocol companion.** `ping-python` (MIT), `s500_ros2` (MIT, stale 2023-06-28).
- **Origin.** Cerulean Sonar (US). Passes US-federal default policy cleanly (no allied caveat).
- **License fit.** MIT on the open-protocol surface (clean fit); SonarView license-undeclared (license clarification needed for adapter-grade reuse).
- **Maintainer signal.** Active flagship; modest stars; vendor email behind ceruleansonar.com.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; sonar-return-array Spec RFC queued in parallel (first sonar RFC; this is the natural place to gather requirements).
- Reference runtime: future `reference/sensor-runtime/CeruleanSonarAdapter` is a candidate via ping-protocol; complements URML's existing marine-runtime (BlueROV ArduSub).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License clarification needed on SonarView** before any Apache-2.0 downstream reuse.
- **First-sonar-RFC novelty.** No existing URML fixture or schema field for sonar return-arrays; Spec RFC needs Cerulean's input.
- **Marine-mammal regulatory cross-link** is future work.

## Alternatives considered

1. **Engage Blue Robotics directly (ping-protocol upstream) instead of Cerulean.** Considered. Blue Robotics may belong in a separate Move-10 follow-on or a marine-specific outreach wave; Cerulean is the higher-leverage single vendor for sonar specifically.
2. **Bundle Cerulean + Blue Robotics ping into one underwater-perception RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Defer Cerulean until license clarifies on SonarView.** Rejected. RFC engagement is itself the license-clarification ask.

## Prior art

- [`CeruleanSonar`](https://github.com/CeruleanSonar) — the upstream organization.
- [`bluerobotics/ping-python`](https://github.com/bluerobotics/ping-python) — the ping-protocol upstream (Blue Robotics maintained).
- URML's existing marine-runtime (BlueROV ArduSub demos) — Cerulean Sonar complements this at the sonar-perception layer.

## Unresolved questions

For the CeruleanSonar maintainers:

1. **License clarification on SonarView.** ~~Can SonarView get an explicit OSI license declaration (MIT / Apache-2.0 / BSD-3-Clause)?~~ **Answered 2026-05-28** by @NickNothom: SonarView license terms are published at [ceruleansonar.com/software-license-sonarview/](https://ceruleansonar.com/software-license-sonarview/). Not OSI-declared in-repo, but explicit terms exist; URML respects the vendor's chosen distribution model.
2. **Sonar return-array measurement_type shape.** URML's v0.1 has no per-bin / per-swath return-array type. Spec RFC queued. Manifest-field expectations (bin count, range resolution, frequency, beam-pattern)?
3. **Ping-protocol declaration.** ~~Should URML's manifest declare ping-protocol version + extension set, and how should that interoperate with Blue Robotics-side protocol evolution?~~ **Pointer received 2026-05-28** by @NickNothom: device communication API docs at [docs.ceruleansonar.com/c/cerulean-ping-protocol](https://docs.ceruleansonar.com/c/cerulean-ping-protocol). URML manifest field shape is downstream work, but the protocol surface is now documented.
4. **Underwater-acoustic safety-envelope cross-link.** Should URML's manifest declare emission-class / frequency-band for marine-mammal regulatory envelope-gating, or is that always envelope-side? *(Flagged incomprehensible by maintainer 2026-05-28; not pursued further on this thread.)*
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Cerulean-maintained, or cross-citation only? *(Flagged incomprehensible by maintainer 2026-05-28; URML proceeds with the cross-citation default on the MIT-licensed `ping-python` / `s500_ros2` surface.)*
6. **Conformance listing.** Would Cerulean consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0135 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`CeruleanSonar/SonarView` has Issues enabled and is the active flagship. URML's planned channel: open a single Issue there labelled `enhancement` or `question`, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (12-repo org, SonarView active 2026-05-18 but license-undeclared; ping-python + s500_ros2 MIT).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, first-sonar-RFC novelty, marine-mammal regulatory cross-link as future work).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Cerulean Sonar US; default policy passes.
- [x] CLAUDE.md compliance check passed.
