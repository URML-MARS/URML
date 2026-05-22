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
