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

# LLM-bridge conformance sub-suite (RFC-0021)

Per-model scoring of `(model, backend, profile)` triples. The sibling
`conformance/fixtures/<profile>/` suites measure runtime conformance; this
sub-suite measures how reliably a given LLM, talking through a given
`LLMProvider` adapter, emits programs the validator accepts for a given
profile's utterance set.

## Why this exists

[RFC-0021](../../docs/rfcs/0021-on-device-llm-bridge.md) makes on-device
inference a first-class component of URML. The spec is provider-neutral;
this sub-suite is the **descriptive** counterpart: it doesn't pick a
default model, it publishes numbers so deployers can.

Two numbers per row matter:

- **`structural_pass_rate`** — fraction of emissions that parse as JSON
  and validate against the program schema's structural shape. For
  grammar-constrained backends (llama_cpp via `llama-server`), this
  is `1.00` by construction; for soft-JSON backends (Ollama, OpenAI
  JSON mode) it is whatever the model produces.
- **`semantic_pass_rate`** — fraction of structurally-valid emissions
  that also pass the full validator (capability checks, envelope checks,
  Layer-3 invariants, policy). This is the number that actually varies
  by model and is the headline number in published reports.

## Row schema

Each measurement is one YAML file under `results/<date>/<row_id>.yaml`:

```yaml
row_id: smollm-360m-llama_cpp-home-20260521
recorded_at: 2026-05-21T14:00:00Z
model_id: smollm-360m-instruct
model_size_b: 0.36
backend: llama_cpp           # one of: llama_cpp | ollama | anthropic | openai | echo
profile: home                # one of the v0.1 profiles
n_utterances: 20
structural_pass_rate: 1.00
semantic_pass_rate: 0.85
revision_attempts_mean: 1.4
hardware_class: pi5          # informational target, not a guarantee
notes: |
  SmolLM 360M on a Raspberry Pi 5, llama.cpp Q4_K_M quantization.
  20 utterances from fixtures/home/utterances-en.yaml.
```

`hardware_class` is informational and follows the [runtime honesty
gradient](../../docs/architecture.md) convention: any number not produced
by an actual measurement is a target, not a guarantee.

## Utterance fixtures

Per-profile sets under `fixtures/<profile>/utterances-<lang>.yaml`:

```yaml
profile: home
language: en
manifest: turtlebot4_home    # name resolved via reference/llm-bridge fixtures
utterances:
  - id: red_mug
    text: "Bring me the red mug from the kitchen."
    expected_kind: positive
  - id: missing_capability
    text: "Make me a sandwich."
    expected_kind: report_failure
```

`expected_kind` is one of:

- `positive` — the bridge should emit a validator-accepted program.
- `report_failure` — the bridge should emit a `report(status: failure)`
  step naming what the manifest doesn't cover, not invent capability.

## Code layout

This directory is the **data and docs** surface (utterance fixtures,
results, this README). The Python code that consumes it lives in the
existing conformance package: `urml_conformance.llm_bridge.loader`
([`conformance/src/urml_conformance/llm_bridge/`](../src/urml_conformance/llm_bridge/)).
The split mirrors the existing convention (`conformance/fixtures/` is
data; `conformance/src/urml_conformance/` is code).

## Running

Hermetic (no real LLM; loader tests confirm the on-disk schema is well-formed):

```bash
cd conformance
pip install -e ".[dev]"
pytest tests/test_llm_bridge_loader.py
```

A real-model run requires the relevant backend's server and model file.
The scoring runner that drives the bridge end-to-end against a real
provider lands in a follow-up commit; once it exists, the invocation will
look like:

```bash
# llama.cpp
llama-server -m ./SmolLM-360M-Q4.gguf --port 8080 &
urml conformance run --suite llm-bridge --backend llama_cpp --profile home

# Ollama
ollama serve &
ollama pull llama3.2:1b
urml conformance run --suite llm-bridge --backend ollama --model llama3.2:1b --profile home
```

Each invocation will write one row YAML to `results/<date>/`.

## Status

Phase 0, pre-alpha. The fixture-loader and scoring schema are stable; the
harness ships in this RFC's PR. Populating the published table with
measured rows is a follow-up project. Per [Phase-0 honesty rules](../../docs/launch/claims-audit.md),
unmeasured cells stay empty rather than guessed.

## Related

- [RFC-0021](../../docs/rfcs/0021-on-device-llm-bridge.md) — the RFC that
  introduces this sub-suite.
- [`reference/llm-bridge/`](../../reference/llm-bridge/) — the bridge and
  the adapters scored here.
- [`conformance/`](../) — the parent conformance suite README.
