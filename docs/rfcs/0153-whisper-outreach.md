---
rfc: 0153
title: OpenAI Whisper (multilingual speech-to-text reference) integration, request for comment from openai/whisper maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0153: OpenAI Whisper (multilingual STT reference) integration, request for comment from openai/whisper maintainers

## Summary

URML does not yet ship a Whisper manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for OpenAI Whisper — the reference open-weights multilingual speech-to-text model — over [`openai/whisper`](https://github.com/openai/whisper) (MIT), and **requests review and feedback from the openai/whisper maintainers**. No spec change.

**This is URML's first Move-12 RFC** — the speech / translation / robot-command-library wave. Move #12 fills the gap left by Moves #1-#11 by engaging the projects on the input side of URML's Layer-4 natural-language grammar. Whisper is the obvious first surface: it is the de facto open-source baseline for speech-to-text and the closest single-repo target to URML's Layer-2 `listen` primitive (`input: speech`).

## Motivation

`openai/whisper` is the reference open-weights multilingual STT model (MIT, 100.8k stars, last commit `2026-04-15`, **not archived**). Whisper natively supports 99 languages, which directly addresses URML's Layer-4 multilingual structural slot reservation (English content, Hebrew / Spanish / Japanese / Mandarin reserved in v0.1).

URML benefits from documenting the Whisper manifest mapping because:

1. **Whisper is the closest single example of an STT engine that maps cleanly onto URML's Layer-2 `listen` primitive.** A robot operator speaks; Whisper transcribes; URML's Layer-4 NL grammar parses the transcript; URML compiles to typed primitives; URML's validator gates the resulting program before publish. The pre-flight check shape is the same one URML's natural-language bridge (RFC-0021) already implies.
2. **Whisper's multilingual coverage is the natural substrate for URML's reserved-but-empty multilingual slots.** A Layer-4 mapping that consumes Whisper transcripts can declare, per-language, which target NL grammar is active.
3. **URML sits above Whisper as the typed-intent layer, not in competition.** The same posture URML adopted toward HuggingFace LeRobot in Move-2 RFC-0040 and OpenVLA in Move-11 RFC-0138.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `whisper_listen_cell.yaml` fixture)

Manifest does not currently declare an STT-engine substrate; the closest existing structure is the `sensors` block (which declares `speech` as a sensor type per Layer-1). Proposed mapping uses the `custom` escape-hatch to declare a Whisper-class STT engine is present:

| URML field | Maps to Whisper attribute |
|---|---|
| `sensors[].type: speech` | Existing — declares speech sensor present |
| `sensors[].class: custom` (`stt_engine: whisper`) | Declares Whisper-family STT engine is the speech substrate |
| `sensors[].class: custom` (`stt_model: whisper-large-v3`) | Declares which Whisper checkpoint is loaded (`tiny`, `base`, `small`, `medium`, `large-v1` … `large-v3`, `large-v3-turbo`) |
| `sensors[].class: custom` (`stt_languages: [en, he, es, ja, zh]`) | Declares the active language set for transcription |
| `sensors[].class: custom` (`stt_decode_mode: transcribe \| translate`) | Whisper's two-mode operation (transcribe in source language vs. translate-to-English) |

### What URML v0.1 does not yet express for Whisper

1. **STT-engine class declaration.** URML's v0.1 manifest declares the `speech` sensor *type* but has no field for which STT *engine* is processing the audio. Spec RFC for STT-engine-class declaration is queued, shared with RFC-0154 (faster-whisper) and RFC-0155 (whisper.cpp). All three target the same Whisper model family with different inference engines, so the declaration needs both `stt_engine_family` (e.g., `whisper`) and `stt_inference_runtime` (e.g., `openai-reference`, `ctranslate2`, `ggml`).
2. **Language-list declaration.** URML's Layer-4 reserves multilingual slots but the manifest cannot today list which languages are active for the speech input path.
3. **Decode-mode declaration.** Whisper's `translate` mode (transcribe-to-English-from-source) is structurally distinct from URML's separate Layer-4 translation-engine layer (RFC-0157 OPUS-MT-train, planned). The manifest should not conflate them.

### Compatibility notes

