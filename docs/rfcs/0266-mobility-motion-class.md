---
rfc: 0266
title: mobility.motion_class — declaring the motion class (locomotion / fabrication) in the Layer-1 manifest
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

# RFC-0266: `mobility.motion_class` and drive_type extensions

## Summary

URML v0.1's `mobility.drive_type` enum (multirotor / fixed_wing / vtol / diff_drive / omni / mecanum / legged) covers locomotion drive types. Move-18's frame-break wave engaged motion classes outside locomotion: Klipper's 3D-printer / CNC fabrication gantry (cartesian / corexy / delta) and WPILib's swerve drive (FIRST Robotics competition platform). This RFC introduces `mobility.motion_class` (`locomotion` vs `fabrication`) as the parent category and extends `drive_type` with the new fabrication and swerve values. Required when applicable. Backward compatible at the field level.

The surfaces that demanded this RFC are Move-18 RFC-0227 (Klipper fabrication motion) and RFC-0228 (WPILib swerve).

## Motivation

URML's mobility primitives (`move_to`, `dock`, `scan_area`) compose against locomotion platforms (multirotor drones, diff-drive mobile bases, legged robots). Move-18 reframed: a 3D-printer / CNC gantry is also a motion platform, and the swerve drive on FIRST Robotics competition robots is a locomotion drive but not in the v0.1 enum.

Three concrete consequences of the gap:

1. **Klipper / G-code substrate has no valid manifest declaration.** Move-18 RFC-0227 engaged Klipper as a fabrication-motion substrate. URML's `drive_type` enum has no value for cartesian / corexy / delta gantries.
2. **Swerve drive is locomotion but unenumerated.** WPILib's swerve is the canonical FIRST Robotics drivetrain; URML's `mobility.drive_type` should include it.
3. **Motion-class distinction is operationally important.** Fabrication motion (G-code) and locomotion motion (Nav2 / autopilot) dispatch through completely different substrates. A single `drive_type` enum without a `motion_class` parent loses the structural difference.

## Detailed design

### Field shape

```yaml
mobility:
  motion_class: locomotion                   # NEW — this RFC; locomotion | fabrication
  drive_type: swerve                          # NEW VALUE — this RFC
  drive_options:
    swerve:                                  # NEW per-drive-type sub-block
      module_count: 4                         # 3 | 4 | 6
      module_layout: square                   # square | diamond | hexagonal
```

Or, for a fabrication platform:

```yaml
mobility:
  motion_class: fabrication                  # NEW value
  drive_type: corexy                          # NEW VALUE — this RFC
  drive_options:
    corexy:
      work_envelope_mm: [300, 300, 400]
      max_velocity_mm_s: [200, 200, 50]
```

### New allowed values

**`motion_class`:**

| Value | Description |
|---|---|
| `locomotion` | Robot moves through an environment (mobile base, drone, legged, swerve) |
| `fabrication` | Stationary platform with a motion-controlled tool (3D printer, CNC gantry) |

**`drive_type`** (extension to existing enum):

| Value | Motion class | Description | Reference |
|---|---|---|---|
| `cartesian` | fabrication | XY (or XYZ) gantry with independent axes | Move-18 RFC-0227 |
| `corexy` | fabrication | CoreXY parallel-belt gantry | Move-18 RFC-0227 |
| `delta` | fabrication | Delta-arm fabrication printer | Move-18 RFC-0227 |
| `swerve` | locomotion | FIRST Robotics swerve drive (per-module steered) | Move-18 RFC-0228 |

Existing `drive_type` values (multirotor / fixed_wing / vtol / diff_drive / omni / mecanum / legged) continue to validate as `motion_class: locomotion`.

### Per-drive-type `drive_options` sub-fields

**`cartesian` / `corexy` / `delta`:**

| Field | Description |
|---|---|
| `work_envelope_mm` | `[x, y, z]` extents in millimeters |
| `max_velocity_mm_s` | `[x, y, z]` max velocity in mm/s (optional) |
| `axis_count` | 2 (XY only) or 3 (XYZ) — required for cartesian only |

**`swerve`:**

| Field | Description |
|---|---|
| `module_count` | 3, 4, or 6 swerve modules |
| `module_layout` | `square`, `diamond`, `hexagonal` |
| `wheel_diameter_m` | Optional |

### Schema fragment (Layer-1 mobility block extension)

```jsonc
{
  "mobility": {
    "properties": {
      "motion_class": {
        "enum": ["locomotion", "fabrication"]
      },
      "drive_type": {
        "enum": [
          "multirotor", "fixed_wing", "vtol",
          "diff_drive", "omni", "mecanum", "legged",
          "swerve",
          "cartesian", "corexy", "delta",
          "custom"
        ]
      },
      "drive_options": { "type": "object" }
    }
  }
}
```

### Validator behavior

