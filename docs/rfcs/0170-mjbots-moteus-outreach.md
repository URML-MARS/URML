---
rfc: 0170
title: mjbots Moteus (brushless servo controller for legged robots) integration, request for comment from mjbots maintainers
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

# RFC-0170: mjbots Moteus (brushless servo controller for legged robots) integration, request for comment from mjbots maintainers

## Summary

URML does not yet ship a Moteus manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for mjbots' Moteus brushless servo controllers over [`mjbots/moteus`](https://github.com/mjbots/moteus) (Apache-2.0), and **requests review and feedback from the mjbots maintainers**. No spec change.

This RFC pairs with [RFC-0169 (ODrive Robotics)](0169-odrive-robotics-outreach.md) on URML's actuator-controller substrate Spec-RFC gap. ODrive and Moteus together cover the bulk of US-origin open-hardware brushless motor controllers in robotics; their target use-cases are distinct (ODrive: general-purpose; Moteus: high-bandwidth quadruped / dynamic-legged).

## Motivation

mjbots Robotic Systems makes the Moteus controller line — high-bandwidth (>1kHz position control) brushless servo controllers designed for dynamic legged robots. Repo at [`mjbots/moteus`](https://github.com/mjbots/moteus) (Apache-2.0, 1.2k stars, Issues enabled, last commit `2026-05-25` very active — 3 days from cutoff, **not archived**).

Used widely in:
- MIT Cheetah-class quadrupeds and research successors.
- Stanford Pupper.
- Several open-source bipeds (Berkeley Humanoid Lite lineage).
- Robotic arms requiring high-bandwidth torque control.

URML's quadruped + biped manifest fixtures imply an underlying actuator-controller substrate URML's v0.1 manifest does not yet make first-class. Moteus is the natural Layer-0 declaration for the legged class.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mjbots_moteus_cell.yaml` fixture)

`actuators` block:

| URML field | Maps to Moteus product attribute |
|---|---|
| `name` | Deployment handle (`mjbots_moteus_r4_11`, `mjbots_moteus_n1`) |
| `actuator_class: custom` (`brushless_servo_controller`) | Declares Moteus class is the per-joint controller |
| `actuator_class: custom` (`product_line`) | `moteus_r4_11` / `moteus_n1` / `moteus_x` |
| `actuator_class: custom` (`interface: fdcan` / `usb_serial`) | FD-CAN is the native high-bandwidth interface |
| `actuator_class: custom` (`control_bandwidth_hz`) | Position-control bandwidth declaration |
| `actuator_class: custom` (`firmware_version`) | Moteus firmware pin |

### What URML v0.1 does not yet express for Moteus

1. **Actuator-controller substrate declaration.** Same gap as RFC-0169 (ODrive); shared Spec RFC queued.
2. **High-bandwidth control-loop declaration.** Moteus's distinguishing feature is >1kHz position control; URML's manifest cannot today declare control-bandwidth requirements that legged-robot deployments depend on.
3. **FD-CAN interface declaration.** FD-CAN is a distinct higher-bandwidth variant of standard CAN; URML's manifest cannot today declare which CAN variant is the actuator-bus protocol.

### Compatibility notes

- **Vendor org.** [`mjbots`](https://github.com/mjbots) — vendor-direct (mjbots Robotic Systems).
- **Flagship repo.** [`mjbots/moteus`](https://github.com/mjbots/moteus) — Apache-2.0, 1.2k stars, Issues enabled, last commit 2026-05-25 very active, **not archived**.
- **Origin.** mjbots Robotic Systems, US. Passes US-federal default policy.
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active (3 days from cutoff); vendor-direct commercial entity; Josh Pieper maintainer signal is consistent across the legged-robotics research community.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; actuator-controller substrate Spec RFC queued (shared with RFC-0169 / RFC-0179 / RFC-0180).
- Reference runtime: future `reference/actuator-runtime/MoteusAdapter` is a candidate; companion to ODrive at the high-bandwidth legged class.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Actuator-controller substrate Spec RFC prerequisite** (shared with RFC-0169 / RFC-0179 / RFC-0180).
- **High-bandwidth declaration is novel manifest territory.** Control-bandwidth requirements aren't a v0.1 first-class concept.
- **FD-CAN interface class** is novel.

## Alternatives considered

1. **Bundle Moteus + ODrive into one motor-controller RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; the use-case distinction (general-purpose vs legged high-bandwidth) is informative on its own.
2. **Defer until legged-robotics actuator Spec RFC lands.** Rejected. mjbots maintainer input informs the Spec RFC.
3. **Cross-citation only.** Rejected. Vendor-direct + Apache-2.0 + active + URML-fit is high; full manifest mapping is appropriate.

## Prior art

- [`mjbots/moteus`](https://github.com/mjbots/moteus) — the upstream flagship.
- [RFC-0169 (ODrive Robotics)](0169-odrive-robotics-outreach.md) — sibling brushless-motor-controller RFC.
- [RFC-0009 (Layer-1 mobility specialization)](0009-layer1-mobility-specialization.md) — Spec RFC that added `biped` / `quadruped` mobility types Moteus actuators implement.

## Unresolved questions

For the mjbots maintainers:

1. **Actuator-controller substrate manifest fields.** Same shared question as RFC-0169 — what manifest fields would a Moteus deployment expect?
2. **Control-bandwidth declaration.** Should URML's manifest declare control-loop bandwidth requirements (Hz) for legged-robot deployments?
3. **FD-CAN interface class.** Manifest declaration for FD-CAN vs standard CAN vs USB-serial?
4. **Adapter home.** URML repo (`reference/actuator-runtime/MoteusAdapter`), mjbots-maintained, or external?
5. **Conformance listing.** Would mjbots consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0170 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`mjbots/moteus` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 1.2k stars, Issues enabled, last commit 2026-05-25 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (actuator-controller Spec-RFC prerequisite, control-bandwidth novelty, FD-CAN class).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: mjbots Robotic Systems US; default policy passes.
- [x] CLAUDE.md compliance check passed.
