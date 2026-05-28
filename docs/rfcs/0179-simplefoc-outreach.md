---
rfc: 0179
title: SimpleFOC (community FOC motor-control library) integration, request for comment from simplefoc maintainers
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

# RFC-0179: SimpleFOC (community FOC motor-control library) integration, request for comment from simplefoc maintainers

## Summary

URML does not yet ship a SimpleFOC manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the SimpleFOC community FOC motor-control library over [`simplefoc/Arduino-FOC`](https://github.com/simplefoc/Arduino-FOC) (MIT), and **requests review and feedback from the SimpleFOC maintainers**. No spec change.

This RFC complements [RFC-0169 (ODrive)](0169-odrive-robotics-outreach.md), [RFC-0170 (Moteus)](0170-mjbots-moteus-outreach.md), and [RFC-0180 (VESC)](0180-vesc-bldc-outreach.md) at the **community library layer**. Where ODrive / Moteus / VESC are vendor-direct hardware + firmware, SimpleFOC is the community-maintained FOC reference library that runs on commodity MCUs.

## Motivation

SimpleFOC is the canonical open-source field-oriented-control library for Arduino-class MCUs. It abstracts the FOC math + driver-IC interface, letting maker / educational / research deployments build custom motor-control boards without writing FOC from scratch. Repo at [`simplefoc/Arduino-FOC`](https://github.com/simplefoc/Arduino-FOC) (MIT, 2.8k stars, Issues + Discussions both enabled, last commit `2026-05-22` very active — 6 days from cutoff, **not archived**).

The URML-fit framing: SimpleFOC is the FOC implementation layer URML's manifest declares for **maker / educational** brushless deployments where commercial controllers (ODrive, Moteus) are overspec'd or out of budget. Same actuator-controller Spec-RFC gap as the sibling vendor-direct controllers.

Tier B framing because SimpleFOC is community-maintained (vendor-neutral) — URML's outreach is vendor-direct first; community libraries are cross-citation depth by default.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `simplefoc_cell.yaml` fixture)

`actuators` block:

| URML field | Maps to SimpleFOC attribute |
|---|---|
| `name` | Deployment handle (`simplefoc_default_axis0`) |
| `actuator_class: custom` (`foc_library`) | Declares SimpleFOC is the FOC implementation library on the MCU |
| `actuator_class: custom` (`mcu_class`) | Which MCU hosts SimpleFOC (Arduino / STM32 / ESP32 / etc.) |
| `actuator_class: custom` (`driver_ic_class`) | Which driver IC the library drives (DRV8302, L6234, etc.) |
| `actuator_class: custom` (`sensor_class`) | Encoder / Hall / sensorless feedback class |

### What URML v0.1 does not yet express for SimpleFOC

1. **FOC-library actuator-class declaration.** URML's v0.1 has no `foc_library` actuator class. Spec RFC queued — same shared gap as RFC-0169 / RFC-0170 / RFC-0171 / RFC-0180.
2. **MCU-host-of-library declaration.** SimpleFOC runs on the MCU; URML's manifest needs to declare the MCU class hosting the library and the driver-IC class it's driving.
3. **Community-vs-vendor library distinction.** URML's actuator-class enum doesn't today distinguish community vs vendor-direct libraries; the engagement-classification matters operationally.

### Compatibility notes

- **Vendor org / community.** [`simplefoc`](https://github.com/simplefoc) — community-maintained (vendor-neutral).
- **Flagship repo.** [`simplefoc/Arduino-FOC`](https://github.com/simplefoc/Arduino-FOC) — MIT, 2.8k stars, Issues + Discussions both enabled, last commit 2026-05-22 active, **not archived**.
- **Origin.** Community (multi-national contributors). Project leads not single-country-domiciled.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active community surface; Discussions present for design discussion.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; FOC-library actuator-class Spec RFC queued (shared with the sibling Move-13 motor-controller RFCs).
- Reference runtime: cross-citation framing recommended; future `reference/actuator-runtime/SimpleFOCAdapter` is a candidate **only** if engagement settles on adapter depth.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Community-vs-vendor library distinction** is novel manifest territory.
- **FOC-library actuator-class Spec RFC prerequisite.**
- **MCU-host-of-library + driver-IC + sensor-class** three-axis declaration is more complex than the vendor-direct flagship pattern.

## Alternatives considered

1. **Bundle SimpleFOC with vendor-direct motor-controller RFCs.** Rejected. Community-vs-vendor distinction is informative; per-target RFCs let conversation thread per maintainer group.
2. **Skip SimpleFOC as overlapping with ODrive.** Rejected. SimpleFOC's library-on-MCU shape is structurally different from ODrive's vendor-direct hardware controller; both are URML-fit.
3. **Cross-citation only with no manifest mapping.** Considered. Tier B framing keeps cross-citation as the recommended posture while still presenting a manifest sketch for maintainer evaluation.

## Prior art

- [`simplefoc/Arduino-FOC`](https://github.com/simplefoc/Arduino-FOC) — the upstream library.
- [RFC-0169 (ODrive)](0169-odrive-robotics-outreach.md), [RFC-0170 (Moteus)](0170-mjbots-moteus-outreach.md), [RFC-0180 (VESC)](0180-vesc-bldc-outreach.md) — sibling motor-controller RFCs.
- [RFC-0173 (Arduino)](0173-arduino-outreach.md) — Move-13 MCU platform where SimpleFOC commonly runs.

## Unresolved questions

For the simplefoc maintainers:

1. **FOC-library actuator-class manifest fields.** URML's v0.1 has no `foc_library` actuator class. Spec RFC queued. Manifest field expectations from the SimpleFOC perspective?
2. **MCU-host + driver-IC + sensor-class declaration.** Three-axis declaration — what granularity is useful?
3. **Community-vs-vendor library distinction.** Should URML's manifest declare this as a separate field, or implicit via the library identifier?
4. **Adapter home.** Cross-citation only (recommended), URML repo (`reference/actuator-runtime/SimpleFOCAdapter`), or community-maintained `simplefoc/Arduino-FOC-urml`?
5. **Conformance listing.** Would the simplefoc maintainers consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

## Implementation note

RFC-0179 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`simplefoc/Arduino-FOC` has Issues + Discussions both enabled. Discussions is the preferred surface for design-discussion. URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 2.8k stars, Issues + Discussions enabled, last commit 2026-05-22 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (community-vs-vendor distinction novelty, FOC-library Spec-RFC prerequisite, three-axis declaration complexity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: community (multi-national); passes default policy.
- [x] CLAUDE.md compliance check passed.
