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

Copy-paste-ready Issue / Discussion bodies for the Move #13 outreach. **Wave shape**: 15 verified Theme C targets (10 Tier A + 5 Tier B), verified 2026-05-28. RFC numbers 0169-0183.

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
- **MCU + maker board-class declaration** (micro:bit RFC-0172, Arduino RFC-0173, Adafruit RFC-0174, Pi Pico RFC-0175, STM32 RFC-0182).
- **Firmware-language substrate declaration** (Python-on-MCU: micro:bit RFC-0172, Adafruit CircuitPython RFC-0174; Go-on-MCU: TinyGo RFC-0183).
- **Build-system substrate declaration** (PlatformIO RFC-0176).
- **MCU-side ROS 2 substrate + multi-RTOS + DDS-XRCE QoS** (micro-ROS RFC-0177).
- **RTOS substrate + scheduling-class + TF-M secure-boot** (Zephyr RFC-0178).
- **Nano-quadcopter payload-class + CRTP protocol substrate + firmware-license-boundary** (Crazyflie RFC-0181).
- **Mixed-license-surface declaration** (STM32 RFC-0182).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` measurement_type / `actuator_class: custom` / `substrate: custom` escape-hatch and reference the queued Spec RFC.

**Three Tier-A/B rows carry license-clarification asks** in their per-target question lists:

- RFC-0173 Arduino (LGPL libraries vs GPL IDE per-surface disambiguation).
- RFC-0180 VESC (no SPDX upstream; GPL-3.0 per LICENSE inspection).
- RFC-0182 STMicroelectronics STM32Cube (mixed-license posture, per-surface clarification).

**One cross-citation framing for GPL-3.0 firmware:**

- RFC-0181 Bitcraze Crazyflie — URML integrates at the Apache-2.0 `crazyflie-lib-python` client boundary, not by embedding the GPL-3.0 firmware.

---

## Tier A — 10 vendor-direct / foundation-direct targets

### Motor controllers / actuators (3)

### RFC-0169: ODrive Robotics

**Post to:** https://github.com/odriverobotics/ODrive/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for ODrive — Layer-0 actuator-controller substrate
```

**Body:**

```markdown
Hi @odriverobotics team,

Proposing a URML v0.1 capability-manifest mapping for ODrive over `odriverobotics/ODrive`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

ODrive is the Layer-0 actuator-controller substrate URML's manifest declares per axis. Where URML's prior outreach engaged the runtime / sensor / VLA layers, ODrive is the actuator-control silicon-and-firmware substrate one layer below the ROS 2 / micro-ROS adapter. Stanford Pupper / Solo / similar legged-research platforms that use ODrive-class drives fit URML's existing quadruped / biped manifest fixtures naturally with ODrive as the declared actuator class.

This is **proposal-only**, posted as part of URML's Move #13 outreach (open-source actuators + embedded / maker substrate, 15 engageable RFCs). No bridge in URML's repo yet; a bridge would ship engagement-driven.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0169-odrive-robotics-outreach.md

Questions worth `odriverobotics` maintainer input on:

1. **Actuator-controller substrate manifest fields.** URML's v0.1 has no `brushless_motor_controller` actuator class. A Spec RFC is queued. What manifest fields would an ODrive deployment expect (product_line, interface, firmware_version, encoder_class, control-mode declaration)?
2. **Interface-class declaration.** USB-native, CAN-simple, Cyphal/CAN-FD — should URML's manifest declare which is the active host-side protocol?
3. **Closed-loop firmware pinning.** Should URML's manifest pin firmware version for reproducible closed-loop control behavior?
4. **Bridge home.** URML repo (`reference/actuator-runtime/ODriveAdapter`), ODrive-maintained `odriverobotics/odrive-urml-bridge`, or external?
5. **Conformance listing.** Would ODrive consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0170: mjbots Moteus

**Post to:** https://github.com/mjbots/moteus/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Moteus — high-bandwidth brushless servo substrate
```

**Body:**

