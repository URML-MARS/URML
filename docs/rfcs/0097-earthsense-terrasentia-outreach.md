---
rfc: 0097
title: EarthSense / TerraSentia integration, research-collab proposal
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0097: EarthSense / TerraSentia integration, research-collab proposal

## Summary

URML proposes alignment with the EarthSense / TerraSentia ecosystem (originated at UIUC's Center for Digital Agriculture; commercial spin-out EarthSense Inc.). The engagement surface is the [`TerraSentia` GitHub org](https://github.com/TerraSentia) (7 public repos, 19 followers): SLAM / LiDAR-IMU drivers (`livox_ros_driver2`, `FAST-LIO-SAM`, `terra-lidar-imu-init`) plus controller firmware (`ES-ESC-FW`, `ES-ESC-HW` for the EarthSense electronic speed controller). The ask is **research-collab**: URML's `measure` primitive as a substrate-neutral intent layer above TerraSentia's under-canopy phenotyping data streams. No spec change on URML's side. Sixth Move #7 RFC.

## Motivation

TerraSentia anchors **under-canopy crop phenotyping** in URML's Move #7 wave. The platform is small (under 15 lbs, 11" width; fits between corn rows), originated at UIUC, and the commercial spin-out (EarthSense Inc.) has run substantial validation at scale: a 2024 Corteva partnership across 142 fields and 200k+ maize plots (documented in Nature Communications 2025).

Verified surface (2026-05-26):
- `TerraSentia` GitHub org: 7 public repos, 19 followers.
- Top repos by star count are low (`FAST-LIO-SAM` 1 star, rest 0); the org's public surface is small.
- `terra-lidar-imu-init` carries GPL-2.0; other repos do not surface a license on the listing (URML's RFC asks for clarification).
- ROS-related repos: `livox_ros_driver2` (Livox device driver, ROS + ROS 2 compatible), `FAST-LIO-SAM` (SLAM with pose graph optimisation + loop closing).
- Controller firmware: `ES-ESC-FW` (EarthSense ESC firmware based on VESC4, C), `ES-ESC-HW` (hardware source files).
- Most-active repo: `livox_ros_driver2`, last commit 2026-05-06.
- Hybrid academic / commercial PI structure: UIUC plant-science research origin + EarthSense Inc. commercial spin-out.

URML's specific value for EarthSense / TerraSentia:
- **`measure` primitive as substrate-neutral intent above SLAM + sensor streams.** A URML program describing "scout the maize trial plot and record stand-count + plant-height every 10cm" decomposes into `move_to(...)` + `measure(stand_count, ...)` + `wait_for(distance, 10cm)`. The TerraSentia ROS drivers consume those primitives at the substrate layer.
- **Cross-platform retargetability.** A URML phenotyping program written for TerraSentia retargets to a future agricultural drone ([RFC-0093 (Sentera)](0093-sentera-outreach.md)) or to a four-wheel-steering platform ([RFC-0096 (INRAE Romea)](0096-inrae-romea-outreach.md)) by manifest swap. The substrate-neutral story is exactly what cross-trial phenotyping research benefits from.
- **Bridge between academic research and commercial deployment.** The UIUC research origin + EarthSense Inc. commercial spin-out structure is the same hybrid URML's Move #6 RFC-0088 navigated for Imperial PRL (academic + commercial entity sharing a name). The lesson: engage both surfaces honestly, expect the academic side to be the substantive partner.

## Detailed design (light, research-collab)

URML proposes:

1. **Documented cross-citation in URML's `reference/agriculture-runtime/` README.** TerraSentia ROS drivers + SLAM as a candidate substrate target for URML's phenotyping-focused `measure` primitives. No adapter shipping in URML's `reference/` (license clarity needed first; one repo is GPL-2.0).
2. **Cross-link to RFC-0093 (Sentera)** + **RFC-0067 (FarmBot)** + **RFC-0092 (Acorn)**: aerial (Sentera) + Cartesian (FarmBot) + open-source rover (Acorn) + research phenotyping (TerraSentia) form a four-surface ag-robotics inventory for URML.
3. **Research-publication cross-link.** TerraSentia's Nature Communications 2025 publication (Corteva, 142 fields, 200k+ maize plots) is the kind of large-scale validation a URML-compatible phenotyping pipeline could publish against in future work.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No URML code.

## Drawbacks

- **Proposal-only.**
- **Thin public GitHub footprint.** 7 repos, mostly 0-star. The substantive engagement surface is academic publications + the EarthSense Inc. commercial channel rather than GitHub Issues. URML's RFC documents this honestly (similar to RFC-0089 Oxford ORI's thin-GitHub posture).
- **License mix unclear.** `terra-lidar-imu-init` is GPL-2.0; other repos do not surface a license. URML's RFC asks the maintainers to clarify license posture before any URML-side code work.
- **Hybrid academic / commercial PI structure.** Engagement should be honest about which surface URML targets (URML's preference: the academic research code + public datasets, not the proprietary commercial platform).
- **No `pr_assets` / public dataset repo visible.** URML's RFC asks whether the Nature Communications 2025 datasets are open or proprietary.

## Alternatives considered

1. **Ship a `TerraSentiaAdapter` in URML's `reference/`.** Rejected. License clarity needed first; substantive engagement comes before adapter code.
2. **Fold TerraSentia into RFC-0067 (FarmBot) or RFC-0092 (Acorn) as another ag platform.** Rejected; different morphology (under-canopy autonomous rover vs Cartesian gantry vs solar-powered above-canopy rover) and different audience (plant-breeding phenotyping research vs DIY raised-bed farming vs open-source over-the-row).

## Prior art

- `TerraSentia` GitHub org (7 public repos, 19 followers).
- `TerraSentia/livox_ros_driver2`, `FAST-LIO-SAM`, `terra-lidar-imu-init` (GPL-2.0), `ES-ESC-FW`, `ES-ESC-HW`.
- UIUC Center for Digital Agriculture (academic origin).
- EarthSense Inc. (commercial spin-out).
- Corteva + EarthSense Nature Communications 2025 publication (142 fields, 200k+ maize plots).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md), [RFC-0093 (Sentera)](0093-sentera-outreach.md): agriculture-vertical precedents.
- [RFC-0088 (Imperial PRL)](0088-imperial-personal-robotics-outreach.md): hybrid academic + commercial entity precedent.
- [RFC-0089 (Oxford ORI)](0089-oxford-ori-outreach.md): thin-GitHub-footprint precedent.

## Unresolved questions

For the TerraSentia maintainers + EarthSense Inc.:

1. **License posture.** Could you confirm the license on `livox_ros_driver2`, `FAST-LIO-SAM`, `ES-ESC-FW`, `ES-ESC-HW`?
2. **Engagement surface.** Which surface is the right one for substantive URML cross-citation: GitHub Issues on a specific repo, the academic UIUC contact channel, the EarthSense Inc. developer-relations team?
3. **Nature Communications 2025 datasets.** Are the trial datasets open or proprietary?
4. **Cross-platform retargetability.** Is there interest in documenting URML's substrate-neutral phenotyping path across TerraSentia + ag-drone (Sentera) + ag-rover (Acorn / AgriCruiser)?
5. **Agriculture-profile co-design.** RFC-0067 raised this; EarthSense + UIUC research is a candidate phenotyping-focused input.
6. **Conformance lane.** Open to a URML conformance line on the `livox_ros_driver2` README or earthsense.co?
7. **Anything else.**

## Implementation note

RFC-0097 ships as a single RFC document PR. No code in this PR. Research-collab framing; no URML-side adapter due to license-clarity needs. Sixth Move #7 RFC. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`TerraSentia/livox_ros_driver2` is the most-recently-updated repo (last commit 2026-05-06, verified 2026-05-26). URML's planned channel: open a single Issue on `TerraSentia/livox_ros_driver2` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to the EarthSense Inc. team via earthsense.co.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Hybrid academic / commercial PI structure surfaced honestly.
- [x] Thin GitHub footprint acknowledged.
- [x] License-clarity gap surfaced as the gating item before adapter code.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, thin footprint, license clarity, hybrid structure, dataset access unclear).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
