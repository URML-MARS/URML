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

# Move-13 research — open-source actuators + embedded / maker substrate (Theme C)

**Research date**: 2026-05-28.
**Audience**: founder review before Move-13 RFCs draft.
**Method**: two Explore agents in parallel covered actuator/motor-controller and embedded/maker categories, cross-checked each candidate against all prior ledgers (Moves 1-12), verified via `gh repo view` + `gh api orgs/...` for `isArchived: false`, license, recency, Issues, origin.
**Outcome**: 15 verified candidates (10 Tier A + 5 Tier B); 12 Tier C excluded with cause.

## Why this wave

URML's substrate-neutral claim composes from the top of the stack (NL layer, Move #11 Gemini Robotics SDK / smolagents) down to the **embedded edge** — motor controllers, MCU substrates, maker platforms. Move-13 engages Layer-0 of URML's substrate story: the actuator and embedded vocabularies URML's micro-class robot story (RFC-0018 `microbit_edu` pattern) depends on.

Founder picked Theme C ahead of Theme B (mobile manipulators + humanoids, queued for Move #14).

## Tier A (10) — vendor-direct or foundation-direct, adapter-eligible

### Motor controllers / actuators (3)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `odrive-robotics` | [odriverobotics/ODrive](https://github.com/odriverobotics/ODrive) | MIT | 3.6k | 2026-01-20 | US | Vendor-direct brushless motor controller (firmware + hardware). 4mo stale but flagship; ODrive Robotics commercial entity. Issues enabled. |
| `mjbots-moteus` | [mjbots/moteus](https://github.com/mjbots/moteus) | Apache-2.0 | 1.2k | 2026-05-25 | US | Vendor-direct brushless servo controller; mjbots Robotic Systems. Very active (3 days). Issues enabled. |
| `trinamic-tmc-api` | [Trinamic/TMC-API](https://github.com/Trinamic/TMC-API) | MIT | 260 | 2026-04-07 | DE (Hamburg) | Vendor-direct stepper-motor driver C-API; Trinamic Motion Control (Analog Devices subsidiary). Active. |

### MCU + maker platforms (5)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `microbit-foundation` | [microbit-foundation/micropython-microbit-v2](https://github.com/microbit-foundation/micropython-microbit-v2) | MIT | 56 | 2024-09-18 | UK | Vendor-foundation-direct MicroPython for BBC micro:bit v2. Direct match to URML's existing `microbit_edu` manifest fixture (RFC-0018). |
| `arduino` | [arduino/Arduino](https://github.com/arduino/Arduino) | Other (license-clarification ask) | 14.6k | 2025-10-11 | IT | Vendor-direct Arduino IDE. License listed as "Other" — clarification needed for adapter-grade bundling. |
| `adafruit-circuitpython` | [adafruit/CircuitPython](https://github.com/adafruit/CircuitPython) | Other (MIT-compatible) | 4.5k | 2026-05-27 | US (NY) | Vendor-direct Python on MCU. Daily activity. Discussions enabled. |
| `raspberry-pi-pico-sdk` | [raspberrypi/pico-sdk](https://github.com/raspberrypi/pico-sdk) | BSD-3-Clause | 4.8k | 2026-05-28 | UK | Vendor-direct RP2040 / RP2350 SDK. Daily activity. |
| `platformio` | [platformio/platformio-core](https://github.com/platformio/platformio-core) | Apache-2.0 | 9.3k | 2026-04-21 | UA | Vendor-direct IDE/build layer spanning 900+ boards. |

### Foundation-direct RTOS / framework (2)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `micro-ros` | [micro-ROS/micro_ros_setup](https://github.com/micro-ROS/micro_ros_setup) | Apache-2.0 | 493 | 2026-05-27 | Multi (Linux Foundation) | Foundation-direct ROS 2 on MCU. URML's natural language-substrate bridge to embedded. |
| `zephyr` | [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr) | Apache-2.0 | 15.4k | 2026-05-28 | Multi (Linux Foundation) | Foundation-direct industrial-grade RTOS. Daily activity. |

## Tier B (5) — research-collab / cross-citation framing

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `simplefoc` | [simplefoc/Arduino-FOC](https://github.com/simplefoc/Arduino-FOC) | MIT | 2.8k | 2026-05-22 | Community | FOC motor-control library; community-maintained, vendor-neutral. Active. Issues + Discussions. |
| `vesc-bldc` | [vedderb/bldc](https://github.com/vedderb/bldc) | TBD (license-clarification ask) | 3.2k | 2026-05-28 | SE (Benjamin Vedder) | Open-source BLDC ESC; daily activity. License clarification on the repo level needed. |
| `bitcraze-crazyflie` | [bitcraze/crazyflie-firmware](https://github.com/bitcraze/crazyflie-firmware) | GPL-3.0 | 1.5k | 2026-05-26 | SE | Vendor-direct nano-quadcopter firmware. GPL-3.0 limits Apache-2.0 bundling — cross-citation framing. |
| `stm-stm32cube` | [STMicroelectronics/STM32CubeF4](https://github.com/STMicroelectronics/STM32CubeF4) | Other (mixed) | 1.2k | 2026-05-26 | CH (HQ Geneva) | Vendor-direct MCU HAL/middleware. Mixed-license posture; cross-citation appropriate. |
| `tinygo` | [tinygo-org/tinygo](https://github.com/tinygo-org/tinygo) | Apache-2.0 | 17.5k | 2026-05-28 | Community | Go compiler for MCU. Foundation-style maintenance; massive star count signals community gravity. |

## Tier C — excluded with cause (recorded so the negative space is auditable)

| Slug | Repo | Cause |
|---|---|---|
| `espressif-esp-idf` | espressif/esp-idf | **Shanghai HQ origin** despite US-listing + Apache-2.0 license. NDAA Section 889 flag for operator decision; URML's default policy excludes by default. Massive 18k-star surface noted; operator can override. |
| `t-motor` | T-Motor catalogue | **PRC origin**. NDAA Section 889. |
| `myactuator` | MyActuator | No verified GitHub surface found. Vendor exists but no engagement surface. |
| `odri` | open-dynamic-robot-initiative/open_robot_actuator_hardware | **Stale >3.8 years** (last push 2022-09-06). Cross-citation only. |
| `franka-robotics` | frankarobotics/franka_ros2 | **Wrong layer** (cobot OEM, not actuator vendor). Deferred to Move #14 Theme B (mobile manipulators + humanoids). |
| `ros2-controls` | ros-controls/ros2_control | **Wrong theme** (substrate framework, Theme A scope). Deferred to a future substrate-spine Move. |
| `ti-instaspin` | TI InstaSPIN | No active public OSI-permissive repo. |
| `adi-motor-refs` | Analog Devices motor refs | No current OSI-permissive repo. |
| `nordic-semiconductor` | NordicSemiconductor/* | Active repos found stale (2+ years); flagship MCU SDKs not in active OSS repos. |
| `sparkfun` | sparkfun/* | Distributor-tier (component libraries / Eagle), no platform-tier repo. |
| `arm-mbed` | ARMmbed/mbed-os | Stale (~7 months from cutoff); approaching dormant. |
| `tessel` | tessel/t2-firmware | Dormant >7 years; effectively retired. |

## Distribution

| Category | Tier A | Tier B | Excluded |
|---|---|---|---|
| Motor controllers / actuators | 3 (ODrive, Moteus, Trinamic) | 2 (SimpleFOC, VESC) | 5 (ODRI stale, MyActuator no repo, T-Motor PRC, TI no repo, ADI no repo) |
| MCU + maker platforms | 5 (micro:bit, Arduino, Adafruit, Pi Pico, PlatformIO) | 2 (STM, TinyGo) | 4 (Espressif Shanghai-flagged, Nordic stale, SparkFun no platform repo, ARM Mbed stale) |
| Foundation RTOS / framework | 2 (micro-ROS, Zephyr) | 0 | 2 (Franka wrong layer, ROS-controls wrong theme) |
| Aerial / nano-drone | 0 | 1 (Bitcraze Crazyflie GPL-3.0) | 0 |
| Total | **10** | **5** | **12** |

## Reserved RFC range

RFCs 0169-0183 reserved for Move #13 in `docs/rfcs/README.md`. Move-12 ends at RFC-0168 (16 RFCs across 0153-0168 per the in-progress outreach-move12.yaml).

## Open license-clarification asks

Three Tier-row license-clarification asks to surface in per-RFC unresolved questions:

- `arduino/Arduino`: license listed as "Other" — request explicit OSI declaration (LGPL / GPL clarification).
- `vedderb/bldc` (VESC): no SPDX visible — request explicit declaration.
- `STMicroelectronics/STM32CubeF4`: mixed license posture — request adapter-grade-OSS surface declaration.

## Espressif operator-decision flag

**`espressif/esp-idf` is one of the most-deployed MCU SDKs in the world** (18k stars, daily commits, Apache-2.0). Origin is Shanghai PRC despite Espressif Systems' US NASDAQ listing. URML's default policy (NDAA Section 889) excludes PRC-domiciled vendors. The operator-decision flag is recorded honestly in this audit so a downstream URML deployment that already depends on ESP32 hardware can make its own determination. URML's Move-13 outreach does NOT include Espressif by default.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move13.yaml` + `posts-move13.md` skeleton + README index update.
3. Subsequent sessions: draft RFCs 0169-0183 one per session (Move-10 batch shape: 5-6 RFCs per PR).
4. Posting follows Move-10/11 pattern: founder review of bodies, then assistant posts via `gh` with explicit "go" authorization.
