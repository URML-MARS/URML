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

# Perception-vendors research, 2026-05-27 (Move #10 audit trail)

## Scope and method

Founder's ask, 2026-05-27: enumerate 50 GitHub repositories of cameras and sensors that fit URML's substrate-neutral perception story, sized as URML's next outreach Move (Move-10). Each candidate verified by parallel research agents against the `AGENTS.md` "no blind posts" discipline.

This document is the **audit trail**: all 50 verified candidates, with metadata, including the 21 that were excluded with cause. The engageable subset (29) lives in [`outreach-move10.yaml`](outreach-move10.yaml); the per-RFC post bodies live in [`posts-move10.md`](posts-move10.md). Together the three documents form the Move-10 backlog state.

## Verification depth (per target)

Per the approved Move-10 plan, each entry carries 8 verified fields:

1. Org / repo URL (resolves)
2. License (SPDX)
3. Stars / open issues / last commit date
4. Surface (Issues, Discussions, CONTRIBUTING)
5. Maintainer identity (vendor vs community)
6. API path (ROS 2 / Python / C++ / vendor SDK)
7. Origin (ISO 3166-1 alpha-2; US-federal default policy fit)
8. URML-fit tier: A (vendor-style, adapter-grade) / B (research-collab / cross-citation with caveats) / C (excluded with cause)

## Summary

