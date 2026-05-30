---
rfc: 0281
title: substrate.bridges — cross-substrate bridge declarations (MAVLink-DDS, G-code-DDS, MQTT)
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

# RFC-0281: `substrate.bridges` — cross-substrate bridge declarations

## Summary

RFC-0274 added `multi_rmw.bridges` for cross-RMW bridges within ROS 2 deployments (DDS-to-Zenoh, DDS-to-DDS, Zenoh-to-Zenoh). Real production deployments often bridge across substrate boundaries entirely: MAVLink to ROS 2 (mavros, mavros2), G-code controller to ROS 2 (custom adapters for Klipper-driven cells), MQTT broker to ROS 2 (IoT gateway patterns), OPC UA to ROS 2 (industrial cell integration). URML's manifest has no place today to declare these cross-substrate bridges. This RFC adds a top-level `substrate.bridges` field generalizing RFC-0274's bridge concept, with closed enum bridge types, namespace-filter declarations, and protocol-translation metadata. Optional. Backward compatible.

The surfaces that demanded this RFC are RFC-0274 deferred questions on MAVLink-DDS and G-code-DDS bridges.

## Motivation

URML's substrate-neutrality means a single deployment can span multiple substrate classes: a drone deployment (PX4 + MAVLink) with a ROS 2 ground-station, an industrial cell (Klipper + G-code) with a ROS 2 supervisor, an outdoor robot with MQTT-published telemetry to a cloud-edge gateway. Each pattern needs a bridge between substrate classes that URML's manifest currently cannot express.

Three concrete consequences of the gap:

1. **Production drone deployments use mavros (MAVLink-DDS bridge) ubiquitously.** URML's manifest declares the PX4 autopilot and the ROS 2 ground-station separately but has no way to declare the mavros bridge that connects them.
2. **Industrial fabrication integration is ad-hoc.** Klipper-driven 3D-printer cells with ROS 2 supervisors use custom bridge code; URML's manifest could declare the bridge pattern formally.
3. **MQTT IoT gateways are common but undocumented.** Many outdoor-robotics deployments publish telemetry to MQTT brokers via custom bridge nodes; URML's manifest should capture the bridge declaration.

## Detailed design

### Field shape

