---
rfc: 0183
title: TinyGo (Go compiler for MCU class) integration, request for comment from tinygo-org maintainers
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

# RFC-0183: TinyGo (Go compiler for MCU class) integration, request for comment from tinygo-org maintainers

## Summary

URML does not yet ship a TinyGo manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for TinyGo — the Go-language compiler for microcontroller substrates — over [`tinygo-org/tinygo`](https://github.com/tinygo-org/tinygo) (Apache-2.0), and **requests review and feedback from the tinygo-org maintainers**. No spec change.

**This RFC completes the 15 Move-13 engageable RFCs.**

## Motivation

TinyGo (community-maintained, BSD-style governance under tinygo-org) brings the Go language to MCU substrates spanning RP2040, SAMD21/51, nRF52, STM32, AVR, and WebAssembly. URML's outreach engages TinyGo as the Go-on-MCU language substrate complement to the Python-on-MCU substrates (RFC-0172 micro:bit MicroPython + RFC-0174 Adafruit CircuitPython).

Repo at [`tinygo-org/tinygo`](https://github.com/tinygo-org/tinygo) (Apache-2.0, 17.5k stars, Issues + Discussions both enabled, last commit `2026-05-28` daily activity, **not archived**). 17.5k stars makes TinyGo the second-largest GitHub-star surface in the Move-13 wave (after Zephyr Project at 15.4k — wait, TinyGo's 17.5k is actually the largest single-repo star count in Move-13).

The URML-fit framing is **firmware-language substrate declaration** at the Go-on-MCU level. URML's manifest declares which language compiles to the firmware artifact; TinyGo joins MicroPython, CircuitPython, native C/C++, and Arduino C++ in the substrate enum.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `tinygo_cell.yaml` fixture)

| URML field | Maps to TinyGo attribute |
|---|---|
| `name` | Deployment handle (`tinygo_default`) |
| `firmware_language: custom` (`tinygo`) | Declares Go (via TinyGo) is the firmware language |
| `mcu_class` | Cross-references RFC-0173 / RFC-0175 / RFC-0182 MCU board-class declarations |
| `tinygo.target` | TinyGo target identifier (`pico` / `arduino-nano33` / `wasm` / etc.) |
| `tinygo.version` | TinyGo release version pin |

### What URML v0.1 does not yet express for TinyGo

1. **Go-on-MCU firmware-language substrate declaration.** URML's v0.1 has no `tinygo` firmware-language enum entry. Spec RFC queued (firmware-language substrate Spec, sub-shared with the Python-on-MCU declarations from RFC-0172 / RFC-0174).
2. **WebAssembly target declaration.** TinyGo's WebAssembly target opens a non-MCU substrate (browser / serverless / WASI) URML's manifest cannot today declare.
3. **TinyGo target catalog.** TinyGo's `tinygo targets` lists 90+ target identifiers; URML's manifest needs an identifier-mapping convention (similar to RFC-0176 PlatformIO).

### Compatibility notes

- **Vendor / org.** [`tinygo-org`](https://github.com/tinygo-org) — community-maintained (vendor-neutral; Linux-Foundation-adjacent posture).
- **Flagship repo.** [`tinygo-org/tinygo`](https://github.com/tinygo-org/tinygo) — Apache-2.0, 17.5k stars, Issues + Discussions both enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** Community (multi-national contributors). Passes URML's US-federal default policy (foundation-adjacent + multi-vendor + Apache-2.0 + no PRC-domiciled-governance flag).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; very large star count (17.5k); Discussions present for design discussion; community gravity is high.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; firmware-language substrate + TinyGo-target-catalog Spec RFCs queued (firmware-language sub-shared with RFC-0172 / RFC-0174).
- Reference runtime: future `reference/edu-runtime/TinyGoAdapter` is a candidate — composes with sibling MCU-platform RFCs at the Go-language layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Firmware-language substrate Spec RFC prerequisite** (sub-shared with Python-on-MCU declarations).
- **WebAssembly target opens a non-MCU substrate** — URML's manifest pattern is robotics-class focused; WASM as a Go target is interesting but out of Move-13 scope.
- **90+ TinyGo targets** demand identifier-mapping convention.

## Alternatives considered

1. **Bundle TinyGo + sibling firmware-language RFCs (RFC-0172 MicroPython, RFC-0174 CircuitPython) into one language-substrate RFC.** Rejected. Per-vendor RFCs let conversation thread per maintainer group.
2. **Skip TinyGo as overlapping with native-C/C++ paths.** Rejected. Go-on-MCU is a distinct language ecosystem with its own community + tooling; complementary to Python and C/C++ on MCU.
3. **Cross-citation only.** Considered. Apache-2.0 + active + URML-fit argues for full manifest mapping.

## Prior art

- [`tinygo-org/tinygo`](https://github.com/tinygo-org/tinygo) — the upstream compiler.
- [RFC-0172 (BBC micro:bit MicroPython)](0172-microbit-foundation-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md) — sibling firmware-language-on-MCU RFCs (Python lineage).
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0175 (Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md) — sibling C/C++ firmware-language RFCs.
- [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling cross-board build-system RFC.

## Unresolved questions

For the tinygo-org maintainers:

1. **Firmware-language substrate manifest fields.** URML's v0.1 has no `tinygo` firmware-language declaration. Spec RFC queued. Manifest field expectations from the TinyGo perspective?
2. **TinyGo-target catalog identifier scheme.** Should URML's manifest use TinyGo's target-id directly, or a separate URML identifier mapped to it?
3. **WebAssembly target scope.** Should URML's manifest declare WebAssembly as a valid TinyGo target (non-MCU substrate), and how does that compose with URML's robotics-class manifest assumptions?
4. **Adapter home.** URML repo (`reference/edu-runtime/TinyGoAdapter`), TinyGo-community-maintained `tinygo-org/tinygo-urml-bridge`, or external?
5. **Conformance listing.** Would the tinygo-org maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0183 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml). **Completes the 15 Move-13 engageable RFCs.**

## How to respond

`tinygo-org/tinygo` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 17.5k stars, Issues + Discussions enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (firmware-language Spec-RFC prerequisite, WebAssembly target out-of-scope, 90+ target scheme).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: community (multi-national); passes default policy.
- [x] CLAUDE.md compliance check passed.