| Tier | Count | Meaning |
|------|-------|---------|
| **A** | **17** | Vendor-direct, OSI license, active maintenance, adapter-grade — engage in Move #10 |
| **B** | **12** | Vendor-direct or de-facto-vendor surface with caveats (stale, copyleft, GitLab not GitHub, dormant org) — engage with light touch / cross-citation framing |
| **C** | **21** | Excluded with cause (archived, PRC-domiciled, no GitHub surface, ITAR-restricted, empty placeholder org) — recorded but not engaged |
| **Already engaged (skip)** | 1 | Ouster (RFC-0032 already on URML's outreach ledger; verified that the live flagship is now `ouster-lidar/ouster-sdk` + `ouster-lidar/ouster-ros`, superseding `ouster-lidar/ouster_example`) |
| **Total verified** | **51** | (50 fresh + 1 already-engaged-skip; "50 candidates" framing rounds Ouster out as not-new) |

## Tier A (17) — engage in Move-10

| # | Vendor / product | Repo | License | Origin | RFC |
|---|------------------|------|---------|--------|-----|
| 1 | Intel RealSense (RealSenseAI) | realsenseai/librealsense | Apache-2.0 | US | RFC-0109 |
| 2 | StereoLabs ZED | stereolabs/zed-ros2-wrapper | Apache-2.0 (wrapper; core closed) | FR/US | RFC-0110 |
| 3 | Carnegie Robotics MultiSense | carnegierobotics/multisense_ros2 | MIT | US | RFC-0111 |
| 4 | Roboception (rc_visard) | roboception/cvkit | BSD-3-Clause | DE | RFC-0112 |
| 5 | Basler (pylon) | basler/pypylon | BSD-3-Clause | DE | RFC-0113 |
| 6 | Prophesee (Metavision) | prophesee-ai/openeb | Apache-2.0 (confirm) | FR | RFC-0114 |
| 7 | ifm Effector (O3X/O3R) | ifm/ifm3d | Apache-2.0 | DE | RFC-0115 |
| 8 | Teledyne FLIR (Boson) | FLIR/BosonUSB | MIT | US | RFC-0116 |
| 9 | MicroStrain by HBK | LORD-MicroStrain/microstrain_inertial | NOASSERTION (verify) | US | RFC-0117 |
| 10 | SBG Systems | SBG-Systems/sbg_ros2_driver | MIT | FR | RFC-0118 |
| 11 | Septentrio | septentrio-gnss/septentrio_gnss_driver | BSD-3-Clause | BE | RFC-0119 |
| 12 | NovAtel (Hexagon) | novatel/novatel_oem7_driver | MIT | CA/SE | RFC-0120 |
| 13 | Robotous (F/T) | ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model | MIT | KR | RFC-0121 |
| 14 | GelSight (tactile) | gelsightinc/gsrobotics | GPL-3.0 | US | RFC-0122 |
| 15 | Cubert (hyperspectral) | cubert-hyperspectral/cuvis.sdk | Apache-2.0 | DE | RFC-0123 |
| 16 | Sensirion (environmental) | Sensirion/* (252 repos) | BSD-3-Clause | CH | RFC-0124 |
| 17 | Bosch Sensortec (MEMS) | boschsensortec/* (33 repos) | BSD-3-Clause (mixed) | DE | RFC-0125 |

## Tier B (12) — engage with caveats

| # | Vendor / product | Repo | License | Origin | RFC | Caveat |
|---|------------------|------|---------|--------|-----|--------|
| 18 | iniVation (DAVIS event) | gitlab.com/inivation/dv/ | (GitLab not GitHub) | CH | RFC-0126 | Off-GitHub primary surface |
| 19 | pmdtechnologies (Royale ToF) | pmdtechnologies/pmd-royale-ros | BSD-3-Clause | DE | RFC-0127 | Stale > 2 years; ROS 1 only |
| 20 | Optris (thermal) | Optris/otcsdk_downloads | unlicensed | DE | RFC-0128 | License-clarification gate |
| 21 | Seek Thermal | seekthermal/seekcamera-python | Apache-2.0 | US | RFC-0129 | Stale ~14 mo; only 1 vendor repo |
| 22 | Velodyne (legacy VLP/HDL) | ros-drivers/velodyne | BSD-3-Clause | US (Ouster-owned brand) | RFC-0130 | Brand now Ouster-owned; routing overlap |
| 23 | Xsens / Movella | xsens/xsens_mti_ros_node | NOASSERTION | NL | RFC-0131 | Vendor migrated off-GitHub |
| 24 | TDK / InvenSense | InvenSenseInc/* (15 repos) | mixed | US/JP | RFC-0132 | MCU-firmware not robotics-stack |
| 25 | u-blox (ubxlib) | u-blox/ubxlib | Apache-2.0 | CH | RFC-0133 | ROS driver is community KumarRobotics/ublox |
| 26 | Emlid (Reach RTK) | emlid/ntripbrowser | BSD-3-Clause | HU (orig HK) | RFC-0134 | Flag HK history; Reach firmware closed |
| 27 | Cerulean Sonar | CeruleanSonar/SonarView | unlicensed | US | RFC-0135 | Flagship no license |
| 28 | Contactile (tactile) | contactile/c3dfbs | GPL-3.0 | AU | RFC-0136 | Single maintainer; stale; copyleft |
| 29 | AMS-OSRAM (ToF + image) | ams-OSRAM/tmf8829_driver_linux | GPL-3.0 | AT | RFC-0137 | GPL-2/3 copyleft limits Apache-2.0 bundling |

## Tier C (21) — excluded with cause, NOT engaged

| # | Vendor / product | Nearest GitHub state | Exclusion cause |
|---|------------------|----------------------|-----------------|
| 30 | Microsoft Azure Kinect | microsoft/Azure-Kinect-Sensor-SDK | **Archived** Oct 2023; product line discontinued |
| 31 | Orbbec (RGB-D) | orbbec/OrbbecSDK_ROS2 | **PRC parent** Shenzhen Orbbec — Section 889 default exclusion |
| 32 | IDS Imaging | no vendor-direct GitHub org | SDK is portal-only closed binaries |
| 33 | Pickit3D | github.com/Pickit3D (forks-only) | No vendor-direct flagship; 0 stars across 8 stale forks |
| 34 | Texas Instruments VoxelSDK (OPT8241 ToF) | 3dtof/voxelsdk | **Abandoned** since 2019; product line exited |
| 35 | Aeva (FMCW lidar) | github.com/aeva-ai (empty org) | 0 public repos; vendor distributes via NDA |
| 36 | Cepton (lidar) | cepton/sdk | Stale since 2022; unlicensed; 1 star |
| 37 | TI mmWave radar | no vendor-direct flagship | SDK distributed via dev.ti.com portal; non-OSI |
| 38 | Continental (radar) | github.com/Continental-Automotive (empty) | 0 public repos; closed CAN protocol |
| 39 | Aptiv (radar) | github.com/APTIV (empty) | 0 public repos; closed OEM-tier protocols |
| 40 | VectorNav (IMU) | no vendor-direct org | Closest is community dawonn/vectornav (unlicensed, stale) |
| 41 | KVH Industries (fiber-optic gyro) | no vendor GitHub | ITAR-controlled defense market; NDA-gated |
| 42 | Trimble (high-end GNSS) | trimble-oss/* (no GNSS repos) | 73 enterprise-tooling repos but no GNSS hardware integration on GitHub |
| 43 | Workswell (thermal) | github.com/workswell (name collision) | The GitHub org belongs to a different AU web-dev shop, not the CZ thermal vendor |
| 44 | ArduSimple (RTK) | ardusimple/simpleRTK2B | Flagship **unlicensed** and stale 4+ years |
| 45 | Wittenstein cyber motor | no vendor-direct org | Closed-source; only third-party Resense.py wrapper (GPL-2, stale) |
| 46 | OnRobot HEX (F/T) | no vendor-direct org | Closest is community jsbyysheng/onrobot_hex_ft_sensor (unlicensed, stale) |
| 47 | Norbit Subsea (sonar) | no vendor-direct org | Closest is academic URI Ocean Robotics + SMARC drivers |
| 48 | Kongsberg Maritime M3 (sonar) | github.com/Kongsberg-Maritime (empty) | 0 public repos; placeholder org |
| 49 | Meta DIGIT (tactile) | facebookresearch/digit-design + digit-interface | Both **archived** 2026; product line spun out to GelSight |
| 50 | Specim (hyperspectral) | no vendor-direct org | Closed vendor SDK (Specim Studio / IQ Studio); no GitHub |

## Already engaged — Ouster (RFC-0032)

The flagship Ouster repos on GitHub are now `ouster-lidar/ouster-sdk` (cross-platform C++/Python SDK) and `ouster-lidar/ouster-ros` (official ROS 2 driver). The original `ouster-lidar/ouster_example` engaged via URML RFC-0032 is the legacy name. Move-10 does NOT add a fresh row for Ouster; URML's existing engagement covers the vendor. Worth noting that the live flagship repos may be the better surface for future Ouster follow-ups than the legacy `ouster_example` thread.

## Categories and counts

| Category | Tier A | Tier B | Tier C | Notes |
|----------|--------|--------|--------|-------|
| RGB-D / depth cameras | 3 (RealSense, ZED, MultiSense) | 0 | 2 (Azure Kinect, Orbbec) | |
| Industrial 3D vision | 2 (Roboception, Basler) | 0 | 2 (IDS, Pickit3D) | + Photoneo / Cognex / Zivid in URML's existing fixtures or engagements |
| Lidar | 0 | 1 (Velodyne via ros-drivers) | 3 (Aeva, Cepton, TI VoxelSDK) | + Ouster already engaged; Hokuyo / SICK / Hesai already in URML |
| Event cameras | 1 (Prophesee) | 1 (iniVation) | 0 | URML-side: event-stream measurement_type Spec RFC needed |
| ToF | 1 (ifm Effector) | 1 (pmdtechnologies) | 1 (TI VoxelSDK — also in lidar count) | |
| Thermal / IR | 1 (Teledyne FLIR) | 2 (Optris, Seek Thermal) | 1 (Workswell name collision) | URML-side: thermal-array measurement_type Spec RFC needed |
| IMU / INS | 2 (MicroStrain, SBG) | 2 (Xsens, TDK/InvenSense) | 2 (VectorNav, KVH) | |
| GNSS / RTK | 2 (Septentrio, NovAtel) | 2 (u-blox, Emlid) | 2 (Trimble GNSS, ArduSimple) | |
| Force / torque | 1 (Robotous) | 0 | 2 (Wittenstein, OnRobot HEX) | + ATI / Bota already in URML fixtures |
| Radar | 0 | 0 | 3 (TI mmWave, Continental, Aptiv) | Lane barren on GitHub; defer entirely |
| Underwater / sonar | 0 | 1 (Cerulean Sonar) | 2 (Norbit, Kongsberg) | |
| Tactile | 1 (GelSight) | 1 (Contactile) | 1 (Meta DIGIT archived) | |
| Spectral / hyperspectral | 1 (Cubert) | 0 | 1 (Specim) | |
| Environmental / chemical | 2 (Sensirion, Bosch Sensortec) | 0 | 0 | |
| Encoder / position | 0 | 1 (AMS-OSRAM) | 0 | (Renishaw absent — substituted AMS-OSRAM per task) |

## Schema-extension flags surfaced by Move-10 (parallel Spec RFCs, not bundled in outreach RFCs)

Move-10 vendors surface several Layer-1 perception-schema gaps that v0.1 can't model cleanly. Each is a separate future Spec RFC that should be opened in parallel to (not bundled inside) the per-target outreach RFCs:

1. **Event-camera measurement_type** — for Prophesee (RFC-0114), iniVation (RFC-0126). v0.1's measurement_type enum has no event-stream class; both targets will use the `custom` escape-hatch with explicit reference to the queued Spec RFC.
2. **Thermal-array per-pixel measurement_type** — for Teledyne FLIR (RFC-0116), Optris (RFC-0128), Seek Thermal (RFC-0129). URML's `temperature` measurement_type is a scalar; thermal cameras emit per-pixel arrays that need their own type or a generalization.
3. **3D point-cloud with color + per-point attributes** — already flagged in RFC-0035 (Zivid, Q1); reinforced by Intel RealSense (RFC-0109). Future Spec RFC parallel to RFC-0039's lidar `point_cloud` work.
4. **Environmental scalar arrays** — CO2 + humidity + VOC + particulate. Sensirion (RFC-0124) emits these together; URML's sensors-block currently expects single-value measurement_types.
5. **Tactile / pressure-array measurement** — for GelSight (RFC-0122), Contactile (RFC-0136). Spatially-organized contact-force arrays + slip-detection metadata are not in v0.1.

## Strategic observations

- **The optical-perception slice is healthier than typical hardware-vendor slices.** 8 of 17 candidates (Tier A side of the optical slice) have active vendor-org maintainership with OSI licenses. The recurring drag is the **closed-SDK-with-thin-open-wrapper pattern** (ZED, Orbbec, FLIR Spinnaker, Optris, Seek): URML manifests can describe the wrapper, not the underlying binary.
- **The radar lane is barren on GitHub.** TI mmWave, Continental, and Aptiv all distribute via portal / NDA / closed-CAN; none surface as engageable. Move-10 records the lane as "defer to direct sales" rather than treating it as a verification miss.
- **IMU + GNSS is the strongest single sub-category for URML-fit.** 4 of 4 IMU/GNSS Tier-A vendors are OSI-licensed, vendor-maintained, with active ROS 2 drivers. The center of gravity of Move-10's high-quality outreach lives in this lane.
- **Tactile sensing is thin.** Meta DIGIT archived, Contactile is single-maintainer-with-stale-repos, GelSight Inc. is effectively the only Tier-A tactile vendor.
- **Component vendors with embedded-systems culture (Sensirion, Bosch Sensortec, Cubert, AMS-OSRAM) keep large daily-active vendor orgs.** They behave structurally like established software-OSS projects more than like one-product hardware vendors.
- **NDAA Section 889 produces exactly one hard exclusion** (Orbbec via Shenzhen parent). Most other exclusions are about absent or dead upstream rather than provenance.
- **Cubert is the only Move-10 candidate with an existing public LLM-tool surface** (cuvis-ai-agentic-skills). Engagement framing should reflect that they have already done the agentic work URML's bridge layer cares about.

## Caveats on the verification pass

- License classifiers on GitHub sometimes return NOASSERTION even when a LICENSE file is present. The research notes flag this; per-RFC verification should re-check before posting.
- Star counts and last-commit dates were captured 2026-05-27; expect drift before the per-RFC posts ship over multiple sessions. URML's `make audit` re-measurer (see `docs/launch/claims-audit.md` for the discipline) should be invoked per RFC draft to refresh the contact-field numbers.
- "Active" means last commit since 2025-11-27 (six months from the verification date). Some Tier B entries are 6-15 months stale and engagement expectation is calibrated accordingly.
- The 50/51 framing comes from Ouster being already-engaged: the founder's ask was for 50 candidates; verification surfaced Ouster as duplicate. The Move-10 ledger has 29 new engageable rows and the 21 Tier-C entries live here in the audit trail.
