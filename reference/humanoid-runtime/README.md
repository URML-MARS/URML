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

# urml-humanoid-runtime

**Humanoid reference runtime for URML** — `DigitAdapter` for **Agility Robotics Digit**.

Of the humanoids on the multi-brand target list, Digit is the only one with a usable public SDK + simulator. Tesla Optimus, Figure, Apptronik Apollo and 1X NEO have no public developer access, so per the plan they are covered **manifest + spec only** (no adapter — code with nothing to run against would be dishonest). Those manifests land with the Phase-5 `Mobility.drive_type` RFC, since a humanoid manifest cannot validate until that schema gap is closed.

## Design

Digit exposes ROS 2 interfaces, so `DigitAdapter` composes the ROS 2 runtime's `RclpyAdapter` — the same single-sourced-substrate pattern the industrial-arm and ANYmal adapters use. Distinct first-class class, brand-scoped not-supported tag, no duplicated ROS 2 plumbing.

## v0.1 scope: the locomotion subset

Digit does whole-body manipulation, but URML `grasp` requires a detected `$target` and whole-body/bimanual semantics are a deliberate **future RFC** (per the multi-brand plan: "v0.1 humanoid coverage is the locomotion + single-arm subset"). v0.1 supports the locomotion path and reports the rest honestly:

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover`, `wait`, `measure`, `wait_for`, `report` | delegated to the composed ROS 2 substrate |
| `grasp` / `release`, `dock`, `detect`, `scan`, `capture`, `speak`, `listen`, drone trio | `not_supported_on_humanoid[digit]: ...` (returned, not raised) |

## Install / use

```bash
pip install -e reference/humanoid-runtime   # needs a sourced ROS 2 env to construct
```

```python
from urml_conformance import ConformanceRunner
from urml_humanoid_runtime import HUMANOID_ADAPTERS

runner = ConformanceRunner(adapter_factory=lambda: HUMANOID_ADAPTERS["digit"]())
```

## Status

**v0.1 (this release):**
- `DigitAdapter` (composes `RclpyAdapter`, locomotion subset) + `HUMANOID_ADAPTERS` registry.
- Hermetic unit tests: delegation, every v0.1 not-supported sentinel, the conformance hook, `runtime_checkable` conformance, context-manager teardown — no ROS 2 install required.
- Gated `.github/workflows/humanoid-integration.yml`: `digit-smoke`, `digit-arm64-build` (hermetic suite under `linux/arm64` QEMU), and a `digit-sim-e2e` that skips cleanly without a sim host (the established px4/ros2 convention).

**Follow-ups (not yet):**
- US-compliant Digit manifest (Agility — US), plus the manifest+spec-only entries for Tesla Optimus / Figure / Apptronik Apollo / 1X NEO. All blocked on the Phase-5 `Mobility.drive_type` RFC (no `biped`/`humanoid` value); they land with it. Correct sequencing, not a shortcut.
- Whole-body / bimanual manipulation primitives (a separate future RFC); then Digit's manipulation path moves out of not-supported.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/reference/ros2-runtime/`](../ros2-runtime/) — the substrate engine `DigitAdapter` composes.
- [`/reference/legged-runtime/`](../legged-runtime/) — the sibling family sharing the compose pattern.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