```markdown
Hi @mjbots team,

Proposing a URML v0.1 capability-manifest mapping for Moteus over `mjbots/moteus`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

Moteus is the high-bandwidth (>1kHz position control) brushless-servo substrate URML's manifest declares for legged / dynamic robot actuators. URML's existing quadruped + biped manifest fixtures imply an underlying actuator-controller substrate URML's v0.1 manifest does not yet make first-class; Moteus is the natural Layer-0 declaration for the legged class (MIT Cheetah lineage, Stanford Pupper, Berkeley Humanoid Lite, etc.).

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0170-mjbots-moteus-outreach.md

Questions worth `mjbots` maintainer input on:

1. **Actuator-controller substrate manifest fields.** Same shared question across the Move-13 motor-controller RFCs — what manifest fields would a Moteus deployment expect?
2. **Control-bandwidth declaration.** Should URML's manifest declare control-loop bandwidth requirements (Hz) for legged-robot deployments?
3. **FD-CAN interface class.** Manifest declaration for FD-CAN vs standard CAN vs USB-serial?
4. **Bridge home.** URML repo (`reference/actuator-runtime/MoteusAdapter`), mjbots-maintained, or external?
5. **Conformance listing.** Would mjbots consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0171: Trinamic TMC-API

**Post to:** https://github.com/Trinamic/TMC-API/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for TMC-API — stepper-driver chip-class substrate
```

**Body:**

```markdown
Hi @Trinamic team,

Proposing a URML v0.1 capability-manifest cross-citation for the TMC-series stepper drivers over `Trinamic/TMC-API`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

TMC chips sit at the **chip-class layer** — one layer below the host-side controller class URML engaged with sibling Move-13 motor-controller RFCs. URML's manifest declares which TMC driver class is present + active configuration (step/dir vs SPI interface, microstep resolution, StallGuard sensorless-homing); the actual chip-level firmware lives outside URML. Cross-citation framing recommended given the chip-vs-robotics-stack engagement-level mismatch.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0171-trinamic-tmc-api-outreach.md

Questions worth `Trinamic` maintainer input on:

1. **Engagement-level preference.** Chip-vendor level (here) or integrator-level (recommend specific OEMs / boards)?
2. **Stepper-driver chip-class manifest fields.** URML's v0.1 has no `stepper_driver_chip` actuator class. Spec RFC queued. Manifest field expectations (product_line, interface, microstep_resolution, sensorless-homing class)?
3. **Step/dir vs SPI declaration.** Should URML's manifest declare which interface mode is active?
4. **Bridge home.** Cross-citation only (recommended given chip-class), URML repo, or Trinamic-maintained?
5. **Conformance listing.** Would Trinamic / ADI consider a README link to URML's compatible-runtimes registry once a working integration ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### MCU + maker platforms (5)

### RFC-0172: BBC micro:bit Foundation

**Post to:** https://github.com/microbit-foundation/micropython-microbit-v2/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for micro:bit v2 — and a refinement of URML's existing microbit_edu fixture
```

**Body:**

```markdown
Hi @microbit-foundation team,

Proposing a URML v0.1 capability-manifest mapping for the BBC micro:bit v2 over `microbit-foundation/micropython-microbit-v2`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's `microbit_edu` manifest fixture has been the canonical URML pattern for the **micro-class robot** since RFC-0018 — engagement at the Foundation level closes the loop upstream. The fixture sketches the micro:bit v2 manifest mapping (nRF52833 main MCU + KL27Z interface MCU, MicroPython firmware-language, accelerometer + magnetometer + microphone + speaker + LED matrix + buttons); your view on its refinement carries unusual weight for downstream educational deployments.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0172-microbit-foundation-outreach.md

Questions worth `microbit-foundation` maintainer input on:

1. **Manifest fixture refinement.** URML's existing `microbit_edu` fixture sketches the micro:bit v2 manifest mapping. What fields would the foundation refine / add?
2. **MicroPython vs MakeCode declaration.** Should URML's manifest declare which firmware-language substrate is loaded?
3. **Educational-class declaration.** Useful manifest flag for K-12 deployments + default safety envelopes?
4. **Adapter home.** URML repo (`reference/edu-runtime/MicrobitAdapter`), micro:bit-Foundation-maintained `microbit-foundation/microbit-urml-bridge`, or both?
5. **Conformance listing.** Would the foundation consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0173: Arduino

**Post to:** https://github.com/arduino/Arduino/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Arduino-compatible boards — and a license-clarification ask
```

