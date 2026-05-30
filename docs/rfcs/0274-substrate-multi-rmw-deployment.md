---
rfc: 0274
title: substrate.rmw_options.multi_rmw — declaring multi-RMW deployments in the Layer-1 manifest
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

# RFC-0274: `substrate.rmw_options.multi_rmw` — multi-RMW deployment declaration

## Summary

RFC-0251 deferred the multi-RMW deployment question. Some production deployments run different RMWs for different namespaces or different nodes: Fast DDS for sensor traffic where the multicast discovery works, Cyclone DDS for control traffic where the latency profile is better, Zenoh for WAN-bridged traffic where the routing model fits. URML's manifest cannot today declare such a topology. This RFC adds a `multi_rmw` sub-block to `rmw_options` that overrides the deployment-wide `rmw_implementation` (RFC-0251) on a per-namespace or per-node basis, with bridge-declaration fields for cross-RMW traffic. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0251 (deferred from Move-16 substrate-spine engagement).

## Motivation

Production fleet-scale deployments increasingly mix RMWs. The patterns:

- Sensor traffic: Fast DDS multicast discovery on the local LAN; transient-local durability for robot_description; best-effort for high-rate sensor topics.
- Control traffic: Cyclone DDS for predictable low-latency dispatch.
- WAN bridging: Zenoh for cross-site routing without DDS-side discovery overhead.

URML's manifest declaring deployment-wide `rmw_implementation` (RFC-0251) doesn't capture this. Three concrete consequences of the gap:

1. **Real production topologies are undocumented.** Maintainers running multi-RMW deployments work around URML's manifest, undermining the validator-as-contract property.
2. **Cross-RMW bridge declarations are nowhere.** Multi-RMW deployments need a DDS-to-DDS or DDS-to-Zenoh bridge (rmw_zenoh comes with a bridge; vendor-specific bridges exist). URML's manifest needs to declare the bridge layer.
3. **Per-namespace dispatch ambiguity.** Without manifest declaration, downstream tooling can't tell which RMW is responsible for which namespace.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp        # from RFC-0251 — deployment-wide default
  rmw_options:
    multi_rmw:                                # NEW — this RFC, list of namespace/node overrides
      overrides:
        - namespace_pattern: "/sensors/**"
          rmw_implementation: rmw_fastrtps_cpp  # explicit; same as default but documented
        - namespace_pattern: "/control/**"
          rmw_implementation: rmw_cyclonedds_cpp
        - node_pattern: "wan_bridge"
          rmw_implementation: rmw_zenoh_cpp
      bridges:
        - type: dds_to_zenoh
          endpoint: tcp/router.example.org:7447
          namespace_filter: "/sensors/**"
        - type: dds_to_dds
          source_rmw: rmw_fastrtps_cpp
          target_rmw: rmw_cyclonedds_cpp
          namespace_filter: "/shared/**"
