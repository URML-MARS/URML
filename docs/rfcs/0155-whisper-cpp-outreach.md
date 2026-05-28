---
rfc: 0155
title: ggml-org whisper.cpp (embedded C++ Whisper inference) integration, request for comment from whisper.cpp maintainers
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

# RFC-0155: ggml-org whisper.cpp (embedded C++ Whisper inference) integration, request for comment from whisper.cpp maintainers

## Summary

URML does not yet ship a whisper.cpp manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for whisper.cpp — the embedded C++ Whisper inference engine that runs the Whisper model family on edge / microcontroller / no-Python deployment paths — over [`ggml-org/whisper.cpp`](https://github.com/ggml-org/whisper.cpp) (MIT), and **requests review and feedback from the whisper.cpp maintainers**. No spec change.

whisper.cpp is the embedded substrate for URML's Layer-2 `listen` primitive on edge robots. It is one of three Whisper-family RFCs in Move #12 batch 1 (RFC-0153 reference Whisper, RFC-0154 faster-whisper, this RFC) that together cover the URML speech-input path across the three deployment profiles most likely to appear on real robots: reference research (PyTorch), realtime Python (CTranslate2), and embedded C++ (ggml).

## Motivation

`ggml-org/whisper.cpp` is the canonical embedded Whisper inference engine (MIT, 50.2k stars, Issues + Discussions both enabled, last commit `2026-05-28` — daily activity, **not archived**). It runs the Whisper model family through the ggml tensor library, which means no Python runtime, no PyTorch, no CUDA — just a C++ binary that links into existing robot software stacks.

The embedded profile is what makes whisper.cpp interesting to URML, not the model:

1. **No-Python `listen` on edge robots.** URML's reference runtimes already target Python-on-Linux deployment, but most embedded robotics stacks (PX4 NuttX, AUTOSAR Adaptive, vendor RTOSes) cannot host Python. whisper.cpp closes the Layer-2 `listen` path on those substrates.
2. **Microcontroller-class footprint.** whisper.cpp runs the `tiny` and `base` Whisper checkpoints on Raspberry Pi 4 and even on some Cortex-A class boards. URML's HAL (Layer 1) targets this hardware tier; the speech path should not require a workstation.
3. **Same model weights, different deployment path.** A URML manifest declaring "Whisper-family STT" is portable across the three engines (this RFC's `stt_inference_runtime: ggml` vs. RFC-0153 `openai-reference` vs. RFC-0154 `ctranslate2`). What changes is the deployment substrate, not the language coverage.

**Repo provenance note.** This project was originally hosted at `ggerganov/whisper.cpp`. The canonical home is now [`ggml-org/whisper.cpp`](https://github.com/ggml-org/whisper.cpp) — the `ggml-org` umbrella covers the ggml tensor library and its consumer projects (whisper.cpp, llama.cpp, …). This RFC targets the `ggml-org`-hosted location.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `whisper_cpp_listen_cell.yaml` fixture)

Manifest does not currently declare an STT-engine substrate or an inference-runtime. Proposed mapping uses the `custom` escape-hatch to declare both:

| URML field | Maps to whisper.cpp attribute |
|---|---|
| `sensors[].type: speech` | Existing — declares speech sensor present |
| `sensors[].class: custom` (`stt_engine_family: whisper`) | Declares Whisper-family STT (shared with RFC-0153 / RFC-0154) |
| `sensors[].class: custom` (`stt_inference_runtime: ggml`) | Declares ggml backend (this RFC's distinct contribution) |
| `sensors[].class: custom` (`stt_runtime_dependency_profile: no_python`) | Declares the deployment-substrate constraint (no Python interpreter required) |
| `sensors[].class: custom` (`stt_quantization: q4_0 \| q4_1 \| q5_0 \| q8_0 \| f16 \| f32`) | ggml's quantization scheme; smaller is faster on microcontroller-class CPUs |

### What URML v0.1 does not yet express for whisper.cpp

1. **STT inference-runtime declaration.** Shared with RFC-0153 / RFC-0154. URML's v0.1 has no field for which inference backend processes the audio.
2. **Runtime-dependency-profile declaration.** URML's manifest has no field declaring whether a sensor substrate requires a Python interpreter, libc only, or a custom RTOS. For edge deployment validation, this is the field that lets `urml validate` flag "this manifest declares Python-only STT but the target substrate is PX4 NuttX, which cannot host Python".
3. **ggml-quantization declaration.** whisper.cpp's quantization scheme is distinct from CTranslate2's (RFC-0154); URML's manifest needs a runtime-aware quantization field, not a runtime-agnostic one.

### Compatibility notes

- **Vendor org.** [`ggml-org`](https://github.com/ggml-org) — vendor-direct (the umbrella for the ggml library and its consumer projects).
- **Flagship repo.** [`ggml-org/whisper.cpp`](https://github.com/ggml-org/whisper.cpp) — MIT, 50.2k stars, Issues + Discussions both enabled, last commit `2026-05-28` (daily activity), **not archived**.
- **Origin.** Project originally led by Georgi Gerganov (Bulgaria, individual); now consolidated under the `ggml-org` umbrella. EU / individual; passes US-federal default policy (NATO / EU allied).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active surface (50.2k stars, daily commits). The ggml-org consolidation is recent; engagement should reference both the historic `ggerganov/` URL and the canonical `ggml-org/` URL.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; STT-engine-class + STT-inference-runtime + runtime-dependency-profile declaration Spec RFC queued (shared with RFC-0153 / RFC-0154 for the STT halves; the runtime-dependency-profile field is novel and may need its own Spec RFC).
- Reference runtime: future `reference/speech-bridge/WhisperCppListenAdapter` (a Python wrapper around the whisper.cpp binary via subprocess / pybind) is the natural integration; lets URML's Python-side reference runtime delegate transcription to a C++ binary on substrates where Python is itself absent.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Org migration noise.** The historic `ggerganov/whisper.cpp` URL is widely cited; URML's RFC needs to handle the migration cleanly so the URL doesn't bit-rot.
- **Subprocess / FFI boundary.** A Python-side reference adapter calls into the whisper.cpp binary via subprocess (or pybind), which adds a deployment-packaging concern URML's Python-only runtime doesn't otherwise have.
- **Runtime-dependency-profile declaration is novel.** URML has not before declared a "this substrate needs / doesn't need Python" constraint; the Spec RFC must argue this is the right abstraction.

## Alternatives considered

1. **Engage only the reference openai/whisper and faster-whisper repos.** Rejected. Embedded deployment is a real first-class robotics constraint; without whisper.cpp the URML speech-input path effectively requires Python, which closes the door on RTOS substrates.
2. **Bundle this RFC into RFC-0153.** Rejected; ggml-org is the active maintainer, OpenAI is the reference; conflating papers over a real engagement-channel difference.
3. **Cross-citation only.** Considered. Concrete enough (no-Python deployment is a real manifest gap) that an explicit RFC is worth maintainer time.

## Prior art

- [`ggml-org/whisper.cpp`](https://github.com/ggml-org/whisper.cpp) — the upstream repo.
- [`ggml-org/ggml`](https://github.com/ggml-org/ggml) — the inference backend.
- [RFC-0153 (openai/whisper)](0153-whisper-outreach.md) — sibling RFC, reference Whisper PyTorch implementation (Move-12 batch 1).
- [RFC-0154 (SYSTRAN faster-whisper)](0154-faster-whisper-outreach.md) — sibling RFC, CTranslate2-backed realtime Whisper (Move-12 batch 1).
- [RFC-0021 (On-device LLM bridge)](0021-on-device-llm-bridge.md) — URML's NL substrate that consumes the transcribed text.

## Unresolved questions

For the ggml-org whisper.cpp maintainers:

1. **STT-inference-runtime declaration.** Would whisper.cpp benefit from URML's manifest declaring the runtime explicitly (e.g., a README badge "URML manifest declares `stt_inference_runtime: ggml`"), or is this internal detail?
2. **Runtime-dependency-profile declaration.** Does the whisper.cpp team have a convention for documenting "this build requires libc only, no Python, no CUDA"? URML's `stt_runtime_dependency_profile` field would reflect that.
3. **ggml-quantization declaration.** Is the q4_0 / q4_1 / q5_0 / q8_0 / f16 / f32 enumeration the right granularity, or should it be a free-form ggml-quant-string?
4. **Adapter home.** URML-side adapter in URML's `reference/speech-bridge/` calling whisper.cpp via subprocess, contributed example in `whisper.cpp/examples/`, or external bridge repo?
5. **Org-migration handling.** Is `ggml-org/whisper.cpp` the URL that should be cited going forward, or is the historic `ggerganov/whisper.cpp` URL still the primary?
6. **Conformance listing.** Would the whisper.cpp maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0155 ships as a single RFC document PR (Move-12 batch 1). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`ggml-org/whisper.cpp` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `ggml-org/whisper.cpp`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 50.2k stars, Issues + Discussions enabled, last commit 2026-05-28 daily, isArchived: false).
- [x] Org migration noted (`ggerganov/` → `ggml-org/`).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (org-migration noise, FFI boundary, novel runtime-dependency-profile declaration).
- [x] Sibling RFC cross-links explicit (RFC-0153 whisper, RFC-0154 faster-whisper).
- [x] No spec change proposed in this RFC.
