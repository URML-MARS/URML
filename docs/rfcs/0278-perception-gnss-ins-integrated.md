---
rfc: 0278
title: perception.integrated_sensor — GNSS-INS integrated sensor declarations
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-30
updated: 2026-05-30
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

# RFC-0278: `perception.integrated_sensor` — GNSS-INS integrated declarations

## Summary

URML's perception block (RFC-0263, RFC-0267) declares individual sensors (lidar, camera, IMU, GNSS) as separate entries in the `sensors` list. Production robotics increasingly uses **integrated sensors** that ship as one physical unit producing a tightly-coupled fused output: Inertial Sense (GNSS-INS in one package), Lord MicroStrain 3DM-GQ7 (GNSS + IMU + Kalman filter fused), Trimble integrated INS, Septentrio integrated GNSS-INS. Declaring these as two separate sensors loses the integration semantics. This RFC adds `perception.integrated_sensor` as a sibling cluster declaration with closed enum values for integration types and a `fusion_mode` sub-field. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0267 deferred-question on GNSS-INS integrated systems.

## Motivation

GNSS-INS integration is real production: a single IC or board produces fused output where the IMU's accelerometer + gyro data is tightly-coupled with GNSS pseudo-range data in a Kalman filter or similar. Downstream consumers (Nav2 navigation, EKF localization) get a single fused state estimate, not two raw sensor streams. URML's manifest declaring two separate sensors (`measurement_type: imu` + `measurement_type: gnss_rtk`) misrepresents the integration:

1. **Fused output has different consumer semantics.** A Nav2 deployment consuming fused GNSS-INS output expects different topic structure (one `/imu/data_fused` + `/gnss_ins/odometry`) than consuming separate IMU + GNSS streams.
2. **Failure modes are correlated.** When GNSS reception drops, integrated systems fall back to IMU-only dead-reckoning with declared bias-drift accumulation. URML's manifest should declare the integration so failure-mode semantics are validate-time checkable.
3. **Provenance + license attestation differ.** Integrated systems are commercial (Inertial Sense, Lord MicroStrain) vs assembled from open-source components. URML's manifest should declare the integration type for procurement audit.

## Detailed design

### Field shape

```yaml
perception:
  sensors:                                   # existing list (RFC-0263, 0267)
    - name: lidar
      measurement_type: point_cloud
      # ... lidar config
  integrated_sensors:                        # NEW — this RFC, parallel list
    - name: gnss_ins
      type: gnss_ins                         # gnss_ins | gnss_imu_separate_fused | ahrs | custom
      product: inertial_sense_ux             # informational; product identifier
      fusion_mode: tightly_coupled            # tightly_coupled | loosely_coupled | unaided
      component_sensors:                     # informational; what's inside the integration
        - kind: gnss
          frequency_class: dual_l1_l2         # see RFC-0263
        - kind: imu
          imu_class: industrial_mems          # see RFC-0267
      output_streams:
        - name: odom
          topic_template: /<name>/odometry
        - name: state
          topic_template: /<name>/state
        - name: raw_gnss
          topic_template: /<name>/gnss_raw
      failure_modes:
        gnss_loss_fallback: ins_dead_reckoning  # ins_dead_reckoning | hold_last | fail
        max_unaided_drift_seconds: 30
```

### Allowed values for `type`

| Value | Description |
|---|---|
| `gnss_ins` | Tightly-coupled GNSS + INS in one package (Inertial Sense, Trimble integrated, Septentrio AsteRx INS) |
| `gnss_imu_separate_fused` | GNSS receiver + IMU in separate housings, fused via vendor SDK or external filter |
| `ahrs` | Attitude-Heading Reference System (IMU + magnetometer fused; no GNSS) |
| `custom` | Vendor-specific or experimental integration; requires `integrated_sensor_note` |

### Allowed values for `fusion_mode`

| Value | Description |
|---|---|
| `tightly_coupled` | Pseudo-range observations enter Kalman filter directly (best accuracy) |
| `loosely_coupled` | GNSS produces position fix; IMU produces motion estimate; fusion combines (standard pattern) |
| `unaided` | Sensors run independently; downstream consumer fuses externally |

### Allowed values for `failure_modes.gnss_loss_fallback`

| Value | Description |
|---|---|
| `ins_dead_reckoning` | Continue INS-only navigation with accumulating drift |
| `hold_last` | Hold last known GNSS-fused position; do not advance |
| `fail` | Stop estimation; downstream consumer must handle |

### Schema fragment (Layer-1, new top-level under perception)

