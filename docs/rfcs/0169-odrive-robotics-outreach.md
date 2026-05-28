---
rfc: 0169
title: ODrive Robotics (open-hardware brushless motor controller) integration, request for comment from odriverobotics maintainers
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

# RFC-0169: ODrive Robotics (open-hardware brushless motor controller) integration, request for comment from odriverobotics maintainers

## Summary

URML does not yet ship an ODrive manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for ODrive Robotics' brushless motor controllers (ODrive S1 / Pro / 3.6) over [`odriverobotics/ODrive`](https://github.com/odriverobotics/ODrive) (MIT), and **requests review and feedback from the odriverobotics maintainers**. No spec change.

**This is URML's first Move-13 RFC** (Theme C: open-source actuators + embedded / maker substrate). The Layer-0 substrate URML's full-stack substrate-neutral claim depends on starts here.

## Motivation

ODrive Robotics is the canonical US-origin open-hardware brushless motor controller for robotics. Firmware + hardware MIT-licensed. Used widely in quadruped research (Stanford Pupper lineage), mobile-base direct-drive wheels, robotic arms, and high-performance hobby/maker builds. Repo at [`odriverobotics/ODrive`](https://github.com/odriverobotics/ODrive) (MIT, 3.6k stars, Issues enabled, last commit `2026-01-20` — 4 months from cutoff 2026-05-28, **not archived**).

URML benefits from documenting the ODrive manifest mapping because:

1. **ODrive is the Layer-0 actuator-controller substrate** URML's manifest declares per axis. Where URML's prior outreach engaged the runtime / sensor / VLA layers, ODrive is the actuator-control silicon-and-firmware substrate one layer below the ROS 2 / micro-ROS adapter.
2. **The host-USB / CAN interface is the engagement point.** URML adapters can target ODrive via odrivetool, the Python library, or the CAN protocol. The manifest declares the interface class.
3. **Stanford Pupper / Solo / similar legged-robot research platforms use ODrive class drives.** URML's existing quadruped fixtures (`anymal_quadruped.yaml`, `digit_biped.yaml`) imply an actuator-controller layer URML's manifest has not made first-class.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `odrive_robotics_cell.yaml` fixture)

`actuators` block:

| URML field | Maps to ODrive product attribute |
|---|---|
| `name` | Deployment handle (`odrive_s1_axis0`, `odrive_pro_left_wheel`) |
| `actuator_class: custom` (`brushless_motor_controller`) | Declares ODrive class is the host-side controller |
| `actuator_class: custom` (`product_line`) | `odrive_s1` / `odrive_pro` / `odrive_3_6` |
| `actuator_class: custom` (`interface: usb_native` / `can_simple` / `can_cyphal`) | Declares which interface URML's adapter speaks |
| `actuator_class: custom` (`firmware_version`) | ODrive firmware version pin (for closed-loop reproducibility) |
| `actuator_class: custom` (`encoder_class`) | Magnetic / optical encoder class declaration |

### What URML v0.1 does not yet express for ODrive

1. **Actuator-controller substrate declaration.** URML's v0.1 has no `actuator_class: brushless_motor_controller` enum entry. Spec RFC queued; shared with RFC-0170 (Moteus), RFC-0179 (SimpleFOC), RFC-0180 (VESC).
2. **Per-axis interface-class declaration.** USB-native vs CAN-simple vs Cyphal/CAN-FD are distinct host-side protocols ODrive supports; URML's manifest cannot today declare which is active.
3. **Closed-loop firmware pinning.** ODrive's closed-loop control behavior depends on firmware version + tuning state; URML's manifest cannot today express the firmware/tuning pin for reproducible deployments.

### Compatibility notes

- **Vendor org.** [`odriverobotics`](https://github.com/odriverobotics) — vendor-direct.
- **Flagship repo.** [`odriverobotics/ODrive`](https://github.com/odriverobotics/ODrive) — MIT, 3.6k stars, Issues enabled, last commit 2026-01-20, **not archived**.
- **Origin.** ODrive Robotics, US. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active commercial entity; 4mo push staleness is borderline but the project is the flagship surface.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; actuator-controller substrate Spec RFC queued (shared with RFC-0170 / RFC-0179 / RFC-0180).
- Reference runtime: future `reference/actuator-runtime/ODriveAdapter` is a candidate; composes below URML's `reference/ros2-runtime/` at the actuator-control layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Actuator-controller substrate Spec RFC prerequisite.** Same gap as RFC-0170 / RFC-0179 / RFC-0180.
- **Closed-loop firmware reproducibility** is novel manifest territory.
- **4-month push staleness** at cutoff — borderline by URML's 6-month rule, but flagship.

## Alternatives considered

1. **Bundle ODrive + Moteus + SimpleFOC + VESC into one motor-controller RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; the actuator-controller Spec RFC is the shared piece.
2. **Defer until actuator-controller Spec RFC lands.** Rejected. ODrive maintainer input informs the Spec RFC.
3. **Cross-citation only.** Rejected. ODrive is vendor-direct + active + clean license; full manifest mapping is the appropriate engagement depth.

## Prior art

- [`odriverobotics/ODrive`](https://github.com/odriverobotics/ODrive) — the upstream flagship.
- [RFC-0170 (mjbots Moteus)](0170-mjbots-moteus-outreach.md) — sibling brushless-motor-controller RFC.
- [RFC-0179 (SimpleFOC)](0179-simplefoc-outreach.md) — community FOC reference library.
- [RFC-0180 (VESC Project)](0180-vesc-bldc-outreach.md) — sibling open-source BLDC ESC.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the micro-class robot manifest pattern that motor-controller declarations slot into.

## Unresolved questions

For the odriverobotics maintainers:

1. **Actuator-controller substrate manifest fields.** URML's v0.1 has no `brushless_motor_controller` actuator class. A Spec RFC is queued. What manifest fields would an ODrive deployment expect (product_line, interface, firmware_version, encoder_class, control-mode declaration)?
2. **Interface-class declaration.** USB-native, CAN-simple, Cyphal/CAN-FD — should URML's manifest declare which is the active host-side protocol?
3. **Closed-loop firmware pinning.** Should URML's manifest pin firmware version for reproducible closed-loop control behavior?
4. **Adapter home.** URML repo (`reference/actuator-runtime/ODriveAdapter`), ODrive-maintained `odriverobotics/odrive-urml-bridge`, or external?
5. **Conformance listing.** Would ODrive consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0169 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`odriverobotics/ODrive` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 3.6k stars, Issues enabled, last commit 2026-01-20, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (actuator-controller Spec-RFC prerequisite, firmware-pinning novelty, 4-mo push staleness).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: ODrive Robotics US; default policy passes.
- [x] CLAUDE.md compliance check passed.
