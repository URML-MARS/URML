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

# urml-px4-runtime

**PX4 / MAVLink reference runtime for URML** — the second reference substrate, after [urml-ros2-runtime](../ros2-runtime/). Proves URML's substrate-neutrality concretely: this adapter has **no ROS 2 dependency**. It talks MAVLink directly via [pymavlink](https://github.com/ArduPilot/pymavlink) to a PX4 autopilot (real hardware, or PX4 SITL simulator).

A single reference runtime — no matter how clean — risks the spec accidentally encoding substrate assumptions. A second runtime on an entirely different stack (no rclpy, no Nav2, no ROS topics, just MAVLink frames over UDP/serial) keeps the spec honest. The two reference runtimes share the same `ROSAdapter` Protocol (the "ROS" in the name is vestigial — the Protocol is substrate-neutral) and pass the same conformance fixtures via the `ConformanceRunner.adapter_factory` hook.

## Method coverage

Full `ROSAdapter` Protocol (12 core methods + 3 drone-profile methods), wired against MAVLink commands. A flight primitive succeeds only when PX4's telemetry shows it happened; a `COMMAND_ACK` alone is never reported as success (see [Flight completion](#flight-completion)).

| URML primitive | MAVLink mapping | Done when |
|---|---|---|
| `take_off` | `MAV_CMD_COMPONENT_ARM_DISARM` if disarmed, then `MAV_CMD_NAV_TAKEOFF` (altitude AMSL) | armed bit on `HEARTBEAT`, then `GLOBAL_POSITION_INT.relative_alt` within tolerance of the target |
| `move_to` | `MAV_CMD_DO_REPOSITION` as `COMMAND_INT` (lat / lon in degE7) | inside `arrival_radius_m` and `arrival_alt_tolerance_m` of the target |
| `hover` over a place | same as `move_to`; PX4 then holds in Hold mode | as `move_to` |
| `return_to_home` | `MAV_CMD_NAV_RETURN_TO_LAUNCH` | inside `arrival_radius_m` of home, in the air or landed |
| `land` | `MAV_CMD_NAV_LAND` (none if already on the ground) | `EXTENDED_SYS_STATE.landed_state` is ON_GROUND |
| `wait` | timed sleep (PX4 holds position in Hold mode) | |
| `wait_for` `emergency_stop` | the autopilot's `HEARTBEAT.system_status` | `MAV_STATE_FLIGHT_TERMINATION` or `MAV_STATE_EMERGENCY` from the autopilot itself; otherwise a timeout |
| `wait_for` battery `sensor_threshold` | `BATTERY_STATUS` | a sample that meets the threshold; samples that do not are skipped until the timeout |
| `measure` | sensor telemetry stream (`DISTANCE_SENSOR`, `BATTERY_STATUS`, etc.) | |
| `report` | `STATUSTEXT` MAVLink message | |

The not-applicable primitives (`dock`, `grasp`, `release`, `detect`, `scan`, `capture`, `speak`, `listen`) return a result with `success=False` and `reason="not_supported_on_bare_autopilot: ..."` rather than raising. A scan is waypoints plus a capture at each one, and a bare autopilot has no camera to capture with, so `scan` does not report success. Real drone deployments pair a PX4 autopilot with a ROS 2 companion computer for perception / manipulation / speech; in those stacks, dispatch through `CompositeAdapter` (below) instead of `PX4Adapter` alone.

PX4 v1.17 reports `MAV_STATE_FLIGHT_TERMINATION` for a terminated flight, an engaged kill switch, and the motor lockdown that holds a throw launch (`COM_THROW_EN`, off by default). It does not send `MAV_STATE_EMERGENCY`; the adapter accepts it for autopilots that do. A heartbeat from a ground station or another vehicle never counts.

## Flight completion

Each flight primitive sends its command, then reads telemetry until the action is complete or a timeout expires. A refusal or a timeout is returned as `success=False` with a reason; nothing is raised.

