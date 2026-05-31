---
rfc: 0270
title: substrate.class — MCU substrate extensions (circuitpython, micropython, arduino, mbed, freertos)
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

# RFC-0270: `substrate.class` — MCU substrate extensions

## Summary

URML v0.1's `substrate.class` enum covers ROS 2, PX4, and a small set of operating-system-scale substrates. URML's Move-13 microcontroller outreach (CircuitPython engaged, Arduino, others) surfaced an entire substrate class URML can't name today: deployments running directly on a microcontroller without a host operating system. This RFC extends `substrate.class` with five MCU-substrate values (`circuitpython`, `micropython`, `arduino`, `mbed`, `freertos`), adds a `substrate.mcu_options` sub-block for board / chip / memory declarations, and defines validator behavior. Backward compatible.

The surface that demanded this RFC is Move-13 RFC-0174 (CircuitPython, engaged with Adafruit's @dhalbert).

## Motivation

URML's substrate-neutrality claim cannot be honest if the manifest can't declare deployments running on MCU substrates. A Crazyflie nano-drone running its own CRTP-firmware over a STM32 is a real URML target. A FIRST Robotics RoboRIO running WPILib is another. A Bittle quadruped running CircuitPython on a Seeeduino XIAO RP2040 is another. URML's manifest currently has no language to declare any of them.

Three concrete consequences of the gap:

1. **Substrate-neutrality is OS-biased.** URML's substrate enum implicitly assumes a host OS. MCU substrates run without one (or with FreeRTOS as the closest equivalent).
2. **Move-13 outreach has no manifest landing.** Adafruit's CircuitPython engagement (RFC-0174) requested URML manifest mapping for MCU deployments; URML cannot today.
3. **CRTP / G-code / direct-bus protocols make sense only in MCU context.** Sibling RFCs (RFC-0256 protocol.embedded_class, RFC-0266 motion_class) declare protocols and motion that only deploy on MCU substrates. The substrate class itself should be declarable.

## Detailed design

### Extension to `substrate.class` enum

| Value | Description | Reference |
|---|---|---|
| `ros2` | (existing) ROS 2 with RMW | RFC-0200 |
| `px4` | (existing) PX4 autopilot | RFC-0196 |
| `opc_ua_robotics` | (existing) OPC UA Robotics | RFC-0214 |
| `circuitpython` | NEW — Adafruit CircuitPython on MCU | Move-13 RFC-0174 |
| `micropython` | NEW — MicroPython on MCU | Cross-reference |
| `arduino` | NEW — Arduino framework (C++ libraries on AVR / ARM / RP2040 / ESP32) | Move-13 outreach |
| `mbed` | NEW — Arm Mbed OS | Cross-reference |
| `freertos` | NEW — FreeRTOS (lightweight RTOS) | Cross-reference |
| `custom` | (existing) escape hatch | n/a |

### `mcu_options` sub-block

```yaml
substrate:
  class: circuitpython                       # NEW
  mcu_options:                                # NEW — this RFC
    board: seeeduino_xiao_rp2040             # board identifier
    chip: rp2040                              # MCU family identifier
    flash_kb: 2048                            # storage budget
    ram_kb: 264                               # RAM budget
    bus_protocols:                            # MCU-side communication
      - type: i2c
        speed_khz: 400
      - type: spi
        speed_mhz: 8
      - type: uart
        baud: 115200
    library_bundle: circuitpython_community_bundle  # informational
```

### Schema fragment (Layer-1 substrate block extension)

```jsonc
{
  "substrate": {
    "properties": {
      "class": {
        "enum": [
          "ros2", "px4", "opc_ua_robotics",
          "circuitpython", "micropython", "arduino", "mbed", "freertos",
          "custom"
        ]
      },
      "mcu_options": {
        "type": "object",
        "properties": {
          "board": { "type": "string" },
          "chip": { "type": "string" },
          "flash_kb": { "type": "integer", "minimum": 1 },
          "ram_kb": { "type": "integer", "minimum": 1 },
          "bus_protocols": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["type"],
              "properties": {
                "type": { "enum": ["i2c", "spi", "uart", "can", "usb", "ethernet"] },
                "speed_khz": { "type": "integer" },
                "speed_mhz": { "type": "integer" },
                "baud": { "type": "integer" }
              }
            }
          },
          "library_bundle": { "type": "string" }
        }
      }
    },
    "if": {
      "properties": {
        "class": {
          "enum": ["circuitpython", "micropython", "arduino", "mbed", "freertos"]
        }
      }
    },
    "then": {
      "required": ["mcu_options"],
      "properties": {
        "mcu_options": {
          "required": ["board", "chip"]
        }
      }
    }
  }
}
```

### Validator behavior

1. **MCU class triggers required `mcu_options`.** Each MCU substrate class requires the sub-block with at least `board` and `chip` declared.
2. **MCU substrate incompatible with RMW.** `substrate.class: circuitpython + substrate.rmw_implementation: rmw_fastrtps_cpp` fails. MCU substrates do not host RMW; the validator catches the inconsistency.
3. **MCU substrate incompatible with `ipc_substrate: iceoryx`.** iceoryx requires shared-memory + RouDi daemon; MCU substrates don't host them.
4. **`bus_protocols` consistency.** `type: i2c` requires `speed_khz` (or default); `type: spi` requires `speed_mhz`; `type: uart` requires `baud`. Validator emits warning on missing-but-needed fields.
5. **Memory budget sanity.** `flash_kb` and `ram_kb` must be `>= 1`. The validator does not enforce upper bounds (MCU vendors vary widely from <100KB to 16MB+ flash).
6. **Forward-compat.** Closed enum.

### Reference-runtime behavior

URML's `reference/ros2-runtime/` does not target MCU substrates. A future `reference/mcu-runtime/` (or per-MCU-class adapters: `reference/circuitpython-runtime/`, etc.) is candidate work. Until those ship, URML's MCU support is at the manifest-declaration layer only; the validator accepts the declarations, and downstream tooling (e.g., the Crazyflie-CRTP adapter that pairs with this RFC's `circuitpython` value plus RFC-0256's `crtp` protocol value) consumes them.

### Conformance test additions

`conformance/tests/test_manifest_mcu_substrate.py`:

1. Manifest with `substrate.class: circuitpython + mcu_options.board + mcu_options.chip` passes.
2. Manifest with `substrate.class: circuitpython` without `mcu_options` fails.
3. Manifest with `substrate.class: circuitpython + substrate.rmw_implementation: rmw_fastrtps_cpp` fails (incompatible).
4. Manifest with `bus_protocols: [{type: i2c}]` without `speed_khz` passes with warning.
5. Existing manifests with `substrate.class: ros2` continue to validate (backward-compat).

## Backward compatibility

Pre-v1.0. Additive: existing manifests with `ros2 / px4 / opc_ua_robotics / custom` unchanged. New values extend the enum.

## Drawbacks

- **MCU substrate scope expansion is significant.** URML moves from OS-scale substrates to MCU-scale; the validator and reference runtime story grows.
- **No reference-runtime yet for MCU substrates.** This RFC scopes the manifest declaration; the runtime is future work.
- **`bus_protocols` array is loose.** Per-protocol field validation is partial. A tighter schema with per-type required-fields could be added (similar to RFC-0263 measurement_options pattern); v0.1 of this field uses soft warnings.
- **Five new substrate.class values is a big expansion at once.** Each value has its own ecosystem; URML accepts all five in the same RFC because they share the MCU-substrate frame, but the cost is a more interesting validator-test surface.

## Alternatives considered

1. **Single `mcu` substrate.class value with framework sub-field.** Rejected. CircuitPython, MicroPython, Arduino, Mbed, FreeRTOS are structurally distinct frameworks; collapsing loses precision.
2. **Skip MCU substrate; treat Crazyflie as `ros2 + crazyflie_bridge`.** Rejected. The bridge pattern works but masks the substrate-neutrality claim; explicit MCU declaration is more honest.
3. **Only add `circuitpython` (the engaged surface from Move-13).** Rejected. The remaining four MCU substrates are obvious siblings; declaring them together preserves the open-door framing for future Move-13 outreach to other MCU communities.
4. **Use a new `mcu` top-level field rather than extending substrate.class.** Rejected. Substrate.class is the canonical declaration layer; extending preserves URML's structural model.

## Prior art

- [Move-13 RFC-0174 (CircuitPython outreach)](0174-circuitpython-outreach.md) — first MCU-substrate engagement, dhalbert engaged at Adafruit.
- [Move-18 RFC-0229 (Crazyflie outreach)](0229-crazyflie-outreach.md) — nano-drone CRTP firmware, MCU substrate; pairs with this RFC's `circuitpython` or `freertos` values plus RFC-0256's `crtp` protocol.
- [Move-18 RFC-0228 (WPILib outreach)](0228-wpilib-outreach.md) — FIRST Robotics RoboRIO; pairs with this RFC's `freertos` or `arduino` value plus RFC-0266's `swerve` drive_type.
- [RFC-0256 (protocol.embedded_class)](0256-protocol-embedded-class.md) — sibling Spec RFC; CRTP value lives in `protocol.embedded_class`.
- [RFC-0266 (motion_class)](0266-mobility-motion-class.md) — sibling Spec RFC; education-tier drive_types compose with MCU substrates.

## Unresolved questions

1. **ESP32 sub-class.** ESP32 (Espressif) runs Arduino, ESP-IDF, and MicroPython. URML's manifest declares one framework; ESP32 deployments declare the framework they target, not the chip. Future RFC could add chip-family enumeration.
2. **CMSIS-NN / on-MCU ML.** Some MCU substrates run on-device neural inference (CMSIS-NN, TensorFlow Lite Micro). URML's manifest doesn't capture this dimension today.
3. **Cross-MCU communication protocols.** When multiple MCUs in a deployment talk over CAN / RS-485 / wireless, URML's manifest doesn't capture the inter-MCU topology. Future RFC.

## Implementation plan

1. JSON Schema fragment with extended enum + mcu_options sub-block.
2. Validator with consistency checks (MCU ↔ RMW / IPC incompatibility, bus_protocols partial validation).
3. Conformance tests (five).
4. Update example manifests to include at least one MCU example.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (substrate scope expansion, no runtime yet, loose bus_protocols schema, five-value expansion).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to Move-13 outreach (0174), Move-18 outreach (0228, 0229), sibling Spec RFCs (0256, 0266).
- [x] CLAUDE.md compliance: substrate-neutrality preserved (URML doesn't prefer one MCU framework); enum closure preserves moat.
