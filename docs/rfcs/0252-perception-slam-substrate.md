---
rfc: 0252
title: perception.slam_substrate — declaring the SLAM substrate in the Layer-1 manifest
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

# RFC-0252: `perception.slam_substrate` — declaring the SLAM substrate

## Summary

URML's perception manifest declares lidar, camera, and radar sensors but never declares which SLAM stack consumes them. Production users care: Cartographer's lidar-2D-vs-3D pose-graph differs from ORB-SLAM3's visual-SLAM five-mode set, RTAB-Map's visual-inertial database model, and Stella VSLAM's community-fork ORB lineage. This RFC adds `perception.slam_substrate` to the Layer-1 manifest with a closed enum, a `slam_mode` sub-field, and license-binding metadata. Optional when the deployment has no SLAM dependency. No primitive changes. Backward compatible.

The surfaces that demanded this RFC are RFC-0205 (Cartographer), RFC-0206 (ORB-SLAM3), RFC-0207 (RTAB-Map), and RFC-0211 (Stella VSLAM). This is URML's first SLAM-substrate field, and the field's existence is the principal positioning move Move-16 batch 3 made explicit.

## Motivation

The same Layer-2 program (`scan_area`, `move_to`, `dock`) runs against different SLAM stacks in different deployments. URML's manifest currently has no way to declare which SLAM substrate is active. Three concrete consequences:

1. **Pose-frame semantics drift.** Cartographer publishes `map` and `tracking_frame` frames. ORB-SLAM3 publishes its own world frame. RTAB-Map publishes a `map_frame`. URML's `move_to(target_pose)` against a manifest cannot statically check that the pose frame is consistent with the SLAM stack the runtime composes against.
2. **License binding affects URML adapter posture.** ORB-SLAM3 is GPL-3.0; URML's Apache-2.0 adapter cannot embed it, only cross-cite (per RFC-0206). RTAB-Map and Stella VSLAM are license-clarification-pending. URML's manifest needs to declare the SLAM-substrate license class so downstream packagers see the constraint at validate time.
3. **Mode enumeration is per-stack.** Cartographer's 2D vs 3D mode is structurally different from ORB-SLAM3's five-mode set (monocular, stereo, RGB-D, monocular-inertial, stereo-inertial). URML's manifest declares the substrate first; `slam_mode` is interpreted in the substrate's terms.

The Move-16 batch 3 outreach (RFCs 0205-0211) all flag this gap. URML's perception layer cannot honestly claim SLAM-substrate-neutrality until the manifest can declare which SLAM the runtime composes against.

## Detailed design

### Field shape

```yaml
perception:
  sensors: [...]                              # existing v0.1
  slam_substrate: cartographer                # NEW — this RFC
  slam_mode: 2d                                # NEW — substrate-specific value
  slam_options:                                # NEW — optional
    config_reference: /etc/cartographer.lua   # substrate-specific config path
    license_bind: apache_2_0                  # constraint for downstream packagers
    pose_frame:
      tracking_frame: base_link
      published_frame: map
```

### Allowed values for `slam_substrate`

Closed enum. Growth via follow-up RFC + outreach.

| Value | Description | Reference | License (downstream constraint) |
|---|---|---|---|
| `cartographer` | Google Cartographer (2D/3D lidar SLAM) | RFC-0205 | apache_2_0 |
| `orb_slam3` | UZ-SLAMLab ORB-SLAM3 (visual SLAM canonical) | RFC-0206 | gpl_3_0 |
| `rtabmap` | IntRoLab RTAB-Map (visual-inertial) | RFC-0207 | mixed_lgpl_bsd (license-clarification pending) |
| `stella_vslam` | stella-cv Stella VSLAM (OpenVSLAM community fork) | RFC-0211 | unknown (license-clarification pending) |
| `none` | Deployment does not use SLAM | n/a | n/a |
| `custom` | Vendor-specific or experimental SLAM | escape hatch + `slam_substrate_note` required | unknown |

### Allowed values for `slam_mode`

Per-substrate. The validator interprets `slam_mode` only when paired with a compatible `slam_substrate`.

