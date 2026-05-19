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

# URML Glossary

Working definitions of terms used across the specification, reference implementations, and conformance suite. This file extends [`MANIFESTO.md`](../MANIFESTO.md) Appendix A and is the authoritative entry when a term appears in any URML document without a local definition.

When in doubt about a definition, the precedence order is the same as the rest of the repository (see [`CLAUDE.md`](../CLAUDE.md) §Reference Documents): a layer specification's local definition overrides this glossary; the Manifesto overrides everything.

---

**Behavior** — A complete URML program: a tree (or sequence) of composed primitives expressing what should happen. Behaviors live in Layer 3. They are statically verifiable.

**Capability manifest** — A Layer-1 document that declares what a given robot can do: declared mobility, manipulation, perception, frames, limits. The validator checks every URML program against the target robot's manifest before execution.

**Composition** — How primitives are combined into behaviors. URML defines a small fixed set of composition operators (sequence, branch, parallel, retry, on-error). Composition is bounded and statically checkable — URML is not Turing-complete by design.

**Conformance** — The property of a runtime correctly implementing a given URML specification version. Determined by passing the conformance suite at that version.

**Conformance suite** — The Apache-2.0, freely runnable set of tests that determine whether a runtime is URML-compatible. Part of the Core Commitment.

**Core Commitment** — The list of components URML guarantees to keep under Apache 2.0 in perpetuity: the specification documents, the conformance suite, the ROS 2 and PX4 reference runtimes, the validator, and the LLM prompt contract. See [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md).

**DCO** — Developer Certificate of Origin. The per-commit sign-off URML uses in place of a Contributor License Agreement. See [`DCO`](../DCO) and [`CONTRIBUTING.md`](../CONTRIBUTING.md).

**Domain profile** — See *Profile*.

**Frame** — A coordinate frame, in the URDF / ROS sense. URML reuses standard frame conventions rather than inventing its own.

**Hardware abstraction** — Layer 1. The capability manifest, the safety envelope schema, the frame conventions, and the reuse of URDF/SDF.

**Intent** — What should happen, independent of how. The level URML operates at. `move_to(kitchen)` is intent; a Nav2 action with a planned trajectory is *implementation* of intent.

**Intent primitive** — See *Primitive*.

**Layer** — One of the five horizontal slices of URML. Layer 1 (HAL), Layer 2 (primitives), Layer 3 (composition), Layer 4 (NL interface), plus Layer 0 (substrate, not part of URML). See [`architecture.md`](architecture.md).

**LLM bridge** — The provider-agnostic glue that takes natural language, prompts an LLM with the URML contract and the active robot's capability manifest, validates the LLM's structured output, and surfaces revision feedback when validation fails. Part of the Core Commitment. Lives in [`/reference/llm-bridge`](../reference/llm-bridge/).

**Maintainer** — During Phase 0, the founder. In later phases, a member of the steering committee (Phase 1+) or a working-group lead (Phase 2+). See [`GOVERNANCE.md`](../GOVERNANCE.md).

**Manifest** — Short for *capability manifest*.

**Manifesto** — [`MANIFESTO.md`](../MANIFESTO.md). The constitution of the project; the document the rest of the repo cites when in doubt.

**Phase** — One of the roadmap phases defined in `MANIFESTO.md` §Roadmap Snapshot. Phase 0 is now (months 0–2); Phase 1 begins when external code contributions open.

**Primitive** — An atomic intent verb, defined in Layer 2. Examples: `move_to`, `grasp`, `hover`, `scan`, `detect`, `dock`, `release`. Adding a primitive is a one-way door — once shipped, removing it breaks every downstream user — so the bar for new primitives is deliberately high (see [`CONTRIBUTING.md`](../CONTRIBUTING.md) §Proposing a Layer 2 Primitive).

**Profile** — A domain-specific extension to the core (home, drone, industrial, agricultural, ...). A profile may add primitives, constrain core primitives, and declare a profile-specific safety-envelope class. It may not weaken the core's safety guarantees or break the substrate-neutrality acid test.

**Reference runtime** — An open-source implementation, maintained by URML, that translates URML programs into a specific substrate. The ROS 2 reference runtime is the first; the PX4 reference runtime is the second. Both are part of the Core Commitment.

**RFC** — A numbered proposal in [`docs/rfcs/`](rfcs/) that changes specification semantics. PRs implement RFCs; they don't replace them. Process documented in [`docs/rfcs/0001-rfc-process.md`](rfcs/0001-rfc-process.md).

**Runtime** — An implementation that translates URML programs into substrate-specific commands. May be a URML reference runtime or a third-party runtime.

**Safety envelope** — A declared, runtime-enforced set of limits the robot will not exceed regardless of intent. Examples: maximum velocity, no-fly zones, restricted-zone polygons, force ceilings. Distinct from declared *capability* — capability says what the robot *can* do; the envelope says what the robot *will not* do.

**Specification (spec)** — The versioned documents in [`/spec`](../spec/) that define URML normatively. Each layer and each profile versions independently per semver.

**Steering committee** — The 3-to-5-person body that takes over from the sole maintainer starting in Phase 1. Membership recorded in [`GOVERNANCE.md`](../GOVERNANCE.md).

**Substrate** — The underlying robot OS that URML compiles to: ROS 2, PX4, OPC UA Robotics, Autoware, AUTOSAR Adaptive, a vendor SDK. Not part of URML; URML names targets but does not specify them.

**Substrate-neutrality acid test** — The rule that every Layer-2 primitive must be cleanly implementable on a runtime with zero ROS dependencies. The single most important architectural constraint in URML. Enforced by the primitive-proposal issue template.

**URDF** — Unified Robot Description Format. Existing standard URML reuses (not reinvents) for kinematic and geometric description.

**URML** — Universal Robot Language. Working name; subject to finalization in Phase 0 (see `MANIFESTO.md` Appendix B, Question 1).

**URML-Certified** — The (future) trademark / conformance mark granted to runtimes that pass the conformance suite. The mark is the commercial moat; the tests are the open core.

**URML program** — An instance of the URML language: a YAML (canonical) or JSON-LD document containing a single behavior. Statically verified before execution.

**Validator** — The static verification engine that checks a URML program against a capability manifest and active safety envelope. Part of the Core Commitment. Lives in [`/reference/validator`](../reference/validator/).

**Working group** — A Phase 2+ body with merge authority within one profile (home, drone, industrial, ...). Cross-cutting changes escalate to the steering committee.