- **take_off** arms the vehicle if it is disarmed and confirms the armed bit, re-reads home (PX4 moves home to the vehicle when it arms), and sends `MAV_CMD_NAV_TAKEOFF` with param 7 = home altitude + the requested height, because PX4 reads that parameter as AMSL. Latitude, longitude and yaw are sent as NaN, which PX4 reads as "here, current heading". The step succeeds when `relative_alt` is within `arrival_alt_tolerance_m` of the target (capped at half the target, so a low take-off still has to leave the ground). If PX4 refuses the take-off after this adapter armed it, the adapter disarms it again. `climb_rate` has no MAVLink take-off parameter; PX4 climbs at its `MPC_TKO_SPEED`.
- **move_to** resolves a location through `location_to_pose` (or takes `pose` x = north, y = east, z = metres above home), converts that offset from home to WGS84 with the projection PX4 uses, and sends `MAV_CMD_DO_REPOSITION` as `COMMAND_INT` with the change-mode flag PX4 requires. A pose without `z` keeps the current altitude. PX4 executes a reposition only while armed, so a disarmed vehicle fails at once with `not_airborne`.
- **return_to_home** succeeds when the vehicle is within `arrival_radius_m` of home. PX4's own RTL then descends and lands. On the ground at home it reports `already_at_home` without commanding anything.
- **land** reports `already_on_ground` (success, no command) when PX4 already says ON_GROUND, for example after an RTL that landed by itself. `land(at=...)` flies to that location at the current altitude first. `precision` is not mapped; PX4 lands the way it is configured to.

Refusal and timeout reasons carry PX4's `MAV_RESULT` or what telemetry last showed, followed by the warnings PX4 sent about it as `STATUSTEXT` (severity WARNING or worse; PX4's INFO lines such as "Takeoff detected" narrate and stay out). For example, a take-off requested before PX4 v1.17 SITL had passed its pre-arm checks returned:

```
arm_rejected: mav_result_temporarily_rejected; PX4 said: "Arming denied: Resolve system health failures first"
```

A reason quotes only what PX4 sent from the command on. After a refusal the adapter listens for up to a second, because PX4 can send its explanation just after the `COMMAND_ACK`, and it joins texts PX4 splits into 50-character chunks. PX4 names a failing pre-arm check ("Preflight Fail: ...") when the check starts failing, which can be before the arm command; the adapter reads that text but leaves it out of the reason, because it cannot tell whether an older warning still holds.

The adapter talks to PX4 only: it refuses an autopilot whose heartbeat is not `MAV_AUTOPILOT_PX4`, because ArduPilot reads the same take-off parameter as a relative altitude. Use `ArduCopterAdapter` for ArduPilot.

### Ground-station heartbeat and PX4's data-link-loss failsafe

PX4 sends `STATUSTEXT` only on links where it sees a ground-station heartbeat. So from the moment it connects until `close()`, the adapter sends a `MAV_TYPE_GCS` heartbeat once a second from a daemon thread. Every send on the connection (the heartbeat, commands, `report`) takes one lock, because pymavlink sends are not thread-safe. `close()` stops the thread before it closes the connection, and a closed adapter does not reconnect. An adapter that is garbage-collected without `close()` stops its heartbeat too.

This makes URML a ground station in PX4's eyes, with a consequence to plan for. If URML stops mid-flight (the program ends, `close()` runs, the process dies, the link drops), the heartbeat stops, and after `COM_DL_LOSS_T` seconds (10 by default) PX4 logs "Connection to ground station lost" and applies its data-link-loss action, `NAV_DLL_ACT`:

- PX4 ships with `NAV_DLL_ACT = 0`: no action. The vehicle carries on with what it was doing, for example holding position.
- An operator who wants the vehicle to return or land when its controller dies sets `NAV_DLL_ACT` (2 = Return, 3 = Land). That is the intended behavior, not a side effect to suppress.
- `COM_DLL_EXCEPT` exempts modes from the action. Its Hold bit (1) also covers take-off, and `take_off` and `move_to` leave the vehicle in Hold, so leave that bit clear if you want the action while URML flies.
- With `NAV_DLL_ACT` set, PX4 also refuses to arm while no ground station is connected. The adapter's heartbeat counts as one.

### Flight settings

These live in `px4_adapter.yaml` next to `connection_url` and `location_to_pose`. Every value must be positive.

