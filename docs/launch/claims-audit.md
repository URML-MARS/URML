# Claims audit

Every `✅` in the README "What URML gives you" table maps to a shipped file and
a passing test or recorded CI run. This document is the backing evidence. It
exists so a reader can verify the front page is not overselling — and so the
maintainer can re-check before each public update.

**Measured 2026-05-16, on `main`.** Test counts are `pytest` pass totals, run
per package (the packages share test-module names, so a single combined
invocation collides on collection — run each separately).

| Suite | Command | Result |
|---|---|---|
| validator | `cd reference/validator && python -m pytest` | **188 passed** |
| llm-bridge | `cd reference/llm-bridge && python -m pytest` | **77 passed** |
| ros2-runtime | `cd reference/ros2-runtime && python -m pytest` | **114 passed, 4 skipped** |
| px4-runtime | `cd reference/px4-runtime && python -m pytest` | **54 passed, 1 skipped** |
| conformance | `python -m pytest conformance/tests` | **41 passed** |
| **Total** | | **474 passed + 5 gated-skipped** |

The 5 skips are the live integration tests, gated behind
`URML_ROS2_INTEGRATION=1` / `URML_GAZEBO_E2E=1` (ROS 2 / Gazebo) and
`URML_PX4_SITL=1` (PX4 SITL) — no rclpy/sim/SITL on a dev box. They are
*run* by the gated CI workflows: the ROS 2 ones by
`ros2-integration.yml` (see the ROS 2 row below), the PX4 SITL one by
`px4-integration.yml` (see the PX4 row below).

## Per-row backing

**Five-pass static validator — 188 unit tests.**
`reference/validator/src/urml_validator/validator.py` (`validate()` runs Pass
1–5); `errors.py` `ErrorCode` namespaces. Pass 3 geofence / 3D-altitude /
people-occupancy: `_check_envelope_geofence`, `_altitude_in_band`,
`_check_envelope_occupancy_zones`. Pass 4 cross-primitive type check:
`binding.type_mismatch`. Evidence: validator suite 188 passed.

**17 primitives — validator + reference-runtime executors for all 17.**
Schemas: `reference/validator/src/urml_validator/schemas/`. Runtime executors
incl. drone `take_off`/`land`/`return_to_home`:
`reference/ros2-runtime/src/urml_ros2_runtime/` (dispatched by RclpyAdapter /
MockROSAdapter). Evidence: ros2-runtime 114 passed; conformance drone fixtures.

**Compliance enforcement — `--no-policy` opt-out.**
`reference/validator/src/urml_validator/policy.py` + bundled default policy;
RFC-0004. Evidence: validator suite policy tests; `compliance-walkthrough.md`
commands reproduce verbatim.

**LLM bridge — 77 unit tests.**
`reference/llm-bridge/` — `providers/` (anthropic, openai, echo); revision loop
with `BridgePolicyViolation` short-circuit; home/drone/industrial few-shots.
Evidence: llm-bridge 77 passed.

**Conformance suite — 33 fixtures, `urml conformance run`.**
`conformance/fixtures/**/*.yaml` = 33 files (home + drone + industrial +
compliance + policy-override). CLI: `urml conformance run`. Evidence:
conformance 41 passed (parametrized over fixtures + loader/smoke). The
33rd is `drone/flight_only_positive`, the pure-flight fixture the PX4
SITL e2e flies (see the PX4 row).

**CLI — six subcommands.** `urml --help` →
`validate schema translate emit-prompt init conformance`.

**Mock reference runtime.** `reference/ros2-runtime/.../substrate/mock.py`
(`MockROSAdapter`). Default substrate for the hermetic suites.

**Real ROS 2 adapter (`RclpyAdapter`) — end-to-end verified ×3.**
`reference/ros2-runtime/src/urml_ros2_runtime/substrate/rclpy_adapter.py`
(full ROSAdapter Protocol, lazy `rclpy`). End-to-end: the
`home/nav_patrol_positive` conformance fixture run through `ConformanceRunner`
with a live `RclpyAdapter` driving a TurtleBot 4 + Nav2 Gazebo simulation,
green on three calibration runs of `.github/workflows/ros2-integration.yml`
(`gazebo-e2e` job): runs **25953413044, 25953936578, 25954097635**. The
`rclpy-smoke` job (real rclpy, no sim) also green after the venv calibration
(merged in #45).

**PX4 / MAVLink reference runtime (`PX4Adapter`).**
`reference/px4-runtime/src/urml_px4_runtime/adapter.py` — full Protocol via
`pymavlink`, no ROS dependency; flight primitives real, perception/manipulation
return a documented not-supported result. Evidence: px4-runtime 54 passed.

**PX4 SITL end-to-end — added and gated, NOT yet calibrated.**
`reference/px4-runtime/tests/integration/test_px4_sitl_e2e.py` flies the
`drone/flight_only_positive` conformance fixture through `ConformanceRunner`
with a live `PX4Adapter` against PX4 SITL, gated behind `URML_PX4_SITL=1`.
The gated CI job is `px4-sitl-e2e` in `.github/workflows/px4-integration.yml`
(workflow_dispatch + weekly cron). Honest status: this is the PX4 analog of
the ROS 2 `gazebo-e2e` job *before* its calibration runs. No green run is
claimed here — the workflow has not been executed yet; its first run is the
calibration run, exactly as `gazebo-e2e` was treated, and a green run ID will
be recorded in this row only once one exists. Hermetic evidence today:
px4-runtime 54 passed, 1 skipped (the gated e2e), conformance 41 passed
(incl. the fixture it flies).

**CompositeAdapter.**
`reference/px4-runtime/src/urml_px4_runtime/composite.py` — routes each
Protocol method to a flight (PX4) or companion (ROS 2) backend; explicit
overridable routing table. Evidence: px4-runtime 54 passed (incl. composite
routing/lifecycle tests).

**Seven RFCs (0001–0007).** `docs/rfcs/` — `0001`–`0007` (`0000` is the
template). RFC-0006 (connectivity/link-loss) and RFC-0007 (manufacturer
go-to-market) are accepted and implemented.

## Re-running this audit

```bash
for d in reference/validator reference/llm-bridge reference/ros2-runtime reference/px4-runtime; do
  echo -n "$d: "; (cd "$d" && python -m pytest -q | tail -1)
done
python -m pytest conformance/tests -q | tail -1
find conformance/fixtures -name '*.yaml' | wc -l   # fixtures
ls docs/rfcs/ | grep -E '^000[1-9]'                 # RFCs (exclude 0000-template)
urml --help                                          # subcommands
```

Update the date and any moved numbers here and in the README table together —
they are a pair. Numbers without this audit are not allowed on the front page.
