---
rfc: 0207
title: RTAB-Map (visual-inertial SLAM substrate) integration, request for comment from introlab maintainers
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

# RFC-0207: RTAB-Map (visual-inertial SLAM substrate) integration

## Summary

URML's perception manifest does not yet declare a visual-inertial SLAM substrate with ROS 2-native integration. This RFC documents the proposed URML v0.1 capability-manifest mapping for RTAB-Map (Real-Time Appearance-Based Mapping), engaged at the Université de Sherbrooke IntRoLab layer via [`introlab/rtabmap`](https://github.com/introlab/rtabmap) (Other — mixed LGPL/BSD), and **requests review and feedback from the IntRoLab / RTAB-Map maintainers**. No spec change.

**License clarification is the gating fact.** The repo is GitHub-classified as Other; the README cites BSD-3-Clause / LGPLv3 mixed. URML's adapter posture depends on per-module license clarity.

## Motivation

RTAB-Map is a widely-deployed visual-inertial SLAM library with strong ROS 2 integration via `rtabmap_ros`. It complements ORB-SLAM3 (sibling [RFC-0206](0206-orb-slam3-outreach.md), academic / GPL-3.0) and Cartographer (sibling [RFC-0205](0205-cartographer-outreach.md), Google / Apache-2.0) by occupying the production-friendly visual-inertial slot in the SLAM-substrate enum.

Repo at [`introlab/rtabmap`](https://github.com/introlab/rtabmap) (Other — mixed LGPL/BSD, 3.8k stars, Issues enabled, last commit `2026-05-28`, **not archived**). Université de Sherbrooke IntRoLab (Quebec, Canada).

URML benefits from documenting the engagement because:

1. **Visual-inertial slot in the SLAM-substrate enum.** RTAB-Map is the production-friendly visual-inertial SLAM choice; URML's manifest enum needs the slot.
2. **License clarification ask.** Mixed LGPL/BSD is workable for URML's adapter pattern but the boundary between LGPL and BSD-3 modules must be clear before any in-repo URML adapter ships.
3. **Loop-closure / appearance-based recognition manifest semantics.** RTAB-Map's appearance-based loop closure is a degree of freedom URML's manifest could declare for performance-tier hints.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `rtabmap_visual_inertial_cell.yaml` fixture, pending license clarification)

| URML field | Maps to RTAB-Map attribute |
|---|---|
| `name` | Deployment handle (`rtabmap_humble_stereo_imu`) |
| `perception.slam_substrate: rtabmap` | URML's visual-inertial SLAM enum value |
| `perception.slam_mode: stereo` / `rgbd` / `stereo_imu` / `rgbd_imu` | RTAB-Map sensor topology mode |
| `perception.database_path` | RTAB-Map database file reference |
| `perception.loop_closure_threshold` | Appearance-based loop-closure confidence threshold |
| `perception.feature_detector` | SURF / SIFT / ORB / BRIEF / KAZE / GFTT feature extractor |
| `pose_frame.map_frame` | RTAB-Map map frame |

### What URML v0.1 does not yet express for RTAB-Map

1. **Database-path manifest field.** RTAB-Map's persistent database is its memory model; URML's manifest could declare path + size hint.
2. **Loop-closure-threshold field.** Performance-tier hint relevant for high-throughput deployments.
3. **Feature-detector enumeration.** SURF / SIFT / ORB / BRIEF / KAZE / GFTT — URML's manifest could declare per-deployment selection.
4. **Mixed-license per-module declaration.** Manifest could declare which RTAB-Map modules are LGPL vs BSD-3 for downstream packaging.

### Compatibility notes

- **Vendor org.** [`introlab`](https://github.com/introlab) — Université de Sherbrooke IntRoLab (Quebec, Canada).
- **Engagement repo.** [`introlab/rtabmap`](https://github.com/introlab/rtabmap) — Other (mixed LGPL/BSD per README), 3.8k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `introlab/rtabmap_ros` (ROS 2 binding) — the canonical ROS 2 integration.
- **Origin.** Canada (NATO-allied, Five Eyes); academic. Passes US-federal default policy.
- **License fit.** Mixed LGPL/BSD requires per-module clarification before in-repo URML adapter ships; cross-citation framing safe by default.
- **Maintainer signal.** Active commits; widely-deployed visual-inertial SLAM.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; SLAM-substrate enum (sibling [RFC-0205](0205-cartographer-outreach.md)) + sensor-topology mode + feature-detector + loop-closure manifest Spec RFCs queued.
- Reference runtime: future `reference/ros2-runtime/RTABMapAdapter` is a candidate via `rtabmap_ros` pending license clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate** — mixed LGPL/BSD per-module clarity needed before any in-repo URML adapter ships.
- **Feature-detector enumeration burden** — six common feature detectors are a real manifest-shape design surface.
- **Database-path persistence semantics** — RTAB-Map's persistent database is a stateful side-effect URML's stateless-validation philosophy must reconcile.

## Alternatives considered

1. **Cross-citation only; defer in-repo adapter until license clarifies.** Considered; current default posture. The RFC engagement is itself the license-clarification ask.
2. **Engage the `rtabmap_ros` binding repo instead of core.** Considered. Core RTAB-Map is the substrate; binding is downstream. Engagement at core covers both.
3. **Bundle RTAB-Map with ORB-SLAM3 in a single visual-SLAM RFC.** Rejected. Different licenses (GPL-3.0 vs mixed LGPL/BSD), different focus (visual-SLAM canonical reference vs production-friendly visual-inertial); per-vendor RFCs let conversation thread per group.

## Prior art

- [`introlab/rtabmap`](https://github.com/introlab/rtabmap) — the upstream RTAB-Map stack (engagement anchor).
- [RFC-0205 (Cartographer outreach)](0205-cartographer-outreach.md), [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md), [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md) — sibling Move-16 batch-3 RFCs; alternative SLAM substrates.

## Unresolved questions

For the IntRoLab / RTAB-Map maintainers:

1. **License clarification.** Per-module LGPL / BSD-3 boundary — can the README or LICENSE file declare per-directory licensing for downstream packager clarity?
2. **SLAM-substrate enum value.** URML's manifest enum value preference (`rtabmap`, `rtab_map`)?
3. **Database-path manifest field.** Persistent database is RTAB-Map's memory model; manifest declaration shape?
4. **Loop-closure-threshold field.** Performance-tier hint; preferred manifest shape?
5. **Feature-detector enumeration.** SURF / SIFT / ORB / BRIEF / KAZE / GFTT — manifest-declared, or always launch-param?
6. **Adapter home.** Future URML `reference/ros2-runtime/RTABMapAdapter` (in-repo, pending license clarity), RTAB-Map-side, or cross-citation only?
7. **Conformance listing.** Would IntRoLab consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once a working adapter ships?
8. **Anything else.**

## Implementation note

RFC-0207 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`introlab/rtabmap` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the license-clarification + visual-inertial-slot framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Other — mixed LGPL/BSD, 3.8k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license-clarification gate, feature-detector enumeration burden, database-path persistence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Université de Sherbrooke Canada (NATO-allied, Five Eyes academic); default policy passes.
- [x] CLAUDE.md compliance check passed.
