---
rfc: 0159
title: Marian-NMT (research-backbone NMT toolkit) integration, request for comment from marian-nmt maintainers
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

# RFC-0159: Marian-NMT (research-backbone NMT toolkit) integration, request for comment from marian-nmt maintainers

## Summary

URML does not yet ship a Marian-NMT manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Marian-NMT — the C++ neural machine-translation toolkit jointly developed by the University of Edinburgh and Microsoft Translator — over [`marian-nmt/marian-dev`](https://github.com/marian-nmt/marian-dev) (license listed as "Other", MIT-style historically), and **requests review and feedback from the marian-nmt maintainers**. No spec change.

Marian is the **research-backbone inference runtime** beneath the Move-12 translation cluster: OPUS-MT (RFC-0157) trains and publishes against Marian; Argos Translate (RFC-0158) embeds Marian inference. Engaging the upstream toolkit closes the loop on the runtime-side of URML's translation-substrate-class declaration. This RFC also surfaces a **license-clarification ask** — the GitHub API reports "Other"; URML needs the explicit OSI classification.

## Motivation

`marian-nmt/marian-dev` is the active development branch of Marian-NMT (license: Other / MIT-style, 287 stars, Issues + Discussions both enabled, last commit `2025-07-09`, **not archived**). Marian is a C++ NMT toolkit optimized for speed and quality; it's been the de facto research backbone for Helsinki-NLP's OPUS-MT and for Microsoft Translator's production deployments.

Marian is interesting to URML for three reasons:

1. **Runtime-side of the translation-substrate manifest declaration.** OPUS-MT (RFC-0157) is the model family; URML's manifest needs to also declare which inference runtime processes the translation. Marian is the default; declaring `nl_layer.translation_runtime: marian` makes the substrate explicit.
2. **C++ inference path (parallel to RFC-0155 whisper.cpp).** Marian is C++; URML's edge / embedded / no-Python deployment story for translation parallels the whisper.cpp story for STT. The runtime-dependency-profile manifest field (introduced in RFC-0155) applies symmetrically.
3. **Microsoft Translator + Edinburgh provenance.** Marian's production-tested origin (Microsoft Translator builds on it) gives URML's manifest declaration a credibility anchor that pure-research projects don't.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `marian_translate_runtime_cell.yaml` fixture)

Manifest does not currently declare a translation-runtime substrate. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0157 / RFC-0158):