`substrate.bridges` is a top-level list (parallel to RFC-0274's `multi_rmw.bridges` which covered RMW-to-RMW bridges only).

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp
  bridges:                                   # NEW — this RFC, top-level list
    - type: mavlink_to_dds
      name: mavros_bridge
      source_substrate:
        class: px4
        autopilot_class: px4                  # see RFC-0250
      target_substrate:
        class: ros2
        rmw_implementation: rmw_fastrtps_cpp
      namespace_filter: "/uav1/**"
      protocol_translation:
        mavlink_version: v2                   # see RFC-0256 protocol_options
        ros_message_pkg: mavros_msgs
        bidirectional: true
    - type: gcode_to_dds
      name: klipper_bridge
      source_substrate:
        class: ros2                            # the supervisor side is ROS 2
      target_substrate:
        class: custom
        custom_note: Klipper Klippy host
      namespace_filter: "/fabrication/**"
      protocol_translation:
        gcode_dialect: klipper                 # see RFC-0271 fabrication_options
        transport: uds
        socket: /tmp/klippy_uds
        bidirectional: false                   # supervisor sends G-code; no return path
    - type: mqtt_to_dds
      name: cloud_telemetry_bridge
      source_substrate:
        class: ros2
      target_substrate:
        class: custom
        custom_note: MQTT broker (cloud)
      namespace_filter: "/telemetry/**"
      protocol_translation:
        mqtt_broker: mqtt://broker.example.org:8883
        mqtt_topic_prefix: robots/fleet-a/
        qos_level: 1                           # MQTT QoS 0/1/2
        tls_enabled: true
        bidirectional: false
```

### Allowed values for `type`

| Value | Description | Reference |
|---|---|---|
| `mavlink_to_dds` | MAVLink (drone autopilot) to DDS (ROS 2) bridge; mavros / mavros2 pattern | RFC-0197 + RFC-0274 |
| `dds_to_mavlink` | Reverse direction; ROS 2 commands compile to MAVLink messages | RFC-0197 |
| `gcode_to_dds` | G-code controller (Klipper, Marlin) to DDS bridge | RFC-0271 |
| `dds_to_gcode` | Reverse; DDS topics generate G-code on the controller side | RFC-0271 |
| `mqtt_to_dds` | MQTT broker (IoT gateway) to DDS bridge | New |
| `dds_to_mqtt` | DDS to MQTT (publish DDS topics to MQTT broker) | New |
| `opc_ua_to_dds` | OPC UA server to DDS bridge | RFC-0214 |
| `dds_to_opc_ua` | DDS to OPC UA (publish ROS 2 topics to OPC UA address space) | RFC-0214 |
| `dds_to_dds` | DDS-to-DDS bridge (cross-implementation) | RFC-0274 (kept for compatibility) |
| `dds_to_zenoh` | DDS-to-Zenoh bridge | RFC-0274 (kept for compatibility) |
| `custom` | Vendor-specific bridge | escape hatch + `type_note` required |

### Schema fragment (Layer-1)

```jsonc
{
  "substrate": {
    "properties": {
      "bridges": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["type", "name", "source_substrate", "target_substrate"],
          "properties": {
            "type": {
              "enum": [
                "mavlink_to_dds", "dds_to_mavlink",
                "gcode_to_dds", "dds_to_gcode",
                "mqtt_to_dds", "dds_to_mqtt",
                "opc_ua_to_dds", "dds_to_opc_ua",
                "dds_to_dds", "dds_to_zenoh",
                "custom"
              ]
            },
            "type_note": { "type": "string" },
            "name": { "type": "string" },
            "source_substrate": { "type": "object" },
            "target_substrate": { "type": "object" },
            "namespace_filter": { "type": "string" },
            "protocol_translation": { "type": "object" }
          }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional list.** Missing block acceptable; deployment is single-substrate.
2. **Required name + type + source + target.** Each bridge entry must declare all four.
3. **Bidirectional consistency.** When `protocol_translation.bidirectional: true`, the validator checks that both directions are operationally valid (e.g., MAVLink-DDS supports bidirectional; MQTT-DDS may be unidirectional depending on broker support).
4. **`mqtt_to_dds + tls_enabled: false` warning.** Unencrypted MQTT over public networks is a security concern; the validator surfaces.
5. **`custom` requires `type_note`.**
6. **Substrate-class cross-check.** When the deployment declares `substrate.class: px4` but no `mavlink_to_dds` bridge AND a ROS 2 ground-station node is declared, the validator emits a soft suggestion noting that mavros is the common pattern.
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read the bridges list and spawn the appropriate bridge processes. For mavros (mavlink_to_dds), the runtime launches the mavros2 node with the declared MAVLink endpoint. For Klipper (gcode_to_dds), the runtime composes against the Klippy UDS socket. For MQTT (mqtt_to_dds), the runtime starts the bridge node with broker credentials from a `secret_reference` (RFC-0262 convention).

### Conformance test additions

`conformance/tests/test_manifest_bridges.py`:

1. Manifest without `bridges` passes (single-substrate).
2. Manifest with `bridges: [{type: mavlink_to_dds, name: mavros, source_substrate: {class: px4}, target_substrate: {class: ros2}}]` passes.
3. Manifest with `bridges: [{type: mqtt_to_dds, protocol_translation.tls_enabled: false}]` passes with warning.
4. Manifest with `type: custom` and no `type_note` fails.
5. Drone manifest (px4 substrate) without `mavlink_to_dds` bridge passes with soft suggestion.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests without bridges unchanged. RFC-0274's `multi_rmw.bridges` continues to work; this RFC's top-level `substrate.bridges` is a superset that subsumes the DDS-to-DDS / DDS-to-Zenoh cases.

## Drawbacks

- **Bridge taxonomy is opinion.** Ten enum values capture the dominant cases; novel bridges go in `custom`.
- **`source_substrate` / `target_substrate` field shapes are partial.** Full substrate descriptions can be elaborate; the validator allows shallow declarations that cite the substrate.class plus type-specific fields. Future RFC could deepen.
- **Bidirectional flag is binary.** Some bridges support per-topic directionality (some topics flow one way, others another). v0.1 of this field is per-bridge.
- **MQTT QoS field semantics differ from ROS 2 QoS.** The `qos_level: 0/1/2` for MQTT is the MQTT broker's QoS level, not the ROS 2 QoS profile. The validator does not confuse them; the field is per-bridge.

## Alternatives considered

1. **Skip cross-substrate bridges; declare each substrate separately and let runtime infer.** Rejected. Production deployments need explicit bridge declaration for reproducibility and audit.
2. **Merge RFC-0274's `multi_rmw.bridges` into this RFC's `substrate.bridges`.** Considered. The two could merge; for backward compatibility, RFC-0274's existing field continues to work and this RFC's field accepts the same bridge types as a superset.
3. **Per-bridge protocol-translation schema as a closed object.** Rejected. Protocol-specific fields vary widely (MAVLink uses version + dialect; MQTT uses broker + QoS; OPC UA uses NodeID space); free-object schema accommodates the variance.
4. **Treat MQTT as a `substrate.class` value alongside ros2/px4/opc_ua_robotics.** Rejected. MQTT is a transport pattern, not a substrate in URML's sense; bridging is the right framing.

## Prior art

- [RFC-0274 (multi_rmw)](0274-substrate-multi-rmw-deployment.md) — parent Spec RFC; this RFC closes the deferred MAVLink-DDS and G-code-DDS bridge questions.
- [RFC-0197 (MAVLink outreach)](0197-mavlink-outreach.md), [RFC-0214 (OPC UA outreach)](0214-opc-foundation-ua-nodeset-outreach.md) — outreach RFCs that surfaced cross-substrate integration patterns.
- [RFC-0250 (substrate.autopilot_class)](0250-substrate-autopilot-class.md), [RFC-0256 (protocol.embedded_class)](0256-protocol-embedded-class.md), [RFC-0271 (protocol.fabrication_class)](0271-protocol-gcode-substrate.md) — sibling Spec RFCs whose substrates this RFC's bridges connect.
- mavros / mavros2 (ROS 2 community), Klipper Klippy UDS pattern (community-documented), mqtt_bridge / mqtt_client (ROS community).

## Unresolved questions

1. **Discovery-server overlay declarations.** RFC-0274 also deferred Discovery Server overlay declarations; that's a sibling future RFC, not part of this RFC.
2. **Per-topic transformation declarations.** Some bridges transform messages (e.g., MAVLink GLOBAL_POSITION_INT to NavSatFix); URML's manifest could declare the transformation map. Future RFC.
3. **Bridge node lifecycle declarations.** When does the bridge start (deployment boot, on-demand, watchdog)? Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with seven checks.
3. Conformance tests (five).
4. Reference-runtime bridge-spawning hooks.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (taxonomy opinion, partial substrate descriptions, binary bidirectional, MQTT QoS semantics).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0274 (parent), 0197, 0214, 0250, 0256, 0271 (substrates being bridged).
- [x] CLAUDE.md compliance: substrate-neutrality preserved (URML doesn't prefer one bridge pattern); enum closure preserved.
