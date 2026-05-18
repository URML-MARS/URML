# urml-legged-runtime

**Legged/quadruped reference runtime for URML** — first-class adapters for **Boston Dynamics Spot** and **ANYbotics ANYmal**.

Two vendors, two substrates, the same `ROSAdapter` Protocol:

- **`SpotAdapter`** talks the Boston Dynamics `bosdyn` gRPC SDK directly. **No ROS 2 dependency** — like `PX4Adapter` for MAVLink, it is a second proof that URML's spec carries no ROS assumptions. Spot's own companion computer is commonly a Jetson, so the offline, Jetson-class deployment story is native here.
- **`AnymalAdapter`** speaks ROS 2, so it composes the ROS 2 runtime's `RclpyAdapter` — the same single-sourced-substrate pattern the industrial-arm runtime uses. No duplicated ROS 2 plumbing.

## Method coverage

**SpotAdapter** (bosdyn):

| URML primitive | Mapping |
|---|---|
| `move_to` / `hover` | GraphNav navigate-to (location → waypoint via `SpotConfig`) |
| `dock` | `bosdyn.client.docking` blocking dock |
| `wait` | held stand command |
| `measure` | robot-state telemetry (battery / e-stop) — *partial* |
| `wait_for` | robot-state poll — *partial* |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** (waypoint expansion is a follow-up) |

Not supported on a bare Spot — `grasp`/`release` (needs the Spot Arm SDK), `detect`, `capture`, `speak`, `listen`, and the drone trio — return `not_supported_on_spot: ...` (returned, not raised).

**AnymalAdapter** (composes `RclpyAdapter`): `move_to`/`hover`, `wait`, `measure`, `wait_for`, `report` delegate to the ROS 2 substrate. `grasp`/`release` (no arm), `dock`, `detect`, `scan`, `capture`, `speak`, `listen`, and the drone trio return `not_supported_on_quadruped[anymal]: ...`. A payload-equipped ANYmal pairs with a companion adapter, exactly as the drone stack pairs flight with a ROS 2 companion.

## Install

```bash
pip install -e reference/legged-runtime          # AnymalAdapter (needs a sourced ROS 2 env to construct)
pip install -e reference/legged-runtime[spot]    # + SpotAdapter (bosdyn wheels)
```

`bosdyn` and `rclpy` are imported lazily, so the package imports on every host; constructing an adapter needs that vendor's runtime.

## Use

```python
from urml_legged_runtime import SpotAdapter, SpotConfig

cfg = SpotConfig(hostname="192.168.80.3", location_to_waypoint={"dock": "wp-12"})
with SpotAdapter(cfg) as spot:                       # credentials read from env-var NAMES in cfg
    assert spot.send_navigation_goal(location="dock").success
```

```python
from urml_conformance import ConformanceRunner
from urml_legged_runtime import LEGGED_ADAPTERS

runner = ConformanceRunner(adapter_factory=lambda: LEGGED_ADAPTERS["spot"]())
```

## Status

**v0.1 (this release):**
- `SpotAdapter` (standalone bosdyn) + `AnymalAdapter` (composes `RclpyAdapter`) + `LEGGED_ADAPTERS` registry.
- Hermetic unit tests: Spot against an injected fake `bosdyn` (navigation, dock, wait, measure, scan-stub, every not-supported sentinel, lifecycle power-off, the missing-`[spot]`-extra error); ANYmal against an injected fake inner (delegation + not-supported + conformance hook + `runtime_checkable`).
- Gated `.github/workflows/legged-integration.yml`: `spot-smoke` (real bosdyn wheels), `spot-arm64-build` (the bosdyn stack under `linux/arm64` QEMU — the Jetson-companion signal, mirroring `px4-arm64-build`), and a gated `legged-sim-e2e` matrix that skips cleanly without a sim/credential.

**Follow-ups (not yet):**
- US-compliant capability manifests (Boston Dynamics — US/Hyundai-owned; ANYbotics — Switzerland). Blocked on the `Mobility.drive_type` schema, which has no `legged`/`quadruped` value; that is the Phase-5 RFC fast-follow. Quadruped conformance fixtures land with the RFC, not before (correct sequencing, not a shortcut).
- Spot Arm SDK wiring for `grasp`/`release`; a vision/speech companion split.
- A real Spot sim path: Boston Dynamics' public sim is weaker than PX4 SITL and Isaac-Sim Spot needs an RTX host (never the Jetson). Until that or hardware exists, the Spot integration lane is honestly the hermetic fake-bosdyn path; the gated sim job skips cleanly.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema (the `drive_type` gap is tracked by the Phase-5 RFC).
- [`/reference/ros2-runtime/`](../ros2-runtime/) — the substrate engine `AnymalAdapter` composes.
- [`/reference/px4-runtime/`](../px4-runtime/) — the no-ROS sibling whose structure `SpotAdapter` mirrors.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
