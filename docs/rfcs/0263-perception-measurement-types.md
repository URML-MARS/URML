---
rfc: 0263
title: perception.sensors[].measurement_type — extending the sensor measurement-type enum
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

# RFC-0263: `perception.sensors[].measurement_type` extensions

## Summary

URML's Layer-1 sensor declaration accepts `measurement_type` per sensor (distance, image, point_cloud, etc.) but the v0.1 enum is too narrow for several sensor classes URML's Move-10 outreach engaged: sonar return arrays (Cerulean Sonar), water column profiles (underwater perception), GNSS RTK / L1L2 (u-blox), and per-bin sonar returns. This RFC extends the `measurement_type` enum with five new sensor-output classes and defines the validator's handling. Optional in the sense that existing measurement_type values continue to validate; the new values are additive. Backward compatible.

The surfaces that demanded this RFC are Move-10 RFC-0135 (Cerulean Sonar) and Move-10 RFC-0133 (u-blox GNSS, vendor-archived but community-side covered).

## Motivation

The Move-10 perception-vendor wave surfaced sensor classes URML's v0.1 measurement_type enum does not capture cleanly:

1. **Underwater sonar return arrays.** Cerulean Sonar's S500 single-beam sounder and Omniscan side-scan sonar produce per-bin return-intensity arrays for sonar profile / side-scan swath data. The current `measurement_type: distance` is for scalar distance-to-bottom only and loses the array structure.
2. **Water column profiles.** Multi-bin water-column return data for in-water object detection. Distinct from sonar return arrays at the sensor-output level; some sensors produce both.
3. **GNSS RTK / L1L2 / multi-frequency.** u-blox and other survey-grade GNSS produce centimeter-accurate position fixes with RTK corrections. URML's existing `measurement_type: position` is correct in spirit but the receiver-class enumeration (consumer GPS vs RTK vs L1L2 dual-frequency) is missing.
4. **IMU classes.** 6-DOF vs 9-DOF (with magnetometer) vs 9-DOF-with-temperature vs MEMS-grade vs fiber-optic-grade IMUs have different downstream consumption patterns. Out of scope for this RFC; flagged for future RFC.
5. **LiDAR multi-return.** Multi-return LiDAR (e.g., Velodyne VLP-32C) returns multiple intensity values per beam. URML's `measurement_type: point_cloud` doesn't capture the multi-return dimension.

Three concrete consequences:

1. **URML's marine-runtime track is blocked.** Move-10 engaged underwater perception (RFC-0135 Cerulean Sonar); a working marine adapter cannot validate without sonar-return-array types.
2. **GNSS deployment fidelity is lossy.** A survey-grade RTK deployment validates against the same manifest as a consumer GPS deployment.
3. **Standards-body cross-citation is incomplete.** URML's perception spec doesn't capture sensor-output classes that ASTM F45 (RFC-0221) and IEEE P1872.2 (RFC-0219) would cross-reference.

## Detailed design

### Field shape

Extend the existing `perception.sensors[].measurement_type` enum (defined in Layer-1 HAL spec) with new values. Existing values stay unchanged.

```yaml
perception:
  sensors:
    - name: sonar
      product: cerulean_s500
      measurement_type: sonar_return_array   # NEW
      measurement_options:
        bin_count: 200
        range_resolution_m: 0.05
        frequency_khz: 500
    - name: rtk_gps
      product: ublox_zed_f9p
      measurement_type: gnss_rtk              # NEW
      measurement_options:
        frequency_class: dual_l1_l2           # NEW sub-field
        rtk_correction_source: ntrip          # NEW sub-field
        accuracy_cm: 1.0
    - name: side_scan_sonar
      product: cerulean_omniscan
      measurement_type: sonar_swath           # NEW
      measurement_options:
        swath_width_m: 50
        ping_rate_hz: 5
    - name: lidar
      product: velodyne_vlp_32c
      measurement_type: point_cloud_multireturn  # NEW
      measurement_options:
        max_returns: 2
```

### New measurement_type values

| Value | Description | Reference |
|---|---|---|
| `sonar_return_array` | Per-bin return-intensity array (single-beam sounder, vertical profile) | Move-10 RFC-0135 (Cerulean S500) |
| `sonar_swath` | Side-scan sonar swath (2-D intensity map across cross-track distance) | Move-10 RFC-0135 (Cerulean Omniscan) |
| `water_column_profile` | Multi-bin water-column return data for in-water object detection | Cerulean Sonar / Move-10 |
| `gnss_rtk` | RTK-corrected GNSS position; sub-cm accuracy | Move-10 RFC-0133 (u-blox) |
| `point_cloud_multireturn` | LiDAR point cloud with multiple returns per beam | Cross-reference; common Velodyne pattern |

### New measurement_options sub-fields

Per measurement_type, the `measurement_options` block accepts the following per-type fields (optional unless noted):

**For `sonar_return_array`:**
- `bin_count` (integer, required)
- `range_resolution_m` (number)
- `frequency_khz` (number)
- `beam_pattern_deg` (number, optional)

**For `sonar_swath`:**
- `swath_width_m` (number, required)
- `ping_rate_hz` (number)

**For `water_column_profile`:**
- `bin_count` (integer)
- `time_window_s` (number)

