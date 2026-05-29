---
rfc: 0256
title: protocol.embedded_class — declaring the embedded-network protocol in the Layer-1 manifest
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

# RFC-0256: `protocol.embedded_class` — declaring the embedded-network protocol

## Summary

URML's drone substrate (RFC-0250 `substrate.autopilot_class`) dispatches over an embedded-network protocol. MAVLink is the default over serial / UDP / TCP. DroneCAN is the alternative over CAN-bus. Some deployments use both: MAVLink for autopilot ↔ ground-station and DroneCAN for autopilot ↔ ESCs. URML's manifest cannot today declare which protocol class the deployment uses. This RFC adds `protocol.embedded_class` to the Layer-1 manifest as a list-valued field (because multi-protocol topologies are common), with a closed enum, a per-protocol `protocol_options` sub-block, and defines validator behavior. Required for drone deployments. Backward compatible (additive).

The surface that demanded this RFC is Move-16 RFC-0199 (DroneCAN libcanard outreach).

## Motivation

Drone deployments today span at least two protocol families:

- **MAVLink** (RFC-0197) over serial / UDP / TCP. The default autopilot ↔ ground-station protocol.
- **DroneCAN** (RFC-0199) over CAN-bus. The embedded-network protocol for autopilot ↔ ESC, autopilot ↔ smart-sensor, autopilot ↔ servo.

A real deployment runs MAVLink upstream and DroneCAN downstream. URML's manifest needs to declare both protocols and their respective configurations. Three concrete consequences of the gap:

1. **Static-validation incomplete.** A Layer-2 program that targets a DroneCAN-only ESC cannot be validated against a manifest that only declares MAVLink.
2. **CAN-FD vs classic CAN distinction.** DroneCAN supports both CAN-FD (faster, larger frames) and classic CAN. URML's manifest needs to capture the transport choice for embedded-resource validation.
3. **Multi-system topology in MAVLink.** A deployment with multiple drones, multiple ground stations, and routing components requires MAVLink system_id / component_id declaration. URML's manifest cannot today declare the topology.

The Move-16 RFC-0199 explicitly requests this field. Move-16 RFC-0197 (MAVLink) requests the multi-system topology declaration.

## Detailed design

### Field shape

`protocol.embedded_class` is a **list** because multi-protocol topologies are the production case, not the exception.

```yaml
protocol:
  embedded_class:                            # NEW — this RFC, list-valued
    - mavlink
    - dronecan
  protocol_options:                          # NEW — per-protocol sub-blocks
    mavlink:
      version: v2                            # v1 | v2
      dialect: common                        # common | ardupilotmega | development | custom
      signing_enabled: false
      system_id: 1
      component_id: 1
      transport:
        - type: udp
          endpoint: 127.0.0.1:14550
        - type: serial
          device: /dev/ttyUSB0
          baud: 57600
    dronecan:
      version: v1                            # v0 (UAVCAN v0) | v1 (DroneCAN v1)
      transport: can_fd                      # classic_can | can_fd
      node_id_space: [10, 127]               # reserved node-ID range
      dsdl_dialect: standard                 # standard | vendor
```

### Allowed values for `embedded_class`

| Value | Description | Reference |
|---|---|---|
| `mavlink` | MAVLink (serial / UDP / TCP) | RFC-0197 |
| `dronecan` | DroneCAN (CAN-bus) | RFC-0199 |
| `crtp` | Bitcraze CRTP (Crazyflie nano-drones) | Move-18 RFC-0229 |
| `custom` | Vendor-specific or experimental protocol | escape hatch + `embedded_class_note` required (list-paired) |

### Allowed values for protocol-specific sub-blocks

**MAVLink:**

| Field | Values |
|---|---|
| `version` | `v1`, `v2` |
| `dialect` | `common`, `ardupilotmega`, `development`, `custom` |
| `signing_enabled` | boolean |
| `system_id` | integer 1-255 |
| `component_id` | integer 1-255 |
| `transport` | list of `{type, endpoint, ...}` — `type` in `udp`, `tcp`, `serial` |

**DroneCAN:**

| Field | Values |
|---|---|
| `version` | `v0` (UAVCAN v0), `v1` (DroneCAN v1) |
| `transport` | `classic_can`, `can_fd` |
| `node_id_space` | [low, high] integer pair |
| `dsdl_dialect` | `standard`, `vendor` |

**CRTP** (sketch, future-extension):

| Field | Values |
|---|---|
| `version` | `crtp1` |
| `transport` | `radio_2_4ghz`, `usb` |

### Schema fragment (Layer-1)

