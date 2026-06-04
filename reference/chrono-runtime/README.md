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

# urml-chrono-runtime

**High-fidelity validation reference runtime for URML** — `ChronoAdapter` for **Project Chrono** multibody / multi-physics, via `pychrono`.

Project Chrono is an open high-fidelity multibody engine (Chrono::Vehicle ground dynamics, terramechanics for deformable terrain, Chrono::Sensor) from the University of Wisconsin-Madison and the University of Parma. This adapter mirrors `MujocoAdapter` / `PX4Adapter`: lazy `pychrono`, **no ROS 2 dependency**, a lazily-built cached `ChSystem`, failures returned not raised. Built against the frozen substrate Protocol per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md).

Chrono's distinctive role for URML is **high-fidelity pre-deployment validation** ([RFC-0328](../../docs/rfcs/0328-project-chrono-outreach.md)): URML checks a program statically against the declared capability manifest and active safety envelope first, then drives the same validated intent through a short Chrono simulation segment so the dynamics come back as evidence. URML composes **above** Chrono; it never embeds it. The differentiator is the static capability-and-envelope check *before* the expensive multibody solver ever spins, so the high-fidelity run only ever exercises admissible programs.

The primitive → driver-input altitude follows Project Chrono lead Dan Negrut's feedback on [issue #746](https://github.com/projectchrono/chrono/issues/746): align each manifest entry to a concrete `ChSystem` configuration at the level of Chrono's motion primitives and driver inputs.

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | apply the configured driver segment, advance the `ChSystem` `steps_per_command` steps, return the dynamics evidence (sim time, contacts, commanded driver inputs) |
| `wait` | step the engine |
| `measure` | return the accumulated dynamics evidence (`value`=contacts, `sim_time`, `driver`, `backend`) |
| `wait_for` | step-then-check (a sim has no external event bus) |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** (mirrors `PX4Adapter.run_scan`) |

`grasp`/`release`, `dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_in_base_sim` (a Chrono::Sensor or articulated-model companion supplies them under the unchanged program, manifest, and validator). The drone trio returns `not_applicable_sim`.

## Install / use

PyChrono ships via **conda-forge**, not as a PyPI wheel. The `[chrono]` extra is intentionally empty (it documents the boundary); `pychrono` is imported lazily, so this module loads on every host without it.

```bash
conda install -c conda-forge pychrono            # the engine
pip install -e reference/chrono-runtime[chrono]   # the adapter
```

```python
from urml_chrono_runtime import ChronoAdapter, ChronoConfig
from urml_chrono_runtime.adapter import DriverSegment
cfg = ChronoConfig(steps_per_command=200,
                   location_to_segment={"ridge_waypoint": DriverSegment(driver=[0.8, 0.1, 0.0])})
with ChronoAdapter(cfg) as sim:
    r = sim.send_navigation_goal(location="ridge_waypoint")
    assert r.success and r.final_pose["sim_time"] > 0.0
```

Without `pychrono` installed, `ChronoAdapter()` raises a clear error pointing at conda-forge.

## Status

**v0.1 (this release):**
- `ChronoAdapter` + `ChronoConfig` (PyChrono, no ROS). `chrono_vehicle_cell` manifest + `conformance/fixtures/home/21_chrono_vehicle_terrain_positive.yaml` verified through the runner (hermetic against `MockROSAdapter`; adapter-agnostic against `ChronoAdapter`).
- Hermetic unit tests: navigation (configured + unmapped), the NSC/SMC system-type switch, measure (validation-evidence payload), scan-stub, lifecycle, the not-supported / not-applicable-sim sentinels, the missing-`pychrono` (conda-pointing) error, and the conformance hook — no pychrono install required (a fake `pychrono` is injected into `sys.modules`).
- Gated `.github/workflows/chrono-integration.yml`: `chrono-smoke` (real pychrono from conda-forge + the hermetic suite + the live smoke) and `chrono-sitl-e2e` against a real Chrono::Vehicle scene (first run is a calibration run by design — the established px4 / mujoco / opcua convention).
- [`SPEC-GAPS.md`](SPEC-GAPS.md): two manifest gaps the mapping surfaced (a terrain-fidelity hint and a simulator-target-class hint), queued as Spec RFCs for maintainer decision per RFC-0328, **not** silently added.

**Follow-ups (not yet):** a bundled Chrono::Vehicle terramechanics scene + a true sentence→motion validation video; a Chrono::Sensor companion for `detect` / `capture`; richer evidence (contact forces, sinkage, tip margin) once a scene is pinned.

## Core Commitment

This runtime is Apache 2.0. It is outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 reference runtimes are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. PyChrono / Project Chrono is BSD-3-Clause (confirmed by the maintainers on #746); a validated-intent mapping carries no license entanglement.

## Related documents

- [`/reference/mujoco-runtime/`](../mujoco-runtime/) — the zero-ROS simulator sibling whose structure this mirrors.
- [`/docs/rfcs/0328-project-chrono-outreach.md`](../../docs/rfcs/0328-project-chrono-outreach.md) — the engagement and mapping this implements.
- [`/docs/rfcs/0014-substrate-conformance.md`](../../docs/rfcs/0014-substrate-conformance.md) — the conformance contract this is built against.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
