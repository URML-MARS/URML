---
rfc: 0317
title: openWakeWord (open wake-word engine) integration, request for comment from openWakeWord maintainers
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

# RFC-0317: openWakeWord (open wake-word engine) integration, request for comment from openWakeWord maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

A wake word is the always-on front gate of a spoken URML interaction: it decides when to start listening before speech-to-text and URML's natural-language layer take over. URML's Move #12 engaged Porcupine (RFC-0165) but hit a commercial-SDK surface; openWakeWord is the fully-open alternative. This RFC **requests review from the openWakeWord maintainers**. Apache-2.0 both sides; no spec change.

## Motivation

[`dscripka/openWakeWord`](https://github.com/dscripka/openWakeWord) (Apache-2.0, ~2.3k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the leading permissively-licensed wake-word engine. It fits URML's offline, no-API-key posture (the educational lesson, Tutorial 5, runs hermetically) far better than a commercial SDK: a classroom or home deployment can run wake-word detection fully on-device with no account.

## Detailed design

### URML composes above openWakeWord

| URML concept | openWakeWord concept | Relationship |
|---|---|---|
| Natural-language layer (Layer 4) | wake-word trigger | A detection event gates when URML begins capturing an instruction. |
| Capability manifest (Layer 1) | wake-word model id / threshold | A manifest can declare wake-word as the speech-input front gate (confidence-gated). |
| Confidence-gated intent | detection score | Mirrors the confidence-gated input pattern URML queued for non-language inputs (RFC-0230 BCI). |

### What URML v0.1 does not yet express

1. A wake-word / always-on speech-input declaration in the manifest, with a confidence threshold. Spec RFC candidate; sibling to the Move #12 STT work and RFC-0230 confidence gating.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- Wake-word is an input trigger, one step before URML's language layer; the maintainers may view the manifest declaration as out of scope on their side.

## Alternatives considered

1. Rely on the Porcupine engagement (RFC-0165). Rejected: Porcupine's commercial-SDK surface clashed with URML's offline/no-key posture; openWakeWord is the open fit.
2. Skip wake-word as out of URML's scope. Rejected: it is the always-on front gate of the spoken-intent loop and pairs naturally with the educational/offline story.

## Prior art

- [`dscripka/openWakeWord`](https://github.com/dscripka/openWakeWord).
- [RFC-0165 (Porcupine, Move #12)](0165-porcupine-outreach.md); the Move #12 STT/TTS cluster; [RFC-0230 (BCI confidence-gated input)](0230-openbci-brainflow-outreach.md).

## Unresolved questions

For the openWakeWord maintainers:

1. What grain should a URML manifest use to declare a wake-word front gate (model id, threshold)?
2. Is an English-to-validated-intent pipeline behind openWakeWord interesting to mention, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`openWakeWord` has Issues and Discussions enabled. URML's planned channel: a single Issue or Ideas Discussion pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (Apache-2.0, ~2.3k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real; additive; no spec change.
- [x] Provenance: individual maintainer (US); default policy passes.
- [x] CLAUDE.md compliance: composes above the wake-word engine; offline/no-key fit; no commercial surface.
