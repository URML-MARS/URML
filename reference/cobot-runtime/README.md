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

# urml-cobot-runtime

**Collaborative-arm reference runtime for URML** — `UrRtdeAdapter` (Universal Robots / RTDE) + `FrankaFciAdapter` (Franka / FCI via `panda-py`), **zero ROS**.

The two most-deployed cobots, driven by their **native SDKs with no ROS** — the proof that the popular real arms need no ROS. `industrial-arm-runtime`'s `Ur`/`FrankaAdapter` compose `RclpyAdapter` (ROS 2 + MoveIt 2); these are the ROS-free siblings, exactly as `marine-runtime` is the ROS-free sibling of `ros2-runtime`. Both mirror `BlueRovAdapter`: lazy vendor SDK, cached lazy connection, failures returned not raised. Built against the frozen Protocol per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md).

## Method coverage (both adapters)

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | drive the TCP to a configured pose (UR `moveL` / Franka joint move) |
| `grasp` / `release` | gripper command; scalar `force_n` honoured at v0.1 fidelity |
| `wait` | hold (success) |
| `measure` / `wait_for` | TCP force / robot state read |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** |

`dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_on_bare_cobot` (pair a station/vision/HMI companion). The drone trio returns `not_applicable_cobot`.

## Spec gaps (RFC-0014 protocol)

One genuinely inexpressible need filed as **RFC-0017 (Draft)** — raw digital-I/O tool actuation (not `grasp`, not a station service). Force/impedance beyond scalar `force_n` is a documented **watch-item** (no RFC); joint-space waypoints are absorbed by config (no gap). See [`SPEC-GAPS.md`](SPEC-GAPS.md).

## Install / use

```bash
pip install -e reference/cobot-runtime[ur]      # Universal Robots (ur_rtde)
pip install -e reference/cobot-runtime[franka]  # Franka (panda-python, Apache-2.0)
```

```python
from urml_cobot_runtime import UrRtdeAdapter, CobotConfig
from urml_cobot_runtime.adapter import Pose
cfg = CobotConfig(robot_ip="192.168.1.10",
                  location_to_pose={"pick": Pose(vector=[0.4, -0.3, 0.1, 0, 3.14, 0])})
with UrRtdeAdapter(cfg) as ur:
    assert ur.send_navigation_goal(location="pick").success
```

## Status

**v0.1 (this release):**
- `UrRtdeAdapter` + `FrankaFciAdapter` + `CobotConfig` (native SDKs, no ROS). `cobot_cell` US-provenance manifest + `conformance/fixtures/industrial/08_cobot_cell_positive.yaml` (RFC-0013 `pick_from`/`place_at`) verified through the runner (hermetic against `MockROSAdapter`; adapter-agnostic against the cobot adapters).
- Hermetic unit tests for both adapters: nav (configured + unmapped), grasp/release, measure, scan-stub, lifecycle, the not-supported / not-applicable sentinels, the missing-`[ur]`/`[franka]`-extra errors, the conformance hook — no vendor SDK install required.
- Gated `.github/workflows/cobot-integration.yml`: `cobot-smoke` (real SDKs), `cobot-arm64-build` (Jetson-class QEMU), `cobot-controller-e2e` placeholder against a real UR/Franka (first run is a calibration run by design).

**Follow-ups (not yet):** RFC-0017 outcome (digital I/O); real Robotiq/Franka-gripper wiring beyond the v0.1 gripper command.

## Core Commitment

Apache 2.0. Outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. `panda-py` is Apache-2.0; `ur_rtde` is an optional `[ur]` extra imported lazily, never at module load (the `rclpy`/`pymavlink` posture).

## Related documents

- [`/reference/marine-runtime/`](../marine-runtime/) — the zero-ROS sibling whose structure this mirrors.
- [`/reference/industrial-arm-runtime/`](../industrial-arm-runtime/) — the ROS 2 + MoveIt 2 Ur/Franka adapters this is the ROS-free sibling of.
- [`/docs/rfcs/0017-digital-io-actuation.md`](../../docs/rfcs/0017-digital-io-actuation.md) — the surfaced spec gap.
