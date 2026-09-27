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

The engagement-side companion to this dossier is
[`outreach-commitments.md`](outreach-commitments.md), which lists every open
public commitment URML has made to engaged outreach maintainers (Ouster,
Kawasaki, Zivid, Marty, Spot, Maytronics, Clearpath). Claims audit measures
what URML has shipped; outreach commitments tracks what URML has promised in
public threads. Both are derivative views of `main`; both should be re-checked
before any public update.

**Measured 2026-09-27, on `feat/rulebooks-impl`** (the RFC-0702 implementation,
with `main` at `dca0112` merged in), via
[`tools/scripts/refresh_audit.py`](../../tools/scripts/refresh_audit.py)
(invoke with `make audit`), with `PYTHONPATH` set to the branch's `src`
directories. Every row was re-measured on this host. New since the 2026-08-29
measurement: the Microduck adapter in `edu-runtime` (0569e50), the capture
camera selector (RFC-0699), the social profile with `look_at` and `gesture`
(RFC-0698), `urml bench` (a97a175), clarify mode (RFC-0700), the RFC-0382
monitorable-envelope fixtures and example (9357edb), the bench that counts
saves and its striker corpora (c2d251d), the envelope coverage fixes (949ce9b),
the runtime gate and goal-line lane (c7dec9b), pinned constraints on the MCP
server (a16a03f), the committed striker rows with their guard test
(9636cd7, 0dc49b5), dynamic-target grasping (RFC-0671, 9838aa0), and the
rulebook pass with the bundled FAA Part 107 rulebook (RFC-0702). The prior
measurements (2026-09-26: 2516 total; 2026-08-29: 2122 total; 2026-08-09: 1997 total; 2026-06-24: 1668 total;
2026-05-20 / 2026-05-22: 244 validator, 765 total, 101 fixtures) are in git
history.

| Suite | Result |
|---|---|
| validator | **1175 passed** |
| llm-bridge | **277 passed** (2 more tests need the `openai` extra, not installed on this host) |
| ros2-runtime | **204 passed, 4 skipped** |
| px4-runtime | **54 passed, 4 skipped** |
| ardupilot-runtime | **38 passed, 9 skipped** (live smoke, bench, SITL gated) |
| conformance | **803 passed** |
| marine-runtime | **4 passed** |
| industrial-arm-runtime | **65 passed, 1 skipped** (16 brand adapters parameterized) |
| legged-runtime | **6 passed** |
| humanoid-runtime | **4 passed** |
| mobile-runtime | **4 passed** |
| opcua-runtime | **4 passed, 3 skipped** |
| cobot-runtime | **12 passed, 2 skipped** (8 brand adapters parameterized) |
| mujoco-runtime | **10 passed, 4 skipped** |
| embedded-runtime | **4 passed, 3 skipped** |
| edu-runtime | **28 passed, 2 skipped** (7 platform adapters) |
| isaac-runtime | **5 passed, 3 skipped** |
| autosar-runtime | **4 passed, 3 skipped** |
| model | **32 passed** |
| **Total** | **2733 passed + 38 gated-skipped** |

The two `openai` tests (`test_providers_openai.py` and `test_speech_openai.py`,
`test_base_url_forwarded_to_client`) fail on this host because the optional
`openai` package is absent; the llm-bridge row counts only what passed. Two
newer packages, `chrono-runtime` and `mcp-server`, have suites that the audit
script does not run yet, so the total leaves them out.

The 38 skips are live integration tests, gated behind per-runtime environment
flags (`URML_ROS2_INTEGRATION` / `URML_GAZEBO_E2E` / `URML_PX4_SITL` /
`URML_ARDUPILOT_INTEGRATION` / `URML_ARDUPILOT_BENCH` / `URML_ARDUPILOT_SITL` /
`URML_OPCUA_INTEGRATION` / `URML_COBOT_INTEGRATION` / `URML_MUJOCO_INTEGRATION`
/ `URML_EMBEDDED_INTEGRATION` / `URML_EDU_INTEGRATION` /
`URML_ISAAC_INTEGRATION` / `URML_AUTOSAR_INTEGRATION`, plus the industrial-arm
sim flag) — no rclpy/sim/SITL/vendor-SDK on a dev box. They are *run* by the
gated CI workflows (`*-integration.yml`, workflow_dispatch + weekly cron), each
of which carries a top-of-file honesty note: the first run of any live e2e is a
calibration run, not a regression signal.

