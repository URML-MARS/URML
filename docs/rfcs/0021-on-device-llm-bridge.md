---
rfc: 0021
title: On-device LLM bridge — schema-derived GBNF, GGUF model contract, per-model conformance
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-21
updated: 2026-06-07
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

# RFC-0021: On-device LLM bridge — schema-derived GBNF, GGUF model contract, per-model conformance

## Summary

Make on-device, model-agnostic LLM inference a first-class component of URML.
Concretely, this RFC adds two reference `LLMProvider` adapters
(`llama_cpp`, `ollama`), a deterministic schema-to-GBNF helper
(`grammar.py`) shared by both, the **GGUF** file format as the contract for
on-device model interchange, and a per-model conformance sub-suite under
`conformance/llm-bridge/` that scores any `(model, backend, profile)` triple
on the same fixture set the cloud adapters already pass. The existing
`LLMProvider` Protocol is not modified; grammar derivation is a
backend-internal concern.

The effect: URML becomes deployable end to end on a $80 SBC with no cloud
account, while preserving every existing cloud path. Two static gates before
any motor moves: GBNF rejects structurally invalid URML at decode time;
`urml_validator.validate()` rejects semantically invalid URML before
dispatch.

## Motivation

[Layer 4 v0.1.0](../../spec/layer-4-nl-grammar/v0.1.0.md) §1 already names
"open-weights (Llama/Mistral/Qwen via vLLM/llama.cpp/Ollama), and on-device
models" as first-class. The shipped reference bridge does not yet honor
that: of the three adapters in
[`reference/llm-bridge/src/urml_llm_bridge/providers/`](../../reference/llm-bridge/src/urml_llm_bridge/providers/),
two (`anthropic.py`, `openai.py`) require an outbound API call and the
third (`echo.py`) is a hermetic test double. A robot maker who reads the
spec, builds against the bridge, and asks "how do I ship this on a Pi 5
with no cloud" gets no answer in code.

The gap matters for three audiences the project is committed to serving:

1. **Manufacturers** courting the federal and small-fleet market, who need
   an offline path for procurement and air-gap reasons.
2. **Educational and research users**, who cannot rely on per-device API
   spend, and whose hardware budgets sit at SBC scale.
3. **The standard itself.** As long as the only working `LLMProvider`s call
   a cloud, the LLM bridge's provider-neutrality clause
   ([Layer 4 v0.1.0](../../spec/layer-4-nl-grammar/v0.1.0.md) §1; [CLAUDE.md](../../CLAUDE.md)
   §What Claude Should Never Do) is aspirational rather than demonstrated.
   A second non-cloud adapter is the cheapest possible proof.

The grammar piece is the load-bearing addition. Cloud adapters can rely on
the provider's own structured-output mode (Anthropic tool use, OpenAI JSON
mode). Small open-weights models on a local serving stack typically have no
such mode, and unguided decoding from a 270M-class model produces
structurally invalid JSON often enough to make the revision loop the
dominant cost. A GBNF grammar derived from the program JSON Schema makes
structural invalidity unrepresentable at the token level, which is the
right place to enforce it: at the decoder, before tokens commit, with no
network round-trip per fix.

## Detailed design

### Spec changes

