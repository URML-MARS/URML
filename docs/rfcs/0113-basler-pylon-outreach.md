---
rfc: 0113
title: Basler (pylon) integration, request for comment from basler/pypylon maintainers
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

# RFC-0113: Basler (pylon) integration, request for comment from basler/pypylon maintainers

## Summary

URML does not yet ship a Basler manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Basler's USB3 Vision and GigE Vision industrial cameras over [`basler/pypylon`](https://github.com/basler/pypylon) (BSD-3-Clause Python bindings over closed pylon C++ SDK) and the sibling [`basler/pylon-ros-camera`](https://github.com/basler/pylon-ros-camera) ROS 1/2 driver, and **requests review and feedback from the basler/pypylon maintainers**. No spec change.

## Motivation

`basler/pypylon` is the largest machine-vision vendor-direct surface in URML's Move #10 verification: BSD-3-Clause, 696 stars, 210 open issues, vendor-org maintainership (Angel Bakardzhiev and other Basler engineers), last commit 2026-05-27 (active today). Basler AG (Ahrensburg DE) covers industrial machine vision across USB3 Vision and GigE Vision standards. First machine-vision-camera (industrial inspection grade, not RGB-D / stereo) RFC in URML's outreach landscape.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `basler_aca_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to Basler product attribute |
|---|---|
| `name` | Deployment handle (`basler_aca2440_75um`, etc.) |
| `supports_photo` | `true` — primary product is high-resolution frames |
| `supports_video` | `true` |
| `supports_stream` | Configurable per deployment (trigger vs continuous) |
| `max_resolution` | Per-model |
| `transport` (proposed) | `usb3_vision` or `gige_vision` — GenICam-family standards |

### What URML v0.1 does not yet express for Basler

1. **GenICam-protocol capability declaration.** USB3 Vision and GigE Vision are standardized protocols; manifest could declare GenICam compliance as transport-class capability. Same question raised by RFC-0112 (Roboception).
2. **High-bandwidth / trigger-controlled acquisition modes.** Industrial-inspection cameras run hardware-triggered acquisition; URML's manifest has no acquisition-mode declaration today.
3. **License clarification on `pylon-ros-camera`** — repo classifier shows NOASSERTION; the `pypylon` repo is cleanly BSD-3-Clause.

### Compatibility notes

- **Vendor org.** [`basler/pypylon`](https://github.com/basler/pypylon) (BSD-3-Clause), [`basler/pylon-ros-camera`](https://github.com/basler/pylon-ros-camera) (NOASSERTION — verify), closed pylon C++ SDK at the core.
- **Origin.** Basler AG, Ahrensburg DE. Passes US-federal default policy (NATO allied).
- **License fit.** BSD-3-Clause on `pypylon`; ROS driver license needs clarification.

### Spec / validator / reference-runtime / conformance changes

- None in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Closed pylon C++ SDK at core** — URML's manifest reasons about the open Python binding only.
- **License classifier ambiguity on `pylon-ros-camera`** — clarification gate before any adapter code reuse.

## Alternatives considered

1. **Bundle Basler + IDS + (Tier-C-excluded) machine-vision vendors into one RFC.** Rejected. Basler is the only Tier A machine-vision vendor surviving verification; per-vendor RFC respects that.
2. **Skip industrial-inspection cameras because URML's primary focus is mobile / collaborative robotics.** Rejected. Manifest-level coverage of machine-vision cameras matters for hand-eye + bin-picking deployments.

## Prior art

- [`basler/pypylon`](https://github.com/basler/pypylon) — the upstream binding.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — engaged industrial 3D-vision precedent.
- [RFC-0112 (Roboception)](0112-roboception-outreach.md) — parallel industrial-vision RFC.

## Unresolved questions

For the `basler/pypylon` maintainers:

1. **License clarification on `pylon-ros-camera`.** Classifier shows NOASSERTION; could you confirm SPDX in-repo?
2. **GenICam-protocol declaration.** Should URML's manifest declare USB3 Vision / GigE Vision compliance as transport-class capability?
3. **Hardware-triggered acquisition declaration.** Industrial-inspection deployments lean on hardware trigger. Manifest declaration or runtime parameter?
4. **Native detection / inspection-AI declaration.** Some Basler products ship inspection-AI add-ons (e.g. pylon Vision Connector). How should the manifest declare those when present?
5. **Adapter home.** URML repo, Basler-hosted, or both?
6. **Conformance listing.** Would Basler consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0113 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`basler/pypylon` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (BSD-3-Clause, 696 stars, 210 open issues, Issues enabled, last commit 2026-05-27).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (closed core, license-classifier ambiguity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Basler DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
