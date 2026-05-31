---
rfc: 0282
title: asset_references — declaring large-asset paths (vocabulary files, model weights, maps) in the Layer-1 manifest
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

# RFC-0282: `asset_references` — large-asset path declarations

## Summary

URML's manifest references several classes of large external assets: ORB vocabulary files for visual SLAM (RFC-0252, RFC-0206), pre-built maps for navigation (Nav2 / RFC-0201), URDF and SRDF descriptions (RFC-0202), model weights (RFC-0260, RFC-0277), camera-calibration YAML, world files for simulation (RFC-0269). Each is currently declared in an ad-hoc per-substrate sub-field. The lack of a unified asset-reference convention makes reproducibility audit and content addressing inconsistent. This RFC adds a top-level `asset_references` block with a closed enum of asset classes, URI scheme support (including RFC-0277's `hf://`), checksum declarations, and size-class hints. Optional. Backward compatible.

The surfaces that demanded this RFC are RFC-0252 (ORB vocabulary deferral), RFC-0206 (ORB-SLAM3 vocabulary), and several other Spec RFCs with deferred asset-path discussions.

## Motivation

URML's reproducibility depends on the manifest declaring assets unambiguously. Three concrete consequences of the gap:

1. **Vocabulary-file checksums are missing.** ORB-SLAM3 ships a ~150 MB ORB vocabulary file; if the file is replaced or corrupted, downstream SLAM accuracy degrades silently. URML's manifest should declare the checksum so downstream tooling can verify.
2. **Asset URIs are ad-hoc.** Some manifests use absolute filesystem paths (`/etc/urml/maps/lab.pgm`); others use relative paths; others use HTTP / S3 / hf:// URIs. URML's manifest should unify the convention.
3. **Audit + provenance is incomplete.** A federally-procurement-eligible deployment should be able to audit which version of which asset is in use; current ad-hoc paths can't do that consistently.

## Detailed design

### Field shape

`asset_references` is a top-level list. Each entry declares one external asset with class, URI, checksum, and size hint.

```yaml
asset_references:
  - name: orb_vocabulary
    asset_class: slam_vocabulary
    uri: "hf://UZ-SLAMLab/ORB_SLAM3/orbvoc.txt@v1.0?license=gpl_3_0"
    checksum: "sha256:abc123def456..."
    size_class: large_mb                     # tiny_kb | small_mb | medium_mb | large_mb | very_large_gb
    license: gpl_3_0                          # see RFC-0262 license enum; redundant when URI is hf:// with ?license=
    used_by:
      - perception.slam_substrate            # references the consumer for cross-audit
  - name: lab_map
    asset_class: occupancy_map
    uri: "file:///etc/urml/maps/lab_v3.pgm"
    checksum: "sha256:deadbeef..."
    size_class: small_mb
    map_metadata:
      resolution_m: 0.05
      origin: [0.0, 0.0]
  - name: ur5_urdf
    asset_class: urdf
    uri: "file:///etc/urml/robots/ur5_with_gripper.urdf"
    checksum: "sha256:cafe1234..."
    size_class: small_mb
  - name: gazebo_world
    asset_class: simulation_world
    uri: "file:///etc/urml/worlds/lab.world"
    checksum: "sha256:1234abcd..."
    size_class: small_mb
    used_by:
      - simulation.substrate
```

### Allowed values for `asset_class`