**Body:**

```markdown
Hi @arduino team,

Proposing a URML v0.1 capability-manifest mapping for Arduino-compatible boards over `arduino/Arduino`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

Arduino is the world's largest hobbyist MCU platform; URML's manifest declares Arduino-compatible board class so the same English-language URML program retargets across Uno / Nano / Mega / MKR / Portenta variants by manifest swap. **License-clarification ask** is the gating fact: the repo's license is listed as "Other" by the GitHub API. Arduino's source has historically been a mix of LGPL (libraries) and GPL (IDE), with the trademark layer kept separate; URML's adapter-grade reuse depends on per-surface clarity.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0173-arduino-outreach.md

Questions worth `arduino` maintainer input on:

1. **License clarification.** Can `arduino/Arduino` get an explicit OSI license declaration (LGPL libraries / GPL IDE / which-on-which-surface)?
2. **Arduino-compatible board-class manifest fields.** URML's v0.1 has no `arduino_compatible` mcu_class. Spec RFC queued. Manifest field expectations (FQBN, board_identifier, package_manager dependencies)?
3. **License-surface manifest declaration.** Should URML's manifest declare the license boundary the firmware was built against?
4. **Adapter home.** URML repo (`reference/edu-runtime/ArduinoAdapter`), Arduino-maintained `arduino/arduino-urml-bridge`, or both?
5. **Conformance listing.** Would Arduino consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0174: Adafruit CircuitPython

**Post to:** https://github.com/adafruit/CircuitPython/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for CircuitPython — Python-on-MCU substrate
```

**Body:**

```markdown
Hi @adafruit team,

Proposing a URML v0.1 capability-manifest mapping for CircuitPython over `adafruit/CircuitPython`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

CircuitPython runs on 400+ board variants spanning RP2040, SAMD21/51, nRF52, STM32, and ESP32. URML's `microbit_edu` manifest pattern (RFC-0018) implicitly covers CircuitPython-class boards, but the Python-on-MCU substrate is its own layer URML's manifest should declare explicitly. The natural URML integration shape is host-side: a Mu / Thonny / Code-with-Mu IDE-side bridge that emits validated URML primitives, with CircuitPython on the device dispatching them.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0174-adafruit-circuitpython-outreach.md

Questions worth `adafruit/CircuitPython` maintainer input on:

1. **Python-on-MCU substrate manifest fields.** Spec RFC queued (shared with MicroPython-on-MCU declarations). Manifest field expectations from the CircuitPython perspective?
2. **400+ board-variant identifier scheme.** Should URML's manifest use CircuitPython's existing board-id convention, or a separate URML identifier mapped to it?
3. **Drag-drop deploy-model declaration.** Useful manifest field for educational deployments?
4. **Library-ecosystem declaration.** Should URML's manifest declare which Adafruit_CircuitPython_* libraries are loaded?
5. **Adapter home.** URML repo (`reference/edu-runtime/CircuitPythonAdapter`), Adafruit-maintained `adafruit/circuitpython-urml-bridge`, or both?
6. **Conformance listing.** Would Adafruit consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0175: Raspberry Pi Pico SDK

**Post to:** https://github.com/raspberrypi/pico-sdk/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for RP2040 / RP2350 — dual-core MCU substrate
```

**Body:**

