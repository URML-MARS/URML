---
rfc: 0267
title: perception.sensors[].measurement_type — IMU classes and event-camera type
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0267: `measurement_type` extensions for IMU classes and event-camera

## Summary

RFC-0263 extended the `perception.sensors[].measurement_type` enum with sonar, GNSS RTK, and multi-return LiDAR types and deferred two follow-on extensions: IMU class differentiation and event-camera sensor type. This RFC closes both deferrals. IMU class becomes a sub-field of the existing `measurement_type: imu`; event-camera becomes a new `measurement_type: event_stream`. Optional. Backward compatible.

## Motivation

URML's v0.1 `measurement_type: imu` does not distinguish MEMS-grade IMUs (Bosch BNO055, InvenSense ICM-20948) from fiber-optic or ring-laser IMUs (KVH 1750, Honeywell HG1700). The downstream consumer treats the IMU output identically; the differentiation matters for:

1. **Bias / drift expectations.** MEMS IMUs have orders-of-magnitude higher bias drift than fiber-optic. SLAM and dead-reckoning algorithms tune differently.
2. **Survey-grade deployments.** Mapping deployments using fiber-optic IMUs validate differently than consumer-grade.
3. **Procurement-policy implications.** Some federal-procurement contexts require tactical-grade IMUs; URML's manifest should declare the class.

Event cameras (Prophesee, DVS) produce sparse event streams rather than dense frames. The `measurement_type: image` doesn't capture the structural difference; downstream pipelines (event-based feature tracking, event-based optical flow) consume events very differently from frames.

## Detailed design

### IMU class sub-field

The existing `measurement_type: imu` gains `imu_class` in `measurement_options`:

```yaml
perception:
  sensors:
    - name: imu
      product: vectornav_vn200
      measurement_type: imu
      measurement_options:
        imu_class: tactical_grade               # NEW
        axes: 9_dof                             # 6_dof | 9_dof (with magnetometer) | 9_dof_with_temperature
        sample_rate_hz: 200
        bias_drift_degrees_per_hour: 1.0        # informational
```

### Event-camera measurement_type

New value `event_stream`:

```yaml
perception:
  sensors:
    - name: event_cam
      product: prophesee_evk4
      measurement_type: event_stream            # NEW
      measurement_options:
        resolution: [1280, 720]                  # pixel resolution
        event_rate_meps: 1000                    # max event rate (Mega Events Per Second)
        polarity_encoded: true                   # whether each event carries polarity (+/-)
```

### IMU class enum

| Value | Description |
|---|---|
| `consumer_mems` | Consumer-grade MEMS (Bosch BNO055, Invensense, etc.) |
| `industrial_mems` | Industrial MEMS (Xsens MTi, VectorNav VN-100) |
| `tactical_grade` | Tactical-grade MEMS / fiber-optic (Honeywell HG1700, KVH 1750-IMU) |
| `fiber_optic_gyro` | Fiber-optic gyro IMU (high-end navigation grade) |
| `ring_laser_gyro` | Ring-laser-gyro IMU (military / surveying) |
| `unknown` | IMU class not declared by upstream |

### Schema fragment (Layer-1 sensor block extension)

```jsonc
{
  "perception": {
    "properties": {
      "sensors": {
        "items": {
          "properties": {
            "measurement_type": {
              "enum": [
                "distance", "image", "depth",
                "point_cloud", "point_cloud_multireturn",
                "imu",
                "position", "gnss_rtk",
                "sonar_return_array", "sonar_swath", "water_column_profile",
                "event_stream",
                "custom"
              ]
            },
            "measurement_options": {
              "type": "object",
              "properties": {
                "imu_class": {
                  "enum": ["consumer_mems", "industrial_mems", "tactical_grade", "fiber_optic_gyro", "ring_laser_gyro", "unknown"]
                },
                "axes": {
                  "enum": ["6_dof", "9_dof", "9_dof_with_temperature"]
                },
                "sample_rate_hz": { "type": "number", "minimum": 1 },
                "bias_drift_degrees_per_hour": { "type": "number", "minimum": 0 },
                "event_rate_meps": { "type": "number", "minimum": 0 },
                "polarity_encoded": { "type": "boolean" }
              }
            }
          }
        }
      }
    }
  }
}
```

### Validator behavior

