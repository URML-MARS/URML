---
rfc: 0180
title: VESC Project (open-source brushless ESC) integration, request for comment from vedderb maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
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

# RFC-0180: VESC Project (open-source brushless ESC) integration, request for comment from vedderb maintainers

## Summary

URML does not yet ship a VESC manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the VESC Project — Benjamin Vedder's open-source brushless ESC platform — over [`vedderb/bldc`](https://github.com/vedderb/bldc), and **requests review and feedback from the vedderb maintainer**. **License-clarification ask:** no SPDX license is visible on the repo; an explicit OSI declaration is the gating ask. No spec change.

This RFC completes the Move-13 motor-controller bucket alongside [RFC-0169 (ODrive)](0169-odrive-robotics-outreach.md), [RFC-0170 (Moteus)](0170-mjbots-moteus-outreach.md), and [RFC-0179 (SimpleFOC)](0179-simplefoc-outreach.md).

## Motivation

The VESC Project is Benjamin Vedder's open-source brushless ESC firmware + hardware platform, widely deployed in e-bikes, e-scooters, e-skateboards, and increasingly in robotics applications (mobile-base drive, hub motors, high-power applications where ODrive / Moteus are overspec'd or undersized). Repo at [`vedderb/bldc`](https://github.com/vedderb/bldc) — 3.2k stars, Issues enabled, last commit `2026-05-28` daily activity, **not archived**.

**License-clarification ask is the gating fact**: the repo's license is not visible via the GitHub API (the LICENSE file is GPL-3.0 per a manual inspection but the SPDX detection didn't surface it). An explicit license declaration would clarify URML's adapter-grade reuse boundaries. The cross-citation framing assumes GPL-3.0 until clarified — URML would integrate at the protocol boundary, not by embedding VESC firmware.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `vesc_bldc_cell.yaml` fixture)

`actuators` block:

| URML field | Maps to VESC product attribute |
|---|---|
| `name` | Deployment handle (`vesc_75_300`, `vesc_6_mkv`) |
| `actuator_class: custom` (`brushless_esc_open_hardware`) | Declares VESC class is the host-side controller |
| `actuator_class: custom` (`product_line`) | `vesc_75_300` / `vesc_6_mkv` / `vesc_express` / etc. |
| `actuator_class: custom` (`interface: vesc_can` / `vesc_uart` / `vesc_usb`) | VESC's native protocols |
| `actuator_class: custom` (`power_class_watts`) | Power-class declaration (VESC scales from sub-kilowatt to multi-kilowatt) |
| `actuator_class: custom` (`firmware_version`) | VESC firmware pin |

### What URML v0.1 does not yet express for VESC

1. **Open-hardware ESC actuator class declaration.** Same shared gap as RFC-0169 / RFC-0170 / RFC-0179 — actuator-controller substrate Spec RFC queued.
2. **Power-class declaration.** VESC's distinguishing feature is power-scalability (hundreds of watts to multi-kilowatt); URML's manifest cannot today declare this.
3. **License clarification.** SPDX not visible upstream blocks Apache-2.0 downstream reuse without manual inspection.

### Compatibility notes

- **Vendor / maintainer.** [`vedderb`](https://github.com/vedderb) — Benjamin Vedder (Sweden); single-maintainer pattern.
- **Flagship repo.** [`vedderb/bldc`](https://github.com/vedderb/bldc) — license TBD (clarification ask), 3.2k stars, Issues enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** Sweden (SE). Passes US-federal default policy (NATO+EU).
- **License fit.** Pending clarification (GPL-3.0 per LICENSE file inspection; SPDX detection missing).
- **Maintainer signal.** Single-maintainer pattern; daily activity from the maintainer is the durability signal.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; actuator-controller substrate Spec RFC queued (shared with the sibling Move-13 motor-controller RFCs).
- Reference runtime: cross-citation framing pending license clarification; future `reference/actuator-runtime/VescAdapter` is a candidate **only** if license clarifies as Apache-2.0-compatible AND engagement settles on adapter depth.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.** SPDX not visible upstream; GPL-3.0 (if confirmed) limits Apache-2.0 bundling.
- **Single-maintainer pattern.** Light-touch engagement expected; the surface depends on Benjamin Vedder's availability.
- **Actuator-controller substrate Spec RFC prerequisite.**
- **Power-class declaration novelty.**

## Alternatives considered

1. **Bundle VESC with sibling Move-13 motor-controller RFCs.** Rejected. Per-vendor RFCs let conversation thread per maintainer group.
2. **Skip VESC as duplicate with ODrive.** Rejected. VESC's power-scalability and e-mobility heritage are structurally distinct from ODrive's robotics-first design.
3. **Cross-citation only.** Considered. Tier B framing keeps cross-citation as the recommended posture pending license + Spec RFC.

## Prior art

- [`vedderb/bldc`](https://github.com/vedderb/bldc) — the upstream firmware + hardware.
- [RFC-0169 (ODrive)](0169-odrive-robotics-outreach.md), [RFC-0170 (Moteus)](0170-mjbots-moteus-outreach.md), [RFC-0179 (SimpleFOC)](0179-simplefoc-outreach.md) — sibling motor-controller RFCs.

## Unresolved questions

For the vedderb maintainer:

1. **License clarification.** Can `vedderb/bldc` get an explicit OSI license declaration (GPL-3.0 per LICENSE file; SPDX visibility upstream)?
2. **Actuator-controller substrate manifest fields.** Same shared question as sibling Move-13 motor-controller RFCs.
3. **Power-class declaration.** Should URML's manifest declare VESC's power-class (sub-kilowatt to multi-kilowatt)?
4. **Adapter home.** Cross-citation only (recommended pending license), URML repo (`reference/actuator-runtime/VescAdapter`), or VESC-maintained?
5. **Conformance listing.** Would Benjamin / the VESC project consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

## Implementation note

RFC-0180 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`vedderb/bldc` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license TBD, 3.2k stars, Issues enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license gate, single-maintainer pattern, Spec-RFC prerequisite, power-class novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Sweden SE; default policy passes.
- [x] CLAUDE.md compliance check passed.
