---
rfc: 0112
title: Roboception (rc_visard / rc_cube) integration, request for comment from roboception maintainers
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

# RFC-0112: Roboception (rc_visard / rc_cube) integration, request for comment from roboception maintainers

## Summary

URML does not yet ship a Roboception manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Roboception's rc_visard 3D stereo sensor + rc_cube compute family over [`roboception/cvkit`](https://github.com/roboception/cvkit) (BSD-3-Clause C++ computer-vision toolkit) and the sibling `rc_genicam_api`, and **requests review and feedback from the roboception maintainers**. No spec change.

## Motivation

Roboception (Munich DE) is an ex-DLR spin-off; co-founder Heiko Hirschmueller's lineage in stereo-vision benchmarks is widely cited and overlaps with RFC-0111 (Carnegie Robotics MultiSense maintainers). The vendor org's `cvkit` is BSD-3-Clause and actively maintained (last commit 2026-05-14); `rc_genicam_api` provides the GenICam-protocol interface. The ROS driver `rc_visard_ros` is stale 2022 — URML's RFC asks the maintainers about its current status.

URML's Move #10 wave includes Roboception as one of two industrial-3D-vision Tier-A vendors (alongside Basler RFC-0113). The vendor's pick-and-place application focus aligns with RFC-0013 (industrial primitives — `pick_from`, `place_at`, `swap_tool`).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `roboception_rc_visard_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to Roboception product attribute |
|---|---|
| `name` | Deployment handle (`rc_visard_65`, `rc_visard_160`) |
| `supports_photo` | `true` — stereo left + right |
| `supports_video` | `true` |
| `supports_stream` | `true` — RGB + disparity + 3D + grasp-detection (where licensed) |
| `max_resolution` | Per-model |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: point_cloud` | rc_visard 3D output |
| `measurement_type: distance` | Disparity frame |

### What URML v0.1 does not yet express for Roboception

1. **Per-point attributes on point clouds** — same gap as RFC-0035 / RFC-0109 / RFC-0110 / RFC-0111 / RFC-0115.
2. **GenICam-protocol capability declaration** — `rc_genicam_api` exposes GenICam standard; URML's manifest could declare GenICam compliance as a transport-protocol capability, paralleling the way industrial cells declare other transports.
3. **Bundled grasp / pick-detection** — Roboception ships licensed grasp-detection modules; same detection-declaration question raised by RFC-0109 + RFC-0110 + RFC-0115.

### Compatibility notes

- **Vendor org.** [`roboception/cvkit`](https://github.com/roboception/cvkit) (BSD-3-Clause), `roboception/rc_genicam_api` (NOASSERTION — verify), `roboception/rc_visard_ros` (ROS driver, stale 2022).
- **Origin.** Roboception GmbH, Munich DE. Passes US-federal default policy (NATO allied).
- **License fit.** BSD-3-Clause on `cvkit` is clean; `rc_genicam_api` license needs clarification.

### Spec / validator / reference-runtime / conformance changes

- None in this RFC. Future `reference/perception-runtime/` would host `RoboceptionAdapter`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **ROS driver `rc_visard_ros` is stale (2022).** URML's RFC asks whether the driver is in maintenance mode, deprecated, or being replaced.
- **Licensed grasp-detection modules** sit outside the OSS surface; URML's manifest can declare them but cannot exercise them without a vendor license.

## Alternatives considered

1. **Bundle Roboception + Carnegie MultiSense (shared lineage) + ZED into a single "industrial stereo" RFC.** Rejected. Per-vendor RFCs.
2. **Skip Roboception because the ROS driver is stale.** Rejected. The `cvkit` / `rc_genicam_api` surface is live; URML can engage there.

## Prior art

- [`roboception/cvkit`](https://github.com/roboception/cvkit) — the upstream toolkit.
- [RFC-0111 (Carnegie Robotics MultiSense)](0111-carnegie-multisense-outreach.md) — sibling stereo-vision RFC, shared maintainer lineage.
- [RFC-0013 (industrial primitives)](0013-industrial-layer2-primitives.md) — Roboception's pick-and-place focus aligns with `pick_from` / `place_at`.

## Unresolved questions

For the `roboception` maintainers:

1. **`rc_visard_ros` status.** Is the ROS driver in maintenance mode, deprecated, or being replaced by a newer ROS 2 wrapper?
2. **GenICam-protocol capability declaration.** Should URML's manifest declare GenICam compliance as a transport-protocol capability for cameras that follow the standard? (Same question potentially applies to Basler RFC-0113.)
3. **Licensed grasp-detection / pick-quality modules.** How should URML's manifest declare the licensed Roboception modules so a deployment's `pick_from` / `query_detection` validates against actual capability + license-state?
4. **Per-point attributes on point clouds.** Color + intensity per-point.
5. **License clarification on `rc_genicam_api`.** Repo classifier shows NOASSERTION; could you confirm the SPDX?
6. **Adapter home.** URML repo, Roboception-hosted, or both?
7. **Conformance listing.** Would Roboception consider a README link to URML's compatible-runtimes registry once a working adapter ships?
8. **Anything else.**

## Implementation note

RFC-0112 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`roboception/cvkit` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (BSD-3-Clause, 279 stars, 0 open issues, Issues enabled, last commit 2026-05-14 active).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (stale ROS driver, licensed modules outside OSS surface).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Roboception DE; default policy passes.
- [x] CLAUDE.md compliance check passed.
