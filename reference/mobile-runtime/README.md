# urml-mobile-runtime

**Wheeled-AMR reference runtime for URML** — `HuskyAdapter` and `JackalAdapter` for **Clearpath Husky / Jackal**, the canonical ROS 2 differential-drive research/field bases.

Husky and Jackal speak ROS 2 + Nav2, so each adapter **composes** the ROS 2 runtime's `RclpyAdapter` — the same single-sourced-substrate pattern the industrial-arm, ANYmal, and Digit families use. Distinct first-class classes, brand-scoped not-supported tag, no duplicated Nav2 plumbing. `differential` `drive_type` is already in the v0.1 manifest schema, so this needs no RFC.

## Method coverage

`move_to`/`hover`, `wait`, `measure`, `wait_for`, `report` delegate to the composed ROS 2 substrate. `grasp`/`release`, `dock`, `detect`, `scan`, `capture`, `speak`, `listen`, and the drone trio return `not_supported_on_amr[<brand>]` (returned, not raised). A Clearpath base carrying a UR/Franka arm + Robotiq gripper (a common mobile-manipulator config) pairs with an industrial-arm companion adapter, exactly as the drone stack pairs flight with a companion.

## Declared "parts"

The companion fixture `clearpath_husky` manifest declares parts as first-class provenance components: a **Robotiq** 2F-85 gripper (Canada), an **Intel RealSense** D435 (US), and a **Clearpath** base (Canada) — all compliant under the bundled US-federal default policy. Its negative twin `hesai_lidar_denied` swaps in one critical **Hesai** LIDAR (FCC Covered List) and is rejected with `policy.vendor_denied`, pushing the denylisted-vendor check down to component granularity (cf. `home/policy_vendor_denylist`, `quadruped/unitree_vendor_denied`).

## Install / use

```bash
pip install -e reference/mobile-runtime   # needs a sourced ROS 2 env to construct
```

```python
from urml_conformance import ConformanceRunner
from urml_mobile_runtime import MOBILE_ADAPTERS

runner = ConformanceRunner(adapter_factory=lambda: MOBILE_ADAPTERS["husky"]())
```

## Status

**v0.1 (this release):**
- `HuskyAdapter` + `JackalAdapter` over a shared `ClearpathAdapter` core (composes `RclpyAdapter`) + `MOBILE_ADAPTERS` registry.
- Hermetic unit tests: delegation, every not-supported sentinel, the conformance hook, `runtime_checkable` conformance, teardown — no ROS 2 install required.
- `clearpath_husky` (compliant parts) + `hesai_lidar_denied` (denied part) manifests + `conformance/fixtures/mobile/` positive & negative fixtures, verified through the conformance runner.
- Gated `.github/workflows/mobile-integration.yml`: `mobile-smoke`, `mobile-arm64-build` (hermetic suite under `linux/arm64` QEMU — the Jetson-class signal), and a matrixed `mobile-sim-e2e` against the Clearpath Gazebo sim (first runs per brand are calibration runs by design, the established `ros2-integration` convention).

**Follow-ups (not yet):**
- A mobile-manipulator composite (Clearpath base + UR/Franka arm) wiring, analogous to the industrial vision-companion split.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/reference/ros2-runtime/`](../ros2-runtime/) — the substrate engine these adapters compose.
- [`/reference/industrial-arm-runtime/`](../industrial-arm-runtime/) — the arm companion for mobile-manipulator configs.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
