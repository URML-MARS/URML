---
rfc: 0152
title: NUS Clear Lab Octopi (octopus-inspired soft-robotics) integration, request for comment from clear-nus maintainers
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

# RFC-0152: NUS Clear Lab Octopi (octopus-inspired soft-robotics) integration, request for comment from clear-nus maintainers

## Summary

URML does not yet ship an Octopi manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest cross-citation for Octopi — octopus-inspired soft-robotics research from National University of Singapore Clear Lab — over [`clear-nus/octopi`](https://github.com/clear-nus/octopi), and **requests review and feedback from the clear-nus maintainers**. **License clarification ask:** no SPDX license is visible on the repo; an explicit OSI declaration is the gating ask. No spec change.

**This is URML's first soft-robotics RFC.** The contribution is the **soft-body actuator class** schema-extension question — URML's `mobility.drive_type` and `actuators` vocabulary are rigid-body-centric.

## Motivation

`clear-nus/octopi` is the Clear Lab (NUS) octopus-inspired soft-robotics research surface. License TBD (clarification ask), 76 stars, Issues enabled, last commit `2026-05-24` very active (4 days from cutoff 2026-05-28), **not archived**. National University of Singapore = passes US-federal default policy (NATO+ allied; SG is a strategic US partner).

Soft-robotics is a structural URML schema gap. URML's `mobility.drive_type` enum is rigid-body-centric (differential / omnidirectional / ackermann / tracked / biped / quadruped / manipulator_base / multirotor / fixed_wing / vtol / underwater_thrusters). Soft-body actuators (continuum manipulators, pneumatic networks, octopus-like tentacles) don't fit this vocabulary. A Spec RFC adding `soft_body` mobility class and `pneumatic_network` / `continuum_manipulator` actuator classes is queued; Octopi is the natural research input.

Cross-citation framing is recommended given the license-clarification gate and soft-body schema novelty.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `nus_octopi_cell.yaml` fixture, cross-citation framing)

| URML field | Maps to Octopi attribute |
|---|---|
| `name` | Deployment handle (`nus_octopi_default`) |
| `mobility.drive_type: custom` (`soft_body_continuum`) | Declares soft-body continuum-manipulator mobility (v0.1 enum has no `soft_body`) |
| `actuators: custom` (`pneumatic_network`) | Declares pneumatic-network actuator class (v0.1 actuator vocabulary doesn't include this) |
| `sensors` block | Octopi's proprioceptive sensing inside the continuum body |

### What URML v0.1 does not yet express for Octopi

1. **Soft-body mobility class.** URML's `mobility.drive_type` enum is rigid-body-centric. Spec RFC adding `soft_body_continuum` queued.
2. **Pneumatic-network actuator class.** URML's actuator vocabulary is electric-motor-centric. Spec RFC adding `pneumatic_network` queued.
3. **Continuum-manipulator kinematics.** URML's kinematics vocabulary assumes discrete joints; continuum manipulators have continuous deformation. Schema-extension needed.
4. **License clarification.** No SPDX visible upstream blocks Apache-2.0 downstream reuse.

### Compatibility notes

- **Vendor / lab.** [`clear-nus`](https://github.com/clear-nus) — Clear Lab, National University of Singapore.
- **Flagship repo.** [`clear-nus/octopi`](https://github.com/clear-nus/octopi) — license TBD (clarification ask), 76 stars, Issues enabled, last commit 2026-05-24 (4 days), **not archived**.
- **Origin.** National University of Singapore, Singapore (SG). Passes US-federal default policy (SG = NATO+ allied / strategic US partner).
- **License fit.** Pending clarification.
- **Maintainer signal.** Very active (4 days from cutoff); modest stars; research surface.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; soft-body mobility + pneumatic-network actuator + continuum-manipulator kinematics Spec RFCs queued.
- Reference runtime: cross-citation framing pending license + schema-extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate.**
- **Multiple Spec-RFC prerequisites** (soft-body mobility + pneumatic-network actuator + continuum-manipulator kinematics).
- **Novel domain.** Soft-robotics is a structural URML gap; the engagement is partly URML-self-correction (the manifest vocabulary is implicitly rigid-body-centric).
- **Modest 76 stars.** Light-touch engagement.

## Alternatives considered

1. **Defer Octopi until soft-body Spec RFCs land.** Rejected. Octopi maintainer input shapes the Spec RFCs.
2. **Bundle Octopi with broader soft-robotics RFC.** Rejected. URML has no other soft-robotics outreach target identified yet; Octopi is the first.
3. **Cross-citation only with no manifest mapping.** Considered. The manifest mapping is the schema-exploration artifact maintainers can evaluate.

## Prior art

- [`clear-nus/octopi`](https://github.com/clear-nus/octopi) — the upstream repo.
- URML's existing soft-robotics manifest fixture (`soft_robotics_compliant_cell.yaml`) — single existing soft-robotics fixture; no upstream engagement until this RFC.
- [RFC-0009 (Layer-1 mobility specialization)](0009-layer1-mobility-specialization.md) — the rigid-body-centric mobility-class Spec RFC that soft-body extends.

## Unresolved questions

For the clear-nus octopi maintainers:

1. **License clarification.** Can `clear-nus/octopi` get an explicit OSI license declaration?
2. **Soft-body mobility class manifest fields.** URML's v0.1 mobility enum is rigid-body-centric. Spec RFC adding `soft_body_continuum` queued. Manifest field expectations (DOF, continuum-segment count, control-input class)?
3. **Pneumatic-network actuator declaration.** URML's actuator vocabulary is electric-motor-centric. Spec RFC adding `pneumatic_network` queued. Manifest field expectations?
4. **Continuum-manipulator kinematics.** Should URML's manifest declare continuum kinematics class, and at what granularity?
5. **Bridge home.** Cross-citation only (recommended), URML repo, or NUS-maintained?
6. **Conformance listing.** Would Clear Lab consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
7. **Anything else.**

## Implementation note

RFC-0152 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml). **Completes the 15 Move-11 engageable RFCs.**

## How to respond

`clear-nus/octopi` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license TBD, 76 stars, Issues enabled, last commit 2026-05-24, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license gate, multiple Spec-RFC prerequisites, novel domain, modest stars).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: National University of Singapore SG; default policy passes.
- [x] CLAUDE.md compliance check passed.