| URML field | Maps to Marian attribute |
|---|---|
| `nl_layer.translation_runtime: custom` (`marian`) | Declares Marian is the inference runtime for the active translation engine |
| `nl_layer.translation_runtime_version` | Declares the Marian binary version (Marian uses semantic versioning) |
| `nl_layer.translation_runtime_dependency_profile: no_python` | Declares the C++ deployment substrate (mirrors RFC-0155's `stt_runtime_dependency_profile` field for the speech side) |
| `nl_layer.translation_runtime_quantization: int8 \| float16 \| float32` | Declares Marian's quantization level |

### What URML v0.1 does not yet express for Marian-NMT

1. **Translation-runtime declaration.** Shared with RFC-0157 / RFC-0158. URML's v0.1 manifest has no field for the inference runtime that backs the declared translation engine.
2. **Runtime-dependency-profile declaration for the translation side.** Parallel to the STT-side field introduced in RFC-0155. URML's manifest cannot today distinguish "Python-backed translation" from "C++ binary translation".
3. **Quantization declaration for the translation side.** Symmetric to the STT-side declaration; Marian's int8 / float16 / float32 selector is a real deployment knob.

### Compatibility notes

- **Vendor org.** [`marian-nmt`](https://github.com/marian-nmt) — vendor-direct.
- **Flagship repo.** [`marian-nmt/marian-dev`](https://github.com/marian-nmt/marian-dev) — license listed as "Other" (MIT-style historically — **clarification ask below**), 287 stars, Issues + Discussions both enabled, last commit `2025-07-09`, **not archived**.
- **Origin.** University of Edinburgh (UK) + Microsoft Translator (US / MSR). Passes US-federal default policy.
- **License fit.** MIT-style historically composes with URML's Apache-2.0 stance; **license-clarification ask** to confirm OSI classification.
- **Maintainer signal.** Smaller star count but anchored by Edinburgh + MSR; production-deployed at Microsoft Translator. Lower star count is a research-toolkit signal, not a maintenance signal.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; translation-runtime declaration Spec RFC queued (shared with RFC-0157 / RFC-0158). Runtime-dependency-profile Spec RFC is the same one introduced in RFC-0155 (covers both speech and translation runtimes symmetrically).
- Reference runtime: future `reference/translation-bridge/MarianTranslator` (a thin Python wrapper around the Marian binary, mirroring the RFC-0155 whisper.cpp approach for STT) is the natural integration.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License clarification gate.** URML cannot ship a reference adapter until the OSI classification is confirmed. The RFC asks; the adapter waits.
- **Translation-runtime Spec RFC prerequisite** (shared with RFC-0157 / RFC-0158).
- **C++ binary deployment.** Mirrors the RFC-0155 whisper.cpp story; URML's Python-side reference runtime calls into the Marian binary via subprocess. Adds packaging complexity.
- **Low star count may bias engagement velocity.** Marian is a serious research toolkit but does not have a community-vendor surface like the higher-star projects in Move-12. Engagement may be slower / more academic in tone.

## Alternatives considered

1. **Engage only OPUS-MT (RFC-0157) and Argos (RFC-0158) without explicit Marian engagement.** Rejected. The runtime declaration is a real manifest gap that the model-and-library upstream engagements alone don't close.
2. **Bundle this RFC into RFC-0157.** Rejected. Helsinki-NLP and marian-nmt are separate teams with separate maintainers; conflating them papers over a real engagement difference.
3. **Engage Microsoft Translator directly instead of marian-nmt.** Rejected. URML's policy is open-source-upstream-first; Microsoft Translator is a closed commercial product; marian-nmt is the open shared substrate.
4. **Cross-citation only.** Considered. The license-clarification ask alone makes a direct RFC worth maintainer time.

## Prior art

- [`marian-nmt/marian-dev`](https://github.com/marian-nmt/marian-dev) — the upstream repo.
- [`marian-nmt/marian`](https://github.com/marian-nmt/marian) — the release branch.
- [RFC-0157 (Helsinki-NLP OPUS-MT)](0157-opus-mt-train-outreach.md) — sibling Move-12 RFC, model family that trains against Marian.
- [RFC-0158 (Argos Translate)](0158-argos-translate-outreach.md) — sibling Move-12 RFC, runtime library that embeds Marian.
- [RFC-0155 (whisper.cpp)](0155-whisper-cpp-outreach.md) — STT-side parallel; introduces the runtime-dependency-profile manifest field that this RFC reuses on the translation side.

## Unresolved questions

For the marian-nmt maintainers:

1. **License clarification.** GitHub reports `licenseInfo: Other`. What is the explicit OSI license URML should cite? (MIT? Modified-MIT? Some Edinburgh-specific clause?)
2. **Translation-runtime declaration shape.** Is "marian" the right slug for the engine declaration, or does the team prefer a more specific version (e.g., distinguishing the `marian` release branch from `marian-dev`)?
3. **Runtime-dependency-profile.** URML's manifest will declare `translation_runtime_dependency_profile: no_python` for the C++ path. Does the marian-nmt team have a convention for declaring the deployment-substrate constraint that URML can reuse?
4. **Quantization declaration.** Is `int8 / float16 / float32` the right granularity for Marian, or are there project-specific levels URML should enumerate?
5. **Adapter home.** URML-side adapter in URML's `reference/translation-bridge/`, contributed example in `marian-dev/examples/`, or external bridge repo?
6. **Engagement cadence.** Is `marian-nmt/marian-dev` actively monitored for new Issues / Discussions, or does the team prefer a different channel for design-discussion?
7. **Conformance listing.** Would the marian-nmt maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0159 ships as a single RFC document PR (Move-12 batch 2 — translation cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`marian-nmt/marian-dev` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `marian-nmt/marian-dev`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license "Other" — clarification ask, 287 stars, Issues + Discussions enabled, last commit 2025-07-09 active, isArchived: false).
- [x] License-clarification ask flagged up front.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (license gate, Spec-RFC prerequisite, C++ binary deployment, low-star engagement-velocity).
- [x] Sibling RFC cross-links explicit (RFC-0157 OPUS-MT, RFC-0158 Argos, RFC-0155 whisper.cpp symmetric).
- [x] No spec change proposed in this RFC.
