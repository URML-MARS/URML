---
rfc: 0304
title: language.translation_alternatives — declaring a commercial-eligible permissive translation substrate
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-01
updated: 2026-06-01
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

# RFC-0304: `language.translation_alternatives` — declaring a commercial-eligible permissive translation substrate

## Summary

RFC-0260 lets a manifest declare a single translation engine per deployment. RFC-0262 lets it declare that engine's license and a `commercial_use_gate`. RFC-0268 makes a commercial deployment paired with a gated component (NLLB-200's CC-BY-NC weights) a hard failure under `urml validate --policy`. The three together leave a commercial deployment that wants 200-language breadth with a dead end and no in-manifest path forward. This RFC adds the missing path: a new `open_llm` translation engine class for permissive-license open LLMs, and a `language.translation_alternatives` block that lets a deployment declare a commercial-eligible substrate alongside a license-gated primary. The validator then treats a declared permissive alternative as the satisfying answer to the commercial gate instead of failing outright. Optional. Backward compatible.

The surface that demanded this RFC is the NLLB-200 maintainer's own guidance on RFC-0167 (see Prior art): for a commercial path, pair NLLB with a permissive open LLM (the Qwen and Gemma families translate hundreds of languages under permissive licenses).

## Motivation

NLLB-200 covers 200 languages, more than any other open translation model. Its weights are CC-BY-NC 4.0. A research, education, or hobby deployment uses NLLB freely. A commercial deployment cannot, and RFC-0268 correctly fails it under `--policy`.

The current spec stops there. A maintainer who wants NLLB's breadth in a commercial product has no way to declare, in one manifest, both the breadth substrate (NLLB, for non-commercial contexts and for languages a permissive model covers poorly) and a commercial-eligible substrate (a permissive open LLM). The `custom` escape hatch can name a permissive LLM, but it carries no commercial-eligibility signal the validator can act on, so the deployment still fails the gate.

Two concrete consequences of the gap:

1. **The commercial gate is a dead end, not a fork.** RFC-0268 fails a commercial-plus-CC-BY-NC manifest. The right answer is not "fail" but "use the permissive alternative the deployment already declared." URML has no field for that alternative today.
2. **Permissive-LLM translation is invisible to the validator.** Permissive open LLMs (Qwen 3.5, Gemma 4) are a real translation substrate, recommended by the NLLB maintainer for exactly this case. Buried under `custom`, they carry no engine identity and no commercial-eligibility flag, so the validator cannot reason about them.

## Detailed design

### Field shape

```yaml
language:
  translation_engine_class: nllb                 # primary (RFC-0260); CC-BY-NC, 200-language breadth
  translation_alternatives:                       # NEW — this RFC, optional list
    - engine_class: open_llm
      engine_class_note: "Qwen3.5-Instruct, Apache-2.0"
      commercial_eligible: true
      source_languages: [en, he, es, ja, zh]
      target_languages: [en]
```

The `translation_alternatives` list sits inside RFC-0260's `language` block. Each entry reuses the `source_languages` / `target_languages` shape RFC-0260 already defines under `engine_options.translation`. The primary `translation_engine_class` is unchanged from RFC-0260; this RFC only adds substrates a deployment may fall back to.

### Allowed values

This RFC extends RFC-0260's `translation_engine_class` enum with one value, usable both as the primary class and as an `alternatives[].engine_class`:

| Value | Description | Reference |
|---|---|---|
| `open_llm` | A permissive-license open large language model used as a translation substrate (Qwen, Gemma, and similar families). Requires a note naming the specific model and license. | This RFC; surfaced by RFC-0167 maintainer guidance |

`open_llm` is added rather than reused from `custom` because the validator must distinguish a substrate with a known permissive-license posture from an opaque vendor escape hatch. A `custom` value tells the validator nothing about commercial eligibility; `open_llm` plus a `commercial_eligible` flag does.

`commercial_eligible` is a per-alternative boolean. It asserts that the named substrate carries a license permitting commercial deployment. The validator does not verify the claim against the model's actual license; this is a declaration, consistent with RFC-0268's declaration-not-verification stance. The deployment maintainer is responsible for the truth of the flag, and a corresponding `licensing.components[]` entry (RFC-0262) carries the formal license value and a `commercial_use_gate: false`.

### Schema fragment (Layer-1)

