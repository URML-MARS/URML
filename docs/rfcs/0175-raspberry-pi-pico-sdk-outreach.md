---
rfc: 0175
title: Raspberry Pi Pico SDK (RP2040 / RP2350 native C/C++) integration, request for comment from raspberrypi maintainers
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

# RFC-0175: Raspberry Pi Pico SDK (RP2040 / RP2350 native C/C++) integration, request for comment from raspberrypi maintainers

## Summary

URML does not yet ship a Raspberry Pi Pico manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for RP2040 / RP2350 native C/C++ firmware over [`raspberrypi/pico-sdk`](https://github.com/raspberrypi/pico-sdk) (BSD-3-Clause), and **requests review and feedback from the raspberrypi maintainers**. No spec change.

This RFC pairs with [RFC-0172 (BBC micro:bit Foundation)](0172-microbit-foundation-outreach.md) as the second UK-foundation MCU engagement. micro:bit targets K-12; Pi Pico targets the higher-perf MCU class — robotics, audio synthesis, dual-core compute.

## Motivation

The Raspberry Pi Foundation (Cambridge, UK) shipped the RP2040 SoC in 2021 and the RP2350 successor in 2024. The Pico SDK is the native C/C++ surface for both. URML benefits from documenting the Pi Pico manifest mapping because:

1. **RP2040 / RP2350 are the rising default MCU** for hobbyist robotics, drone flight-controllers (Crazyflie successor lineage), and educational sensor platforms.
2. **Dual-core symmetric architecture** is structurally distinct from single-core MCUs URML's existing fixtures cover.
3. **Foundation-direct engagement** complements RFC-0172 (micro:bit Foundation) at the higher-perf MCU class.

Repo at [`raspberrypi/pico-sdk`](https://github.com/raspberrypi/pico-sdk) (BSD-3-Clause, 4.8k stars, Issues enabled, last commit `2026-05-28` daily activity, **not archived**).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `raspberrypi_pico_cell.yaml` fixture)

| URML field | Maps to Pi Pico attribute |
|---|---|
| `name` | Specific board (`pico_w`, `pico2_w`, `pico_2`) |
| `mcu_class: custom` (`rp2040` / `rp2350`) | RP2040 / RP2350 SoC |
| `mcu_class: custom` (`core_count`) | 2 (dual-core ARM Cortex-M0+ on RP2040; dual-core Cortex-M33 + RISC-V on RP2350) |
| `mcu_class: custom` (`pio_blocks`) | RP-series PIO (Programmable I/O) state machines — distinctive feature |
| `firmware_language: custom` (`pico_sdk_c_cpp`) | Pico SDK native C/C++ |
| `peripherals` | Wireless if Pico W / 2 W (CYW43439 Wi-Fi + Bluetooth) |

### What URML v0.1 does not yet express for Pi Pico

1. **Dual-core MCU declaration.** URML's existing `microbit_edu` pattern assumes single-core; dual-core is structurally distinct (which core hosts which adapter functionality matters).
2. **PIO state-machine declaration.** RP-series PIO is the distinguishing feature; URML's manifest cannot today declare PIO availability + which state machines are committed.
3. **Heterogeneous-core declaration (RP2350).** RP2350 ships both Cortex-M33 and RISC-V cores selectable at boot; URML's manifest cannot today declare the active core architecture.

### Compatibility notes

- **Vendor org.** [`raspberrypi`](https://github.com/raspberrypi) — Raspberry Pi Foundation; UK Cambridge.
- **Flagship repo.** [`raspberrypi/pico-sdk`](https://github.com/raspberrypi/pico-sdk) — BSD-3-Clause, 4.8k stars, Issues enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** UK Cambridge. Passes US-federal default policy (Five Eyes ally).
- **License fit.** BSD-3-Clause cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; foundation-direct.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; dual-core + PIO + heterogeneous-core declaration Spec RFCs queued.
- Reference runtime: future `reference/edu-runtime/PiPicoAdapter` is a candidate — companion to RFC-0172 micro:bit at the higher-perf MCU class.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Dual-core + PIO + heterogeneous-core declarations** are all novel manifest territory; multiple Spec-RFC prerequisites.
- **MicroPython on Pi Pico exists too** — URML's manifest may need to handle both native-C/C++ (this RFC) and MicroPython (similar to RFC-0172 micro:bit pattern) on the same board class.

## Alternatives considered

1. **Engage MicroPython-on-Pico instead.** Considered. The native SDK is the more general substrate; MicroPython is a downstream port. Per-flagship engagement at the foundation level.
2. **Bundle Pi Pico + sibling MCU-platform RFCs.** Rejected. Per-vendor RFCs.
3. **Cross-citation only.** Rejected. Foundation-direct + BSD-3-Clause + daily activity + URML-fit is high.

## Prior art

- [`raspberrypi/pico-sdk`](https://github.com/raspberrypi/pico-sdk) — the upstream SDK.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML manifest pattern.
- [RFC-0172 (BBC micro:bit Foundation)](0172-microbit-foundation-outreach.md) — sibling UK-foundation MCU RFC (K-12 layer).
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling MCU-platform RFCs.

## Unresolved questions

For the raspberrypi maintainers:

1. **Dual-core declaration manifest fields.** Which core hosts which adapter functionality? Should URML's manifest declare per-core assignments?
2. **PIO state-machine declaration.** Manifest field for PIO availability + which state machines are reserved / committed?
3. **Heterogeneous-core declaration (RP2350).** Cortex-M33 vs RISC-V selection — manifest declaration shape?
4. **Native-SDK vs MicroPython manifest declaration.** Should URML's manifest distinguish the firmware-language substrate explicitly?
5. **Adapter home.** URML repo (`reference/edu-runtime/PiPicoAdapter`), Raspberry-Pi-maintained `raspberrypi/pico-urml-bridge`, or both?
6. **Conformance listing.** Would the Raspberry Pi Foundation consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0175 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`raspberrypi/pico-sdk` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 4.8k stars, Issues enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites — dual-core, PIO, heterogeneous-core; firmware-language overlap with MicroPython).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Raspberry Pi Foundation UK; default policy passes.
- [x] CLAUDE.md compliance check passed.
