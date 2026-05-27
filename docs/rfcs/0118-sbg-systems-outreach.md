---
rfc: 0118
title: SBG Systems (Ellipse / Quanta IMU / INS) integration, request for comment from SBG-Systems maintainers
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

# RFC-0118: SBG Systems (Ellipse / Quanta IMU / INS) integration, request for comment from SBG-Systems maintainers

## Summary

URML does not yet ship an SBG Systems manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for SBG's Ellipse / Quanta IMU / AHRS / INS line over [`SBG-Systems/sbg_ros2_driver`](https://github.com/SBG-Systems/sbg_ros2_driver) (MIT-licensed ROS 2 driver) and the sibling ROS 1 driver, and **requests review and feedback from the SBG-Systems maintainers**. No spec change.

## Motivation

`SBG-Systems/sbg_ros2_driver` is one of the cleanest IMU/INS surfaces URML's Move #10 verification surfaced: MIT-licensed (cleaner inbound-equals-outbound than the NOASSERTION patterns on some sibling IMU vendor repos), dual ROS 1 / ROS 2 coverage, vendor-org maintained, active (last commit ~3 months from verification). SBG Systems (Carrières-sur-Seine, FR) is NATO-allied origin; URML's US-federal default policy passes cleanly.

URML's IMU/INS lane is the strongest URML-fit sub-category in Move #10 — four Tier-A vendors (MicroStrain, SBG, Septentrio, NovAtel) share clean OSI + active maintainership. SBG sits in the middle-of-the-line space: smaller form-factor Ellipse for cost-sensitive deployments, Quanta for survey-grade INS, Apogee for high-precision. Their dual ROS-version coverage is a maintenance signal worth pairing with URML's substrate-neutrality story.

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `sbg_ellipse_cell.yaml` fixture)

`Sensor` block (no `Camera` involvement):

| URML field | Maps to SBG product attribute |
|---|---|
| `name: imu` (Sensor) | Ellipse-A/E AHRS, Quanta-N INS, or similar |
| `measurement_type: acceleration` (custom) | Linear acceleration; v0.1 enum has no `acceleration` |
| `measurement_type: custom` (angular_velocity) | Angular velocity; same enum gap |
| `measurement_type: custom` (orientation) | Quaternion orientation from EKF; same enum gap |
| `measurement_type: custom` (gnss_position) | Quanta-N / Apogee-N GNSS-aided INS position |
| `units` | `g`, `rad/s`, `m`, `degrees` per channel |

### What URML v0.1 does not yet express for SBG

Same three gaps as RFC-0117 (MicroStrain) — these are the IMU/INS lane's shared schema-extension questions:

1. **First-class IMU measurement_types** (`acceleration`, `angular_velocity`, `orientation`) — currently `custom`.
2. **INS fusion declaration** — Quanta-N emits fused pose; manifest can't declare the fusion fact today.
3. **RTK / NTRIP-correction declaration** — survey-grade SBG INS accepts NTRIP; manifest has no NTRIP block.

### Compatibility notes

- **Vendor org.** [`SBG-Systems/sbg_ros2_driver`](https://github.com/SBG-Systems/sbg_ros2_driver) (MIT, ROS 2), [`SBG-Systems/sbg_ros_driver`](https://github.com/SBG-Systems/sbg_ros_driver) (MIT, ROS 1). 21 public vendor repos.
- **Origin.** SBG Systems, Carrières-sur-Seine, FR. Passes US-federal default policy (NATO allied).
- **License fit.** MIT on the ROS drivers; cleanest license posture among the four Move-10 IMU/GNSS Tier-A vendors.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: a future `reference/perception-runtime/` or `reference/sensor-runtime/` package with `SbgEllipseAdapter` (or `SbgInsAdapter` covering Ellipse + Quanta + Apogee). Out of scope here.
- Conformance: a future `sbg_ellipse_cell.yaml` manifest fixture + positive conformance case after the IMU-measurement-type Spec RFC clarifies the enum.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Three Spec-RFC gaps surfaced** (same as RFC-0117 MicroStrain).
- **EKF vendor-specific behavior.** SBG's EKF is proprietary; URML's manifest can describe the outputs but not the fusion model. (Same constraint as any vendor-fused INS.)

## Alternatives considered

1. **Bundle SBG + MicroStrain into one INS RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor; the two engagements may yield different framings of the IMU-measurement-type Spec RFC.
2. **Wait for the IMU-measurement-type Spec RFC.** Rejected. SBG's feedback is part of what informs that Spec RFC.
3. **Use `voltage` measurement_type for raw analog IMU readouts.** Rejected (same reasoning as RFC-0117).

## Prior art

- [`SBG-Systems/sbg_ros2_driver`](https://github.com/SBG-Systems/sbg_ros2_driver) — the upstream ROS 2 driver.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) — parallel IMU/INS RFC, US origin.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) — parallel GNSS RFC, BE origin.
- [RFC-0120 (NovAtel)](0120-novatel-hexagon-outreach.md) — parallel GNSS+INS RFC, CA origin.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) — engagement-driven adapter-ship pattern.

## Unresolved questions

For the `SBG-Systems/sbg_ros2_driver` maintainers:

1. **IMU measurement-type shape.** URML's v0.1 enum has no `acceleration` / `angular_velocity` / `orientation` types — would a Spec RFC adding these (parallel to RFC-0039's `point_cloud`) be useful from SBG's perspective, or is the `custom` escape-hatch sufficient for now?
2. **INS fusion declaration.** Quanta-N / Apogee-N emit GNSS-fused pose with vendor EKF. Should URML's manifest declare "this device emits GNSS-aided INS pose" as a first-class fact?
3. **RTK / NTRIP-correction declaration.** Is "this INS accepts NTRIP corrections from constellations X / Y / Z" something the manifest should carry?
4. **Product-line coverage.** Should URML ship one adapter per product line (Ellipse / Quanta / Apogee), or one `SbgInsAdapter` parameterized by product? Your maintenance preference matters more than URML's instinct here.
5. **Adapter home.** When the URML-side adapter ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `SBG-Systems/sbg-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
6. **Conformance listing.** Would the SBG team consider a README link to URML's compatible-runtimes registry once a working adapter ships and a real-hardware run is recorded? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0118 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## Requested feedback (from SBG-Systems maintainers)

Items 1–7 from Unresolved questions above.

## How to respond

`SBG-Systems/sbg_ros2_driver` has Issues enabled. URML's planned channel: open a single Issue labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `SBG-Systems/sbg_ros2_driver` surface (MIT, 52 stars, 15 open issues, Issues enabled, last commit 2026-03-04).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, three Spec-RFC gaps, vendor-EKF opacity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: SBG Systems FR; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
