---
rfc: 0251
title: substrate.rmw_implementation — declaring the ROS 2 RMW middleware in the Layer-1 manifest
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

# RFC-0251: `substrate.rmw_implementation` — declaring the ROS 2 RMW middleware

## Summary

URML's primary substrate is ROS 2, and ROS 2 runs over an RMW (ROS Middleware) layer that has several swappable implementations: Fast DDS (the default since Foxy), Cyclone DDS (the Eclipse Foundation alternative used by Autoware and Foxglove), Zenoh (an emerging next-generation pub-sub overlay), and others. The choice of RMW materially affects QoS profile semantics, discovery topology, latency, and corner-case behavior. URML's manifest cannot today declare which RMW the deployment runs. This RFC adds `substrate.rmw_implementation` to the Layer-1 manifest, with a closed enum, a `qos_profile` sub-field, and a discovery-topology field, defines validator behavior, and adds conformance test coverage. The field is optional when `substrate.class` is not `ros2`. No primitive changes. Backward compatible.

The surfaces that demanded this RFC are RFC-0200 (ROS 2 core outreach), RFC-0203 (Fast DDS outreach), RFC-0204 (Cyclone DDS outreach), and RFC-0209 (Zenoh outreach).

## Motivation

ROS 2's substrate-neutral message-passing API hides which RMW implementation is active, by design. URML's manifest, by contrast, exists precisely to make substrate choices explicit and validator-checkable. Without `rmw_implementation` declaration, three concrete problems follow:

1. **QoS profile semantics drift between implementations.** Reliability, durability, history, deadline, and lifespan policies interact differently with Fast DDS vs Cyclone DDS at corner cases (large fan-out, transient subscribers, multi-network discovery). URML programs that rely on QoS guarantees cannot be statically validated without knowing the RMW.
2. **Discovery topology varies.** Fast DDS supports Simple Discovery and Discovery Server. Cyclone DDS supports XML-configured topology with partitions. Zenoh supports peer/client/router modes. URML's manifest cannot today declare which discovery topology the deployment uses.
3. **DDS-Security profiles are RMW-specific.** Authentication and access-control plugins differ; URML's manifest has no place to declare which security profile is active. This RFC scopes that field for future work but does not land it.

The four outreach RFCs (0200, 0203, 0204, 0209) all flag this gap explicitly. Move-16 substrate-spine engagement cannot honestly continue without this field.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp     # NEW — this RFC
  rmw_options:                              # NEW — this RFC, optional
    qos_profile:
      reliability: reliable                # reliable | best_effort
      durability: volatile                 # volatile | transient_local | transient | persistent
      history: keep_last                   # keep_last | keep_all
      history_depth: 10                    # required when history == keep_last
      deadline_ms: 100                     # optional
      lifespan_ms: 1000                    # optional
    discovery_topology: simple             # simple | discovery_server | xml_configured | peer | client | router
    config_reference: /etc/urml/dds.xml    # optional, RMW-specific config file path
