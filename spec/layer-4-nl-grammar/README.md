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

# Layer 4 — Natural Language Interface

**Status:** Drafted. The normative specification is [`v0.1.0.md`](v0.1.0.md) — the published prompt contract: the system-prompt surface, the few-shot library, the bounded validator-feedback revision loop, and the provider-neutral interface (Layer 4 has no dedicated RFC; the contract is the shipped `reference/llm-bridge/`). This README is the orientation; `v0.1.0.md` is what an integration must implement.

## Purpose

Layer 4 defines the **published prompt contract** — the documented way for any large language model to translate natural language into a valid URML program. Concretely:

- The JSON Schema a URML program must match.
- A library of few-shot examples spanning the v1.0 profiles (home, drone, industrial).
- The structured questions an LLM must ask the user when the natural-language input is ambiguous (e.g., "which red mug?").
- The validator-feedback format: when an LLM's emission is rejected by Layer-3 static checks or Layer-1 capability checks, the validator returns a structured error that the LLM can use to revise its emission.

Layer 4 is not a natural-language *parser*. URML does not parse English. It asks an LLM to emit URML, then validates the URML. The LLM is doing the language work; URML's job is to give the LLM a precise enough target that the result is reliable.

## Boundaries

Layer 4 must **not** include:

- A specific LLM provider. The contract is provider-neutral: Anthropic, OpenAI, open-weights models (Llama, Mistral, Qwen), and on-device models must all be first-class. Vendor lock-in here would forfeit the standard's neutrality and is forbidden by [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do.
- The runtime that executes URML. That's Layer 0 / the substrate.
- The robot's world model. Layer 4 may *describe* what world-model facts an LLM is allowed to reference (e.g., named locations from the capability manifest), but the world model itself lives at the substrate.
- A natural-language *grammar* in the formal-linguistics sense. The "grammar" in this layer's name is loose — what is specified is the *output* an LLM produces (URML), not the *input* (English / Hebrew / Spanish / ...).

## What the normative document specifies

[`v0.1.0.md`](v0.1.0.md) carries the items below. Note its §5: the interactive
disambiguation protocol described next is **not** in v0.1 — ambiguity is
resolved by a manifest-grounded default or a `report(status: failure)`, and
the only loop is the deterministic validator-feedback loop.

- The JSON Schema for a complete URML program.
- The few-shot example library: at least three examples per supported profile, demonstrating the common cases plus at least one error-handling case.
- The disambiguation protocol: when the LLM should ask the user vs. when it should pick a reasonable default and proceed.
- The validator-feedback specification: error codes, error messages, expected LLM revision behavior.
- The multilingual posture: how the contract handles non-English input. (English-only is the v0.1 *content* coverage; the *structure* reserves slots for Hebrew, Spanish, Japanese, and Mandarin.)

## Why this matters

[`MANIFESTO.md`](../../MANIFESTO.md) §Why Now names this as the bottleneck that has shifted:

> *"The bottleneck has moved from 'can a model produce structured robot commands' to 'what is the right structure for a model to produce.' That second question is what URML answers."*

Layer 4 is the surface where that answer meets the LLM ecosystem. The quality of this layer determines how reliably language models emit valid URML, which determines how usable URML is end-to-end.

## Reference implementation

The provider-agnostic glue lives in [`/reference/llm-bridge/`](../../reference/llm-bridge/). That code is part of the [Core Commitment](../../CORE_COMMITMENT.md) — always Apache 2.0, no vendor coupling.

## Conformance points

The test + conformance surface covers:

- That the JSON Schema correctly accepts every shipped example and rejects a documented set of malformed programs.
- That the validator-feedback format is stable across the supported error categories.
- That the few-shot example library round-trips cleanly: each `(natural_language, urml_program)` pair, given to a model with the contract, reliably yields the documented program above a stated success rate.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Layer 4.
- [`/docs/glossary.md`](../../docs/glossary.md) — LLM bridge, validator.
- [`/reference/llm-bridge/`](../../reference/llm-bridge/) — the reference implementation.
- [`/examples/`](../../examples/) — the paired natural-language and URML scenario fixtures.