**For `gnss_rtk`:**
- `frequency_class` (`single_l1` / `dual_l1_l2` / `triple_l1_l2_l5`)
- `rtk_correction_source` (`ntrip` / `rtcm_serial` / `lband_subscription`)
- `accuracy_cm` (number, informational)

**For `point_cloud_multireturn`:**
- `max_returns` (integer, required)
- `return_filter` (`strongest` / `last` / `all`)

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
                "distance",
                "image",
                "depth",
                "point_cloud",
                "point_cloud_multireturn",
                "imu",
                "position",
                "gnss_rtk",
                "sonar_return_array",
                "sonar_swath",
                "water_column_profile",
                "custom"
              ]
            },
            "measurement_options": { "type": "object" }
          },
          "required": ["measurement_type"]
        }
      }
    }
  }
}
```

### Validator behavior

1. **Closed enum extension.** The new values join the existing closed enum. Unknown values fail.
2. **Per-type required sub-fields.** When `measurement_type: sonar_return_array`, `measurement_options.bin_count` must be present. The validator enforces per-type required-sub-fields.
3. **`gnss_rtk` correction-source consistency.** When `measurement_type: gnss_rtk` and `rtk_correction_source: lband_subscription`, a soft warning surfaces (subscription-based RTK may not work offline; URML's no-cloud invariant applies).
4. **`point_cloud_multireturn` max_returns range.** `max_returns` in `[1, 5]` (LiDAR vendors typically support 1-5 returns).
5. **Forward-compat.** Closed enum.

### Reference-runtime behavior

Reference runtimes read the new measurement_types for startup-log diagnostics and to select the per-sensor adapter. Cerulean Sonar adapters consume `sonar_return_array` / `sonar_swath`; u-blox adapters consume `gnss_rtk`. URML's marine and outdoor-mapping runtimes extend to handle the new types.

### Conformance test additions

`conformance/tests/test_manifest_measurement_types.py`:

1. Manifest with `measurement_type: sonar_return_array` and `bin_count: 200` passes.
2. Manifest with `measurement_type: sonar_return_array` without `bin_count` fails.
3. Manifest with `measurement_type: gnss_rtk + rtk_correction_source: lband_subscription` passes with warning.
4. Manifest with `measurement_type: point_cloud_multireturn + max_returns: 10` fails (out of range).
5. Existing manifests with `measurement_type: distance | image | point_cloud` continue to validate (backward-compat).

## Backward compatibility

Pre-v1.0. Additive: existing measurement_type values unchanged. New values extend the enum.

## Drawbacks

- **Per-type required-sub-fields complicate the schema.** Conditional `required` in JSON Schema is workable but adds validator complexity.
- **`water_column_profile` overlaps with `sonar_return_array`.** Some sensors produce both; the manifest may need to declare two sensor entries for the same physical sensor. Documentation only at v0.1.
- **GNSS multi-frequency enumeration is partial.** L1 + L2 + L5 + L6 + ... frequency combinations grow; the current `single_l1 / dual_l1_l2 / triple_l1_l2_l5` covers the dominant cases.
- **IMU classes deferred.** A future RFC will extend `measurement_type: imu` with class-of-IMU sub-field (MEMS / fiber-optic / ring-laser).

## Alternatives considered

1. **Skip the new types; let users use `custom` measurement_type.** Rejected. `custom` is for one-off cases; common sensor classes (sonar, RTK GPS, multi-return LiDAR) deserve named types.
2. **Single `sonar` measurement_type with mode sub-field.** Rejected. Single-beam sounder and side-scan sonar are structurally different sensor outputs; separate types read cleaner.
3. **Bundle IMU class extension with this RFC.** Rejected. IMU classes are a separate sensor-class concern; bundling would dilute focus.
4. **Use `measurement_subtype` instead of new `measurement_type` values.** Rejected. The existing v0.1 enum is the established surface; extending it preserves the validator-as-static-gate property without adding a new field layer.

## Prior art

- [Move-10 RFC-0135 (Cerulean Sonar)](0135-cerulean-sonar-outreach.md) — the outreach RFC that surfaced sonar-return-array and water-column-profile types.
- Move-10 RFC-0133 (u-blox GNSS, vendor-archived; community side referenced) — surfaced gnss_rtk type.
- URML Layer-1 HAL spec (in `spec/layer-1-hal/`) — defines the existing measurement_type enum.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — conformance framework this RFC extends with new test cases.

## Unresolved questions

1. **IMU classes (`mems` / `fiber_optic` / `ring_laser` / `tactical_grade`).** Future RFC.
2. **Multi-band radar measurement_type.** Some automotive radars produce per-band returns. Future RFC if URML engages automotive-radar vendors.
3. **Event-camera measurement_type.** Event-based vision sensors (DVS / Prophesee) produce event streams, not frames. Different structural type entirely; future RFC.

## Implementation plan

1. JSON Schema fragment with extended enum + per-type required sub-fields.
2. Validator with per-type checks (4 + closed-enum forward-compat).
3. Conformance tests (five).
4. Update marine-runtime reference adapter (planned) to consume the new types.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (per-type sub-field complexity, sonar overlap, partial GNSS, IMU deferred).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (0135, 0133) + sibling Spec RFC (0014).
- [x] CLAUDE.md compliance: enum extension preserves moat; no-cloud warning honored on `lband_subscription` RTK source.
