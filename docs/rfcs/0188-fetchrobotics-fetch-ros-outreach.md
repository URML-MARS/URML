---
rfc: 0188
title: Fetch Robotics (Fetch + Freight mobile manipulator) integration, request for comment from fetchrobotics maintainers — license + post-acquisition-governance asks
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

# RFC-0188: Fetch Robotics (Fetch + Freight mobile manipulator) integration — license + post-acquisition-governance asks

## Summary

URML does not yet ship a Fetch manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest **cross-citation** for Fetch Robotics' Fetch mobile manipulator + Freight mobile base over [`fetchrobotics/fetch_ros`](https://github.com/fetchrobotics/fetch_ros), and **requests review and feedback from the fetchrobotics maintainers** (post-Zebra acquisition). **License-clarification ask + post-acquisition-governance question** are the gating items. No spec change.

## Motivation

Fetch Robotics (US, San Jose) built the Fetch mobile manipulator and Freight mobile base — research-grade platforms widely deployed in academic robotics labs for mobile-manipulation research and benchmarking. Fetch was acquired by Zebra Technologies in 2023; the GitHub presence remains but has been stale ever since.

Repo at [`fetchrobotics/fetch_ros`](https://github.com/fetchrobotics/fetch_ros) (no SPDX visible — clarification ask, 202 stars, Issues enabled, last commit `2024-08-20` — **stale 646 days from cutoff 2026-05-28**, **not archived**).

URML's engagement angle is partly a status-check and partly an honest cross-citation. The 202-star adoption signal reflects substantial deployed-fleet presence in academic robotics; URML's manifest declares Fetch class for those deployments. Post-acquisition governance is the open question — has Zebra maintained the GitHub surface, or has engagement moved elsewhere?

## Detailed design

### URML v0.1 capability-manifest mapping (cross-citation framing for `fetch_robot_cell.yaml` fixture)

| URML field | Maps to Fetch attribute |
|---|---|
| `name` | Specific platform (`fetch_research`, `freight_mobile_base`) |
| `mobility.drive_type: differential` | Fetch / Freight differential mobile base (clean v0.1 fit) |
| `actuators` | Fetch 7-DoF arm (when Fetch, not Freight) |
| `cameras` | Head pan-tilt RGB-D |
| `topology: custom` (`mobile_base_plus_arm_plus_head`) | Same composite topology gap as RFC-0184 Hello Robot Stretch |
| `acquisition_era: custom` (`fetch_pre_zebra_2023` / `zebra_era`) | Manifest declaration of acquisition-era governance posture |

### What URML v0.1 does not yet express for Fetch

1. **Mobile-manipulator topology declaration.** Same shared gap as RFC-0184 Hello Robot Stretch.
2. **Acquisition-era governance declaration.** URML's manifest cannot today declare that a platform was acquired and the governance pin moved. Spec RFC queued — relevant for any URML target that gets acquired during its deployment lifetime.
3. **License clarification.** No SPDX upstream blocks Apache-2.0 downstream bundling.

### Compatibility notes

- **Vendor org.** [`fetchrobotics`](https://github.com/fetchrobotics) — Fetch Robotics (acquired by Zebra Technologies 2023), US San Jose.
- **Flagship repo.** [`fetchrobotics/fetch_ros`](https://github.com/fetchrobotics/fetch_ros) — license: none visible (clarification ask), 202 stars, Issues enabled, last commit 2024-08-20 (**stale 646 days**), **not archived**.
- **Origin.** Fetch Robotics → Zebra Technologies, US. Passes US-federal default policy.
- **License fit.** Pending clarification.
- **Maintainer signal.** Stale + post-acquisition; engagement is a status-check on whether the platform is still community-supported.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; mobile-manipulator topology (shared with RFC-0184) + acquisition-era governance Spec RFCs queued.
- Reference runtime: cross-citation framing pending license + governance clarification.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License-clarification gate** combined with **post-acquisition-governance unknown.** Two open questions before adapter-grade reuse.
- **Staleness >1.5 years.** Engagement may yield slow / no response.
- **Acquisition-era governance declaration** is novel manifest territory; first concrete case URML's outreach has encountered (Velodyne was a sibling but the brand survives under Ouster post-acquisition; Fetch's case is closer-to-orphaned).

## Alternatives considered

1. **Skip Fetch as the surface is post-acquisition and stale.** Rejected. 202-star adoption signal + URML's mobile-manipulator class gap make the engagement worthwhile even if Tier B / cross-citation only.
2. **Engage Zebra Technologies directly instead of the legacy GitHub org.** Considered. Zebra has not surfaced a successor robotics org publicly; engagement on the legacy surface is the right first ask.
3. **Bundle Fetch with sibling Move-14 mobile-manipulator RFCs.** Rejected. Per-vendor RFCs.

## Prior art

- [`fetchrobotics/fetch_ros`](https://github.com/fetchrobotics/fetch_ros) — the upstream ROS driver.
- [RFC-0184 (Hello Robot Stretch)](0184-hello-robot-stretch-outreach.md) — sibling Move-14 mobile-manipulator RFC sharing the topology Spec-RFC gap.
- [RFC-0130 (Velodyne via ros-drivers)](0130-velodyne-via-ros-drivers-outreach.md) — Move-10 sibling RFC where brand-acquisition routing was the design point; Velodyne survives under Ouster, Fetch's case is closer-to-orphaned.

## Unresolved questions

For the fetchrobotics maintainers (and Zebra Technologies, if reachable):

1. **License clarification.** Can `fetchrobotics/fetch_ros` get an explicit OSI license declaration?
2. **Post-acquisition governance.** Is the Fetch GitHub org actively maintained under Zebra, dormant-but-monitored, or has engagement moved to a successor surface entirely?
3. **Mobile-manipulator topology manifest fields.** Same shared question as RFC-0184 Hello Robot Stretch.
4. **Acquisition-era governance manifest declaration.** Should URML's manifest declare acquisition-era platforms for downstream operator awareness?
5. **Bridge home.** Cross-citation only (recommended pending license + governance), URML repo (`reference/mobile-manipulator-runtime/FetchAdapter`), or none?
6. **Conformance listing.** If the platform is still community-supported, would the maintainers consider a README link to URML's compatible-runtimes registry?
7. **Anything else.**

## Implementation note

RFC-0188 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`fetchrobotics/fetch_ros` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the staleness + post-Zebra-acquisition governance question.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license none visible, 202 stars, Issues enabled, last commit 2024-08-20 stale 646d, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license + governance + staleness; acquisition-era declaration novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Fetch Robotics → Zebra Technologies US; default policy passes.
- [x] CLAUDE.md compliance check passed.
