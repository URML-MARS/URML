---
rfc: 0276
title: language.wake_word_substrate — declaring wake-word detection + STT handoff
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-30
updated: 2026-05-30
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

# RFC-0276: `language.wake_word_substrate` — wake-word detection + STT handoff

## Summary

RFC-0260 declared `language.stt_engine_class` covering speech-to-text engines (Whisper, faster-whisper, whisper.cpp, vosk, Porcupine handoff). The `porcupine_handoff` value implies a wake-word engine sits in front of the STT engine; that engine itself was not declared. Production always-on speech deployments use a low-power wake-word detector (e.g., "Hey URML") to gate the full STT path, conserving energy and bandwidth. This RFC adds `language.wake_word_substrate` as a sibling to `stt_engine_class`, with closed enum values, license-tier handling, and a handoff declaration that ties the wake-word detector to the downstream STT engine. Optional. Backward compatible.

The surface that demanded this RFC is Move-12 RFC-0165 (Picovoice Porcupine outreach).

## Motivation

URML's `listen` primitive accepts speech input. On a resource-constrained robot (or any always-on deployment), running Whisper continuously is energy-expensive. The standard pattern is:

1. A low-power wake-word detector listens always-on; on a "wake-word" detection, it triggers downstream STT.
2. The downstream STT engine wakes up, transcribes one utterance, and shuts down until the next wake-word.

URML's manifest cannot today declare either side of this pattern. Three concrete consequences:

1. **`stt_engine_class: porcupine_handoff` is incomplete.** RFC-0260 accepts the value but doesn't say what wake-word engine implements the front-end.
2. **License-tier matters for Porcupine.** Picovoice sells gated commercial tiers (Porcupine free for individual / non-commercial; paid for commercial deployments). URML's manifest needs to declare the license tier.
3. **Always-on / on-demand mode toggle.** Some deployments use wake-word-then-STT; others use push-to-talk (physical button → STT). URML's manifest should declare the activation mode.

## Detailed design

### Field shape

```yaml
language:                                    # block defined in RFC-0260
  wake_word_substrate: porcupine             # NEW — this RFC
  stt_engine_class: whisper                  # from RFC-0260; downstream of wake-word
  wake_word_options:
    activation_mode: wake_word                # wake_word | push_to_talk | always_on
    wake_phrases: ["hey urml", "robot listen"]
    license_tier: free_personal              # free_personal | commercial_paid | enterprise | none
    license_key_reference: env:PV_ACCESS_KEY  # secret reference (RFC-0262 convention)
    sensitivity: 0.5                          # 0.0 (strict) .. 1.0 (lenient)
    handoff_to_stt: true                      # whether wake-word triggers the stt_engine_class
```

### Allowed values for `wake_word_substrate`

| Value | Description | Reference |
|---|---|---|
| `porcupine` | Picovoice Porcupine | Move-12 RFC-0165 |
| `precise` | Mycroft Precise (deprecated upstream but still deployed) | Cross-reference |
| `openwakeword` | OpenWakeWord (community open-source) | Cross-reference |
| `snowboy` | Snowboy (archived but still deployed in legacy systems) | Cross-reference |
| `custom` | Vendor-specific or experimental | escape hatch + `wake_word_substrate_note` required |
| `none` | No wake-word stage; STT runs continuously or per push-to-talk | n/a |

### `activation_mode` enum

| Value | Description |
|---|---|
| `wake_word` | Wake-word detector listens; on detection, hands off to STT |
| `push_to_talk` | Physical input (button, gesture, GPIO) triggers STT directly |
| `always_on` | STT runs continuously; no wake-word gating |

### `license_tier` enum