| `slam_substrate` | Allowed `slam_mode` values |
|---|---|
| `cartographer` | `2d`, `3d` |
| `orb_slam3` | `monocular`, `stereo`, `rgbd`, `monocular_inertial`, `stereo_inertial` |
| `rtabmap` | `stereo`, `rgbd`, `stereo_imu`, `rgbd_imu` |
| `stella_vslam` | `monocular`, `stereo`, `rgbd` |
| `none` | (no `slam_mode` expected) |
| `custom` | free-string; document in `slam_substrate_note` |

### Allowed values for `license_bind`

This sub-field declares the downstream packaging constraint imposed by the SLAM substrate. URML's adapter posture composes at the API boundary in all cases; `license_bind` is documentation for downstream packagers.

| Value | Meaning |
|---|---|
| `apache_2_0` | Clean fit; no constraint on URML's Apache-2.0 adapter |
| `bsd_3_clause` | Clean fit |
| `mit` | Clean fit |
| `epl_2_0` | Cross-citation at API boundary; no source-embedding |
| `lgpl_3_0` | Cross-citation at API boundary; no static linking of GPL-tainted code |
| `gpl_3_0` | Cross-citation only; URML's Apache-2.0 adapter cannot embed; downstream packagers must respect GPL-3.0 propagation |
| `mixed_lgpl_bsd` | Mixed licensing; per-module clarification required for adapter-grade reuse |
| `unknown` | License not declared by upstream; URML treats as cross-citation only until clarified |

### Schema fragment (Layer-1)

```jsonc
{
  "perception": {
    "properties": {
      "slam_substrate": {
        "type": "string",
        "enum": ["cartographer", "orb_slam3", "rtabmap", "stella_vslam", "none", "custom"]
      },
      "slam_substrate_note": { "type": "string" },
      "slam_mode": { "type": "string" },
      "slam_options": {
        "type": "object",
        "properties": {
          "config_reference": { "type": "string" },
          "license_bind": {
            "enum": ["apache_2_0", "bsd_3_clause", "mit", "epl_2_0", "lgpl_3_0", "gpl_3_0", "mixed_lgpl_bsd", "unknown"]
          },
          "pose_frame": {
            "type": "object",
            "properties": {
              "tracking_frame": { "type": "string" },
              "published_frame": { "type": "string" }
            }
          }
        }
      }
    },
    "if": {
      "properties": { "slam_substrate": { "const": "custom" } }
    },
    "then": {
      "required": ["slam_substrate_note"]
    }
  }
}
```

### Validator behavior

1. **`slam_substrate` and `slam_mode` consistency.** If `slam_substrate` is set, `slam_mode` must be one of the allowed values for that substrate. The table is canonical; growth via follow-up RFCs.
2. **Custom note required.** If `slam_substrate: custom`, `slam_substrate_note` must be non-empty.
3. **Optional field.** If the deployment has no SLAM dependency (e.g., a stationary-arm industrial cell), neither `slam_substrate` nor `slam_mode` is required. Setting `slam_substrate: none` is the explicit "no SLAM" declaration.
4. **License-bind warning.** If `license_bind` is `gpl_3_0`, `unknown`, or `mixed_lgpl_bsd`, the validator emits a warning at validate time pointing downstream packagers at the license-handling implications. The warning is informational; it does not fail validation.
5. **Pose-frame opacity.** The validator does not check that the declared frames exist in the deployment's TF tree. That's a runtime concern, not a static one.

### Reference-runtime behavior

`reference/ros2-runtime/` reads `perception.slam_substrate` when present and uses it to select the SLAM dispatcher path. For Apache-2.0-bound substrates (Cartographer), the runtime composes via `cartographer_ros`. For GPL-3.0-bound substrates (ORB-SLAM3), the runtime composes via a separately-licensed companion package that the URML repo does not ship.

### Conformance test additions

`conformance/tests/test_manifest_slam_substrate.py`:

