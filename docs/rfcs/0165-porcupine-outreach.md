---
rfc: 0165
title: Picovoice Porcupine (on-device wake-word detection) integration, request for comment from Picovoice maintainers
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

# RFC-0165: Picovoice Porcupine (on-device wake-word detection) integration, request for comment from Picovoice maintainers

## Summary

URML does not yet ship a Porcupine manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Picovoice Porcupine — the on-device wake-word detection engine — over [`Picovoice/porcupine`](https://github.com/Picovoice/porcupine) (Apache-2.0 SDK), and **requests review and feedback from the Picovoice maintainers**. No spec change.

**This is a Move-12 Tier B RFC with one explicit friction note**: Porcupine ships under a commercial-SDK model (free / personal tier + paid commercial tier). URML's outreach is light-touch and frames the integration around the open-source / personal tier; commercial deployments inherit Picovoice's commercial-license obligations directly. URML's manifest declares the wake-word substrate cleanly, and commercial-tier composition is the operator's decision, not URML's.

## Motivation

`Picovoice/porcupine` is the most-adopted on-device wake-word detection engine in the embedded-audio ecosystem (Apache-2.0 SDK, 4.8k stars, Issues enabled, last commit `2026-05-28` — daily activity, **not archived**). It runs on microcontrollers, single-board computers, and full Linux deployments; it supports multiple custom-keyword wake words; and it is the canonical choice for "always-listening" robot interfaces where Whisper-class STT is too heavy to keep continuously active.

Porcupine is interesting to URML for three reasons:

1. **Front-end to the `listen` primitive.** URML's `listen` (RFC-0153 Whisper, RFC-0154 faster-whisper, RFC-0155 whisper.cpp) cannot stay continuously active on resource-constrained robots — full STT inference is too power-hungry. Porcupine sits in front as a lightweight always-on detector; only when a wake word fires does the URML `listen` pipeline activate full STT.
2. **RTOS / Layer-1 substrate fit.** Porcupine's resource footprint is small enough to run on Cortex-M class boards (the same class URML's RFC-0155 whisper.cpp targets for embedded STT). The wake-word path closes URML's Layer-1 speech-input story.
3. **Custom-keyword authoring is a deployment knob URML should declare.** Each robot deployment may need its own wake word (`"Hey Robotik"`, `"OK Robi"`, `"Activate URML"`). URML's manifest can declare the active wake-word set; the validator can flag deployments with unset / default-only keywords as a likely operator oversight.

URML's outreach is **light-touch**: Picovoice sells the commercial tiers and the engagement-velocity expectation should be calibrated to a vendor whose paying customers are the priority. URML frames the ask as "open-source-tier composition + manifest declaration", not "free commercial use".

## Detailed design

### URML v0.1 capability-manifest mapping (planned `porcupine_wake_word_cell.yaml` fixture)

Manifest does not currently declare a wake-word substrate. Proposed mapping uses the `custom` escape-hatch (parallel to the STT-engine-class mapping in RFC-0153 / RFC-0154 / RFC-0155):

| URML field | Maps to Porcupine attribute |
|---|---|
| `sensors[].type: speech` | Existing — declares speech sensor present |
| `sensors[].class: custom` (`wake_word_engine: porcupine`) | Declares Porcupine is the wake-word substrate |
| `sensors[].class: custom` (`wake_word_keywords: [robotik, activate]`) | Declares the active wake-word set |
| `sensors[].class: custom` (`wake_word_sensitivity: float`) | Declares Picovoice's per-keyword sensitivity (0.0-1.0) |
| `sensors[].class: custom` (`wake_word_license_tier: personal \| commercial`) | Declares the Picovoice license tier the deployment operates under |
| `sensors[].class: custom` (`wake_word_handoff_engine: whisper \| faster_whisper \| whisper_cpp`) | Declares the STT engine activated after the wake word fires (cross-link to RFCs 0153-0155) |

### What URML v0.1 does not yet express for Porcupine

1. **Wake-word substrate declaration.** URML's v0.1 manifest has no `wake_word_engine` field. Spec RFC for wake-word substrate declaration is queued, related to (but distinct from) the STT-engine-class Spec RFC shared by RFC-0153 / RFC-0154 / RFC-0155.
2. **License-tier declaration.** Porcupine's personal-vs-commercial tier is a deployment-shape concern URML's manifest can express. The declaration helps deployments stay honest about which tier they are operating under (commercial deployments using personal-tier limits is a common compliance error).
3. **Wake-word-to-STT handoff declaration.** The wake-word substrate hands off to a full STT engine when triggered. URML's manifest should express the handoff explicitly so static validation can flag a wake-word-without-STT misconfiguration.

### Compatibility notes