| Value | Description |
|---|---|
| `free_personal` | Free tier (Porcupine's free-for-personal-use) |
| `commercial_paid` | Paid commercial license |
| `enterprise` | Enterprise license with custom terms |
| `none` | No license tier (for community open-source engines like OpenWakeWord) |

### Schema fragment (extending RFC-0260's language block)

```jsonc
{
  "language": {
    "properties": {
      "wake_word_substrate": {
        "enum": ["porcupine", "precise", "openwakeword", "snowboy", "custom", "none"]
      },
      "wake_word_substrate_note": { "type": "string" },
      "wake_word_options": {
        "type": "object",
        "properties": {
          "activation_mode": {
            "enum": ["wake_word", "push_to_talk", "always_on"]
          },
          "wake_phrases": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1
          },
          "license_tier": {
            "enum": ["free_personal", "commercial_paid", "enterprise", "none"]
          },
          "license_key_reference": { "type": "string" },
          "sensitivity": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "handoff_to_stt": { "type": "boolean" }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional field.** Missing `wake_word_substrate` means no wake-word stage; deployment uses STT engine directly (`activation_mode: always_on` or `push_to_talk` semantics).
2. **`activation_mode: wake_word` requires `wake_word_substrate`** other than `none`. Mismatch fails.
3. **Porcupine + commercial deployment cross-check.** When `wake_word_substrate: porcupine` AND `deployment.commercial_use: true` (RFC-0268) AND `license_tier: free_personal`, the validator emits a warning surfacing the license-tier mismatch.
4. **`license_key_reference` opacity.** The validator does not dereference the secret (per RFC-0262 secret-reference convention).
5. **Wake-phrases minimum.** When `activation_mode: wake_word`, at least one wake_phrase must be declared.
6. **Handoff consistency.** When `handoff_to_stt: true`, `stt_engine_class` (RFC-0260) must be declared.
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read the wake-word block to spawn the wake-word detector process. On wake-word detection, the runtime triggers the STT engine. The handoff implementation is per-substrate (Porcupine has its own callback API; OpenWakeWord exposes a different one).

### Conformance test additions

`conformance/tests/test_manifest_wake_word.py`:

1. Manifest without `wake_word_substrate` passes (STT runs without wake-word stage).
2. Manifest with `wake_word_substrate: porcupine + activation_mode: wake_word + wake_phrases: ["hey urml"]` passes.
3. Manifest with `wake_word_substrate: porcupine + deployment.commercial_use: true + license_tier: free_personal` passes with warning.
4. Manifest with `activation_mode: wake_word` and no `wake_word_substrate` fails (or `wake_word_substrate: none`).
5. Manifest with `handoff_to_stt: true` and no `stt_engine_class` fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests without wake-word declarations unchanged.

## Drawbacks

- **Five-value enum may grow.** Speech-detection upstream landscape evolves; new wake-word substrates appear. The `custom` escape hatch holds.
- **License-tier enum is Porcupine-shaped.** Other substrates have different commercial tier structures (OpenWakeWord is uniformly free; Precise was deprecated mid-tier; Snowboy was acquired-and-discontinued). URML's enum is a coarse fit.
- **Sensitivity is a single float.** Some wake-word substrates expose per-phrase sensitivity; URML's manifest is single-value at v0.1.
- **`activation_mode: always_on` is real but rare.** Listed for completeness; most production deployments use wake_word or push_to_talk.

## Alternatives considered

1. **Bundle `wake_word_substrate` under `stt_engine_class: porcupine_handoff` as a sub-field.** Rejected. Wake-word and STT are structurally separate engines; sibling fields read cleaner.
2. **Skip `license_tier`; rely on RFC-0262's licensing block.** Considered. The license tier is Porcupine-specific (commercial vs free) and benefits from declaration alongside the substrate identity. Sibling RFC-0262 covers component licenses; this RFC covers the commercial-tier dimension specifically.
3. **Skip `wake_phrases` declaration; let the substrate handle phrase configuration internally.** Rejected. Wake phrases are deployment-critical (the operator chose "hey urml"; another deployment chose "robot listen"); the manifest declaring them is part of the deployment contract.
4. **Combine wake-word + push-to-talk into `intent_trigger_mode`.** Considered. Push-to-talk and wake-word are different mechanisms (one is hardware GPIO, one is speech). Combining loses precision.

## Prior art

- [Move-12 RFC-0165 (Picovoice Porcupine outreach)](0165-porcupine-outreach.md) — outreach RFC that surfaced this field.
- [RFC-0260 (language engine classes)](0260-language-engine-classes.md) — parent Spec RFC; `stt_engine_class: porcupine_handoff` value pairs with this RFC's `wake_word_substrate: porcupine`.
- [RFC-0262 (licensing.boundary)](0262-licensing-boundary.md) — sibling Spec RFC; license_tier complements components-level license declaration.
- [RFC-0268 (deployment.commercial_use)](0268-deployment-commercial-use-flag.md) — cross-check field for Porcupine commercial-tier validation.

## Unresolved questions

1. **Custom wake-phrase training declaration.** Porcupine allows custom wake-phrase training via paid tier; URML's manifest could declare training data references. Future RFC.
2. **Multi-language wake-word.** Some substrates support multi-language wake-word; URML's manifest doesn't capture per-language sensitivity today.
3. **Wake-word-to-multi-STT routing.** Some deployments route different wake phrases to different STT engines. URML's manifest is single-STT today.

## Implementation plan

1. JSON Schema fragment extending RFC-0260's language block.
2. Validator with six checks.
3. Conformance tests (five).
4. Runtime wake-word-detector lifecycle hooks.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (enum growth, Porcupine-shaped license tier, single sensitivity, rare always_on).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0260, RFC-0165, RFC-0262, RFC-0268.
- [x] CLAUDE.md compliance: substrate-neutrality preserved across wake-word substrates; commercial-license tier surfaced honestly.
