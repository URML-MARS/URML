---
rfc: 0131
title: Xsens / Movella (MTi IMU / AHRS / INS) integration, request for comment from Movella maintainers
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

# RFC-0131: Xsens / Movella (MTi IMU / AHRS / INS) integration, request for comment from Movella maintainers

## Summary

URML does not yet ship an Xsens / Movella manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Xsens MTi-series IMU / AHRS / INS over [`xsens/xsens_mti_ros_node`](https://github.com/xsens/xsens_mti_ros_node) (legacy ROS 1, NOASSERTION) and the newer ROS 2 driver Movella distributes off-GitHub via tarball, and **requests review and feedback from the Movella maintainers**. No spec change.

This RFC complements [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) and [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md). Xsens MTi is the third major IMU/AHRS/INS lineage in URML's coverage, sharing the same IMU-measurement_type Spec-RFC gap.

## Motivation

Xsens (now [Movella](https://www.movella.com/), Enschede NL) is one of the foundational IMU/AHRS/INS vendors for robotics. The MTi product line covers stand-alone IMU (MTi-1 series), AHRS (MTi-30x), and INS with GNSS (MTi-680). Three vendor presences exist:

1. [`xsens/xsens_mti_ros_node`](https://github.com/xsens/xsens_mti_ros_node) — the legacy ROS 1 driver, 89 stars, 25 open issues, NOASSERTION license, last commit `2019-02-27` (>7 years stale on GitHub).
2. Movella distributes the newer ROS 2 driver via tarball download from `movella.com`, **not via the GitHub repo**.
3. [`xsens`](https://github.com/xsens) GitHub org — 8 public repos, vendor-direct, but the active ROS 2 driver has migrated off-GitHub.

**The migration off-GitHub is the engagement-shape question.** URML's outreach pipeline is GitHub-default; Movella's active ROS 2 driver is off-GitHub. This RFC asks whether Movella plans to revive a GitHub presence, prefers URML target the tarball directly, or recommends a different engagement channel entirely.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `xsens_mti_cell.yaml` fixture)

`Sensor` block, multi-measurement IMU:

| URML field | Maps to Xsens MTi product attribute |
|---|---|
| `name: imu` (Sensor) | MTi-series IMU (accel + gyro + mag, optionally fused) |
| `measurement_type: custom` (acceleration) | Linear acceleration — v0.1 has no native `acceleration` |
| `measurement_type: custom` (angular_velocity) | Angular velocity |
| `measurement_type: custom` (orientation) | MTi AHRS / VRU fused-orientation output |
| `measurement_type: custom` (gnss_position) | MTi-680 INS with GNSS — same gap as RFC-0119 / RFC-0120 |

### What URML v0.1 does not yet express for Xsens MTi

1. **IMU measurement_types** (`acceleration` / `angular_velocity` / `orientation`) — same gap shared with RFC-0117 (MicroStrain) and RFC-0118 (SBG); one Spec RFC covers all three vendors.
2. **GNSS-class measurement_types** — same gap shared with RFC-0119 (Septentrio) and RFC-0120 (NovAtel); INS variants need GNSS-aware manifest declarations.
3. **Off-GitHub driver distribution.** URML's outreach pipeline is GitHub-default; the active Movella ROS 2 driver lives behind a tarball download. Manifest declarations of "driver distribution channel" are not in v0.1 scope, but the engagement-channel mismatch is real.

### Compatibility notes

- **Vendor org.** [`xsens`](https://github.com/xsens) (org renamed-but-not-redirected from Xsens to Movella).
- **Legacy repo.** [`xsens/xsens_mti_ros_node`](https://github.com/xsens/xsens_mti_ros_node) — NOASSERTION, 89 stars, 25 open issues, last commit 2019-02-27 (`>7 years` stale on the GitHub branch).
- **Active driver.** Off-GitHub at `movella.com` tarball distribution.
- **Origin.** Enschede, Netherlands. Passes US-federal default policy (NATO allied).
- **License fit.** NOASSERTION on the GitHub legacy repo blocks adapter-grade reuse without clarification. Tarball-distributed ROS 2 driver license is documented in the tarball README.
- **Maintainer signal.** Vendor org real; GitHub-side dormant by design (Movella consolidated on off-GitHub distribution).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; IMU + GNSS-class Spec RFCs queued in parallel (shared with RFC-0117 / RFC-0118 / RFC-0119 / RFC-0120).
- Reference runtime: future `reference/sensor-runtime/` `XsensMtiAdapter` is a candidate **only** if engagement settles whether to target the legacy GitHub driver, the off-GitHub tarball driver, or cross-citation.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Off-GitHub active driver.** URML's GitHub-default pipeline routes around the active Movella surface; engagement shape is ambiguous.
- **Legacy GitHub repo NOASSERTION license.** Even if URML targets the legacy repo for compatibility, license clarification is required for adapter-grade reuse.
- **Two Spec-RFC prerequisites** (IMU types + GNSS-class). Same gaps as RFC-0117 through RFC-0120.

## Alternatives considered

1. **Engage exclusively on the legacy GitHub repo.** Considered. Risk: Movella has moved off-GitHub; the conversation may not reach active maintainers.
2. **Engage via direct email to Movella support.** Possible. Out of URML's GitHub-default outreach pattern; not the right shape for an open RFC.
3. **Cross-citation only (no adapter, no fixture).** Honest fallback if Movella prefers off-GitHub engagement entirely.

## Prior art

- [`xsens/xsens_mti_ros_node`](https://github.com/xsens/xsens_mti_ros_node) — legacy ROS 1 driver.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) + [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — sibling IMU/INS RFCs sharing the IMU-type Spec-RFC gap.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) + [RFC-0120 (NovAtel / Hexagon)](0120-novatel-hexagon-outreach.md) — sibling GNSS RFCs sharing the GNSS-class Spec-RFC gap.

## Unresolved questions

For the Movella maintainers:

1. **Engagement-channel preference.** GitHub Issue on `xsens/xsens_mti_ros_node`, Movella support email, Movella forum, or a different channel?
2. **GitHub roadmap.** Does Movella plan to revive an active GitHub presence (vendor-direct ROS 2 driver mirror on GitHub), or is the tarball-distribution model permanent?
3. **Legacy-repo license.** Can `xsens/xsens_mti_ros_node` get an explicit OSI license declaration (the ROS 1 driver is field-deployed on long-running fleets)?
4. **IMU + GNSS-class manifest fields.** Same questions as RFC-0117 / RFC-0118 / RFC-0119 / RFC-0120. Manifest-field expectations for MTi-680 INS-with-GNSS?
5. **Adapter home.** URML repo, Movella-maintained, or cross-citation only?
6. **Conformance listing.** Would Movella consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0131 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`xsens/xsens_mti_ros_node` has Issues enabled even though the branch is stale. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the off-GitHub migration and an offer to take the conversation to Movella's preferred channel.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (vendor org real, legacy ROS 1 repo stale 7 years, active ROS 2 driver off-GitHub on movella.com).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (off-GitHub active driver, NOASSERTION legacy license, two Spec-RFC prerequisites).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Movella NL; default policy passes.
- [x] CLAUDE.md compliance check passed.
