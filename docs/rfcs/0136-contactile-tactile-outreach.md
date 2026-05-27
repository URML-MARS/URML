---
rfc: 0136
title: Contactile (PapillArray tactile sensor) integration, request for comment from contactile maintainers
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

# RFC-0136: Contactile (PapillArray tactile sensor) integration, request for comment from contactile maintainers

## Summary

URML does not yet ship a Contactile manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Contactile's PapillArray tactile sensor over [`contactile/c3dfbs`](https://github.com/contactile/c3dfbs) (GPL-3.0) and the community ROS 2 wrapper [`mgonzs13/contactile_ros`](https://github.com/mgonzs13/contactile_ros), and **requests review and feedback from the contactile maintainers**. No spec change.

This RFC complements [RFC-0122 (GelSight)](0122-gelsight-tactile-outreach.md), URML's first tactile-sensing RFC. Where GelSight uses vision-based tactile sensing (camera under a deformable membrane), Contactile uses an array of capacitive force sensors arranged in a fingerprint-like pattern (the "PapillArray"). The two tactile-vendor RFCs are complementary, not duplicative.

## Motivation

Contactile is a [UNSW spin-off](https://www.contactile.com/) (University of New South Wales, Sydney, Australia) commercializing the PapillArray tactile-sensing technology. Their flagship `c3dfbs` repo (GPL-3.0, 0 stars, 1 open issue, last commit 2025-02-04 — stale `>15 months` from cutoff) is the vendor C++ driver; the community-maintained `mgonzs13/contactile_ros` is a more recent ROS 2 wrapper.

**Engagement-shape question:** vendor account on GitHub is a *user* account (not org-type), single-maintainer pattern, GPL-3.0 copyleft license. URML-fit via cross-citation is the recommended posture given:

1. Copyleft GPL-3.0 limits Apache-2.0 bundling.
2. Single-maintainer pattern means slow response is expected.
3. The community ROS 2 wrapper is the practical-leverage point.

This is URML's second tactile-sensing RFC after RFC-0122. Together they map the two dominant lineages (vision-based vs capacitive-array) and provide vendor input for the eventual tactile / pressure-array measurement_type Spec RFC.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `contactile_papillarray_cell.yaml` fixture)

`Sensor` block, multi-channel tactile:

| URML field | Maps to Contactile product attribute |
|---|---|
| `name: tactile` (Sensor) | Contactile PapillArray fingertip sensor |
| `measurement_type: custom` (tactile_array) | Per-pillar 3-axis force vector (X / Y / Z normal+shear forces) |
| `measurement_type: custom` (slip_detection) | Vendor-side slip-detection event |
| `measurement_type: custom` (contact_localization) | Per-pillar contact localization (which pillars active) |

### What URML v0.1 does not yet express for Contactile

1. **Tactile / pressure-array measurement_type.** Same gap RFC-0122 (GelSight) flagged; one Spec RFC adding `tactile_array` covers both. PapillArray's per-pillar 3-axis force vector is structurally different from GelSight's vision-based output — vendor input from both sharpens the Spec RFC.
2. **Slip-detection event declaration.** Tactile sensors emit slip-detection events as a derived semantic on top of raw forces; URML's manifest cannot today declare which derived events are vendor-supported.
3. **Force-feedback safety-envelope cross-link.** Tactile thresholds (peak force > threshold, slip onset) can gate URML grasp primitive execution; URML's `grasp` primitive (Layer 2) does not today consume tactile feedback. Future cross-layer work.

### Compatibility notes

- **Vendor account.** [`contactile`](https://github.com/contactile) — **user-type GitHub account, not organization**. Single-maintainer pattern.
- **Vendor repo.** [`contactile/c3dfbs`](https://github.com/contactile/c3dfbs) — GPL-3.0, 0 stars, 1 open issue, Issues enabled, last commit 2025-02-04 (`>15 months` stale).
- **Community ROS 2 wrapper.** [`mgonzs13/contactile_ros`](https://github.com/mgonzs13/contactile_ros) — practical-use ROS 2 wrapper, more recent than vendor repo.
- **Origin.** UNSW spin-off, Sydney, Australia (AU). Passes US-federal default policy (allied; Five Eyes).
- **License fit.** GPL-3.0 copyleft. Limits Apache-2.0 bundling; cross-citation framing is appropriate.
- **Maintainer signal.** Thin commercial GitHub presence; vendor active off-GitHub via website + email.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; tactile-array Spec RFC queued in parallel (shared with RFC-0122 GelSight).
- Reference runtime: cross-citation recommended over adapter; if engagement settles otherwise, future `reference/sensor-runtime/ContactileAdapter` would target the open ROS 2 wrapper, not the GPL-3.0 vendor driver, to keep adapter Apache-2.0-compatible.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 copyleft** on the vendor driver limits Apache-2.0 bundling; cross-citation is the honest fit.
- **Single-maintainer / user-account pattern** — slow response expected.
- **Tactile-array Spec RFC prerequisite.** Same gap as RFC-0122.
- **Vendor repo staleness** (>15 months).

## Alternatives considered

1. **Engage via the community ROS 2 wrapper (mgonzs13/contactile_ros) instead of the vendor.** Considered seriously. The community wrapper is more recent and Apache-2.0-friendly. URML's outreach is vendor-direct first; mgonzs13 RFC would be a follow-on.
2. **Defer Contactile until repo reactivates.** Rejected. The repo is stale but the vendor (per contactile.com) is operating; the RFC may be the reactivating nudge.
3. **Bundle Contactile + GelSight into one tactile RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; tactile-array Spec RFC is the shared piece.

## Prior art

- [`contactile/c3dfbs`](https://github.com/contactile/c3dfbs) — the upstream vendor driver.
- [`mgonzs13/contactile_ros`](https://github.com/mgonzs13/contactile_ros) — community ROS 2 wrapper.
- [RFC-0122 (GelSight)](0122-gelsight-tactile-outreach.md) — sibling tactile-sensing RFC sharing the tactile-array Spec-RFC gap.

## Unresolved questions

For the contactile maintainers:

1. **Engagement-channel preference.** GitHub Issue on `c3dfbs`, vendor support email at contactile.com, or other channel?
2. **License posture.** GPL-3.0 on the driver limits Apache-2.0 downstream bundling. Is a dual-license (GPL-3.0 + commercial) shape possible, or is GPL-3.0 the deliberate choice?
3. **Tactile-array measurement_type shape.** Same question as RFC-0122. PapillArray's per-pillar 3-axis force vector vs GelSight's vision-based output — manifest-field expectations (pillars / pixels, force / image, contact-localization granularity)?
4. **Slip-detection event declaration.** Should URML's manifest declare which derived events (slip-detection, contact-onset, force-peak) are vendor-supported?
5. **Adapter home.** Cross-citation only (recommended), URML repo (`reference/sensor-runtime/`) targeting the community wrapper, or vendor-maintained `contactile/contactile-urml` repo?
6. **Anything else.**

## Implementation note

RFC-0136 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml). Cross-citation framing is the recommended posture.

## How to respond

`contactile/c3dfbs` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with light-touch expectation for slow response.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (GPL-3.0, user-account-type, single-maintainer, last commit 2025-02-04 stale >15 months, community ROS 2 wrapper at mgonzs13/contactile_ros).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (GPL-3.0 copyleft, single-maintainer pattern, staleness, tactile-array Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Contactile AU (UNSW spin-off); default policy passes.
- [x] CLAUDE.md compliance check passed.