```

### Allowed values for `rmw_implementation`

The enum is closed, like `substrate.autopilot_class` (RFC-0250). Growth requires its own follow-up RFC.

| Value | Description | Reference |
|---|---|---|
| `rmw_fastrtps_cpp` | eProsima Fast DDS (default ROS 2 RMW since Foxy) | RFC-0203 |
| `rmw_cyclonedds_cpp` | Eclipse Cyclone DDS | RFC-0204 |
| `rmw_zenoh_cpp` | Eclipse Zenoh (substrate-emerging) | RFC-0209 |
| `rmw_connextdds` | RTI Connext DDS (commercial; supported for completeness) | Not yet engaged via outreach |
| `custom` | Vendor-specific or experimental RMW | Escape hatch; requires `rmw_implementation_note` free-text |

The value `rmw_zenoh_cpp` is marked substrate-emerging via the `substrate.maturity_tier` field (sibling RFC-0254). URML accepts it for validate-time declaration but the conformance suite may flag substrate-emerging deployments in its output.

### Schema fragment (JSON Schema additions to Layer-1)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_implementation": {
        "type": "string",
        "enum": [
          "rmw_fastrtps_cpp",
          "rmw_cyclonedds_cpp",
          "rmw_zenoh_cpp",
          "rmw_connextdds",
          "custom"
        ]
      },
      "rmw_implementation_note": {
        "type": "string",
        "description": "Required when rmw_implementation == custom."
      },
      "rmw_options": {
        "type": "object",
        "properties": {
          "qos_profile": { "$ref": "#/$defs/QosProfile" },
          "discovery_topology": {
            "type": "string",
            "enum": ["simple", "discovery_server", "xml_configured", "peer", "client", "router"]
          },
          "config_reference": { "type": "string" }
        }
      }
    },
    "if": {
      "properties": { "class": { "const": "ros2" } }
    },
    "then": {
      "required": ["rmw_implementation"]
    }
  },
  "$defs": {
    "QosProfile": {
      "type": "object",
      "properties": {
        "reliability": { "enum": ["reliable", "best_effort"] },
        "durability": { "enum": ["volatile", "transient_local", "transient", "persistent"] },
        "history": { "enum": ["keep_last", "keep_all"] },
        "history_depth": { "type": "integer", "minimum": 1 },
        "deadline_ms": { "type": "integer", "minimum": 0 },
        "lifespan_ms": { "type": "integer", "minimum": 0 }
      },
      "if": { "properties": { "history": { "const": "keep_last" } } },
      "then": { "required": ["history_depth"] }
    }
  }
}
```

### Validator behavior

Five checks added:

1. **Required-when-ros2.** If `substrate.class: ros2`, the manifest must declare `substrate.rmw_implementation`.
2. **Custom note.** If `rmw_implementation: custom`, `rmw_implementation_note` must be a non-empty string.
3. **History depth required.** If `qos_profile.history: keep_last`, `qos_profile.history_depth` must be present.
4. **Discovery-topology compatibility.** Some `discovery_topology` values are only valid with certain `rmw_implementation` values. For example, `xml_configured` is meaningful for Cyclone DDS but not for Fast DDS Simple Discovery. The validator emits a warning (not a hard error) on incompatible pairings; a future RFC may harden this to an error once URML has full coverage of cross-RMW compatibility tables.
5. **Forward-compat for unknown values.** Closed enum; unknown values fail with a pointer to this RFC.

### Reference-runtime behavior

`reference/ros2-runtime/` already targets the RMW via the `RMW_IMPLEMENTATION` environment variable. This RFC adds a `Manifest -> environment` mapping: when the manifest declares `rmw_implementation`, the runtime sets `RMW_IMPLEMENTATION` accordingly on dispatch. The `rmw_options.config_reference` is passed via the RMW-specific environment variable (Cyclone DDS reads `CYCLONEDDS_URI`; Fast DDS reads `FASTRTPS_DEFAULT_PROFILES_FILE`; the runtime knows which variable to set from the implementation choice).

### Conformance test additions

`conformance/tests/test_manifest_rmw_implementation.py` adds:

1. A `ros2` manifest without `rmw_implementation` fails validation.
2. A `ros2` manifest with `rmw_implementation: rmw_fastrtps_cpp` passes.
3. A QoS profile with `history: keep_last` and no `history_depth` fails.
4. A `discovery_topology: xml_configured` paired with `rmw_implementation: rmw_fastrtps_cpp` emits a warning but does not fail.
5. A manifest with `rmw_implementation: custom` and no note fails; with a note, passes.

## Backward compatibility

Pre-v1.0. Additive at the field level. Existing `ros2`-class manifests that don't declare RMW will start failing validation. The migration path: any URML user with an existing manifest declares `rmw_implementation: rmw_fastrtps_cpp` (the historical default) explicitly. The example manifests in `examples/` are updated in the same PR.

## Drawbacks