```jsonc
{
  "perception": {
    "properties": {
      "integrated_sensors": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "type"],
          "properties": {
            "name": { "type": "string" },
            "type": {
              "enum": ["gnss_ins", "gnss_imu_separate_fused", "ahrs", "custom"]
            },
            "integrated_sensor_note": { "type": "string" },
            "product": { "type": "string" },
            "fusion_mode": {
              "enum": ["tightly_coupled", "loosely_coupled", "unaided"]
            },
            "component_sensors": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "kind": {
                    "enum": ["gnss", "imu", "magnetometer", "barometer", "wheel_encoder"]
                  }
                }
              }
            },
            "output_streams": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "topic_template": { "type": "string" }
                }
              }
            },
            "failure_modes": {
              "type": "object",
              "properties": {
                "gnss_loss_fallback": {
                  "enum": ["ins_dead_reckoning", "hold_last", "fail"]
                },
                "max_unaided_drift_seconds": { "type": "number", "minimum": 0 }
              }
            }
          },
          "if": { "properties": { "type": { "const": "custom" } } },
          "then": { "required": ["integrated_sensor_note"] }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing `integrated_sensors` is acceptable. Deployments without integrated sensors use the standard `sensors` list only.
2. **Required-name + type for each entry.** Each entry must declare name and type.
3. **`type: gnss_ins` + `component_sensors` consistency.** Recommended to include both `gnss` and `imu` in `component_sensors`; warning surfaces if either is missing.
4. **`fusion_mode: unaided` consistency.** Unaided fusion mode is unusual for an integrated sensor (the whole point is integration); the validator emits a warning.
5. **`failure_modes.max_unaided_drift_seconds` recommended when `gnss_loss_fallback: ins_dead_reckoning`.** Without it, downstream consumers can't reason about drift budgets. Soft suggestion.
6. **Custom requires note.**
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read the integrated_sensors list and configure the sensor adapter (Inertial Sense ROS 2 driver, MicroStrain ROS 2 driver) accordingly. The runtime exposes the declared `output_streams` as ROS 2 topics under the templates.

### Conformance test additions

`conformance/tests/test_manifest_integrated_sensors.py`:

1. Manifest without `integrated_sensors` passes.
2. Manifest with `integrated_sensors: [{name: ins, type: gnss_ins, fusion_mode: tightly_coupled}]` passes.
3. Manifest with `type: gnss_ins` and component_sensors missing GNSS or IMU passes with warning.
4. Manifest with `fusion_mode: unaided + type: gnss_ins` passes with warning.
5. Manifest with `type: custom` and no note fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests without integrated_sensors unchanged.

## Drawbacks

- **`integrated_sensors` parallel to `sensors` may duplicate.** Some deployments declare individual GNSS + IMU in `sensors` AND the integrated unit in `integrated_sensors`. The validator does not enforce non-overlap; downstream tooling consumes both.
- **Vendor-specific output stream conventions vary.** Inertial Sense exposes `/ins/odom`; MicroStrain exposes `/mip/odometry`. URML's `output_streams.topic_template` is configuration; the runtime adapter follows the template.
- **`failure_modes.gnss_loss_fallback` is opinionated.** Some integrated systems support more failure modes (graceful degradation, sensor-aware downstream weighting); URML's enum is coarse.
- **No multi-IMU integration.** Some high-end systems use multiple IMUs internally; URML's component_sensors list captures presence but not per-IMU sub-config.

## Alternatives considered

1. **Skip `integrated_sensors`; declare both IMU and GNSS in `sensors`.** Rejected. Integration semantics matter for downstream consumer behavior; the manifest should distinguish.
2. **Nest integrated sensors under `sensors` with an `integration` sub-field.** Rejected. Integrated sensors have multiple output streams and component semantics that don't fit the per-sensor entry shape.
3. **Use a single `integration_type` field on individual sensors.** Rejected. The integration spans multiple sensors; declaring on each individual would be redundant.
4. **Generalize to `cluster_sensors` (e.g., stereo-camera pairs, multi-lidar arrays).** Considered. v0.1 of this field is GNSS-INS-shaped; clusters of other types (stereo cameras, microphone arrays) could extend the pattern in future RFCs. The `type` enum has `custom` for now; growth via RFC.

## Prior art

- [RFC-0263 (perception measurement_type extensions)](0263-perception-measurement-types.md) — added `gnss_rtk` measurement_type that is one component of GNSS-INS integration.
- [RFC-0267 (perception IMU + event-camera)](0267-perception-imu-event-camera.md) — added IMU class differentiation; this RFC closes the deferred GNSS-INS-integrated question.
- Move-10 RFC-0133 (u-blox; vendor-archived but community-side covered) — surfaced GNSS adjacent concerns.
- Move-10 perception-vendor outreach generally (28 RFCs) — surfaced sensor-integration patterns.

## Unresolved questions

1. **Stereo-camera pairs as integrated sensors.** Future RFC could generalize the cluster pattern to stereo-camera and multi-camera arrays.
2. **GNSS RTK correction provenance.** When `failure_modes.gnss_loss_fallback: ins_dead_reckoning` and the GNSS uses RTCM correction from a network mountpoint, the RTCM correction loss is a separate failure mode. Future RFC.
3. **Per-component health-status declaration.** Integrated sensors emit per-component health; URML's manifest could declare which health topics to expect. Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with consistency checks.
3. Conformance tests (five).
4. Update example manifests with at least one integrated-sensor example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (parallel-list duplication risk, vendor-specific conventions, opinion failure-mode enum, no multi-IMU integration).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0263 (sibling measurement_type), RFC-0267 (parent IMU+event-camera; closes integrated-sensor deferral).
- [x] CLAUDE.md compliance: substrate-neutrality preserved (URML doesn't prefer Inertial Sense over MicroStrain); enum closure preserved.
