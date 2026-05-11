# Layer 2 — Intent Primitives

**Status:** Pre-draft. The specification document for this layer is targeted for v0.1; see roadmap in [`MANIFESTO.md`](../../MANIFESTO.md).

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

## What goes here when this document is drafted

For each primitive:

- The verb name (snake_case).
- The argument schema (JSON Schema or YAML equivalent).
- One-sentence semantics in plain English.
- Layer-1 capability requirements (which manifest fields must be present).
- Safety-envelope checks (which limits the validator enforces before allowing execution).
- Variable-binding behavior (which arguments may bind a `$name` variable; which output is bound to a `store_as`).
- A "what NOT to assume" subsection naming substrate-leaks proposers must avoid.

The initial vocabulary will be drafted as **RFC-0002: Initial Layer-2 Primitive Vocabulary**.

## Conformance points

When this layer is drafted, the conformance suite will test:

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
