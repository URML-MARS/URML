---
rfc: 0171
title: Trinamic TMC-API (stepper-motor driver C-API, Analog Devices subsidiary) integration, request for comment from Trinamic maintainers
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

# RFC-0171: Trinamic TMC-API (stepper-motor driver C-API) integration, request for comment from Trinamic maintainers

## Summary

URML does not yet ship a Trinamic manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Trinamic Motion Control's TMC-series stepper-motor driver C-API over [`Trinamic/TMC-API`](https://github.com/Trinamic/TMC-API) (MIT), and **requests review and feedback from the Trinamic maintainers**. No spec change.

This RFC complements [RFC-0169 (ODrive Robotics)](0169-odrive-robotics-outreach.md) and [RFC-0170 (mjbots Moteus)](0170-mjbots-moteus-outreach.md) on URML's actuator-controller substrate Spec-RFC gap. Where ODrive and Moteus target brushless motors, Trinamic TMC-series targets stepper motors — the actuator class for 3D printers, lab gantries, educational hardware, and precision positioning.

## Motivation

Trinamic Motion Control (Hamburg, Germany; now Analog Devices subsidiary post-acquisition) makes the TMC-series stepper driver chip family (TMC2208, TMC2209, TMC5160, TMC2300, etc.) — the de facto standard for silent, microstepped, stallguard-capable stepper control. Repo at [`Trinamic/TMC-API`](https://github.com/Trinamic/TMC-API) (MIT, 260 stars, Issues enabled, last commit `2026-04-07`, **not archived**).

URML-fit angle: TMC chips sit at the **chip-class layer** — one layer below the camera-class engagement URML had with ams-OSRAM (RFC-0137) and the host-side controller class URML's Move-13 engaged with ODrive / Moteus. The cross-citation framing established in RFC-0137 applies here too: URML's manifest declares which TMC driver class is present + active configuration; the actual chip-level firmware lives outside URML.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `trinamic_tmc_cell.yaml` fixture)

`actuators` block:

| URML field | Maps to Trinamic TMC product attribute |
|---|---|
| `name` | Deployment handle (`trinamic_tmc2209_axis0`, `trinamic_tmc5160_z`) |
| `actuator_class: custom` (`stepper_driver_chip`) | Declares stepper driver chip-class actuator |
| `actuator_class: custom` (`product_line`) | `tmc2208` / `tmc2209` / `tmc5160` / `tmc2300` / etc. |
| `actuator_class: custom` (`step_dir_interface` vs `spi_interface`) | Some TMC chips speak step/dir, others SPI |
| `actuator_class: custom` (`microstep_resolution`) | Microstepping configuration |
| `actuator_class: custom` (`stallguard_enabled`) | StallGuard sensorless-homing flag |

### What URML v0.1 does not yet express for Trinamic

1. **Stepper-driver chip-class declaration.** URML's v0.1 has no `stepper_driver_chip` actuator class. Spec RFC queued — same gap shape as RFC-0169 / RFC-0170 / RFC-0179 / RFC-0180 actuator-controller substrate.
2. **Step/dir vs SPI interface declaration.** TMC chips support both interface modes; URML's manifest cannot today declare which is active.
3. **Sensorless-homing (StallGuard) declaration.** TMC's distinguishing feature is sensorless homing via load-sensing; URML's manifest cannot today declare this capability.

### Compatibility notes

- **Vendor org.** [`Trinamic`](https://github.com/Trinamic) — vendor-direct (Trinamic Motion Control, Analog Devices subsidiary).
- **Flagship repo.** [`Trinamic/TMC-API`](https://github.com/Trinamic/TMC-API) — MIT, 260 stars, Issues enabled, last commit 2026-04-07, **not archived**.
- **Origin.** Hamburg, Germany (DE). Trinamic is a wholly-owned subsidiary of Analog Devices (US). Passes US-federal default policy (NATO+EU + US parent).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Vendor-direct via ADI acquisition; active (~7 weeks from cutoff).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; chip-class actuator-controller Spec RFC queued (shared with the sibling Move-13 motor-controller RFCs).
- Reference runtime: cross-citation framing appropriate at the chip-class layer; future `reference/actuator-runtime/TrinamicTMCAdapter` is a candidate **only** if engagement settles on adapter shape vs cross-citation.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Chip-class vs robotics-stack engagement-level mismatch.** Same shape as RFC-0137 (AMS-OSRAM) — TMC chips are one layer below URML's adapter pattern. Cross-citation may be the honest fit.
- **Chip-class actuator-controller Spec RFC prerequisite.**
- **Multi-product-family scope.** TMC has many chips; URML may engage at the API level rather than per-chip.

## Alternatives considered

1. **Engage Analog Devices at the broader motor-control level.** Considered. ADI broader has multiple motor-control reference designs; per-subsidiary engagement (Trinamic) is the cleaner shape.
2. **Bundle Trinamic with sibling motor-controller RFCs.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Cross-citation only.** Honest fallback given the chip-class layer mismatch.

## Prior art

- [`Trinamic/TMC-API`](https://github.com/Trinamic/TMC-API) — the upstream C-API.
- [RFC-0169 (ODrive)](0169-odrive-robotics-outreach.md), [RFC-0170 (Moteus)](0170-mjbots-moteus-outreach.md) — sibling motor-controller RFCs at the host-controller class.
- [RFC-0137 (AMS-OSRAM)](0137-ams-osram-outreach.md) — Move-10 chip-class engagement pattern (cross-citation framing for ToF chips).

## Unresolved questions

For the Trinamic maintainers:

1. **Engagement-level preference.** Chip-vendor level (here) or integrator-level (recommend specific OEMs / boards)?
2. **Stepper-driver chip-class manifest fields.** URML's v0.1 has no `stepper_driver_chip` actuator class. Spec RFC queued. Manifest field expectations (product_line, interface, microstep_resolution, sensorless-homing class)?
3. **Step/dir vs SPI declaration.** Should URML's manifest declare which interface mode is active?
4. **Adapter home.** Cross-citation only (recommended given chip-class), URML repo (`reference/actuator-runtime/TrinamicTMCAdapter`), or Trinamic-maintained?
5. **Conformance listing.** Would Trinamic / ADI consider a README link to URML's compatible-runtimes registry once a working integration ships?
6. **Anything else.**

## Implementation note

RFC-0171 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml). Cross-citation framing is the recommended posture.

## How to respond

`Trinamic/TMC-API` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with cross-citation framing explicit given the chip-vs-robotics-stack engagement-level mismatch.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 260 stars, Issues enabled, last commit 2026-04-07, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (chip-vs-robotics-stack engagement-level mismatch, Spec-RFC prerequisite, multi-product-family scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Trinamic DE / ADI US; default policy passes.
- [x] CLAUDE.md compliance check passed.