| Key | Default | Meaning |
|---|---|---|
| `arm_timeout_seconds` | 10 | Wait for the armed bit after PX4 accepts the arm command. |
| `takeoff_timeout_seconds` | 120 | Climb time allowed. PX4 climbs at 1.5 m/s by default, so this covers a 120 m take-off. |
| `arrival_radius_m` | 1.5 | Horizontal distance that counts as arrived (move_to, hover, return_to_home). |
| `arrival_alt_tolerance_m` | 1.0 | Altitude difference that counts as arrived (take_off, move_to). |
| `arrival_timeout_seconds` | 120 | Time allowed to reach a target or home. Raise it for long legs; PX4 cruises at 5 m/s by default. |
| `land_timeout_seconds` | 180 | Time allowed from the land command to ON_GROUND. |
| `ack_timeout_seconds` | 5 | Wait for a `COMMAND_ACK`. |
| `heartbeat_timeout_seconds` | 5 | Wait for PX4's heartbeat when connecting. |
| `message_timeout_seconds` | 5 | Wait for a telemetry message the adapter needs (home, position, landed state). |

`relative_alt` comes from PX4 and moves with PX4's home altitude. PX4 v1.17 corrects home altitude against GNSS in flight; in SIH simulation that made `relative_alt` wander by about a metre around a steady hover. The arrival checks need one telemetry sample inside the band, which was enough in the SITL runs so far, and this wander is why the altitude band is not tighter.

## CompositeAdapter — PX4 flight + ROS 2 companion

`CompositeAdapter` implements the full `ROSAdapter` Protocol by holding two backing adapters and routing each method to whichever one owns that capability. The URML program, manifest, and validator are unchanged and unaware — the split lives entirely at the deployment boundary.

```python
from urml_px4_runtime import CompositeAdapter, PX4Adapter, PX4AdapterConfig
from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter
from urml_ros2_runtime.substrate.adapter_config import load_adapter_config

flight = PX4Adapter(PX4AdapterConfig(connection_url="udp:127.0.0.1:14540"))
companion = RclpyAdapter(load_adapter_config("adapter.yaml"))

with CompositeAdapter(flight=flight, companion=companion) as adapter:
    # take_off/land/RTH/move_to -> PX4 (MAVLink); detect/grasp/capture/
    # speak -> ROS 2 companion. One URML program, two substrates.
    runtime = URMLRuntime(adapter)
    runtime.execute(program, manifest, envelope, profiles=("drone",))
```

Default routing (the drone-stack policy) sends flight primitives (`take_off`, `land`, `return_to_home`, `move_to`/`hover`, `wait`) to the flight adapter and perception/manipulation/speech (`detect`, `grasp`, `release`, `scan`, `measure`, `capture`, `report`, `speak`, `listen`, `wait_for`) to the companion. It is explicit and overridable per method:

```python
# This airframe reads its rangefinder over MAVLink, not the companion:
CompositeAdapter(flight=flight, companion=companion,
                 routing={"take_measurement": "flight"})
```

Unknown method names or backend values other than `flight`/`companion` are rejected at construction, so a routing typo can't silently send a goal to the wrong box. `CompositeAdapter` imports neither pymavlink nor rclpy — it depends only on the substrate-neutral Protocol, loads on every host, and is hermetically unit-tested against two mock backends (24 tests).

## Install

```bash
pip install -e reference/px4-runtime[px4]
```

The `[px4]` extra installs `pymavlink` — a normal PyPI package, unlike `rclpy` which ships with the ROS 2 distribution.

## Use

```python
from urml_px4_runtime import PX4Adapter, PX4AdapterConfig

config = PX4AdapterConfig(
    connection_url="udp:127.0.0.1:14540",  # PX4 SITL's offboard (API) port
)
with PX4Adapter(config) as adapter:
    result = adapter.send_takeoff_goal(altitude=30.0)  # arms, climbs, returns at 30 m
    print(result.success, result.reason)
```

Drop the adapter into the URML runtime:

```python
from urml_ros2_runtime import URMLRuntime
runtime = URMLRuntime(adapter)
runtime.execute(program, manifest, envelope, profiles=("drone",))
```

Or through the conformance suite:

