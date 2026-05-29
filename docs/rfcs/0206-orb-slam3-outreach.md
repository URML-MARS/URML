---
rfc: 0206
title: ORB-SLAM3 (visual-SLAM canonical reference) cross-citation, request for comment from UZ-SLAMLab maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0206: ORB-SLAM3 (visual-SLAM canonical reference) cross-citation

## Summary

URML's perception manifest does not yet declare a visual-SLAM substrate. This RFC documents the proposed URML v0.1 capability-manifest mapping for ORB-SLAM3 as the canonical visual-SLAM reference, engaged at the University of Zaragoza SLAM Lab layer via [`UZ-SLAMLab/ORB_SLAM3`](https://github.com/UZ-SLAMLab/ORB_SLAM3) (GPL-3.0), and **requests review and feedback from the UZ-SLAMLab maintainers**. No spec change.

**GPL-3.0 → cross-citation framing.** URML's Apache-2.0 reference runtimes cannot embed GPL-3.0 ORB-SLAM3 source. The engagement is at the API / protocol boundary (manifest-level declaration + adapter via a separately-licensed bridge), not by source-level reuse. This framing is explicit throughout the RFC.

## Motivation

ORB-SLAM3 is the canonical visual-SLAM reference (monocular, stereo, RGB-D, visual-inertial). Production robotics systems frequently use ORB-SLAM3 in research and prototype phases; URML's manifest needs to be able to declare it as the visual-SLAM substrate without GPL-3.0 contamination of URML's adapter source.

