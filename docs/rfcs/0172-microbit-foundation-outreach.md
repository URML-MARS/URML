---
rfc: 0172
title: BBC micro:bit Foundation (educational MCU platform) integration, request for comment from microbit-foundation maintainers
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

# RFC-0172: BBC micro:bit Foundation (educational MCU platform) integration, request for comment from microbit-foundation maintainers

## Summary

URML does not yet ship a vendor-direct micro:bit Foundation outreach, but **does ship the `microbit_edu` manifest fixture (RFC-0018) — a direct application of the BBC micro:bit platform**. This RFC documents the proposed URML v0.1 capability-manifest mapping for the micro:bit v2 over [`microbit-foundation/micropython-microbit-v2`](https://github.com/microbit-foundation/micropython-microbit-v2) (MIT), and **requests review and feedback from the micro:bit Foundation maintainers**. No spec change.

## Motivation

The BBC micro:bit Foundation (Cambridge, UK) is the educational-MCU institution behind one of the most widely deployed classroom robotics platforms in the world. URML's `microbit_edu` manifest fixture has been the canonical URML pattern for the **micro-class robot** since RFC-0018; the engagement here closes the loop with the foundation upstream.

Repo at [`microbit-foundation/micropython-microbit-v2`](https://github.com/microbit-foundation/micropython-microbit-v2) (MIT, 56 stars, Issues + Discussions both enabled, last commit `2024-09-18`, **not archived**). The star count is modest — micro:bit Foundation engagement is institutional rather than community-volume — but the surface is durable and the fit is uncommon: URML already has the fixture, and the foundation's view on its manifest mapping carries unusual weight for downstream educational deployments.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `microbit_v2_cell.yaml` fixture — refines existing `microbit_edu` fixture)

`hardware` block:

| URML field | Maps to micro:bit v2 attribute |
|---|---|
| `name` | `microbit_v2` |
| `mcu_class: custom` (`nrf52833`) | Nordic nRF52833 SoC |
| `mcu_class: custom` (`coprocessor: kl27z`) | Onboard secondary MCU for USB / debug |
| `firmware_language: custom` (`micropython`) | MicroPython on micro:bit v2 |
| `peripherals` | Accelerometer + magnetometer + microphone + speaker + LED matrix + buttons |

### What URML v0.1 does not yet express for micro:bit

1. **MCU + coprocessor declaration.** micro:bit v2 has two MCUs (nRF52833 main + KL27Z interface); URML's manifest does not today declare multi-MCU compositions.
2. **Firmware-language substrate declaration.** MicroPython vs MakeCode / C++ are distinct firmware-language substrates; URML's manifest cannot today declare which is loaded.
3. **Educational-class declaration.** The "designed for K-12 education" framing is a deployment-context flag URML's manifest does not today carry; relevant for default safety envelopes.

### Compatibility notes

- **Vendor / foundation.** [`microbit-foundation`](https://github.com/microbit-foundation) — BBC micro:bit Educational Foundation; UK Cambridge.
- **Flagship repo.** [`microbit-foundation/micropython-microbit-v2`](https://github.com/microbit-foundation/micropython-microbit-v2) — MIT, 56 stars, Issues + Discussions both enabled, last commit 2024-09-18, **not archived**.
- **Origin.** UK (Cambridge). Passes US-federal default policy (Five Eyes ally).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Foundation-direct; institutional surface. Modest GitHub volume reflects institutional cadence, not project health.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; multi-MCU + firmware-language substrate Spec RFCs queued.
- Reference runtime: existing `microbit_edu` manifest fixture (RFC-0018) is the prior art; this engagement validates / refines the manifest mapping upstream.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multi-MCU declaration Spec RFC prerequisite.**
- **Modest GitHub volume.** Foundation cadence is slower than commercial vendor repos; engagement may be light-touch.
- **Existing `microbit_edu` fixture cross-link.** Any maintainer feedback might prompt fixture refinements — that's positive but is a follow-up scope.

## Alternatives considered

1. **Bundle micro:bit + Pi Pico + Arduino + Adafruit + PlatformIO into one MCU-platforms RFC.** Rejected. Per-vendor RFCs let conversation thread per maintainer group.
2. **Engage MakeCode (Microsoft) instead.** Considered. MakeCode is a downstream tool / IDE, not the foundation; per-target RFC at the foundation layer is the right shape.
3. **Cross-citation only.** Rejected. URML already has the fixture; foundation engagement is appropriate engagement depth.

## Prior art

- [`microbit-foundation/micropython-microbit-v2`](https://github.com/microbit-foundation/micropython-microbit-v2) — the upstream MicroPython port.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML Spec RFC that introduced the `microbit_edu` manifest pattern.
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md), [RFC-0175 (Raspberry Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling MCU-platform RFCs.

## Unresolved questions

For the micro:bit Foundation maintainers:

1. **Manifest fixture refinement.** URML's existing `microbit_edu` fixture sketches the micro:bit v2 manifest mapping. What fields would the foundation refine / add?
2. **MicroPython vs MakeCode declaration.** Should URML's manifest declare which firmware-language substrate is loaded?
3. **Educational-class declaration.** Useful manifest flag for K-12 deployments + default safety envelopes?
4. **Adapter home.** URML repo (`reference/edu-runtime/MicrobitAdapter`), micro:bit-Foundation-maintained `microbit-foundation/microbit-urml-bridge`, or both?
5. **Conformance listing.** Would the foundation consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0172 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`microbit-foundation/micropython-microbit-v2` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC, with the existing `microbit_edu` fixture cross-link explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 56 stars, Issues + Discussions enabled, last commit 2024-09-18, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multi-MCU Spec-RFC prerequisite, modest GitHub volume, existing-fixture cross-link scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: BBC micro:bit Foundation UK; default policy passes.
- [x] CLAUDE.md compliance check passed.
