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

# urml-industrial-arm-runtime

**ROS-Industrial / MoveIt 2 reference runtime for URML** — one first-class adapter per arm vendor: **ABB, FANUC, KUKA, YASKAWA, Universal Robots, Franka Emika**.

> **Maturity.** Code complete and hermetically unit-tested (every brand, every delegated primitive, the not-supported sentinels, the conformance hook). No live arm or ROS 2 + MoveIt 2 sim run has happened yet; the gated integration lane's first run per brand is a calibration run by design, not a regression signal. **Not production-ready.** URML's live-verified surface today is the validator, the `make demo` / `make demo-run` loop, and the ROS 2 runtime; this runtime is not yet in that set.

An industrial manipulator is a fixed-base arm. Its load-bearing URML primitives are `grasp` / `release` (a gripper action) and `move_to` (an end-effector move via MoveIt 2). That dispatch shape is identical to the one the ROS 2 runtime's [`RclpyAdapter`](../ros2-runtime/) already implements, so the substrate plumbing is single-sourced: each brand adapter **composes** a `RclpyAdapter` rather than re-implementing MoveIt 2. The per-brand surface is still real and first-class — distinct classes, distinct default configs (each vendor's ROS-Industrial action-server conventions), distinct not-supported tag. "One adapter per brand", no duplicated substrate code.

## Method coverage

Full `ROSAdapter` Protocol. Supported on a bare fixed-base arm, delegated to the composed adapter:

| URML primitive | Mapping |
|---|---|
| `grasp` / `release` | `control_msgs/GripperCommand` action |
| `move_to` / `hover` | MoveIt 2 move to a named pose (`/move_action`) |
| `measure` | single reading (joint state / wrench) |
| `wait_for` | block on a cell signal / threshold |
| `wait` | dwell in place for a duration |
| `report` | structured status upstream |

The primitives a bare arm cannot serve — `dock`, `detect`, `scan`, `capture`, `speak`, `listen`, and the drone trio `take_off` / `land` / `return_to_home` — return `SubstrateResult(success=False, reason="not_supported_on_industrial_arm[<brand>]: ...")` rather than raising. This is the same pattern `PX4Adapter` uses for `not_supported_on_bare_autopilot`. A work-cell that pairs an arm with a vision system dispatches detection through a companion adapter, exactly as the drone stack pairs flight with a ROS 2 companion; the URML program, manifest, and validator are unchanged and unaware.

## rclpy is lazy

Importing this package works on every host (Windows included): the `rclpy` import lives inside `RclpyAdapter` and only fires when an adapter is **constructed**. Constructing a brand adapter therefore needs a sourced ROS 2 environment — the ROS-Industrial driver plus MoveIt 2 for that arm. There is no installable extra: `rclpy` ships with a ROS 2 distribution, not from PyPI (same as `urml-ros2-runtime`).

## Install

```bash
pip install -e reference/industrial-arm-runtime
```

## Use

```python
from urml_industrial_arm_runtime import AbbAdapter

# Brand default config (ROS-Industrial conventions); override with an
# AdapterConfig for a specific cell's action servers.
with AbbAdapter() as adapter:
    result = adapter.send_manipulation_goal(action="grasp", force_n=15.0)
    assert result.success
```

Through the conformance suite (the same hook every URML runtime uses):

```python
from urml_conformance import ConformanceRunner
from urml_industrial_arm_runtime import BRAND_ADAPTERS

runner = ConformanceRunner(adapter_factory=lambda: BRAND_ADAPTERS["abb"]())
report = runner.run()
```

## Status

**v0.1 (this release) — code complete and hermetically tested; no live-substrate end-to-end run yet:**
- Six first-class brand adapters (`AbbAdapter`, `FanucAdapter`, `KukaAdapter`, `YaskawaAdapter`, `UrAdapter`, `FrankaAdapter`) over a shared `IndustrialArmAdapter` core that composes `RclpyAdapter`. UR (Denmark/Teradyne) is the dominant cobot; Franka (Germany) is the dominant research arm and the educational-community flywheel — both pass the default US-federal policy.
- `BRAND_ADAPTERS` name→class registry for config-driven selection (CI matrices, the conformance `adapter_factory`).
- Hermetic unit tests: every brand, every delegated primitive, every not-supported sentinel, the conformance hook, `runtime_checkable` Protocol conformance, and context-manager teardown — no ROS 2 install required.
- Gated `.github/workflows/industrial-arm-integration.yml` (matrixed abb/fanuc/kuka/yaskawa) running the existing `conformance/fixtures/industrial/pick_red_positive` fixture through each brand adapter against a ROS 2 + MoveIt 2 sim, plus a gated `tests/integration/` scaffold. Modelled on `ros2-integration.yml`; first runs per brand are calibration runs by design, not regression signals.

**Why a vision companion.** `GraspArgs.target` is a required `VarRef` — URML `grasp` always acts on a *detected* target, so any pick-place program contains a `detect` step. A bare fixed-base arm has no onboard perception (returns `not_supported_on_industrial_arm`), exactly as a bare PX4 autopilot has none. The gated test pairs the brand arm with a vision companion via the already-tested generic `urml_px4_runtime.CompositeAdapter` (arm owns motion/manipulation/report; companion owns detection) — no industrial-specific composite code is duplicated. This mirrors the drone stack's flight+companion split.

**Follow-ups (not yet):**
- Per-brand US-compliant provenance manifests (ABB Sweden, FANUC/YASKAWA Japan, KUKA Germany). v0.1 reuses the existing compliant `industrial_cell` manifest; the profile README already documents that ABB/FANUC/KUKA controllers pass the default US-federal policy.
- A detection source wired into the sim so the gated `detect` step resolves against the real `RclpyAdapter` companion (part of the documented first-run calibration).

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/profiles/industrial/`](../../spec/profiles/industrial/) — the profile this runtime targets.
- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema (manipulation fields).
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
- [`/reference/ros2-runtime/`](../ros2-runtime/) — the composed substrate engine (`RclpyAdapter`).
- [`/reference/px4-runtime/`](../px4-runtime/) — the sibling runtime this package's structure mirrors.