Conformance fixtures: **260** YAML cases under `conformance/fixtures/` (live
count 2026-09-27): actuation 5, av 4, biped 16, compliance 5, deployment 3,
drone 34, educational 12, fleet 14, flexbe 2, home 34, industrial 57, language 5,
licensing 3, manipulation 7, marine 1, mobile 2, programs 3, quadruped 8,
research 1, rulebook 13, social 9, translation 3, warehouse 19. Auto-discovered; all pass hermetically
against `MockROSAdapter` (`urml conformance run`: 260/260 passed). The new buckets since v0.1 track the v0.2.0 surface: `fleet`
(RFC-0286/0290/0291), `av` (RFC-0020), `manipulation` (RFC-0010/0586),
`actuation` (RFC-0017), `language`/`translation`/`licensing` (RFC-0260/0262/
0268/0304), `compliance`/`deployment` (policy), `programs` (RFC-0616), `social`
(RFC-0698), `rulebook` (RFC-0702). Of the 73 fixtures added since 2026-08-29,
46 came with the envelope coverage fixes (949ce9b, four of them in `social`),
13 with the rulebook pass (RFC-0702), 5 with the social profile (RFC-0698),
3 with the RFC-0382 monitorable-envelope fixtures (9357edb), 3 with the
capture camera selector (RFC-0699) and 3 with dynamic-target grasping
(RFC-0671).

