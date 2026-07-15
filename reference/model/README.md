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

# urml-model

Dataset synthesis pipeline and training recipe for a URML-native small model ([RFC-0666](../../docs/rfcs/0666-urml-native-model-pipeline.md)).

The idea: URML already owns a perfect, free, machine-checkable reward signal. A candidate program is correct exactly when `urml_validator.validate` accepts it, and when it is wrong the validator says why in ~150 namespaced error codes. This package turns that oracle plus the repository's gold assets (conformance fixtures, the few-shot library, rejected bridge emissions) into a training dataset for a small open-weights model that emits first-pass-valid URML offline.

What this package does **not** do: train a model, download weights, or call a specific LLM vendor. Training is operator-action, documented in [docs/training-recipe.md](docs/training-recipe.md). No model artifact ever lives in this repository.

## Quick start

```bash
# Hermetic: mine the repo's gold assets into a dataset (no network, no LLM)
urml-model synthesize --out data/urml-sft.jsonl

# Write a chat-format SFT file (system prompt = the bridge's real prompt)
urml-model export --in data/urml-sft.jsonl --out data/sft-chatml.jsonl --fmt chatml

# After training: score the model with the conformance scorer (RFC-0021 metrics)
urml-model eval --utterances-root conformance/llm-bridge/fixtures \
  --profile home --backend ollama --model my-urml-3b \
  --out conformance/llm-bridge/results/$(date +%F)/home-my-urml-3b.yaml
```

## Dataset shape

One JSONL record per example: `nl`, `program`, `manifest_ref`, `profile`, `language`, `provenance`, `validator_verdict`, optional `envelope_ref` and `repair`. Records rejected by the validator are only allowed as `rejection_repair` examples (failed emission + error codes + the accepted program as the repair target). The full schema is normative in RFC-0666.

## Diversity at scale

The CLI's synthesize path uses the deterministic template back-translator so CI stays hermetic. Real phrasing diversity comes from `LLMBackTranslator`, a library call that takes any `LLMProvider` (Anthropic, OpenAI, Ollama, llama.cpp — the bridge's own adapters). Every candidate it produces still goes through the oracle before it enters the dataset.
