---
rfc: 0260
title: language.stt_engine_class / tts_engine_class / translation_engine_class — declaring Layer-4 NL infrastructure
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-29
updated: 2026-06-12
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

# RFC-0260: `language.stt_engine_class` / `tts_engine_class` / `translation_engine_class`

## Summary

URML's Layer-4 natural-language interface declares `listen` and `speak` primitives whose execution requires speech-to-text, text-to-speech, and (for multilingual deployments) translation substrates. URML's manifest currently has no place to declare which engine implements each capability. This RFC adds three sibling fields under a new top-level `language` block, with closed enums for each engine class, an `engine_options` sub-block, and defines validator behavior. Optional. Backward compatible.

The surfaces that demanded this RFC are Move-12 RFCs 0153-0159 (Whisper, faster-whisper, whisper.cpp, OpenVoice, OPUS-MT, Argos Translate, Marian-NMT).

## Motivation

URML's Layer-4 NL grammar reserves multilingual slots (English, plus Spanish, Japanese, Mandarin grammars in v0.1). The `listen` primitive accepts speech input; `speak` produces speech output. Both are substrate-dependent: a deployment may use OpenAI Whisper for STT or whisper.cpp for embedded inference; OpenVoice for TTS or a different engine; OPUS-MT, Argos, or Marian-NMT for translation. URML's manifest has no field to declare these choices today.

Three concrete consequences:

1. **Substrate-neutrality is rhetorical at the NL layer.** URML's substrate-neutrality is asserted but the manifest cannot declare which STT engine the deployment composes with. A `listen` primitive against a Whisper-vs-whisper.cpp deployment behaves identically at the language level but materially differently at the latency and offline-capability level.
2. **Layer-4 grammars + Layer-3 dispatch boundary is undefined.** When `listen` produces text and that text compiles to Layer-2 primitives, the manifest needs to declare both the STT engine and the Layer-3 dispatch target. Without the field, downstream tooling cannot validate the pipeline.
3. **Multilingual deployments need translation declaration.** A drone deployment that accepts Hebrew commands and operates with English-only ROS topics needs `translation_engine_class` declared to validate that the pipeline composes correctly.

The Move-12 outreach wave (RFCs 0153-0168) surfaced all three engine-class declarations as recurring requests; this RFC bundles them because they're sibling fields with parallel validation rules.

## Detailed design

### Field shape

```yaml
language:                                    # NEW — this RFC, top-level optional
  stt_engine_class: whisper                  # whisper | faster_whisper | whisper_cpp | vosk | porcupine_handoff | custom
  tts_engine_class: openvoice                # openvoice | piper | mozilla_tts | espeak | custom
  translation_engine_class: opus_mt          # opus_mt | argos_translate | marian_nmt | nllb | libretranslate | custom
  engine_options:
    stt:
      inference_runtime: cpu                  # cpu | gpu | embedded
      quantization_level: int8                # fp32 | fp16 | int8 | int4
      latency_class: realtime                 # realtime | batched | offline
      model_size: small                       # tiny | base | small | medium | large
    tts:
      voice_id: default
      sample_rate_hz: 22050
    translation:
      source_languages: [en, he, es, ja, zh]
      target_languages: [en]
      offline_capable: true
```

### Allowed values

**STT engine class:**

| Value | Description | Reference |
|---|---|---|
| `whisper` | OpenAI Whisper (Python) | Move-12 RFC-0153 |
| `faster_whisper` | SYSTRAN faster-whisper (CTranslate2-accelerated) | Move-12 RFC-0154 |
| `whisper_cpp` | ggml-org whisper.cpp (embedded C++) | Move-12 RFC-0155 |
| `vosk` | alphacep/vosk-api | Excluded from URML default (Move-12 Tier C — Russian-origin per US-federal default policy); accepted as enum value for non-policy-gated deployments |
| `porcupine_handoff` | Picovoice Porcupine wake-word with downstream STT handoff | Move-12 RFC-0165 |
| `custom` | Vendor-specific or experimental STT | escape hatch + `stt_engine_class_note` required |

**TTS engine class:**

| Value | Description | Reference |
|---|---|---|
| `openvoice` | MyShell OpenVoice | Move-12 RFC-0156 |
| `piper` | OHF-Voice piper1-gpl | Move-12 RFC-0166 (GPL-3.0 subprocess-boundary) |
| `mozilla_tts` | Mozilla TTS | Cross-reference; predecessor track |
| `espeak` | eSpeak / eSpeak NG (lightweight, embedded) | Cross-reference |
| `custom` | escape hatch |

