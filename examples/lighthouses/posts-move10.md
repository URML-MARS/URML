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

Copy-paste-ready Issue / Discussion / Contact-form bodies for the Move #10 perception-vendor outreach. **Wave shape**: 29 engageable targets verified 2026-05-27 across 15 sensor sub-categories (17 Tier A vendor-style + 12 Tier B research-collab / cross-citation with caveats). RFC numbers reserved 0109-0137; all 29 RFCs drafted on `main` as of 2026-05-27.

Ledger state: [`outreach-move10.yaml`](outreach-move10.yaml). Full research audit (including 21 Tier C exclusions): [`perception-vendors-research-2026-05-27.md`](perception-vendors-research-2026-05-27.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("ten outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #10 post ends with the one-paragraph authoring-disclosure line. Origin: 2026-05-26 OVOS RFC-0107 wontfix close.

**Schema-extension flags.** Move #10 surfaces multiple v0.1 Layer-1 perception-schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- Event-stream measurement_type (Prophesee RFC-0114, iniVation RFC-0126).
- Thermal-array per-pixel measurement_type (FLIR RFC-0116, Optris RFC-0128, Seek Thermal RFC-0129).
- Color + per-point attributes on 3D point clouds (Intel RealSense RFC-0109, reinforces RFC-0035 Zivid).
- Environmental scalar arrays (Sensirion RFC-0124).
- Tactile / pressure-array measurement (GelSight RFC-0122, Contactile RFC-0136).
- Spectral-cube measurement_type (Cubert RFC-0123).
- IMU measurement_types — acceleration / angular_velocity / orientation (MicroStrain RFC-0117, SBG RFC-0118, Bosch RFC-0125, Xsens RFC-0131, TDK RFC-0132).
- GNSS-class measurement_types (Septentrio RFC-0119, NovAtel RFC-0120, u-blox RFC-0133, Emlid RFC-0134).
- F/T 6-axis measurement_type (Robotous RFC-0121).
- Multi-zone / amplitude on ToF (ifm RFC-0115, pmdtechnologies RFC-0127, AMS-OSRAM RFC-0137).
- Sonar return-array measurement_type (Cerulean Sonar RFC-0135).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type escape-hatch and reference the queued Spec RFC.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier A — 17 vendor-style targets

### RFC-0109: Intel RealSense

**Post to:** https://github.com/IntelRealSense/librealsense/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for librealsense (D400 / D500 / L515)
```

**Body:**

```markdown
Hi @IntelRealSense team,

Proposing a URML v0.1 capability-manifest mapping for the Intel RealSense D400 / D500 / L515 family over `librealsense2`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

URML's perception story benefits from RealSense as the canonical depth-camera lineage. RealSense is also the strongest single example of a v0.1 schema gap URML's outreach has exposed: per-point color + per-point attributes on point clouds are first-class on RealSense (RGB-D + IMU + depth-confidence per pixel) but not yet first-class in URML's manifest (RFC-0039 introduced `point_cloud` as a scalar measurement_type without color/intensity sub-fields).

This is **proposal-only**, posted as part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs). No adapter in URML's repo yet; an adapter would ship engagement-driven.

Full RFC, with the manifest mapping table, v0.1 gaps, three alternatives considered, and detection-capability declaration as Q6: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0109-intel-realsense-outreach.md

Questions worth `librealsense` maintainer input on:

1. **Color + per-point attributes on point clouds.** Spec RFC queued; what manifest fields would a RealSense deployment expect (color, intensity, depth-confidence, IMU-timestamp)?
2. **Object-detection capability declaration.** RealSense modules ship with several depth-derived detection modes (face, object, gesture). Should URML's manifest declare supported detection classes so `query_detection` validates against actual capability?
3. **Adapter home.** URML repo (`reference/perception-runtime/`), Intel-maintained `IntelRealSense/realsense-urml`, or both?
4. **Conformance listing.** Would Intel consider a README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Happy to discuss any of these here, or via a different surface if you'd prefer.

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0110: Stereolabs ZED

**Post to:** https://github.com/stereolabs/zed-ros2-wrapper/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Stereolabs ZED (X / 2i / Mini)
```

**Body:**

```markdown
Hi @stereolabs team,

Proposing a URML v0.1 capability-manifest mapping for the Stereolabs ZED X / 2i / Mini family over `zed-ros2-wrapper` and the underlying ZED SDK. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + Layer-1 capability manifest + static validator.

ZED's GPU-accelerated depth pipeline plus on-board IMU/AHRS plus optional spatial AI (sk_/object detection) places it at the intersection of three v0.1 perception schema gaps URML's outreach is queueing: per-point color + intensity on point clouds, IMU measurement_types, and detection-capability declaration for `query_detection`.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0110-stereolabs-zed-outreach.md

Questions worth maintainer input on:

1. **Per-point attributes Spec RFC shape** (color + intensity + IMU-timestamp). Manifest-field expectations from a ZED deployment?
2. **Spatial AI declaration.** ZED's object-detection module ships supported-class lists; how should URML's manifest declare these so `query_detection` validates against actual capability?
3. **Adapter shape.** Should URML adapter target `zed-ros2-wrapper` (ROS-side), the C++ ZED SDK direct, or both layers?
4. **Adapter home.** URML repo (`reference/perception-runtime/`), Stereolabs-maintained, or both?
5. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0111: Carnegie Robotics MultiSense

**Post to:** https://github.com/carnegierobotics/multisense_ros2/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for MultiSense S-series stereo
```

**Body:**

```markdown
Hi @carnegierobotics team,

Proposing a URML v0.1 capability-manifest mapping for the MultiSense S-series stereo / lidar-stereo family over `multisense_ros2`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

MultiSense's combined stereo + lidar payload — well-deployed across legged robots, AUV / ROV, and field-mobile platforms — exercises URML's `cameras` + `sensors` block boundary in a way single-modality vendors don't. Same per-point-attributes + multi-modal-fusion schema-gaps URML's queued Spec RFCs target.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0111-carnegie-multisense-outreach.md

Questions worth maintainer input on:

1. **Stereo + lidar declaration.** Should URML's manifest express stereo and lidar as separate sensor blocks (current schema) or one fused-payload block?
2. **Per-point attributes Spec RFC shape** (intensity / range / time-of-flight per point).
3. **Adapter home.** URML repo (`reference/perception-runtime/`), Carnegie-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0112: Roboception (rc_visard / rc_cube)

**Post to:** https://github.com/roboception/cvkit/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Roboception rc_visard / rc_cube
```

**Body:**

```markdown
Hi @roboception team,

Proposing a URML v0.1 capability-manifest mapping for Roboception rc_visard (3D camera) and rc_cube (compute box) over `cvkit` and the GenICam-compliant API surface. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

rc_visard's industrial 3D-vision posture (GenICam compliance, in-process pose-estimation, vendor-supported MoveIt integration) places it cleanly in URML's `cameras` + `sensors` manifest blocks, with the same color + per-point-attributes gap on point clouds.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0112-roboception-outreach.md

Questions worth maintainer input on:

1. **GenICam compliance declaration.** Should URML's manifest declare GenICam compliance as a sensor capability so generic GenICam adapters interoperate?
2. **In-process detection / pose-estimation declaration.** Manifest field for vendor-supported detection classes?
3. **Adapter home.** URML repo, Roboception-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0113: Basler (pylon)

**Post to:** https://github.com/basler/pypylon/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Basler ace / dart / blaze over pylon
```

**Body:**

```markdown
Hi @basler team,

Proposing a URML v0.1 capability-manifest mapping for Basler's ace / dart 2D cameras and blaze ToF over `pypylon` and the pylon SDK. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Basler's industrial 2D camera + ToF coverage gives URML's `cameras` block a clean GigE Vision / USB3 Vision substrate. The blaze ToF complements the v0.1 `depth` measurement_type cleanly; pylon's mature SDK is the engagement surface.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0113-basler-pylon-outreach.md

Questions worth maintainer input on:

1. **Camera-protocol declaration.** Should URML's manifest declare GigE Vision / USB3 Vision / CXP camera-protocol class for adapter interoperability?
2. **blaze ToF amplitude declaration.** Per-pixel amplitude / SNR alongside depth — manifest-field expectations? (Spec RFC queued shared with RFC-0115, RFC-0127, RFC-0137.)
3. **Adapter home.** URML repo, Basler-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0114: Prophesee (event cameras)

**Post to:** https://github.com/prophesee-ai/openeb/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Prophesee event cameras
```

**Body:**

```markdown
Hi @prophesee-ai team,

Proposing a URML v0.1 capability-manifest mapping for Prophesee event cameras (Gen3 / Gen4 / EVK4) over `openeb` and the Metavision SDK. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Event cameras are a first-class v0.1 schema gap in URML: asynchronous per-pixel brightness-change events do not map cleanly onto any v0.1 `cameras` or `sensors` field. A Spec RFC adding `event_stream` as a measurement_type is queued (paired with RFC-0126 iniVation). Prophesee's maintainer input would shape the manifest fields (temporal resolution, event-rate, polarity).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0114-prophesee-event-outreach.md

Questions worth maintainer input on:

1. **Event-stream measurement_type shape.** Manifest fields: temporal resolution, event-rate ceiling, polarity, per-event metadata?
2. **Active-pixel-sensor co-fusion declaration.** Some Prophesee modules pair event + frame; should URML's manifest declare the combined modality explicitly?
3. **Adapter home.** URML repo, Prophesee-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0115: ifm Effector (O3X / O3R)

**Post to:** https://github.com/ifm/ifm3d/discussions/new (Discussions preferred per repo settings)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for ifm Effector O3X / O3R
```

**Body:**

```markdown
Hi @ifm team,

Proposing a URML v0.1 capability-manifest mapping for ifm's O3X / O3R industrial ToF camera platform over `ifm3d`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

O3R's multi-head ToF + 2D + IMU integrated platform exercises URML's `cameras` + `sensors` block boundary distinctively (multi-head industrial perception is uncommon in URML's outreach surface). Per-pixel amplitude alongside depth is a v0.1 gap shared with RFC-0127 (pmdtechnologies) and RFC-0137 (AMS-OSRAM); a single amplitude-/depth-class Spec RFC covers all three.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0115-ifm-effector-outreach.md

Questions worth maintainer input on:

1. **Multi-head platform declaration.** Should URML's manifest declare O3R's multi-head topology (shared chassis, multiple aligned sensors) as a first-class concept?
2. **Amplitude alongside depth.** Spec RFC queued; manifest-field expectations (per-pixel amplitude / SNR / confidence)?
3. **Adapter home.** URML repo, ifm-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0116: Teledyne FLIR (Boson)

**Post to:** https://github.com/FLIR/BosonUSB/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for FLIR Boson / Tau 2 thermal
```

**Body:**

```markdown
Hi @FLIR team,

Proposing a URML v0.1 capability-manifest mapping for the FLIR Boson / Tau 2 industrial thermal cameras over `BosonUSB` and the FLIR Spinnaker / Camera SDK. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Thermal cameras are a first-class v0.1 schema gap in URML: per-pixel calibrated temperature is a structured output (thermal-array) not yet first-class in URML's manifest. Spec RFC adding `thermal_array` is queued, shared with RFC-0128 (Optris) and RFC-0129 (Seek Thermal).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0116-teledyne-flir-outreach.md

Questions worth maintainer input on:

1. **Thermal-array measurement_type shape.** Manifest fields: per-pixel temperature units, calibration state, dynamic range, NUC (non-uniformity correction) state?
2. **Detection-capability declaration.** FLIR's thermal-analytics modules ship detection classes; how should URML's manifest declare these for `query_detection`?
3. **Adapter home.** URML repo, FLIR-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0117: MicroStrain by HBK

**Post to:** https://github.com/LORD-MicroStrain/microstrain_inertial/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for MicroStrain CV / GX / GQ IMU/AHRS/INS
```

**Body:**

```markdown
Hi @LORD-MicroStrain team,

Proposing a URML v0.1 capability-manifest mapping for the MicroStrain CV5 / GX5 / GQ7 IMU/AHRS/INS family over `microstrain_inertial`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

IMU measurement_types — `acceleration`, `angular_velocity`, `orientation` — are a first-class v0.1 schema gap; the manifest currently lacks them and URML's outreach uses the `custom` escape-hatch. Spec RFC queued; shared gap with RFC-0118 (SBG), RFC-0125 (Bosch), RFC-0131 (Xsens/Movella), RFC-0132 (TDK).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0117-microstrain-hbk-outreach.md

Questions worth maintainer input on:

1. **IMU measurement_types Spec RFC shape.** Manifest fields: units, sampling rate, fusion state (raw / AHRS / EKF / Kalman-filter), bias compensation?
2. **GNSS-aided INS variants** (GQ7). Manifest-field expectations for INS-with-GNSS class? (Shared gap with RFC-0119 / RFC-0120 / RFC-0133 / RFC-0134.)
3. **Adapter home.** URML repo, HBK-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0118: SBG Systems

**Post to:** https://github.com/SBG-Systems/sbg_ros2_driver/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for SBG Ellipse / Quanta IMU/AHRS/INS
```

**Body:**

```markdown
Hi @SBG-Systems team,

Proposing a URML v0.1 capability-manifest mapping for the SBG Ellipse / Quanta family over `sbg_ros2_driver`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Same IMU-measurement_type gap as MicroStrain (RFC-0117); SBG's defense-grade Quanta tier and Ellipse industrial line give URML's manifest a complementary input to MicroStrain's. INS-with-GNSS variants share the GNSS-class Spec-RFC gap with RFC-0119 / RFC-0120.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0118-sbg-systems-outreach.md

Questions worth maintainer input on:

1. **IMU + INS measurement_types** Spec RFC shape (shared with RFC-0117).
2. **GNSS-class measurement_types** Spec RFC shape (shared with RFC-0119 / RFC-0120 / RFC-0133 / RFC-0134).
3. **Adapter home.** URML repo, SBG-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0119: Septentrio

**Post to:** https://github.com/septentrio-gnss/septentrio_gnss_driver/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Septentrio Mosaic / AsteRx GNSS / RTK
```

**Body:**

```markdown
Hi @septentrio-gnss team,

Proposing a URML v0.1 capability-manifest mapping for the Septentrio Mosaic / AsteRx high-accuracy GNSS / RTK family over `septentrio_gnss_driver`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

GNSS measurement_types (`gnss_position`, `gnss_velocity`, `gnss_quality`, `heading`) are a first-class v0.1 schema gap; URML's manifest uses the `custom` escape-hatch. Spec RFC queued; shared gap with RFC-0120 (NovAtel), RFC-0133 (u-blox), RFC-0134 (Emlid).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0119-septentrio-outreach.md

Questions worth maintainer input on:

1. **GNSS-class measurement_types Spec RFC shape.** Manifest fields: datum (WGS84 / ITRF), fix-type granularity, constellation declaration, frequency-band declaration, RTK correction-source pattern?
2. **High-accuracy positioning manifest fields.** Manifest expectations from a Septentrio-class deployment (mm-class accuracy, multi-frequency, multi-constellation)?
3. **Adapter home.** URML repo, Septentrio-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0120: NovAtel (Hexagon)

**Post to:** https://github.com/novatel/novatel_oem7_driver/discussions/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for NovAtel OEM7 GNSS / SPAN INS
```

**Body:**

```markdown
Hi @novatel / Hexagon team,

Proposing a URML v0.1 capability-manifest mapping for NovAtel OEM7 GNSS receivers and SPAN INS over `novatel_oem7_driver`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Same GNSS-class measurement_types gap as Septentrio (RFC-0119). NovAtel's SPAN INS (tightly-coupled GNSS + IMU) gives URML's manifest an additional integration shape — INS-as-single-sensor vs separate-GNSS-plus-IMU.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0120-novatel-hexagon-outreach.md

Questions worth maintainer input on:

1. **GNSS-class measurement_types Spec RFC shape** (shared with RFC-0119 / RFC-0133 / RFC-0134).
2. **Tightly-coupled INS declaration.** Should URML's manifest declare SPAN as a fused-sensor block, or as separate GNSS + IMU blocks?
3. **Adapter home.** URML repo, NovAtel-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0121: Robotous

**Post to:** https://github.com/ROBOTOUS/ROS-2-Interface-for-RFT-Series-EtherCAT-Model/issues/new (fresh vendor org — light touch)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Robotous RFT series 6-axis F/T sensors
```

**Body:**

```markdown
Hi @ROBOTOUS team,

Proposing a URML v0.1 capability-manifest mapping for Robotous RFT series 6-axis force/torque sensors over your ROS 2 EtherCAT driver. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This is URML's first F/T-sensor RFC. 6-axis force/torque (`Fx Fy Fz Tx Ty Tz`) is a first-class v0.1 schema gap; the manifest uses the `custom` escape-hatch today. Spec RFC adding `ft_6axis` is queued. URML's `grasp` primitive (Layer 2) does not today consume F/T feedback for tactile grasping — future cross-layer work.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs). Noting the recent vendor-org creation (Feb 2026); engagement is light-touch and exploratory.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0121-robotous-ft-outreach.md

Questions worth maintainer input on:

1. **F/T 6-axis measurement_type Spec RFC shape.** Manifest fields: per-axis range, accuracy, sampling rate, bias compensation, mounting frame?
2. **F/T as cobot-grasp feedback.** Should URML's `grasp` primitive consume F/T feedback through the manifest, or always envelope-side?
3. **Adapter home.** URML repo (`reference/sensor-runtime/`), Robotous-maintained, or both?
4. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0122: GelSight

**Post to:** https://github.com/gelsightinc/gsrobotics/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for GelSight vision-based tactile sensors
```

**Body:**

```markdown
Hi @gelsightinc team,

Proposing a URML v0.1 capability-manifest cross-citation for GelSight vision-based tactile sensors (DIGIT-successor / Mini / R1.5) over `gsrobotics`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This is URML's first tactile-sensing RFC. Tactile / pressure-array measurement is a first-class v0.1 schema gap; Spec RFC queued, shared with RFC-0136 (Contactile). GelSight's vision-based output (camera under deformable membrane) and Contactile's capacitive-array output (per-pillar 3-axis force) are structurally different; two vendor inputs sharpen the Spec RFC.

**License note.** `gsrobotics` is GPL-3.0, which limits Apache-2.0 bundling. URML's framing is cross-citation rather than bundled adapter; the RFC discusses this explicitly.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0122-gelsight-tactile-outreach.md

Questions worth maintainer input on:

1. **Tactile-array measurement_type Spec RFC shape.** Manifest fields for vision-based tactile output (image-class, contact-localization, force-estimation derived semantics)?
2. **GPL-3.0 posture.** Is the copyleft license deliberate (and should URML stay strictly cross-citation), or would a dual-license shape be possible later?
3. **Slip-detection / contact-event declaration.** Manifest field for vendor-supported derived events?
4. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0123: Cubert (hyperspectral)

**Post to:** https://github.com/cubert-hyperspectral/cuvis.sdk/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Cubert Ultris snapshot hyperspectral
```

**Body:**

```markdown
Hi @cubert-hyperspectral team,

Proposing a URML v0.1 capability-manifest mapping for the Cubert Ultris-series snapshot hyperspectral cameras over `cuvis.sdk`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This is URML's first hyperspectral-imaging RFC. Per-pixel multi-band spectral signatures are a first-class v0.1 schema gap; Spec RFC adding `spectral_cube` measurement_type is queued (parallel to RFC-0039's `point_cloud`).