```python
from urml_conformance import ConformanceRunner
runner = ConformanceRunner(adapter_factory=lambda: PX4Adapter(config))
report = runner.run()
```

## Status

**v0.1 (this release):**
- Adapter loads on every host (lazy pymavlink import; clear actionable error if `pymavlink` is missing).
- Unit tests with a scripted fake PX4 cover all 15 Protocol methods (including the not-applicable ones). The fake arms, climbs, repositions and lands on a simulated clock, so each flight primitive's success and failure paths (arm refused, take-off timeout, reposition never arriving, landing timeout) are tested against vehicle state, not against acks. Like PX4, the fake sends STATUSTEXT only after it has seen a ground-station heartbeat, so a test reason that quotes PX4 shows the adapter's heartbeat reached it; other tests check the heartbeat thread's period, that it stops on `close()`, and that every send holds the send lock.
- Live PX4 SITL e2e test flies the `drone/flight_only_positive` conformance fixture through `ConformanceRunner` with a real `PX4Adapter` (`tests/integration/test_px4_sitl_e2e.py`, gated by `URML_PX4_SITL=1`). A listen-only witness on PX4's ground-station port checks that the vehicle armed, climbed to at least 90 percent of the take-off altitude, came within twice the acceptance radius of the waypoint, and ended on the ground.

**Verified in simulation (2026-09-27):** the e2e test passed locally in WSL2 against PX4 v1.17.0 SITL (SIH quadrotor), and PX4's own log shows the arm, the take-off, the return to launch, the landing and the disarm; the witness measured a highest relative altitude of 31.79 m for the 30 m take-off and a closest approach of 0.92 m to the waypoint. The record is [`tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md`](tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md). An earlier version of the same test also passed, in 2.37 s, while the adapter counted acks as success and the simulated vehicle never armed; that result does not count as a flight. The CI job has not run.

**With the ground-station heartbeat (2026-09-27):** the same test passed again with the heartbeat running (a highest relative altitude of 31.778 m, a closest approach of 0.95 m), PX4 sent its STATUSTEXT to the adapter's link during the flight, and PX4 logged "Connection to ground station lost" after the adapter closed. A no-flight probe got `arm_rejected: mav_result_temporarily_rejected; PX4 said: "Arming denied: Resolve system health failures first"` from a take-off requested before PX4 was ready, saw `wait_for(emergency_stop)` time out on a healthy vehicle, and saw it fire on `MAV_STATE_FLIGHT_TERMINATION` after a flight termination commanded on the ground. The record is [`tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih-heartbeat.md`](tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih-heartbeat.md).

**Landed since v0.1:**
- `CompositeAdapter` for stacks that pair PX4 with a ROS 2 companion (see above).
- Geofence polygon-containment, 3D altitude bands, and people-occupancy zones in the safety-envelope pass (validator Pass 3).
- Gated `.github/workflows/px4-integration.yml` with three jobs: `px4-smoke` (real pymavlink, no SITL — the `rclpy-smoke` analog), `px4-sitl-e2e` (the flight e2e — the `gazebo-e2e` analog), and `px4-arm64-build` (the hermetic suite under linux/arm64 QEMU emulation — the pre-hardware Jetson-class signal).

**Follow-ups (not yet):**
- First run of `px4-sitl-e2e` on a Linux runner. The job follows the local recipe (PX4 v1.17.0 cloned shallow and recursive, PX4's Python requirements in a venv, the build-only `make px4_sitl_default`, then `sleep infinity | HEADLESS=1 make px4_sitl sihsim_quadx`), but it has not run yet.
- Real Jetson + real-robot hardware-in-the-loop. QEMU emulation is a faithful proxy for our pure-Python + pymavlink code, not a hardware-verification claim.
- A fly-and-capture `scan` (waypoint expansion and a capture at each waypoint) for an autopilot with a camera. Until then `scan` returns not-supported on a bare autopilot, and `CompositeAdapter` routes it to the companion.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/profiles/drone/`](../../spec/profiles/drone/) — the profile this runtime targets.
- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema, including drone-specific fields.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
- [`/reference/ros2-runtime/INTEGRATION.md`](../ros2-runtime/INTEGRATION.md) — the ROS 2 runtime's parallel design notes.
- [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
