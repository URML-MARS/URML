---
rfc: 0166
title: OHF-Voice piper1-gpl (GPL-3.0 neural TTS, Piper successor) integration, request for comment from OHF-Voice maintainers
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

# RFC-0166: OHF-Voice piper1-gpl (GPL-3.0 neural TTS, Piper successor) integration, request for comment from OHF-Voice maintainers

## Summary

URML does not yet ship a piper1-gpl manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Piper — the lightweight neural TTS engine, now hosted under the Open Home Foundation as `piper1-gpl` — over [`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) (**GPL-3.0**), and **requests review and feedback from the OHF-Voice maintainers**. No spec change.

**This is a Move-12 Tier B RFC with one explicit friction note**: piper1-gpl is GPL-3.0, which is strong copyleft. URML's Apache-2.0 reference runtimes cannot statically link or embed GPL-3.0 code without contaminating URML's license posture. The integration shape is therefore **IPC-only**: URML acts as a neighbor process that invokes Piper via subprocess (or a domain-socket / HTTP boundary), never as a library caller. **Completes Move-12** (all 16 engageable RFCs drafted after this PR).

## Motivation

`OHF-Voice/piper1-gpl` is the active successor to the archived `rhasspy/piper` (GPL-3.0, 4.2k stars, Issues + Discussions both enabled, last commit `2026-04-07`, **not archived**). Piper is a lightweight VITS-based neural TTS that supports 75+ languages, runs on CPU at realtime on a Raspberry Pi 4, and ships a clean command-line interface alongside its Python library.

Piper is the surviving open neural-TTS substrate after the Coqui shutdown:

1. **The Coqui-shutdown gap.** With `coqui-ai/TTS` last-pushed 2024-08-16 and Coqui-the-company defunct, the open neural-TTS landscape narrowed to OpenVoice (RFC-0156) and Piper-or-its-successor. OpenVoice is MIT-clean; Piper carries the GPL-3.0 friction but covers languages OpenVoice does not (and has a smaller resource footprint).
2. **IPC-friendly architecture.** Piper ships a clean CLI (`piper --model en_US.onnx`) that accepts text on stdin and emits raw audio on stdout. The URML integration shape — `subprocess.Popen(["piper", ...])` — preserves the GPL/Apache license boundary cleanly.
3. **Resource footprint that matches RFC-0155's runtime profile.** Piper runs on the same Cortex-A / Raspberry Pi class hardware whisper.cpp targets. The speech-IO loop (Porcupine wake-word → whisper.cpp STT → URML processing → Piper TTS) closes on a single low-power Linux board.

URML's outreach is **light-touch**: the engagement frames URML as a *neighbor* of Piper, not a caller of Piper's library. The maintainers' response on whether that framing is correct is the primary value of this RFC.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `piper_tts_cell.yaml` fixture, IPC-bounded)

Manifest does not currently declare a TTS-engine substrate or an IPC-bounded substrate. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0156 OpenVoice):

| URML field | Maps to Piper attribute |
|---|---|
| `actuators[].type: audio_output` | Existing — declares audio output actuator present |
| `actuators[].class: custom` (`tts_engine: piper`) | Declares Piper is the TTS substrate |
| `actuators[].class: custom` (`tts_runtime: piper1_gpl`) | Declares the specific Piper repo (distinguishes from archived rhasspy/piper) |
| `actuators[].class: custom` (`tts_invocation_mode: subprocess \| domain_socket \| http`) | **Declares the IPC boundary** — URML never embeds Piper in-process |
| `actuators[].class: custom` (`tts_license_boundary: gpl_subprocess`) | Declares the GPL-3.0 boundary constraint; validator-enforceable that URML's build does not link Piper |
| `actuators[].class: custom` (`tts_voice_model: <model-name>`) | Declares the active Piper voice model (e.g., `en_US-lessac-medium`) |
| `actuators[].class: custom` (`tts_languages: [en, de, es, ja, zh, ...]`) | Declares active language set (mirrors Layer-4 multilingual reservation) |

### What URML v0.1 does not yet express for Piper

1. **TTS-engine class declaration.** Shared with RFC-0156 OpenVoice. URML's v0.1 manifest has no TTS-engine field.
2. **IPC-boundary declaration.** URML's v0.1 manifest assumes in-process substrate invocation. A `tts_invocation_mode: subprocess \| domain_socket \| http` declaration with the explicit license-boundary framing is structurally new (related to but distinct from RFC-0168 LibreTranslate's network-endpoint boundary).
3. **License-boundary declaration for substrates.** RFC-0168 surfaced the field for network endpoints; this RFC surfaces the field for subprocess boundaries (`gpl_subprocess`). The Spec RFC for license-boundary declaration should cover both cases.
4. **Repo-successor handling.** The predecessor `rhasspy/piper` is archived. URML's manifest must distinguish the canonical successor (`piper1_gpl`) from the historical name; the declaration prevents documentation rot.

### Compatibility notes

- **Vendor org.** [`OHF-Voice`](https://github.com/OHF-Voice) — vendor-direct (Open Home Foundation).
- **Flagship repo.** [`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) — **GPL-3.0**, 4.2k stars, Issues + Discussions both enabled, last commit `2026-04-07`, **not archived**.
- **Predecessor.** [`rhasspy/piper`](https://github.com/rhasspy/piper) — archived 2025-08-26. URML's RFC explicitly targets the OHF-Voice successor.
- **Origin.** Open Home Foundation (US-led non-profit). Passes US-federal default policy.
- **License fit.** GPL-3.0 = strong copyleft. **IPC-only integration**; URML never embeds. The Apache-2.0 stance is preserved.
- **Maintainer signal.** Active surface; OHF-Voice is well-funded (Home Assistant community sponsorship). Engagement-velocity should be moderate-to-high.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. Two Spec RFCs queued: TTS-engine-class declaration (shared with RFC-0156); license-boundary declaration (RFC-0166 surfaces the `gpl_subprocess` variant; RFC-0168 already surfaced the `agpl_network_boundary` variant; the Spec RFC unifies them).
- Reference runtime: future `reference/speech-bridge/PiperSpeakAdapter` (a subprocess wrapper that invokes Piper via stdin/stdout and emits the audio for URML's audio_output actuator) is the natural integration shape. **URML's build pipeline must verify** the adapter never imports Piper as a Python module.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 friction.** URML must enforce the subprocess boundary at the build level. A future contributor who naively `import piper` from URML's reference runtime breaks the license posture.
- **Subprocess overhead.** Subprocess invocation adds latency vs. in-process — a few tens of ms per utterance. For most robot speech-output use cases this is acceptable; for tightly-timed interaction loops it may be a constraint.
- **Two Spec RFCs prerequisite.** TTS-engine-class (shared with RFC-0156) and license-boundary (shared with RFC-0168) both need to land.
- **Repo-successor naming.** URML's manifest declares `tts_runtime: piper1_gpl` to be explicit about the post-rhasspy successor. The naming may need to evolve if OHF-Voice rebrands.

## Alternatives considered

1. **Engage OpenVoice (RFC-0156) only and skip Piper entirely.** Rejected. OpenVoice and Piper cover overlapping but different language sets and footprints; deployments may legitimately want either. URML's manifest should let them declare which.
2. **Engage Piper but as a Python library (statically-linked).** Rejected explicitly. GPL-3.0 + Apache-2.0 static linking contaminates URML's license posture. The IPC framing is the only clean shape.
3. **Bundle this RFC with RFC-0156 OpenVoice.** Rejected. Different maintainers, different licenses, different deployment shapes (MIT-Python in-process vs. GPL-binary IPC).
4. **Engage the archived `rhasspy/piper` upstream directly.** Rejected. Archived; engagement has nowhere to land. OHF-Voice is the active successor.
5. **Cross-citation only.** Considered. The GPL-boundary declaration is novel enough that an explicit RFC is worth maintainer time.

## Prior art

- [`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) — the upstream successor.
- [`rhasspy/piper`](https://github.com/rhasspy/piper) — the archived predecessor.
- [`OHF-Voice/wyoming-piper`](https://github.com/OHF-Voice/wyoming-piper) — Wyoming-protocol wrapper (Home Assistant integration).
- [RFC-0156 (MyShell OpenVoice)](0156-openvoice-outreach.md) — sibling Move-12 RFC, MIT-clean TTS alternative (in-process integration).
- [RFC-0168 (LibreTranslate)](0168-libretranslate-outreach.md) — sibling Move-12 Tier B RFC, parallel license-boundary shape (AGPL network vs. GPL subprocess).
- [RFC-0153 (openai/whisper)](0153-whisper-outreach.md) and [RFC-0155 (whisper.cpp)](0155-whisper-cpp-outreach.md) — STT engines Piper closes the speech-IO loop with.

## Unresolved questions

For the OHF-Voice maintainers:

1. **IPC-boundary framing.** Is "URML is a subprocess caller of `piper` CLI, never embedding the Python module" the framing the OHF-Voice maintainers would endorse, or is there language the project prefers for downstream integrations?
2. **TTS-engine declaration shape.** Is `piper` (with `tts_runtime: piper1_gpl` distinguishing the active repo) the right slug for URML's manifest, or does OHF-Voice have a preferred convention?
3. **License-boundary declaration.** Is `tts_license_boundary: gpl_subprocess` the right way to declare the GPL constraint? Useful as a downstream signal, or unnecessary friction?
4. **Voice-model declaration.** Is the voice-model slug (e.g., `en_US-lessac-medium`) the canonical identifier for downstream-manifest declarations, or is a different identifier preferred?
5. **Subprocess invocation mode.** Is the `piper` CLI the canonical invocation surface, or are there preferred alternatives (Wyoming protocol via wyoming-piper, HTTP server, gRPC) for production deployments?
6. **Adapter home.** URML-side subprocess wrapper in URML's `reference/speech-bridge/`, contributed example in `piper1-gpl/examples/`, or external bridge repo?
7. **Conformance listing.** Would the OHF-Voice maintainers consider a README link to URML's compatible-runtimes registry once a working subprocess-wrapper adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0166 ships as a single RFC document PR (Move-12 batch 4 — Tier B speech). **Completes Move-12** (all 16 engageable RFCs now drafted: RFCs 0153-0168). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`OHF-Voice/piper1-gpl` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `OHF-Voice/piper1-gpl`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (GPL-3.0, 4.2k stars, Issues + Discussions enabled, last commit 2026-04-07 active, isArchived: false).
- [x] GPL-3.0 friction called out up front (IPC-only integration shape; subprocess boundary preserves URML's Apache posture).
- [x] Predecessor `rhasspy/piper` archival noted; OHF-Voice successor framing explicit.
- [x] At least one alternative considered (five).
- [x] Drawbacks real (GPL boundary discipline, subprocess overhead, two Spec-RFCs prerequisite, successor-naming evolution).
- [x] Sibling RFC cross-links explicit (RFC-0156 OpenVoice MIT alternative, RFC-0168 LibreTranslate parallel license-boundary shape, RFC-0153 / RFC-0155 STT loop closure).
- [x] Completes-Move-12 framing noted (all 16 engageable RFCs now drafted).
- [x] No spec change proposed in this RFC.