**The high-leverage angle:** Cubert's `cuvis-ai-agentic-skills` repo already exposes spectral classification as LLM-tool calls — the same surface URML's natural-language layer (RFC-0021) composes with. The URML / Cubert engagement may have the highest semantic overlap of any Move-10 target.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0123-cubert-hyperspectral-outreach.md

Questions worth maintainer input on:

1. **Spectral-cube measurement_type Spec RFC shape.** Manifest fields: spatial resolution, spectral bands, wavelength range, calibration state?
2. **Spectral-classification capability declaration.** Cuvis-AI ships classifiers; manifest field so `query_detection` validates against actual classes?
3. **Agentic-skills bridge.** `cuvis-ai-agentic-skills` exposes spectral primitives as LLM-tool calls. What integration shape would Cubert prefer — bundled URML bridge, contributed example in `cuvis-ai-agentic-skills`, or cross-citation only?
4. **Adapter home.** URML repo (`reference/perception-runtime/`), Cubert-maintained, or both?
5. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0124: Sensirion (environmental sensors)

**Post to:** https://github.com/Sensirion/arduino-i2c-scd30/issues/new (most-engagement-active per-sensor repo; redirect if you prefer a different catalog-level surface)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Sensirion environmental sensors
```

**Body:**

```markdown
Hi @Sensirion team,

