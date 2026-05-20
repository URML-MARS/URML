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

# urml-isaac-runtime

**Simulator reference runtime for URML** — `IsaacAdapter` for **Isaac** physics, via the official Apache-2.0 `isaacsim` wheel.

Isaac is a pure-Python-bindings simulator over a bundled engine: headless, offline, no ROS. This adapter mirrors `BlueRovAdapter` / `PX4Adapter`: lazy `isaacsim`, **no ROS 2 dependency**, a lazily-loaded cached model/data, failures returned not raised. It is the **purest substrate-neutrality acid-test proof** — a runtime that faithfully implements the frozen substrate Protocol (RFC-0014) with zero ROS and no middleware: the sentence→motion loop with no robot at all.

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | write configured `ctrl` target onto `mjData`, step the engine `steps_per_command` steps |
| `wait` | step the engine |
| `measure` | read `mjData.sensordata` |
| `wait_for` | step-then-check (a sim has no external event bus) |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** (mirrors `PX4Adapter.run_scan`) |

`grasp`/`release`, `dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_in_base_isaac_sim` (a task-specific model + controller pairs via a companion). The drone trio `take_off`/`land`/`return_to_home` return `not_applicable_sim`.

## Install / use

```bash
pip install -e reference/isaac-runtime[sim]   # installs isaacsim
```

```python
from urml_isaac_runtime import IsaacAdapter, IsaacConfig
from urml_isaac_runtime.adapter import ControlTarget
cfg = IsaacConfig(model_path="arm.xml",
                   location_to_target={"home_pose": ControlTarget(ctrl=[0, 0, 0])})
with IsaacAdapter(cfg) as sim:
    assert sim.send_navigation_goal(location="home_pose").success
```

## Status

**v0.1 (this release):**
- `IsaacAdapter` + `IsaacConfig` (Isaac, no ROS). `isaac_arm_sim` manifest + `conformance/fixtures/home/17_isaacsim_sentence_to_motion_positive.yaml` verified through the runner (hermetic against `MockROSAdapter`; adapter-agnostic against `IsaacAdapter`).
- Hermetic unit tests: navigation (configured + unmapped), measure, scan-stub, lifecycle, the not-supported / not-applicable-sim sentinels, the model-path-required and missing-`[sim]`-extra errors, the conformance hook — no isaacsim install required.
- Gated `.github/workflows/isaacsim-integration.yml`: `isaacsim-smoke` (real isaacsim), `isaacsim-arm64-build` (the Jetson-class QEMU signal), and `isaacsim-sitl-e2e` against a real MJCF model (first run is a calibration run by design — the established px4/ros2/marine convention).
- [`SPEC-GAPS.md`](SPEC-GAPS.md): **none** — a simulator implements the existing primitives with zero new vocabulary.

**Follow-ups (not yet):** a bundled demo MJCF model + a true sentence→motion video; a task-model companion for `grasp`.

## Core Commitment

This runtime is Apache 2.0. It is outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 reference runtimes are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture.

## Related documents

- [`/reference/marine-runtime/`](../marine-runtime/) — the zero-ROS sibling whose structure this mirrors.
- [`/docs/rfcs/0014-substrate-conformance.md`](../../docs/rfcs/0014-substrate-conformance.md) — the conformance contract this is built against.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
