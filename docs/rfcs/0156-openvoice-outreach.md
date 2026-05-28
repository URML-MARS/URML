---
rfc: 0156
title: MyShell OpenVoice (zero-shot voice cloning TTS) integration, request for comment from myshell-ai maintainers
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

# RFC-0156: MyShell OpenVoice (zero-shot voice cloning TTS) integration, request for comment from myshell-ai maintainers

## Summary

URML does not yet ship an OpenVoice manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for MyShell OpenVoice — the open-weights zero-shot voice cloning text-to-speech engine — over [`myshell-ai/OpenVoice`](https://github.com/myshell-ai/OpenVoice) (MIT), and **requests review and feedback from the OpenVoice maintainers**. No spec change.

**This is URML's first TTS RFC.** Layer-2 declares the `speak` primitive; v0.1 does not declare which TTS engine renders the output. OpenVoice is the first credible Tier A TTS substrate after the Coqui shutdown reduced the open TTS landscape, and its zero-shot voice-cloning capability addresses a fleet-consistency angle that single-voice TTS engines do not.

## Motivation

`myshell-ai/OpenVoice` is the active reference for open-weights zero-shot voice cloning (MIT, 36.6k stars, Issues + Discussions both enabled, last commit `2025-04-19`, **not archived**). The distinguishing feature is that a single reference voice clip lets the model generate consistent speech across arbitrary text inputs, in multiple languages, without per-voice training.

The voice-consistency angle is what makes OpenVoice interesting to URML, not the model:

1. **Fleet voice-consistency.** A robot fleet across multiple deployments can use the same reference voice clip so every robot speaks with one consistent identity. Without OpenVoice (or a similar zero-shot engine), each new deployment requires either picking from a fixed voice library or training a per-deployment voice — both impose lock-in URML's substrate-neutrality posture wants to avoid.
2. **Multilingual TTS.** OpenVoice supports cross-lingual cloning (clone a voice in English, then synthesize in another language). This pairs directly with URML's Layer-4 multilingual structural slot reservation and with the translation-engine path (RFC-0157 OPUS-MT-train).
3. **The Coqui-shutdown gap.** With `coqui-ai/TTS` last-pushed 2024-08-16 and Coqui-the-company defunct, the open neural-TTS landscape is now: OpenVoice, the GPL-licensed Piper successor (RFC-0166 OHF-Voice/piper1-gpl), and a handful of less-mature options. OpenVoice is the cleanest MIT-licensed option that survives the shutdown.

### Origin and domicile audit (cited explicitly to forestall conflation)

URML's outreach posture is US-federal aligned with NDAA Section 889 default-exclude for PRC-domiciled targets. MyShell.ai requires an explicit domicile audit because the founder team is CN-heritage and the broader investor / partner network includes mixed origins.

**Audit finding (verified 2026-05-28).** MyShell is US-domiciled (San Francisco, founded 2023). Crunchbase, CB Insights, and PitchBook concur on US headquarters. The OpenVoice paper was co-authored with MIT-the-institute (Cambridge, MA), not just MIT-the-license. Founders' names are CN-heritage but corporate domicile is US. **Verdict: passes URML's US-federal default policy.**

This audit is documented in [`examples/lighthouses/move12-research-2026-05-28.md`](../../examples/lighthouses/move12-research-2026-05-28.md) and cited here explicitly so the engagement does not get conflated with the PRC-domiciled exclusions in the same Move-12 wave (sherpa-onnx, F5-TTS).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `openvoice_speak_cell.yaml` fixture)

Manifest does not currently declare a TTS-engine substrate; the closest existing structure is the `actuators` block (for the audio-output actuator) plus the `speak` primitive in Layer 2. Proposed mapping uses the `custom` escape-hatch:

| URML field | Maps to OpenVoice attribute |
|---|---|
| `actuators[].type: audio_output` | Existing — declares audio output actuator present |
| `actuators[].class: custom` (`tts_engine: openvoice`) | Declares OpenVoice TTS engine is the speak substrate |
| `actuators[].class: custom` (`tts_voice_clone_ref: <path or url>`) | Declares the reference voice clip URI for fleet-consistent cloning |
| `actuators[].class: custom` (`tts_languages: [en, he, es, ja, zh]`) | Declares active language set for synthesis (mirrors the Layer-4 multilingual reservation) |
| `actuators[].class: custom` (`tts_voice_style: <preset>`) | Declares the active OpenVoice style preset (`default`, `friendly`, `cheerful`, ...) |

### What URML v0.1 does not yet express for OpenVoice

1. **TTS-engine class declaration.** URML's v0.1 manifest declares the `audio_output` actuator type but has no field for which TTS *engine* renders the speech. Spec RFC for TTS-engine-class declaration is queued (parallel to the STT-engine-class Spec RFC shared by RFC-0153 / RFC-0154 / RFC-0155).
2. **Voice-clone-reference declaration.** Zero-shot voice cloning requires declaring the reference clip URI as a manifest field. URML's manifest has no equivalent today; the closest analogue is sensor calibration-file URIs.
3. **TTS-language declaration.** Parallel to RFC-0153's `stt_languages` ask. URML's Layer-4 reserves multilingual slots; the manifest cannot today list which output languages are active.
4. **Voice-style declaration.** OpenVoice's style presets are an output-control surface URML's manifest has no declaration for.