Proposing a URML v0.1 capability-manifest mapping for Sensirion's environmental sensor catalog (SHT humidity, SCD30 / SCD40 CO2, SEN66 multi-parameter, SPS particulate, SGP VOC) over the 252-repo Sensirion org. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This is URML's first environmental / chemical-sensor RFC. v0.1 has `humidity` and `temperature` (clean fits) but no native `co2` / `voc` / `particulate` / `formaldehyde` / `nox`. Env-scalar-array Spec RFC queued; Sensirion is the natural vendor input given the uniform BSD-3-Clause posture and multi-week cadence across the catalog.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0124-sensirion-environmental-outreach.md

Questions worth maintainer input on:

1. **Environmental scalar-array Spec RFC shape.** Manifest fields for CO2 / VOC / particulate / formaldehyde / NOx (range_min, range_max, units, calibration_state)?
2. **Multi-parameter sensor topology.** SEN66 combines multiple sensors in one package; should URML's manifest express shared-housing relationships?
3. **Safety-envelope cross-link.** Environmental thresholds can gate URML primitive execution (RFC-0012 safety envelopes). Should the manifest declare thresholds or always envelope-side?
4. **Per-sensor vs catalog-level engagement.** Per-sensor RFCs (RFC-0124a SCD30, RFC-0124b SHT4x, ...), or is one catalog-level RFC the right shape?
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Sensirion-maintained, or both?
6. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0125: Bosch Sensortec (MEMS)

