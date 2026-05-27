---
rfc: 0121
title: Robotous (RFT-series force/torque sensors) integration, request for comment from ROBOTOUS maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-27
updated: 2026-05-27
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

# RFC-0121: Robotous (RFT-series force/torque sensors) integration, request for comment from ROBOTOUS maintainers

## Summary

URML does not yet ship a Robotous manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Robotous's RFT-series 6-axis force/torque sensors (UART + EtherCAT variants) over [`ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model`](https://github.com/ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model) (MIT, fresh vendor org Feb 2026), and **requests review and feedback from the ROBOTOUS maintainers**. No spec change.

**This is URML's first force/torque vendor RFC** (ATI and Bota Systems are existing URML fixtures but were never engaged through an outreach RFC).

## Motivation

`ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model` is a fresh vendor-direct GitHub presence (org created February 2026): MIT-licensed, ROS 2 driver in EtherCAT variant + UART variant, active commits (last commit 2026-03-04). Robotous (South Korea) makes capacitance-based 6-axis F/T sensors targeted at collaborative arms and unmanned vehicles.

URML's existing F/T-sensor coverage is fixture-only (`ati_ft_cell.yaml`, `bota_ft_cell.yaml`). Robotous is the first F/T vendor URML engages directly through an outreach RFC. Per the Move-10 verification pass: the vendor org is new enough that URML's engagement may meaningfully shape their public-engagement posture going forward, so light-touch framing is the right register.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `robotous_rft_cell.yaml` fixture)

`Sensor` block:

| URML field | Maps to Robotous product attribute |
|---|---|
| `name: force_torque` (Sensor) | RFT-series 6-axis F/T sensor |
| `measurement_type: pressure` (partial fit; F/T isn't strictly pressure) | Force components (Fx, Fy, Fz) + torque (Tx, Ty, Tz) |
| `measurement_type: custom` (force_torque_6axis) | The honest declaration — v0.1 has no `force_torque` type |
| `units` | `N` (force), `Nm` (torque) per channel |

### What URML v0.1 does not yet express for Robotous

1. **First-class force/torque measurement_type.** ATI / Bota / Robotous all share this gap; URML's v0.1 has `pressure` (1D) but no native 6-axis F/T type. Spec RFC queued.
2. **Transport-protocol declaration.** Robotous RFT-series ships UART + EtherCAT variants; URML's manifest could declare which transport a deployment uses for grasp-feedback and contact-detection.

### Compatibility notes

- **Vendor org.** [`ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model`](https://github.com/ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model) (MIT), plus a UART variant repo in the same org.
- **Origin.** Robotous, South Korea (KR). Passes US-federal default policy (NATO/Korea allied).
- **License fit.** MIT; cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Fresh vendor org (created Feb 2026); engagement during this window may shape Robotous's public-engagement posture; light-touch register is appropriate.

### Spec / validator / reference-runtime / conformance changes

- None in this RFC. Future `reference/perception-runtime/` or `reference/sensor-runtime/` package with `RobotousFtAdapter`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Force/torque measurement_type Spec RFC is a prerequisite for clean manifest declaration.** v0.1 `custom` escape-hatch is honest but not adapter-grade.
- **Fresh vendor org.** Engagement turnaround may be slow as Robotous builds their public-engagement posture; light-touch register expected.

## Alternatives considered

1. **Bundle Robotous + ATI + Bota into one F/T-sensor RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; ATI / Bota are fixture-only at URML today and engaging them is a separate decision.
2. **Defer Robotous until F/T measurement_type Spec RFC lands.** Rejected. Robotous feedback informs that Spec RFC.

## Prior art

- [`ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model`](https://github.com/ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model) — the upstream driver.
- URML's existing F/T fixtures: `ati_ft_cell.yaml`, `bota_ft_cell.yaml`.
- [RFC-0013 (industrial primitives)](0013-industrial-layer2-primitives.md) — `grasp` / `release` / `pick_from` semantics that F/T feedback informs.

## Unresolved questions

For the ROBOTOUS maintainers:

1. **Force/torque measurement_type shape.** URML's v0.1 enum has no `force_torque` type; would a Spec RFC adding it (parallel to RFC-0039's `point_cloud`) be useful from Robotous's perspective, or is the `custom` escape-hatch sufficient for now?
2. **Transport-protocol declaration.** Should URML's manifest declare UART vs EtherCAT as a transport-class capability for the F/T sensor?
3. **Adapter home.** When the URML-side `RobotousFtAdapter` ships, should it live in URML's `reference/sensor-runtime/`, in a Robotous-maintained `ROBOTOUS/robotous-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo.
4. **Conformance listing.** Would Robotous consider a README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

## Implementation note

RFC-0121 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (MIT, fresh vendor org Feb 2026, last commit 2026-03-04, Issues enabled).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, F/T type Spec-RFC prerequisite, fresh-vendor pacing).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Robotous KR; default policy passes.
- [x] CLAUDE.md compliance check passed.
