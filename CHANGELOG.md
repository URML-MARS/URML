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

# Changelog

All notable changes to URML are recorded in this file.

The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and URML versioning is per-artifact semantic versioning (see [`MANIFESTO.md`](MANIFESTO.md) §License Direction and [`CONTRIBUTING.md`](CONTRIBUTING.md) — each spec layer, profile, and reference implementation versions independently; this top-level changelog records *project-level* milestones).

## [Unreleased]

Nothing pending.

## [0.4.0] — 2026-08-09

Minor release. Everything is backward-compatible: a v0.3.0 manifest, envelope, and program validate and execute unchanged. All 20 Python packages move to 0.4.0 in lockstep, and 0.4.0 is the first version of the family actually uploaded to PyPI (0.2.0 and 0.3.0 were version alignments on `main`; the index still served 0.1.0).

### Added — Speech front-end (RFC-0670)

- `urml translate --audio request.wav` and `urml run --audio request.wav`: speak the request instead of typing it. A `SpeechProvider` protocol mirrors the LLM provider contract, with adapters for whisper.cpp's `whisper-server` (new `[whisper_cpp]` extra, on-device, the default), OpenAI-compatible transcription endpoints (key not required with a base URL), and a hermetic echo provider. The transcript is echoed to stderr and feeds the unchanged translate path, so the validator boundary is untouched. `--speech-language` hints the language for multilingual requests.

### Added — First-class on-prem LLM providers in the CLI

- `urml translate` and `urml run` gain `--provider ollama` and `--provider llama_cpp`, wiring the RFC-0021 on-device adapters (shipped and tested since v0.2) into the CLI. A new `--base-url` flag overrides the local server endpoint for both, and points `--provider openai` at any OpenAI-compatible server (LM Studio, vLLM).
- `OPENAI_API_KEY` is no longer required when a base URL is set via `--base-url` or `OPENAI_BASE_URL`: local servers ignore the key, so the CLI passes a placeholder. Cloud usage without a base URL is unchanged.
- A dead local server now surfaces as one actionable line naming the endpoint and the fix, instead of a raw httpx traceback.

### Notes

- The PyPI publish (TestPyPI rehearsal, then the real index), the `v0.4.0` git tag, the GitHub release, and the README install-line flip are executed by the maintainer after this lands, per `RELEASING.md`.
- New `tools/scripts/bump_version.py`: the lockstep bump is now scripted and checkable (`--check`), replacing the hand-edited 40-file sweeps of 0.2.0 and 0.3.0.

## [0.3.0] — 2026-07-23

Minor release, and the first to version the full package family in lockstep. Everything is backward-compatible: a v0.2.0 manifest, envelope, and program validate and execute unchanged. All 20 Python packages move to 0.3.0 in lockstep.

### Added — Envelope enforcement (RFC-0667)

- Normative satisfaction semantics for the RFC-0382 temporal-logic core over finite timed traces: completed-trace offline evaluation, three-valued online verdicts (satisfied / violated / pending), strong truncation semantics, and the severity mapping (info records, warning audits, critical vetoes).
- `urml_validator.monitor`: the reference trace evaluator (`evaluate_trace`, `OnlineMonitor`, `compile_envelope_monitors`). Static envelope caps (`max_velocity`, `max_grip_force_n`, altitude) now derive to implicit critical `always` properties, so one evaluator covers declared and derived properties alike.
- `urml_ros2_runtime.shield`: the runtime shield. `Shield` gates each dispatch and observes telemetry; `ShieldedAdapter` wraps any substrate adapter so any driver, a URML runtime or an external policy, passes through envelope checks. New optional `TelemetryAdapter` side-protocol; the frozen RFC-0014 adapter contract is untouched. External runtime-verification backends stay first-class through `compile_to_stl`.

### Added — Rehearsal gate and the `urml run` verb (RFC-0668)

- `urml run "<sentence>"`: translate, validate, optionally rehearse in simulation, then execute, in one verb. `--rehearse` is also available on `urml execute`.
- Rehearsal backends: a hermetic synthetic-kinematics backend (CI floor, honest about being kinematics rather than physics) and a MuJoCo per-tick recording adapter with a declared `SignalMap`. A critical violation in the rehearsed trace blocks execution before any real adapter is constructed.
- The README hero now shows the gate live: the same sentence first blocked (envelope speed cap violated under the default motion assumption), then passing under the deployment's declared profile.

### Added — URML-native model pipeline (RFC-0666)