**Post to:** https://github.com/boschsensortec/BHI385_SensorAPI/issues/new (or BME690_SensorAPI; redirect if you prefer a different catalog-level surface)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Bosch Sensortec MEMS catalog (BMI / BHI / BMP / BME / BMM)
```

**Body:**

```markdown
Hi @boschsensortec team,

Proposing a URML v0.1 capability-manifest mapping for Bosch Sensortec's MEMS catalog (BMI / BHI IMU + Sensor Fusion, BMP / BMP3 pressure, BME680 / BME690 gas, BMM350 magnetometer) over the 33-repo boschsensortec org. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Bosch and Sensirion (RFC-0124) together cover URML's MEMS / environmental sensor layer. IMU measurement_types are a shared v0.1 gap with RFC-0117 / RFC-0118 / RFC-0131; env-scalar-array is shared with RFC-0124.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0125-bosch-sensortec-outreach.md

Questions worth maintainer input on:

1. **IMU measurement_type shape** (acceleration / angular_velocity / orientation, with special attention to BHI fused-orientation outputs).
2. **Environmental scalar-array measurement_type shape** (gas resistance, VOC IAQ, magnetic field — range, units, calibration_state, fusion_state).
3. **On-chip fusion firmware declaration.** BHI ships closed binary fusion firmware (BSEC, BHy2, BSX). Should URML's manifest declare which fusion configuration is active, and how to reason about behavior the closed firmware controls?
4. **Adapter shape.** One umbrella `BoschSensortecAdapter` parameterized by product family, or one adapter per product line?
5. **Adapter home.** URML repo, Bosch-maintained, or both?
6. **Conformance listing.** README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 12 research-collab / cross-citation targets