- **Vendor org.** [`openai`](https://github.com/openai) — vendor-direct.
- **Flagship repo.** [`openai/whisper`](https://github.com/openai/whisper) — MIT, 100.8k stars, **Issues disabled (Discussions only)**, last commit `2026-04-15`, **not archived**.
- **Origin.** OpenAI (US, San Francisco). Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** OpenAI maintains the reference repo on a slower cadence than active community forks (faster-whisper, whisper.cpp). Architecture is stable; engagement-velocity should not be expected to match a daily-active project.
- **Engagement-channel friction.** Issues are disabled on `openai/whisper`. The supported engagement channel is GitHub Discussions; the URML post will land in the Q&A or Show-and-tell category, not as an Issue.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; STT-engine-class declaration Spec RFC queued in parallel (shared with RFC-0154 / RFC-0155).
- Reference runtime: future `reference/speech-bridge/WhisperListenAdapter` (a wrapper that consumes audio and emits transcripts into the existing `reference/llm-bridge/` NL pipeline) is the natural integration shape.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No code lands in this RFC.
- **Engagement-channel constrained.** Issues disabled means engagement is in Discussions, where the OpenAI maintainer presence is light. Realistic expectation: slow upstream response, value comes from URML's documented mapping more than from immediate dialogue.
- **STT-engine-class Spec RFC prerequisite** (shared with RFC-0154 / RFC-0155).
- **Inference-runtime fragmentation.** The Whisper model family ships through at least three engines (this RFC, faster-whisper, whisper.cpp). URML's manifest needs to model both the family and the runtime cleanly.

## Alternatives considered

1. **Skip the reference repo, engage only the active forks (faster-whisper, whisper.cpp).** Rejected. The reference repo is the canonical model-card source and the place model-release announcements land; URML's mapping should anchor to it even if engagement is slower.
2. **Bundle whisper + faster-whisper + whisper.cpp into one RFC.** Rejected. They are distinct projects with distinct maintainers and distinct engagement channels; the STT-engine-class Spec RFC is the natural place to surface their commonality, not a bundled outreach.
3. **Cross-citation only.** Considered. The mapping is concrete enough — STT-engine declaration is a real manifest gap — that an explicit outreach RFC is worth the maintainer time, not just a unilateral cross-citation.

## Prior art

- [`openai/whisper`](https://github.com/openai/whisper) — the upstream reference repo.
- [RFC-0154 (SYSTRAN faster-whisper)](0154-faster-whisper-outreach.md) — sibling RFC, CTranslate2-accelerated Whisper inference (Move-12 batch 1).
- [RFC-0155 (ggml-org whisper.cpp)](0155-whisper-cpp-outreach.md) — sibling RFC, embedded C++ Whisper inference (Move-12 batch 1).
- [RFC-0021 (On-device LLM bridge)](0021-on-device-llm-bridge.md) — URML's NL substrate that consumes Whisper transcripts.
- [RFC-0040 (HuggingFace LeRobot)](0040-huggingface-lerobot-outreach.md) — Move-2 sibling engagement, same URML-sits-above-substrate posture.

## Unresolved questions

For the openai/whisper maintainers:

1. **Engagement channel.** Discussions Q&A or Show-and-tell category? The URML post is a design-discussion request, not a bug report.
2. **STT-engine-class declaration shape.** Does the OpenAI Whisper team have a preferred convention for distinguishing the model family (`whisper`) from the inference runtime (`openai-reference` vs. CTranslate2 vs. ggml), if any?
3. **Multilingual labelling.** Whisper auto-detects source language; URML's manifest declares an explicit `stt_languages` list for static validation. Is the explicit list useful as a downstream signal, or is auto-detect the correct default?
4. **Decode-mode boundary.** Whisper's built-in `translate` mode overlaps URML's separate translation-engine layer (RFC-0157 OPUS-MT-train). Is one of these modes the canonical URML default, or should the manifest allow both?
5. **Cadence expectation.** Is `openai/whisper` actively monitoring Discussions, or is the active community on faster-whisper / whisper.cpp?
6. **Conformance listing.** Would the openai/whisper maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0153 ships as a single RFC document PR (Move-12 batch 1). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`openai/whisper` has Issues disabled. Discussions is the only supported engagement surface. URML's planned channel: open a single Discussion (Q&A category if design-question framing, Show-and-tell if the proposed adapter is the artifact), pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 100.8k stars, Issues disabled / Discussions enabled, last commit 2026-04-15 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (engagement-channel friction, Spec-RFC prerequisite, inference-runtime fragmentation).
- [x] Sibling RFC cross-links explicit (RFC-0154 faster-whisper, RFC-0155 whisper.cpp).
- [x] Engagement-channel constraint noted up front (Issues disabled).
- [x] No spec change proposed in this RFC.
