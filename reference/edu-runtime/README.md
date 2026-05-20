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

# urml-edu-runtime

**Educational-platform reference runtime for URML** — `VexV5Adapter`, `LegoSpikeAdapter`, `ThymioAdapter`, **zero ROS**.

The classroom/maker adoption flywheel (RFC-0011). VEX V5 brain (USB/serial via `pyvex`), LEGO SPIKE Prime / Mindstorms hub (BLE via `pybricksdev`), Thymio (Aseba TDM via `tdmclient`). Each platform's native SDK is imported lazily by its adapter — this module loads on every host without any `[vex]`/`[lego]`/`[thymio]` extra. Built against the frozen substrate Protocol per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md). Mirrors `cobot-runtime`'s `_CobotBase` shape.

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | write the configured firmware command (VEX `run_command` / LEGO `send_command` / Thymio `send_event`) |
| `grasp` / `release` | write the configured claw-servo command |
| `wait` | hold (success) |
| `measure` / `wait_for` | one telemetry read |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** |

`dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_on_edu_platform`. The drone trio returns `not_applicable_edu`.

## Spec gaps (RFC-0014 protocol)

Cross-references existing Drafts — **no new RFC**:
- LED/buzzer/button = digital-output → **RFC-0017** (already Draft from cobot-runtime).
- Non-mobile sensor/actuator-only node → **RFC-0018** (already Draft from embedded-runtime).

See [`SPEC-GAPS.md`](SPEC-GAPS.md).

## Install / use

```bash
pip install -e reference/edu-runtime[vex]      # VEX V5 (pyvex)
pip install -e reference/edu-runtime[lego]     # LEGO Pybricks (pybricksdev BLE)
pip install -e reference/edu-runtime[thymio]   # Thymio (tdmclient)
```

```python
from urml_edu_runtime import VexV5Adapter, EduConfig
cfg = EduConfig(device="COM3",
                location_to_command={"start_mat": "GO START", "home_mat": "GO HOME"})
with VexV5Adapter(cfg) as vex:
    assert vex.send_navigation_goal(location="start_mat").success
```

## Status

**v0.1 (this release):**
- 3 adapters + `EduConfig` + `BRAND_ADAPTERS` registry. Hermetic suite green via fake-SDK injection (`pytest reference/edu-runtime/tests -q`).
- 3 manifest fixtures (VEX V5 clawbot, LEGO SPIKE driving base, Thymio classroom buggy) + 3 conformance fixtures under `conformance/fixtures/educational/`.
- Gated `.github/workflows/edu-integration.yml`: `edu-smoke` (real SDKs), `edu-arm64-build` (Jetson-class QEMU with SDKs absent), `edu-board-e2e` placeholder that `exit 1`s until a real board is wired (the marine/cobot HONESTY-NOTE precedent).

## Core Commitment

Apache 2.0. Outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. All vendor SDKs are optional extras imported lazily, never at module load.

## Related documents

- [`/reference/cobot-runtime/`](../cobot-runtime/) — the zero-ROS sibling whose `_CobotBase` shape this mirrors as `_EduBase`.
- [`/reference/embedded-runtime/`](../embedded-runtime/) — the micro:bit/Arduino serial-port sibling (different transport model).
- [`/spec/profiles/educational/`](../../spec/profiles/educational/) — the RFC-0011 profile this serves.
- [`/docs/rfcs/0017-digital-io-actuation.md`](../../docs/rfcs/0017-digital-io-actuation.md) · [`/docs/rfcs/0018-minimal-mcu-capability-subset.md`](../../docs/rfcs/0018-minimal-mcu-capability-subset.md) — the cross-referenced gaps.