| Value | Description |
|---|---|
| `slam_vocabulary` | ORB vocabulary, BoW dictionary, or similar SLAM substrate asset |
| `occupancy_map` | Pre-built 2D occupancy grid (PGM / YAML pair) |
| `point_cloud_map` | 3D point cloud map (PCD / similar) |
| `urdf` | Unified Robot Description Format (kinematics) |
| `srdf` | Semantic Robot Description Format (MoveIt 2 groups, end-effectors) |
| `simulation_world` | Simulator world file (Gazebo .world, Webots .wbt, etc.) |
| `camera_calibration` | Camera intrinsics / extrinsics YAML |
| `imu_calibration` | IMU bias / scale calibration |
| `model_weights` | ML model weights (paired with hf:// URI from RFC-0277) |
| `voice_sample` | Reference voice samples for voice-cloning (RFC-0280) |
| `mesh_collection` | 3D meshes (STL / OBJ / GLB) for visualization or collision |
| `nav2_behavior_tree` | Nav2 behavior tree XML |
| `lua_config` | Cartographer Lua config (or similar) |
| `custom` | Vendor-specific asset class |

### Allowed values for `size_class`

| Value | Description |
|---|---|
| `tiny_kb` | < 100 KB (config files, small calibrations) |
| `small_mb` | 100 KB to 100 MB (typical maps, URDFs, weights for small models) |
| `medium_mb` | 100 MB to 1 GB (medium SLAM vocabularies, mid-sized weights) |
| `large_mb` | 1 GB to 10 GB (typical LLM weights, large maps) |
| `very_large_gb` | > 10 GB (frontier LLM weights, dataset-sized assets) |

### URI scheme support

The `uri` field accepts:

- **`file://`** — absolute filesystem path. Local deployment.
- **`hf://`** — Hugging Face Hub (per RFC-0277 scheme).
- **`http://`, `https://`** — HTTP-fetched assets. The validator does not fetch.
- **`s3://`** — S3-style object storage. Validator does not fetch.
- **`oci://`** — OCI artifact registry (emerging; future RFC may standardize).
- **`urml://`** — URML-managed asset registry (future RFC defines this).

### Schema fragment (Layer-1)

```jsonc
{
  "asset_references": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["name", "asset_class", "uri"],
      "properties": {
        "name": { "type": "string" },
        "asset_class": {
          "enum": [
            "slam_vocabulary", "occupancy_map", "point_cloud_map",
            "urdf", "srdf",
            "simulation_world",
            "camera_calibration", "imu_calibration",
            "model_weights", "voice_sample",
            "mesh_collection",
            "nav2_behavior_tree", "lua_config",
            "custom"
          ]
        },
        "asset_class_note": { "type": "string" },
        "uri": { "type": "string" },
        "checksum": {
          "type": "string",
          "pattern": "^(sha256|sha512|md5):[a-fA-F0-9]+$"
        },
        "size_class": {
          "enum": ["tiny_kb", "small_mb", "medium_mb", "large_mb", "very_large_gb"]
        },
        "license": { "$ref": "#/$defs/LicenseId" },
        "used_by": {
          "type": "array",
          "items": { "type": "string" }
        },
        "map_metadata": { "type": "object" }
      },
      "if": { "properties": { "asset_class": { "const": "custom" } } },
      "then": { "required": ["asset_class_note"] }
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing block acceptable; deployments without large external assets don't need to declare.
2. **Checksum recommended for non-tiny assets.** Soft suggestion: when `size_class` is `medium_mb` or larger, missing `checksum` emits a soft suggestion (reproducibility recommendation).
3. **`large_mb` / `very_large_gb` + `uri: file://` warning.** Local-filesystem URIs for large assets suggest the asset isn't reproducible from manifest alone; the validator surfaces.
4. **`uri: hf://` cross-check with `license` field.** If both are set, the validator compares the hf:// `?license=` query parameter with the declared `license` field. Mismatch emits a warning.
5. **`custom` requires note.**
6. **`used_by` cross-check.** When `used_by` references a manifest path (e.g., `perception.slam_substrate`), the validator can verify that the referenced field is set in the manifest. Mismatch emits an informational note (the asset may be used by external tooling not declared in the manifest).
7. **Forward-compat.** Closed enum on asset_class.

### Reference-runtime behavior

Reference runtimes read `asset_references` for startup-log diagnostics. The runtime does not auto-fetch URIs; it expects assets to be present in the locations declared. Pre-deployment tooling (a future `urml fetch-assets` command) could implement automatic fetching with checksum verification, but that's out of scope for this RFC.

### Conformance test additions

`conformance/tests/test_manifest_asset_references.py`:

1. Manifest without `asset_references` passes.
2. Manifest with `[{name: vocab, asset_class: slam_vocabulary, uri: hf://..., checksum: sha256:abc..., size_class: large_mb}]` passes.
3. Manifest with `size_class: large_mb` and no `checksum` passes with soft suggestion.
4. Manifest with `asset_class: slam_vocabulary, uri: hf://...?license=mit, license: gpl_3_0` passes with warning (license mismatch).
5. Manifest with `asset_class: custom` and no `asset_class_note` fails.

## Backward compatibility

Pre-v1.0. Additive. Existing per-substrate asset-path sub-fields (e.g., `perception.slam_options.config_reference`, `manipulation.robot_description`) continue to work; this RFC's `asset_references` block is a unified alternative that future deployments can adopt.

## Drawbacks

- **Coexistence with per-substrate asset sub-fields.** Some manifests will declare assets both in `asset_references` and in per-substrate sub-fields; the validator does not enforce non-duplication. Documentation only.
- **Asset class enum requires growth.** Future asset classes (training data, datasets, synthetic-data definitions) will require RFC amendments.
- **Checksum is opt-in.** Soft suggestion, not requirement. Operators can skip it; downstream reproducibility audit suffers.
- **`urml://` URI scheme is forward-reference.** This RFC mentions but doesn't define; a future RFC standardizes the URML asset-registry pattern.

## Alternatives considered

1. **Skip the unified block; keep per-substrate asset sub-fields.** Rejected. Unified declaration enables cross-asset audit and checksum hygiene.
2. **Use a single `assets` field as a map (name → details).** Considered. List shape mirrors RFC-0262's `licensing.components` pattern; consistency wins.
3. **Require checksums for all assets.** Rejected for v0.1. Backward-compat plus opt-in adoption is the right strength; future RFC could harden.
4. **Combine `asset_references` with `licensing.components` (RFC-0262).** Rejected. License is one of several asset-metadata concerns; assets have additional concerns (size, checksum, used_by tracking) that warrant a separate block.

## Prior art

- [RFC-0252 (slam_substrate)](0252-perception-slam-substrate.md) — surfaced ORB vocabulary as deferred-question.
- [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md) — surfaced vocabulary-file path concern.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md) — URDF / SRDF asset patterns.
- [RFC-0260 (language engines)](0260-language-engine-classes.md), [RFC-0277 (hf:// URI)](0277-language-huggingface-uri-scheme.md) — model-weight asset patterns.
- [RFC-0262 (licensing.boundary)](0262-licensing-boundary.md) — sibling Spec RFC for license declarations.
- [RFC-0269 (simulation.substrate)](0269-simulation-substrate.md) — world-file asset patterns.

## Unresolved questions

1. **`urml://` asset registry definition.** The URI scheme is referenced but not defined. Future RFC.
2. **Asset-discovery protocol.** Some assets are auto-discoverable from substrate runtime introspection; URML's manifest could declare discovery hints. Future RFC.
3. **Multi-file asset bundles.** Some assets ship across multiple files (model + tokenizer + config); URML's `asset_references` treats them as one entry today. Future RFC could add `bundle: [...]` sub-field.

## Implementation plan

1. JSON Schema fragment.
2. Validator with six checks.
3. Conformance tests (five).
4. Update example manifests with at least one asset-reference example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (coexistence with per-substrate fields, enum growth, opt-in checksums, forward-reference urml://).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0252, 0206, 0202, 0260, 0277, 0262, 0269.
- [x] CLAUDE.md compliance: reproducibility-discipline preserved; no-cloud invariant honored (validator does not fetch URIs).