1. `slam_substrate: cartographer + slam_mode: 2d` passes.
2. `slam_substrate: cartographer + slam_mode: monocular` fails (wrong mode for substrate).
3. `slam_substrate: custom` without `slam_substrate_note` fails.
4. `slam_substrate: orb_slam3 + license_bind: gpl_3_0` passes with warning.
5. Manifest with no SLAM field at all passes.

## Backward compatibility

Pre-v1.0. Additive: existing manifests without SLAM declaration continue to validate (the field is optional). Existing manifests that referenced SLAM only in narrative are unaffected.

## Drawbacks

- **Per-substrate `slam_mode` table is maintenance burden.** Each new SLAM substrate enum value brings its own mode set. The table must be kept current. The cost is acceptable; URML's enum growth is RFC-gated anyway, so the table updates as RFCs land.
- **`license_bind` overlap with substrate selection.** ORB-SLAM3 is always GPL-3.0; declaring both `slam_substrate: orb_slam3` and `license_bind: gpl_3_0` is partially redundant. The redundancy is intentional: the substrate identifies what runs; the license_bind identifies the downstream constraint a packager must respect. Both belong in the manifest for separate audiences.
- **`pose_frame` opacity.** The validator can't statically check that declared frames exist; declaring them surfaces intent without enforcement. The discipline is documentation, not gating.

## Alternatives considered

1. **Skip `slam_mode` and let the substrate-specific config file declare the mode.** Rejected. Mode is deployment-critical and belongs in the manifest where the validator can reason about it, not in an external file.
2. **Flat `slam_mode` enum across all substrates.** Rejected. Cartographer's 2D vs 3D and ORB-SLAM3's monocular-vs-stereo-vs-RGB-D are structurally different concerns. A flat enum would either lose precision or balloon to a Cartesian product.
3. **Drop `license_bind` and rely on documentation.** Rejected. URML's policy file (RFC-0003) already declares procurement-gating policy; declaring license_bind at the manifest layer extends the same discipline to downstream packaging.
4. **Per-substrate vocabulary file (one YAML per substrate that ships with URML's spec).** Rejected for v0.1. The closed enum + per-substrate `slam_mode` table is sufficient. A per-substrate vocabulary file would be over-engineering for a four-substrate field set.

## Prior art

- [RFC-0205 (Cartographer outreach)](0205-cartographer-outreach.md), [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md), [RFC-0207 (RTAB-Map outreach)](0207-rtabmap-outreach.md), [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md) — the SLAM-substrate outreach quartet that surfaced this field.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — Cartographer / RTAB-Map / Stella VSLAM compose via ROS 2 binding adapters.
- Existing perception manifest in `spec/layer-1-hal/` — sensor declaration; this RFC extends the same perception block.

## Unresolved questions

1. **Lineage declaration.** Stella VSLAM is a community fork of archived OpenVSLAM. Should the manifest declare lineage as a separate field (`slam_substrate.lineage: openvslam`)? Future Spec RFC; not in this RFC's scope.
2. **Per-deployment multi-SLAM support.** Some deployments run two SLAM stacks (e.g., Cartographer for global map + ORB-SLAM3 for visual loop-closure cross-check). Single-substrate-per-manifest is the v0.1 stance; multi-SLAM is future work.
3. **Vocabulary-file path declaration.** ORB-SLAM3 uses an ORB vocabulary file (multi-MB) that the deployment must locate. Should the manifest declare the vocabulary-file path + checksum? Future RFC; surface for Stella VSLAM and ORB-SLAM3 specifically.

## Implementation plan

1. Land JSON Schema fragment.
2. Land validator with per-substrate `slam_mode` consistency check.
3. Land conformance tests.
4. Update example manifests that touch SLAM to declare the new field.
5. Land runtime-side substrate-selection logic in `reference/ros2-runtime/`.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] At least one alternative considered (four).
- [x] Drawbacks named honestly (per-substrate `slam_mode` table burden, `license_bind` partial redundancy, `pose_frame` opacity).
- [x] Backward compatibility additive (optional field).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Validator behavior fully specified.
- [x] Cross-references to outreach RFCs.
- [x] CLAUDE.md compliance: enum closure preserves moat; license-bind discipline extends URML's federal-procurement posture to downstream packaging.
