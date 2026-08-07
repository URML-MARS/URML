---
rfc: 0670
title: Speech front-end for the LLM bridge
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-08-07
updated: 2026-08-07
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

# RFC-0670: Speech front-end for the LLM bridge

## Summary

`urml translate --audio request.wav` and `urml run --audio request.wav`: transcribe a spoken request with a speech-to-text provider, echo the transcript to stderr, and feed it into the exact translate path a typed request takes. A `SpeechProvider` protocol (one `transcribe` method, structural typing) mirrors the `LLMProvider` contract, with three adapters: **whisper.cpp** (`whisper-server`, on-device, the default), **OpenAI** (the transcription API, or any OpenAI-compatible endpoint via base URL), and **echo** (hermetic canned transcript for tests and demos). No spec change: speech sits strictly in front of Layer 4, producing the natural-language text the layer already consumes.

## Motivation

The headline path is one English sentence making a robot move, and since the local LLM providers became first-class CLI citizens, that path runs fully offline. The input was still typed text. Speech closes the loop: say the sentence, the robot moves, zero cloud. whisper.cpp is the natural default backend: the same project family as llama.cpp, the same GGML/GGUF on-device posture as RFC-0021, and multilingual out of the box, which matches Layer 4's multilingual-by-design stance (a Hebrew or Japanese speaker can talk to their robot without an English detour).

## Detailed design

**The contract.** `urml_llm_bridge.speech.base.SpeechProvider`: a runtime-checkable Protocol with one method, `transcribe(*, audio: bytes, filename: str = "audio.wav", language: str | None = None) -> str`. Structural typing, no registration, hand-rolled fakes work in tests. WAV (16 kHz mono PCM) is the recommended interchange format.

**The safety posture.** The transcript feeds `Bridge.translate()` unchanged, so the validator boundary is untouched. A mistranscription produces a wrong request, and the validator gates the resulting program exactly as it gates a wrong typed request: nothing actuates without passing static verification against the manifest and envelope. The CLI echoes the transcript to stderr before translation so the user sees what was heard before the LLM does. An empty transcript is rejected outright.

**Adapters.**

- `speech/whisper_cpp.py`: multipart POST to `whisper-server`'s `/inference` endpoint with `response_format: json`, temperature 0.0, optional `language` hint. Default base URL `http://127.0.0.1:8080` (upstream default; llama-server shares that port, a deployment running both moves one). Lazy `httpx` behind the `[whisper_cpp]` extra, injectable client for hermetic tests, and the same friendly dead-server `ConnectionError` the LLM adapters grew.
- `speech/openai.py`: `client.audio.transcriptions.create` via the openai SDK (lazy, `[openai]` extra), default model `whisper-1`. `base_url` targets any OpenAI-compatible transcription server, with the same key relaxation as the chat provider: a base URL stands in for `OPENAI_API_KEY` and a placeholder key satisfies the SDK.
- `speech/echo.py`: returns a canned string. The speech twin of `EchoProvider`; keeps the audio path exercisable in CI and demos with no model on the host.

**CLI surface.** The positional REQUEST becomes optional on `translate` and `run`; `--audio PATH` replaces it and the two are mutually exclusive. Speech flags live in one `_add_speech_args` helper shared by both subcommands: `--speech-provider {whisper_cpp, openai, echo}` (default `whisper_cpp`), `--speech-base-url`, `--speech-model`, `--speech-language`, `--echo-transcript`. Usage errors exit 2; transcription failures exit 1 with a `speech provider error:` line.

## Alternatives considered

- **faster-whisper / CTranslate2 as an in-process adapter.** A heavy Python dependency tree against the bridge's zero-hard-deps posture. Server-based whisper.cpp keeps the adapter to httpx, and faster-whisper deployments already expose OpenAI-compatible endpoints the `openai` speech provider reaches with `--speech-base-url`.
- **A separate `urml listen` verb with microphone capture.** Deferred. Microphone capture is platform-dependent (PortAudio and friends) and belongs behind its own decision once the file path proves out. `--audio` composes with any recorder (`arecord`, `sox`, a phone).
- **Speech inside the Layer-4 spec.** Rejected. Layer 4 consumes natural-language text; where the text comes from is tooling. Keeping speech out of the normative surface means transcription backends can churn without spec revisions.
- **A combined `--provider` for speech and LLM.** Rejected. Translation and transcription are chosen independently in practice (a local whisper with a cloud LLM is a sensible pairing, and vice versa).

## Prior art

- RFC-0021 established the on-device adapter pattern this RFC copies: lazy httpx, injectable clients, opt-in extras, per-backend defaults matching upstream.
- The Move #12 speech and translation outreach wave (RFCs 0152 through 0167) mapped the speech-vendor landscape; Meta's Seamless team engagement (RFC-0167, RFC-0304) validated the multilingual intent path.
- whisper.cpp's `whisper-server` and OpenAI's transcription API are the two dominant self-hosted and hosted transcription surfaces; both are covered here.

## Implementation

Shipped with this RFC in one PR: the `speech/` subpackage with the three adapters and 14 hermetic provider tests, the CLI flags on `translate` and `run` with 10 hermetic CLI tests, the `[whisper_cpp]` extra, tutorial and README updates, and this document.

## Open questions

- Microphone capture (`urml listen`): worth a verb once there is user pull.
- A conformance sub-suite for speech (per-model word-error tolerance on the canonical utterance set), mirroring the RFC-0021 per-model LLM scoring: deferred until more than one deployment asks for it.
