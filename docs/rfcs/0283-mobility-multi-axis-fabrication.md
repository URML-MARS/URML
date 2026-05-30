---
rfc: 0283
title: mobility.drive_options.fabrication — multi-axis fabrication and thermal / spindle envelope
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

# RFC-0283: `mobility.drive_options.fabrication` — multi-axis fabrication + thermal / spindle envelope

## Summary

RFC-0266 added `mobility.motion_class: fabrication` with cartesian / corexy / delta drive_types and `drive_options` with `axis_count: 2 | 3`. RFC-0271 added fabrication-protocol declarations (G-code dialects + transport + safety_envelope thermal_limit_c). Both deferred multi-axis fabrication (4-axis CNC, 5-axis CNC, robotic-arm fabrication) and the broader fabrication safety envelope (spindle, coolant, vacuum). This RFC closes both deferrals: extends `drive_options` with `axis_count: 2..6`, adds `axis_layout` declaration for 4/5/6-axis geometries, and adds a `fabrication_envelope` sub-block covering spindle, coolant, vacuum, and thermal limits. Optional. Backward compatible.

The surfaces that demanded this RFC are RFC-0266 (axis_count deferral) and RFC-0271 (spindle / coolant / thermal envelope deferral).

## Motivation

Industrial fabrication motion is rarely just XYZ. Three concrete consequences:

1. **5-axis CNC is the canonical industrial-fabrication production case.** A 5-axis CNC adds A and B rotational axes to the XYZ linear axes. URML's manifest cannot declare it today.
2. **Spindle / coolant / vacuum belong to the fabrication safety envelope.** A maintainer declaring `mobility.motion_class: fabrication` with a CNC gantry should be able to declare spindle RPM bounds and coolant-flow expectations as part of the envelope; without them, downstream consumers cannot statically reason about safety.
3. **Robotic-arm-mounted fabrication is a real case.** Some industrial cells mount a router or spindle on a 6-DOF robotic arm (UR5 with a milling end effector); URML's manifest could declare this hybrid pattern.

## Detailed design

### Field shape extension for `drive_options`

Existing `drive_options.cartesian` / `corexy` / `delta` block gains:

```yaml
mobility:
  motion_class: fabrication
  drive_type: cartesian                       # existing values; this RFC extends
  drive_options:
    cartesian:
      axis_count: 5                            # EXTENDED — was 2 | 3; now 2..6
      axis_layout: trunnion_4_axis             # NEW — multi-axis geometry
      work_envelope_mm: [600, 400, 300]
      rotational_axis_range_deg:               # NEW — for 4+/5+ axes
        a_axis: [-180, 180]
        b_axis: [-90, 90]
      max_velocity_mm_s: [200, 200, 100]
      fabrication_envelope:                    # NEW — this RFC
        spindle:
          enabled: true
          max_rpm: 24000
          min_rpm: 1000
          speed_control: vfd                    # vfd | gcode_s | manual
        coolant:
          flood_enabled: true
          mist_enabled: true
          air_blast_enabled: false
        vacuum:
          enabled: true
          hold_psi: 5                            # informational
        thermal_limits:
          spindle_max_c: 80
          extruder_max_c: 280                   # for 3D-print fabrication; pairs with RFC-0271
          ambient_max_c: 50
```

### Allowed values for `axis_layout`

| Value | Description | Axis count |
|---|---|---|
| `xy_2_axis` | 2-axis cartesian (XY only) | 2 |
| `xyz_3_axis` | 3-axis cartesian (XYZ) | 3 |
| `xyz_a_4_axis` | XYZ + one rotational axis (A) | 4 |
| `xyz_ab_5_axis` | XYZ + two rotational axes (A and B) | 5 |
| `trunnion_4_axis` | 4-axis trunnion (X, Y, Z, A on a tilting table) | 4 |
| `trunnion_5_axis` | 5-axis trunnion (X, Y, Z, A, B with tilting + rotating table) | 5 |
| `arm_mounted` | Fabrication tool mounted on a robotic arm (6-DOF arm) | 6 |
| `custom` | Vendor-specific layout; requires `axis_layout_note` |

### Allowed values for `spindle.speed_control`

| Value | Description |
|---|---|
| `vfd` | Variable Frequency Drive (analog 0-10V or digital interface) |
| `gcode_s` | G-code S-word commands (M3 S<rpm>) |
| `manual` | Manual operator control |

### Schema fragment (extending RFC-0266's drive_options)

