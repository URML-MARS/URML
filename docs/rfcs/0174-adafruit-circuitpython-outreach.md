---
rfc: 0174
title: Adafruit CircuitPython (Python on MCU) integration, request for comment from adafruit maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-28
updated: 2026-05-31
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

This table is reconciled to **[RFC-0270](0270-substrate-mcu-class.md)** (the Spec RFC that adds the MCU substrate declaration); the earlier draft of this RFC proposed ad-hoc `mcu_class` / `firmware_language` / `host_interface` fields, which RFC-0270 supersedes with `substrate.class` + `substrate.mcu_options`.

| URML field | Maps to CircuitPython attribute |
|---|---|
| `name` | Specific board (`adafruit_feather_rp2040`, `adafruit_qt_py_esp32`) |
| `substrate.class: circuitpython` | Declares the CircuitPython MCU substrate. RFC-0270 gives `circuitpython` and `micropython` **distinct** enum values (per @dhalbert: CircuitPython is a friendly fork of MicroPython with different hardware modules, so the two are distinct mappings). |
| `substrate.mcu_options.board` / `.chip` | Board + MCU-family identifier (`adafruit_feather_rp2040` / `rp2040`) per RFC-0270 |
| `substrate.mcu_options.bus_protocols` | MCU-side comms (`i2c` / `spi` / `uart`) per RFC-0270 |
| `substrate.mcu_options.library_bundle: circuitpython_community_bundle` | Where the device-side helper library lives — per @dhalbert, the [Community Bundle](https://github.com/adafruit/CircuitPython_Community_Bundle), not core |

### What URML v0.1 does not yet express for CircuitPython

1. **Python-on-MCU language substrate declaration.** URML's v0.1 has no `circuitpython` or generic `python_on_mcu` firmware-language declaration. Spec RFC queued (shared with RFC-0172 micro:bit MicroPython).
2. **Host-side comms, not drag-drop deploy.** URML integrates as a **host-side comms program** (serial / REPL), which @dhalbert confirmed is the direction CircuitPython/MicroPython favour. USB-mass-storage `code.py` drag-drop is **not assumed** — it is not available on every board (some lack an MSC drive). No manifest field is needed for the deploy model; the host-side adapter (see `reference/edu-runtime`) is the integration surface, and the device-side receiver's home is the Community Bundle.
3. **CircuitPython-compatible board-variant scale.** 400+ board variants means URML's manifest needs a structured identifier scheme, not per-board enum entries.

### Compatibility notes

- **Vendor org.** [`adafruit`](https://github.com/adafruit) — Adafruit Industries, US.
- **Flagship repo.** [`adafruit/CircuitPython`](https://github.com/adafruit/CircuitPython) — license Other (MIT-compatible per project), 4.5k stars, Issues + Discussions both enabled, last commit 2026-05-27 daily activity, **not archived**.
- **Origin.** Adafruit Industries, New York, US. Passes US-federal default policy.
- **License fit.** MIT-compatible cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; large active community; Discussions present.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; Python-on-MCU substrate + drag-drop deploy-model Spec RFCs queued.
- Reference runtime: **`CircuitPythonAdapter` shipped** in `reference/edu-runtime` (2026-05-31, in response to the engaged reply) — a host-side comms adapter mirroring the `RoboticalMartyAdapter` / `PetoiAdapter` parametric-dispatch shape, with a manifest fixture (`adafruit_feather_rp2040_cell`) and an educational conformance fixture (`educational/circuitpython_patrol_positive`). The concrete host-bridge package and the device-side Community-Bundle receiver are pending hardware validation.

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

## Maintainer responses

**2026-05-28, @dhalbert (`adafruit/circuitpython` COLLABORATOR, Adafruit) on [adafruit/circuitpython#11035](https://github.com/adafruit/circuitpython/issues/11035):** "We would not mind being listed in the spec," with five concrete points.

1. **Drag-drop deploy is not universal.** Some boards lack a USB-MSC drive, so `code.py` drag-drop cannot be assumed. URML's response: the integration is a host-side comms program (serial / REPL), no MSC assumption; the manifest table above is reframed accordingly.
2. **Adapter home is the Community Bundle, not core.** Adafruit will not maintain the URML adapter; the device-side helper library belongs in the [Adafruit CircuitPython Community Bundle](https://github.com/adafruit/CircuitPython_Community_Bundle). URML's response: the shipped `CircuitPythonAdapter` is the **host-side** half (in `reference/edu-runtime`); the device-side receiver targets the Community Bundle and is a founder action pending hardware validation.
3. **awesome-circuitpython pointer.** A pointer to URML can be added to [awesome-circuitpython](https://github.com/adafruit/awesome-circuitpython). URML's response: accepted as a founder action once the adapter is hardware-validated.
4. **CircuitPython is a friendly fork of MicroPython** sharing the base language but with different hardware modules — two distinct mappings are needed. URML's response: [RFC-0270](0270-substrate-mcu-class.md) already gives `circuitpython` and `micropython` **distinct** `substrate.class` enum values; the split is honoured at the spec layer.
5. **Host-side comms preferred, and a human reply requested.** @dhalbert noted MicroPython is deemphasizing MSC in favour of host-side comms programs, and asked to discuss with a human rather than an LLM. URML's response: the host-side adapter design follows this preference; the substantive thread reply is a founder action (a human reply), per [VIBE.md](../../VIBE.md).

Open items for the maintainers (Q1–Q7 above) remain available; the engaged response resolved the adapter-home (Q5) and library-namespace questions and reframed the deploy-model (Q3).

## Implementation note

RFC-0174 began as a single RFC document; the engaged reply produced a shipped host-side adapter (2026-05-31), so it now carries reference-runtime code, a manifest fixture, and a conformance fixture (the Marty / Petoi engagement-to-adapter pattern). Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

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
