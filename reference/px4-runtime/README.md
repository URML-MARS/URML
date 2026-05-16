# urml-px4-runtime

**PX4 / MAVLink reference runtime for URML** — the second reference substrate, after [urml-ros2-runtime](../ros2-runtime/). Proves URML's substrate-neutrality concretely: this adapter has **no ROS 2 dependency**. It talks MAVLink directly via [pymavlink](https://github.com/ArduPilot/pymavlink) to a PX4 autopilot (real hardware, or PX4 SITL simulator).

A single reference runtime — no matter how clean — risks the spec accidentally encoding substrate assumptions. A second runtime on an entirely different stack (no rclpy, no Nav2, no ROS topics, just MAVLink frames over UDP/serial) keeps the spec honest. The two reference runtimes share the same `ROSAdapter` Protocol (the "ROS" in the name is vestigial — the Protocol is substrate-neutral) and pass the same conformance fixtures via the `ConformanceRunner.adapter_factory` hook.

## Method coverage

Full `ROSAdapter` Protocol (12 core methods + 3 drone-profile methods), wired against MAVLink commands:

| URML primitive | MAVLink mapping |
|---|---|
| `take_off` | `MAV_CMD_NAV_TAKEOFF` |
| `land` | `MAV_CMD_NAV_LAND` |
| `return_to_home` | `MAV_CMD_NAV_RETURN_TO_LAUNCH` |
| `move_to` | `SET_POSITION_TARGET_LOCAL_NED` (offboard mode) |
| `hover` | `SET_POSITION_TARGET_LOCAL_NED` with zero velocity |
| `wait` | timed sleep |
| `wait_for` | MAVLink message-stream subscribe-once with predicate |
| `measure` | sensor telemetry stream (`DISTANCE_SENSOR`, `BATTERY_STATUS`, etc.) |
| `report` | `STATUSTEXT` MAVLink message |
| `scan` | stub success (full waypoint expansion is a follow-up) |

The not-applicable primitives — `dock`, `grasp`, `release`, `detect`, `capture`, `speak`, `listen` — return `NavigationResult(success=False, reason="not_supported_on_bare_autopilot: ...")` rather than raising. Real drone deployments pair a PX4 autopilot with a ROS 2 companion computer for perception / manipulation / speech; in those stacks, dispatch through `CompositeAdapter` (below) instead of `PX4Adapter` alone.

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
    connection_url="udp:127.0.0.1:14550",  # PX4 SITL default
    system_id=1,
    component_id=1,
)
with PX4Adapter(config) as adapter:
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success
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
- Unit tests with mocked pymavlink cover all 15 Protocol methods (including the not-applicable ones).
- Integration testing against a live PX4 SITL is a documented follow-up; the test scaffold lives in `tests/integration/`.

**Landed since v0.1:**
- `CompositeAdapter` for stacks that pair PX4 with a ROS 2 companion (see above).
- Geofence polygon-containment, 3D altitude bands, and people-occupancy zones in the safety-envelope pass (validator Pass 3).

**Follow-ups (not yet):**
- PX4 SITL integration tests in a gated Linux workflow (matches the ROS 2 runtime's pattern).
- True fly-and-capture `scan` (waypoint expansion + per-waypoint trigger) instead of the stub.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/profiles/drone/`](../../spec/profiles/drone/) — the profile this runtime targets.
- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema, including drone-specific fields.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
- [`/reference/ros2-runtime/INTEGRATION.md`](../ros2-runtime/INTEGRATION.md) — the ROS 2 runtime's parallel design notes.
- [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
