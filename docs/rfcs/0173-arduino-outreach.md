---
rfc: 0173
title: Arduino (world's largest hobbyist MCU platform) integration, request for comment from arduino maintainers
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

# RFC-0173: Arduino (world's largest hobbyist MCU platform) integration, request for comment from arduino maintainers — and a license-clarification ask

## Summary

URML does not yet ship an Arduino-board manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Arduino-compatible boards over [`arduino/Arduino`](https://github.com/arduino/Arduino), and **requests review and feedback from the arduino maintainers**. **License-clarification ask:** the repo's license is listed as "Other" by the GitHub API; an explicit OSI declaration (LGPL vs GPL clarification on which surface) is the gating ask. No spec change.

## Motivation

Arduino S.r.l. (Italy) maintains the world's largest hobbyist MCU platform — Arduino IDE, board-package ecosystem, and the implicit "Arduino-compatible" hardware ecosystem spanning thousands of board variants. Repo at [`arduino/Arduino`](https://github.com/arduino/Arduino) (license: Other, 14.6k stars, Issues enabled, last commit `2025-10-11`, **not archived**).

URML's `microbit_edu` manifest pattern (RFC-0018) implicitly covers Arduino-compatible boards but URML has no Arduino-specific manifest yet. Vendor-direct engagement at the Arduino layer covers:

- The IDE / build system Arduino maintains.
- The implicit board-class ecosystem (Uno, Nano, Mega, MKR, Portenta, etc.) URML's manifest would declare.
- The library / package conventions URML adapters compose with.

The license posture is the gating fact. Arduino's source has historically been a mix of LGPL (libraries) and GPL (IDE), with the trademark layer kept separate. URML's adapter-grade reuse depends on which surface carries which license, and the GitHub API's "Other" classification doesn't disambiguate.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `arduino_uno_cell.yaml` fixture, applicable to broader Arduino-compatible class)

| URML field | Maps to Arduino attribute |
|---|---|
| `name` | Specific board (`arduino_uno_r3`, `arduino_nano_33_ble`, `arduino_portenta_h7`) |
| `mcu_class: custom` (`arduino_compatible`) | Declares Arduino-compatible board-class |
| `mcu_class: custom` (`arduino_board_identifier`) | Vendor / model FQBN-style identifier |
| `firmware_language: custom` (`arduino_c_cpp`) | Arduino sketch C/C++ |
| `build_system: custom` (`arduino_ide` or `arduino_cli`) | Declares which build pipeline produced the firmware |

### What URML v0.1 does not yet express for Arduino

1. **Arduino-compatible board-class declaration.** URML's v0.1 has no `arduino_compatible` mcu_class enum entry. Spec RFC queued — shared with RFC-0174 / RFC-0175 / RFC-0176 (MCU + maker platform Spec RFC).
2. **License-surface declaration.** Arduino's mixed-license posture (LGPL libraries, GPL IDE, trademark) is the kind of thing URML's manifest should be able to declare so downstream operators understand the bundling boundaries.
3. **FQBN (Fully Qualified Board Name) declaration.** Arduino's FQBN scheme is the canonical board-identifier; URML's manifest cannot today declare which FQBN is the active target.

### Compatibility notes

- **Vendor org.** [`arduino`](https://github.com/arduino) — Arduino S.r.l., Italy.
- **Flagship repo.** [`arduino/Arduino`](https://github.com/arduino/Arduino) — license Other (clarification ask), 14.6k stars, Issues enabled, last commit 2025-10-11, **not archived**.
- **Origin.** Arduino S.r.l., Italy (IT). Passes US-federal default policy (NATO+EU).
- **License fit.** Pending clarification. LGPL (libraries) cleanly composes with URML's Apache-2.0 stance; GPL (IDE) is OK at the build-tool boundary.
- **Maintainer signal.** ~7-month push staleness on the IDE repo is the cadence; the org has multiple repos with faster cadence (arduino-cli, library-installer, etc.).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; MCU + maker platform Spec RFC queued.
- Reference runtime: future `reference/edu-runtime/ArduinoAdapter` is a candidate — composes with the existing `microbit_edu` fixture pattern.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.** "Other" upstream blocks Apache-2.0 downstream reuse without clarification.
- **MCU + maker platform Spec RFC prerequisite.**
- **FQBN declaration is novel manifest territory.**
- **The Arduino S.r.l. / Arduino LLC fork-history is sometimes resurfaced** in license discussions; URML's RFC doesn't engage that history.

## Alternatives considered

1. **Engage arduino-cli instead.** Considered. The IDE repo is the canonical flagship even though arduino-cli is more actively developed; per-flagship engagement is the cleaner shape.
2. **Bundle Arduino + sibling MCU-platform RFCs.** Rejected. Per-vendor RFCs let conversation thread per maintainer group.
3. **Cross-citation only.** Rejected. Vendor-direct + 14.6k-star surface + URML-fit is high enough for full manifest mapping engagement.

## Prior art

- [`arduino/Arduino`](https://github.com/arduino/Arduino) — the upstream IDE / flagship.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML manifest pattern that Arduino-compatible boards populate.
- [RFC-0172 (BBC micro:bit Foundation)](0172-microbit-foundation-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md), [RFC-0175 (Raspberry Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling MCU-platform RFCs.

## Unresolved questions

For the arduino maintainers:

1. **License clarification.** Can `arduino/Arduino` get an explicit OSI license declaration (LGPL libraries / GPL IDE / clarifies which-on-which-surface)?
2. **Arduino-compatible board-class manifest fields.** URML's v0.1 has no `arduino_compatible` mcu_class. Spec RFC queued. Manifest field expectations (FQBN, board_identifier, package_manager dependencies)?
3. **License-surface manifest declaration.** Should URML's manifest declare the license boundary the firmware was built against?
4. **Adapter home.** URML repo (`reference/edu-runtime/ArduinoAdapter`), Arduino-maintained `arduino/arduino-urml-bridge`, or both?
5. **Conformance listing.** Would Arduino consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0173 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`arduino/Arduino` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license Other, 14.6k stars, Issues enabled, last commit 2025-10-11, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, MCU+maker Spec-RFC prerequisite, FQBN novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Arduino S.r.l. Italy; default policy passes.
- [x] CLAUDE.md compliance check passed.