- **Enum closure refuses unknown RMWs.** Same as RFC-0250: a deployment with a brand-new RMW must file an RFC. The closure preserves the validator-as-static-gate property.
- **Required-when-ros2 is a breaking change for non-conformant manifests.** Existing manifests must declare the field; the migration is a one-line addition. The example manifests in the URML repo are updated in the same PR.
- **QoS sub-field expressivity is partial.** v0.1 of this field set covers the QoS profile types most commonly cited across outreach. Several less-common policies (resource limits, history-cache, custom DataReader/Writer QoS) are intentionally out of scope here.
- **`config_reference` is a per-RMW string and not parsed by URML.** The validator does not interpret the referenced file. This is intentional: each RMW has its own config format, and parsing them would tie URML's validator to RMW-specific schemas.

## Alternatives considered

1. **Use ROS 2's `RMW_IMPLEMENTATION` env var directly without manifest declaration.** Rejected. Env-var-only is not statically validatable. URML's discipline is that the manifest is the contract.
2. **Single field for combined `rmw_implementation + qos_profile`.** Rejected. They're independent degrees of freedom; combining them would inflate the enum past the closure horizon.
3. **`rmw_options` as a free-form object.** Rejected. The discovery-topology and QoS fields are common enough to deserve typed structure. Free-form leaks the same validator-as-gate property the enum closure was designed to preserve.
4. **Defer Zenoh value (`rmw_zenoh_cpp`) until Zenoh stabilizes as ROS 2 default.** Rejected. URML's substrate-emerging tier (RFC-0254) is the right place to mark Zenoh's status; refusing the value would close the door to deployments already using Zenoh today.

## Prior art

- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — surfaced the RMW-implementation field as URML's missing manifest layer.
- [RFC-0203 (Fast DDS outreach)](0203-fast-dds-outreach.md), [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md), [RFC-0209 (Zenoh outreach)](0209-zenoh-outreach.md) — per-implementation outreach RFCs.
- [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — sibling IPC-sub-substrate engagement; `substrate.ipc_substrate` (separate future RFC) is the parallel field for intra-process zero-copy IPC declaration.
- [RFC-0254 (substrate.maturity_tier)](0254-substrate-maturity-tier.md) — sibling Spec RFC that classifies `rmw_zenoh_cpp` as substrate-emerging.

## Unresolved questions

1. **DDS-Security profile field.** Authentication and access-control plugins differ between RMWs. URML's manifest could declare a security-profile reference. This RFC scopes it for future work; the right time is when URML has at least one engaged security-relevant deployment to inform the field shape.
2. **Multi-RMW deployments.** Some production deployments use different RMWs per namespace (Fast DDS for some traffic, Cyclone DDS for others). URML's manifest is single-RMW per deployment today. Multi-RMW expression is future work, not landed here.
3. **Per-topic QoS overrides.** The current shape declares deployment-wide QoS. ROS 2 supports per-topic QoS profiles. Future RFC if the demand surfaces.

## Implementation plan

1. Land the JSON Schema fragment in the Layer-1 schema source.
2. Land the validator checks.
3. Land the conformance tests.
4. Update the example manifests under `examples/` to declare `rmw_fastrtps_cpp` explicitly.
5. Land the runtime-side `Manifest -> environment` mapping in `reference/ros2-runtime/`.

Single atomic PR.

## How to respond

Spec RFC. Comments in the PR thread. Implementation in the same PR.

## Self-review (Phase 0)

- [x] At least one alternative considered (four).
- [x] Drawbacks named honestly (enum closure, breaking-change for non-conformant ros2 manifests, partial QoS expressivity, `config_reference` opacity).
- [x] Backward compatibility documented; migration path one-line for users.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Validator behavior fully specified.
- [x] Cross-references to outreach RFCs that surfaced the gap.
- [x] CLAUDE.md compliance: enum closure preserves moat; substrate-emerging value (`rmw_zenoh_cpp`) is honestly classified via sibling RFC-0254.