```jsonc
{
  "mobility": {
    "properties": {
      "drive_options": {
        "properties": {
          "cartesian": {
            "properties": {
              "axis_count": { "type": "integer", "minimum": 2, "maximum": 6 },
              "axis_layout": {
                "enum": [
                  "xy_2_axis", "xyz_3_axis",
                  "xyz_a_4_axis", "xyz_ab_5_axis",
                  "trunnion_4_axis", "trunnion_5_axis",
                  "arm_mounted", "custom"
                ]
              },
              "axis_layout_note": { "type": "string" },
              "rotational_axis_range_deg": {
                "type": "object",
                "properties": {
                  "a_axis": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 },
                  "b_axis": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 },
                  "c_axis": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 }
                }
              },
              "fabrication_envelope": {
                "type": "object",
                "properties": {
                  "spindle": {
                    "type": "object",
                    "properties": {
                      "enabled": { "type": "boolean" },
                      "max_rpm": { "type": "number", "minimum": 0 },
                      "min_rpm": { "type": "number", "minimum": 0 },
                      "speed_control": { "enum": ["vfd", "gcode_s", "manual"] }
                    }
                  },
                  "coolant": {
                    "type": "object",
                    "properties": {
                      "flood_enabled": { "type": "boolean" },
                      "mist_enabled": { "type": "boolean" },
                      "air_blast_enabled": { "type": "boolean" }
                    }
                  },
                  "vacuum": {
                    "type": "object",
                    "properties": {
                      "enabled": { "type": "boolean" },
                      "hold_psi": { "type": "number" }
                    }
                  },
                  "thermal_limits": {
                    "type": "object",
                    "properties": {
                      "spindle_max_c": { "type": "number" },
                      "extruder_max_c": { "type": "number" },
                      "ambient_max_c": { "type": "number" }
                    }
                  }
                }
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

1. **`axis_count` ↔ `axis_layout` consistency.** Each `axis_layout` value implies an `axis_count`. Mismatch fails.
2. **`axis_count >= 4` requires `rotational_axis_range_deg`** for at least one rotational axis. Missing emits warning.
3. **`fabrication_envelope.spindle.min_rpm <= max_rpm`.** Inversion fails.
4. **`spindle.enabled: true` requires `max_rpm`.** Missing emits soft suggestion.
5. **`arm_mounted` layout requires `substrate.class` to declare a manipulation substrate.** When `arm_mounted` is declared, the manifest should also declare a robot-arm substrate (MoveIt 2 dispatch from RFC-0202). Missing emits warning.
6. **Custom requires note.**
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read the extended drive_options and fabrication_envelope for adapter selection. A future `reference/fabrication-runtime/` would consume these fields. Existing 3-axis manifests continue to work without changes.

### Conformance test additions

`conformance/tests/test_manifest_multi_axis_fabrication.py`:

1. Manifest with `axis_count: 5 + axis_layout: xyz_ab_5_axis` passes.
2. Manifest with `axis_count: 5 + axis_layout: xyz_a_4_axis` fails (count / layout mismatch).
3. Manifest with `axis_count: 4 + axis_layout: xyz_a_4_axis` without rotational_axis_range_deg passes with warning.
4. Manifest with `spindle.enabled: true + min_rpm: 25000 + max_rpm: 10000` fails (inversion).
5. Manifest with `axis_layout: custom` and no note fails.

## Backward compatibility

Pre-v1.0. Additive. Existing 2 / 3-axis manifests continue to validate. RFC-0266's `axis_count: 2 | 3` is now `axis_count: 2..6` (a strict superset).

## Drawbacks

- **Axis layout enum is opinionated.** Six named values capture the dominant CNC and 3D-printer cases; the long tail uses `custom`.
- **`arm_mounted` overlaps with manipulation substrate.** When a 6-DOF arm carries a router, the manifest declares both `motion_class: fabrication` AND a manipulation substrate. The two coexist; URML's discipline keeps both fields.
- **Fabrication envelope fields are partly aspirational.** Some MCU controllers don't support runtime VFD speed control; declaring `speed_control: vfd` in such a manifest is just informational. URML's validator doesn't reach into the controller.
- **Thermal-limits overlap with RFC-0271's `safety_envelope.thermal_limit_c`.** Per-protocol thermal limit and fabrication envelope thermal limit can be set independently; the validator does not enforce coherence.

## Alternatives considered

1. **Skip multi-axis; treat 4/5/6-axis as `custom` drive_type values.** Rejected. Multi-axis fabrication is a major industrial use case; explicit enum values are honest.
2. **Combine spindle / coolant / vacuum into a single `accessory_envelope` field.** Rejected. They have different semantics (spindle controls cutting; coolant manages heat; vacuum holds workpiece).
3. **Per-axis-of-motion separate sub-fields rather than `axis_layout` enum.** Rejected. The enum captures geometry-class succinctly; per-axis enumeration would inflate.
4. **Defer `fabrication_envelope` to a separate RFC.** Considered; bundling reads cleaner since the envelope semantics are intrinsic to multi-axis fabrication.

## Prior art

- [RFC-0266 (motion_class)](0266-mobility-motion-class.md) — parent Spec RFC; closed deferral on axis_count > 3.
- [RFC-0271 (protocol.fabrication_class)](0271-protocol-gcode-substrate.md) — sibling Spec RFC; closed deferral on spindle / coolant / thermal envelope at the protocol layer.
- [Move-18 RFC-0227 (Klipper)](0227-klipper-outreach.md) — fabrication outreach.
- Cross-references to LinuxCNC (5-axis machining), industrial-arm-mounted-spindle case studies.

## Unresolved questions

1. **Tool-changer declarations.** Multi-axis CNCs often have automatic tool changers; URML's manifest doesn't declare the tool inventory today. Future RFC could pair with RFC-0013 industrial-profile's `swap_tool` primitive.
2. **CAD-CAM toolpath provenance.** Multi-axis G-code is generated from CAD-CAM; URML's manifest could declare the toolpath provenance for audit. Future RFC.
3. **Adaptive control declarations.** Some CNCs adjust feedrate dynamically based on spindle load; URML's manifest could declare adaptive-control parameters. Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with seven checks.
3. Conformance tests (five).
4. Update example manifests with at least one 5-axis example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (opinion enum, arm_mounted overlap, aspirational fields, thermal-limit overlap with RFC-0271).
- [x] Backward compatibility additive (axis_count superset).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0266 (parent), RFC-0271 (sibling fabrication-protocol), Move-18 RFC-0227.
- [x] CLAUDE.md compliance: enum closure preserves moat; fabrication-envelope completion of safety-relevant manifest declarations.