- New package `urml-model` (`reference/model`): mines conformance gold programs and the curated few-shot library, back-translates programs to utterances (deterministic templates in CI, any `LLMProvider` at scale), filters every record through the validator oracle, and exports SFT/DPO training files. Ships the operator-run LoRA training recipe. No weights, no vendor coupling, nothing leaves the repo checkout.

### Added — Agent surface

- `urml-mcp-server` (`reference/mcp-server`): URML's validate-before-actuate loop as Model Context Protocol tools for any MCP-capable agent. The server never calls an LLM; the calling agent emits URML, the server checks and runs it.
- An Agent Skill (`.github/skills/urml-robot-intent`) with a hermetic no-key, no-robot path.

### Added — Specification and manifests

- Per-capability evidence traceability (RFC-0631): capability claims carry `derived` / `verified` / `declared` / `inferred` evidence strength, with an opt-in policy to require the stronger grades.
- Whole-body kinematic structure and stability limits for legged and humanoid platforms (RFC-0384); whole-body and bimanual manipulation (RFC-0010).
- Realtime cyclic-timing manifest block (RFC-0016) and the zero-copy IPC sub-substrate declaration (RFC-0385).
- `drive` radius parameterization (RFC-0665): a radius plus sweep angle pass through without arc-length arithmetic, closing the small-model orbit-2x failure observed in the field.

### Fixed

