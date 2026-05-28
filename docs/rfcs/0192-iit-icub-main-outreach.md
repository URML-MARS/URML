---
rfc: 0192
title: IIT iCub (medical-research humanoid) integration, request for comment from robotology maintainers
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

# RFC-0192: IIT iCub (medical-research humanoid) integration

## Summary

URML does not yet ship an iCub manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the iCub humanoid platform over [`robotology/icub-main`](https://github.com/robotology/icub-main) (BSD-3-Clause), and **requests review and feedback from the robotology maintainers**. No spec change.

This RFC is **URML's first medical-research-humanoid engagement**. URML's prior humanoid coverage (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped fixtures per RFC-0009) is commercial-humanoid OEM; iCub is the research-lab-direct medical-relevant humanoid with assistive / prosthetic / rehabilitation focus.

## Motivation

iCub is the open-source humanoid platform from the Italian Institute of Technology (IIT), Genoa. Used worldwide in cognitive-robotics research, assistive-technology development, prosthetic interfaces, and rehabilitation studies. The medical-relevant angle separates iCub from commercial humanoid OEMs: where 1X / Apptronik / Figure / Tesla target labor-augmentation use cases, iCub targets cognitive-development + assistive applications.

Repo at [`robotology/icub-main`](https://github.com/robotology/icub-main) (BSD-3-Clause, 118 stars, Issues enabled, last commit `2026-04-27` active, **not archived**).

URML benefits from documenting the iCub manifest mapping because:

1. **Medical-research humanoid surface URML's prior humanoid coverage didn't reach.** Move-14 RFC-0187 1X Technologies engages the commercial-humanoid OEM layer; iCub is the research-humanoid sibling.
2. **Shares the assistive-application-class declaration gap with Move-14 RFC-0186 Kinova.** Assistive vs industrial vs research deployment-class declaration is needed across multiple URML targets.
3. **YARP middleware composition.** iCub runs on YARP (RFC-0194 sibling); URML's manifest engagement at the platform layer composes with YARP at the substrate layer.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `iit_icub_humanoid_cell.yaml` fixture)

| URML field | Maps to iCub attribute |
|---|---|
| `name` | Specific configuration (`iit_icub3`, `iit_icub_red`, `iit_icub_humanoid`) |
| `mobility.drive_type: biped` | iCub upright bipedal (clean v0.1 fit per RFC-0009) |
| `actuators` | Full-body articulation (head + arms + legs + waist + hands; 53 DoF on iCub3) |
| `cameras` | Stereo head cameras |
| `middleware: custom` (`yarp`) | YARP substrate declaration; cross-link to RFC-0194 |
| `platform_class: custom` (`research_humanoid_with_assistive_angle`) | Distinct from commercial-humanoid platforms |
| `application_class: custom` (`cognitive_research`, `assistive_robotics`, `rehabilitation_research`) | Multi-application class declaration |

### What URML v0.1 does not yet express for iCub

1. **Assistive / prosthetic / rehabilitation application-class declaration.** Shared gap with Move-14 RFC-0186 Kinova (assistive cobot). Spec RFC queued.
2. **YARP middleware substrate declaration.** URML's `reference/ros2-runtime/` is the analog; YARP is a sibling middleware. Spec RFC shared with RFC-0194.
3. **Research-platform-class declaration.** iCub is institutionally maintained (IIT), not vendor-OEM. Manifest field for research-platform distribution-class.
4. **Multi-application platform declaration.** iCub serves cognitive research + assistive robotics + rehabilitation; URML's manifest cannot today declare multi-application platforms cleanly.

### Compatibility notes

- **Research lab / org.** [`robotology`](https://github.com/robotology) — Italian Institute of Technology (IIT), Genoa.
- **Flagship repo.** [`robotology/icub-main`](https://github.com/robotology/icub-main) — BSD-3-Clause, 118 stars, Issues enabled, last commit 2026-04-27, **not archived**.
- **Companion repo.** `robotology/yarp` (LGPL) — middleware iCub runs on; engaged separately via RFC-0194.
- **Origin.** Italian Institute of Technology (IIT), Genoa, Italy. Passes US-federal default policy (NATO+EU).
- **License fit.** BSD-3-Clause on the platform repo cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active institutional research lab; foundational humanoid-research community surface.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; assistive-application-class + YARP-middleware-substrate + research-platform-class + multi-application-platform Spec RFCs queued.
- Reference runtime: future `reference/humanoid-runtime/IcubAdapter` is a candidate; companion to Move-14 RFC-0187 1X at the medical-research-humanoid layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (assistive-application-class, YARP middleware, research-platform-class, multi-application-platform).
- **YARP substrate dependency** — URML's adapter pattern targets ROS 2; YARP adds a sibling substrate URML must declare (per RFC-0194 sibling engagement).
- **53-DoF complexity** — iCub3's full articulation exceeds URML's existing humanoid-fixture detail.

## Alternatives considered

1. **Engage iCub via YARP (RFC-0194) only, treating iCub as a downstream YARP user.** Rejected. iCub is a distinct robot platform; YARP is its substrate. Per-target RFCs at each layer.
2. **Bundle iCub with sibling Move-15 surgical-research RFCs (dVRK).** Rejected. dVRK is telesurgery-class; iCub is humanoid-with-assistive-angle. Structurally different topologies.
3. **Cross-citation only.** Rejected. BSD-3-Clause + active + research-lab-direct + URML-fit-high argues for full manifest mapping.

## Prior art

- [`robotology/icub-main`](https://github.com/robotology/icub-main) — the upstream flagship.
- [`robotology/yarp`](https://github.com/robotology/yarp) — the middleware iCub runs on; engaged via RFC-0194.
- URML's existing humanoid fixtures (apollo_biped, digit_biped, figure_biped, neo_biped, optimus_biped) — commercial-humanoid pattern that iCub extends with the medical-research angle.
- [RFC-0186 (Kinova Robotics)](0186-kinovarobotics-kinova-ros-outreach.md) — sibling assistive-application-class engagement (cobot lineage).
- [RFC-0187 (1X Technologies)](0187-1x-technologies-eve-outreach.md) — sibling commercial-humanoid engagement.

## Unresolved questions

For the robotology maintainers:

1. **Assistive / prosthetic / rehabilitation application-class manifest fields.** URML's v0.1 has no application-class declaration. Spec RFC queued (shared with Move-14 RFC-0186 Kinova). Manifest field expectations from the iCub perspective?
2. **YARP middleware substrate manifest declaration.** Should URML's manifest declare YARP as an alternate substrate to ROS 2, or treat iCub-via-yarp as a single composed declaration?
3. **Research-platform-class declaration.** Should URML's manifest declare institutional research-platform distribution model (vs vendor-OEM commercial)?
4. **53-DoF articulation declaration.** What manifest field granularity makes sense for iCub's full-body DoF inventory?
5. **Adapter home.** URML repo (`reference/humanoid-runtime/IcubAdapter`), IIT-maintained `robotology/icub-urml-bridge`, or both?
6. **Conformance listing.** Would IIT consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0192 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move15.yaml`](../../examples/lighthouses/outreach-move15.yaml).

## How to respond

`robotology/icub-main` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 118 stars, Issues enabled, last commit 2026-04-27 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites, YARP substrate dependency, 53-DoF complexity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Italian Institute of Technology IT Genoa; default policy passes.
- [x] CLAUDE.md compliance check passed.