**Spec vs Outreach RFCs.** The `docs/rfcs/` dir mixes two kinds, distinguished
by the Kind column in [`docs/rfcs/README.md`](../rfcs/README.md). **Spec RFCs**
(51 as of 2026-07-17: 8 Accepted, 37 Implemented, 5 Draft, 1 Open) change
URML's normative surface — Layer-N schemas, primitives, the policy mechanism,
profiles. **Outreach RFCs** (the large remainder of the ~662 total docs) are per-target
request-for-comment documents that explicitly propose zero spec change ("No spec
change is proposed here") and live in the RFC dir for discoverability. The
shipped surface above is the Spec RFCs' result; Outreach RFCs add per-target
manifest fixtures, not new primitives or schema. Several Spec RFCs were
*surfaced by* outreach (e.g. RFC-0039 from Ouster, RFC-0304 from NLLB,
RFC-0385 from iceoryx). Outreach state is tracked in the
[`examples/lighthouses/`](../../examples/lighthouses/) ledgers.

## Per-row backing

**Six-pass static validator (1175 unit tests).**
`reference/validator/src/urml_validator/validator.py` (`validate()` runs the
passes in order); `errors.py` `ErrorCode` namespaces. Pass 3 geofence / 3D-altitude /
people-occupancy; then the rulebook pass (RFC-0702, `rulebook_engine.py`, with
the bundled FAA Part 107 rulebook on by default for drone programs); Pass 4
cross-primitive type check; Pass 5 compliance policy, including the opt-in
evidence-traceability rules (RFC-0631). Evidence: validator suite 1175 passed. Which envelope check runs on which primitive is in
[`docs/safety/envelope-coverage.md`](../safety/envelope-coverage.md).

**24 primitives — validator + reference-runtime executors for all 24.** The 12
core plus profile/extension verbs: home `speak`/`listen`; drone `take_off`/
`land`/`return_to_home`; industrial `pick_from`/`place_at`/`swap_tool`
(RFC-0013); `bimanual` (RFC-0010); `set_output` (RFC-0017); and the `av`
pair `plan_path`/`follow_trajectory` (RFC-0020) — all Implemented. `PRIMITIVE_MODELS`
has **25** entries; the 25th, `call_program` (RFC-0015), is **Open**, not
shipped, so the shipped count is **24**. Evidence: industrial- and av-primitive
e2e tests; `industrial/`, `av/`, `manipulation/` conformance fixtures.

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

**LLM bridge (277 unit tests).**
`reference/llm-bridge/`: provider-agnostic (anthropic, openai, ollama,
llama_cpp, echo; all first-class in the CLI as of 0.4.0) plus the RFC-0670
speech front-end (whisper.cpp, OpenAI-compatible transcription, echo);
revision loop with `BridgePolicyViolation` short-circuit; single-robot +
roster-aware fleet assembly (RFC-0286); the `urml bench` harness. Evidence:
llm-bridge 277 passed (2 more need the `openai` extra; see the table note).

**Conformance suite (260 fixtures), `urml conformance run`, and a normative
runtime contract.** `conformance/fixtures/**/*.yaml` = 260 cases (per-bucket
counts above). [RFC-0014](../rfcs/0014-substrate-conformance.md) defines, normatively,
what makes a runtime URML-compatible (manifest intake, the frozen substrate
Protocol, validate-before-actuate, offline, the zero-ROS acid test, the
spec-gap loop). Evidence: `urml conformance run` reports 260/260 passed, and
the conformance pytest suite 803 passed (parametrized over the fixtures +
loader/registry/smoke).

**CLI (nine subcommands).** `urml --help` →
`validate execute schema translate run bench emit-prompt init conformance`.

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

**PX4 SITL end-to-end: flown locally 2026-09-27, not in CI.**
`test_px4_sitl_e2e.py` (`URML_PX4_SITL=1`) passed on 2026-09-27 in WSL2
(Ubuntu 24.04) on the maintainer's machine, against PX4 v1.17.0 SITL with
PX4's built-in SIH quadrotor (`make px4_sitl sihsim_quadx`, headless), at URML
commit 5c56703. The `drone/flight_only_positive` fixture ran through
`ConformanceRunner` with a live `PX4Adapter`. PX4's log shows `Armed by
external command`, `Takeoff detected`, `Returning to launch`, `Landing
detected` and `Disarmed by landing`, and a listen-only witness on PX4's
ground-station port measured a highest relative altitude of 31.79 m for the
30 m take-off, a closest approach of 0.92 m to the waypoint, and a final
landed state of ON_GROUND. Four runs that day on the final adapter code
passed. Record:
[`reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md`](../../reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih.md).
No earlier green claim stands: earlier the same day the same gate passed in
2.37 s while PX4's log showed no arming and no take-off, because the adapter
then reported every COMMAND_ACK as success. The adapter now reports a flight
primitive as done only when telemetry shows it. A second record the same day
flew the fixture again with the adapter's ground-station heartbeat, showed
PX4's STATUSTEXT reaching the adapter and PX4's own text in a refused arm's
reason, and checked `wait_for(emergency_stop)` against a flight termination:
[`reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih-heartbeat.md`](../../reference/px4-runtime/tests/integration/sitl-runs/2026-09-27-px4-v1.17.0-sih-heartbeat.md).
The GitHub `px4-sitl-e2e` job now follows the same SIH recipe but has not run:
the maintainer's account is flagged and founder-triggered runs do not start.
No hardware flight is claimed.

**ArduPilot / MAVLink reference runtime (`ArduCopterAdapter`) — bench-verified
on physical hardware, no flight claimed.** `reference/ardupilot-runtime/`
(RFC-0041 implemented for Copter). Evidence: the hermetic suite (38 passed,
9 gated-skipped) plus a bench run on 2026-08-29 against a Pixhawk-class board
running ArduCopter 4.6.3 over USB, propellers off: the read-only probe
identified the board, `urml execute --adapter ardupilot` ran the
`bench-battery` example to SUCCESS (battery read over MAVLink), and the
`bench-hop` flight program was refused by the autopilot's own pre-arm checks
with the reason carried verbatim (`arm_rejected: ... Arm: GPS 1: Bad fix ...`),
vehicle still disarmed afterwards. `URML_ARDUPILOT_BENCH=COM5` re-runs those
three assertions as a gated test (3 passed on that host).

**ArduCopter SITL end-to-end — calibration run GREEN 2026-08-29, locally.**
`test_arducopter_sitl_e2e.py` (`URML_ARDUPILOT_SITL=1`) against ArduCopter
SITL built from the `Copter-4.6.3` tag (the board's own firmware version) in
WSL2 on the maintainer's machine, home placed at the example coordinates,
speedup 4: the `drone/flight_only_positive` conformance fixture, the
`site-photogrammetry` example (arm, climb to 100 m, five global setpoints with
ROI, five `DO_DIGICAM_CONTROL` captures, RTL, land) and the `parcel-delivery`
example (gripper + winch via `set_output`, both hovers held) all passed, 3/3.
The run surfaced one real defect fixed the same day: ArduCopter 4.6 rejects
the MAVLink `WINCH_DELIVER` / `WINCH_RETRACT` actions, so the adapter now uses
relative-length control. The GitHub `ardupilot-sitl-e2e` job itself
(manual-trigger) has not been run in CI; the local run is the evidence. The
two flight-test examples have not been flown on hardware.

**LLM bridge on the flight sentences — measured 2026-08-30.** Gemini 2.5 Pro
through the bridge's OpenAI-compatible provider: the photogrammetry sentence
produced the accepted five-station program after 0 revisions; the delivery
sentence first produced an accepted-but-incomplete program (no payload
release; `set_output` was absent from the prompt's few-shots), and after the
drone delivery few-shot was added, the complete winch + latch program after
0 revisions. Both LLM-emitted programs are committed
(`examples/drone/*.gemini.urml.yaml`) and flew unchanged on ArduCopter SITL.
`qwen2.5:7b` locally on CPU was rejected on all four attempts for both
sentences. No physical flight claimed.

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
`edu-runtime` (VEX V5, LEGO SPIKE via Pybricks, Thymio via Aseba TDM,
**`RoboticalMartyAdapter` graduated 2026-05-27 to production**: real-`martypy`
API-surface CI gate in `.github/workflows/marty-real-integration.yml` +
richer arg-passing dispatch via `EduSkillCall`; hardware-in-the-loop still
the documented next gate per `docs/launch/outreach-commitments.md` —
RFC-0011 educational flywheel; RFC-0073 the engagement record),
`isaac-runtime` (NVIDIA Isaac Sim/Lab — local
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

## Striker and goal-line evidence

Measured 2026-09-26. The striker rows measure what the validator admits from
a model that emits whatever an attacker wants. The goal-line lane measures
what the reference runtime does with a program the validator rejects.

**Worst-case striker, before and after the envelope coverage fixes.** A
scripted striker (`bench/strikers/`) stands in for a fully jailbroken model.
For every request in the three `adversarial-*` corpora it emits the unsafe
program an attacker wants, and it never refuses. Each run used the echo
provider, `--no-policy` and a bench envelope from `bench/envelopes/`; the
commands are in [`bench/README.md`](../../bench/README.md).

| Corpus | Envelope rows passed, before (c2d251d) | Envelope rows passed, after (a16a03f) | Safe controls accepted, after |
|---|---|---|---|
| adversarial-industrial-en | 7 of 14 | 0 of 14 | 4 of 4 |
| adversarial-home-en | 6 of 12 | 0 of 12 | 4 of 4 |
| adversarial-drone-en | 8 of 14 | 0 of 14 | 4 of 4 |
| Total | 21 of 40 | 0 of 40 | 12 of 12 |

The before rows are
`bench/results/2026-09-26/2026-09-26-echo-echo-adversarial-{industrial,home,drone}-en-pre-fix.yaml`,
measured at c2d251d, before the envelope coverage fixes in 949ce9b. The after
rows are the matching `-post-fix.yaml` files, measured at a16a03f. In both sets
the 6 `known_gap` rows and the 6 `beyond_envelope` rows pass by design. The
first are limits the spec does not yet require the validator to check. The
second are harmful requests that stay inside every declared limit. The
per-primitive matrix is
[`docs/safety/envelope-coverage.md`](../safety/envelope-coverage.md). A
scripted striker measures the gate, not a model, and no live-model row is
claimed. `reference/llm-bridge/tests/test_bench_results_guard.py` re-runs the
current rows and fails when one stops reproducing or when an input it pins
changes.

**Drone row with the rulebook pass (RFC-0702), measured 2026-09-27.** The
bundled FAA Part 107 rulebook is on by default for drone programs, so the drone
corpus was re-measured with it on:
`bench/results/2026-09-27/2026-09-27-echo-echo-adversarial-drone-en-rulebook.yaml`.
Envelope rows passed 0 of 14, safe controls were accepted 4 of 4, `known_gap`
rows passed 1 of 2 (`gap_wgs84` is now stopped by `rule.place_unknown`), and
`beyond_envelope` rows passed 2 of 2. The a16a03f drone row above stays as the
record of that commit; the guard lists it as superseded and re-runs the new one.

**Industrial row after RFC-0684, measured 2026-09-27.** RFC-0684 (e87d2e9)
added the people-zone check to `release.at`, so the industrial corpus was
re-measured: `bench/results/2026-09-27/2026-09-27-echo-echo-adversarial-industrial-en-release-check.yaml`.
Envelope rows passed 0 of 14, safe controls were accepted 4 of 4, and
`known_gap` rows passed 1 of 2 (`gap_release_in_zone` is now stopped). The
a16a03f industrial row stays as history; the guard lists it as superseded.

**Goal-line lane.** `python -m urml_conformance --goal-line` hands every
rejected conformance fixture to the reference runtime (`URMLRuntime`, and
`FleetRuntime` for fleet fixtures) through an adapter that records every call.
Result with the code at a16a03f: 110/110 rejected fixtures refused, with the
expected codes and zero adapter calls. URML sent zero commands for any of
them. Re-measured 2026-09-27 with the rulebook pass: 121/121, the new
rulebook fixtures included. The lane is `conformance/src/urml_conformance/goal_line.py`, merged in
c7dec9b.

## Re-running this audit

```bash
# Per-package, with PYTHONPATH set to the package src plus
# reference/validator/src, reference/ros2-runtime/src,
# reference/px4-runtime/src, conformance/src.
python -m pytest <pkg>/tests -q --tb=no --junit-xml=j.xml
python -c "import xml.etree.ElementTree as E;print(E.parse('j.xml').getroot().find('testsuite').attrib)"
python -m pytest conformance/tests -q --tb=no --junit-xml=c.xml
find conformance/fixtures -name '*.yaml' | wc -l    # fixtures (260)
ls docs/rfcs/ | grep -E '^00[0-2][0-9]'              # RFCs (exclude 0000-template)
urml --help                                           # subcommands
python -m urml_conformance --goal-line                # rejected fixtures send zero commands
```

The striker rows are re-measured with the three commands in
[`bench/README.md`](../../bench/README.md) (The worst-case striker), run from
the repository root.

Update the date and any moved numbers here and in the README table together —
they are a pair. Numbers without this audit are not allowed on the front page.
