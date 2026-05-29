---
rfc: 0205
title: Google Cartographer (2D/3D SLAM substrate) integration, request for comment from Cartographer maintainers
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

# RFC-0205: Google Cartographer (2D/3D SLAM substrate) integration

## Summary

URML's perception manifest currently declares lidar, camera, and radar sensors but does not declare a SLAM substrate. This RFC documents the proposed URML v0.1 capability-manifest mapping for the SLAM-substrate class, engaged at the Google / cartographer-project layer via [`cartographer-project/cartographer`](https://github.com/cartographer-project/cartographer) (Apache-2.0), and **requests review and feedback from the Cartographer maintainers**. No spec change.

**This is URML's first SLAM-substrate RFC** and the opening of Move-16 batch 3 (SLAM upstreams). Sibling RFCs cover ORB-SLAM3 (visual-SLAM, [RFC-0206](0206-orb-slam3-outreach.md)) and RTAB-Map (visual-inertial, [RFC-0207](0207-rtabmap-outreach.md)).

## Motivation

Google Cartographer is the canonical 2D/3D real-time SLAM stack and integrates natively with ROS 2 via `cartographer_ros`. URML's mobility primitives currently consume map / pose data without declaring the source SLAM substrate; production deployments need explicit substrate declaration to bind the manifest to the actual runtime configuration.

Repo at [`cartographer-project/cartographer`](https://github.com/cartographer-project/cartographer) (Apache-2.0, 7.9k stars, Issues enabled, last commit `2026-05-28`, **not archived**). Google US.

URML benefits from documenting the engagement because:

1. **SLAM-substrate declaration is URML's missing manifest layer.** URML declares lidar / camera / radar sensors; it does not declare which SLAM substrate consumes them. The natural shape is `perception.slam_substrate` with enum values across this batch's three RFCs.
2. **2D vs 3D pose-frame semantics.** Cartographer supports both 2D and 3D modes; URML's manifest could declare per-deployment dimensionality.
3. **Sub-map / global-map decomposition.** Cartographer's sub-map architecture is performance-tier relevant; URML's manifest could declare hints for loop-closure budgets.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `cartographer_lidar_cell.yaml` fixture)

| URML field | Maps to Cartographer attribute |
|---|---|
| `name` | Deployment handle (`cartographer_humble_lidar2d`) |
| `perception.slam_substrate: cartographer` | URML's first SLAM-substrate enum value |
| `perception.slam_mode: 2d` / `3d` | Cartographer 2D vs 3D pose-graph mode |
| `perception.lua_config` | Cartographer Lua configuration reference |
| `perception.submap_publish_period_ms` | Sub-map publish cadence hint |
| `perception.optimization.max_num_iterations` | Pose-graph optimization budget |
| `pose_frame.tracking_frame` | Cartographer tracking frame |
| `pose_frame.published_frame` | Cartographer published frame (map / odom) |

### What URML v0.1 does not yet express for Cartographer

1. **SLAM-substrate enum.** First-class SLAM-substrate field; URML's first (this batch defines the field across three implementations).
2. **Lua-configuration reference convention.** Cartographer's Lua config is its own DSL; URML's manifest could declare reference path or canonicalize via launch param.
3. **Sub-map publish cadence + loop-closure budgets.** Performance-tier hints relevant for high-frequency deployments.
4. **Pose-frame manifest fields.** Tracking + published frames are TF2-side today; manifest declaration future work.

### Compatibility notes

- **Vendor org.** [`cartographer-project`](https://github.com/cartographer-project) — Google / community.
- **Engagement repo.** [`cartographer-project/cartographer`](https://github.com/cartographer-project/cartographer) — Apache-2.0, 7.9k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `cartographer-project/cartographer_ros`, `cartographer-project/cartographer_documentation` — the ROS 2 binding and documentation.
- **Origin.** Google US. Passes US-federal default policy.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** Active commits; the canonical 2D/3D SLAM reference.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; SLAM-substrate enum + Lua-configuration reference + pose-frame Spec RFCs queued.
- Reference runtime: future `reference/ros2-runtime/CartographerAdapter` is a candidate via `cartographer_ros`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **First-SLAM-RFC novelty** — URML's first SLAM-substrate field; manifest semantics require this batch's three vendors' input.
- **Lua-configuration dependency surface** — Cartographer's DSL is its own format; URML's manifest indirectly depends on it.

## Alternatives considered

1. **Engage at the `cartographer_ros` binding repo instead of core.** Considered. Core Cartographer is the substrate; the binding is downstream. Engagement at the core layer covers binding-side discussions.
2. **Skip SLAM-substrate manifest field; let URML declare only sensors.** Rejected. Production users care which SLAM stack runs; ignoring it leaves the manifest incomplete.
3. **Bundle Cartographer + ORB-SLAM3 + RTAB-Map in a single SLAM-substrate RFC.** Rejected. Different licenses (Apache-2.0 vs GPL-3.0 vs mixed LGPL/BSD), different communities, different SLAM modalities (lidar vs visual vs visual-inertial); per-vendor RFCs let conversation thread per group.

## Prior art

- [`cartographer-project/cartographer`](https://github.com/cartographer-project/cartographer) — the upstream Cartographer stack (engagement anchor).
- [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md), [RFC-0207 (RTAB-Map outreach)](0207-rtabmap-outreach.md) — sibling Move-16 batch-3 RFCs; alternative SLAM modalities.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement (Cartographer's ROS 2 binding).

## Unresolved questions

For the Cartographer maintainers:

1. **SLAM-substrate enum manifest field.** URML's first; Cartographer perspective on the enum value (`cartographer`, `google_cartographer`, `cartographer-2d` / `cartographer-3d`)?
2. **Lua-configuration reference convention.** Manifest-declared path, or always launch-param?
3. **2D vs 3D mode declaration.** Per-deployment mode field, or always Lua-config-side?
4. **Sub-map cadence + loop-closure budget hints.** URML's manifest could declare performance-tier hints; preferred shape from the Cartographer side?
5. **Pose-frame manifest field.** Tracking + published frames — manifest declaration or always TF2-side?
6. **Adapter home.** Future URML `reference/ros2-runtime/CartographerAdapter`, Cartographer-maintained, or cross-citation only?
7. **Conformance listing.** Would the Cartographer project consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once a working adapter ships?
8. **Anything else.**

## Implementation note

RFC-0205 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`cartographer-project/cartographer` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the SLAM-substrate-declaration framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, 7.9k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (first-SLAM-RFC novelty, Lua-configuration dependency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Google US; default policy passes.
- [x] CLAUDE.md compliance check passed.
