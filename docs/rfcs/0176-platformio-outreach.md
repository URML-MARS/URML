---
rfc: 0176
title: PlatformIO (cross-board MCU IDE / build system) integration, request for comment from platformio maintainers
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

# RFC-0176: PlatformIO (cross-board MCU IDE / build system) integration, request for comment from platformio maintainers

## Summary

URML does not yet ship a PlatformIO manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for PlatformIO — the cross-board MCU IDE / build pipeline spanning 900+ board variants — over [`platformio/platformio-core`](https://github.com/platformio/platformio-core) (Apache-2.0), and **requests review and feedback from the platformio maintainers**. No spec change.

This RFC complements [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md), [RFC-0175 (Raspberry Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md) at the **build-system layer** — one layer above the per-board / per-vendor MCU platforms.

## Motivation

PlatformIO Labs (Ukraine) maintains the canonical multi-vendor MCU build system spanning 900+ board variants and 30+ MCU families. Repo at [`platformio/platformio-core`](https://github.com/platformio/platformio-core) (Apache-2.0, 9.3k stars, Issues enabled, last commit `2026-04-21`, **not archived**).

The URML-fit framing is **build-system substrate declaration**: where Arduino / Pi Pico / CircuitPython declare the firmware-language and target board class, PlatformIO declares the build pipeline that produced the firmware. URML's manifest can declare PlatformIO as the build-substrate the firmware artifact targets; PlatformIO's `platformio.ini` board-config maps to URML's hardware identifier with vendor-neutrality across the 900+ boards.

This is structurally similar to how PlatformIO itself abstracts MCU diversity — URML's manifest is the substrate-neutral vocabulary above, PlatformIO is the substrate-neutral build pipeline below, with both sides making compatible bets on vendor-neutrality.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `platformio_build_cell.yaml` fixture)

| URML field | Maps to PlatformIO attribute |
|---|---|
| `build_system.framework: custom` (`platformio`) | Declares PlatformIO is the build-substrate |
| `build_system.platformio_ini` (board / platform / framework triple) | PlatformIO's canonical board-config |
| `build_system.dependency_specs` | `lib_deps` declarations in `platformio.ini` |
| `mcu_class` | Derived from PlatformIO board-id (cross-references RFC-0173 / RFC-0174 / RFC-0175 board declarations) |

### What URML v0.1 does not yet express for PlatformIO

1. **Build-system substrate declaration.** URML's v0.1 has no `build_system` block. Spec RFC queued — PlatformIO is the natural reference shape.
2. **PlatformIO board-id mapping.** PlatformIO's 900+ board catalog has its own identifier scheme; URML's manifest needs a mapping convention.
3. **Build-time dependency-spec declaration.** `lib_deps` declares the libraries a firmware was built against — URML's manifest cannot today declare this build-time dependency provenance.

### Compatibility notes

- **Vendor org.** [`platformio`](https://github.com/platformio) — PlatformIO Labs.
- **Flagship repo.** [`platformio/platformio-core`](https://github.com/platformio/platformio-core) — Apache-2.0, 9.3k stars, Issues enabled, last commit 2026-04-21, **not archived**.
- **Origin.** PlatformIO Labs, Ukraine (UA). Passes US-federal default policy (Ukraine is allied / strategic US partner).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** ~5-week push staleness at cutoff is normal cadence; 9.3k-star surface is substantial.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; build-system substrate Spec RFC queued (this is the natural reference shape).
- Reference runtime: future `reference/edu-runtime/PlatformIOAdapter` is a candidate — composes above per-board / per-vendor adapters (RFC-0173 / RFC-0174 / RFC-0175).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Build-system substrate Spec RFC prerequisite.**
- **900+ board-catalog scale** demands manifest-side identifier mapping convention.
- **Dependency-spec declaration** is novel manifest territory.

## Alternatives considered

1. **Engage at the IDE / Cloud product level (PlatformIO Labs' commercial offerings).** Rejected. PlatformIO Core is the OSS substrate URML adapters compose with; vendor-direct OSS engagement is the right shape.
2. **Bundle PlatformIO + sibling MCU-platform RFCs.** Rejected. Per-vendor RFCs; build-system layer is structurally distinct from per-board layer.
3. **Cross-citation only.** Rejected. Apache-2.0 + URML-fit + 9.3k stars is high enough for full manifest mapping.

## Prior art

- [`platformio/platformio-core`](https://github.com/platformio/platformio-core) — the upstream build system.
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0174 (Adafruit CircuitPython)](0174-adafruit-circuitpython-outreach.md), [RFC-0175 (Raspberry Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md) — sibling MCU-platform RFCs at the per-board layer that PlatformIO abstracts above.

## Unresolved questions

For the platformio maintainers:

1. **Build-system substrate manifest fields.** URML's v0.1 has no `build_system` block. Spec RFC queued. Manifest field expectations from PlatformIO's perspective (platformio.ini reflection, lib_deps declaration, board-id mapping convention)?
2. **900+ board-catalog identifier scheme.** Should URML's manifest use PlatformIO's board-id directly, or a separate URML identifier mapped to it?
3. **Build-time dependency-spec declaration.** Useful manifest field for downstream operators checking which libraries the firmware was built against?
4. **Adapter home.** URML repo (`reference/edu-runtime/PlatformIOAdapter`), PlatformIO-maintained `platformio/platformio-urml-bridge`, or both?
5. **Conformance listing.** Would PlatformIO consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0176 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`platformio/platformio-core` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 9.3k stars, Issues enabled, last commit 2026-04-21, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (build-system Spec-RFC prerequisite, 900+ board scheme, dependency-spec novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: PlatformIO Labs UA; default policy passes.
- [x] CLAUDE.md compliance check passed.
