---
rfc: 0154
title: SYSTRAN faster-whisper (CTranslate2-accelerated Whisper inference) integration, request for comment from faster-whisper maintainers
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

# RFC-0154: SYSTRAN faster-whisper (CTranslate2-accelerated Whisper inference) integration, request for comment from faster-whisper maintainers

## Summary

URML does not yet ship a faster-whisper manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for SYSTRAN faster-whisper — the CTranslate2-accelerated Whisper inference engine that delivers realtime-class STT on commodity CPU and GPU — over [`SYSTRAN/faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (MIT), and **requests review and feedback from the faster-whisper maintainers**. No spec change.

faster-whisper is the realtime-latency substrate for URML's Layer-2 `listen` primitive. It is one of three Whisper-family RFCs in Move #12 batch 1 (RFC-0153 reference Whisper, this RFC, RFC-0155 whisper.cpp) that together cover the URML speech-input path on the three Whisper inference paths most likely to appear on real robots.

## Motivation

`SYSTRAN/faster-whisper` is the most-used realtime Whisper inference engine (MIT, 23.2k stars, Issues + Discussions both enabled, last commit `2025-11-19`, **not archived**). It uses CTranslate2 as its inference backend rather than the reference PyTorch implementation, which delivers 2-4× faster transcription on the same hardware with the same model weights.

The realtime profile is what makes faster-whisper interesting to URML, not the model:

1. **Realtime `listen` on resource-constrained robots.** URML's `listen` primitive cannot block the control loop. Reference Whisper's PyTorch path is too slow for "speak to the robot and have it move within one human-conversational turn". faster-whisper's CTranslate2 path closes that latency gap.
2. **Same model weights as reference Whisper.** A URML manifest declaring "Whisper-family STT" is portable across the three inference engines — what changes is the latency profile, not the language coverage. The manifest should model this cleanly.
3. **CPU-friendly.** faster-whisper runs the small / base / medium checkpoints at realtime on commodity laptop CPUs. URML's reference runtimes already target CPU-only deployment paths (Phase 1 hermetic-CI posture); CTranslate2 fits that constraint.

**Repo provenance note.** This project was originally hosted at `guillaumekln/faster-whisper`. SYSTRAN (Paris, FR) assumed maintainership; the canonical home is now [`SYSTRAN/faster-whisper`](https://github.com/SYSTRAN/faster-whisper). This RFC targets the SYSTRAN-hosted location.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `faster_whisper_listen_cell.yaml` fixture)

Manifest does not currently declare an STT-engine substrate or an inference-runtime. Proposed mapping uses the `custom` escape-hatch to declare both:

| URML field | Maps to faster-whisper attribute |
|---|---|
| `sensors[].type: speech` | Existing — declares speech sensor present |
| `sensors[].class: custom` (`stt_engine_family: whisper`) | Declares Whisper-family STT (shared with RFC-0153 / RFC-0155) |
| `sensors[].class: custom` (`stt_inference_runtime: ctranslate2`) | Declares CTranslate2 backend (this RFC's distinct contribution) |
| `sensors[].class: custom` (`stt_compute_type: int8 \| float16 \| float32`) | faster-whisper's quantization-level selector (one of CTranslate2's distinguishing features) |
| `sensors[].class: custom` (`stt_realtime_class: realtime \| near_realtime \| batch`) | Declares the latency class the deployment targets |

### What URML v0.1 does not yet express for faster-whisper

1. **STT inference-runtime declaration.** Shared with RFC-0153 / RFC-0155. URML's v0.1 has no field for which inference backend (PyTorch reference / CTranslate2 / ggml) processes the audio; the Whisper *family* is one declaration, the *runtime* is another.
2. **Quantization-level declaration.** CTranslate2's int8 / float16 / float32 compute-type selector is one of the distinguishing knobs that determines whether `listen` meets a robot's realtime budget. URML's manifest has no first-class field for STT-engine quantization.
3. **Latency-class declaration.** URML's manifest declares actuators with realtime control loops but does not declare sensor latency-classes. Declaring `stt_realtime_class` would let downstream validators (`urml validate`) flag when a non-realtime STT path is wired into a realtime behavior.

### Compatibility notes

- **Vendor org.** [`SYSTRAN`](https://github.com/SYSTRAN) — vendor-direct.
- **Flagship repo.** [`SYSTRAN/faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — MIT, 23.2k stars, Issues + Discussions both enabled, last commit `2025-11-19`, **not archived**.
- **Origin.** SYSTRAN (Paris, FR). Passes US-federal default policy (NATO / EU allied).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface; project moved from `guillaumekln/` to `SYSTRAN/` and continues to ship regular releases. Issues + Discussions both enabled, both used.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; STT-engine-class + STT-inference-runtime declaration Spec RFC queued (shared with RFC-0153 / RFC-0155).
- Reference runtime: future `reference/speech-bridge/FasterWhisperListenAdapter` (a CTranslate2-backed `listen` substrate) is the natural integration; can ship alongside the reference Whisper adapter as separate selectable backends.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Same-model-different-runtime fragmentation.** URML must clearly distinguish Whisper-the-family from Whisper-the-reference-runtime. Doing so requires the STT-engine-class + STT-inference-runtime Spec RFC to land first.
- **CTranslate2 is a transitive dependency.** The reference adapter will depend on `ctranslate2` (Python) and a `cuDNN`/`oneDNN`-style native runtime per platform. CPU-only-CI requires CPU build variants.
- **Realtime-class declaration is novel.** URML has not before declared sensor-side latency classes; the Spec RFC needs to argue that this is the right abstraction and not knob-creep.

## Alternatives considered

1. **Engage only the reference openai/whisper repo (RFC-0153) and treat the runtimes as implementation detail.** Rejected. The inference runtime is a deployment-defining choice for realtime robots; treating it as implementation detail loses the realtime-class declaration the manifest needs.
2. **Bundle this RFC into RFC-0153.** Rejected; SYSTRAN is the active maintainer, OpenAI is the reference; conflating them papers over a real engagement-channel difference.
3. **Bundle this RFC with RFC-0155 (whisper.cpp).** Rejected; CTranslate2 and ggml are distinct runtimes with distinct maintainers and distinct deployment profiles (Python+CTranslate2 vs. embedded C++).

## Prior art

- [`SYSTRAN/faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — the upstream repo.
- [`OpenNMT/CTranslate2`](https://github.com/OpenNMT/CTranslate2) — the inference backend.
- [RFC-0153 (openai/whisper)](0153-whisper-outreach.md) — sibling RFC, reference Whisper PyTorch implementation (Move-12 batch 1).
- [RFC-0155 (whisper.cpp)](0155-whisper-cpp-outreach.md) — sibling RFC, ggml-backed embedded Whisper (Move-12 batch 1).
- [RFC-0021 (On-device LLM bridge)](0021-on-device-llm-bridge.md) — URML's NL substrate that consumes the transcribed text.

## Unresolved questions

For the SYSTRAN faster-whisper maintainers:

1. **STT-inference-runtime declaration.** Would faster-whisper benefit from URML's manifest declaring the runtime explicitly (e.g., a README badge "URML manifest declares `stt_inference_runtime: ctranslate2`"), or is this internal detail that should stay opaque?
2. **Realtime-class declaration.** Does the faster-whisper team have a benchmarking convention for declaring "realtime on platform X" that URML's `stt_realtime_class` field could reference?
3. **Quantization declaration.** Is `int8 / float16 / float32` the right granularity, or should the manifest list specific CTranslate2 quantization presets (`int8`, `int8_float16`, `int8_bfloat16`, ...)?
4. **Adapter home.** URML-side adapter in URML's `reference/speech-bridge/`, contributed example in `SYSTRAN/faster-whisper/examples/`, or external bridge repo?
5. **Conformance listing.** Would the faster-whisper maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0154 ships as a single RFC document PR (Move-12 batch 1). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`SYSTRAN/faster-whisper` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `SYSTRAN/faster-whisper`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 23.2k stars, Issues + Discussions enabled, last commit 2025-11-19 active, isArchived: false).
- [x] Org migration noted (`guillaumekln/` → `SYSTRAN/`).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (runtime fragmentation, CTranslate2 dependency, novel realtime-class declaration).
- [x] Sibling RFC cross-links explicit (RFC-0153 whisper, RFC-0155 whisper.cpp).
- [x] No spec change proposed in this RFC.
