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

# urml-ardupilot-runtime

**ArduPilot / MAVLink reference runtime for URML.** Flies ArduCopter (a Pixhawk-class board running ArduPilot, or ArduCopter SITL) from a validated URML program over [pymavlink](https://github.com/ArduPilot/pymavlink). No ROS 2 dependency. This is the package [RFC-0041](../../docs/rfcs/0041-ardupilot-integration.md) proposed; Copter ships first, Plane and Rover are follow-ups.

`ArduCopterAdapter` subclasses the PX4 reference adapter ([urml-px4-runtime](../px4-runtime/)). The MAVLink command set is shared; what this package adds is the firmware behaviour ArduPilot needs around those commands and PX4 does not.

## What ArduPilot needs that PX4 does not

| Concern | PX4Adapter | ArduCopterAdapter |
|---|---|---|
| Flight mode | implicit | enters `GUIDED` before take-off and setpoints, confirms on heartbeat |
| Arming | implicit | `MAV_CMD_COMPONENT_ARM_DISARM`, waits for the armed flag; a refusal carries the autopilot's `PreArm:` text |
| `COMMAND_ACK` | first ack wins | matched on `ack.command` |
| `move_to` | send setpoint, return | send setpoint, wait for arrival within `arrival_radius_m` |
| `land` / `return_to_home` | `NAV_LAND` / `NAV_RTL` commands | `LAND` / `RTL` mode entry |
| Global positions | none | `SET_POSITION_TARGET_GLOBAL_INT` for locations bound to WGS84 in the config |
| `capture` | not supported | `DO_DIGICAM_CONTROL` or a servo pulse; result carries the autopilot position at trigger time |
| `set_output` | not supported | ArduPilot gripper (`DO_GRIPPER`), winch (`DO_WINCH`), or servo (`DO_SET_SERVO`) |
| Serial | URL only | `baud` appended to `COMn` / `/dev/tty*` URLs; `pyserial` in the extra |

Nothing in this package disables `ARMING_CHECK` or any pre-arm gate. On a bench with no GPS fix the autopilot refuses GUIDED or arming, and the adapter reports that refusal as the step's `reason` and stops. That refusal is the intended bench proof.

## Method coverage

| URML primitive | MAVLink | ArduCopter behaviour |
|---|---|---|
| `take_off` | `DO_SET_MODE(GUIDED)`, `COMPONENT_ARM_DISARM`, `NAV_TAKEOFF` | climbs; success when `GLOBAL_POSITION_INT.relative_alt` reaches 95 % of target |
| `move_to` (named, WGS84-bound) | `SET_POSITION_TARGET_GLOBAL_INT` | flies to lat/lon at relative altitude; optional `DO_SET_ROI_LOCATION` after arrival |
| `move_to` (named, NED-bound, or `pose`) | `SET_POSITION_TARGET_LOCAL_NED` | flies to local-NED offset from home |
| `hover` | mode confirm only | GUIDED holds position; a `hover` without `over` is a confirmed no-op |
| `land` | `DO_SET_MODE(LAND)` | waits for auto-disarm (bounded) |
| `return_to_home` | `DO_SET_MODE(RTL)` | clears any ROI first |
| `capture` (photo) | `DO_DIGICAM_CONTROL` or `DO_SET_SERVO` pulse | image stays on the camera; payload has `camera://shot/N` and the trigger-time position |
| `set_output` | `DO_GRIPPER` / `DO_WINCH` / `DO_SET_SERVO` | per `output_lines` binding in the config; winch uses relative-length control (+length deliver, -length retract) because ArduCopter 4.6 rejects the `WINCH_DELIVER` / `WINCH_RETRACT` actions |
| `measure` (distance, voltage), `wait_for`, `report`, `wait` | inherited from PX4Adapter | |
| `dock`, `grasp`, `release`, `detect`, `speak`, `listen`, video capture | not supported | documented `not_supported` result, never raised |

## Install

```bash
pip install -e reference/ardupilot-runtime[ardupilot]
```

The extra installs `pymavlink` and `pyserial`. Without it the module imports but constructing the adapter raises a clear install hint.

## Bring-up

Read-only probe. Sends no mode, arm, or motion command.

```bash
python -m urml_ardupilot_runtime.probe COM5
```

Prints the autopilot type, vehicle type, MAVLink system id, armed state, mode, firmware version, battery voltage, GPS fix, and any recent STATUSTEXT. A Pixhawk on USB is usually `COM<n>` on Windows and `/dev/ttyACM0` on Linux; ArduCopter SITL is `udp:127.0.0.1:14550`.

## Use

```bash
urml execute program.urml.yaml -m manifest.yaml --profile drone --no-policy \
    --adapter ardupilot --adapter-config ardupilot_adapter.yaml
```

A minimal `ardupilot_adapter.yaml`:

```yaml
connection_url: "COM5"
baud: 115200

location_to_pose:          # local metres from the launch point
  bench_north: { north: 5.0, east: 0.0, alt: 3.0 }
  home:        { north: 0.0, east: 0.0, alt: 0.0 }

location_to_global:        # WGS84, wins over location_to_pose for the same name
  site_p1: { lat: 32.0853, lon: 34.7818, alt_agl: 100.0, look_at: { lat: 32.0850, lon: 34.7815 } }

camera:
  kind: digicam            # or `servo` with `channel`

output_lines:
  payload_latch: { kind: gripper, instance: 1 }
  winch:         { kind: winch, instance: 1, deliver_length_m: 15.0, rate_m_s: 0.5 }
```

`location_to_global` is written by [`tools/scripts/geocode_locations.py`](../../tools/scripts/geocode_locations.py) at configuration time. The runtime never geocodes and never touches the network.

From Python:

```python
from urml_ardupilot_runtime import ArduCopterAdapter, load_ardupilot_config
from urml_ros2_runtime import URMLRuntime

with ArduCopterAdapter(load_ardupilot_config("ardupilot_adapter.yaml")) as adapter:
    runtime = URMLRuntime(adapter)
    result = runtime.execute(program, manifest, envelope, profiles=("drone",))
```

`CompositeAdapter` from the PX4 runtime accepts an `ArduCopterAdapter` as its `flight` backend unchanged.

## Tests

Three tiers, mirroring the PX4 runtime:

- `tests/test_arducopter_adapter.py`: hermetic, a fake `pymavlink` is injected; runs everywhere.
- `tests/integration/test_arducopter_live.py`: gated on `URML_ARDUPILOT_INTEGRATION=1`; real pymavlink, no autopilot contacted.
- `tests/integration/test_arducopter_bench.py`: gated on `URML_ARDUPILOT_BENCH=<port>`; a real board, props off. Asserts the identity probe, a successful battery read through the runtime, and that a take-off is refused cleanly by the autopilot's own pre-arm checks.
- `tests/integration/test_arducopter_sitl_e2e.py`: gated on `URML_ARDUPILOT_SITL=1`; flies the `drone/flight_only_positive` conformance fixture against ArduCopter SITL.

## Status

Bench link verified on hardware (Pixhawk, ArduCopter 4.6.3, USB). The SITL e2e (flight-only fixture plus both flight-test examples) is green against ArduCopter SITL built from `Copter-4.6.3`, run locally on 2026-08-29. No physical flight is claimed anywhere in this repository; see [`docs/demos/sentence-to-pixhawk.md`](../../docs/demos/sentence-to-pixhawk.md) for the bench runbook and the two flight-test runbooks that gate a field run on a green SITL pass.

## License

Apache 2.0. The adapter talks to ArduPilot firmware (GPLv3) over MAVLink; it links `pymavlink` (LGPLv3) as a normal Python import and never links the firmware.
