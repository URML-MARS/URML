---
rfc: 0279
title: perception measurement_type — multi-band radar declaration
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

# RFC-0279: `measurement_type: radar_returns` — multi-band radar

## Summary

RFC-0263 and RFC-0267 extended the `measurement_type` enum with sonar, GNSS RTK, multi-return LiDAR, IMU class, and event-camera types but deferred radar. This RFC closes that deferred. Adds `radar_returns` as a new measurement_type value covering automotive and outdoor-robotics radar, with `frequency_band` enumeration (24 GHz / 77 GHz / 79 GHz) and `radar_options` sub-block. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0263 deferred-question on multi-band radar.

## Motivation

Radar is a major perception modality URML's v0.1 enum left out:

- **Automotive radar:** 77 GHz / 79 GHz long-range radar (LRR) and short-range radar (SRR) for vehicle perception. Continental ARS series, Bosch FRS, Aptiv ESR.
- **Outdoor robotics radar:** 24 GHz / 77 GHz Doppler radar for ground-vehicle and agricultural-robot perception. Sonatech, MIT Lincoln Lab patterns.
- **Ground-penetrating radar (GPR):** Lower frequency (100 MHz to 2 GHz) for subsurface mapping. Specialty use.

Three concrete consequences of the gap:

1. **Automotive deployments are blocked.** URML's substrate-spine engaged Nav2 / MoveIt 2 / ROS 2 core (Move-16); automotive deployments need radar declaration as their primary perception modality.
2. **Multi-band declaration matters.** A 77 GHz LRR plus 24 GHz Doppler in the same deployment produces different downstream consumer needs (long-range vs short-range; range-Doppler vs amplitude only).
3. **Range-Doppler vs point-target output structure.** Some radars emit per-target detections (range, azimuth, Doppler); others emit raw range-Doppler maps. URML's manifest needs to declare the output structure.

## Detailed design

### Field shape

```yaml
perception:
  sensors:
    - name: front_radar
      product: continental_ars540
      measurement_type: radar_returns         # NEW — this RFC
      measurement_options:
        frequency_band: 77_ghz                 # 24_ghz | 77_ghz | 79_ghz | 100_mhz_gpr | custom
        output_format: point_targets           # point_targets | range_doppler_map | raw_iq
        max_range_m: 250
        azimuth_fov_deg: 120
        elevation_fov_deg: 18
        doppler_enabled: true
        max_targets: 256
```

### Allowed values for `frequency_band`

| Value | Description |
|---|---|
| `24_ghz` | 24 GHz ISM band (short-range, lower regulatory restrictions in some jurisdictions) |
| `77_ghz` | 77 GHz automotive band (long-range radar; standard in modern automotive) |
| `79_ghz` | 79 GHz automotive band (short-range, higher bandwidth than 77 GHz) |
| `100_mhz_gpr` | 100 MHz to 2 GHz ground-penetrating radar |
| `custom` | Other frequency band; requires `frequency_band_note` |

### Allowed values for `output_format`

