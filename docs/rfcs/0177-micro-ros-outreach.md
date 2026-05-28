---
rfc: 0177
title: micro-ROS (ROS 2 on MCU substrate) integration, request for comment from micro-ROS maintainers
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

# RFC-0177: micro-ROS (ROS 2 on MCU substrate) integration, request for comment from micro-ROS maintainers

## Summary

URML does not yet ship a micro-ROS manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for micro-ROS — ROS 2 on microcontroller substrates — over [`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup) (Apache-2.0), and **requests review and feedback from the micro-ROS maintainers**. No spec change.

**This is the structural bridge URML's substrate story needs at the MCU edge.** URML's existing `reference/ros2-runtime/` adapter composes with full ROS 2 on host-class robots; micro-ROS extends that surface down to MCU-class targets URML's `microbit_edu` fixture (RFC-0018) and Move-13 MCU + maker RFCs (RFC-0172 through RFC-0176) depend on.

## Motivation

micro-ROS is the multi-vendor foundation-project (Linux Foundation / ROS 2 ecosystem, with Eclipse Foundation governance backing) bringing ROS 2 nodes to MCU substrates: ESP32, STM32, Teensy, RP2040, Zephyr-supported boards, etc. The natural URML composition shape: URML's adapter speaks ROS 2 to a micro-ROS agent on the host, which transports messages to MCU-side ROS 2 nodes — letting URML's typed primitive vocabulary dispatch onto firmware-class robots with the same adapter pattern URML uses for host-class robots.

Repo at [`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup) (Apache-2.0, 493 stars, Issues enabled, last commit `2026-05-27` very active — 1 day from cutoff, **not archived**).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `micro_ros_cell.yaml` fixture)

`substrate` block:

| URML field | Maps to micro-ROS attribute |
|---|---|
| `substrate.framework: custom` (`micro_ros`) | Declares micro-ROS is the MCU-side ROS 2 substrate |
| `substrate.host_agent: micro_ros_agent` | Declares the micro-ROS agent runs on the host bridging to ROS 2 |
| `substrate.target_rtos: custom` (`freertos` / `nuttx` / `zephyr` / `bare_metal`) | Which RTOS hosts micro-ROS on the MCU |
| `substrate.mcu_class` | Cross-references RFC-0172 through RFC-0176 MCU board-class declarations |
| `substrate.qos_class` | micro-ROS QoS profile (DDS-XRCE protocol) |

### What URML v0.1 does not yet express for micro-ROS

1. **MCU-side ROS 2 substrate declaration.** URML's existing `reference/ros2-runtime/` adapter assumes host-class ROS 2; the MCU side via micro-ROS is structurally distinct. Spec RFC queued.
2. **Multi-RTOS substrate declaration.** micro-ROS runs on FreeRTOS, NuttX, Zephyr, or bare-metal; URML's manifest cannot today declare the RTOS substrate.
3. **DDS-XRCE QoS class declaration.** micro-ROS uses DDS-XRCE (eXtremely Resource Constrained Environments) — a different QoS surface from standard DDS; URML's manifest cannot today declare DDS-XRCE-specific profiles.

### Compatibility notes

- **Vendor / foundation.** [`micro-ROS`](https://github.com/micro-ROS) — multi-vendor consortium under the ROS 2 / Linux Foundation umbrella.
- **Flagship repo.** [`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup) — Apache-2.0, 493 stars, Issues enabled, last commit 2026-05-27, **not archived**.
- **Origin.** Multi-national (Linux Foundation / Eclipse Foundation governance). Passes US-federal default policy (foundation-direct + multi-vendor + Apache-2.0).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active (1 day from cutoff); foundation-direct.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; MCU-side ROS 2 substrate + multi-RTOS + DDS-XRCE QoS Spec RFCs queued.
- Reference runtime: future `reference/edu-runtime/MicroRosAdapter` is a strong candidate — composes with the existing `reference/ros2-runtime/` host adapter at the MCU edge.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Three Spec-RFC prerequisites** (MCU-side ROS 2 substrate, multi-RTOS class, DDS-XRCE QoS).
- **Host-side micro-ROS agent dependency.** URML's deployment-time topology must declare where the agent runs.

## Alternatives considered

1. **Bundle micro-ROS + Zephyr (RFC-0178) into one RTOS-substrate RFC.** Rejected. micro-ROS is the ROS-2 surface; Zephyr is the RTOS. Different layers, different maintainer groups.
2. **Engage individual micro-ROS RMW implementations (rmw_microxrcedds, rmw_uxrce_dds).** Rejected. Per-flagship engagement at the foundation level is the cleaner shape.
3. **Cross-citation only.** Rejected. Foundation-direct + Apache-2.0 + very active + URML-fit is very high.

## Prior art

- [`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup) — the upstream flagship.
- URML's existing `reference/ros2-runtime/` — the host-side ROS 2 adapter micro-ROS extends downward.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md), [RFC-0172](0172-microbit-foundation-outreach.md), [RFC-0173](0173-arduino-outreach.md), [RFC-0174](0174-adafruit-circuitpython-outreach.md), [RFC-0175](0175-raspberry-pi-pico-sdk-outreach.md), [RFC-0176](0176-platformio-outreach.md) — MCU manifest pattern + per-platform RFCs that micro-ROS composes with.
- [RFC-0178 (Zephyr Project)](0178-zephyr-outreach.md) — sibling RTOS-substrate RFC.

## Unresolved questions

For the micro-ROS maintainers:

1. **MCU-side ROS 2 substrate manifest fields.** URML's v0.1 has no `substrate.framework: micro_ros` declaration. Spec RFC queued. Manifest field expectations from the micro-ROS perspective?
2. **Multi-RTOS substrate declaration.** Should URML's manifest declare which RTOS (FreeRTOS / NuttX / Zephyr / bare-metal) hosts micro-ROS on the MCU?
3. **DDS-XRCE QoS class.** Manifest field expectations for resource-constrained QoS profiles?
4. **Host-side agent topology.** Should URML's manifest declare where the micro-ROS agent runs (companion-computer vs sidecar vs host-process)?
5. **Adapter home.** URML repo (`reference/edu-runtime/MicroRosAdapter` or `reference/micro-ros-runtime/`), micro-ROS-maintained `micro-ROS/micro_ros_urml_bridge`, or both?
6. **Conformance listing.** Would the micro-ROS maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0177 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`micro-ROS/micro_ros_setup` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the URML-extends-ROS-2-to-MCU-edge framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 493 stars, Issues enabled, last commit 2026-05-27 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (three Spec-RFC prerequisites, host-side agent dependency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation multi-national; default policy passes.
- [x] CLAUDE.md compliance check passed.
