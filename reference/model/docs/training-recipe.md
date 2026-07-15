# Training recipe: a URML-native small model

> Operator-run. Nothing here executes in CI, and no artifact it produces is committed to this repository (RFC-0666).

This walkthrough takes the dataset this package synthesizes and produces a LoRA fine-tune of a small open-weights model that emits first-pass-valid URML. The base model is a replaceable parameter, not an endorsement; any instruction-tuned model in the 1B to 9B class with a permissive license works. Pick per your deployment target (a Raspberry Pi 5 wants 1.5B to 3B quantized; a Jetson or desktop tolerates 7B to 9B).

## 0. What you need

- A GPU with 16 GB or more VRAM (a single rented A10/A100/4090-class card is enough for LoRA at 3B).
- The dataset: run the synthesis on the repo checkout, then (optionally, recommended) enrich it with LLM back-translation.
- An inference server for evaluation: `ollama serve` or `llama-server`.

## 1. Build the dataset

Hermetic floor (template utterances, every record oracle-verified):

```bash
urml-model synthesize --out data/urml.jsonl
```

Diversity pass (operator-action; pick any provider the bridge supports):

```python
from urml_llm_bridge.providers.anthropic import AnthropicProvider  # or openai / ollama
from urml_model import LLMBackTranslator, mine_fixture_programs, synthesize, Dataset

gold = mine_fixture_programs()
translator = LLMBackTranslator(AnthropicProvider(model="claude-haiku-4-5-20251001"))
diverse, report = synthesize(gold, translator, per_program=5)
print(report.summary())

base = Dataset.read_jsonl("data/urml.jsonl")
base.extend(diverse.records)
base.write_jsonl("data/urml.jsonl")
```

Provider terms note: utterances written by a hosted model inherit that provider's output terms. Read them before redistributing the enriched dataset; the hermetic floor carries no such question.

If you have bridge sessions from real use (for example a `--save-rejected` debugging trail rebuilt as `TranslateResult` objects), mine them too:

```python
from urml_model import mine_rejections, session_from_result
records = mine_rejections([session_from_result(nl, result) for nl, result in sessions],
                          manifest=manifest, manifest_ref="turtlebot4_home", profile="home")
```

## 2. Export

```bash
urml-model export --in data/urml.jsonl --out data/sft.jsonl --fmt chatml
urml-model export --in data/urml.jsonl --out data/dpo.jsonl --fmt dpo   # only if repair records exist
```

The chatml system prompt is the bridge's real prompt (manifest summary, envelope, few-shots, JSON schema). Train on it unmodified so inference-time and training-time prompts match.

## 3. Fine-tune (LoRA SFT)

Any LoRA-capable trainer works; the shape below is the reference point, not a framework mandate.

| knob | value | note |
| --- | --- | --- |
| method | LoRA (r=16, alpha=32, dropout 0.05) | full fine-tune is unnecessary at this dataset size |
| target modules | attention + MLP projections | the usual all-linear set |
| epochs | 2 to 3 | watch validation loss; this dataset is small and memorizes fast |
| learning rate | 1e-4 cosine, warmup 3% | |
| sequence length | long enough for the full system prompt (measure it: `urml emit-prompt` + tokenize; expect several thousand tokens) | truncating the schema out of the prompt defeats the training |
| batch | effective 16 via gradient accumulation | |
| completion-only loss | yes | mask the prompt; learn the emission, not the manifest |

If you exported DPO pairs, run a short DPO pass after SFT (beta 0.1, 1 epoch). Whether SFT-with-error-context or DPO helps more is an open question RFC-0666 expects this first run to answer; record what you find.

## 4. Evaluate honestly

Serve the tune, then score it with the same harness that scores any other model:

```bash
ollama create urml-3b -f Modelfile   # or llama-server with the GGUF export
urml-model eval --utterances-root conformance/llm-bridge/fixtures \
  --profile home --backend ollama --model urml-3b \
  --out conformance/llm-bridge/results/<date>/home-urml-3b.yaml
```

Score the untuned base model the same way first. The claim worth making is the delta: base vs tuned on `structural_pass_rate`, `semantic_pass_rate`, `revision_attempts_mean`. Numbers enter `docs/launch/claims-audit.md` only through the `make audit` transcription discipline, and only after they were actually measured.

## 5. Deployment pairing

Pair the tuned model with GBNF grammar-constrained decoding (`urml_llm_bridge.grammar`, the `llama_cpp` provider) in production: the grammar guarantees structural validity at decode time, the tune carries the semantic load, and the validator remains the gate either way. The bridge's validate-and-revise loop stays on; a good tune makes it cheap, not optional.