```jsonc
{
  "protocol": {
    "type": "object",
    "properties": {
      "embedded_class": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["mavlink", "dronecan", "crtp", "custom"]
        },
        "minItems": 1,
        "uniqueItems": true
      },
      "embedded_class_note": { "type": "string" },
      "protocol_options": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "mavlink": { "$ref": "#/$defs/MavlinkOptions" },
          "dronecan": { "$ref": "#/$defs/DronecanOptions" },
          "crtp": { "$ref": "#/$defs/CrtpOptions" }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Required-when-drone.** If `mobility.drive_type` is `multirotor`, `fixed_wing`, or `vtol`, the manifest must declare `protocol.embedded_class` with at least one value.
2. **Per-protocol options consistency.** For each value in `embedded_class`, the corresponding sub-block in `protocol_options` must be present if any options are needed. Missing options sub-block is allowed; the runtime falls back to substrate-side defaults.
3. **Custom requires note.** If `custom` appears in the list, `embedded_class_note` must be non-empty.
4. **DroneCAN node-ID range validation.** If `dronecan.node_id_space` is set, the validator checks the pair is `[low, high]` with `1 <= low <= high <= 127`.
5. **MAVLink system_id + component_id range.** Both must be in `[1, 255]`.
6. **Forward-compat.** Closed enum on `embedded_class`. Sub-block schemas are per-protocol-versioned.

### Reference-runtime behavior

`reference/ros2-runtime/` and `reference/drone-runtime/` read `protocol.embedded_class` to select the dispatch path. Multi-protocol deployments route each topic / service through its declared protocol. The runtime does not multiplex protocols itself; it dispatches per the manifest declaration.

### Conformance test additions

`conformance/tests/test_manifest_protocol_embedded_class.py`:

1. Drone manifest with `embedded_class: [mavlink]` passes.
2. Drone manifest with `embedded_class: [mavlink, dronecan]` and both option sub-blocks passes.
3. Non-drone manifest without `embedded_class` field passes.
4. Drone manifest without `embedded_class` fails.
5. Drone manifest with `embedded_class: [custom]` and no note fails.

## Backward compatibility

Pre-v1.0. Additive at the field level. Existing drone manifests that didn't declare embedded protocol must add the field; the migration is one-line per manifest. Example manifests in the URML repo are updated in the same PR.

## Drawbacks

- **List-valued primary field is unusual.** Most URML manifest fields are scalar. The list shape mirrors the production reality of multi-protocol drone deployments.
- **`crtp` value covers a single use case.** Crazyflie nano-drones are the only CRTP target today. The value exists because Move-18 explicitly engaged Bitcraze; growth via outreach.
- **MAVLink dialect field is opinionated.** `common`, `ardupilotmega`, `development`, `custom` is the practical enumeration today. A new dialect requires an RFC amendment.
- **No declaration for protocol bridging.** Real-world deployments often use mavros (MAVLink-to-ROS-2 bridge) or similar. URML's manifest declares the wire protocol; the bridge layer is downstream of that.

## Alternatives considered

1. **Single-valued `embedded_class` instead of list.** Rejected. Multi-protocol topologies are real and the manifest needs to express them.
2. **Per-topic protocol declaration instead of deployment-wide.** Rejected for v0.1. Most deployments are protocol-homogeneous within a layer (autopilot ↔ ground-station = MAVLink; autopilot ↔ ESC = DroneCAN); per-topic granularity would be over-engineering.
3. **Inline protocol options as object instead of `protocol_options` sub-block.** Rejected. Keeping options in a per-protocol sub-block keeps the schema readable.
4. **`embedded_class: required` only for `substrate.autopilot_class` declarations.** Rejected. The autopilot_class field is required when drive_type is drone-class; embedded_class follows the same trigger.

## Prior art

- [RFC-0197 (MAVLink outreach)](0197-mavlink-outreach.md), [RFC-0199 (DroneCAN libcanard outreach)](0199-dronecan-libcanard-outreach.md) — the outreach RFCs that surfaced this field.
- [RFC-0229 (Crazyflie outreach)](0229-crazyflie-outreach.md) — Move-18 CRTP engagement; adds the `crtp` value.
- [RFC-0250 (substrate.autopilot_class)](0250-substrate-autopilot-class.md) — sibling Spec RFC; declares the autopilot stack that runs above the embedded-network protocol.
- [RFC-0008 (drone profile)](0008-drone-profile.md) — URML's drone profile that consumes this field.

## Unresolved questions

1. **Per-protocol QoS / reliability declaration.** MAVLink has per-message reliability semantics; DroneCAN's CAN-bus is reliable-by-arbitration. URML's manifest could declare per-protocol reliability hints. Future RFC.
2. **Protocol-version compatibility matrix.** MAVLink v1 ↔ v2 cross-talk is supported but with caveats. URML's manifest doesn't capture the caveats today.
3. **CRTP option schema.** Bitcraze CRTP detailed options are out of scope for this RFC; a future RFC (timed with Crazyflie outreach response) defines them.

## Implementation plan

1. JSON Schema fragment with `$defs` per protocol.
2. Validator with per-protocol consistency checks.
3. Conformance tests.
4. Update drone-profile example manifests.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (list-valued field unusual, single-use CRTP value, dialect opinion, no bridging declaration).
- [x] Backward compatibility additive at field level; required-when-drone is one-line migration.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (0197, 0199, 0229) and sibling Spec RFCs (0250, 0008).
- [x] CLAUDE.md compliance: enum closure preserves moat; list-valued shape reflects production reality without adding configuration knobs.
