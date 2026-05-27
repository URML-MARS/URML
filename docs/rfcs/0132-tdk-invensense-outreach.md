---
rfc: 0132
title: TDK / InvenSense (ICM/IIM MEMS IMU) integration, request for comment from InvenSenseInc maintainers
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

# RFC-0132: TDK / InvenSense (ICM/IIM MEMS IMU) integration, request for comment from InvenSenseInc maintainers

## Summary

URML does not yet ship a TDK / InvenSense manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for TDK's InvenSense ICM/IIM MEMS IMU catalog (ICM-20948, ICM-42688, IIM-42652) over the [`InvenSenseInc`](https://github.com/InvenSenseInc) GitHub organization (15 public vendor repos), and **requests review and feedback from the InvenSenseInc maintainers**. No spec change.

This RFC complements [RFC-0125 (Bosch Sensortec)](0125-bosch-sensortec-outreach.md). Bosch and TDK / InvenSense together are the two dominant low-power MEMS IMU vendors. The URML-fit framing for TDK is more conservative than Bosch: TDK's GitHub content is MCU-firmware level (`tdk_robokit`, `tdk_robotics_rbx_apps`), one layer below URML's robotics-stack adapter surface; cross-citation is the recommended shape.

## Motivation

[InvenSenseInc](https://github.com/InvenSenseInc) is the GitHub presence of TDK's MEMS IMU business (post-2017 TDK acquisition of InvenSense). Fifteen public repos cover firmware, application code (tdk_robokit, tdk_robotics_rbx_apps with Apache-2.0), and driver code (tdk_robotics_rbx_drivers_code, NOASSERTION). Top star counts are modest (~6); last commits in the 2020-2021 range — the vendor org is real but quiet on GitHub.

URML's outreach is vendor-direct first. TDK's ICM-20948 and ICM-42688 lineage powers a large fraction of consumer / hobby / educational IMUs (every typical "9-DoF breakout board" carries an InvenSense part). For URML's micro-class robot story (RFC-0018 `microbit_edu` pattern), the InvenSense parts are present even when the vendor name does not appear on the bill of materials.

**The framing question this RFC asks:** does TDK want URML's outreach to live at the IC-vendor level (here), at the OEM-integrator level (Bosch's pattern via RFC-0125), or only as cross-citation in URML's docs?

## Detailed design

### URML v0.1 capability-manifest mapping (planned `tdk_icm_cell.yaml` fixture)

`Sensor` block, multi-measurement IMU:

| URML field | Maps to TDK / InvenSense product attribute |
|---|---|
| `name: imu` (Sensor) | ICM-20948 / ICM-42688 / IIM-42652 9-axis or 6-axis IMU |
| `measurement_type: custom` (acceleration) | Linear acceleration — v0.1 has no native `acceleration` |
| `measurement_type: custom` (angular_velocity) | Angular velocity |
| `measurement_type: custom` (magnetic_field) | Built-in 3-axis magnetometer on -20948 (AK09916 chip die) |
| `measurement_type: custom` (orientation) | DMP-fused orientation on parts with Digital Motion Processor |

### What URML v0.1 does not yet express for TDK / InvenSense

1. **IMU measurement_types** (`acceleration` / `angular_velocity` / `orientation` / `magnetic_field`) — same gap shared with RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131; one Spec RFC covers all.
2. **MCU-firmware vs robotics-stack content level.** TDK's GitHub repos sit at the embedded-firmware-MCU layer; URML adapters live one layer up. The manifest can declare IC presence but the adapter shape is not natural for this layer.
3. **DMP (Digital Motion Processor) on-chip fusion declaration.** ICM-20948 etc. ship an on-chip DMP; URML's manifest cannot today express which DMP firmware is active. Same closed-fusion question as RFC-0125.

### Compatibility notes

- **Vendor org.** [`InvenSenseInc`](https://github.com/InvenSenseInc) — 15 public repos.
- **Active repos.** `tdk_robokit`, `tdk_robotics_rbx_apps` (Apache-2.0), `tdk_robotics_rbx_drivers_code` (NOASSERTION).
- **Repo state.** Top stars ~6; last commits 2020-2021 (older than URML's 6-month recency window from 2026-05-27; vendor org quiet but not abandoned).
- **Origin.** TDK Corporation (Tokyo, Japan) acquired InvenSense (San Jose, CA, US) in 2017. Dual JP / US presence. Passes US-federal default policy (allied + US presence).
- **License fit.** Apache-2.0 on robokit / rbx_apps (clean fit); NOASSERTION on drivers (license clarification needed for adapter-grade reuse).
- **Maintainer signal.** Vendor org real; GitHub activity modest. Likely vendor engagement happens off-GitHub.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; IMU measurement_type Spec RFC queued in parallel (shared with RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131).
- Reference runtime: cross-citation recommended over adapter; if engagement settles on adapter, future `reference/sensor-runtime/TdkIcmAdapter` would target the MCU-firmware-host bridge layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Content-level mismatch.** TDK's GitHub presence is MCU-firmware-level; URML's adapter pattern lives at the robotics-stack layer. Cross-citation may be the only honest shape.
- **NOASSERTION license on the driver repo** blocks adapter-grade reuse without clarification.
- **IMU-type Spec RFC prerequisite.** Same gap as RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131.

## Alternatives considered

1. **Cross-citation only (no adapter, no fixture).** The most likely outcome given content-level mismatch.
2. **Engage TDK at the IC-vendor level (here) and Bosch at the module-integrator level (RFC-0125).** Considered. The two vendor surfaces look superficially similar; in practice the URML-fit case is stronger for Bosch's vendor-direct module sensors than for TDK's MCU-firmware repos.
3. **Bundle TDK + Bosch into one MEMS-IMU RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; the URML-fit framing differs between them and one RFC would conflate.

## Prior art

- [`InvenSenseInc`](https://github.com/InvenSenseInc) — the upstream organization.
- [RFC-0125 (Bosch Sensortec)](0125-bosch-sensortec-outreach.md) — sibling MEMS-IMU vendor RFC; Bosch is the comparison case.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) + [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) + [RFC-0131 (Xsens / Movella)](0131-xsens-movella-outreach.md) — sibling IMU/INS RFCs sharing the IMU-type Spec-RFC gap.
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md) Draft — the micro-class robot manifest pattern that InvenSense parts naturally populate.

## Unresolved questions

For the InvenSenseInc maintainers:

1. **Engagement-level preference.** Should URML engage TDK at the IC-vendor level (here), at the OEM-integrator level (cross-cite via Bosch-pattern only), or only as documentation cross-reference?
2. **Driver-repo license.** Can `tdk_robotics_rbx_drivers_code` get an explicit OSI license declaration?
3. **DMP declaration.** On-chip DMP firmware varies by part and configuration. Should URML's manifest declare which DMP configuration is active, and at what granularity?
4. **IMU manifest fields.** Same questions as RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131. Manifest-field expectations from TDK's perspective?
5. **Anything else.**

## Implementation note

RFC-0132 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml). Cross-citation framing is the recommended posture.

## How to respond

`InvenSenseInc` has 15 public repos; URML's planned channel: open a single Issue on the most-active repo (likely `tdk_robokit` or `tdk_robotics_rbx_apps`) labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement that cross-citation may be the right shape.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (15 vendor repos, Apache-2.0 + NOASSERTION mix, top stars ~6, last commits 2020-2021).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (content-level mismatch, NOASSERTION on drivers, IMU-type Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: TDK (JP) / InvenSense (US); default policy passes.
- [x] CLAUDE.md compliance check passed.
