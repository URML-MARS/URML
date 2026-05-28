---
rfc: 0158
title: Argos Translate (offline on-device translation library) integration, request for comment from argosopentech maintainers
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

# RFC-0158: Argos Translate (offline on-device translation) integration, request for comment from argosopentech maintainers

## Summary

URML does not yet ship an Argos Translate manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Argos Translate — the MIT-licensed offline on-device translation library — over [`argosopentech/argos-translate`](https://github.com/argosopentech/argos-translate) (MIT), and **requests review and feedback from the argosopentech maintainers**. No spec change.

Argos Translate is the **federated-fleet-friendly** translation substrate for URML's Layer-4 NL grammar. Where OPUS-MT (RFC-0157) is the model family and Marian (RFC-0159) is the research toolkit, Argos is the runnable Python library that ships translations on-device with zero API dependency — directly aligned with URML's no-cloud-runtime invariant.

## Motivation

`argosopentech/argos-translate` is the most-adopted MIT-licensed offline translation library (MIT, 6.1k stars, Issues + Discussions both enabled, last commit `2026-04-25`, **not archived**). It packages OPUS-MT-derived models behind a simple Python API; downloads happen once at install time; everything after runs locally.

The offline-on-device profile is what makes Argos interesting to URML:

1. **URML's reference runtimes execute fully offline once validated.** [CLAUDE.md](../../CLAUDE.md) is explicit: "URML programs must execute fully offline once validated. Hosted services are a separate, commercial concern that lives outside this repository." The Layer-4 NL path must not introduce a cloud dependency. Argos Translate is the only credible MIT-licensed Tier A option that keeps the offline invariant intact.
2. **Federated robot fleets.** A robot deployed in the field cannot rely on cloud translation. Argos lets each robot carry its language pairs locally; URML's manifest declares which pairs the fleet ships with.
3. **Composes cleanly with OPUS-MT (RFC-0157).** Argos consumes OPUS-MT-derived models; the engagements stack — OPUS-MT is the model source, Argos is the runtime. URML's manifest can declare both fields without conflict.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `argos_translate_cell.yaml` fixture)

Manifest does not currently declare a translation-engine substrate. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0157):

| URML field | Maps to Argos attribute |
|---|---|
| `nl_layer.translation_engine: custom` (`argos_translate`) | Declares Argos is the translation substrate (runtime side) |
| `nl_layer.translation_model_source: opus_mt \| custom` | Declares the upstream model family Argos is using (default: OPUS-MT, RFC-0157) |
| `nl_layer.translation_pairs: [en-he, en-es, en-ja, en-zh, ...]` | Declares the language pairs the deployment ships with (must be installed locally) |
| `nl_layer.translation_offline: true` | Declares the no-cloud invariant; lets `urml validate` flag a manifest that pairs Argos with cloud-dependent flows |
| `nl_layer.translation_pair_install_class: bundled \| on_demand \| user_install` | Declares whether the pair ships pre-installed, gets downloaded on first use, or is the operator's responsibility |

### What URML v0.1 does not yet express for Argos Translate

1. **Translation-engine-class declaration.** Shared with RFC-0157 / RFC-0159. URML's v0.1 manifest has no translation-engine field.
2. **Offline / no-cloud declaration.** URML has the implicit no-cloud invariant in CLAUDE.md but no manifest field that lets a validator enforce it. The `translation_offline: true` field would be the first explicit declaration of the invariant in the manifest schema.
3. **Pair-install-class declaration.** Argos's bundled-vs-on-demand-vs-user-install distinction is a deployment concern URML's manifest cannot today express.

### Compatibility notes

