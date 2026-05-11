# Layer 3 — Behavior Composition

**Status:** Pre-draft. The specification document for this layer is targeted for v0.1; see roadmap in [`MANIFESTO.md`](../../MANIFESTO.md).

## Purpose

Layer 3 defines the **grammar for assembling Layer-2 primitives into behaviors**. A URML program is a tree (or sequence) of composed primitives plus the composition operators that glue them together. Layer 3 specifies those operators and their semantics:

- **`sequence`** — do A, then B, then C, in order.
- **`branch`** — given a condition, do A else B.
- **`parallel`** — do A and B simultaneously; declare what "done" means (all, any, first-to-succeed).
- **`retry`** — repeat A until it succeeds or a bound is hit.
- **`on_error`** — `abort_and_report | continue | substitute(other_behavior)`.
- **Variables** — `store_as: name` on a primitive binds its result; `$name` references it later.

Layer 3 borrows freely from **behavior trees** and **PDDL** in spirit. It ships its own serialization, optimized for human reading and LLM emission.

## Boundaries

Layer 3 must **not** include:

- New primitives — those are Layer 2.
- A general-purpose programming language. URML is bounded by design: no arbitrary user-defined functions, no unbounded loops, no closures. Every URML program is statically checkable.
- Substrate-specific composition (ROS lifecycle states, MAVLink modes, vendor finite-state machines). Those are Layer 0 concerns.
- Trajectory or control-loop composition. A `parallel` block of two `move_to`s does *not* prescribe how the runtime coordinates the two motions; it prescribes that both motions should happen and gives the runtime the freedom to coordinate.

## What goes here when this document is drafted

- The full composition grammar: every operator's syntax, semantics, and termination conditions.
- The error-handling model: which primitives can fail, what failure looks like at the composition layer, how `on_error` interacts with `retry` and `parallel`.
- The variable system: scope rules, type compatibility, when a variable is "set," what happens if it's referenced before it's set.
- The static-checking rules the validator enforces: type compatibility across primitives, termination of retry blocks, no-dangling-variable, no-unreachable-branch.
- The canonical serialization (YAML) and the equivalent JSON-LD encoding.

## Conformance points

When this layer is drafted, the conformance suite will test:

- That conformant runtimes execute every operator's documented semantics, including edge cases (empty sequence, single-branch parallel, retry with zero bound).
- That the validator rejects every documented invalid construction (untyped variable reference, infinite retry, unreachable branch, type-mismatched primitive arguments).
- That the YAML and JSON-LD encodings round-trip cleanly.

## Open design questions

- **`parallel-with-handoff`** (one branch can preempt another). Initial position: don't add it — compose with `branch` + abort instead. Re-evaluate if a profile shows it's needed.
- **Variable typing.** Is the type of a variable inferred from the producing primitive's `store_as` signature, declared by the consuming primitive's argument signature, or both? Lean: both, and the validator checks they agree.
- **Iterators / map-style composition** ("for each `red_widget` detected, pick it"). PDDL has a `forall`; behavior trees don't. URML's bounded-by-design posture leans against; profiles may declare bounded iteration primitives if they need it.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Layer 3.
- [`/docs/glossary.md`](../../docs/glossary.md) — composition, behavior.
- [`/spec/layer-2-primitives/`](../layer-2-primitives/) — what gets composed.
