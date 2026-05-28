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

# Move #13 post bodies — open-source actuators + embedded / maker substrate (Theme C)

Copy-paste-ready Issue / Discussion bodies for the Move #13 outreach. **Wave shape**: 15 verified Theme C targets (10 Tier A + 5 Tier B), verified 2026-05-28. RFC numbers reserved 0169-0183.

Ledger state: [`outreach-move13.yaml`](outreach-move13.yaml). Full research audit: [`move13-research-2026-05-28.md`](move13-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("thirteen outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #13 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #13 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- **Actuator-controller substrate declaration** (ODrive RFC-0169, Moteus RFC-0170, SimpleFOC RFC-0179, VESC RFC-0180).
- **Stepper-driver chip-class declaration** (Trinamic RFC-0171).
- **MCU board-class declaration** (Arduino RFC-0173, Adafruit RFC-0174, Pi Pico RFC-0175, STM32 RFC-0182).
- **RTOS-substrate declaration** (micro-ROS RFC-0177, Zephyr RFC-0178).
- **Firmware-language substrate declaration** (CircuitPython Python RFC-0174, TinyGo Go RFC-0183).
- **Build-system substrate declaration** (PlatformIO RFC-0176).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / actuator-class escape-hatch and reference the queued Spec RFC.

**Three Tier-A rows carry license-clarification asks** (in the per-target unresolved-questions list):

- RFC-0173 Arduino (license listed as "Other").
- RFC-0180 VESC (no SPDX visible).
- RFC-0182 STMicroelectronics STM32Cube (mixed-license posture).

---

## Tier A — 10 vendor-direct / foundation-direct targets

### Motor controllers / actuators (3)

### RFC-0169: ODrive Robotics
**Post to**: https://github.com/odriverobotics/ODrive/issues/new (Issues enabled). Body TBD when RFC drafts.

### RFC-0170: mjbots Moteus
**Post to**: https://github.com/mjbots/moteus/issues/new (Issues enabled). Body TBD.

### RFC-0171: Trinamic TMC-API
**Post to**: https://github.com/Trinamic/TMC-API/issues/new (Issues enabled). Body TBD.

### MCU + maker platforms (5)

### RFC-0172: BBC micro:bit Foundation
**Post to**: https://github.com/microbit-foundation/micropython-microbit-v2/issues/new (Issues + Discussions enabled). Body TBD. Direct match to URML's existing `microbit_edu` manifest fixture (RFC-0018).

### RFC-0173: Arduino
**Post to**: https://github.com/arduino/Arduino/issues/new (Issues enabled). Body TBD. **License-clarification ask** (license listed as "Other").

### RFC-0174: Adafruit CircuitPython
**Post to**: https://github.com/adafruit/CircuitPython/discussions/new (Discussions enabled). Body TBD.

### RFC-0175: Raspberry Pi Pico SDK
**Post to**: https://github.com/raspberrypi/pico-sdk/issues/new (Issues enabled). Body TBD.

### RFC-0176: PlatformIO
**Post to**: https://github.com/platformio/platformio-core/issues/new (Issues enabled). Body TBD.

### Foundation-direct RTOS / framework (2)

### RFC-0177: micro-ROS
**Post to**: https://github.com/micro-ROS/micro_ros_setup/issues/new (Issues enabled). Body TBD. URML-fit framing: micro-ROS is the natural language-substrate bridge between URML primitives and MCU-class targets.

### RFC-0178: Zephyr Project
**Post to**: https://github.com/zephyrproject-rtos/zephyr/discussions/new (Discussions enabled). Body TBD.

---

## Tier B — 5 research-collab / cross-citation targets

### RFC-0179: SimpleFOC
**Post to**: https://github.com/simplefoc/Arduino-FOC/discussions/new (Discussions enabled). Body TBD.

### RFC-0180: VESC Project (vedderb/bldc)
**Post to**: https://github.com/vedderb/bldc/issues/new (Issues enabled). Body TBD. **License-clarification ask** (no SPDX visible).

### RFC-0181: Bitcraze Crazyflie
**Post to**: https://github.com/bitcraze/crazyflie-firmware/issues/new (Issues enabled). Body TBD. **GPL-3.0** — cross-citation framing.

### RFC-0182: STMicroelectronics STM32Cube
**Post to**: https://github.com/STMicroelectronics/STM32CubeF4/issues/new (Issues enabled). Body TBD. **License-clarification ask** (mixed-license posture).

### RFC-0183: TinyGo
**Post to**: https://github.com/tinygo-org/tinygo/discussions/new (Discussions enabled). Body TBD.

---

## Tier C (12) — recorded in research file, NOT engaged

See [`move13-research-2026-05-28.md`](move13-research-2026-05-28.md) for the full Tier-C list with exclusion causes (Shanghai-HQ NDAA operator-decision flag × 1 — Espressif/esp-idf; PRC origin × 1 — T-Motor; no GitHub presence × 3 — MyActuator, TI InstaSPIN, ADI motor refs; stale > 6mo × 4 — ODRI, Nordic, ARM Mbed, Tessel; wrong layer/theme × 3 — Franka Robotics, ROS 2 Controls, SparkFun). No posts.