### RFC-0126: iniVation (DAVIS event cameras)

**Post to:** https://gitlab.com/inivation/dv/dv-processing/-/issues/new (GitLab vendor-native) + parallel GitHub Issue on a utility-fork repo for routing visibility (https://github.com/inivation/flatbuffers or similar).

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for iniVation DAVIS / DVXplorer event cameras
```

**Body:**

```markdown
Hi @inivation team,

Proposing a URML v0.1 capability-manifest mapping for the DAVIS346 / DVXplorer event-camera family over `dv-processing` + `dv-ros`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This RFC pairs with RFC-0114 (Prophesee) on URML's event-stream Spec-RFC gap. iniVation's DAVIS pixel-level integration of event + APS frame is structurally distinct from Prophesee's; two vendor inputs sharpen the Spec RFC.

**Engagement-surface question.** Vendor-native development lives on GitLab. URML's outreach pipeline is GitHub-default. This RFC opens the conversation on both surfaces and asks which channel you prefer.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0126-inivation-event-outreach.md

Questions worth maintainer input on:

1. **Engagement-surface preference.** GitLab Issue on `dv-processing` or `dv-ros`, GitHub Issue on a utility-fork repo as routing notice, or vendor-redirect to a different channel entirely?
2. **Event-stream measurement_type shape** (shared with RFC-0114 Prophesee).
3. **Dual-mode DAVIS declaration.** Should URML's manifest express event-and-frame integration explicitly (one Camera block with both modes), or as two logically separate sensors?
4. **Inline IMU declaration.** DAVIS346 / DVXplorer ship co-located IMU; shared IMU-type Spec-RFC gap with RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131.
5. **Adapter home.** URML repo, iniVation-maintained, or cross-citation only?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0127: pmdtechnologies (Royale ToF)

**Post to:** https://github.com/pmdtechnologies/pmd-royale-ros/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for pmdtechnologies Royale ToF
```

**Body:**

```markdown
Hi @pmdtechnologies team,

Proposing a URML v0.1 capability-manifest mapping for the PicoFlexx / CamBoard pico monstar Royale-based ToF cameras over `pmd-royale-ros`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Acknowledging the repo has been quiet for `>2 years`. Engaging anyway — the manifest mapping is worth documenting even when adapter-grade reuse depends on Royale SDK licensing the operator accepts. If `pmd-royale-ros` is fully retired and engagement should route elsewhere, a redirect would help.