```jsonc
{
  "language": {
    "properties": {
      "translation_engine_class": {
        "enum": ["opus_mt", "argos_translate", "marian_nmt", "nllb", "libretranslate", "open_llm", "custom"]
      },
      "translation_alternatives": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["engine_class", "commercial_eligible"],
          "properties": {
            "engine_class": {
              "enum": ["opus_mt", "argos_translate", "marian_nmt", "nllb", "libretranslate", "open_llm", "custom"]
            },
            "engine_class_note": { "type": "string" },
            "commercial_eligible": { "type": "boolean" },
            "source_languages": { "type": "array", "items": { "type": "string" } },
            "target_languages": { "type": "array", "items": { "type": "string" } }
          },
          "if": { "properties": { "engine_class": { "enum": ["open_llm", "custom"] } } },
          "then": { "required": ["engine_class_note"] }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional list.** A missing `translation_alternatives` is acceptable. Deployments that declare no gated primary, or that are non-commercial, never need an alternative.
2. **`open_llm` and `custom` require a note.** An `alternatives[]` entry (or a primary `translation_engine_class`) of `open_llm` or `custom` without `engine_class_note` fails. This mirrors RFC-0260's `custom` rule and forces the deployment to name the model.
3. **Commercial-gate satisfaction (the new rule).** Under `--policy`, when `deployment.commercial_use: true` (RFC-0268) and the primary translation substrate has a matching `licensing.components[]` entry with `commercial_use_gate: true` (RFC-0262, the NLLB case), validation **passes** if and only if `translation_alternatives` contains at least one entry with `commercial_eligible: true` whose own `licensing.components[]` entry is not commercial-gated. The validator emits an informational message naming the alternative the commercial deployment must use. With no such alternative, behavior is unchanged from RFC-0268: hard failure.
4. **Consistency with the licensing block.** When an alternative declares `commercial_eligible: true` but its matching `licensing.components[]` entry declares `commercial_use_gate: true`, the validator fails on the contradiction. The two declarations must agree.
5. **No enforcement without `--policy`.** In default mode the commercial gate is informational (per RFC-0268); the alternative is recorded but nothing fails.
6. **Forward-compat.** Closed enum on `engine_class`.

### Reference-runtime behavior

Reference runtimes read `translation_alternatives` for startup-log diagnostics and to select which translation substrate to load given the deployment's commercial posture. The runtime does not enforce license terms at runtime; substrate selection and license compliance are static-validation and deployment-packaging concerns. URML's manifest declaring both substrates surfaces the audit trail.

### Conformance test additions

`conformance/tests/test_manifest_translation_alternatives.py`:

1. `nllb` primary, no alternatives, `deployment.commercial_use: true`, under `--policy` → fails (status quo from RFC-0268).
2. `nllb` primary plus an `open_llm` alternative with `commercial_eligible: true`, `deployment.commercial_use: true`, under `--policy` → passes, with an informational message naming the alternative (the new behavior).
3. `open_llm` as the primary class with a permissive (`commercial_use_gate: false`) licensing component, `commercial_use: true`, under `--policy` → passes.
4. A `translation_alternatives` entry with `engine_class: open_llm` and no `engine_class_note` → fails.
5. Non-commercial deployment (`commercial_use: false`), `nllb` primary, no alternatives, under `--policy` → passes (NLLB permitted non-commercially).

## Backward compatibility

Pre-v1.0. Additive. The new enum value and the new optional list do not affect existing manifests. A manifest that declares no `translation_alternatives` behaves exactly as it does under RFC-0268. No migration required.

## Drawbacks

- **Depends on three Draft RFCs.** This RFC composes on RFC-0260 (`language` block, base enum), RFC-0262 (`licensing.components` and `commercial_use_gate`), and RFC-0268 (`deployment.commercial_use`). All three are Draft. RFC-0304 lands after them, or alongside them in a sequenced batch; it does not stand alone.
- **`commercial_eligible` is a declaration, not a proof.** The validator does not check the named model's actual license. A maintainer can declare an ineligible model eligible. This matches RFC-0268's stance: URML is a static-validation tool, not an attestation engine. Cross-check rule 4 catches only the self-contradiction within the manifest.
- **One enum value for a moving target.** `open_llm` collapses a fast-moving model landscape (Qwen, Gemma, and successors) into one class, distinguished only by the free-text note. Finer-grained per-family declaration is deliberately out of scope; the note carries the specificity.
- **Single-tier fallback.** This RFC models one declared alternative set, not a priority-ordered chain of fallbacks. A deployment that wants "permissive-A, then permissive-B" expresses both as eligible alternatives without ordering; ordered preference is future work.

## Alternatives considered

1. **Leave permissive LLMs under `custom`.** Rejected. `custom` carries no commercial-eligibility signal the validator can act on, so the commercial gate stays a dead end. The maintainer of the substrate this RFC was built around recommended permissive LLMs explicitly; the path deserves a first-class engine identity.
2. **Fold the alternative into RFC-0260.** Rejected. RFC-0260 is single-engine-per-class by design (its first unresolved question defers pipelining), and the commercial-eligibility selection is a distinct validator behavior tied to RFC-0262 and RFC-0268, not to RFC-0260's engine-declaration concern. Bundling would entangle three review threads.
3. **General multi-engine pipelining.** Rejected for v0.1. A full pipeline model (on-device draft plus cloud verification, ordered fallback chains) is broader than the commercial-eligibility problem and is named as future work in RFC-0260. This RFC scopes only the commercial-eligible alternative.
4. **Per-program-run substrate swap.** Rejected. The manifest is deployment-static (consistent with RFC-0268's deployment-static commercial flag). Per-run substrate selection is future work.

## Prior art

- [RFC-0167 (fairseq / NLLB-200 outreach)](0167-fairseq-outreach.md) — the outreach RFC whose engagement produced this design input. The NLLB-200 maintainer, replying on the live successor surface (`facebookresearch/seamless_communication`, issue 578), confirmed CC-BY-NC 4.0 is the only NLLB-200 license and recommended permissive open LLMs (the Qwen and Gemma families) for a commercial translation path. This RFC turns that guidance into manifest structure.
- [RFC-0260 (language engine classes)](0260-language-engine-classes.md) — owner of the `language` block and the base `translation_engine_class` enum this RFC extends.
- [RFC-0262 (licensing boundary)](0262-licensing-boundary.md) — owner of `licensing.components` and `commercial_use_gate`, the license-side declaration this RFC's `commercial_eligible` flag pairs with.
- [RFC-0268 (deployment.commercial_use)](0268-deployment-commercial-use-flag.md) — owner of the commercial-deployment flag whose hard failure this RFC converts into a fork when an alternative is declared.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — the default-policy mechanism the `--policy` enforcement runs under.

## Unresolved questions

1. **Ordered fallback chains.** A deployment may want a preference order across several eligible alternatives. v0.1 declares an unordered set; ordering is future work.
2. **Per-language substrate routing.** A deployment may want NLLB for the long tail of languages and a permissive LLM for the common ones, routed per language pair. This RFC declares substrates, not per-pair routing. Future work.
3. **License-claim verification.** URML accepts the `commercial_eligible` declaration without checking the model's actual license. A future RFC could require attestation (a signed license reference) for federally-procured commercial deployments.

## Implementation plan

1. Extend the Layer-1 JSON Schema: add `open_llm` to the `translation_engine_class` enum and add the `translation_alternatives` array with its conditional note requirement.
2. Validator: the six checks above, with the commercial-gate-satisfaction rule (check 3) as a new branch in the RFC-0268 enforcement path.
3. Conformance tests (five).
4. Cross-link RFC-0260's enum table and RFC-0268's enforcement section to this RFC.

Single atomic PR, sequenced after (or batched with) RFC-0260 / RFC-0262 / RFC-0268.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (depends on three Draft RFCs, declaration-not-proof, one enum value for a moving target, single-tier fallback).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive (`listen` / `speak` already exist; this is a manifest-declaration field).
- [x] Conformance tests added (five).
- [x] Cross-references to the motivating outreach RFC (0167) and sibling Spec RFCs (0260, 0262, 0268, 0003).
- [x] CLAUDE.md compliance: substrate-neutral (the commercial-eligibility mechanism is license-driven, not vendor-driven); multilingual orientation honored (the point is keeping 200-language breadth reachable); Apache-2.0 stance preserved (permissive alternatives are the commercial path, no relicensing of anything in-repo); no LLM-provider lock-in (`open_llm` names a license posture, not a vendor).
