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

# urml-embedded-runtime

**Educational-MCU reference runtime for URML** — `EmbeddedAdapter` for **micro:bit / Arduino-class** buggies over a plain serial line, **zero ROS**.

URML scales *down* to a microcontroller: a buggy whose firmware reads short ASCII commands off serial. The educational-flywheel analog of the PX4/marine no-ROS proof (RFC-0011 educational profile), mirroring `BlueRovAdapter`: lazy `pyserial`, cached lazy port, failures returned not raised. Built against the frozen Protocol per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md).

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | write the configured firmware command |
| `grasp` / `release` | write the configured gripper-servo command |
| `wait` | hold (success) |
| `measure` / `wait_for` | query + read one serial line |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** |

`dock`, `detect`, `capture`, `speak`, `listen` return `not_supported_on_mcu`. The drone trio returns `not_applicable_mcu`.

## Spec gaps (RFC-0014 protocol)

A *mobile* buggy fits the v0.1 schema honestly (it really is `differential`). A non-mobile LED/sensor MCU node does not — filed as **RFC-0018 (Draft)**: a minimal-MCU manifest subset, explicitly cross-referencing **RFC-0017** for the raw-actuation verb (not duplicated). See [`SPEC-GAPS.md`](SPEC-GAPS.md). `educational` validates with no schema change (`program.profile` is an open `Identifier`).

## Install / use

```bash
pip install -e reference/embedded-runtime[serial]   # installs pyserial
```

```python
from urml_embedded_runtime import EmbeddedAdapter, EmbeddedConfig
cfg = EmbeddedConfig(port="/dev/ttyACM0",
                     location_to_command={"waypoint_a": "GO A", "dock": "HOME"})
with EmbeddedAdapter(cfg) as buggy:
    assert buggy.send_navigation_goal(location="waypoint_a").success
```

## Status

**v0.1 (this release):**
- `EmbeddedAdapter` + `EmbeddedConfig` (pyserial, no ROS). `microbit_edu` manifest + `conformance/fixtures/educational/01_buggy_patrol_positive.yaml` verified through the runner (hermetic against `MockROSAdapter`; adapter-agnostic against `EmbeddedAdapter`). First fixture under the new `educational` profile dir.
- Hermetic unit tests: nav (configured + unmapped), grasp, measure, scan-stub, lifecycle, the not-supported / not-applicable sentinels, the missing-`[serial]`-extra error, the conformance hook — no pyserial install required.
- Gated `.github/workflows/embedded-integration.yml`: `embedded-smoke` (real pyserial loopback), `embedded-arm64-build` (Jetson-class QEMU), `embedded-board-e2e` placeholder against a real micro:bit/Arduino (manual dispatch only; first run is a calibration run by design).

**Follow-ups (not yet):** RFC-0018 outcome (minimal-MCU subset); a `pyfirmata2` path for stock Firmata sketches.

## Core Commitment

Apache 2.0. Outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. `pyserial`/`pyfirmata2` are optional extras imported lazily, never at module load.

## Related documents

- [`/reference/marine-runtime/`](../marine-runtime/) — the zero-ROS sibling whose structure this mirrors.
- [`/spec/profiles/educational/`](../../spec/profiles/educational/) — the RFC-0011 profile this serves.
- [`/docs/rfcs/0018-minimal-mcu-capability-subset.md`](../../docs/rfcs/0018-minimal-mcu-capability-subset.md) — the surfaced spec gap.
