---
rfc: 0178
title: Zephyr Project (industrial-grade RTOS for MCU class) integration, request for comment from zephyrproject-rtos maintainers
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

# RFC-0178: Zephyr Project (industrial-grade RTOS for MCU class) integration, request for comment from zephyrproject-rtos maintainers

## Summary

URML does not yet ship a Zephyr-substrate manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Zephyr RTOS over [`zephyrproject-rtos/zephyr`](https://github.com/zephyrproject-rtos/zephyr) (Apache-2.0), and **requests review and feedback from the zephyrproject-rtos maintainers**. No spec change.

This RFC pairs with [RFC-0177 (micro-ROS)](0177-micro-ros-outreach.md): Zephyr is the RTOS layer, micro-ROS is the ROS-2 surface above it. URML's manifest can declare both — Zephyr hosts the firmware, micro-ROS (or other middleware) carries the ROS 2 messages.

## Motivation

The Zephyr Project (Linux Foundation, multi-vendor: Intel, NXP, Nordic, Silicon Labs, ST, Espressif, and dozens more) is the industrial-grade open-source RTOS for resource-constrained devices. Used in robotics applications where bare-metal isn't enough but Linux is too heavy: real-time motor control, sensor fusion at the MCU edge, safety-critical micro-class robots.

Repo at [`zephyrproject-rtos/zephyr`](https://github.com/zephyrproject-rtos/zephyr) (Apache-2.0, 15.4k stars, Issues + Discussions both enabled, last commit `2026-05-28` daily activity, **not archived**).

URML's existing micro-class manifest fixtures (`microbit_edu`) implicitly cover bare-metal MCU firmware. Zephyr is the RTOS substrate URML's manifest can declare for deployments requiring real-time scheduling, multi-task workloads, or industrial certification posture.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `zephyr_rtos_cell.yaml` fixture)

`substrate` block:

| URML field | Maps to Zephyr attribute |
|---|---|
| `substrate.rtos: custom` (`zephyr`) | Declares Zephyr is the RTOS substrate |
| `substrate.zephyr_version` | Zephyr release version pin |
| `substrate.board_target` | Zephyr board-config identifier (`nucleo_f767zi`, `mimxrt1060_evk`, etc.) |
| `substrate.kernel_config: custom` (`scheduler_class`, `tick_rate_hz`) | Real-time scheduling declarations |
| `substrate.tfm_enabled` | Trusted Firmware-M secure-boot flag (industrial / safety posture) |

### What URML v0.1 does not yet express for Zephyr

1. **RTOS substrate declaration.** URML's v0.1 has no `substrate.rtos` field. Spec RFC queued — shared with RFC-0177 micro-ROS (RTOS as host for ROS 2 on MCU).
2. **Real-time scheduling-class declaration.** Zephyr's scheduler-class + tick-rate are deployment-defining parameters URML's manifest cannot today declare.
3. **TF-M (Trusted Firmware-M) secure-boot declaration.** Zephyr's industrial / safety posture often involves TF-M secure-boot; URML's manifest cannot today declare this security-boundary class.
4. **Multi-vendor board catalog scale.** Zephyr supports 700+ boards; URML's manifest needs identifier-mapping conventions (similar to RFC-0176 PlatformIO).

### Compatibility notes

- **Vendor / foundation.** [`zephyrproject-rtos`](https://github.com/zephyrproject-rtos) — Linux Foundation; multi-vendor governance (Intel, NXP, Nordic, Silicon Labs, ST, Espressif, and others).
- **Flagship repo.** [`zephyrproject-rtos/zephyr`](https://github.com/zephyrproject-rtos/zephyr) — Apache-2.0, 15.4k stars, Issues + Discussions both enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** Multi-national (Linux Foundation governance). Passes US-federal default policy.
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; large multi-vendor consortium; Discussions present for design discussion.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; RTOS substrate + scheduling-class + TF-M security-boundary Spec RFCs queued.
- Reference runtime: future `reference/edu-runtime/ZephyrAdapter` is a candidate; companion to RFC-0177 micro-ROS at the RTOS layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (RTOS substrate, scheduling-class, TF-M, board-catalog identifier scheme).
- **Multi-vendor governance** means engagement is foundation-direct rather than single-vendor; coordination overhead.
- **Espressif overlap** — Zephyr has strong ESP32 support, and Espressif is excluded by URML's NDAA Section 889 default policy. The Zephyr engagement doesn't carry the same flag (the foundation is multi-vendor + multi-national), but operator-aware deployments may want manifest-side board-class declarations that distinguish.

## Alternatives considered

1. **Bundle Zephyr + micro-ROS into one RTOS-substrate RFC.** Rejected. Distinct layers / maintainer groups.
2. **Engage individual board vendors instead of Zephyr Project.** Rejected. Foundation-direct engagement is the cleaner shape for multi-vendor RTOS.
3. **Cross-citation only.** Rejected. Foundation-direct + Apache-2.0 + daily activity + URML-fit is high.

## Prior art

- [`zephyrproject-rtos/zephyr`](https://github.com/zephyrproject-rtos/zephyr) — the upstream RTOS.
- [RFC-0177 (micro-ROS)](0177-micro-ros-outreach.md) — sibling MCU-side ROS 2 substrate RFC; Zephyr is one of micro-ROS's host RTOSes.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) — the URML manifest pattern.
- [RFC-0173 (Arduino)](0173-arduino-outreach.md), [RFC-0175 (Pi Pico SDK)](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176 (PlatformIO)](0176-platformio-outreach.md) — sibling Move-13 MCU/build-system RFCs.

## Unresolved questions

For the zephyrproject-rtos maintainers:

1. **RTOS substrate manifest fields.** URML's v0.1 has no `substrate.rtos` declaration. Spec RFC queued. Manifest field expectations from the Zephyr perspective?
2. **Real-time scheduling-class declaration.** Manifest field for scheduler-class + tick-rate + priority-band declarations?
3. **TF-M secure-boot declaration.** Manifest field for industrial / safety posture (TF-M-enabled flag, secure-boot chain class)?
4. **700+ board-catalog identifier scheme.** Should URML's manifest use Zephyr's board-config identifier directly, or a separate URML identifier mapped to it?
5. **Adapter home.** URML repo (`reference/edu-runtime/ZephyrAdapter`), Zephyr-Foundation-maintained `zephyrproject-rtos/zephyr-urml-bridge`, or both?
6. **Conformance listing.** Would the Zephyr maintainers consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0178 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`zephyrproject-rtos/zephyr` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 15.4k stars, Issues + Discussions enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites, multi-vendor coordination, Espressif overlap with NDAA exclusion).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Zephyr Project / Linux Foundation multi-national; default policy passes.
- [x] CLAUDE.md compliance check passed.