**Translation engine class:**

| Value | Description | Reference |
|---|---|---|
| `opus_mt` | Helsinki-NLP OPUS-MT | Move-12 RFC-0157 |
| `argos_translate` | argosopentech/argos-translate | Move-12 RFC-0158 |
| `marian_nmt` | marian-nmt/marian-dev | Move-12 RFC-0159 |
| `nllb` | Meta NLLB-200 (CC-BY-NC weights gate; manifest declares for cross-citation; not URML-default) | Move-12 RFC-0167 |
| `libretranslate` | LibreTranslate (AGPL-3.0 REST-boundary) | Move-12 RFC-0168 |
| `custom` | escape hatch |

### Schema fragment (Layer-1)

```jsonc
{
  "language": {
    "type": "object",
    "properties": {
      "stt_engine_class": {
        "enum": ["whisper", "faster_whisper", "whisper_cpp", "vosk", "porcupine_handoff", "custom"]
      },
      "stt_engine_class_note": { "type": "string" },
      "tts_engine_class": {
        "enum": ["openvoice", "piper", "mozilla_tts", "espeak", "custom"]
      },
      "tts_engine_class_note": { "type": "string" },
      "translation_engine_class": {
        "enum": ["opus_mt", "argos_translate", "marian_nmt", "nllb", "libretranslate", "custom"]
      },
      "translation_engine_class_note": { "type": "string" },
      "engine_options": {
        "type": "object",
        "properties": {
          "stt": { "$ref": "#/$defs/SttOptions" },
          "tts": { "$ref": "#/$defs/TtsOptions" },
          "translation": { "$ref": "#/$defs/TranslationOptions" }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional fields.** Missing fields acceptable. Deployments without `listen` / `speak` primitives in active programs don't need to declare engine classes.
2. **Required-when-primitive-used.** If the deployment's example programs include `listen`, `stt_engine_class` is recommended (soft suggestion at validate time). Same for `speak` ↔ `tts_engine_class`.
3. **`vosk` policy gate.** When `--policy` is active and the default-policy file is in effect, `stt_engine_class: vosk` fails validation per Move-12 Tier C (Russian-origin under URML's US-federal default policy). Without `--policy`, the value is accepted.
4. **Custom requires note** for each of the three engine classes.
5. **Translation language-list consistency.** `engine_options.translation.target_languages` must include at least one language; `source_languages` should include all languages the Layer-4 grammar accepts. Inconsistency is a soft warning.
6. **License-boundary cross-check.** When `tts_engine_class: piper`, the validator surfaces a warning about GPL-3.0 subprocess-boundary integration shape (cross-link to future RFC on license_boundary).
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read engine declarations for startup-log diagnostics and to select Layer-4 grammar dispatch. The runtime does not orchestrate the engines themselves; deployment-side tooling owns engine lifecycle.

### Conformance test additions

`conformance/tests/test_manifest_language_engines.py`:

1. Manifest without `language` block passes.
2. Manifest with `stt_engine_class: whisper` passes.
3. Manifest with `stt_engine_class: vosk` passes without `--policy`; fails with `--policy` against default policy.
4. Manifest with all three engine classes and full `engine_options` passes.
5. Manifest with `translation_engine_class: nllb` and `engine_options.translation.commercial_use_gate: true` produces a warning (CC-BY-NC weights).

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **Three sibling enums.** Per-engine-class lists are maintenance burden. Closed enum keeps each in check.
- **`vosk` value present in enum but policy-gated.** The schema accepts it; the default policy refuses it. The two-layer model (schema validates shape; policy validates substrate-permissibility) is consistent with how URML treats other policy-gated origins.
- **License-boundary cross-link is forward-reference.** This RFC mentions a future `license_boundary` RFC (Batch 4 candidate) without it landing first. The cross-link is documentation; nothing in this RFC depends on the future RFC landing.
- **Embedded inference declaration is partial.** `engine_options.stt.inference_runtime: embedded` plus `quantization_level: int4` captures the embedded posture; finer-grained device targeting (specific NPU / DSP) is out of scope for v0.1.

## Alternatives considered

1. **Three separate RFCs instead of bundled.** Considered. Bundling reads better because the three engine classes share parallel validation rules and `engine_options` sub-block. Split would triple the cross-reference burden for no gain.
2. **Nest under `substrate` instead of top-level `language` block.** Rejected. Language infrastructure is structurally separate from substrate; placing top-level matches the conceptual layering (Layer 4 ↔ substrate is a different axis from Layer 1 ↔ Layer 2).
3. **Free-string engine class values.** Rejected. Defeats validator-as-static-gate. Closed enum with `custom` escape hatch is URML convention.
4. **Single `engine_class` field with engine-type prefix (`stt:whisper` / `tts:openvoice` / `translation:opus_mt`).** Rejected. Three separate fields read cleanly and let validators target each independently.

## Prior art

- Move-12 outreach RFCs 0153-0168 — the wave that surfaced all three engine classes.
- URML Layer-4 spec (in `spec/layer-4-nl-grammar/`) — the grammar that consumes these engine declarations.
- URML Layer-2 primitive set (`listen`, `speak`) — the primitives whose execution depends on the engines declared here.

## Unresolved questions

1. **Engine pipelining.** A deployment may use whisper.cpp on-device for fast preliminary STT plus Whisper-API in the cloud for accuracy verification. URML's manifest is single-engine-per-class today; pipelining is future work.
2. **Multi-language STT on-device.** Whisper supports multilingual mode by default; whisper.cpp requires per-language model loading. URML's manifest does not capture this distinction today.
3. **Voice cloning declaration (TTS-specific).** OpenVoice does zero-shot voice cloning. URML's manifest could declare voice-cloning intent for envelope-validation. Future RFC.

## Implementation plan

1. JSON Schema fragment with three engine-class enums + `engine_options` sub-block.
2. Validator with the seven checks above.
3. Conformance tests (five).
4. Cross-link to default-policy file for `vosk` handling.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Shipped (Draft → Implemented, 2026-06-12)

Landed as the single additive Layer-1 block this RFC proposed (every existing
manifest stays valid; `manifest_version` stays `0.1`). It is the foundation of
the translation-licensing stack: RFC-0262 (licensing boundary), RFC-0268
(`deployment.commercial_use`), and RFC-0304 (the permissive-translation
alternative that serves the engaged NLLB maintainer, RFC-0167) build on the
`translation_engine_class` enum landed here.

- **Schema** (`manifest.py`): `Language` + `EngineOptions` / `SttOptions` /
  `TtsOptions` / `TranslationOptions`, and `CapabilityManifest.language`. Closed
  enums for all three engine classes; a `custom` value requires its `*_note`
  (intra-block `model_validator`). Spec: `spec/layer-1-hal/v0.2.0.md` §2.18.
- **Validator**: a Pass-2 `_check_language_static` (license advisories for
  piper / nllb / libretranslate; empty-translation-target-languages
  consistency) and `_check_language_primitives` (the `listen`/`speak`
  engine-undeclared soft suggestion); a Pass-5 `_check_language_origin_gate`
  (the `vosk` US-federal origin gate, fired only under the bundled default
  policy). Five new error codes (`policy.stt_engine_origin_denied`,
  `capability.stt_engine_undeclared`, `capability.tts_engine_undeclared`,
  `capability.translation_languages_inconsistent`,
  `capability.engine_license_advisory`).
- **Conformance**: `conformance/fixtures/language/` (whisper positive; vosk
  accepted no-policy; vosk rejected under default policy; full-engines positive;
  nllb positive) + four registered manifests.
- **Example**: `examples/language/multilingual-greeting` — a home robot that
  `listen`s and `speak`s, declaring Whisper / eSpeak / OPUS-MT; validates under
  the default policy and executes on the hermetic mock.
- **Tests**: `reference/validator/tests/test_language.py` (20 cases).

Two scoping notes. (1) The `vosk` gate is implemented as a manifest-static
Pass-5 check keyed on the default policy's `policy_id`, rather than as a
provenance-DSL rule, because the policy DSL operates on `provenance` components,
not the `language` block; this keeps RFC-0004's DSL unchanged. (2) The RFC's
conformance test 5 referenced `engine_options.translation.commercial_use_gate`;
that field belongs to RFC-0262 (not yet built), so the shipped nllb check is a
license *advisory* (warning) independent of a `commercial_use_gate` field. The
license-boundary cross-link (check 6) is likewise an advisory pending the
license-boundary RFC. Per-program enforcement and engine pipelining stay
deferred (Unresolved §1).

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (three enum maintenance, vosk policy-gated, license-boundary forward-reference, partial embedded declaration).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive (listen / speak already exist).
- [x] Conformance tests added (five).
- [x] Cross-references to 13 Move-12 outreach RFCs.
- [x] CLAUDE.md compliance: enum closure preserves substrate moat; policy-gating respects US-federal default for Russian-origin vosk; multilingual orientation honored.
