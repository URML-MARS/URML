---
rfc: 0666
title: URML-native model, a dataset synthesis pipeline and training recipe for the on-device bridge
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-12
updated: 2026-07-12
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

# RFC-0666: URML-native model, a dataset synthesis pipeline and training recipe for the on-device bridge

## Summary

This RFC adds `reference/model` (`urml-model`), a pipeline that turns the repository's existing gold assets into a training dataset for a small open-weights language model that emits first-pass-valid URML. The validator is the labeling oracle: every synthesized `(natural language, program, manifest)` triple must pass `urml_validator.validate` before it enters the dataset, and every rejected bridge emission becomes a repair example paired with the validator's machine-readable errors. The RFC makes the dataset record schema and the evaluation protocol normative; the synthesis code, export formats, and the LoRA training recipe are reference material. Training itself happens outside the repository and no model weights are ever committed.

## Motivation

RFC-0021 committed URML to an on-device bridge story: translation must work without a cloud API key, on hardware a hobbyist owns. The measured reality is that generic small models struggle with URML. The project's first sustained user spent weeks fighting remote-LLM timeouts and local-model rejections before finding one 9B model that translates cleanly at a 128k context (Discussion #497). The bridge's revision loop papers over this at the cost of latency and tokens; `urml translate --save-rejected` exists because rejection is common enough to need a debugging workflow.

The repository already contains everything needed to fix this at the model level rather than the prompt level. The conformance suite holds over a hundred validator-accepted programs spanning every shipped profile. The few-shot library holds curated natural-language pairs. The validator emits namespaced, machine-readable error codes for every rejection. Together these are a verifiable-reward training signal: a candidate program is correct exactly when the validator accepts it, and when it is wrong the validator says why, in a form a training pipeline can use. No annotation vendor, no human labeling, no ambiguity about ground truth.

What is missing is the plumbing: mining the gold programs out of fixture files, pairing them with natural-language utterances, filtering everything through the oracle, and exporting in the formats fine-tuning frameworks consume. That plumbing is small, deterministic, and belongs in the open core, because a community that can regenerate the dataset can also extend it to new profiles and languages.

## Detailed design

### Overview

```
conformance/fixtures/**/*_positive.yaml   few_shot.py pairs      rejected bridge emissions
            |                                   |                        |
            v                                   v                        v
       mining.py  ------------------->  synthesize.py  <----------  rejections.py
                                              |
                              urml_validator.validate (the oracle)
                                              |
                                              v
                                       dataset.py (JSONL)
                                              |
                                              v
                                        export.py (SFT / DPO)
                                              |
                                              v
                       founder-run fine-tune (docs/training-recipe.md)
                                              |
                                              v
                    conformance llm-bridge scorer (existing, RFC-0021)
```

### Normative: the dataset record schema

A dataset is a JSONL file. Each line is one record with exactly these fields:

| field | type | meaning |
| --- | --- | --- |
| `nl` | string | The natural-language instruction. |
| `program` | object | The URML program the instruction should produce. |
| `manifest_ref` | string | Name of the capability manifest the pair validates against: a conformance `MANIFEST_REGISTRY` key, or the file stem of a validator manifest fixture for the few canonical manifests (the few-shot library's educational buggy) that predate the registry. |
| `profile` | string | The active URML profile. |
| `language` | string | BCP-47 tag of `nl` (`en` in v1). |
| `provenance` | string | One of `few_shot`, `fixture_backtranslation`, `llm_backtranslation`, `rejection_repair`. |
| `validator_verdict` | object | `{accepted: bool, error_codes: [string]}` as measured at synthesis time. |

Two optional fields: `envelope_ref` (the safety-envelope name when the validation context includes one, an `ENVELOPE_REGISTRY` key) and `repair` (see below).

Records with `validator_verdict.accepted == false` are permitted only for `rejection_repair` provenance, where the record additionally carries `repair` (the accepted program) and the error codes are the training signal. Every other record must be validator-accepted. A dataset containing a non-repair rejected record is malformed.

The schema is normative so that independently produced datasets compose: a third party can synthesize records for their own robot's manifest and merge them with the reference dataset without renegotiating field meanings.

### Normative: the evaluation protocol

A trained model is evaluated with the existing conformance llm-bridge scorer (RFC-0021), unchanged: `structural_pass_rate`, `semantic_pass_rate`, and `revision_attempts_mean` over a profile's utterance set, recorded as a `ResultRow`. A model claiming URML fluency reports these three numbers per profile, measured with the model plugged in as an ordinary `LLMProvider` (the `ollama` or `llama_cpp` adapter for local weights). No new metric is introduced; the point of training is to move numbers that already exist.

### Reference: package layout

New package `reference/model`, module `urml_model`, following the `reference/mcp-server` layout:

```
reference/model/
  pyproject.toml            urml-model; deps: urml-validator, urml-llm-bridge, urml-conformance, PyYAML
  src/urml_model/
    __init__.py             public API re-exports
    py.typed
    dataset.py              DatasetRecord, Dataset, JSONL read/write, split
    mining.py               mine_fixture_programs(), mine_few_shot_pairs()
    backtranslate.py        BackTranslator protocol, TemplateBackTranslator, LLMBackTranslator
    synthesize.py           synthesize(): oracle-filtered triple production, dedup
    rejections.py           mine_rejections(): TranslateResult/exception -> repair records
    export.py               export_sft() chatml/completions, export_dpo()
    cli.py                  urml-model synthesize | export | eval
  docs/training-recipe.md   the founder-run LoRA fine-tune recipe
  tests/
```

### Reference: mining

`mine_fixture_programs()` walks the conformance fixture registry via `urml_conformance.fixtures.discover_fixtures()` and keeps every single-robot case whose `expected_validation.accepted` is true, yielding the program, the resolved manifest, and the registry names. Fleet cases are excluded in v1 (their programs validate with `validate_fleet` and their prompt shape differs; see Unresolved questions).

`mine_few_shot_pairs()` converts the curated `few_shot.py` library into records. These pairs already carry natural language, so they skip back-translation and enter the dataset with `provenance: few_shot` after re-validation against the profile's canonical manifest.

### Reference: back-translation

Fixture programs have no paired utterance, so one is produced from the program. `BackTranslator` is a protocol with two implementations:

- `TemplateBackTranslator` renders deterministic English from the program's steps with per-primitive templates ("take off to 30 meters, fly to roof_north, take a photo, return home, land"). It is hermetic and runs in CI. Its output is stylistically narrow by design; it exists so the pipeline is testable end to end without a network and so the dataset floor never depends on an external model.
- `LLMBackTranslator` asks any `LLMProvider` for n paraphrases of the intent a program encodes. It is where dataset diversity comes from and it is founder-action at scale, run with whatever provider the operator configures. The pipeline treats its output identically: every candidate goes through the oracle.

Provider neutrality is preserved by construction: the pipeline names no vendor, and the hermetic path is the default.

### Reference: synthesis and the oracle

`synthesize()` takes mined gold examples and a back-translator, produces candidate records, validates each `(program, manifest, profile)` with `urml_validator.validate`, records the verdict, drops rejects (with a logged reason), and deduplicates on `(nl, canonical program JSON)`. The oracle call is not optional and not cached across schema versions: a dataset is only as trustworthy as the validator that filtered it, so the record carries the verdict measured at synthesis time.

### Reference: rejection mining

`mine_rejections()` consumes `TranslateResult` objects and `BridgeRevisionExhausted` / `BridgePolicyViolation` exceptions, both of which carry `raw_completions` (every attempt, not just the last). Each failed attempt whose session eventually produced an accepted program becomes a `rejection_repair` record: the failed emission, the validator's error codes for it, and the accepted program as the repair target. These records train the revision behavior directly and are also exportable as DPO preference pairs (accepted preferred over rejected, same prompt).

### Reference: export

`export_sft()` writes chat-format JSONL (system prompt built with the bridge's own `build_system_prompt` for the record's manifest, user turn = `nl`, assistant turn = the program as compact JSON) or bare completions format. `export_dpo()` writes `(prompt, chosen, rejected)` triples from repair records. Using the bridge's real prompt builder is deliberate: the model trains on exactly the prompt shape the bridge will hand it at inference time.

### Reference: the training recipe

`reference/model/docs/training-recipe.md` documents a LoRA supervised fine-tune of a small open-weights model (3B class) on the SFT export, followed by optional DPO on the repair pairs, with concrete hyperparameters and a walkthrough for a single rented GPU. The recipe ends by scoring the result with the conformance scorer and comparing against the untuned base. The recipe is documentation, not code; the repository never downloads weights, never trains in CI, and never commits a model artifact.

### Spec changes

None to Layers 1 through 4. The normative surface of this RFC is the dataset record schema and the evaluation protocol above, both of which live at the tooling layer.

### Validator changes

None. The validator is consumed as-is; its acceptance verdict and error codes are the pipeline's ground truth.

### Reference runtime changes

None.

### Conformance suite changes

None required for this RFC to land. Expanding utterance sets beyond the `home` profile improves evaluation coverage and is tracked as follow-on work, not a blocker.

## Backward compatibility

Fully additive. A new package, no changes to any existing module's behavior. Pre-v1.0, the dataset record schema may evolve with the program schema; a dataset is stamped by the validator version that filtered it (the verdict is re-measurable at any time by re-running synthesis).

## Drawbacks

The template back-translator produces a small, stylistically monotone corpus; a model trained only on it would overfit to one phrasing register. Real diversity requires the LLM back-translation path, which costs operator money and injects another model's phrasing distribution into the dataset. The dataset also inherits the fixtures' distribution: fixture programs were written to exercise validator checks, not to mirror what users ask for, so the pipeline's output is gold-correct but not usage-representative until organic utterances accumulate. Finally, shipping a recipe that names a base-model class invites "URML endorses model X" misreadings; the recipe text addresses this by treating the base model as a replaceable parameter.

## Alternatives considered

**Prompt-side fixes only (bigger few-shot sets, tighter grammar constraints).** The GBNF grammar path already guarantees structural validity, and it has not closed the semantic gap on small models: grammars cannot teach a model which capability a manifest actually declares. Rejected as insufficient, though grammar-constrained decoding remains the recommended deployment pairing.

**Human-annotated dataset.** Costs money the project does not have, introduces label noise the validator would then disagree with, and is unnecessary: the oracle's verdict is strictly more reliable than a human annotator's for this task.

**Hosting the pipeline outside the repository (separate repo or a hosted service).** Violates the adoption logic of the open core: the community that can regenerate and extend the dataset is the community that ports URML to new profiles. The pipeline is small, hermetic, and belongs beside the assets it mines.

**Committing a trained model or its weights.** Rejected outright: weights are provider-flavored, multi-gigabyte, unreviewable, and would rot with every spec version. The repository ships the recipe and the measurement harness; artifacts live wherever the operator publishes them.

## Prior art

RFC-0021 defined the on-device bridge, the provider adapters, and the scorer this RFC evaluates against. RFC-0630 and RFC-0665 are precedents for feeding measured small-model failure modes back into the project (both encode lessons from GoPiGo3 field use into few-shots and spec text; this RFC generalizes that loop). Outside the project: verifiable-rewards fine-tuning is standard practice where a mechanical checker exists (compilers, theorem provers, unit tests); URML's validator is exactly such a checker for robot intent. Back-translation for data augmentation is long-established in machine translation.

## Unresolved questions

- Multilingual scope: the natural-language layer is multilingual by commitment (examples in Hebrew, Spanish, Japanese, Mandarin since v0.1), but v1 of the pipeline emits English only. Whether template back-translation should grow per-language renderers or lean entirely on the LLM path is open.
- Repair records ship as SFT-with-error-context and as DPO pairs; which of the two the recipe should prefer first is an empirical question the founder's first training run will answer.
- Fleet programs (RFC-0286) are excluded from mining in v1. Including them needs a fleet-aware prompt shape in the export and `validate_fleet` in the oracle step.
- Dataset licensing: records derived from repo fixtures are Apache 2.0 alongside everything else; records produced by LLM back-translation inherit provider-terms questions that the recipe must surface to the operator.

## Implementation note

One vertical-slice PR: this RFC, the `reference/model` package with hermetic tests, Makefile and audit-script wiring, and the RFC index row. The founder then runs the LLM back-translation and the fine-tune off-repository, scores the result with the conformance scorer, and transcribes measured numbers through the `make audit` discipline. Nothing in the PR claims a trained model exists until one does.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] This RFC adds no Layer-2 primitive (substrate-neutrality acid test not applicable).
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
