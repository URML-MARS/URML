---
rfc: 0682
title: 3D-camera declaration, color point clouds, per-point attributes, and the hand-eye mount
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-08-27
updated: 2026-08-27
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

# RFC-0682: 3D-camera declaration

## Summary

The Layer-1 `Camera` block gains five optional, additive fields so a 3D camera can be declared as what it is:

1. `point_cloud: { channels, organized }`: the primary product is a point cloud with a closed-set list of per-point attributes (`xyz | rgba | rgb | snr | normals | intensity | amplitude | confidence | custom`) and an `organized` flag (one point per image pixel).
2. `rate_hz_max` and `time_sync_methods`: the parity fields RFC-0039 added to `Sensor` and left as its own open question for cameras.
3. `datasheet_ref`: an opaque pointer to the authoritative per-model datasheet. URML never compresses accuracy into a scalar.
4. `mount: { frame, kind, calibration_ref }`: the hand-eye declaration. `kind` is `eye_in_hand` or `eye_to_hand`, `frame` names a declared frame the optical frame is expressed in, `calibration_ref` is an opaque handle to the calibration artifact. The extrinsic topology rides the declared `frames` (RFC-0290 `Frame.transform`); URML invents no calibration file format.

Validation is pydantic constraints plus one coherence rule (`mount.frame` must be a declared frame). No Pass-2/Pass-3 code, no error codes, no envelope interaction. Every existing manifest validates unchanged. No primitive changes.

## Motivation

[RFC-0035](0035-zivid-integration.md) asked Zivid how URML should declare a 3D camera. Espen Holmbakken (Principal Engineering Manager, Zivid) answered on 2026-05-27, and the answers are this RFC's design inputs rather than suggestions:

- Zivid cameras output 3D color point clouds (XYZ, RGBA, SNR, normals) as the primary product, not 2D images. The v0.1 `Camera` block (photo, video, stream, a free-form resolution) cannot say that; the repo's own Zivid fixture declared the camera as a 5 MP photo device, which is honest about the schema and wrong about the camera.
- A single `accuracy_mm` misrepresents the product: dimension trueness, point precision, and working distance interact and are documented per model. Resolved with a clear no; the manifest points at the datasheet instead.
- Acquisition modes (HDR, multi-acquisition, projector settings, exposure) are substrate-internal. Not surfaced.
- Surface normals and SNR are standard output; a pick-quality score is an application-layer construct. `pick_from` gains no vision-source field ([RFC-0615](0615-world-model-areas-and-detection.md) `object_detection` already links object classes to a declared camera).
- Hand-eye calibration was left to URML.

The same gap is queued in six other perception-vendor threads that cite RFC-0035 by name: RealSense ([RFC-0109](0109-intel-realsense-outreach.md)), ZED ([RFC-0110](0110-stereolabs-zed-outreach.md)), MultiSense ([RFC-0111](0111-carnegie-multisense-outreach.md)), Roboception ([RFC-0112](0112-roboception-outreach.md)), ifm ([RFC-0115](0115-ifm-effector-outreach.md), per-point amplitude), and Velodyne ([RFC-0130](0130-velodyne-via-ros-drivers-outreach.md)). One RFC closes all of them. [RFC-0039](0039-sensor-schema-v0-2-iteration.md) did the lidar side and named a parallel `Camera` iteration as its follow-up (its Drawback 5 and open question); this is that iteration.

## Detailed design

### Schema changes

```python
class PointCloudOutput(BaseModel):
    channels: list[Literal["xyz", "rgba", "rgb", "snr", "normals",
                           "intensity", "amplitude", "confidence", "custom"]]  # min_length=1
    organized: bool = False

class CameraMount(BaseModel):
    frame: Identifier                       # a declared frame
    kind: Literal["eye_in_hand", "eye_to_hand"]
    calibration_ref: str | None = None      # opaque, not parsed

class Camera(BaseModel):
    ...existing fields unchanged...
    point_cloud: PointCloudOutput | None = None
    rate_hz_max: float | None = None        # gt=0
    time_sync_methods: list[str] | None = None
    datasheet_ref: str | None = None
    mount: CameraMount | None = None
```

`CapabilityManifest` gains one `model_validator`: every `perception.cameras[].mount.frame` must name a declared frame (same shape as the RFC-0617 `learned_policies` name rule).

A 3D camera stays a `Camera`. It also captures 2D images, and the fields that describe a camera (movable, capture modes, mount) are exactly the ones a lidar lacks. Lidar stays on `Sensor.measurement_type: point_cloud` with RFC-0039's free-form `channels`: lidar declares beams and timing, cameras declare color and organization. The two are deliberately not unified.