1. **`motion_class` ↔ `drive_type` consistency.** Each new drive_type maps to one motion_class. Fabrication drive_types (cartesian / corexy / delta) require `motion_class: fabrication`. Locomotion drive_types (including the new `swerve`) require `motion_class: locomotion`. Inconsistency fails.
2. **`motion_class` is required when `drive_type` is set.** Existing manifests without `motion_class` declared infer `locomotion` for backward-compat for the duration of v0.x; v1.0 makes it required.
3. **Fabrication ↔ drone-protocol cross-check.** `motion_class: fabrication` is incompatible with `substrate.autopilot_class` (RFC-0250). Declaring both fails.
4. **`fabrication + protocol.embedded_class` cross-check.** Fabrication deployments use G-code over serial or socket; this is a separate protocol class from drone embedded protocols. A future RFC declares the G-code protocol class; for now, `motion_class: fabrication + protocol.embedded_class: mavlink` fails.
5. **`swerve` module_count range.** `module_count` in `{3, 4, 6}`.
6. **Forward-compat.** Closed enum.

### Reference-runtime behavior

`reference/ros2-runtime/` reads `motion_class` to select the dispatch path. For locomotion deployments, Nav2 / drone-runtime composes. For fabrication deployments, a future `reference/fabrication-runtime/` composes (composes against Klipper / similar via G-code). URML's `move_to(target_pose)` against a fabrication manifest dispatches as a G-code move command, not a Nav2 navigate-to-pose action.

### Conformance test additions

`conformance/tests/test_manifest_motion_class.py`:

1. Manifest with `motion_class: locomotion + drive_type: diff_drive` passes (existing pattern, backward-compat verified).
2. Manifest with `motion_class: fabrication + drive_type: corexy` passes.
3. Manifest with `motion_class: locomotion + drive_type: corexy` fails (motion_class / drive_type inconsistent).
4. Manifest with `motion_class: fabrication + substrate.autopilot_class: px4` fails (incompatible substrates).
5. Manifest with `drive_type: swerve + module_count: 5` fails (out of range).

## Backward compatibility

Pre-v1.0. Additive at the field level. Existing manifests without `motion_class` infer `locomotion` until v1.0 makes the field required. The `swerve`, `cartesian`, `corexy`, `delta` drive_types are new enum values; they don't affect existing manifests.

## Drawbacks

- **`motion_class` is a new top-level concept.** URML's spec evolves to recognize fabrication as a first-class motion category, which is conceptual scope expansion.
- **Reference fabrication-runtime doesn't exist yet.** Move-18 RFC-0227 (Klipper) is the engagement that surfaces the need; the runtime is future work.
- **Some drive_types could arguably support both motion_classes.** A custom gantry could be locomotion (e.g., an overhead-crane robot). URML's enum decides one motion_class per drive_type; this RFC's mappings reflect the dominant case.
- **G-code substrate declaration is deferred.** Sibling future RFC declares the G-code-over-serial / G-code-over-socket protocol class for fabrication deployments. This RFC scopes the motion_class + drive_type but not the protocol.

## Alternatives considered

1. **Skip `motion_class`; add fabrication drive_types to a flat enum.** Rejected. The motion_class distinction is operationally important; flat enum loses it.
2. **Treat fabrication as a `substrate.class` value (alongside `ros2`, `px4`) instead of a motion_class.** Rejected. Klipper-driven fabrication composes against ROS 2 in some deployments and against direct Klipper in others; substrate is a different axis from motion_class.
3. **Bundle G-code substrate declaration in this RFC.** Rejected. Substrate class is a separate field; bundling would dilute the focus.
4. **Use `mobility_type` instead of `motion_class`.** Rejected. The word "mobility" already names the parent block; using it for the sub-field would be confusing.

## Prior art

- [Move-18 RFC-0227 (Klipper outreach)](0227-klipper-outreach.md) — surfaced fabrication motion drive_types.
- [Move-18 RFC-0228 (WPILib outreach)](0228-wpilib-outreach.md) — surfaced swerve drive_type.
- [RFC-0008 (drone profile)](0008-drone-profile.md), [RFC-0009 (mobile-base profile)](0009-mobile-base-profile.md) — sibling profiles that consume drive_type.
- [RFC-0250 (substrate.autopilot_class)](0250-substrate-autopilot-class.md) — sibling Spec RFC; this RFC's fabrication motion_class is incompatible with autopilot_class declarations.

## Unresolved questions

1. **G-code substrate declaration RFC.** Fabrication motion requires G-code-over-serial / G-code-over-socket declaration. Sibling future RFC.
2. **Hybrid platforms.** Some platforms combine locomotion + fabrication (mobile manufacturing robots, drone-mounted 3D printers). URML's manifest is single-motion-class-per-deployment today.
3. **Multi-axis fabrication beyond XYZ.** 5-axis CNC, robotic-arm-based fabrication. URML's `axis_count` field covers XYZ; multi-axis is future work.

## Implementation plan

1. JSON Schema fragment with motion_class + extended drive_type enum + per-drive-type drive_options.
2. Validator with consistency checks (motion_class / drive_type / substrate cross-checks).
3. Conformance tests (five).
4. Update example manifests.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (motion_class is conceptual expansion, no fabrication runtime yet, edge cases on dual-purpose drive_types, G-code declaration deferred).
- [x] Backward compatibility additive (existing manifests infer locomotion).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to Move-18 outreach (0227, 0228) + sibling Spec RFCs (0250, 0008, 0009).
- [x] CLAUDE.md compliance: enum closure preserves moat; URML's substrate-neutrality stance preserved (motion_class is orthogonal to substrate).