1. **`measurement_type: imu` + `imu_class` recommended.** When `measurement_type: imu` is declared, `imu_class` is recommended (soft suggestion at validate time). Manifests without `imu_class` continue to validate.
2. **`measurement_type: event_stream` requires `resolution`.** Resolution is required for event-camera declaration.
3. **IMU axes consistency.** `axes: 6_dof` is accelerometer + gyro (no magnetometer); `axes: 9_dof` adds magnetometer; `axes: 9_dof_with_temperature` adds temperature sensor. The validator does not enforce a relationship to the IMU class but surfaces the declared axes for documentation.
4. **Bias drift sanity range.** If `bias_drift_degrees_per_hour` is set, the value must be `>= 0`. The validator does not enforce a maximum; tactical-grade IMUs can drift `0.001 deg/hr` while consumer-MEMS can drift `> 1000 deg/hr`.
5. **Event rate range.** `event_rate_meps` must be `> 0`.
6. **Forward-compat.** Closed enum on imu_class.

### Reference-runtime behavior

Reference runtimes read `imu_class` and `measurement_type: event_stream` for startup-log diagnostics and adapter selection. SLAM substrates (RFC-0252) that consume IMU input may parameterize differently based on `imu_class`; the future adapter is the consumer.

### Conformance test additions

`conformance/tests/test_manifest_imu_event_camera.py`:

1. Manifest with `measurement_type: imu` and no `imu_class` passes with soft suggestion.
2. Manifest with `measurement_type: imu + imu_class: tactical_grade` passes silently.
3. Manifest with `measurement_type: event_stream + resolution: [1280, 720]` passes.
4. Manifest with `measurement_type: event_stream` without resolution fails.
5. Existing IMU manifests (no new fields) continue to validate (backward-compat).

## Backward compatibility

Pre-v1.0. Additive: existing `measurement_type: imu` manifests unchanged; `imu_class` is optional. `measurement_type: event_stream` is a new value.

## Drawbacks

- **Soft-suggestion on `imu_class`.** Recommended but not required. Some operators will skip it; the manifest still validates. The soft-suggestion is documentation-discipline.
- **Event-camera `resolution` field assumes a 2D event stream.** Some research event sensors have non-grid event spaces; URML's `resolution: [x, y]` assumes Cartesian grid.
- **IMU class enum is six values.** Growth via RFC. The current set covers the dominant commercial classes.
- **`bias_drift_degrees_per_hour` is informational.** Validator does not enforce. The field exists for downstream tooling (procurement audit, deployment configurator).

## Alternatives considered

1. **Make `imu_class` required.** Rejected. Backward-compat for existing manifests requires keeping the field optional; soft-suggestion is the right strength.
2. **Use `measurement_type: imu_consumer / imu_industrial / imu_tactical` (per-class measurement_type).** Rejected. Inflates the top-level enum; per-class differentiation belongs in measurement_options.
3. **Skip event_stream; use `measurement_type: image` with sub-field.** Rejected. Event streams are structurally different from images at the output level; separate type reads cleaner.
4. **Bundle multi-band radar in this RFC.** Rejected. Multi-band radar is a separate sensor-class concern that needs its own RFC (deferred per RFC-0263 unresolved questions).

## Prior art

- [RFC-0263 (perception measurement type extensions)](0263-perception-measurement-types.md) — parent Spec RFC; this RFC closes two deferred extensions.
- Move-10 RFC-0135 (Cerulean Sonar), RFC-0133 (u-blox) — surfaced the original sensor-type extension demand.
- Cross-references to industrial-IMU vendors (VectorNav, Xsens) and event-camera vendors (Prophesee, iniVation) are not from URML outreach yet; future moves may engage.

## Unresolved questions

1. **Multi-band radar measurement_type.** Future RFC; some automotive radars produce per-band returns.
2. **Per-pixel-event encoding.** Event cameras vary in their event encoding (timestamp resolution, polarity bit count). URML's manifest does not capture this.
3. **GNSS / IMU integrated systems.** Some integrated INS / GNSS systems (Inertial Sense, etc.) produce a combined output; URML's manifest declares them as two separate sensors today.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks.
3. Conformance tests (five).
4. Update example manifests where IMUs are declared.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (soft-suggestion vs required, 2D-grid assumption, six-value enum, informational drift field).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0263 (parent) + Move-10 outreach.
- [x] CLAUDE.md compliance: enum closure preserves moat; soft-suggestion respects backward-compat without surrendering documentation discipline.
