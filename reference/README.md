# URML Reference Implementations

This directory holds the **reference implementations** maintained by the URML organization. They exist for three reasons:

1. **To prove the specification is implementable.** A spec that no one has implemented is a hope, not a contract. Every primitive that lands in the core ships with at least one reference implementation.
2. **To give first-time integrators a working starting point.** A robot maker building a URML-compatible runtime has an Apache 2.0 codebase to read, fork, or take as inspiration.
3. **To anchor the conformance suite.** The conformance tests are written against the spec, not the reference runtime — but in practice the reference runtime is the first thing the conformance suite is exercised against, and divergences surface quickly.

## What lives here

| Component | What it is | Phase |
|---|---|---|
| [`ros2-runtime/`](ros2-runtime/) | The first reference runtime. Translates URML programs into ROS 2 actions, services, and topics. C++17 where performance matters, Python for everything else. | Phase 1 |
| [`px4-runtime/`](px4-runtime/) | The second reference runtime; targets the drone profile. Translates URML programs into PX4 / MAVLink commands. | Phase 2 |
| [`validator/`](validator/) | The static verification engine. Checks a URML program against a Layer-1 capability manifest and the active safety envelope before execution. Python; long-running deployments may eventually be backed by a Rust service. | Phase 1 |
| [`llm-bridge/`](llm-bridge/) | Provider-agnostic glue that prompts an LLM with the URML contract, validates the LLM's emission, and surfaces revision feedback when validation fails. | Phase 1 |

## What the Core Commitment says

Every component in this directory is part of the [Core Commitment](../CORE_COMMITMENT.md). That means:

- **Apache 2.0 forever.** No move behind a paywall, no "enterprise edition," no conditional license.
- **No vendor coupling.** The LLM bridge does not embed Anthropic, OpenAI, or any other specific provider. The ROS 2 runtime targets upstream ROS 2; the PX4 runtime targets upstream PX4.
- **Offline-first.** A validated URML program executes fully offline. The reference runtimes do not require cloud connectivity at execution time. Hosted services — fleet management, telemetry, observability — are a separate, commercial concern and live outside this repository.

These are not aspirations. They are commitments. See [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md) for the full statement and the procedure for changing it (extraordinary, by design).

## Language conventions

Per [`CLAUDE.md`](../CLAUDE.md) §Working Conventions, in order of preference:

- **Python** for specifications, validators, tooling, LLM bridge. `mypy --strict`, full PEP 484.
- **C++17** for ROS 2 nodes that need performance. Concepts where reasonable.
- **Rust** for long-running infrastructure (validator service, conformance harness).
- TypeScript / JavaScript is **avoided** in this repository. Web tooling, when it is needed, lives in a separate repository.

## Status

Phase 0. Every subdirectory holds a `README.md` describing what the component will do when it is implemented. None of the implementations exist yet. Substantive code work begins in Phase 1.

## How to add a new reference implementation

Adding a *third-party* runtime does not require touching this directory — anyone can write a URML-compatible runtime under any license and demonstrate conformance via the conformance suite (and, when the trademark program exists, apply for the URML-Certified mark).

Adding a *reference* implementation maintained by the URML organization is a different decision: it expands what the Core Commitment covers. That requires an RFC (RFC-0001 process), and the RFC must include a maintenance commitment — who will keep this code working, against which spec versions, on what cadence. A reference implementation is a long-lived dependency on a real human's time; adding one without a maintenance commitment is rejected.