```markdown
Hi @raspberrypi team,

Proposing a URML v0.1 capability-manifest mapping for the RP2040 / RP2350 native SDK over `raspberrypi/pico-sdk`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

RP2040 / RP2350 are the rising default MCUs for hobbyist robotics, drone flight-controllers, and educational sensor platforms. The dual-core symmetric architecture (Cortex-M0+ on RP2040; Cortex-M33 + RISC-V on RP2350) is structurally distinct from single-core MCUs URML's existing micro:bit-class fixtures cover, and the RP-series PIO state machines are a distinguishing feature URML's manifest cannot today declare. Foundation-direct engagement complements URML's micro:bit-Foundation engagement at the higher-perf MCU class.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0175-raspberry-pi-pico-sdk-outreach.md

Questions worth `pico-sdk` maintainer input on:

1. **Dual-core declaration manifest fields.** Which core hosts which adapter functionality? Should URML's manifest declare per-core assignments?
2. **PIO state-machine declaration.** Manifest field for PIO availability + which state machines are reserved / committed?
3. **Heterogeneous-core declaration (RP2350).** Cortex-M33 vs RISC-V selection — manifest declaration shape?
4. **Native-SDK vs MicroPython manifest declaration.** Should URML's manifest distinguish the firmware-language substrate explicitly?
5. **Adapter home.** URML repo (`reference/edu-runtime/PiPicoAdapter`), Raspberry-Pi-maintained `raspberrypi/pico-urml-bridge`, or both?
6. **Conformance listing.** Would the Raspberry Pi Foundation consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0176: PlatformIO

**Post to:** https://github.com/platformio/platformio-core/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for PlatformIO — cross-board build-system substrate
```

**Body:**

```markdown
Hi @platformio team,

Proposing a URML v0.1 capability-manifest mapping for PlatformIO over `platformio/platformio-core`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

PlatformIO is the cross-board IDE / build pipeline spanning 900+ MCU board variants and 30+ MCU families. URML's manifest declares PlatformIO as the build-substrate the firmware artifact targets; PlatformIO's `platformio.ini` board-config maps to URML's hardware identifier with vendor-neutrality across the catalog. Structurally similar to how PlatformIO itself abstracts MCU diversity — URML's manifest is the substrate-neutral vocabulary above, PlatformIO is the substrate-neutral build pipeline below, with both sides making compatible bets on vendor-neutrality.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0176-platformio-outreach.md

Questions worth `platformio` maintainer input on:

1. **Build-system substrate manifest fields.** URML's v0.1 has no `build_system` block. Spec RFC queued. Manifest field expectations from PlatformIO's perspective (platformio.ini reflection, lib_deps declaration, board-id mapping convention)?
2. **900+ board-catalog identifier scheme.** Should URML's manifest use PlatformIO's board-id directly, or a separate URML identifier mapped to it?
3. **Build-time dependency-spec declaration.** Useful manifest field for downstream operators checking which libraries the firmware was built against?
4. **Adapter home.** URML repo (`reference/edu-runtime/PlatformIOAdapter`), PlatformIO-maintained `platformio/platformio-urml-bridge`, or both?
5. **Conformance listing.** Would PlatformIO consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### Foundation-direct RTOS / framework (2)

### RFC-0177: micro-ROS

**Post to:** https://github.com/micro-ROS/micro_ros_setup/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) extends to MCU edge via micro-ROS — the structural bridge
```

**Body:**

