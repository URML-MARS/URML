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

# Move #10 post bodies — perception vendors (cameras + sensors)

Copy-paste-ready Issue / Discussion / Contact-form bodies for the Move #10 perception-vendor outreach. **Wave shape**: 29 engageable targets verified 2026-05-27 across 15 sensor sub-categories (17 Tier A vendor-style + 12 Tier B research-collab / cross-citation with caveats). RFC numbers reserved 0109-0137; each per-target body lands in a separate future session as the RFC drafts.

Ledger state: [`outreach-move10.yaml`](outreach-move10.yaml). Full research audit (including 21 Tier C exclusions): [`perception-vendors-research-2026-05-27.md`](perception-vendors-research-2026-05-27.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts (`reference/marine-runtime/`, `reference/edu-runtime/`, RFCs in `docs/rfcs/`) are fine to cite. Aggregate counts ("ten outreach waves across URML's outreach to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #10 post ends with the one-paragraph authoring-disclosure line.

**Schema-extension flags.** Move #10 surfaces multiple v0.1 Layer-1 perception-schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- Event-camera measurement_type (for Prophesee RFC-0114, iniVation RFC-0126).
- Thermal-array per-pixel measurement_type (for Teledyne FLIR RFC-0116, Optris RFC-0128, Seek Thermal RFC-0129).
- Color + per-point attributes on 3D point clouds (already flagged in RFC-0035 Zivid round; reinforced by Intel RealSense RFC-0109).
- Environmental scalar arrays (CO2 + humidity + VOC) for Sensirion RFC-0124.
- Tactile / pressure-array measurement (for GelSight RFC-0122, Contactile RFC-0136).

Each is a separate Spec RFC; URML's outreach RFCs can ship with the v0.1 `custom` measurement_type escape-hatch and reference the queued Spec RFC.

---

## Tier A — 17 vendor-style targets

### RFC-0109: Intel RealSense
**Post to**: https://github.com/realsenseai/librealsense/issues/new (Issues enabled). Body TBD when RFC drafts.

### RFC-0110: StereoLabs ZED
**Post to**: https://github.com/stereolabs/zed-ros2-wrapper/issues/new (Issues enabled). Body TBD.

### RFC-0111: Carnegie Robotics MultiSense
**Post to**: https://github.com/carnegierobotics/multisense_ros2/issues/new (Issues enabled). Body TBD.

### RFC-0112: Roboception (rc_visard)
**Post to**: https://github.com/roboception/cvkit/issues/new (Issues enabled). Body TBD.

### RFC-0113: Basler (pylon)
**Post to**: https://github.com/basler/pypylon/issues/new (Issues enabled). Body TBD.

### RFC-0114: Prophesee (Metavision / event cameras)
**Post to**: https://github.com/prophesee-ai/openeb/issues/new (Issues enabled). Body TBD. **Schema-extension flag**: event-camera measurement_type Spec RFC.

### RFC-0115: ifm Effector (O3X / O3R)
**Post to**: https://github.com/ifm/ifm3d/discussions/new (Discussions preferred per repo settings). Body TBD.

### RFC-0116: Teledyne FLIR (Boson)
**Post to**: https://github.com/FLIR/BosonUSB/issues/new (Issues enabled). Body TBD. **Schema-extension flag**: thermal-array per-pixel measurement_type Spec RFC.

### RFC-0117: MicroStrain / HBK
**Post to**: https://github.com/LORD-MicroStrain/microstrain_inertial/issues/new (Issues enabled). Body TBD.

### RFC-0118: SBG Systems
**Post to**: https://github.com/SBG-Systems/sbg_ros2_driver/issues/new (Issues enabled). Body TBD.

### RFC-0119: Septentrio
**Post to**: https://github.com/septentrio-gnss/septentrio_gnss_driver/issues/new (Issues enabled). Body TBD.

### RFC-0120: NovAtel (Hexagon)
**Post to**: https://github.com/novatel/novatel_oem7_driver/discussions/new (Discussions enabled). Body TBD.

### RFC-0121: Robotous
**Post to**: https://github.com/ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model/issues/new (Issues enabled). Body TBD. Note: fresh vendor org (Feb 2026); light touch.

### RFC-0122: GelSight
**Post to**: https://github.com/gelsightinc/gsrobotics/issues/new (Issues enabled). Body TBD. **License caveat**: GPL-3.0; cross-citation framing rather than bundled adapter. **Schema-extension flag**: tactile / pressure-array measurement Spec RFC.

### RFC-0123: Cubert (hyperspectral)
**Post to**: https://github.com/cubert-hyperspectral/cuvis.sdk/issues/new (Issues enabled). Body TBD. Highest-leverage angle: Cubert's existing cuvis-ai-agentic-skills LLM-tool surface.

### RFC-0124: Sensirion (environmental)
**Post to**: TBD (per-sensor repo with most engagement; likely Sensirion/embedded-i2c-scd30 or similar). Body TBD. **Schema-extension flag**: environmental scalar arrays Spec RFC.

### RFC-0125: Bosch Sensortec (MEMS)
**Post to**: TBD (per-sensor repo; likely boschsensortec/BHI385_SensorAPI or BME690_SensorAPI). Body TBD.

---

## Tier B — 12 research-collab / cross-citation targets

### RFC-0126: iniVation (DAVIS event cameras)
**Post to**: TBD — GitLab vs GitHub pipeline-scope decision is the gating question. iniVation development lives on gitlab.com/inivation/dv/. Body TBD.

### RFC-0127: pmdtechnologies (Royale ToF)
**Post to**: https://github.com/pmdtechnologies/pmd-royale-ros/issues/new (Issues enabled, vendor stale > 2 years). Body TBD; expect slow response.

### RFC-0128: Optris (thermal)
**Post to**: https://github.com/Optris/otcsdk_downloads/issues/new (Issues enabled). Body TBD. License-clarification gate first.

### RFC-0129: Seek Thermal
**Post to**: https://github.com/seekthermal/seekcamera-python/issues/new (Issues enabled, stale ~14 mo). Body TBD.

### RFC-0130: Velodyne (via ros-drivers)
**Post to**: https://github.com/ros-drivers/velodyne/issues/new (Issues enabled). Body TBD. **Routing question**: Velodyne brand is Ouster-owned post-2023; engagement may belong on the existing Ouster (RFC-0032) thread rather than as a separate Move-10 RFC.

### RFC-0131: Xsens / Movella
**Post to**: https://github.com/xsens/xsens_mti_ros_node/issues/new (Issues enabled, repo stale ~7 years). Body TBD. Ask: GitHub revival vs off-GitHub tarball is the canonical surface?

### RFC-0132: TDK / InvenSense
**Post to**: TBD (per-repo on InvenSenseInc org; firmware-MCU-level not robotics-stack-level). Body TBD; cross-citation framing.

### RFC-0133: u-blox (ubxlib + KumarRobotics/ublox)
**Post to**: https://github.com/u-blox/ubxlib/issues/new (Issues enabled) + cross-cite https://github.com/KumarRobotics/ublox community ROS driver. Body TBD.

### RFC-0134: Emlid Reach
**Post to**: https://github.com/emlid/ntripbrowser/issues/new (Issues enabled). Body TBD. Flag HK-registration history for US-federal-procurement deployments.

### RFC-0135: Cerulean Sonar
**Post to**: https://github.com/CeruleanSonar/SonarView/issues/new (Issues enabled, flagship no license — license-clarification gate first). Body TBD. Cross-link existing URML marine-runtime (BlueRovAdapter).

### RFC-0136: Contactile (tactile)
**Post to**: https://github.com/contactile/c3dfbs/issues/new (Issues enabled). Body TBD. Light touch; community ROS 2 wrapper at mgonzs13/contactile_ros is the practical leverage point.

### RFC-0137: AMS-OSRAM (ToF + image sensors)
**Post to**: https://github.com/ams-OSRAM/tmf8829_driver_linux/issues/new (Issues enabled). Body TBD. GPL-2/3 copyleft; cross-citation / manifest-component framing.

---

## Tier C (21) — recorded in research file, NOT engaged

See [`perception-vendors-research-2026-05-27.md`](perception-vendors-research-2026-05-27.md) for the full Tier-C list with exclusion causes. No posts; these are URML's "investigated and chose not to pursue" record so the negative space is auditable.