Shared amplitude / depth-class Spec-RFC gap with RFC-0115 (ifm) and RFC-0137 (AMS-OSRAM).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0127-pmdtechnologies-tof-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, dormant-but-supported, or fully retired? Where does vendor engagement live in 2026?
2. **ROS 2 driver.** Planned, or has the vendor consolidated on a non-ROS surface?
3. **Amplitude / depth-class manifest fields** (shared with RFC-0115 / RFC-0137).
4. **Closed-SDK declaration.** Should URML's manifest declare "depends-on-closed-Royale-SDK" and at what granularity?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0128: Optris (thermal)

**Post to:** https://github.com/Optris/otcsdk_downloads/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Optris Xi / PI industrial thermal — and a license-clarification ask
```

**Body:**

```markdown
Hi @Optris team,

Proposing a URML v0.1 capability-manifest mapping for the Optris Xi / PI industrial thermal imagers over `otcsdk_downloads` and `optris_drivers2`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Shared thermal-array Spec-RFC gap with RFC-0116 (FLIR) and RFC-0129 (Seek Thermal).

**Engagement is partly a license-clarification ask.** Both `otcsdk_downloads` (no license declared) and `optris_drivers2` (NOASSERTION) block Apache-2.0 downstream reuse without explicit upstream OSI license declarations. URML's adapter-grade integration depends on this clarification.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0128-optris-thermal-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `otcsdk_downloads` and `optris_drivers2` get explicit OSI license declarations (Apache-2.0 / BSD-3-Clause / MIT)?
2. **Thermal-array measurement_type shape** (shared with RFC-0116 / RFC-0129).
3. **Calibration declaration.** Should URML's manifest declare NUC / emissivity calibration state?
4. **Vendor vs community ROS 2 driver.** Should URML adapter target `Optris/optris_drivers2` (vendor) or `evocortex/optris_drivers2` (community-practical)?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0129: Seek Thermal

**Post to:** https://github.com/seekthermal/seekcamera-python/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Seek Thermal Compact / CompactPRO USB thermal
```

**Body:**

```markdown
Hi @seekthermal team,

Proposing a URML v0.1 capability-manifest mapping for the Seek Compact / CompactPRO / MicroCore USB thermal imagers over `seekcamera-python`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Acknowledging `seekcamera-python` is the single vendor repo and has been quiet for `>14 months`. Engaging anyway because Seek Thermal's compact USB form-factor is URML's portable / micro-class-robot complement to FLIR (RFC-0116) and Optris (RFC-0128) at the industrial end.

Shared thermal-array Spec-RFC gap.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0129-seek-thermal-outreach.md

Questions worth maintainer input on:

1. **Repository status.** Active, dormant-but-supported, or fully retired?
2. **Thermal-array measurement_type shape** (shared with RFC-0116 / RFC-0128).
3. **Compact / USB-class declaration.** Should URML's manifest declare physical-connection class (USB / USB-C / Lightning) for portable form-factor cameras?
4. **Adapter home.** URML repo, Seek-maintained, or both?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0130: Velodyne (via ros-drivers)

**Post to:** https://github.com/ros-drivers/velodyne/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for legacy Velodyne VLP/HDL via ros-drivers/velodyne — and a routing question
```

**Body:**

```markdown
Hi @ros-drivers/velodyne maintainers,