```markdown
Hi @micro-ROS team,

Proposing a URML v0.1 capability-manifest mapping for micro-ROS over `micro-ROS/micro_ros_setup`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

micro-ROS is the structural bridge URML's substrate story needs at the MCU edge. URML's existing `reference/ros2-runtime/` adapter composes with full ROS 2 on host-class robots; micro-ROS extends that surface down to MCU-class targets URML's `microbit_edu` fixture (RFC-0018) and the sibling Move-13 MCU + maker RFCs depend on. The natural composition: URML adapter speaks ROS 2 to a micro-ROS agent on the host, which transports messages to MCU-side ROS 2 nodes via DDS-XRCE — URML's typed primitive vocabulary dispatching onto firmware-class robots with the same adapter pattern URML uses for host-class robots.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0177-micro-ros-outreach.md

Questions worth `micro-ROS` maintainer input on:

1. **MCU-side ROS 2 substrate manifest fields.** URML's v0.1 has no `substrate.framework: micro_ros` declaration. Spec RFC queued. Manifest field expectations from the micro-ROS perspective?
2. **Multi-RTOS substrate declaration.** Should URML's manifest declare which RTOS (FreeRTOS / NuttX / Zephyr / bare-metal) hosts micro-ROS on the MCU?
3. **DDS-XRCE QoS class.** Manifest field expectations for resource-constrained QoS profiles?
4. **Host-side agent topology.** Should URML's manifest declare where the micro-ROS agent runs (companion-computer vs sidecar vs host-process)?
5. **Adapter home.** URML repo (`reference/edu-runtime/MicroRosAdapter` or `reference/micro-ros-runtime/`), micro-ROS-maintained `micro-ROS/micro_ros_urml_bridge`, or both?
6. **Conformance listing.** Would the micro-ROS maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0178: Zephyr Project

**Post to:** https://github.com/zephyrproject-rtos/zephyr/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for Zephyr — industrial-grade RTOS substrate
```

**Body:**

```markdown
Hi @zephyrproject-rtos team,

Proposing a URML v0.1 capability-manifest mapping for the Zephyr RTOS over `zephyrproject-rtos/zephyr`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

Zephyr is the industrial-grade RTOS substrate URML's manifest declares for MCU-class robots requiring real-time scheduling, multi-task workloads, or industrial certification posture. Zephyr pairs naturally with URML's sibling Move-13 micro-ROS engagement (Zephyr hosts the RTOS, micro-ROS hosts the ROS 2 messaging above it). The 700+ board catalog Zephyr supports gives URML's manifest a substantial substrate identifier scheme to map onto.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0178-zephyr-outreach.md

Questions worth `zephyrproject-rtos` maintainer input on:

1. **RTOS substrate manifest fields.** URML's v0.1 has no `substrate.rtos` declaration. Spec RFC queued. Manifest field expectations from the Zephyr perspective?
2. **Real-time scheduling-class declaration.** Manifest field for scheduler-class + tick-rate + priority-band declarations?
3. **TF-M secure-boot declaration.** Manifest field for industrial / safety posture (TF-M-enabled flag, secure-boot chain class)?
4. **700+ board-catalog identifier scheme.** Should URML's manifest use Zephyr's board-config identifier directly, or a separate URML identifier mapped to it?
5. **Adapter home.** URML repo (`reference/edu-runtime/ZephyrAdapter`), Zephyr-Foundation-maintained `zephyrproject-rtos/zephyr-urml-bridge`, or both?
6. **Conformance listing.** Would the Zephyr maintainers consider a README / wiki link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 5 research-collab / cross-citation targets

### RFC-0179: SimpleFOC

**Post to:** https://github.com/simplefoc/Arduino-FOC/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for SimpleFOC — community FOC library substrate
```

**Body:**

```markdown
Hi @simplefoc team,

Proposing a URML v0.1 capability-manifest mapping for SimpleFOC over `simplefoc/Arduino-FOC`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

SimpleFOC is the community FOC implementation library URML's manifest can declare for **maker / educational** brushless deployments where commercial controllers (ODrive, Moteus) are overspec'd or out of budget. URML's manifest declares the FOC-library substrate class + MCU host + driver IC + sensor class as a three-axis declaration; SimpleFOC's library-on-MCU shape is structurally different from vendor-direct hardware controllers, and the community-vs-vendor distinction is informative for downstream consumers.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0179-simplefoc-outreach.md

Questions worth `simplefoc` maintainer input on:

1. **FOC-library actuator-class manifest fields.** URML's v0.1 has no `foc_library` actuator class. Spec RFC queued. Manifest field expectations from the SimpleFOC perspective?
2. **MCU-host + driver-IC + sensor-class declaration.** Three-axis declaration — what granularity is useful?
3. **Community-vs-vendor library distinction.** Should URML's manifest declare this as a separate field, or implicit via the library identifier?
4. **Bridge home.** Cross-citation only (recommended), URML repo (`reference/actuator-runtime/SimpleFOCAdapter`), or community-maintained `simplefoc/Arduino-FOC-urml`?
5. **Conformance listing.** Would the simplefoc maintainers consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0180: VESC Project

**Post to:** https://github.com/vedderb/bldc/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for VESC — and a license-clarification ask
```

