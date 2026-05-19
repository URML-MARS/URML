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

# urml-opcua-runtime

**Industrial-automation reference runtime for URML** — `OpcUaAdapter` for **OPC UA Robotics** cells, via `asyncua`.

OPC UA Robotics is the universal factory-floor / PLC companion spec. This adapter is the industrial-automation analog of the PX4/marine no-ROS proof and mirrors `BlueRovAdapter`: lazy `asyncua`, **no ROS 2 dependency**, a lazily-opened cached client, failures returned not raised. It hits the manufacturer / federal-procurement wedge ([RFC-0007](../../docs/rfcs/0007-manufacturer-go-to-market.md)) and complements the shipped industrial-arm family + [RFC-0013](../../docs/rfcs/0013-industrial-layer2-primitives.md) primitives. Built against the frozen substrate Protocol per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md).

## Method coverage

| URML primitive | v0.1 |
|---|---|
| `move_to` / `hover` | call the configured per-location OPC UA method node |
| `dock` | call the configured station-service method — **the path RFC-0013 `swap_tool` rides, preserved** |
| `grasp` / `release` | call the configured manipulation method |
| `wait` | hold (success) |
| `measure` / `wait_for` | read the configured variable node |
| `report` | structured record to a local sink (no cloud) |
| `scan` | documented **stub success** |

`detect`, `capture`, `speak`, `listen` return `not_supported_on_opcua_cell` (pair a vision/HMI companion). The drone trio returns `not_applicable_opcua`.

## Spec gaps (RFC-0014 protocol)

This runtime surfaced two genuinely inexpressible needs — filed as **RFC-0015** (ControlProgram/PLC-method invocation) and **RFC-0016** (real-time/cyclic manifest block), both `Draft`, maintainer-decided. They are **not** silently bolted on. See [`SPEC-GAPS.md`](SPEC-GAPS.md), which also flags the `asyncua` **LGPL-3.0** optional-dependency posture for maintainer ratification.

## Install / use

```bash
pip install -e reference/opcua-runtime[opcua]   # installs asyncua
```

```python
from urml_opcua_runtime import OpcUaAdapter, OpcUaConfig
from urml_opcua_runtime.adapter import MethodTarget
cfg = OpcUaConfig(location_to_method={"pick_bin": MethodTarget(method="ns=2;s=MoveTo", args=["pick_bin"])})
with OpcUaAdapter(cfg) as cell:
    assert cell.send_navigation_goal(location="pick_bin").success
```

## Status

**v0.1 (this release):**
- `OpcUaAdapter` + `OpcUaConfig` (asyncua, no ROS). `opcua_cell` US-provenance manifest + `conformance/fixtures/industrial/07_opcua_cell_positive.yaml` (RFC-0013 `pick_from`/`place_at`) verified through the runner (hermetic against `MockROSAdapter`; adapter-agnostic against `OpcUaAdapter`).
- Hermetic unit tests: nav (configured + unmapped), dock/swap_tool, grasp, measure, scan-stub, lifecycle, the unconfigured / not-supported / not-applicable sentinels, the missing-`[opcua]`-extra error, the conformance hook — no asyncua install required.
- Gated `.github/workflows/opcua-integration.yml`: `opcua-smoke` (real asyncua), `opcua-arm64-build` (the Jetson-class QEMU signal), `opcua-server-e2e` against a local asyncua server (first run is a calibration run by design — the established px4/ros2/marine convention).

**Follow-ups (not yet):** RFC-0015/0016 outcomes; a bundled asyncua demo server for the e2e.

## Core Commitment

Apache 2.0. Outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 reference runtimes are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. `asyncua` is an LGPL-3.0 *optional* dependency — see SPEC-GAPS.md.

## Related documents

- [`/reference/marine-runtime/`](../marine-runtime/) — the zero-ROS sibling whose structure this mirrors.
- [`/docs/rfcs/0014-substrate-conformance.md`](../../docs/rfcs/0014-substrate-conformance.md) — the conformance contract.
- [`/docs/rfcs/0015-control-program-invocation.md`](../../docs/rfcs/0015-control-program-invocation.md) · [`/docs/rfcs/0016-realtime-cyclic-manifest-block.md`](../../docs/rfcs/0016-realtime-cyclic-manifest-block.md) — the surfaced spec gaps.