| Value | Description |
|---|---|
| `point_targets` | List of detected targets (range, azimuth, Doppler, intensity) |
| `range_doppler_map` | 2D range-Doppler intensity map (pre-CFAR processing) |
| `raw_iq` | Raw in-phase / quadrature samples (deepest level; for research / custom processing) |

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
                "radar_returns",
                "custom"
              ]
            },
            "measurement_options": {
              "type": "object",
              "properties": {
                "frequency_band": {
                  "enum": ["24_ghz", "77_ghz", "79_ghz", "100_mhz_gpr", "custom"]
                },
                "frequency_band_note": { "type": "string" },
                "output_format": {
                  "enum": ["point_targets", "range_doppler_map", "raw_iq"]
                },
                "max_range_m": { "type": "number", "minimum": 0 },
                "azimuth_fov_deg": { "type": "number", "minimum": 0, "maximum": 360 },
                "elevation_fov_deg": { "type": "number", "minimum": 0, "maximum": 180 },
                "doppler_enabled": { "type": "boolean" },
                "max_targets": { "type": "integer", "minimum": 1 }
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

1. **`measurement_type: radar_returns` requires `frequency_band`.** Missing field fails.
2. **`output_format: point_targets` recommended with `max_targets`.** Without it, downstream consumers can't size buffers. Soft suggestion.
3. **`output_format: raw_iq` warning.** Raw I/Q is unusual at the URML manifest layer (most deployments process I/Q before publishing). The validator surfaces the choice for review.
4. **FOV range checks.** `azimuth_fov_deg` in `[0, 360]`; `elevation_fov_deg` in `[0, 180]`.
5. **`frequency_band: custom` requires `frequency_band_note`.**
6. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read `radar_returns` for adapter selection. Continental ARS series uses Ethernet output; Bosch FRS uses CAN. URML's manifest declares the radar; deployment-side configuration handles the per-vendor wire format.

### Conformance test additions

`conformance/tests/test_manifest_radar.py`:

1. Manifest with `measurement_type: radar_returns + frequency_band: 77_ghz + output_format: point_targets + max_targets: 256` passes.
2. Manifest with `measurement_type: radar_returns` without `frequency_band` fails.
3. Manifest with `output_format: point_targets` without `max_targets` passes with soft suggestion.
4. Manifest with `output_format: raw_iq` passes with warning.
5. Manifest with `azimuth_fov_deg: 400` fails (out of range).

## Backward compatibility

Pre-v1.0. Additive: existing manifests unchanged. New value extends the enum.

## Drawbacks

- **Three-band enum may need extension.** Some specialty radars use other bands (350 MHz GPR, 5.8 GHz, 94 GHz). URML's enum captures the dominant cases; `custom` holds the long tail.
- **Output format enum is coarse.** `point_targets` covers most consumer-side use; some vendors emit additional structures (tracked targets with IDs, cluster maps) that URML's manifest doesn't capture.
- **Per-target field schema is deferred.** When `output_format: point_targets`, the per-target schema (range, azimuth, Doppler, intensity, etc.) is consumer-side; URML's manifest doesn't validate.
- **Multi-band declaration is per-sensor entry.** A deployment with both 77 GHz LRR and 24 GHz SRR needs two sensor entries; cross-band coordination is downstream.

## Alternatives considered

1. **Skip multi-band; treat radar as a single measurement_type.** Rejected. Frequency band materially affects deployment characteristics (range, regulatory, interference); the manifest should declare it.
2. **Use `radar_lrr` / `radar_srr` / `radar_gpr` as separate measurement_types.** Rejected. The differentiation is by frequency band, not by use case; sub-field captures the distinction cleanly.
3. **Defer until automotive outreach engages a radar vendor.** Rejected. URML's manifest already declares lidar and camera as standard outdoor-perception modalities; radar belongs alongside them.
4. **Per-target schema standardization in this RFC.** Rejected. The per-target output is consumer-side and varies wildly between vendors; URML's manifest declares the format choice and lets consumers consume.

## Prior art

- [RFC-0263 (perception measurement_type extensions)](0263-perception-measurement-types.md) — parent Spec RFC; deferred multi-band radar.
- [RFC-0267 (perception IMU + event-camera)](0267-perception-imu-event-camera.md) — sibling extension; this RFC closes the radar deferral.
- Continental, Bosch, Aptiv automotive-radar product literature (cross-cite for context).

## Unresolved questions

1. **Tracked-target output schema.** Some radars emit tracked targets (with IDs and history). URML's manifest doesn't declare tracking state.
2. **Inter-radar interference declaration.** When multiple radars operate in adjacent bands, interference becomes a real concern. URML's manifest could declare a coordination scheme. Future RFC.
3. **Regulatory band declaration.** 24 GHz uses different power limits in EU vs US; URML's manifest could declare jurisdiction for envelope-validation. Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks.
3. Conformance tests (five).
4. Update example manifests with at least one radar example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (enum may grow, coarse output format, deferred per-target schema, per-sensor multi-band).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0263 (parent), RFC-0267 (sibling).
- [x] CLAUDE.md compliance: enum closure preserves moat; substrate-neutrality preserved (URML doesn't prefer Continental over Bosch).