### Compatibility notes

- **Vendor org.** [`myshell-ai`](https://github.com/myshell-ai) — vendor-direct.
- **Flagship repo.** [`myshell-ai/OpenVoice`](https://github.com/myshell-ai/OpenVoice) — MIT, 36.6k stars, Issues + Discussions both enabled, last commit `2025-04-19`, **not archived**.
- **Origin.** MyShell US-domiciled (San Francisco, founded 2023; Crunchbase / CB Insights / PitchBook concur). MIT-the-institute co-authored the paper. **Passes US-federal default policy.** Audit trail in [`move12-research-2026-05-28.md`](../../examples/lighthouses/move12-research-2026-05-28.md).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface (36.6k stars). Last commit ~13 months at time of RFC drafting; not stale by URML's 18-month rule but not daily-active either. MyShell.ai is the underlying company; engagement velocity may vary with their commercial priorities.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; TTS-engine-class declaration Spec RFC queued (will be drafted alongside the STT-engine-class Spec RFC so the speech-IO substrates are declared symmetrically).
- Reference runtime: future `reference/speech-bridge/OpenVoiceSpeakAdapter` (a `speak`-primitive substrate that consumes URML's text output and renders to audio) is the natural integration shape.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Domicile-audit defensiveness.** OpenVoice's PRC-conflation risk is real even though the audit passes; the RFC needs to surface the audit early to avoid the engagement being read as inconsistent with URML's exclude of sherpa-onnx and F5-TTS in the same wave.
- **TTS-engine-class Spec RFC prerequisite.** Parallel to but distinct from the STT-engine-class Spec RFC; both need to land for the speech-IO declarations to be coherent.
- **Voice-clone-reference is a privacy-adjacent field.** Declaring a reference voice clip URI in the manifest invites questions about consent, voice-identity provenance, and reuse. URML's default posture is "ship clean, document the field, defer the consent-framework discussion to the per-deployment operator decision".

## Alternatives considered

1. **Engage Piper-successor (RFC-0166) only as the canonical TTS path.** Rejected. piper1-gpl is GPL-3.0 which forces URML's reference adapter to call via IPC; OpenVoice is MIT and can compose more cleanly. Both are worth engaging.
2. **Skip TTS in Move-12 batch 1; defer to a later batch.** Rejected. The speech-IO substrate is incomplete if only STT lands; symmetry between `listen` and `speak` is part of why Move-12 exists.
3. **Bundle OpenVoice with Piper-successor into one TTS RFC.** Rejected. Different maintainers, different licenses, different deployment shapes (MIT-Python vs. GPL-binary-IPC).

## Prior art

- [`myshell-ai/OpenVoice`](https://github.com/myshell-ai/OpenVoice) — the upstream repo.
- [RFC-0166 (OHF-Voice piper1-gpl)](0166-piper1-gpl-outreach.md) — sibling TTS RFC for the Piper-successor (Move-12 Tier B; later batch).
- [RFC-0153 (openai/whisper)](0153-whisper-outreach.md) — sibling STT-side RFC; symmetric `listen` substrate (Move-12 batch 1).
- [RFC-0021 (On-device LLM bridge)](0021-on-device-llm-bridge.md) — URML's NL substrate; produces the text that OpenVoice renders.
- [RFC-0157 (Helsinki-NLP OPUS-MT-train)](0157-opus-mt-train-outreach.md) — sibling Move-12 RFC for the translation layer (cross-lingual TTS is the OpenVoice + OPUS-MT composition target).

## Unresolved questions

For the myshell-ai OpenVoice maintainers:

1. **TTS-engine-class declaration shape.** Does the OpenVoice team have a preferred convention for declaring "OpenVoice is the TTS engine" in a downstream manifest, or is this internal detail that should stay opaque?
2. **Voice-clone-reference declaration.** Is a manifest field that names the reference voice clip URI useful (for downstream consent/audit), or does it introduce a privacy footprint the project would rather not have associated with it?
3. **Voice-style enumeration.** Is the preset set stable enough for URML's manifest to declare an enum, or is it evolving fast enough that a free-form string is the right shape?
4. **Multilingual coverage.** OpenVoice supports cross-lingual cloning. What is the active set of synthesis languages URML's manifest should list (the README documents some; is the README authoritative)?
5. **Adapter home.** URML-side adapter in URML's `reference/speech-bridge/`, contributed example in `OpenVoice/examples/`, or external bridge repo?
6. **MyShell.ai engagement cadence.** Is the OpenVoice maintainer team funded by MyShell.ai-the-company or community-driven? URML's engagement-expectation calibration depends on this.
7. **Conformance listing.** Would the OpenVoice maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0156 ships as a single RFC document PR (Move-12 batch 1). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`myshell-ai/OpenVoice` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `myshell-ai/OpenVoice`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 36.6k stars, Issues + Discussions enabled, last commit 2025-04-19, isArchived: false).
- [x] Origin / domicile audit cited explicitly (US-domiciled MyShell SF, Crunchbase / CB Insights / PitchBook concur; passes US-federal default policy).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (domicile-audit defensiveness, Spec-RFC prerequisite, voice-clone privacy-adjacency).
- [x] Sibling RFC cross-links explicit (RFC-0166 piper1-gpl, RFC-0153 whisper, RFC-0157 opus-mt-train).
- [x] No spec change proposed in this RFC.