**Body:**

```markdown
Hi @vedderb,

Proposing a URML v0.1 capability-manifest cross-citation for the VESC Project over `vedderb/bldc`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

VESC is the open-source brushless ESC widely deployed in e-bikes, e-scooters, e-skateboards, and increasingly in robotics applications (mobile-base drive, hub motors, high-power applications where ODrive / Moteus are overspec'd or undersized). URML's manifest can declare VESC class controllers with their distinctive power-scalability — sub-kilowatt to multi-kilowatt — and protocol class (VESC-CAN, VESC-UART, VESC-USB). **License-clarification ask** is the gating fact: the repo's license is not visible via the GitHub SPDX API; an explicit declaration would clarify URML's adapter-grade reuse boundaries.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0180-vesc-bldc-outreach.md

Questions worth maintainer input on:

1. **License clarification.** Can `vedderb/bldc` get an explicit OSI license declaration (GPL-3.0 per LICENSE file; SPDX visibility upstream)?
2. **Actuator-controller substrate manifest fields.** Same shared question across the Move-13 motor-controller RFCs.
3. **Power-class declaration.** Should URML's manifest declare VESC's power-class (sub-kilowatt to multi-kilowatt)?
4. **Bridge home.** Cross-citation only (recommended pending license), URML repo (`reference/actuator-runtime/VescAdapter`), or VESC-maintained?
5. **Conformance listing.** Would the VESC project consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0181: Bitcraze Crazyflie

**Post to:** https://github.com/bitcraze/crazyflie-firmware/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for Crazyflie — research nano-quadcopter integration at the Apache-2.0 client boundary
```

**Body:**

```markdown
Hi @bitcraze team,

Proposing a URML v0.1 capability-manifest cross-citation for the Crazyflie nano-quadcopter platform over `bitcraze/crazyflie-firmware`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

URML's drone profile (RFC-0008) + multirotor mobility class compose naturally with Crazyflie's research-nano-quadcopter platform. **GPL-3.0 firmware = cross-citation framing**: URML's Apache-2.0 adapter pattern does not embed GPL-3.0 firmware; URML composes at the Apache-2.0 `crazyflie-lib-python` client boundary on the host side. The right integration shape is URML adapter → `crazyflie-lib-python` → Crazyradio dongle → swarm, with URML's manifest declaring the firmware-license boundary explicitly.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0181-bitcraze-crazyflie-outreach.md

Questions worth `bitcraze` maintainer input on:

1. **Nano-quadcopter payload-class manifest fields.** URML's `multirotor` class doesn't today distinguish nano (sub-100g research) from larger. Manifest field expectations?
2. **CRTP protocol substrate declaration.** Should URML's manifest declare CRTP as the integration substrate, and at what granularity (protocol version, channel/band, throughput class)?
3. **Firmware-license-boundary declaration.** Should URML's manifest declare the GPL-3.0-firmware / Apache-2.0-client license boundary explicitly?
4. **Crazyradio dongle declaration.** Manifest field for the host-side radio dependency?
5. **Bridge home.** URML repo (`reference/drone-runtime/CrazyflieAdapter`), Bitcraze-maintained `bitcraze/crazyflie-urml-bridge`, or external?
6. **Conformance listing.** Would Bitcraze consider a README link to URML's compatible-runtimes registry once a working bridge ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0182: STMicroelectronics STM32Cube

**Post to:** https://github.com/STMicroelectronics/STM32CubeF4/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) cross-citation for STM32Cube — mixed-license clarification ask + multi-series scope question
```

