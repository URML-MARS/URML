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

# urml-marine-runtime

**Underwater-vehicle reference runtime for URML** — `BlueRovAdapter` for **BlueROV2 / ArduSub**, via MAVLink.

ArduSub speaks MAVLink exactly like PX4, so this adapter mirrors `PX4Adapter`: lazy `pymavlink`, **no ROS 2 dependency**, a lazily-opened cached connection, failures returned not raised. It is the underwater analog of the PX4 no-ROS proof, and it activates the `underwater_thrusters` `mobility.drive_type` that already exists in the v0.1 manifest schema (so **no RFC is needed** — unlike legged/biped, which needed RFC-0009).

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | `SET_POSITION_TARGET_LOCAL_NED` to a configured waypoint (location → north/east/depth) |
| `wait` | timed hold |
| `measure` | `SCALED_PRESSURE` (depth) / `BATTERY_STATUS` telemetry |
| `wait_for` | MAVLink message subscribe-once with predicate |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** (mirrors `PX4Adapter.run_scan`) |

`grasp`/`release`, `dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_on_bare_rov` (a manipulator/perception payload pairs via a companion). The drone trio `take_off`/`land`/`return_to_home` return `not_applicable_underwater` — honest: a submersible does not take off or land.

## Install / use

```bash
pip install -e reference/marine-runtime[marine]   # installs pymavlink
```

```python
from urml_marine_runtime import BlueRovAdapter, MarineConfig
with BlueRovAdapter(MarineConfig(connection_url="udp:127.0.0.1:14550")) as rov:
    assert rov.send_navigation_goal(pose={"north": 5.0, "east": 0.0, "depth": 3.0}).success
```

## Status

**v0.1 (this release):**
- `BlueRovAdapter` + `MarineConfig` (MAVLink, no ROS). `bluerov_marine` manifest exercises `drive_type: underwater_thrusters`; `conformance/fixtures/marine/` survey fixture verified through the runner.
- Hermetic unit tests: navigation (configured + unmapped), measure, scan-stub, lifecycle, the not-supported / not-applicable-underwater sentinels, the missing-`[marine]`-extra error, the conformance hook — no pymavlink install required.
- Gated `.github/workflows/marine-integration.yml`: `marine-smoke` (real pymavlink), `marine-arm64-build` (the Jetson-class QEMU signal), and `marine-sitl-e2e` against ArduSub SITL (first run is a calibration run by design — the established px4/ros2 convention).

**Follow-ups (not yet):**
- Manipulator-payload companion (BlueROV + arm) wiring; true survey-pattern `scan` instead of the stub.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/reference/px4-runtime/`](../px4-runtime/) — the MAVLink sibling whose structure this mirrors.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
