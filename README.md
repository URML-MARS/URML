# URML — Universal Robot Language

A small, opinionated, human-readable language for describing robot **intent**.

URML sits above existing robot operating systems (ROS 2, PX4, OPC UA Robotics, vendor SDKs) and lets humans, large language models, and robots share one vocabulary for *what should happen* — independent of which motors, joints, or frames carry it out. Every URML program is statically verified against the robot's declared capabilities, the active safety envelope, and the deployment's compliance policy **before a single actuator moves**.

URML is a **specification** and a set of **reference implementations**, not a robot operating system. The specification is Apache 2.0 — see [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) for what will always remain so.

---

## Try it in three commands

URML is in Phase 0 (pre-public draft). The reference packages are **not on PyPI yet** (that's a deliberate Phase-1 step); you install them editable from the clone. One script does it on any OS — no namespace claimed, nothing published, fully reversible (`make clean` removes every trace).

```bash
git clone https://github.com/URML-MARS/URML.git && cd URML
python bootstrap.py     # creates .venv, installs all 5 packages editable, in order
make demo               # → Validation passed
```

`make demo` validates the canonical red-mug example through all five passes (argument typing → capability → safety envelope → variable bindings → compliance policy). No make? `bootstrap.py` prints the exact one-line command to run instead. `make help` lists the rest (`install-dev`, `test`, `clean`).

Then scaffold your own project:

```bash
. .venv/bin/activate                  # Windows: .venv\Scripts\activate
urml init my-robot --profile home && cd my-robot
urml validate program.urml.yaml \
    --manifest manifest.yaml --envelope envelope.yaml --profile home
```

`--profile home`, `--profile drone`, and `--profile industrial` are all supported by `urml init`; `--policy` and `--no-policy` flags control the compliance pass.

See [`docs/demos/compliance-walkthrough.md`](docs/demos/compliance-walkthrough.md) for a 90-second walkthrough that shows the compliance pass rejecting a covered-foreign-country component manifest, and the override path.

---

## What URML gives you

| Capability | State |
|---|---|
| **Five-pass static validator** — argument typing, capability checks against a manifest, safety-envelope tightening, variable-binding analysis, compliance policy | ✅ Implemented, 134 unit tests |
| **17 primitives** — the 12 core (`move_to`, `dock`, `hover`, `wait`, `wait_for`, `grasp`, `release`, `detect`, `scan`, `measure`, `capture`, `report`) plus 5 profile-extensions across home (`speak`, `listen`) and drone (`take_off`, `land`, `return_to_home`) | ✅ Validator + home runtime; drone runtime is a near-term follow-up |
| **Compliance enforcement** — provenance schema on the manifest, a pluggable YAML policy DSL, and a bundled US-federal default policy (NDAA §889 / FY26, FCC Covered List, EO 14307, ASRA) | ✅ Implemented; `--no-policy` opt-out |
| **LLM bridge** — provider-agnostic (Anthropic + OpenAI shipped; EchoProvider for tests); revision loop with policy-error short-circuit | ✅ 67 unit tests |
| **Conformance suite** — declarative YAML fixtures any URML-compatible runtime must pass | ✅ 24 fixtures (home + drone + compliance + policy-override) |
| **CLI** — `urml validate`, `urml schema`, `urml translate`, `urml emit-prompt`, `urml init` | ✅ All five subcommands |
| **Mock reference runtime** — hermetic execution without a robot, used by the conformance suite | ✅ Implemented |
| **Real ROS 2 adapter** — production-grade rclpy adapter | ⏳ Phase 1+ |
| **PX4 reference runtime** — second reference runtime, targets the drone profile | ⏳ Phase 2 |

---

## Regulatory alignment

URML's default validator policy aligns with **United States federal robotics and uncrewed-systems regulation**:

- NDAA Section 889 and FY26 NDAA procurement restrictions
- FCC Covered List (DJI, Autel, etc.) effective 2025-12-23
- Executive Order 14307 ("Unleashing American Drone Dominance")
- The American Security Robotics Act once enacted

Deployments outside the US can override the default with `urml validate --policy <file.yaml>`, or disable the compliance pass entirely with `--no-policy`. The mechanism is regulation-neutral; the bundled default is US-aligned by design.

See [RFC-0003](docs/rfcs/0003-us-alignment.md) for the strategic decision and trade-offs accepted; [RFC-0004](docs/rfcs/0004-compliance-policy.md) for the technical mechanism; [`spec/layer-1-hal/policy.md`](spec/layer-1-hal/policy.md) for the normative policy file format.

---

## Architecture in one diagram

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 4: Natural Language → URML                                 │
│  LLM bridge: provider-agnostic, prompt contract, revision loop    │
├──────────────────────────────────────────────────────────────────┤
│  Layer 3: Behavior Composition                                    │
│  sequence · branch · parallel · retry · on_error                  │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2: Intent Primitives                                       │
│  12 core + home (speak / listen) + drone (take_off / land / RTH)  │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1: Hardware Abstraction Layer                              │
│  capability manifest + provenance + safety envelope               │
├──────────────────────────────────────────────────────────────────┤
│  Layer 0: Substrate (NOT part of URML)                            │
│  ROS 2 · PX4 / MAVLink · OPC UA · KUKA · ABB · IEC 61131-3 · ...  │
└──────────────────────────────────────────────────────────────────┘

  Validation pipeline (runs before any actuator):
  Pass 1 → Pass 2 → Pass 3 → Pass 4 → Pass 5
  args     caps      envelope binding   compliance policy
```

---

## Status

**Phase 0** — pre-public draft, solo author working in public. The artifact under review is the manifesto itself plus the implementation that backs it. Direct code contributions open in Phase 1 (see [`GOVERNANCE.md`](GOVERNANCE.md) for the phased plan).

What works today is what the table above lists as `✅`. What's planned is in [`MANIFESTO.md`](MANIFESTO.md) §Roadmap Snapshot. The decision history is in [`docs/rfcs/`](docs/rfcs/); five RFCs are filed as of this writing.

---

## Start here

| You want to... | Read this |
|---|---|
| Get URML running in under an hour | [Tutorial 1: Getting started](docs/tutorials/01-getting-started.md) |
| See compliance enforcement in action | [Compliance walkthrough](docs/demos/compliance-walkthrough.md) |
| Understand the strategic case | [`MANIFESTO.md`](MANIFESTO.md) |
| Understand the design decisions | [`docs/rfcs/`](docs/rfcs/) (RFC-0002 for primitives; 0003 for US alignment; 0004 for compliance) |
| Write a URML program | [Tutorial 2: Anatomy of a URML program](docs/tutorials/02-anatomy-of-a-program.md) |
| Author a capability manifest | [Tutorial 4: Writing your own manifest](docs/tutorials/04-writing-your-own-manifest.md) |
| Connect URML to an LLM | [Tutorial 3: Natural language to URML](docs/tutorials/03-natural-language-to-urml.md) |
| Understand governance and the open-source posture | [`GOVERNANCE.md`](GOVERNANCE.md), [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) |
| Contribute (Phase 1+) | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Report a security issue | [`SECURITY.md`](SECURITY.md) |

---

## Engagement

For the duration of Phase 0, the artifact under review is the manifesto and the v0.1 implementation. The author welcomes critique of the primitive vocabulary, the layer boundaries, the strategic posture, pointers to prior art, and use cases that strain the current architecture.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to reach the author.

---

## License

Apache License 2.0. See [`LICENSE`](LICENSE). Contributions require a [Developer Certificate of Origin](DCO) sign-off — `git commit -s` adds the required line. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the engagement details and [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) for what stays Apache 2.0 forever.

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md) Code of Conduct.