- GoPiGo3 example runtime converts URML's FLU (+CCW) frame to the platform's RFD (+CW) frame at the hardware boundary (#591, #598, PR #602). URML's first merged external code contribution, found and fixed on real hardware by @slowrunner.

## [0.2.0] — 2026-06-02

Minor release. The first spec-bumping release since v0.1.0: it transcribes the accepted multi-robot fleet RFCs into the normative layer specs, so the specification stops lagging its own accepted decisions. Layers 1, 3, and 4 advance to v0.2.0; Layer 2 is unchanged (still 20 normative primitives). All additions are backward-compatible — a v0.1.0 manifest and a single-robot program validate unchanged.

### Added — Specification

- **Layer 1 (HAL) → v0.2.0.** Three additive, optional items: a frame `transform` (SE(3) pose in the parent frame), a `mobility.clearance` operational volume (lateral footprint + vertical altitude/depth band), and the new §6 fleet `roster` (binds N per-robot manifests by handle; `world_frame`, `shared_frames`, per-member `anchor`s) plus the `validate_fleet` cross-robot checks. RFCs [0286](docs/rfcs/0286-multi-robot-fleet-addressing.md), [0290](docs/rfcs/0290-frame-transform-graph.md), [0291](docs/rfcs/0291-utm-strategic-deconfliction.md). `manifest_version` stays `"0.1"`.
- **Layer 3 (behavior composition) → v0.2.0.** Two additive composition nodes: `on` (scope a subtree to a fleet member) and `barrier` (synchronize members at a rendezvous). RFC [0286](docs/rfcs/0286-multi-robot-fleet-addressing.md).
- **Layer 4 (NL grammar) → v0.2.0.** Roster-aware fleet (multi-member) prompt assembly and a fleet revision loop (`validate_fleet`), emitting `on`/`barrier` programs. RFC [0286](docs/rfcs/0286-multi-robot-fleet-addressing.md).
- **Sensor schema v0.2 reconciled.** The RFC-0039 sensor capability fields (`beam_count`, `channels`, `time_sync_methods`, `rate_hz_max`, `point_cloud` type), already shipped in the Layer-1 doc since v0.1.1, are now carried normatively at v0.2.0. RFC [0039](docs/rfcs/0039-sensor-schema-v0-2-iteration.md).

### Added — Reference implementation

- **Multi-robot fleet vertical slice.** `validate_fleet` (four cross-robot checks plus shared-frame/anchor validation), a concurrent `FleetRuntime`, the courier-to-arm handoff demo, and a fleet conformance lane (`conformance/fixtures/fleet/`, 14 cases covering ground/air/water separation and the engaged-partners choreography). RFCs [0286](docs/rfcs/0286-multi-robot-fleet-addressing.md), [0290](docs/rfcs/0290-frame-transform-graph.md), [0291](docs/rfcs/0291-utm-strategic-deconfliction.md).
- **`urml-edu-runtime`: fourth platform.** `RoboticalMartyAdapter` graduated to production (real-`martypy` API-surface CI gate), joining VEX V5, LEGO SPIKE, and Thymio.

### Notes

- All 17 in-repo packages (5 published on PyPI + 12 in-repo runtimes) bump 0.1.1 → 0.2.0 in lockstep.
- This is **strategic** cross-robot deconfliction: static rejection of plans that would put two robots in one volume at one time, before execution. It is not a live collision-avoidance loop and not a building-scale traffic manager (that is Open-RMF's domain; URML composes above it).
- The PyPI publish, the `v0.2.0` git tag, and the README/Tutorial-01 install-instruction flip follow [`RELEASING.md`](RELEASING.md) and are gated on the maintainer.

## [0.1.1] — 2026-05-26

Patch release. Phase 1 maintenance since v0.1.0: the first outreach-feedback-driven adapter, two committed homepage diagrams with byte-exact guard tests, and the PyPI packaging fix that should have shipped earlier. No spec change (RFC-0039 sensor schema v0.2 remains in **Draft**); no breaking change.

### Added — Reference implementation

- **`urml-edu-runtime`: `RoboticalMartyAdapter`.** New adapter for the Robotical Marty platform, scaffolded in response to early outreach feedback. Conformance fixtures stay hermetic against `MockROSAdapter`. RFC [0073](docs/rfcs/0073-robotical-marty-outreach.md); commit `d516535`.

### Added — Docs & assets

- **Architecture-stack diagram.** Committed, deterministic SVG of the five-layer URML stack at `docs/assets/architecture-stack.svg`, generated by `tools/scripts/gen_architecture_svg.py` and pinned to `docs/architecture.md` by `reference/validator/tests/test_architecture_svg.py`. Same pure-stdlib, byte-exact, CSS-`@keyframes`-only discipline as the README hero. PR [#129](https://github.com/URML-MARS/URML/pull/129).
- **One-intent-many-bodies portability demo.** Committed SVG showing the same URML program executing across multiple substrate adapters, byte-asserted against a live hermetic run. PR [#132](https://github.com/URML-MARS/URML/pull/132).

### Added — Outreach (no spec change)

Seven outreach waves since v0.1.0 (Moves #2 through #8, RFCs 0040–0107, 68 RFCs total). Each is a per-target request-for-comment document explicitly framed "No spec change is proposed here." Per-wave ledgers at `examples/lighthouses/outreach-move{2..8}.yaml`. Aggregate response state across all ledgers at release time: 4 engaged · 2 declined · 1 wontfix · 77 none.

### Fixed

- **`urml-validator`: PyPI upload.** Redundant `force-include` in the package build config was breaking PyPI uploads. Removed. Commit [`1d631b4`](https://github.com/URML-MARS/URML/commit/1d631b4).

### Notes

- All 17 in-repo packages (5 published on PyPI + 12 in-repo runtimes) bump 0.1.0 → 0.1.1 to preserve the alignment policy from v0.1.0. None of the 12 in-repo runtimes ship to PyPI in v0.1.1 either; that follow-up is per-package and tracked separately.
- Layer-1 sensor schema is normative at v0.1.0 still; the v0.2 iteration ([RFC-0039](docs/rfcs/0039-sensor-schema-v0-2-iteration.md)) lands in a future spec-bumping release once Accepted.
- Phase 1 cosmetics on urml.dev shipped in the website repo (separate from this changelog): why-now hook, architecture SVG, audience-segmented CTAs, Phase 0 → Phase 1 chrome refresh ([urml-website#11](https://github.com/URML-MARS/urml-website/pull/11), [#12](https://github.com/URML-MARS/urml-website/pull/12)).

## [0.1.0] — 2026-05-22

First public release. URML moves from Phase 0 (solo-author working in public) to **Phase 1**: `pip install urml-validator` (and four sibling packages) ships, external contributions open per [`CONTRIBUTING.md`](CONTRIBUTING.md). The strategic posture, the Core Commitment, and the substrate-neutrality contract are unchanged from the manifesto; what changes is the gate.

### Added — Specification

- **Layer 1 (HAL).** Capability manifest with provenance, safety envelope, and connectivity / link-loss as a validated safety contract. Normative at v0.1.0. RFCs [0001](docs/rfcs/0001-rfc-process.md), [0002](docs/rfcs/0002-initial-primitive-vocabulary.md), [0006](docs/rfcs/0006-connectivity-and-link-loss.md), [0009](docs/rfcs/0009-legged-humanoid-mobility.md), [0014](docs/rfcs/0014-substrate-conformance.md).
- **Layer 2 (intent primitives).** 20 normative primitives: 12 core (`move_to`, `dock`, `hover`, `wait`, `wait_for`, `grasp`, `release`, `detect`, `scan`, `measure`, `capture`, `report`) plus 8 profile-scoped (`speak`/`listen` home; `take_off`/`land`/`return_to_home` drone; `pick_from`/`place_at`/`swap_tool` industrial). RFCs [0002](docs/rfcs/0002-initial-primitive-vocabulary.md), [0013](docs/rfcs/0013-industrial-layer2-primitives.md).
- **Layer 3 (behavior composition).** `sequence` / `branch` / `parallel` / `retry` + `on_error` (`abort_and_report` / `continue` / `retry`). Normative at v0.1.0.
- **Layer 4 (natural-language bridge).** Provider-agnostic prompt contract, validator-feedback revision loop with policy-error short-circuit, schema-derived GBNF + GGUF contract for on-device models. RFC [0021](docs/rfcs/0021-on-device-llm-bridge.md).
- **Profiles.** home, drone, industrial, educational, research, warehouse — each with its own README, default safety envelope, and conformance fixtures. RFCs [0011](docs/rfcs/0011-educational-profile.md), [0012](docs/rfcs/0012-research-profile.md), [0022](docs/rfcs/0022-warehouse-domain-profile.md).
- **Compliance policy enforcement.** Provenance schema on the manifest, pluggable YAML policy DSL, bundled US-federal default policy aligning with NDAA §889 / FY26, FCC Covered List (effective 2025-12-23), Executive Order 14307, and the American Security Robotics Act once enacted. `--no-policy` opt-out. RFCs [0003](docs/rfcs/0003-us-alignment.md), [0004](docs/rfcs/0004-compliance-policy.md), [0005](docs/rfcs/0005-hbom-parsing.md).
- **Substrate-conformance contract.** What it means for a runtime to be URML-compatible, codified normatively. RFC [0014](docs/rfcs/0014-substrate-conformance.md).

### Added — Reference implementation (PyPI)

Five canonical packages ship on PyPI in v0.1.0:

- [`urml-validator`](reference/validator/) — five-pass static validator (argument typing → capability → safety envelope → variable bindings → compliance policy) and the `urml` CLI with seven subcommands: `validate`, `execute`, `schema`, `translate`, `emit-prompt`, `init`, `conformance run`.
- [`urml-ros2-runtime`](reference/ros2-runtime/) — `MockROSAdapter` (hermetic, zero-dep) plus `RclpyAdapter` against the live ROS 2 graph (Nav2, MoveIt 2, vision_msgs). The `home/nav_patrol_positive` conformance fixture is end-to-end verified ×3 on a TurtleBot 4 + Nav2 + Gazebo Ignition simulation via the gated `gazebo-e2e` CI job — green at the job level on three calibration runs; not a hardware-verification claim.
- [`urml-llm-bridge`](reference/llm-bridge/) — provider-agnostic NL → URML bridge with `Anthropic`, `OpenAI`, hermetic `Echo`, plus on-device `llama_cpp` and `ollama` providers (RFC [0021](docs/rfcs/0021-on-device-llm-bridge.md)). Schema-derived GBNF grammar; GGUF model contract; per-model conformance harness.
- [`urml-px4-runtime`](reference/px4-runtime/) — `PX4Adapter` via `pymavlink` (no ROS dependency); `CompositeAdapter` routes a single URML program across a PX4 flight backend and a ROS 2 companion. Hermetic + gated SITL e2e.
- [`urml-conformance`](conformance/) — 101 declarative YAML fixtures (auto-discovered) across 10 profiles, runnable via `urml conformance run`; the bring-your-own-adapter kit for runtime authors.

### Added — Twelve further reference runtimes (in-repo, not on PyPI in v0.1.0)

Hermetic suites green; live e2e is gated CI (calibration-staged, **not** a hardware claim):

- `marine` (BlueROV2 / ArduSub), `industrial-arm` (16 brand adapters: ABB / FANUC / KUKA / YASKAWA / UR / Franka / Kawasaki / Stäubli / Comau / Mitsubishi / Denso / Hyundai / Nachi / Epson / Omron / Hanwha), `legged` (Spot / ANYmal), `humanoid` (Digit), `mobile` (Husky / Jackal); the zero-ROS `opcua` (OPC UA Robotics) and `cobot` (8 native SDKs: UR / Franka / Doosan / Techman / Kinova / Mecademic / Neura / Kassow); `mujoco` and `isaac` (NVIDIA Sim/Lab, local RTX host) sims; `embedded` (micro:bit / Arduino serial); `edu` (VEX / LEGO SPIKE / Thymio); `autosar` (RFC [0019](docs/rfcs/0019-autosar-adaptive-substrate.md) scaffold). Autoware ships manifest + spec only pending RFC [0020](docs/rfcs/0020-autoware-av-substrate.md). Each is one `pip install -e <path>` away from runnable; PyPI follow-up per package.

### Added — Conformance & lighthouses

- **101 conformance fixtures** under `conformance/fixtures/`, hermetic against `MockROSAdapter`: home 18, drone 14, industrial 44, biped 5, quadruped 4, mobile 2, warehouse 8, marine 1, educational 4, research 1. Auto-discovered.
- **Move #1 lighthouse program.** Per-vendor request-for-comment RFCs to 16 Tier-1 vendors (RFCs [0023](docs/rfcs/0023-yaskawa-motoros2-integration.md)–[0038](docs/rfcs/0038-ros-industrial-consortium.md)): Yaskawa, Universal Robots, KUKA, Stäubli, Mitsubishi MELFA, FANUC, Kawasaki, Denso, SCHUNK, Ouster, SICK, Festo, Zivid, Hokuyo, OSRF / Gazebo Sim, ROS-Industrial Consortium. Per-vendor outreach state tracked in [`examples/lighthouses/outreach.yaml`](examples/lighthouses/outreach.yaml); the parameterized demo runner in `examples/lighthouses/demo.py` exercises any single vendor's conformance fixture hermetically.

### Added — Tooling & developer experience

- `make demo` / `make demo-run` / `make demo-record` / `make audit` / `make test`. The flagship `make demo-run` is the universal-language pitch concretised: one English sentence becomes a validated URML program becomes an executed step-by-step trace, hermetic, any-OS, no API key, no robot. The animated SVG hero in the README is exactly what `make demo-run` prints (every line asserted in CI via [`reference/validator/tests/test_demo_svg.py`](reference/validator/tests/test_demo_svg.py)).
- [`tools/scripts/refresh_audit.py`](tools/scripts/refresh_audit.py) — stdlib-only re-measurer for the front-page numbers; honest about rows the host cannot remeasure; does not auto-edit. `make audit`.

### Added — Process & community

- RFC process (RFC [0001](docs/rfcs/0001-rfc-process.md)): Draft → Open → Accepted → Implemented with a 7-day Phase-0 comment window; 22 Spec RFCs and 16 Outreach RFCs filed and indexed (Kind column distinguishes the two; see [`docs/rfcs/README.md`](docs/rfcs/README.md)).
- Public GitHub Discussions open (Q&A, Ideas, Show-and-tell, Builders & Makers, General) per RFC [0008](docs/rfcs/0008-community-discussions.md).
- Manufacturer go-to-market wedge per RFC [0007](docs/rfcs/0007-manufacturer-go-to-market.md); the live manufacturer / federal-validation surface on [urml.dev](https://urml.dev).
- US-federal regulatory alignment per RFC [0003](docs/rfcs/0003-us-alignment.md). Strategic trade-offs accepted in writing.

### Test surface (claims-audit, measured 2026-05-20 with partial 2026-05-22 re-run)

- **765 passed + 28 gated-skipped** across 16 reference packages.
- Live integration is gated CI (`*-integration.yml`, workflow_dispatch + weekly cron). First run of any live e2e is a calibration baseline, not a regression signal. Backing is recorded in [`docs/launch/claims-audit.md`](docs/launch/claims-audit.md).

### Honest scope (no overclaiming)

- **No physical-hardware verification.** Live e2e is simulated (Gazebo / PX4 SITL) or gated CI calibration. Where the README says "verified," it means the gated CI job was green; that is the load-bearing claim, not a hardware-on-a-bench claim.
- **Compliance enforcement is not legal advice.** The bundled default policy mirrors enacted US federal procurement law as of release date; deployers consult counsel. Disclaimers in [`docs/launch/claims-audit.md`](docs/launch/claims-audit.md) and the bundled policy file.
- **Five canonical packages on PyPI in v0.1.0; the twelve further runtimes follow per-package** as each is ready.
- **One maintainer.** Phase 1 opens external contributions; it does not assert contributors have arrived. The `Status: one person` line in [`GOVERNANCE.md`](GOVERNANCE.md) remains true until it isn't.

---

*Released versions are appended above this line as `[X.Y.Z] — YYYY-MM-DD` sections.*
