---
rfc: 0174
title: Adafruit CircuitPython (Python on MCU) integration, request for comment from adafruit maintainers
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

# RFC-0174: Adafruit CircuitPython (Python on MCU) integration, request for comment from adafruit maintainers

## Summary

URML does not yet ship an Adafruit CircuitPython manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for CircuitPython — Adafruit's Python-on-MCU language and library ecosystem — over [`adafruit/CircuitPython`](https://github.com/adafruit/CircuitPython) (MIT-compatible), and **requests review and feedback from the adafruit maintainers**. No spec change.

This RFC complements [RFC-0172 (BBC micro:bit Foundation)](0172-microbit-foundation-outreach.md) on URML's Python-on-MCU surface. Where micro:bit Foundation ships MicroPython for one specific board, Adafruit ships CircuitPython across hundreds of boards including their own Feather / Trinket / QT Py lines.

## Motivation

Adafruit Industries (US, New York) is the maker-class MCU institution behind CircuitPython — a Python derivative purpose-built for embedded education and rapid prototyping. CircuitPython runs on 400+ board variants spanning RP2040, SAMD21/51, nRF52, STM32, and ESP32. Repo at [`adafruit/CircuitPython`](https://github.com/adafruit/CircuitPython) (Other / MIT-compatible per project license, 4.5k stars, Issues + Discussions both enabled, last commit `2026-05-27` daily activity, **not archived**).

URML's existing `microbit_edu` manifest pattern (RFC-0018) implicitly covers CircuitPython-class boards. Vendor-direct engagement at the CircuitPython layer covers:

- The Python-on-MCU language substrate URML's manifest declares.
- The board-variant-class ecosystem (Adafruit Feather / Trinket / QT Py / etc. plus third-party CircuitPython-compatible boards).
- The library ecosystem (Adafruit_CircuitPython_*) URML adapters compose with.

The natural URML integration shape is host-side: a Mu / Thonny / Code-with-Mu IDE-side bridge that emits validated URML primitives, with CircuitPython on the device dispatching them.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `adafruit_feather_rp2040_cell.yaml` fixture)

| URML field | Maps to CircuitPython attribute |
|---|---|
| `name` | Specific board (`adafruit_feather_rp2040`, `adafruit_qt_py_esp32`) |
| `mcu_class: custom` (`circuitpython_compatible`) | Declares CircuitPython-compatible board-class |
| `firmware_language: custom` (`circuitpython`) | Python derivative on the MCU |
| `host_interface: custom` (`circuitpython_repl` / `code_drag_drop`) | CircuitPython's distinctive USB-mass-storage `code.py` model |
| `library_namespace: custom` (`adafruit_circuitpython_*`) | Adafruit library naming convention |

### What URML v0.1 does not yet express for CircuitPython

1. **Python-on-MCU language substrate declaration.** URML's v0.1 has no `circuitpython` or generic `python_on_mcu` firmware-language declaration. Spec RFC queued (shared with RFC-0172 micro:bit MicroPython).
2. **Drag-drop `code.py` deploy-model declaration.** CircuitPython's distinguishing feature is USB-mass-storage drag-drop deploy — URML's manifest cannot today declare this deploy-model class.
3. **CircuitPython-compatible board-variant scale.** 400+ board variants means URML's manifest needs a structured identifier scheme, not per-board enum entries.

### Compatibility notes

- **Vendor org.** [`adafruit`](https://github.com/adafruit) — Adafruit Industries, US.
- **Flagship repo.** [`adafruit/CircuitPython`](https://github.com/adafruit/CircuitPython) — license Other (MIT-compatible per project), 4.5k stars, Issues + Discussions both enabled, last commit 2026-05-27 daily activity, **not archived**.
- **Origin.** Adafruit Industries, New York, US. Passes US-federal default policy.
- **License fit.** MIT-compatible cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; large active community; Discussions present.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; Python-on-MCU substrate + drag-drop deploy-model Spec RFCs queued.
- Reference runtime: future `reference/edu-runtime/CircuitPythonAdapter` is a candidate — composes with the existing `microbit_edu` fixture pattern at the Python-MCU layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Python-on-MCU substrate Spec RFC prerequisite** (shared with RFC-0172 micro:bit).
- **400+ board-variant scale** demands manifest identifier scheme work.
- **Drag-drop deploy-model declaration is novel manifest territory.**

## Alternatives considered

1. **Engage MicroPython upstream instead.** Considered. CircuitPython is the Adafruit fork with distinctive deploy-model + library ecosystem; vendor-direct engagement is the right shape. (MicroPython upstream could be a future Move target.)
2. **Bundle Adafruit + sibling MCU-platform RFCs.** Rejected. Per-vendor RFCs.
3. **Cross-citation only.** Rejected. Vendor-direct + daily-active + URML-fit is high.

## Prior art

- [`adafruit/CircuitPython`](https://github.com/adafruit/CircuitPython) — the upstream Python-on-MCU.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML manifest pattern.
- [RFC-0172 (BBC micro:bit Foundation)](0172-microbit-foundation-outreach.md) — sibling MicroPython-on-MCU RFC (single-board surface).
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0175 (Raspberry Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling MCU-platform RFCs.

## Unresolved questions

For the adafruit maintainers:

1. **Python-on-MCU substrate manifest fields.** Same shared question as RFC-0172. Manifest field expectations from the CircuitPython perspective?
2. **400+ board-variant identifier scheme.** Should URML's manifest use CircuitPython's existing board-id convention, or a separate URML identifier mapped to it?
3. **Drag-drop deploy-model declaration.** Useful manifest field for educational deployments?
4. **Library-ecosystem declaration.** Should URML's manifest declare which Adafruit_CircuitPython_* libraries are loaded?
5. **Adapter home.** URML repo (`reference/edu-runtime/CircuitPythonAdapter`), Adafruit-maintained `adafruit/circuitpython-urml-bridge`, or both?
6. **Conformance listing.** Would Adafruit consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0174 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`adafruit/CircuitPython` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT-compatible, 4.5k stars, Issues + Discussions enabled, last commit 2026-05-27 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (Python-on-MCU Spec-RFC prerequisite, 400+ variant scheme, drag-drop deploy-model novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Adafruit Industries US; default policy passes.
- [x] CLAUDE.md compliance check passed.