- **Vendor org.** [`Picovoice`](https://github.com/Picovoice) — vendor-direct.
- **Flagship repo.** [`Picovoice/porcupine`](https://github.com/Picovoice/porcupine) — Apache-2.0 SDK, 4.8k stars, Issues enabled, Discussions disabled, last commit `2026-05-28` (daily activity), **not archived**.
- **Companion products.** Picovoice's ecosystem also includes Cheetah (STT), Rhino (NL understanding), Leopard (transcription), Falcon (speaker diarization), and Cobra (voice activity). This RFC engages Porcupine specifically; other Picovoice products are out of scope here.
- **Origin.** Picovoice (Vancouver, Canada). Passes US-federal default policy (NATO allied; Five Eyes).
- **License fit.** Apache-2.0 SDK; the SDK source is permissive, the model files require a Picovoice access key (personal: free; commercial: paid). URML's manifest expresses the tier; the operator manages the license.
- **Maintainer signal.** Daily commits. Commercial-SDK posture means upstream engagement-velocity may be tepid on community-facing surfaces (Issues), since paying-customer support is the priority.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; wake-word substrate declaration Spec RFC queued.
- Reference runtime: future `reference/speech-bridge/PorcupineWakeWordAdapter` (a Picovoice-SDK-backed wake-word detector that triggers the declared `wake_word_handoff_engine`) is the natural integration shape.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Commercial-SDK posture friction.** Picovoice's commercial tier means engagement-velocity may be low on the open Issues channel; the vendor's paying customers take priority. URML should not block on rapid response.
- **License-tier expression burden.** URML's manifest now expresses a vendor-specific license tier. Generalizing this to other commercial-SDK substrates may surface a "substrate-license-tier" Spec RFC.
- **Wake-word-substrate Spec RFC prerequisite.** Distinct from but adjacent to the STT-engine-class Spec RFC.
- **Custom-keyword training.** Custom wake words require Picovoice Console (commercial tier). URML's manifest can declare custom keywords but the training itself is outside URML's reach.

## Alternatives considered

1. **Skip Porcupine entirely; rely only on the STT engines (RFC-0153 / RFC-0154 / RFC-0155).** Rejected. Always-on STT is too heavy for resource-constrained robots; the wake-word path is genuinely the missing piece.
2. **Engage an MIT-licensed alternative (e.g., openWakeWord).** Considered. openWakeWord is a real alternative but with less production coverage; Porcupine is the dominant choice in the field. Engaging both is plausible in a future Move.
3. **Cross-citation only.** Considered. The commercial-tier-license expression is concrete enough that an explicit RFC is worth maintainer time.

## Prior art

- [`Picovoice/porcupine`](https://github.com/Picovoice/porcupine) — the upstream repo.
- [`dscripka/openWakeWord`](https://github.com/dscripka/openWakeWord) — MIT-licensed wake-word alternative (candidate for a future Move).
- [RFC-0153 (openai/whisper)](0153-whisper-outreach.md) — STT engine Porcupine hands off to.
- [RFC-0154 (SYSTRAN faster-whisper)](0154-faster-whisper-outreach.md) — realtime STT engine Porcupine pairs with.
- [RFC-0155 (ggml-org whisper.cpp)](0155-whisper-cpp-outreach.md) — embedded STT engine on the same Layer-1 substrate Porcupine targets.

## Unresolved questions

For the Picovoice maintainers:

1. **Wake-word substrate declaration shape.** Is `porcupine` the right slug for URML's manifest, or does Picovoice prefer a different convention?
2. **License-tier declaration.** Is `personal \| commercial` the right enumeration for URML's manifest, or are there additional tiers (research, education, enterprise) URML should enumerate?
3. **Wake-word-to-STT handoff declaration.** Is the handoff field useful as a downstream signal, or unnecessary?
4. **Custom-keyword authoring.** Does Picovoice have a preferred convention for declaring custom keywords in a downstream manifest (file path? URI? Picovoice Console handle)?
5. **Engagement cadence.** Is `Picovoice/porcupine` actively monitored for new design-discussion Issues, or is the vendor's preferred channel for non-customer questions a different surface?
6. **Adapter home.** URML-side adapter in URML's `reference/speech-bridge/`, contributed example in `porcupine/examples/`, or external bridge repo?
7. **Conformance listing.** Would the Picovoice maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0165 ships as a single RFC document PR (Move-12 batch 4 — Tier B speech). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`Picovoice/porcupine` has Issues enabled (Discussions disabled). URML's planned channel: open a single Issue on `Picovoice/porcupine` framed as "URML manifest declaration + wake-word-substrate integration shape, design RFC", pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0 SDK, 4.8k stars, Issues enabled, last commit 2026-05-28 daily, isArchived: false).
- [x] Commercial-SDK friction called out up front (Tier B; engagement-velocity expectation calibrated).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (commercial-tier velocity, license-tier expression burden, Spec-RFC prerequisite, custom-keyword training outside URML).
- [x] Sibling RFC cross-links explicit (RFC-0153 / RFC-0154 / RFC-0155 STT engines).
- [x] License-tier declaration field surfaced as novel manifest concern.
- [x] No spec change proposed in this RFC.