**Body:**

```markdown
Hi @STMicroelectronics team,

Proposing a URML v0.1 capability-manifest cross-citation for STM32Cube over `STMicroelectronics/STM32CubeF4`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

STM32 is one of the two most-deployed MCU families in robotics; URML's manifest declares STM32 board class spanning the F4 / H7 / U5 / G0 / G4 / WB / WL / WBA series. **Mixed-license posture is the gating fact**: ST's repos carry a mix of permissive (BSD-3-Clause, MIT, Apache-2.0) and proprietary-with-redistribution-license components. URML's adapter-grade reuse depends on per-surface clarity. **Multi-series scope is the second question**: this RFC anchors on STM32CubeF4 but the discussion likely belongs at a higher-level org surface if you have one.

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0182-stmicroelectronics-stm32cube-outreach.md

Questions worth `STMicroelectronics` maintainer input on:

1. **License clarification.** Can the STM32Cube repos get explicit per-surface SPDX declarations? Which subdirectories are BSD-3-Clause / MIT / Apache-2.0 vs proprietary-with-redistribution?
2. **MCU substrate manifest fields.** URML's v0.1 has no `mcu_class: stm32_*` enum entries. Spec RFC queued. Manifest field expectations from ST's perspective (series identifier, Cube version pin, middleware declarations)?
3. **Mixed-license-surface declaration.** Should URML's manifest declare per-component license boundaries explicitly?
4. **Multi-series scope.** Should URML engagement live per-series-repo (F4 / H7 / U5 etc.) or at a higher-level umbrella?
5. **Adapter home.** Cross-citation only (recommended pending license clarification), URML repo (`reference/edu-runtime/STM32CubeAdapter`), or ST-maintained?
6. **Conformance listing.** Would STMicroelectronics consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0183: TinyGo

**Post to:** https://github.com/tinygo-org/tinygo/discussions/new (Discussions enabled, preferred surface for design-discussion)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) capability-manifest mapping for TinyGo — Go-on-MCU firmware-language substrate
```

**Body:**

```markdown
Hi @tinygo-org team,

Proposing a URML v0.1 capability-manifest mapping for TinyGo over `tinygo-org/tinygo`. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent.

TinyGo brings the Go language to MCU substrates spanning RP2040, SAMD21/51, nRF52, STM32, AVR, and WebAssembly. URML's manifest declares which firmware-language substrate is loaded; TinyGo joins MicroPython, CircuitPython, native C/C++, and Arduino C++ in the substrate enum URML's sibling Move-13 MCU + maker RFCs populate. The 90+ TinyGo targets need an identifier-mapping convention in URML's manifest (similar to PlatformIO's 900+ board catalog).

This is **proposal-only**, posted as part of URML's Move #13 outreach (15 engageable RFCs in this wave).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0183-tinygo-outreach.md

Questions worth `tinygo-org` maintainer input on:

1. **Firmware-language substrate manifest fields.** URML's v0.1 has no `tinygo` firmware-language declaration. Spec RFC queued. Manifest field expectations from the TinyGo perspective?
2. **TinyGo-target catalog identifier scheme.** Should URML's manifest use TinyGo's target-id directly, or a separate URML identifier mapped to it?
3. **WebAssembly target scope.** Should URML's manifest declare WebAssembly as a valid TinyGo target (non-MCU substrate), and how does that compose with URML's robotics-class manifest assumptions?
4. **Adapter home.** URML repo (`reference/edu-runtime/TinyGoAdapter`), TinyGo-community-maintained `tinygo-org/tinygo-urml-bridge`, or external?
5. **Conformance listing.** Would the tinygo-org maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier C — none in this Move

Move-13 has 12 Tier C exclusions documented in [`move13-research-2026-05-28.md`](move13-research-2026-05-28.md) (PRC origin × 2 including Espressif Shanghai-HQ flag; no GitHub × 3; stale × 4; wrong layer/theme × 3). No posts.