```

### `overrides` array semantics

Each override declares one of:

- `namespace_pattern`: glob-style namespace match (e.g., `/sensors/**` matches everything under `/sensors/`).
- `node_pattern`: glob-style node-name match (similar to RFC-0272 per-node QoS).

Per override:

- `rmw_implementation`: required; one of the values defined in RFC-0251 (`rmw_fastrtps_cpp`, `rmw_cyclonedds_cpp`, `rmw_zenoh_cpp`, `rmw_connextdds`, `custom`).
- Optional `rmw_options` overrides per-namespace / per-node (e.g., the namespace uses Cyclone DDS with a specific XML config).

### `bridges` array semantics

Each bridge declares a cross-RMW or cross-substrate traffic path:

- `type`: bridge type. `dds_to_zenoh` is the common case (Zenoh router bridging DDS traffic). `dds_to_dds` covers cross-DDS bridges where a deployment needs to mix two DDS implementations.
- `endpoint`: bridge endpoint URI (Zenoh routers use `tcp://host:port`).
- `source_rmw` / `target_rmw`: the two RMWs the bridge connects.
- `namespace_filter`: limits which topics the bridge forwards.

### Allowed values for `bridges.type`

| Value | Description |
|---|---|
| `dds_to_zenoh` | DDS-to-Zenoh bridge (the rmw_zenoh / zenoh-bridge pattern) |
| `dds_to_dds` | DDS-to-DDS bridge (cross-RMW DDS interop) |
| `zenoh_to_zenoh` | Zenoh router federation (multi-router topology) |
| `custom` | Vendor-specific bridge; requires `bridge_note` |

### Precedence rules

When a topic creation needs an RMW choice:

1. **`overrides` (per-namespace / per-node)** — first-match wins.
2. **Deployment-wide `rmw_implementation`** (RFC-0251) — the default.

Within overrides, per-node matches win over per-namespace matches when both could apply (consistent with RFC-0272's more-specific-wins discipline).

### Schema fragment (extending RFC-0251)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_options": {
        "properties": {
          "multi_rmw": {
            "type": "object",
            "properties": {
              "overrides": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["rmw_implementation"],
                  "properties": {
                    "namespace_pattern": { "type": "string" },
                    "node_pattern": { "type": "string" },
                    "rmw_implementation": { "$ref": "#/$defs/RmwImplementation" },
                    "rmw_options": { "type": "object" }
                  },
                  "oneOf": [
                    { "required": ["namespace_pattern"] },
                    { "required": ["node_pattern"] }
                  ]
                }
              },
              "bridges": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["type"],
                  "properties": {
                    "type": {
                      "enum": ["dds_to_zenoh", "dds_to_dds", "zenoh_to_zenoh", "custom"]
                    },
                    "bridge_note": { "type": "string" },
                    "endpoint": { "type": "string" },
                    "source_rmw": { "$ref": "#/$defs/RmwImplementation" },
                    "target_rmw": { "$ref": "#/$defs/RmwImplementation" },
                    "namespace_filter": { "type": "string" }
                  },
                  "if": { "properties": { "type": { "const": "custom" } } },
                  "then": { "required": ["bridge_note"] }
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

1. **Optional block.** Missing block means single-RMW deployment per RFC-0251.
2. **Override entries require exactly one of `namespace_pattern` or `node_pattern`.** A single override can't target both at once (different schemas for different scoping).
3. **First-match wins.** When multiple overrides could match, the validator emits an informational note documenting the resolution.
4. **Bridge consistency.** When `bridges` declares a `dds_to_dds` bridge with `source_rmw` and `target_rmw`, both must appear in at least one override (or be the deployment-wide default). Inconsistency emits a warning.
5. **Topology sanity.** When a deployment declares three or more RMWs without bridge declarations, the validator emits an informational note suggesting bridge declarations for cross-RMW topics.
6. **`zenoh_to_zenoh` bridge requires Zenoh in at least one override.** Inconsistency fails.
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes use the multi_rmw overrides to spawn per-namespace / per-node RMW contexts. ROS 2 supports this via launch-time `RMW_IMPLEMENTATION` env var per-node; URML's runtime sets the env var per the declared override before launching each node. Bridge declarations spawn bridge processes (Zenoh routers, DDS-to-DDS bridges) according to the topology.

### Conformance test additions

`conformance/tests/test_manifest_multi_rmw.py`:

1. Manifest without `multi_rmw` passes (single-RMW per RFC-0251).
2. Manifest with namespace override `/sensors/** → rmw_fastrtps_cpp` and deployment-wide `rmw_cyclonedds_cpp` passes.
3. Manifest with override declaring neither `namespace_pattern` nor `node_pattern` fails (schema requires one).
4. Manifest with `dds_to_dds` bridge declaring source_rmw not in any override emits warning.
5. Manifest with `bridges.type: custom` and no `bridge_note` fails.

## Backward compatibility

Pre-v1.0. Additive. Single-RMW deployments unchanged.

## Drawbacks

- **Operational complexity is real.** Multi-RMW topologies are inherently more complex than single-RMW; URML's manifest captures the complexity rather than hides it. The cost is that simple deployments don't need this block.
- **Bridge configuration depth is partial.** Zenoh routers have many tunable parameters (downsampling, deduplication, key-expression rewriting); URML's manifest declares the bridge existence and namespace filter; the per-bridge config lives in the bridge's own config file.
- **Cross-RMW QoS interop is not standardized.** When two RMWs bridge, the QoS interpretation can diverge in corner cases. URML's manifest doesn't capture this; it's a substrate-side concern.
- **Three-layer precedence (per-topic from RFC-0265, per-node from RFC-0272, per-namespace / per-node here).** The precedence rules grow; documentation must be clear.

## Alternatives considered

1. **Skip multi-RMW; treat each as a separate deployment with single-RMW manifest.** Rejected. The bridge configuration is intrinsic to the deployment; separate manifests would lose the bridge declaration.
2. **Merge `multi_rmw.overrides` with per-topic / per-node QoS overrides into one unified list.** Rejected. QoS and RMW are different concerns; combining them inflates the schema.
3. **Per-process RMW declaration (one entry per node launch).** Rejected. The override-pattern shape is more compact for namespace-uniform deployments; per-process granularity is over-engineered for v0.1.
4. **Treat bridges as a separate top-level field outside `rmw_options`.** Considered. Bridges are RMW-related and live under `rmw_options` naturally; top-level placement would be future work if bridges expand beyond RMW concerns (e.g., to MAVLink-DDS bridges or G-code-DDS bridges).

## Prior art

- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — parent Spec RFC; this RFC closes the deferred multi-RMW-deployment question.
- [RFC-0265 (qos_profile_overrides)](0265-substrate-rmw-qos-overrides.md), [RFC-0272 (per_node_qos)](0272-substrate-rmw-per-node-qos.md), [RFC-0273 (dds_security)](0273-substrate-dds-security-profile.md) — sibling RFCs all extending RFC-0251's `rmw_options`.
- ROS 2 multi-RMW patterns (rmw_zenoh + zenoh-bridge precedent).

## Unresolved questions

1. **MAVLink-DDS bridges.** Some drone deployments bridge MAVLink (RFC-0197) to ROS 2 / DDS (e.g., mavros). URML's manifest could declare such a bridge; v0.1 of this RFC is RMW-centric. Future RFC.
2. **G-code-DDS bridges.** Klipper (RFC-0227, motion_class: fabrication via RFC-0266) doesn't typically bridge to DDS, but some integrated industrial-fabrication deployments do. Future RFC.
3. **Discovery-server overlay declarations.** Fast DDS Discovery Server can sit in front of multi-RMW topologies; URML's manifest doesn't capture this. Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with override-schema + bridge consistency + topology sanity checks.
3. Conformance tests (five).
4. Reference-runtime per-namespace RMW selection at launch time.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (operational complexity, partial bridge config, cross-RMW QoS, three-layer precedence).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0251 (parent), RFC-0265 + RFC-0272 + RFC-0273 (siblings extending rmw_options).
- [x] CLAUDE.md compliance: substrate-neutrality preserved across multi-RMW topologies; enum closure preserved.
