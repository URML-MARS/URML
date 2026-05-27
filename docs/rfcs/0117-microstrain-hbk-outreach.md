---
rfc: 0117
title: MicroStrain by HBK (IMU / AHRS / INS) integration, request for comment from LORD-MicroStrain maintainers
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

# RFC-0117: MicroStrain by HBK (IMU / AHRS / INS) integration, request for comment from LORD-MicroStrain maintainers

## Summary

URML does not yet ship a MicroStrain-specific manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for MicroStrain's 3DM-CV7 / 3DM-GX5 / 3DM-GQ7 IMU / AHRS / INS line over [`LORD-MicroStrain/microstrain_inertial`](https://github.com/LORD-MicroStrain/microstrain_inertial) (ROS 1 + ROS 2 driver, 28-repo vendor org) and the MIP SDK, and **requests review and feedback from the MicroStrain maintainers**. No spec change.

## Motivation

`LORD-MicroStrain/microstrain_inertial` is the strongest IMU/INS vendor surface in URML's Move #10 verification: 133 stars, 33 open issues, Issues enabled, last commit days ago, 28 vendor public repos with regular cadence. The vendor org is MicroStrain by HBK (formerly Lord MicroStrain, now part of Hottinger Brüel & Kjær), Williston VT, US-domiciled. US-federal default policy passes cleanly.

URML's Move #10 wave identified IMU + GNSS as the strongest URML-fit sub-category — four Tier-A vendors (MicroStrain, SBG, Septentrio, NovAtel) all share clean OSI license + active ROS 2 driver maintainership. MicroStrain leads on US origin + GNSS-aided INS coverage (3DM-GQ7 RTK class).

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `microstrain_cv7_cell.yaml` fixture)

The MicroStrain class falls under URML's `Sensor` block (no `Camera` involvement). Per-device declaration:

| URML field | Maps to MicroStrain product attribute |
|---|---|
| `name: imu` (Sensor) | 3DM-CV7 / 3DM-GX5 IMU stream |
| `measurement_type: acceleration` (custom) | Linear acceleration (m/s²) — v0.1 enum has no `acceleration`, uses `custom` escape-hatch |
| `measurement_type: custom` (angular_velocity) | Angular velocity (rad/s) — same escape-hatch |
| `measurement_type: custom` (orientation) | AHRS-fused orientation (quaternion) — same escape-hatch |
| `measurement_type: custom` (gnss_position) | 3DM-GQ7 GNSS-aided INS position fix |
| `units` | `g`, `rad/s`, `m`, `degrees` per channel |

### What URML v0.1 does not yet express for MicroStrain

1. **First-class IMU measurement_types.** `acceleration`, `angular_velocity`, `orientation` all sit under `custom` in v0.1; a Spec RFC for IMU-class types is queued.
2. **INS fusion declaration.** 3DM-GQ7 emits GNSS-fused pose; URML's manifest can declare the constituent streams but not the fusion fact.
3. **RTK / NTRIP declaration.** GQ7's RTK-corrected position needs a manifest declaration of "this INS accepts NTRIP corrections from these constellations" — same gap as RFC-0118 (SBG) / RFC-0119 (Septentrio) / RFC-0120 (NovAtel).

### Compatibility notes

- **Vendor org.** [`LORD-MicroStrain/microstrain_inertial`](https://github.com/LORD-MicroStrain/microstrain_inertial) (ROS 1 + ROS 2 driver), sibling repos for MIP SDK (`mip_sdk`), NTRIP client, msgs.
- **Origin.** MicroStrain by HBK (Hottinger Brüel & Kjær), Williston VT, US. Passes US-federal default policy.
- **License fit.** Repo classifier shows NOASSERTION on `microstrain_inertial`; in-repo LICENSE likely MIT or BSD per sibling pattern — verification before any adapter code reuse.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: a future `reference/perception-runtime/` or `reference/sensor-runtime/` package with `MicroStrainAdapter`. Out of scope here.
- Conformance: a future `microstrain_cv7_cell.yaml` manifest fixture + positive conformance case after the IMU-measurement-type Spec RFC clarifies the enum.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Three Spec-RFC gaps surfaced.** IMU-class measurement_types, INS fusion declaration, NTRIP-correction declaration. All queued; none closed here.
- **License classifier ambiguity.** Repo classifier is NOASSERTION; in-repo LICENSE file needs reading before adapter code can rely on it.

## Alternatives considered

1. **Use `voltage` measurement_type for IMU outputs.** Rejected. URML's other adapters (Marty RFC-0073, Zivid RFC-0035) have used `custom` for non-enum measurement classes; consistency matters.
2. **Wait for the IMU-measurement-type Spec RFC.** Rejected. Vendor feedback on the manifest shape is what informs that Spec RFC.
3. **Combine MicroStrain + SBG + InvenSense + Xsens into a single "IMU consortium" RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor.

## Prior art

- [`LORD-MicroStrain/microstrain_inertial`](https://github.com/LORD-MicroStrain/microstrain_inertial) — the upstream driver.
- [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — parallel IMU/INS RFC, FR origin.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) — parallel GNSS RFC, BE origin.
- [RFC-0120 (NovAtel)](0120-novatel-hexagon-outreach.md) — parallel GNSS+INS RFC, CA origin.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) — engagement-driven adapter-ship pattern.

## Unresolved questions

For the `LORD-MicroStrain/microstrain_inertial` maintainers:

1. **License clarification.** The repo classifier shows NOASSERTION; could you confirm the SPDX in-repo (MIT? BSD-3-Clause? other?) so URML's adapter code reuse posture is unambiguous?
2. **IMU measurement-type shape.** URML's v0.1 enum has no `acceleration` / `angular_velocity` / `orientation` types — would a Spec RFC adding these (parallel to RFC-0039's `point_cloud`) be useful from an INS vendor's perspective, or is the `custom` escape-hatch sufficient?
3. **INS fusion declaration.** 3DM-GQ7 emits fused pose. Should URML's manifest declare "this device emits GNSS-aided INS pose" as a first-class fact, or is that better surfaced through the application layer?
4. **RTK / NTRIP-correction declaration.** The MicroStrain NTRIP client repo handles correction streams; URML's manifest has no NTRIP declaration today. Is "this INS accepts NTRIP corrections from constellations X / Y / Z" something the manifest should carry?
5. **Adapter home.** When the URML-side `MicroStrainAdapter` ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `LORD-MicroStrain/microstrain-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
6. **Conformance listing.** Would the MicroStrain team consider a README link to URML's compatible-runtimes registry once a working adapter ships and a real-hardware run is recorded? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0117 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## Requested feedback (from LORD-MicroStrain maintainers)

Items 1–7 from Unresolved questions above.

## How to respond

`LORD-MicroStrain/microstrain_inertial` has Issues enabled. URML's planned channel: open a single Issue labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `LORD-MicroStrain/microstrain_inertial` surface (133 stars, 33 open issues, Issues enabled, last commit 2026-05-21, 28-repo vendor org).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, three Spec-RFC gaps, license classifier ambiguity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: MicroStrain by HBK, US; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