- **Vendor org.** [`argosopentech`](https://github.com/argosopentech) — vendor-direct.
- **Flagship repo.** [`argosopentech/argos-translate`](https://github.com/argosopentech/argos-translate) — MIT, 6.1k stars, Issues + Discussions both enabled, last commit `2026-04-25`, **not archived**.
- **Origin.** Argos Open Tech (Ithaca, NY, US). Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface, regular release cadence. Project is maintained by a small team; engagement velocity should be calibrated accordingly.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; translation-engine-class declaration Spec RFC queued (shared with RFC-0157 / RFC-0159). The offline / no-cloud declaration may surface in its own Spec RFC if other Move-12 targets want it.
- Reference runtime: future `reference/translation-bridge/ArgosTranslator` (an Argos-backed translation adapter) is the natural integration; composes above the existing `reference/llm-bridge/` package.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Translation-engine-class Spec RFC prerequisite** (shared with RFC-0157 / RFC-0159).
- **Per-pair install footprint.** Each language pair is a downloadable model (~80-200 MB). A robot manifest that declares many pairs ships a non-trivial bundle. URML's manifest should make the size implication visible.
- **Argos depends on a small CTranslate2 build path.** Composition with CTranslate2 (also used by faster-whisper, RFC-0154) is convenient but couples runtime expectations.

## Alternatives considered

1. **Engage only OPUS-MT (RFC-0157) and treat Argos as a downstream wrapper.** Rejected. Argos is the runtime substrate URML's reference adapter would actually call; engaging only OPUS-MT misses the offline-deployment design surface.
2. **Use LibreTranslate (RFC-0168) as the offline substrate.** Rejected. LibreTranslate is AGPL-3.0; URML's reference adapter cannot statically link AGPL into Apache-2.0 code, forcing an HTTP-server boundary. Argos avoids that friction.
3. **Cross-citation only.** Considered. Concrete enough (no-cloud invariant is a real URML constraint Argos directly serves) that an explicit RFC is worth maintainer time.

## Prior art

- [`argosopentech/argos-translate`](https://github.com/argosopentech/argos-translate) — the upstream repo.
- [RFC-0157 (Helsinki-NLP OPUS-MT)](0157-opus-mt-train-outreach.md) — sibling Move-12 RFC, model-family upstream.
- [RFC-0159 (Marian-NMT)](0159-marian-dev-outreach.md) — sibling Move-12 RFC, NMT toolkit Argos relies on.
- [RFC-0167 (Meta fairseq / NLLB-200)](0167-fairseq-outreach.md) — sibling Move-12 RFC, alternate model family.
- [RFC-0168 (LibreTranslate)](0168-libretranslate-outreach.md) — sibling Move-12 RFC, AGPL alternative with REST-boundary friction.
- [CLAUDE.md "URML programs must execute fully offline"](../../CLAUDE.md) — the architectural invariant Argos serves.

## Unresolved questions

For the argosopentech maintainers:

1. **Translation-engine-class declaration shape.** Is "argos_translate" + per-pair list the right granularity, or does the team prefer a different naming for downstream-manifest declarations?
2. **Pair-install-class declaration.** Is `bundled \| on_demand \| user_install` the right enumeration, or is the model-install lifecycle different in practice?
3. **Offline / no-cloud declaration.** Is an explicit `translation_offline: true` manifest field useful as a downstream signal, or unnecessary (since Argos is inherently offline)?
4. **Composition with OPUS-MT.** Is OPUS-MT the canonical upstream Argos should declare in URML's manifest, or are alternatives (custom-trained, NLLB-derived) common enough to enumerate?
5. **Adapter home.** URML-side adapter in URML's `reference/translation-bridge/`, contributed example in `argos-translate/examples/`, or external bridge repo?
6. **Conformance listing.** Would the argosopentech maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0158 ships as a single RFC document PR (Move-12 batch 2 — translation cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`argosopentech/argos-translate` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `argosopentech/argos-translate`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 6.1k stars, Issues + Discussions enabled, last commit 2026-04-25 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (Spec-RFC prerequisite, per-pair install footprint, CTranslate2 coupling).
- [x] Sibling RFC cross-links explicit (RFC-0157 OPUS-MT, RFC-0159 Marian, RFC-0167 NLLB, RFC-0168 LibreTranslate).
- [x] CLAUDE.md no-cloud invariant cited as the architectural anchor.
- [x] No spec change proposed in this RFC.
