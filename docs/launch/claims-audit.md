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

# Claims audit

Every `✅` in the README "What URML gives you" table maps to a shipped file and
a passing test or recorded CI run. This document is the backing evidence. It
exists so a reader can verify the front page is not overselling — and so the
maintainer can re-check before each public update.

**Measured 2026-05-20, on `main`** (commit `a19daee`). This is the post-Track-I
refresh — three new PRs (#102 / #103 / #104) added eight compliant-part fixtures,
five ROS-Industrial arm-brand adapters, and three zero-ROS cobot-brand adapters
since the post-A-G audit. No new runtime packages and no new RFCs in this batch
(parts and brands rode the existing frozen Protocol; the spec-gap loop produced
nothing inexpressible). The figures below were re-measured from scratch via
per-package `PYTHONPATH` + `--junit-xml` (pytest's terminal summary truncates in
some shells; the xml is the reliable count).

| Suite | Result |
|---|---|
| validator | **242 passed** |
| llm-bridge | **77 passed** |
| ros2-runtime | **115 passed, 4 skipped** |
| px4-runtime | **54 passed, 4 skipped** |
| conformance | **97 passed** |
| marine-runtime | **4 passed** |
| industrial-arm-runtime | **65 passed, 1 skipped** (16 brand adapters parameterized) |
| legged-runtime | **5 passed** |
| humanoid-runtime | **4 passed** |
| mobile-runtime | **4 passed** |
| opcua-runtime | **4 passed, 3 skipped** |
| cobot-runtime | **11 passed, 2 skipped** (8 brand adapters parameterized) |
| mujoco-runtime | **5 passed, 3 skipped** |
| embedded-runtime | **4 passed, 3 skipped** |
| edu-runtime | **6 passed, 2 skipped** (3 platform adapters parameterized) |
| isaac-runtime | **5 passed, 3 skipped** |
| autosar-runtime | **4 passed, 3 skipped** |
| **Total** | **706 passed + 28 gated-skipped** |

The 28 skips are live integration tests, gated behind per-runtime environment
flags (`URML_ROS2_INTEGRATION` / `URML_GAZEBO_E2E` / `URML_PX4_SITL` /
`URML_OPCUA_INTEGRATION` / `URML_COBOT_INTEGRATION` / `URML_MUJOCO_INTEGRATION`
/ `URML_EMBEDDED_INTEGRATION` / `URML_EDU_INTEGRATION` /
`URML_ISAAC_INTEGRATION` / `URML_AUTOSAR_INTEGRATION`, plus the industrial-arm
sim flag) — no rclpy/sim/SITL/vendor-SDK on a dev box. They are *run* by the
gated CI workflows (`*-integration.yml`, workflow_dispatch + weekly cron), each
of which carries a top-of-file honesty note: the first run of any live e2e is a
calibration run, not a regression signal.

Conformance fixtures: **89** YAML cases under `conformance/fixtures/` — drone
14, home 18, industrial 40, biped 5, quadruped 4, mobile 2, marine 1,
educational 4, research 1. Auto-discovered; all pass hermetically against
`MockROSAdapter`.

## Per-row backing

**Five-pass static validator — 242 unit tests.**
`reference/validator/src/urml_validator/validator.py` (`validate()` runs Pass
1–5); `errors.py` `ErrorCode` namespaces. Pass 3 geofence / 3D-altitude /
people-occupancy; Pass 4 cross-primitive type check. Evidence: validator suite
242 passed.

**20 primitives — validator + reference-runtime executors for all 20.** The 12
core plus 8 profile-extensions (home `speak`/`listen`, drone `take_off`/`land`/
`return_to_home`, industrial `pick_from`/`place_at`/`swap_tool`, RFC-0013).
Still exactly 20: tracks A–G added **no** primitive. RFC-0015 (`call_program`),
RFC-0017 (`set_output`), and RFC-0020's proposed `plan_path`/`follow_trajectory`
are **Draft proposals**, surfaced honestly by the runtime spec-gap loops, not
shipped. Evidence: `PRIMITIVE_MODELS` has 20 entries; industrial-primitive e2e
tests; `industrial/04–08` + `industrial/24` conformance fixtures.

**Compliance enforcement — `--no-policy` opt-out.**
`reference/validator/src/urml_validator/policy.py` + bundled default policy
(RFC-0004). Evidence: validator-suite policy tests; **fifteen** compliant-part
manifests (Track C: schunk / piab / onrobot / soft_robotics / ati / cognex /
sick; Track I-C: robotiq / schmalz / festo / bota / hokuyo / ouster / photoneo /
zivid), **sixteen** industrial-arm-brand manifests (Tracks A + I-A:
kawasaki / staubli / comau / mitsubishi / denso / hyundai / nachi / epson /
omron / hanwha, plus the original abb / fanuc / kuka / yaskawa / ur / franka),
and **eight** zero-ROS cobot manifests (Tracks B + I-B: doosan / techman /
kinova / mecademic / neura / kassow, plus the original ur / franka) are all
ACCEPTED; `unitree_quadruped_denied` / `hesai_lidar_denied` /
`turtlebot4_home_dji_vendor` remain rejected. All exercised by the conformance
suite.

**LLM bridge — 77 unit tests.**
`reference/llm-bridge/` — provider-agnostic (anthropic, openai, echo);
revision loop with `BridgePolicyViolation` short-circuit. Evidence: llm-bridge
77 passed.

**Conformance suite — 89 fixtures, `urml conformance run`, and a normative
runtime contract.** `conformance/fixtures/**/*.yaml` = 89 cases.
[RFC-0014](../rfcs/0014-substrate-conformance.md) defines, normatively, what
makes a runtime URML-compatible (manifest intake, the frozen substrate
Protocol, validate-before-actuate, offline, the zero-ROS acid test, the
spec-gap loop). Evidence: conformance 97 passed (parametrized over the 89
fixtures + loader/registry/smoke).

**CLI — seven subcommands.** `urml --help` →
`validate execute schema translate emit-prompt init conformance`.

**Mock reference runtime.** `reference/ros2-runtime/.../substrate/mock.py`
(`MockROSAdapter`). Default substrate for every hermetic suite.

**Real ROS 2 adapter (`RclpyAdapter`) — end-to-end verified, job-level green
×3.** `reference/ros2-runtime/.../substrate/rclpy_adapter.py` (full Protocol,
lazy `rclpy`). End-to-end: the `home/nav_patrol_positive` fixture through
`ConformanceRunner` with a live `RclpyAdapter` driving a TurtleBot 4 + Nav2
Gazebo sim. The proving job is **`gazebo-e2e`** in
`.github/workflows/ros2-integration.yml`; it passed on three runs —
**25953413044, 25953936578, 25954097635**. Honest detail a skeptic will hit:
on the first two of those runs the *workflow badge is red* because the
unrelated, pre-calibration `rclpy-smoke` job failed (fixed in #45); only run
**25954097635** is green at the workflow level. The claim is "the adapter's
proving job is green ×3," verifiable with `gh run view <id> --json jobs`, not
"the workflow is green ×3."

**PX4 / MAVLink reference runtime (`PX4Adapter`) — 54 tests, zero ROS.**
`reference/px4-runtime/` — full Protocol via `pymavlink`. Evidence: 54 passed,
4 skipped (gated SITL/live).

**PX4 SITL end-to-end — gated, NOT yet calibrated.** Unchanged honest status:
`px4-sitl-e2e` in `px4-integration.yml` has not been executed; its first run
is the calibration run. No green run is claimed.

**CompositeAdapter.** `reference/px4-runtime/.../composite.py` — per-method
routing across a flight + companion backend. Evidence: px4-runtime suite.

**Twelve further reference runtimes — hermetic-tested, live CI gated (no
hardware claim).** Beyond ROS 2 and PX4, `main` ships:
`marine-runtime` (BlueROV2/ArduSub MAVLink), `industrial-arm-runtime`
(16 brand adapters across ROS-Industrial + MoveIt 2: ABB / FANUC / KUKA /
YASKAWA / UR / Franka / Kawasaki / Stäubli / Comau / Mitsubishi Electric /
Denso / Hyundai / Nachi / Epson / Omron / Hanwha), `legged-runtime`
(Spot/ANYmal), `humanoid-runtime` (Digit), `mobile-runtime` (Husky/Jackal),
`opcua-runtime` (OPC UA Robotics, RFC-0015/0016 spec-gaps), `cobot-runtime`
(8 brand adapters via native SDKs: UR RTDE, Franka FCI, Doosan DRFL, Techman
TMflow, Kinova Kortex, Mecademic mecademicpy, Neura neurapy, Kassow kassow-py;
RFC-0017 spec-gap), `mujoco-runtime` (simulator — pure Protocol proof),
`embedded-runtime` (micro:bit/Arduino over serial; RFC-0018 spec-gap),
`edu-runtime` (VEX V5, LEGO SPIKE via Pybricks, Thymio via Aseba TDM —
RFC-0011 educational flywheel), `isaac-runtime` (NVIDIA Isaac Sim/Lab — local
RTX/Omniverse host, **not** cloud), `autosar-runtime` (AUTOSAR Adaptive
scaffold, RFC-0019 Draft). **Honest scope:** each ships a hermetic unit suite
that passes today (counts in the table above; vendor SDKs are lazy, so suites
run with the SDK absent) and a gated `*-integration.yml` whose live e2e is an
explicit calibration placeholder that fails loudly until wired — exactly the
PX4-SITL posture. These prove *our code* across the substrate set and the
zero-ROS acid test (RFC-0014); they are **not** hardware-verification claims.
Each carries a `SPEC-GAPS.md` recording anything the substrate needed that
URML cannot express, promoted to a Draft RFC (0015/0016/0017/0018/0019/0020)
rather than silently bolted on.

**Autoware AV — manifest+spec only (RFC-0020 Draft).** The
`autoware_av_research` manifest validates under the existing `research`
profile; there is **no** `reference/autoware-runtime/` package. RFC-0020
proposes two new primitives (`plan_path`, `follow_trajectory`) and an `av`
profile + hd_map/odd/mrm manifest blocks — none ratified, so this follows the
no-SDK-humanoid precedent (Optimus/Figure/Apollo/NEO/Ghost). A green adapter
will land only after RFC-0020 + the new primitives ratify.

**RFCs 0001–0020.** `docs/rfcs/`. States are tracked per-RFC header
(RFC-0001 §Lifecycle is authoritative). 0015/0016/0017/0018 are the Drafts
the substrate work surfaced; 0014 (substrate conformance) defines the runtime
contract above; 0019 (AUTOSAR binding) and 0020 (Autoware AV substrate) are
the latest Drafts. No primitive or schema changed without an accepted RFC.

## Re-running this audit

```bash
# Per-package, with PYTHONPATH set to the package src plus
# reference/validator/src, reference/ros2-runtime/src,
# reference/px4-runtime/src, conformance/src.
python -m pytest <pkg>/tests -q --tb=no --junit-xml=j.xml
python -c "import xml.etree.ElementTree as E;print(E.parse('j.xml').getroot().find('testsuite').attrib)"
python -m pytest conformance/tests -q --tb=no --junit-xml=c.xml
find conformance/fixtures -name '*.yaml' | wc -l    # fixtures (89)
ls docs/rfcs/ | grep -E '^00[0-2][0-9]'              # RFCs (exclude 0000-template)
urml --help                                           # subcommands
```

Update the date and any moved numbers here and in the README table together —
they are a pair. Numbers without this audit are not allowed on the front page.