- **Layer 4** ([`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md)):
  add §2.3 *Grammar-constrained providers* (normative): a provider MAY
  enforce structural validity at decode time via a GBNF derived from the
  exported program JSON Schema; the derivation is informative (the schema is
  authoritative) and the validator MUST still run. Add §2.4
  *On-device model interchange*: when a provider distributes a model file,
  the file format is **GGUF**; this is a packaging contract, not a runtime
  one (a provider that does not distribute model files is unaffected).
- **Layer 4 README** ([`spec/layer-4-nl-grammar/README.md`](../../spec/layer-4-nl-grammar/README.md)):
  add a one-paragraph pointer to the on-device path and the
  `conformance/llm-bridge/` sub-suite. No status change (the spec is already
  Drafted).

### Bridge changes

None. `Bridge.translate()`'s deterministic validator-feedback loop
([Layer 4 v0.1.0](../../spec/layer-4-nl-grammar/v0.1.0.md) §3) is the
correct algorithm for grammar-constrained providers too: a grammar that
guarantees parseable JSON does not guarantee schema-valid JSON (missing
`required` fields, unrecognized primitives, type-mismatched bindings remain
possible), and the validator catches the residue. The Protocol surface
(`LLMProvider.complete(system, user, schema, max_tokens) -> str`) is
unchanged; grammar is a per-backend implementation detail, derived from the
already-passed `schema:` argument.

### New providers

Two adapters in [`reference/llm-bridge/src/urml_llm_bridge/providers/`](../../reference/llm-bridge/src/urml_llm_bridge/providers/),
both following the lazy-import, opt-in-extra pattern set by
`anthropic.py` and `openai.py`:

- **`llama_cpp.py`** (production target). Talks to a running `llama-server`
  process over HTTP, sending `prompt`, `grammar` (derived once per schema
  via `grammar.schema_to_gbnf`, cached), `n_predict`, and `temperature`.
  Returns the completion as a JSON string. Lazy-imports `httpx`; install
  with `pip install urml-llm-bridge[llama_cpp]`. Defaults to
  `http://127.0.0.1:8080` (the llama.cpp default).
- **`ollama.py`** (developer convenience). POSTs to `/api/generate` with
  `format: "json"` for soft JSON guidance. Grammar enforcement on Ollama is
  weaker than on llama-server (Ollama's `format: json` is a hint, not a
  hard grammar gate); the adapter passes the schema through anyway so a
  future Ollama version that supports JSON-Schema constraints picks it up.
  [Erratum 2026-08: the shipped adapter uses `/api/chat` and forwards the
  full JSON Schema as `format`, which Ollama 0.5+ honors as a decoder
  constraint.]
  Documented in the adapter docstring. Lazy-imports `httpx`; install with
  `pip install urml-llm-bridge[ollama]`. Defaults to
  `http://127.0.0.1:11434`.

Neither adapter speaks an SDK; both speak HTTP. This keeps the dependency
surface small (one extra: `httpx`) and avoids tying URML to a specific
llama-cpp or ollama Python client release cadence. Both adapters accept an
injectable `client` for hermetic testing, mirroring the
`AnthropicProvider(client=...)` injection pattern.

### Grammar derivation

`reference/llm-bridge/src/urml_llm_bridge/grammar.py` exposes one public
function:

```python
def schema_to_gbnf(schema: dict[str, Any], *, root: str = "root") -> str: ...
```

It walks a JSON Schema Draft 2020-12 document and produces a GBNF grammar
that accepts the same JSON value space *structurally*. Supported features:

- `type: object` with `properties`, `required`, and
  `additionalProperties: false` (a strict-mode requirement; objects with
  `additionalProperties: true` widen to free-form JSON).
- `type: array` with `items` (homogeneous) and `prefixItems`.
- `type: string`, `number`, `integer`, `boolean`, `null`.
- `enum` and `const` (literal alternation; the canonical place where GBNF
  excludes invalid emissions cheaply).
- `oneOf` / `anyOf` (alternation; cycle-safe).
- `$ref` against `#/$defs/...` (recursive rules; the program schema's
  `Branch -> if_true -> Branch` cycle is the canonical reason this matters).

Deliberately **not** enforced in GBNF (semantic residue handled by the
validator):

- `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `multipleOf`.
- Cross-field constraints (e.g., a `store_as` name being unique within a
  scope, or a `held` reference resolving to an `{"object"}`-typed binding).
- Manifest-aware constraints (locations declared, primitives capability-
  matched, services declared on docking stations).

These reject downstream in the validator's revision loop, which is the
spec-defined place for them.

The function is pure, deterministic, and cached by a hash of the input
schema (`functools.lru_cache` on the JSON-serialized canonical form). For
the v0.1.0 program schema, one derivation call produces a grammar of
roughly 4 KB; the cache makes repeated `complete()` calls free after the
first.

### Conformance suite changes

A new sub-suite, `conformance/llm-bridge/`, parametrized over
`(model, backend, profile)`. Each row of the published table is a tuple:

```yaml
model_id: smollm-360m-instruct
model_size_b: 0.36
backend: llama_cpp
profile: home
n_utterances: 20
structural_pass_rate: 1.00     # GBNF guarantees this when llama_cpp is the backend
semantic_pass_rate: 0.85       # post-validator
hardware_class: pi5            # informational; targets, not certifications (RFC-0007 honesty rule)
revision_attempts_mean: 1.4
```

`structural_pass_rate` is meaningful even on cloud backends (Anthropic
tool-use ~ 1.00, OpenAI json-mode ~ 1.00); `semantic_pass_rate` is the
number that actually varies by model and backend. Reports land under
`conformance/llm-bridge/results/<date>/<row>.yaml` and aggregate into the
published table in
[`conformance/llm-bridge/README.md`](../../conformance/llm-bridge/README.md).
No model is default-recommended in the spec; the published table lists
scored models with their scores. (The sibling registry
[`docs/compatible-runtimes.md`](../../docs/compatible-runtimes.md) is the
*runtime*-side equivalent, scoped to substrate runtimes; the two surfaces
stay distinct because they answer different questions.)

CLI surface (existing `urml conformance run` plus a new sub-suite name):

```bash
urml conformance run --suite llm-bridge --backend llama_cpp --model ./SmolLM-360M-Q4.gguf --profile home
```

This RFC ships the directory, README, fixture-loader, scoring schema, and
**one** measured row (a hermetic echo-backend run that exercises the
parametrization path). The first real-model measurement lands in a
follow-up commit, deliberately separated so this RFC PR does not require a
GGUF artifact in CI.

### Provider-neutrality acid test (analogue of the RFC-0001 substrate-neutrality test)

Every claim made by this RFC must work for at least one non-llama-cpp
backend. The acid test, per piece:

- **The Protocol** is unchanged, so all existing backends (Anthropic,
  OpenAI, echo) continue to pass `test_bridge` with no modification.
- **`grammar.schema_to_gbnf`** is a pure function of a JSON Schema. It does
  not name llama.cpp anywhere. The Ollama adapter receives the same string
  and forwards it; an OpenAI adapter that wanted to use it for the
  forthcoming OpenAI grammar support could do so without touching this
  module.
- **`conformance/llm-bridge/`** scores `backend in {llama_cpp, ollama,
  anthropic, openai, echo}` with the same fixture set. The first row in
  the v0.1 table is the echo-backend row (deterministic, exercises the
  harness). Cloud backends populate when a maintainer runs them.

If any of the three above starts to require llama-cpp-specific assumptions,
the implementation is wrong and is sent back.

### US-alignment defaults

[RFC-0003](0003-us-alignment.md) governs default-recommended choices. This
RFC honors it as follows:

- The spec (§2.4) names **GGUF** as the on-device interchange format. GGUF
  is provenance-neutral; no vendor implication.
- The conformance docs may score any model the user runs, including Qwen,
  Mistral, or other non-US-aligned weights. Scoring is descriptive, not
  prescriptive.
- The bridge ships no default model. When example commands in docs need a
  concrete model name, they prefer US-origin or unambiguously-permissive
  weights (Llama family, Phi, SmolLM, Gemma) over non-US-aligned weights
  (Qwen, Yi, DeepSeek). A US-federal deployer running with the bundled
  compliance policy (`policy: "DEFAULT"`) can swap to Qwen explicitly; the
  bridge does not block it, the deployer's procurement does.

## Backward compatibility

Purely additive and pre-v1.0. No existing primitive, schema, fixture,
provider, or runtime behavior changes. The `LLMProvider` Protocol is
unchanged; the three existing providers keep working. Cloud-only deployers
add nothing. On-device deployers install one or both new extras.

## Drawbacks

1. **Grammar coverage is partial by design.** `schema_to_gbnf` enforces
   structure but not `pattern`, length, or numeric range. A GBNF-perfect
   string of valid JSON may still be rejected by the validator. This is the
   correct division (validator owns semantics) but the RFC must say so
   loudly to avoid the misread "the grammar makes the validator unnecessary."
2. **Two new HTTP backends to maintain.** Both adapters depend on
   external servers (`llama-server`, `ollama serve`) the project does not
   ship. Their HTTP surfaces are stable but not frozen; a breaking change
   upstream is a maintenance event we accept.
3. **Ollama's `format: json` is weaker than llama-server's `grammar`.** The
   adapter is honest about this in its docstring; users who care about
   token-level structural guarantees should prefer `llama_cpp`. The
   adapter is shipped anyway because it is the lowest-friction path for
   developer experimentation, which is where adoption lives.
4. **First-call grammar derivation cost.** `schema_to_gbnf` on the v0.1.0
   program schema takes a few milliseconds. After `lru_cache` warms it is
   free. This is fine, but a freshly-launched bridge process pays it once
   per schema; no per-request cost.
5. **Hardware-class claims are informational.** Pi 5 and Rock 5B appear in
   the conformance table as `hardware_class` strings, but the spec makes
   no latency or token/sec guarantee. Per the runtime-honesty gradient
   (PR #100), unmeasured claims are not promises; this RFC publishes the
   numbers that are measured and labels the rest as targets.

## Alternatives considered

- **Extend `LLMProvider.complete()` with a `grammar:` parameter.** The
  genuine, non-strawman alternative. Rejected: the Protocol's current
  surface (system, user, schema, max_tokens → JSON string) is already
  sufficient. Grammar is derivable from `schema`, so adding `grammar` as a
  separate kwarg would force every provider to think about it even when
  the provider cannot use it (Anthropic and OpenAI both ignore it).
  Keeping grammar inside the llama-cpp adapter localizes the concern.
- **A separate `GrammarConstrainedProvider` Protocol.** Rejected: doubles
  the Protocol surface for one capability that splits 2-and-2 today and
  may split differently next quarter (OpenAI's preview grammar support
  could move it across the line). A single Protocol with internal
  variation is the more durable design.
- **Vendor a pre-built GBNF file with the spec.** Rejected: the schema
  evolves per-validator-release; a pre-built grammar would drift the moment
  the schema gains a primitive. Generating on first use from the
  authoritative schema makes drift impossible.
- **Defer on-device entirely and ship cloud only for v0.1.** Rejected: the
  spec already commits to provider neutrality; shipping zero non-cloud
  backends with that commitment is dishonest.
- **Use the `outlines` library for grammar-constrained decoding.**
  Considered. Adds a heavyweight dependency, couples the backend choice to
  a specific Python library, and duplicates what `llama-server` already
  does natively. The HTTP-to-llama-server path is simpler and lighter.

## Prior art

- The `LLMProvider` Protocol itself
  ([`providers/base.py`](../../reference/llm-bridge/src/urml_llm_bridge/providers/base.py))
  was designed to admit "vLLM, llama.cpp, Ollama, or future on-device
  runtimes" by name in its docstring. This RFC delivers what that comment
  promised.
- llama.cpp ships
  [`examples/json_schema_to_grammar.py`](https://github.com/ggerganov/llama.cpp),
  MIT-licensed, the reference implementation of schema-to-GBNF derivation.
  Our `grammar.py` is a clean, narrower reimplementation (covering only
  the JSON Schema features the URML program schema actually uses) to avoid
  vendoring a third-party tool and to keep the surface tested against our
  schema specifically. The Apache-2.0 licensing of this repo is preserved.
- The Anthropic and OpenAI adapter pattern (lazy SDK import, optional
  extras, injectable client for tests) is established in
  `providers/anthropic.py` and `providers/openai.py` and is followed
  verbatim.
- The conformance-suite parametrization model (declarative YAML fixtures,
  auto-discovery, structured report) is established in
  [`conformance/`](../../conformance/) and extended, not redesigned, by
  this RFC.

## Unresolved questions

- **OpenAI strict `json_schema` mode.** OpenAI's stricter
  `response_format: json_schema` rejects pydantic-generated schemas
  (every field required, no `oneOf`, no `pattern`). A future RFC may add
  a schema-preprocessing path that satisfies strict mode and lets
  `OpenAIProvider` use `json_schema` for harder structural guarantees;
  out of scope here.
- **Per-model hardware-class measurement.** This RFC ships the schema for
  `hardware_class` and one echo row; populating Pi 5 / Rock 5B / Jetson
  rows is a measurement project, tracked separately.
- **Multilingual conformance.** The v0.1 conformance utterance sets are
  English. The structure already supports `<scenario>.<lang>.txt`
  variants; a follow-up populates Hebrew and Spanish sets for at least
  the home and industrial profiles.
- **Grammar regeneration on schema bump.** Today the LRU cache keys on
  schema content, so a validator upgrade that ships a new schema
  invalidates the cache automatically. If we later persist grammars to
  disk for startup cost reasons, the cache key needs to incorporate the
  validator version explicitly.

## Implementation note

One PR set, mirroring the RFC-0013 precedent (RFC doc + code land
together; the `Accepted -> Implemented` frontmatter flip is the final
commit, after all suites are green). Commit order: (1) this RFC at
`Draft` + the index row; (2) `grammar.py` + its hermetic tests;
(3) `providers/llama_cpp.py` + tests with an injected httpx-like fake;
(4) `providers/ollama.py` + tests with an injected httpx-like fake;
(5) `pyproject.toml` extras for `[llama_cpp]` and `[ollama]`;
(6) `conformance/llm-bridge/` README + fixture-loader + scoring schema +
the echo-backend row; (7) Layer-4 spec promotion (§2.3, §2.4) +
README pointer; (8) RFC flip `Draft -> Open -> Accepted -> Implemented`.
The Phase-0 seven-day Open-to-Accepted comment window is a founder-
triggered calendar step tracked separately; it gates the state flip, not
the code.

### Shipped (Draft → Implemented, 2026-06-07)

Landed as a complete vertical slice, purely additive (the `LLMProvider`
Protocol is unchanged; the three existing providers and every runtime are
untouched):

- **Spec**: Layer-4 §2.3 *Grammar-constrained providers* + §2.4 *On-device
  model interchange (GGUF)* (`spec/layer-4-nl-grammar/v0.1.0.md`), README
  pointer to the on-device path + the conformance sub-suite.
- **Grammar**: `reference/llm-bridge/src/urml_llm_bridge/grammar.py` —
  `schema_to_gbnf()` (pure, `lru_cache`d, derives a GBNF from the program JSON
  Schema), with hermetic tests (`test_grammar.py`).
- **Providers**: `providers/llama_cpp.py` (HTTP to `llama-server`, sends the
  derived grammar) and `providers/ollama.py` (`/api/generate`, `format: json`
  [Erratum 2026-08: shipped as `/api/chat` with the full schema as `format`]),
  both lazy-importing `httpx` behind opt-in extras (`[llama_cpp]`, `[ollama]`)
  with injectable clients; tests with injected fakes.
- **Conformance sub-suite**: `conformance/llm-bridge/` (README + row schema +
  home utterance fixtures) and `conformance/src/urml_conformance/llm_bridge/`
  — a dependency-light `loader` (utterance sets + `ResultRow`) and a
  backend-neutral `scorer.score()` that drives the bridge over an utterance set
  and tallies structural / semantic pass rates + mean revisions. One committed
  **hermetic echo-backend row** (`results/2026-06-07/home-echo-double.yaml`)
  exercises the `(model, backend, profile)` parametrization path; loader +
  scorer tests are fully hermetic (`urml_llm_bridge` imported lazily, gated by
  the `[llm-bridge]` extra).

Deliberately a follow-up (kept out of CI so this needs no GGUF artifact):
populating the published table with **real-model** rows (a `llama_cpp`/`ollama`
run against a downloaded GGUF + a running server). The harness is the same
`score()` function; only the provider changes. The provider-neutrality acid
test holds: `schema_to_gbnf` names no backend, the loader needs no bridge, and
the scorer scores `echo` today and any backend tomorrow with the same code.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in three concrete audiences (manufacturers,
      educational/research, the standard's own consistency) and one
      concrete failure mode (small models produce structurally invalid
      JSON without a grammar).
- [x] The Detailed design names every affected spec document and reference
      component, with file paths.
- [x] At least one alternative is genuinely considered (the
      `grammar:` kwarg on `LLMProvider.complete()` — argued, not
      strawmanned).
- [x] Drawbacks are listed; the partial grammar coverage, Ollama's weaker
      enforcement, and the dependency on external servers are real
      downsides.
- [x] Backward compatibility is honest: purely additive, pre-v1.0,
      Protocol unchanged.
- [x] This RFC concerns Layer 4 and the LLM bridge specifically; the
      substrate-neutrality acid test (RFC-0001) is adapted to the
      analogous *provider*-neutrality acid test, with concrete checks.
- [x] US-alignment ([RFC-0003](0003-us-alignment.md)) is honored: GGUF is
      vendor-neutral, no model is default-recommended in the spec, docs
      example commands favor US-permissive weights, federal deployers can
      swap explicitly.
- [x] The implementation note explains how this lands (commit order,
      one-PR-set + final state-flip precedent), not just what.
- [x] The author re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude
      Should Never Do: this RFC adds on-device, model-agnostic inference,
      does not embed a specific LLM provider, does not bypass the
      validator (the validator MUST still run), and adds no cloud
      dependency at the runtime path.