Proposing a URML v0.1 capability-manifest mapping for the legacy Velodyne VLP-16 / VLP-32C / HDL-32E / HDL-64E family over `ros-drivers/velodyne` (the community-maintained de facto driver). [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

**Routing question is the primary design point.** The Velodyne brand is now Ouster-owned (post-2023 merger). URML has already engaged Ouster in an earlier outreach wave on their modern product line. This RFC explicitly asks whether the legacy-VLP / community-driver engagement should be (a) on `ros-drivers/velodyne`, (b) a courtesy cross-link on the existing Ouster thread, or (c) both.

URML's adapter request lands on a community-org surface, not an OEM; the legacy-fleet audience is real (VLP-16 deployments persist across field-mobile fleets long after the OEM merged) but ros-drivers maintainers do not speak for Ouster on roadmap.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0130-velodyne-via-ros-drivers-outreach.md

Questions worth maintainer input on:

1. **Routing.** Issue on `ros-drivers/velodyne`, courtesy cross-link on the Ouster thread, or both?
2. **Per-point-attributes Spec RFC shape** (intensity / dual-return / time-of-flight per point).
3. **Dual-return mode declaration.**
4. **Maintenance posture.** Long-term legacy support, or migrate-to-Ouster-OS as legacy hardware ages out?
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0131: Xsens / Movella

**Post to:** https://github.com/xsens/xsens_mti_ros_node/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Xsens MTi IMU/AHRS/INS — and an engagement-channel question
```

**Body:**

```markdown
Hi @xsens / Movella team,

Proposing a URML v0.1 capability-manifest mapping for the Xsens MTi-series IMU / AHRS / INS family. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Acknowledging `xsens_mti_ros_node` is `>7 years` stale on GitHub and the active ROS 2 driver lives off-GitHub via tarball at movella.com. **Engagement-channel preference is the design point.** URML's outreach pipeline is GitHub-default; Movella's active surface is off-GitHub. A redirect to the right channel would be valuable.

Shared IMU-type Spec-RFC gap with RFC-0117 / RFC-0118 / RFC-0125 / RFC-0132; shared GNSS-class Spec-RFC gap with RFC-0119 / RFC-0120 / RFC-0133 / RFC-0134 (for MTi-680 INS-with-GNSS variants).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0131-xsens-movella-outreach.md

Questions worth maintainer input on:

1. **Engagement-channel preference.** GitHub Issue on `xsens/xsens_mti_ros_node`, Movella support email, Movella forum, or different channel?
2. **GitHub roadmap.** Vendor-direct GitHub mirror of the ROS 2 driver planned, or is the tarball-distribution model permanent?
3. **Legacy-repo license.** Can `xsens/xsens_mti_ros_node` get an explicit OSI license declaration (field-deployed ROS 1 fleets persist)?
4. **IMU + GNSS-class manifest fields** (shared with RFC-0117 through RFC-0134).
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0132: TDK / InvenSense

**Post to:** https://github.com/InvenSenseInc/tdk_robokit/issues/new (or `tdk_robotics_rbx_apps`; redirect if you prefer a different repo)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for TDK / InvenSense ICM/IIM MEMS IMU
```

**Body:**

```markdown
Hi @InvenSenseInc team,

Proposing a URML v0.1 capability-manifest cross-citation for the ICM-20948 / ICM-42688 / IIM-42652 MEMS IMU family over the InvenSenseInc GitHub org. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

**Cross-citation framing.** TDK's GitHub content sits at the MCU-firmware-host layer; URML's adapter pattern composes one layer up (robotics-stack level). The honest framing here is cross-citation — URML's manifest declares which TDK IMU is present and what measurement_types it produces, without claiming a bundled adapter at the embedded-driver layer.

Shared IMU-type Spec-RFC gap with RFC-0117 / RFC-0118 / RFC-0125 / RFC-0131. Comparable RFC for Bosch Sensortec at the integrator level is RFC-0125.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0132-tdk-invensense-outreach.md

Questions worth maintainer input on:

1. **Engagement-level preference.** IC-vendor level (here), OEM-integrator level (cross-cite via Bosch-pattern), or documentation cross-reference only?
2. **Driver-repo license.** Can `tdk_robotics_rbx_drivers_code` get an explicit OSI license declaration?
3. **DMP declaration.** On-chip DMP firmware varies; should URML's manifest declare which DMP configuration is active?
4. **IMU manifest fields** (shared with RFC-0117 through RFC-0131).
5. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0133: u-blox (ubxlib + KumarRobotics/ublox)

**Post to:** https://github.com/u-blox/ubxlib/issues/new (vendor) + cross-referenced second Issue on https://github.com/KumarRobotics/ublox (community ROS driver)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for u-blox ZED-F9P / NEO-M9N / LEA-F9R GNSS / RTK
```

**Body:**

```markdown
Hi @u-blox team (and a parallel post on @KumarRobotics/ublox),

Proposing a URML v0.1 capability-manifest mapping for the u-blox ZED-F9P / NEO-M9N / LEA-F9R / MAX GNSS / RTK family over `ubxlib` (vendor) and `KumarRobotics/ublox` (community ROS driver). [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

**Dual-surface engagement is the design point.** `u-blox/ubxlib` is the vendor-direct embedded UBX-protocol library; `KumarRobotics/ublox` is the de facto ROS-side community driver. URML benefits from engaging both surfaces; the RFC asks how vendor and community see the boundary.

Shared GNSS-class Spec-RFC gap with RFC-0119 / RFC-0120 / RFC-0134.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0133-ublox-gnss-outreach.md

Questions worth maintainer input on (for u-blox):

1. **Vendor-vs-community engagement boundary.** Is `ubxlib` the canonical vendor surface with `KumarRobotics/ublox` as community add-on, or both first-class?
2. **GNSS-class measurement_type shape** (datum, fix-type granularity, constellation/frequency declaration).
3. **RTK correction-source declaration.** Should URML's manifest declare the RTCM correction-source pattern (NTRIP, base-station, SBAS, PPP)?

For KumarRobotics:

4. **Driver maintenance posture.** Long-term ROS 2 support, or research-fork only?
5. **Cross-citation vs co-maintenance.** Contributed URML-bridge example in the repo, or cross-citation the right shape?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0134: Emlid Reach RTK

**Post to:** https://github.com/emlid/ntripbrowser/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Emlid Reach RTK GNSS
```

**Body:**

```markdown
Hi @emlid team,

Proposing a URML v0.1 capability-manifest mapping for the Emlid Reach RS3 / M2 / RX low-cost multi-band RTK GNSS receivers over `ntripbrowser` and the standard NMEA / UBX output. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Shared GNSS-class Spec-RFC gap with RFC-0119 / RFC-0120 / RFC-0133.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0134-emlid-rtk-outreach.md

Questions worth maintainer input on:

1. **Engagement-channel preference.** GitHub Issue on `ntripbrowser` or other active repo, Emlid forum, or vendor support email?
2. **GitHub cadence.** Vendor org cadence remain as-is, or planned for revival?
3. **GNSS-class manifest fields** (shared with RFC-0119 / RFC-0120 / RFC-0133).
4. **NTRIP correction-source declaration.** Manifest pattern for caster URL / mountpoint / auth-method-class?
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Emlid-maintained, or cross-citation only?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0135: Cerulean Sonar

**Post to:** https://github.com/CeruleanSonar/SonarView/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Cerulean S500 / Omniscan underwater sonar — and a license-clarification ask
```

**Body:**

```markdown
Hi @CeruleanSonar team,

Proposing a URML v0.1 capability-manifest mapping for the Cerulean S500 sounder and Omniscan multibeam over the ping-protocol family (`SonarView`, `ping-python`, `s500_ros2`). [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

This is URML's first sonar / underwater-perception RFC. URML already has an existing marine-runtime (BlueROV ArduSub) covering surface-vehicle / ROV mobility; Cerulean complements at the underwater-acoustic perception layer on the same Blue Robotics open-protocol substrate.

**License clarification ask.** `SonarView` has no license declared upstream. `ping-python` and `s500_ros2` are MIT (clean fit). Adapter-grade reuse depends on SonarView license clarification.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0135-cerulean-sonar-outreach.md

Questions worth maintainer input on:

1. **License clarification on SonarView.** Explicit OSI declaration (MIT / Apache-2.0 / BSD-3-Clause)?
2. **Sonar return-array measurement_type Spec RFC shape.** Per-bin / per-swath return-array manifest fields (bin count, range resolution, frequency, beam-pattern)?
3. **Ping-protocol declaration.** Manifest field for protocol version + extension set?
4. **Underwater-acoustic safety-envelope cross-link.** Should URML's manifest declare emission-class / frequency-band for marine-mammal regulatory envelope-gating?
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Cerulean-maintained, or cross-citation only?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0136: Contactile (tactile)

**Post to:** https://github.com/contactile/c3dfbs/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Contactile PapillArray tactile sensor
```

**Body:**

```markdown
Hi @contactile team,

Proposing a URML v0.1 capability-manifest cross-citation for the Contactile PapillArray tactile sensor over `c3dfbs` and the community ROS 2 wrapper `mgonzs13/contactile_ros`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

Second tactile RFC after RFC-0122 GelSight. PapillArray's per-pillar 3-axis force vector and GelSight's vision-based output are structurally different; two vendor inputs sharpen the tactile-array Spec RFC.

**Cross-citation framing.** GPL-3.0 on `c3dfbs` limits Apache-2.0 bundling. URML's framing here is cross-citation rather than bundled adapter; if engagement settles otherwise, the community ROS 2 wrapper is the practical Apache-2.0-friendly leverage point.

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs). Light touch expected.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0136-contactile-tactile-outreach.md

Questions worth maintainer input on:

1. **Engagement-channel preference.** GitHub Issue on `c3dfbs`, vendor support email, or other channel?
2. **License posture.** GPL-3.0 deliberate, or dual-license (GPL + commercial) shape possible?
3. **Tactile-array measurement_type shape** (shared with RFC-0122 GelSight).
4. **Slip-detection / contact-event declaration.** Manifest field for vendor-supported derived events?
5. **Adapter home.** Cross-citation only (recommended), URML repo targeting the community wrapper, or vendor-maintained?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0137: AMS-OSRAM (ToF + image sensors)

**Post to:** https://github.com/ams-OSRAM/tmf8829_driver_linux/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for AMS-OSRAM TMF ToF + Mira image-sensor
```

**Body:**

```markdown
Hi @ams-OSRAM team,

Proposing a URML v0.1 capability-manifest cross-citation for the TMF8828 / TMF8829 multi-zone ToF and Mira220 global-shutter image sensor over `tmf8829_driver_linux` and `mira220_v4l2_driver`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent.

**Cross-citation framing.** GPL-2.0 / GPL-3.0 copyleft on the drivers limits Apache-2.0 bundling. URML's framing here is cross-citation / manifest-component rather than bundled adapter.

**Engagement-level mismatch.** ams-OSRAM ships chips; URML adapters compose at the camera-module-integrator level (one layer up). The RFC asks whether chip-vendor or module-integrator engagement is the right shape.

Shared multi-zone-ToF / amplitude / depth-class Spec-RFC gap with RFC-0115 (ifm) and RFC-0127 (pmdtechnologies).

This is **proposal-only**, part of URML's Move #10 outreach (perception-vendor wave, 29 engageable RFCs). **Completes the 29 engageable Move-10 RFCs.**

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0137-ams-osram-outreach.md

Questions worth maintainer input on:

1. **Engagement-level preference.** Chip-vendor level (here) or module-integrator level (recommend specific OEMs)?
2. **License clarification on tmf8829_driver_python.** OSI declaration?
3. **Multi-zone ToF manifest fields** (shared with RFC-0115 / RFC-0127).
4. **Histogram-of-photons declaration.** Manifest field for histogram modes (resolution / bin-count / photon-counting)?
5. **Adapter home.** Cross-citation only (recommended given GPL posture), URML repo, or ams-OSRAM-maintained?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier C (21) — recorded in research file, NOT engaged

See [`perception-vendors-research-2026-05-27.md`](perception-vendors-research-2026-05-27.md) for the full Tier-C list with exclusion causes. No posts; these are URML's "investigated and chose not to pursue" record so the negative space is auditable.
