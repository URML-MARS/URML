---
rfc: 0182
title: STMicroelectronics STM32Cube (industrial MCU HAL + middleware) integration, request for comment from STMicroelectronics maintainers — mixed-license clarification ask
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

# RFC-0182: STMicroelectronics STM32Cube integration, request for comment from STMicroelectronics maintainers — mixed-license clarification ask

## Summary

URML does not yet ship an STM32 manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest cross-citation for STMicroelectronics' STM32Cube HAL + middleware over [`STMicroelectronics/STM32CubeF4`](https://github.com/STMicroelectronics/STM32CubeF4), and **requests review and feedback from the STMicroelectronics maintainers**. **Mixed-license posture — clarification ask:** ST's repos carry a mix of permissive (BSD-3-Clause, MIT) and proprietary-with-redistribution-license components; an explicit per-surface SPDX declaration would clarify URML's adapter-grade-reuse boundaries. No spec change.

## Motivation

STMicroelectronics (HQ Geneva, Switzerland; Franco-Italian heritage) makes the STM32 family — one of the two most-deployed MCU families in robotics (alongside ESP32, which URML excluded under NDAA Section 889 — see RFC-0137 / move13-research file). Used widely in drone flight controllers (Crazyflie / PX4-class), industrial robots, medical devices, automotive ECUs.

Repo at [`STMicroelectronics/STM32CubeF4`](https://github.com/STMicroelectronics/STM32CubeF4) — license "Other" (mixed), 1.2k stars, Issues enabled, last commit `2026-05-26` very active, **not archived**. The repo is one of many in the `STMicroelectronics` org (separate STM32CubeF0/F1/F2/F3/F4/F7/H7/L0/L1/L4/U5/G0/G4/WB/WL/WBA series).

URML's manifest can declare STM32 as the MCU substrate class; the cross-citation framing reflects the mixed-license posture (URML doesn't bundle ST middleware but composes via PlatformIO / STM32CubeIDE / stand-alone toolchain build).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `st_stm32cube_cell.yaml` fixture)

| URML field | Maps to STM32Cube attribute |
|---|---|
| `name` | Specific board (`stm32_nucleo_f767zi`, `stm32_disco_h747i`) |
| `mcu_class: custom` (`stm32_<series>`) | STM32 series (`stm32f4` / `stm32h7` / `stm32u5` etc.) |
| `mcu_class: custom` (`cube_hal_version`) | STM32Cube HAL release pin |
| `middleware: custom` (FreeRTOS / LwIP / USB-OTG / etc.) | Cube middleware components used |
| `firmware_license_posture: custom` (`mixed_st_permissive_plus_proprietary`) | Cross-citation framing flag |

### What URML v0.1 does not yet express for STM32

1. **MCU substrate declaration** — same shared gap as RFC-0172 / RFC-0173 / RFC-0174 / RFC-0175 (MCU + maker Spec RFC queued).
2. **Mixed-license-surface declaration.** URML's manifest cannot today declare per-surface license boundaries (ST permissive cores vs proprietary-with-redistribution middleware).
3. **Cube ecosystem version pinning.** STM32Cube version compatibility matrix (HAL + LL + middleware) is a deployment-defining property URML's manifest cannot today carry.
4. **Multi-series scope.** STM32 has 15+ series families; URML's manifest needs to handle the series identifier scheme.

### Compatibility notes

- **Vendor org.** [`STMicroelectronics`](https://github.com/STMicroelectronics) — vendor-direct.
- **Flagship repo (this RFC's anchor).** [`STMicroelectronics/STM32CubeF4`](https://github.com/STMicroelectronics/STM32CubeF4) — license "Other" (mixed), 1.2k stars, Issues enabled, last commit 2026-05-26, **not archived**.
- **Origin.** STMicroelectronics N.V. — HQ Geneva, Switzerland (CH); Franco-Italian operating heritage. Passes US-federal default policy (NATO+EU; STMicroelectronics is the world's largest semiconductor company by some measures and a major US-government supplier).
- **License fit.** Mixed: permissive (BSD-3-Clause, MIT, Apache-2.0) on much of the codebase + proprietary-with-redistribution on some middleware. Cross-citation framing is the recommended posture; per-surface clarification is the ask.
- **Maintainer signal.** Very active (2 days from cutoff on the F4 repo); ST maintains the per-series Cube repos in parallel.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; MCU substrate + mixed-license-surface declaration + Cube-version-pin Spec RFCs queued.
- Reference runtime: cross-citation framing pending license clarification; future `reference/edu-runtime/ST32CubeAdapter` is a candidate **only** if license clarifies cleanly.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Mixed-license posture is the gating fact.** URML can compose with permissive ST code (BSD-3-Clause / MIT cores) but the proprietary middleware boundary needs explicit declaration.
- **Multiple Spec-RFC prerequisites** (MCU substrate, mixed-license-surface, Cube-version-pin).
- **15+ series families** means manifest-side identifier scheme work.
- **STM32CubeF4 is one of many** — engagement on F4 is the anchor; ST may prefer a different per-series surface.

## Alternatives considered

1. **Engage at the broader STMicroelectronics org level.** Considered. Per-flagship-repo engagement is the cleaner shape; broader engagement can follow if F4 maintainers redirect.
2. **Bundle STM32 + sibling MCU-platform RFCs.** Rejected. Per-vendor RFCs.
3. **Skip STM32 entirely as overlapping with PlatformIO (RFC-0176).** Rejected. ST is the chip vendor; PlatformIO is the build pipeline above. Both are URML-fit at different layers.

## Prior art

- [`STMicroelectronics/STM32CubeF4`](https://github.com/STMicroelectronics/STM32CubeF4) — the upstream HAL + middleware (F4 series anchor).
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML manifest pattern.
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0175 (Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md), [RFC-0178 (Zephyr)](0178-zephyr-outreach.md) — sibling MCU-platform / RTOS RFCs that STM32 boards participate in.

## Unresolved questions

For the STMicroelectronics maintainers:

1. **License clarification.** Can the STM32Cube repos get explicit per-surface SPDX declarations? Which subdirectories are BSD-3-Clause / MIT / Apache-2.0 vs proprietary-with-redistribution?
2. **MCU substrate manifest fields.** URML's v0.1 has no `mcu_class: stm32_*` enum entries. Spec RFC queued. Manifest field expectations from ST's perspective (series identifier, Cube version pin, middleware declarations)?
3. **Mixed-license-surface declaration.** Should URML's manifest declare per-component license boundaries explicitly?
4. **Multi-series scope.** Should URML engagement live per-series-repo (F4 / H7 / U5 etc.) or at a higher-level umbrella?
5. **Adapter home.** Cross-citation only (recommended pending license clarification), URML repo (`reference/edu-runtime/STM32CubeAdapter`), or ST-maintained?
6. **Conformance listing.** Would STMicroelectronics consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
7. **Anything else.**

## Implementation note

RFC-0182 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml). Cross-citation framing is the recommended posture pending license clarification.

## How to respond

`STMicroelectronics/STM32CubeF4` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the per-surface license-clarification ask explicit + the multi-series scope question.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license Other / mixed, 1.2k stars, Issues enabled, last commit 2026-05-26 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (mixed-license gate, multiple Spec-RFC prerequisites, 15+ series scheme, anchor-repo selection).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: STMicroelectronics N.V. CH; default policy passes.
- [x] CLAUDE.md compliance check passed.
