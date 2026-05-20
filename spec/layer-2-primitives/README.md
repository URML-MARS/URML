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

# Layer 2 — Intent Primitives

**Status:** Drafted. The normative specification is [`v0.1.0.md`](v0.1.0.md) — twenty primitives (twelve core + eight profile-scoped), transcribed from [RFC-0002](../../docs/rfcs/0002-initial-primitive-vocabulary.md) (the initial seventeen) and extended by [RFC-0013](../../docs/rfcs/0013-industrial-layer2-primitives.md) (`pick_from`, `place_at`, `swap_tool` for the industrial profile). This README is the orientation; `v0.1.0.md` is what a runtime must implement.

## Purpose

Layer 2 defines the **atomic vocabulary of robot intent**. Each primitive is a verb — `move_to`, `grasp`, `hover`, `scan`, `detect`, `dock`, `release` — with a typed argument schema, documented semantics, declared capability requirements (which Layer-1 fields must be present in the target's manifest), and declared safety-envelope checks.

A primitive carries *intent*, not implementation. `move_to(kitchen)` says go there; the runtime decides how, using whatever Layer-0 substrate it implements (Nav2 goal on ROS 2, offboard setpoint on PX4, vendor-specific API call elsewhere).

The Manifesto target is **under thirty primitives** in the core. Domain richness lives in profiles, not in the core.

## Boundaries

Layer 2 must **not** include:

- Trajectories, motor commands, or control loops. Those are Layer 0.
- Composition — sequence, branch, parallel, retry. That is Layer 3. A primitive does one thing.
- Natural-language ambiguity. By the time an LLM emits a primitive, its structured fields are unambiguous; ambiguity is resolved in Layer 4's interaction step.
- Profile-specific verbs. If only one domain uses it, it belongs in a profile, not the core.

## The substrate-neutrality acid test

Per [`MANIFESTO.md`](../../MANIFESTO.md) §Design Principles and [`CLAUDE.md`](../../CLAUDE.md), every primitive in this layer must be **cleanly implementable on a runtime with zero ROS dependencies**. The Issue template at [`.github/ISSUE_TEMPLATE/primitive_proposal.md`](../../.github/ISSUE_TEMPLATE/primitive_proposal.md) forces every proposer to sketch both a ROS-2 implementation and a non-ROS implementation up front, before the RFC stage. A primitive that fails the acid test is leaking substrate assumptions and needs rework.

## What the normative document specifies

[`v0.1.0.md`](v0.1.0.md) carries, for each primitive:

- The verb name (snake_case).
- The argument schema (JSON Schema or YAML equivalent).
- One-sentence semantics in plain English.
- Layer-1 capability requirements (which manifest fields must be present).
- Safety-envelope checks (which limits the validator enforces before allowing execution).
- Variable-binding behavior (which arguments may bind a `$name` variable; which output is bound to a `store_as`).
- A "what NOT to assume" subsection naming substrate-leaks proposers must avoid.

The initial vocabulary was decided in **RFC-0002: Initial Layer-2 Primitive Vocabulary** and is now normatively specified in [`v0.1.0.md`](v0.1.0.md).

## Conformance points

The conformance suite (`/conformance/fixtures/`) tests:

- For each primitive, that conformant runtimes correctly execute it given a valid manifest and accept/reject the documented edge cases.
- That the validator correctly rejects programs that use primitives the manifest doesn't support.
- That the validator correctly enforces every documented safety-envelope check.

## How new primitives are added

1. Open a [primitive-proposal issue](../../.github/ISSUE_TEMPLATE/primitive_proposal.md), including both implementation sketches (ROS-2 and non-ROS).
2. The maintainer (Phase 0) or steering committee (Phase 1+) routes the proposal: accept, reject, or "make this a profile primitive instead."
3. If routed forward, file an RFC. A Layer-2 RFC must include all the per-primitive sections listed above.
4. On Accepted: implement in at least one runtime, write conformance tests, write a runnable example. Only then does the RFC reach Implemented.

A new primitive is a one-way door. Composition is preferred over expansion: if a behavior can be expressed by composing existing primitives, the composition is the right answer.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Layer 2.
- [`/docs/glossary.md`](../../docs/glossary.md) — primitive, intent, safety envelope.
- [`/spec/layer-3-behavior/`](../layer-3-behavior/) — how primitives compose.
- [`/spec/profiles/`](../profiles/) — profile-specific primitives.