The `channels` set is closed with a `custom` escape (the [RFC-0586](0586-dexterous-hand-declaration.md) pattern) because the values come from shipped hardware: xyz, rgba, snr, normals from Zivid; amplitude from ToF (ifm); confidence from stereo (ZED, MultiSense); intensity is shared with lidar. The lidar-side `channels` stays free-form as RFC-0039 left it; tightening it is that RFC's follow-up, not this one's.

### Layer-1 HAL spec changes

`spec/layer-1-hal/v0.2.0.md` §2.6, the `cameras` bullet, gains the five fields and the capability-versus-configuration sentence mirrored from the sensors bullet.

### Validator changes

None beyond pydantic and the one frame-reference rule. No error codes.

### Reference runtime changes

None. Runtimes may read `mount` to pick the frame a detection is reported in; nothing is required for conformance.

### Conformance suite changes

The Zivid Two cell manifest (`reference/validator/tests/fixtures/manifests/zivid_two_cell.yaml`) declares every new field on `zivid_two_cell_3d`; conformance fixture `industrial/32_zivid_two_cell_positive` keeps passing unchanged. Unit tests in `reference/validator/tests/test_camera_rfc0682.py` cover the closed set, the empty-channels rejection, the rate constraint, the undeclared-frame rule, the fixture, and a pre-RFC manifest validating unchanged.

### LLM bridge changes

None. The fields are declarative; the bridge's manifest summary already lists cameras by name.

## Backward compatibility

Additive and optional. No existing manifest, program, fixture, or runtime changes behavior. The schema export (`urml schema`) grows; consumers that forbid unknown fields are unaffected because nothing is emitted unless declared.

## Drawbacks

1. Five more fields on a block that had six. All optional, all documented as capability declarations, but the surface grows.
2. `datasheet_ref` is a pointer, not data. A validator cannot reason about accuracy from it. That is the point (the vendor said a scalar misrepresents the product), but it means accuracy-aware checks stay out of URML until a vendor proposes a shape that does not lie.
3. `mount` describes topology and references a calibration; it does not carry the calibration. A deployment that declares `eye_in_hand` with a wrong `calibration_ref` is trusted, like every manifest field.
4. Two point-cloud homes (camera-side `point_cloud`, lidar-side `Sensor`). Deliberate, argued above, and a reader still has to learn it.

## Alternatives considered

- **A new `measurement_type: color_point_cloud` on `Sensor`** (the shape [RFC-0109](0109-intel-realsense-outreach.md) floated). Rejected: it would move 3D cameras out of the block that declares movable, capture modes, and mount, and would fork `point_cloud` into two types for one attribute.
- **A scalar `accuracy_mm`.** Rejected by the vendor whose product it would describe.
- **A calibration file schema.** Rejected: hand-eye calibration outputs are tool-specific and the geometry URML needs already has a home (RFC-0290 frame transforms). A pointer plus topology is the honest minimum.
- **Unify lidar and camera point clouds under one block.** Rejected: beams and timing versus color and organization are different declarations, and RFC-0039 deployments would have to migrate.
- **Skip `mount`, leave hand-eye deployment-side.** Rejected: without it a manifest cannot say which frame a 3D camera's output is expressed in, which is the one thing a validator placing a `pick_from` target needs to know.

## Prior art

- ROS `sensor_msgs/PointCloud2` fields (`x y z rgb intensity normal_x normal_y normal_z`) and the organized-cloud convention (height > 1) are the source of `channels` and `organized`.
- OPC UA Robotics and ISO 8373 describe calibration as a deployment property attached to a frame, not a device property, which is why `mount` references a frame.
- Zivid's *General 3D Topics* and *API Reference* (per Espen's pointers) are the vendor description the field names follow.

## Unresolved questions

- Whether a future envelope rule should bind `rate_hz_max` (a perception rate floor for a monitorable property, RFC-0667). Deferred until a deployment asks.
- Whether the lidar-side `Sensor.channels` should adopt a closed set now that the camera side has one. RFC-0039's follow-up.

## Implementation note

Lands in one PR: this RFC and its index row, the pydantic models and manifest rule, the spec bullet, the Zivid fixture and its conformance fixture (description corrected from "third-party-audited" to "self-declared"), the unit tests, the RFC-0035 follow-up note, and the commitments-page boxes. State is Implemented on merge (the RFC-0670 precedent for RFC-plus-implementation PRs). The report-back to Zivid (public note on zivid-ros#163, founder email to Espen) follows the merge.

## Self-review (Phase 1)

- [x] Problem statement grounded in a named maintainer's answers, quoted from RFC-0035.
- [x] Every field justified by shipped hardware or an explicit vendor constraint; the vendor's explicit no (scalar accuracy) is honored as a rejected alternative.
- [x] Additive, optional, backward compatible; validation kept to schema plus one coherence rule.
- [x] No primitive added; no substrate coupling; no cloud dependency; no telemetry.
- [x] Drawbacks name the trust boundary and the two-homes cost honestly.
