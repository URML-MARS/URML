---
rfc: 0271
title: protocol.fabrication_class — declaring G-code (and successor) protocols for fabrication motion
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

# RFC-0271: `protocol.fabrication_class` — G-code substrate declaration

## Summary

RFC-0266 added `mobility.motion_class: fabrication` for 3D-printer / CNC fabrication-motion platforms and reserved the sibling fabrication-protocol declaration for a follow-up RFC. This RFC closes that loop: adds `protocol.fabrication_class` as a sibling list to `protocol.embedded_class` (RFC-0256) with closed enum values for G-code (the dominant fabrication protocol) and its variants, plus a `fabrication_options` sub-block for transport and dialect declarations. Required when `mobility.motion_class: fabrication` is declared. Backward compatible.

The surface that demanded this RFC is Move-18 RFC-0227 (Klipper outreach), with the deferral noted in RFC-0266.

## Motivation

Fabrication motion (RFC-0266) is dispatched through G-code in the overwhelming majority of cases. Klipper, Marlin, GRBL, LinuxCNC, and direct controller firmware all consume G-code as their motion-command language. The G-code dialect varies (RepRap-flavor for 3D printers, classic ISO 6983 for CNC, vendor-specific extensions), and the transport varies (serial UART, USB-serial, Klipper's UDS socket, file-based G-code uploads).

URML's manifest declares fabrication motion at the mobility layer (RFC-0266) but has no place to declare the protocol layer underneath. Three concrete consequences of the gap:

1. **`mobility.motion_class: fabrication` is incomplete without protocol.** The validator can pass the motion_class declaration but cannot verify the deployment ships with a compatible G-code dispatcher.
2. **Dialect differences matter at validate time.** RepRap G-code's M-codes for hot-end temperature differ from CNC G-code's M-codes for spindle control. URML's manifest declaring the dialect lets the validator surface dialect-specific deployment guidance.
3. **Klipper / Marlin transport diversity.** Klipper supports serial + USB + UDS; Marlin supports serial + SD-card; GRBL supports serial + WebSocket. URML's manifest needs to declare the transport to validate end-to-end.

## Detailed design

### Field shape

`protocol.fabrication_class` is a **list** like `protocol.embedded_class` (RFC-0256), allowing multi-protocol deployments (e.g., G-code over serial for primary motion + custom JSON-RPC over WebSocket for parameter queries).

```yaml
protocol:
  embedded_class:                            # from RFC-0256
    - mavlink                                # not for fabrication; example shows drone
  fabrication_class:                         # NEW — this RFC, list-valued
    - gcode
    - klipper_extras                         # Klipper's macro extensions
  fabrication_options:                       # NEW — per-protocol sub-blocks
    gcode:
      dialect: reprap                        # reprap | iso_6983 | grbl | marlin | klipper | custom
      version: "1.0"                          # informational
      transport:
        type: serial                          # serial | usb | uds | file_upload | websocket
        device: /dev/ttyUSB0
        baud: 250000
      safety_envelope:
        max_feedrate_mm_s: 200
        thermal_limit_c: 280                  # extruder thermal limit
    klipper_extras:
      transport:
        type: uds
        socket: /tmp/klippy_uds
```

### Allowed values for `fabrication_class`

| Value | Description | Reference |
|---|---|---|
| `gcode` | Generic G-code (covers all dialects) | Move-18 RFC-0227 (Klipper) |
| `klipper_extras` | Klipper-specific macro extensions over UDS socket | RFC-0227 |
| `marlin_extras` | Marlin-specific M-code extensions | Move-18 RFC-0231 (Marlin; staged) |
| `linuxcnc_hal` | LinuxCNC HAL (Hardware Abstraction Layer) | Move-18 RFC-0233 (LinuxCNC; staged) |
| `custom` | Vendor-specific | escape hatch + `fabrication_class_note` required |

### Allowed values for `gcode.dialect`

| Value | Description |
|---|---|
| `reprap` | RepRap-flavor (most 3D-printer firmware) |
| `iso_6983` | ISO 6983 classic CNC G-code |
| `grbl` | GRBL (CNC-focused subset) |
| `marlin` | Marlin-flavor (extensions over RepRap) |
| `klipper` | Klipper-flavor (extensions over RepRap) |
| `custom` | Vendor-specific dialect |

### Schema fragment (Layer-1, extending RFC-0256)

```jsonc
{
  "protocol": {
    "properties": {
      "fabrication_class": {
        "type": "array",
        "items": {
          "enum": ["gcode", "klipper_extras", "marlin_extras", "linuxcnc_hal", "custom"]
        },
        "minItems": 1,
        "uniqueItems": true
      },
      "fabrication_class_note": { "type": "string" },
      "fabrication_options": {
        "type": "object",
        "properties": {
          "gcode": {
            "type": "object",
            "properties": {
              "dialect": {
                "enum": ["reprap", "iso_6983", "grbl", "marlin", "klipper", "custom"]
              },
              "version": { "type": "string" },
              "transport": { "$ref": "#/$defs/FabricationTransport" },
              "safety_envelope": {
                "type": "object",
                "properties": {
                  "max_feedrate_mm_s": { "type": "number", "minimum": 0 },
                  "thermal_limit_c": { "type": "number" }
                }
              }
            }
          }
        }
      }
    }
  },
  "$defs": {
    "FabricationTransport": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "enum": ["serial", "usb", "uds", "file_upload", "websocket"]
        },
        "device": { "type": "string" },
        "baud": { "type": "integer" },
        "socket": { "type": "string" }
      }
    }
  }
}
```

### Validator behavior

1. **Required-when-fabrication.** If `mobility.motion_class: fabrication`, `protocol.fabrication_class` must be declared with at least one value.
2. **`fabrication_class: gcode` requires `dialect`.** Missing dialect emits a warning (defaults to `reprap` for downstream consumers).
3. **Transport ↔ device-field consistency.** `type: serial` requires `device` and `baud`. `type: uds` requires `socket`. `type: file_upload` requires `device` (the path to write the G-code file). `type: websocket` requires endpoint info (future RFC; v0.1 accepts as informational).
4. **Klipper/Marlin extras coexistence.** `fabrication_class: [gcode, klipper_extras]` is valid (Klipper accepts standard G-code over serial AND Klipper-specific macros over UDS). The validator accepts the combination.
5. **Custom requires note.** `fabrication_class: [custom, ...]` requires `fabrication_class_note`.
6. **Cross-class consistency.** `protocol.embedded_class` (for drone substrates) and `protocol.fabrication_class` are mutually exclusive: a deployment cannot be both drone and fabrication. The validator catches the combination.
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

URML does not yet ship a fabrication-runtime reference. A future `reference/fabrication-runtime/` composes against Klipper / Marlin / LinuxCNC via the declared `fabrication_class`. URML's manifest declares the protocol expectation; the runtime dispatches.

### Conformance test additions

`conformance/tests/test_manifest_fabrication_class.py`:

1. Fabrication manifest with `fabrication_class: [gcode] + gcode.dialect: reprap + transport.type: serial + device: /dev/ttyUSB0 + baud: 250000` passes.
2. Fabrication manifest without `fabrication_class` fails.
3. Fabrication manifest with `fabrication_class: [gcode]` and no dialect passes with warning.
4. Non-fabrication manifest without `fabrication_class` passes.
5. Manifest declaring both `embedded_class: [mavlink]` and `fabrication_class: [gcode]` fails (mutual exclusion).

## Backward compatibility

Pre-v1.0. Additive. Existing manifests that don't declare `motion_class: fabrication` unchanged. Manifests that do declare it (added in RFC-0266) gain a required sibling field.

## Drawbacks

- **G-code dialect proliferation.** Each firmware (Klipper, Marlin, GRBL, LinuxCNC, FluidNC, Smoothieware) has its own extensions. URML's enum captures the dominant cases; the long tail uses `custom`.
- **`fabrication_options` parallel to `protocol_options` (RFC-0256).** Two sibling sub-blocks; the symmetry is intentional but adds cognitive overhead.
- **`safety_envelope` inside fabrication_options overlaps with the top-level `safety_envelope` field.** Per-protocol safety bounds (G-code-side) vs deployment-wide envelope (URML's Layer-1) are different scopes; documenting the layering is the discipline.
- **No reference fabrication-runtime yet.** Sibling to RFC-0270 (MCU substrate); both ship manifest declarations without their corresponding runtime adapter today.

## Alternatives considered

1. **Add G-code to `protocol.embedded_class` instead of separate `fabrication_class`.** Rejected. Embedded protocols (MAVLink, DroneCAN, CRTP) are conceptually different from fabrication protocols (G-code dialects). Sibling lists keep the structure clean.
2. **Single `gcode` value with sub-fields for everything.** Rejected. Klipper extras over UDS are a separate protocol surface; treating them as a separate enum value is honest.
3. **Skip `fabrication_class`; let the substrate-side runtime figure it out.** Rejected. URML's discipline is that the manifest is the contract.
4. **Treat G-code-over-file-upload separately from over-serial.** Considered; folded into `transport.type` per RFC-0256's pattern.

## Prior art

- [Move-18 RFC-0227 (Klipper outreach)](0227-klipper-outreach.md) — the outreach RFC that surfaced this field.
- [Move-18 RFC-0231 (Marlin), RFC-0233 (LinuxCNC)](0231-marlin-outreach.md) — staged in user's Move-18 batches; pairs with this RFC's enum values.
- [RFC-0266 (mobility.motion_class)](0266-mobility-motion-class.md) — parent Spec RFC; this RFC closes the fabrication-protocol-declaration deferral.
- [RFC-0256 (protocol.embedded_class)](0256-protocol-embedded-class.md) — sibling Spec RFC; this RFC mirrors the list-valued + per-protocol options pattern.

## Unresolved questions

1. **STEP / IGES / native-CAD protocol declarations.** Some industrial fabrication consumes STEP files directly; URML's manifest doesn't capture this today.
2. **Multi-axis fabrication beyond XYZ.** 5-axis CNC needs `axis_count: 5` in mobility (RFC-0266 deferred) plus fabrication-protocol-side multi-axis declaration. Future RFC.
3. **Thermal / spindle / coolant declarations.** Fabrication safety envelopes extend beyond motion; thermal limits, spindle RPM bounds, coolant flow declarations. v0.1 captures thermal_limit_c; the rest is future work.

## Implementation plan

1. JSON Schema fragment extending RFC-0256 protocol block.
2. Validator with required-when-fabrication + transport-consistency + mutual-exclusion checks.
3. Conformance tests (five).
4. Update example manifests with at least one fabrication example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (dialect proliferation, parallel sub-blocks, safety_envelope overlap, no runtime yet).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to Move-18 outreach (0227, 0231, 0233 staged) + sibling Spec RFCs (0256, 0266).
- [x] CLAUDE.md compliance: enum closure preserves moat; substrate-neutrality preserved (URML doesn't prefer Klipper over Marlin); list-valued shape matches production reality.
