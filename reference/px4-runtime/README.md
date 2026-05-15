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

The not-applicable primitives — `dock`, `grasp`, `release`, `detect`, `capture`, `speak`, `listen` — return `NavigationResult(success=False, reason="not_supported_on_bare_autopilot: ...")` rather than raising. Real drone deployments typically pair a PX4 autopilot with a ROS 2 companion computer for perception / manipulation / speech; in those stacks, dispatch through a composite adapter (a near-term follow-up).

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

**Follow-ups (not in v0.1):**
- PX4 SITL integration tests in a gated Linux workflow (matches the ROS 2 runtime's pattern).
- Composite adapter for stacks that pair PX4 with ROS 2 perception.
- Full geofence polygon-containment math in the safety-envelope pass.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/profiles/drone/`](../../spec/profiles/drone/) — the profile this runtime targets.
- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema, including drone-specific fields.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
- [`/reference/ros2-runtime/INTEGRATION.md`](../ros2-runtime/INTEGRATION.md) — the ROS 2 runtime's parallel design notes.
- [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