Repo at [`UZ-SLAMLab/ORB_SLAM3`](https://github.com/UZ-SLAMLab/ORB_SLAM3) (GPL-3.0, 8.7k stars, Issues enabled, last commit `2026-05-28`, **not archived**). University of Zaragoza SLAM Lab (Spain).

URML benefits from documenting the engagement because:

1. **Visual-SLAM substrate is a real production case.** Visual + visual-inertial SLAM is the dominant modality for camera-only and consumer-grade robots; URML cannot ignore this substrate class.
2. **GPL-3.0 cross-citation discipline.** URML's Apache-2.0 stance forces the engagement to declare clean license boundaries. The pattern is well-established (see how Apache-2.0 distributions cite GPL-3.0 dependencies). This RFC documents the discipline upstream so the engagement is unambiguous.
3. **Visual-SLAM manifest-field shape.** Monocular / stereo / RGB-D / visual-inertial modes require URML's manifest to express camera-topology and inertial-fusion intent.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `orb_slam3_stereo_cell.yaml` fixture, GPL-3.0 cross-citation)

| URML field | Maps to ORB-SLAM3 attribute |
|---|---|
| `name` | Deployment handle (`orb_slam3_stereo_visual_inertial`) |
| `perception.slam_substrate: orb_slam3` | URML's visual-SLAM enum value |
| `perception.slam_mode: monocular` / `stereo` / `rgbd` / `monocular_inertial` / `stereo_inertial` | ORB-SLAM3 operation mode |
| `perception.camera_config_yaml` | ORB-SLAM3 camera-calibration YAML reference |
| `perception.vocabulary_path` | ORB vocabulary file reference (BoW dictionary) |
| `perception.imu_topic` | IMU input topic for visual-inertial modes |
| `pose_frame.world_frame` | ORB-SLAM3 world-frame convention |

### What URML v0.1 does not yet express for ORB-SLAM3

1. **SLAM-mode enumeration covering all five ORB-SLAM3 modes** (monocular / stereo / RGB-D / monocular-inertial / stereo-inertial).
2. **Camera-calibration YAML reference convention.** ORB-SLAM3 ships with its own calibration format; URML's manifest could declare reference path.
3. **Vocabulary-file declaration.** BoW vocabulary file is multi-MB; URML's manifest could declare path + checksum hint.
4. **GPL-3.0 cross-citation declaration in the manifest itself.** Manifest should mark the visual-SLAM substrate as GPL-3.0-bound so downstream packaging is unambiguous.

### Compatibility notes

- **Vendor org.** [`UZ-SLAMLab`](https://github.com/UZ-SLAMLab) — University of Zaragoza SLAM Lab (Spain).
- **Engagement repo.** [`UZ-SLAMLab/ORB_SLAM3`](https://github.com/UZ-SLAMLab/ORB_SLAM3) — GPL-3.0, 8.7k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `UZ-SLAMLab/ORB_SLAM2` (prior generation) — the lab's SLAM family.
- **Origin.** Spain (NATO-allied); academic. Passes US-federal default policy as an allied-academic-origin substrate.
- **License fit.** GPL-3.0 → cross-citation only at API boundary; URML's Apache-2.0 adapter source cannot embed ORB-SLAM3 source.
- **Maintainer signal.** Active commits; the canonical visual-SLAM reference.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; SLAM-mode enumeration + camera-calibration reference + vocabulary-path + GPL-3.0 cross-citation declaration Spec RFCs queued.
- Reference runtime: no in-repo adapter; URML cites ORB-SLAM3 at the API boundary; adapter (if any) lives in a separately-licensed companion package.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 → cross-citation only.** No in-repo URML adapter; any working bridge lives in a separately-licensed companion package.
- **Five-mode enumeration complexity** — ORB-SLAM3's five operation modes are a real manifest-shape burden.
- **Academic-vs-production-maintainer cadence** — UZ-SLAMLab is an academic lab; sustained engagement cadence is non-trivial.

## Alternatives considered

1. **Skip ORB-SLAM3; declare only Apache-2.0-licensed SLAM substrates (Cartographer).** Rejected. ORB-SLAM3 is the canonical visual-SLAM reference; ignoring it would bias URML's manifest toward Apache-only substrates.
2. **Engage with academic citation only, no GitHub Issue.** Rejected. The GitHub Issue surface is the active maintainer channel; an Issue is the right first-contact.
3. **Bundle ORB-SLAM3 with Stella VSLAM in a single visual-SLAM RFC.** Rejected. Different governance (academic lab vs community fork), different licenses (GPL-3.0 vs license-unclear). Per-vendor RFCs let conversation thread per group; Stella VSLAM sibling [RFC-0211](0211-stella-vslam-outreach.md).

## Prior art

- [`UZ-SLAMLab/ORB_SLAM3`](https://github.com/UZ-SLAMLab/ORB_SLAM3) — the upstream ORB-SLAM3 stack (engagement anchor).
- [RFC-0205 (Cartographer outreach)](0205-cartographer-outreach.md), [RFC-0207 (RTAB-Map outreach)](0207-rtabmap-outreach.md), [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md) — sibling Move-16 batch-3 RFCs; alternative SLAM substrates.

## Unresolved questions

For the UZ-SLAMLab / ORB-SLAM3 maintainers:

1. **SLAM-substrate enum value.** URML's manifest enum value preference (`orb_slam3`, `orbslam3`, `uz_orb_slam3`)?
2. **Five-mode enumeration shape.** Monocular / stereo / RGB-D / monocular-inertial / stereo-inertial — URML's manifest field shape: single `slam_mode` enum or `camera_topology` + `inertial_fusion` decomposed?
3. **Camera-calibration YAML reference convention.** Manifest-declared path or always launch-param?
4. **Vocabulary-file declaration.** Manifest field for path + size hint? Checksum-bind URML's validate step?
5. **GPL-3.0 cross-citation declaration.** Should URML's manifest itself declare a `license_bind: GPL-3.0` flag so downstream packagers see the constraint at validate time?
6. **Adapter home.** Separately-licensed companion package (likely GPL-3.0); URML-side citation only?
7. **Conformance listing.** Would UZ-SLAMLab consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) as a cross-citation entry?
8. **Anything else.**

## Implementation note

RFC-0206 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`UZ-SLAMLab/ORB_SLAM3` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the GPL-3.0-cross-citation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (GPL-3.0, 8.7k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (GPL-3.0 cross-citation only, five-mode enumeration, academic-maintainer cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: University of Zaragoza Spain (NATO-allied academic); default policy passes.
- [x] CLAUDE.md compliance check passed.
