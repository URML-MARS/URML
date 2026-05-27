---
rfc: 0126
title: iniVation (DAVIS event-camera, GitLab-primary) integration, request for comment from iniVation maintainers
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

# RFC-0126: iniVation (DAVIS event-camera) integration, request for comment from iniVation maintainers

## Summary

URML does not yet ship an iniVation manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for iniVation's DAVIS-series event cameras over `dv-processing` and `dv-ros` (GitLab-primary, [`gitlab.com/inivation`](https://gitlab.com/inivation)), and **requests review and feedback from the iniVation maintainers**. No spec change.

This RFC pairs with [RFC-0114 (Prophesee event-stream)](0114-prophesee-event-outreach.md) as URML's two-vendor coverage of the event-camera category. The same event-stream Spec RFC Prophesee gates iniVation needs.

## Motivation

iniVation AG (Zürich, Switzerland) is the commercial home of the DAVIS event-camera lineage that came out of the original [INI/ETH dynamic-vision pixel work](https://sensors.ini.uzh.ch/) by Tobi Delbrück and colleagues. URML's perception story benefits from the DAVIS family because the integrated Active Pixel Sensor (APS) + event-pixel design supports natural fall-back to a conventional frame when an event-only mode is insufficient.

Engagement-surface shape is the gating question. iniVation's active development lives on **GitLab** (`gitlab.com/inivation/dv/dv-processing`, `gitlab.com/inivation/dv/dv-ros`), not GitHub. Their GitHub presence is utility-only (forks of `flatbuffers`, `vcpkg`, `etl`). The community ROS 2 wrapper [`Telios/dv-ros2`](https://github.com/Telios/dv-ros2) (11 stars) is the closest GitHub-side surface, but it is community-maintained, not vendor.

URML's outreach pipeline is GitHub-default. This RFC opens the conversation across both surfaces — GitLab for vendor-native engagement, GitHub utility repo for routing visibility — and asks iniVation maintainers which channel they prefer.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `inivation_davis_cell.yaml` fixture)

`Camera` block:

| URML field | Maps to iniVation product attribute |
|---|---|
| `name` | Deployment handle (`inivation_davis346`, `inivation_dvxplorer`) |
| `supports_photo` | `true` — APS still-frame from co-located pixels |
| `supports_video` | `true` — APS conventional-frame at modest rate |
| `supports_stream` | `true` — dual-mode event-stream + APS frames |
| `max_resolution` | Per-model (DAVIS346: 346x260; DVXplorer: 640x480) |

`Sensor` block:

| URML field | Maps to |
|---|---|
| `measurement_type: custom` (event_stream) | Asynchronous pixel-level brightness-change events; v0.1 has no native `event_stream` type |
| `measurement_type: custom` (imu) | Inline 6-axis IMU on DAVIS346/DVXplorer modules |

### What URML v0.1 does not yet express for iniVation

1. **Event-stream measurement_type.** Same gap RFC-0114 (Prophesee) flagged; one Spec RFC covers both.
2. **Dual-mode camera (event + APS).** DAVIS pixels are integrated event-and-frame; URML's `cameras` block treats frame-modes uniformly and the manifest cannot today express the cross-coupling.
3. **Inline IMU declaration.** DAVIS modules ship a co-located IMU — same gap RFC-0117 / RFC-0118 flagged for the IMU measurement_type Spec RFC.

### Compatibility notes

- **Vendor origin.** Zürich, Switzerland. Passes US-federal default policy (NATO allied).
- **Vendor-native surface.** [`gitlab.com/inivation/dv`](https://gitlab.com/inivation/dv) (GitLab, not GitHub).
- **GitHub side.** Utility forks only on [`github.com/inivation`](https://github.com/inivation); the community ROS 2 wrapper [`Telios/dv-ros2`](https://github.com/Telios/dv-ros2) (11 stars) is the closest GitHub vendor-context surface.
- **License posture.** Apache-2.0 on the dv-processing core (clean fit) per the GitLab repo READMEs.
- **Maintainer signal.** Active GitLab development; vendor email through inivation.com.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; event-stream + IMU Spec RFCs queued in parallel (shared with RFC-0114 / RFC-0117 / RFC-0118).
- Reference runtime: future `reference/perception-runtime/` `IniVationDavisAdapter` if engagement settles on adapter shape; cross-citation is the more likely outcome given the GitLab-primary surface.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GitLab-primary engagement surface** is off URML's default pipeline. Either URML widens outreach to GitLab or engagement routes via the thin GitHub utility-fork org.
- **Two Spec-RFC prerequisites** (event-stream + IMU types). Same gaps as RFC-0114 / RFC-0117 / RFC-0118.

## Alternatives considered

1. **Engage exclusively on GitLab.** Considered. URML's outreach ledger is GitHub-shaped; widening to GitLab requires ledger-schema changes (`channel: gitlab_issue` etc). Out of scope for this RFC; could become a separate operational RFC.
2. **Engage via the community ROS 2 wrapper `Telios/dv-ros2`.** Possible. Risk: not vendor; iniVation maintainers may not see the conversation.
3. **Cross-citation only (no adapter, no fixture).** Honest fallback if vendor prefers the GitLab-native conversation stays GitLab-native.

## Prior art

- [`gitlab.com/inivation/dv/dv-processing`](https://gitlab.com/inivation/dv/dv-processing) — the upstream processing library.
- [`gitlab.com/inivation/dv/dv-ros`](https://gitlab.com/inivation/dv/dv-ros) — ROS bindings.
- [RFC-0114 (Prophesee event-stream)](0114-prophesee-event-outreach.md) — sibling event-camera RFC sharing the event-stream Spec-RFC gap.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) + [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — sibling IMU/INS RFCs sharing the IMU-type Spec-RFC gap.

## Unresolved questions

For the iniVation maintainers:

1. **Engagement-surface preference.** GitLab Issue on `dv-processing` or `dv-ros`, GitHub Issue on a utility-fork repo as a routing notice, or a vendor-redirect to a different channel entirely (forum, email)?
2. **Event-stream measurement_type shape.** Same question as RFC-0114 — temporal resolution, event-rate, event-polarity declaration. Two vendor inputs are better than one.
3. **Dual-mode DAVIS declaration.** Should URML's manifest express the event-and-frame integration explicitly (one Camera block with both modes), or as two logically separate sensors?
4. **Inline IMU declaration.** DAVIS346 / DVXplorer ship co-located IMU. Same Spec-RFC gap as RFC-0117 / RFC-0118; iniVation's perspective on IMU-class manifest fields would help.
5. **Adapter home.** URML repo, iniVation-maintained, both, or cross-citation only?
6. **Conformance listing.** Would iniVation consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0126 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

Vendor-native channel is GitLab; URML's pipeline is GitHub. Planned channel: open a GitLab Issue on `dv-processing` (vendor-native) + a parallel cross-referenced GitHub Issue on a utility-fork repo for routing visibility. If iniVation prefers one channel, RFC engagement consolidates there.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (GitLab vendor-native; GitHub utility-only; community ROS 2 wrapper noted).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (GitLab surface mismatch, two Spec-RFC prerequisites).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: iniVation CH; default policy passes.
- [x] CLAUDE.md compliance check passed.
