---
rfc: 0700
title: Clarify mode, the opt-in ask-instead-of-guess protocol for the Layer-4 bridge
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-25
updated: 2026-09-25
supersedes: —
superseded-by: —
---

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

# RFC-0700: Clarify mode, the opt-in ask-instead-of-guess protocol for the Layer-4 bridge

## Summary

Since v0.1 the Layer-4 prompt contract has carried an honest disclaimer: the
interactive disambiguation protocol described in the READMEs ("which red
mug?") is not implemented, is a candidate for a future RFC, and until then a
conformant bridge MUST NOT be expected to conduct a clarifying dialogue
(`spec/layer-4-nl-grammar/v0.2.0.md` §5). This is that RFC.

The proposal is deliberately small: an **operator-enabled clarify mode**, off
by default, in which the model's first emission may be either an ordinary
URML program or a single **clarify object**,
`{"clarify": {"question": "...", "options": [...]?}}`. The integration relays
the question, folds the answer into the request
(`Clarification: Q: ... A: ...`), and re-enters the ordinary loop. One
question per translation, only before any validation failure, never about
something the manifest already decides, with a hard budget the integration
enforces at the decoder level where decoding is constrained. When clarify
mode is off — the default — the contract is byte-identical to v0.2.0.

The safety story extends from two outcomes to three: a request the manifest
cannot satisfy is refused (`report(status: failure)`), a request it can
satisfy one obvious way is translated, and a request it can satisfy more than
one way may now be asked about instead of guessed at. Refuse or ask, never
guess.

## Motivation

The header instruction today tells an ambiguous model to "pick a reasonable
manifest-grounded default". For a home robot told "bring me the mug" when the
manifest's vocabulary declares mugs and the room holds two, the reasonable
default is a coin flip the user never sees. Guessing is the one behavior a
validate-before-actuate posture cannot check: the guessed program is
admissible, so the validator rightly accepts it, and the wrongness only
surfaces in the world.

The refusal channel is the wrong tool for this. `report(status: failure)` is
for capability the manifest lacks; refusing a doable request because it was
underspecified trains operators to distrust refusals. A single budgeted
question is the honest middle path, and it is what every operator-facing
robot interface converges on in practice.

The disclaimer in §5 was written to keep the spec honest until the shape was
designed rather than to forbid the feature forever. Three constraints from
that section carry into the design: no free-form dialogue, no hidden state,
and no change to what a default-configured bridge is expected to do.

## Detailed design

The normative text is the new `spec/layer-4-nl-grammar/v0.3.0.md` §2.6 and
the amended §3 loop, shipped in this change per the document's own §6 rule.
In brief:

### Emission contract

In clarify mode a conformant first emission is either an unchanged program
object or:

```json
{"clarify": {"question": "Which red mug — the one on the counter or the shelf?",
             "options": ["counter", "shelf"]}}
```

`question` is a required non-empty string; `options` is an optional list of
short strings an integration may render as choices. The object has exactly
one top-level key, `clarify`. There is no discriminator wrapper on the
program side: a program's required keys make the two shapes structurally
disjoint, so every existing few-shot, fixture, and saved emission stays valid
byte-for-byte.

### Rules

1. **Opt-in.** Clarify mode is enabled by the operator out-of-band (a
   `Bridge(clarify=True)` constructor flag; `--clarify` on the CLI). It is
   never inferred from the request. Off is the default and the v0.2.0
   contract applies unchanged.
2. **One question, first emission only.** At most one clarify emission per
   translation, and only before any validation failure: revision attempts
   commit to a program. This keeps the loop's state machine small and its
   bound obvious.
3. **The manifest decides, not the model's curiosity.** A question about
   anything the manifest already determines (declared locations, gripper
   force classes, camera modes) is non-conformant; the prompt addendum says
   so. Undeclared capability still yields `report(status: failure)`, never a
   question.
4. **Budget enforced below the model.** The integration tracks
   `max_clarifications` (default 1). While budget remains, a
   schema/grammar-constrained provider widens its constraint to the union of
   the program schema and the clarify schema; once spent, the constraint
   narrows back and a constrained model physically cannot ask again. A
   question never consumes a revision attempt.
5. **Statelessness.** The answer is folded into the effective user request
   (`Clarification: Q: ... A: ...`); the prompt remains stateless per
   attempt, no transcript accumulates.
6. **Non-interactive honesty.** An integration with no human to relay to
   surfaces the question as a distinct terminal outcome
   (`BridgeClarificationNeeded` in the reference bridge), and never invents
   an answer.

### Reference implementation shape (informative)

- `Bridge(..., clarify: bool = False, max_clarifications: int = 1)`;
  `translate(request, *, on_clarify: Callable[[question, options], str] | None)`.
  Callback present: relay, fold, continue. Callback absent: raise
  `BridgeClarificationNeeded`.
- `LLMProvider.complete` gains an optional `clarify_schema` keyword (default
  `None` = today's behavior). Per adapter: Anthropic registers a second tool
  `ask_clarification` and widens `tool_choice` to `any`, mapping a clarify
  tool call back to the wire shape; llama.cpp derives GBNF from the union
  schema (`$defs` hoisted to the union root); Ollama sends the union as
  `format`; OpenAI JSON mode stays unconstrained and the prompt addendum
  carries the contract.
- CLI: `--clarify` on `translate` and `run`, question relayed on stderr,
  answer read from stdin; a non-TTY caller that cannot answer exits with the
  question printed. On the speech input path (RFC-0670) the question is
  relayed as text and the answer typed.

### Non-goals

- Multi-turn dialogue beyond the single budgeted question.
- Spoken answers on the speech path.
- Clarify in the fleet assembly (§2.5); a fleet translation runs with
  clarify off in v0.3.
- Any change to the program JSON Schema: a program is a program in both
  modes, and the clarify object is versioned with Layer 4 and the bridge.

## Alternatives considered

1. **A `{"kind": "program"|"clarify"}` discriminator wrapper.** Cleaner for
   union schemas, but it changes the byte shape of every program emission,
   breaking every existing few-shot, echo fixture, and downstream consumer
   for zero user-visible gain. Rejected.
2. **A `clarify` primitive inside the program schema.** It would let the
   validator see questions, but a question is not robot intent: it never
   reaches a runtime, and putting it in Layer 2 would force every runtime to
   refuse it. The emission-level union keeps Layer 2 clean. Rejected.
3. **Free-form multi-turn dialogue.** The industry default, and exactly what
   §5 warned against: unbounded loops, hidden state, and a prompt whose
   behavior is no longer deterministic per attempt. The single budgeted
   question keeps the bound `max_revisions + 1 + max_clarifications`.
   Rejected for v0.3; a future RFC can widen the budget if field use asks
   for it.
4. **Answering from context automatically** (the model asks itself and
   picks). That is guessing with extra steps. Rejected.

## Prior art

- The v0.1/v0.2 §5 disclaimer naming this exact protocol as the future RFC.
- RFC-0021 (grammar-constrained decoding): the union-schema mechanism reuses
  its GBNF derivation unchanged.
- RFC-0286 (fleet assembly): the pattern of an additive prompt-contract
  section with an explicit off-switch.
- Operator-facing conversational robot stacks (reachy-nova among them)
  converge on a bounded ask-back; none of them can check the question
  against a declared manifest, which is the piece URML adds.

## Implementation plan

This RFC PR carries the spec text only: `v0.3.0.md`, the layer README
pointer, and the llm-bridge README disclaimer update. The code lands in a
separate PR behind the off-by-default flag (bridge loop branch, provider
`clarify_schema` keyword for all five adapters, `_CLARIFY_ADDENDUM`, one
clarify few-shot injected only in clarify mode, `--clarify` on
`translate`/`run`, hermetic tests). Default behavior stays spec-conformant
with v0.2.0 throughout, so the code PR does not gate on this RFC's
acceptance; flipping any default would.

## Open questions

1. Should `options`, when present, constrain the accepted answer, or stay
   advisory? (Proposed: advisory; the answer is free text.)
2. Should a future bench mode report a clarify rate per model? (Out of scope
   here; noted in `bench/README.md` follow-ups.)
