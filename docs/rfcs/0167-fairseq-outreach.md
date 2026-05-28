---
rfc: 0167
title: Meta fairseq / NLLB-200 (archived seq2seq toolkit, 200-language model) integration, request for comment from facebookresearch maintainers
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

# RFC-0167: Meta fairseq / NLLB-200 (200-language translation model, archived toolkit) integration, request for comment from facebookresearch maintainers

## Summary

URML does not yet ship a fairseq / NLLB-200 manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Meta's NLLB-200 ("No Language Left Behind") 200-language translation model — hosted on [`facebookresearch/fairseq`](https://github.com/facebookresearch/fairseq) (MIT for code; **CC-BY-NC 4.0** for the NLLB-200 model weights) — and **requests review and feedback from Meta on the successor-surface question** now that fairseq is archived. No spec change.

**This is a Move-12 Tier B RFC with two explicit friction notes**: (a) the upstream `facebookresearch/fairseq` repo is **archived (2025-09-30)** so no PRs merge; (b) the NLLB-200 model weights ship under **CC-BY-NC 4.0** (non-commercial only), which conflicts with URML's commercial-friendly default posture. URML's engagement is light-touch: surface the manifest mapping, ask Meta what the canonical successor surface for NLLB engagement is now, and document the model-license constraint in the URML manifest.

## Motivation

`facebookresearch/fairseq` was Meta's flagship seq2seq toolkit (MIT, 32.2k stars, Issues enabled, last commit `2025-09-30` — **archived**). The repo hosted the NLLB-200 model card and inference recipes; NLLB-200 itself is Meta's 200-language single-model translation system, the breadth-leader in open translation today.

The friction is structural:

1. **fairseq is archived.** Issues remain open and viewable; PRs do not merge. Engagement is limited to "ask Meta what's next" rather than "contribute upstream".
2. **NLLB-200 model weights are CC-BY-NC 4.0.** The training code is MIT-clean; the weights are not. URML's commercial-friendly stance means a reference adapter that uses NLLB-200 must either declare a non-commercial flag (`--no-policy nllb`-style) or not bundle the weights.
3. **The successor surface is unclear.** Meta has scattered translation-related work across multiple repos (`facebookresearch/seamless_communication`, `facebookresearch/large_concept_model`, HuggingFace model cards). URML needs to know which surface is the active engagement channel.

URML still engages despite the friction because:

1. **NLLB-200's 200-language coverage is unmatched.** No other open translation model spans that many languages with one weight set. URML's Layer-4 multilingual story benefits from declaring NLLB-200 as an alternate substrate even with the non-commercial flag.
2. **The model-license question is generalizable.** URML's manifest will encounter many non-commercial-only model weights as the ecosystem evolves; documenting the friction in the manifest schema (rather than papering over it) is the durable answer.
3. **The successor-surface question matters for downstream URML users.** If a URML deployment declares NLLB-200 in its manifest, future users need a stable URL to point at for support.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `nllb_translate_cell.yaml` fixture, marked non-commercial)

Manifest does not currently declare a translation-engine substrate or a non-commercial flag. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0157 / RFC-0158 / RFC-0159):

| URML field | Maps to NLLB-200 attribute |
|---|---|
| `nl_layer.translation_engine: custom` (`nllb_200`) | Declares NLLB-200 is the translation substrate |
| `nl_layer.translation_runtime: fairseq \| transformers \| ctranslate2` | Declares the inference runtime (fairseq's reference is archived; HuggingFace `transformers` is the practical runtime today) |
| `nl_layer.translation_model_uri: huggingface://facebook/nllb-200-distilled-600M` | Declares the HuggingFace model path |
| `nl_layer.translation_model_license: cc_by_nc_4_0` | **Declares the non-commercial constraint** (first manifest field for model-license declaration) |
| `nl_layer.translation_languages: [...200 codes...]` | Declares the supported language set (NLLB-200's distinguishing feature) |
| `nl_layer.translation_commercial_use: false` | Validator-enforceable: a manifest that pairs NLLB-200 with a commercial-deployment flag triggers a build-time error |

### What URML v0.1 does not yet express for NLLB-200

1. **Translation-engine-class declaration.** Shared with RFC-0157 / RFC-0158 / RFC-0159. URML's v0.1 manifest has no translation-engine field.
2. **Model-license declaration.** URML's v0.1 manifest has no field for declaring the license of a learned model component. NLLB-200's CC-BY-NC constraint is the first concrete case where this declaration is load-bearing.
3. **Commercial-use validator gate.** If `translation_model_license: cc_by_nc_4_0` is declared and `commercial_use: true` is set elsewhere, `urml validate` should fail at static-check time. URML's validator does not today have this rule.
4. **Successor-surface declaration.** With `facebookresearch/fairseq` archived, URML cannot point at a single canonical "active" repo. The manifest may need to declare a chain of upstream URIs (primary, archived-historical, active-successor).

### Compatibility notes

- **Vendor org.** [`facebookresearch`](https://github.com/facebookresearch) — vendor-direct (Meta AI Research).
- **Flagship repo.** [`facebookresearch/fairseq`](https://github.com/facebookresearch/fairseq) — MIT code, 32.2k stars, Issues enabled, **archived 2025-09-30**.
- **Model card.** NLLB-200 lives at [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) (and sibling sizes) on HuggingFace. Model weights are **CC-BY-NC 4.0**.
- **Origin.** Meta (US, Menlo Park). Passes US-federal default policy.
- **License fit.** Code MIT-clean; weights CC-BY-NC-flagged. URML's manifest must reflect both.
- **Maintainer signal.** Archived upstream. Engagement-velocity expectation: low. Value comes from the documented mapping and the model-license question, not from immediate dialogue.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. Two Spec RFCs queued for follow-up: translation-engine-class declaration (shared with RFC-0157 / RFC-0158 / RFC-0159) and model-license declaration (novel here; surfaces from RFC-0167 first but will recur).
- Reference runtime: future `reference/translation-bridge/NLLBTranslator` would be **non-commercial-flagged**; bundling NLLB-200 weights in URML's core distribution is rejected. The adapter would download weights at install time with an explicit user opt-in to the CC-BY-NC license.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Archived upstream.** No PRs merge; engagement-channel velocity will be slow at best.
- **Non-commercial-only model weights.** URML's reference adapter cannot bundle NLLB-200 by default. A `--no-policy nllb` flag would be the cleanest opt-in shape.
- **Successor-surface ambiguity.** Meta has not designated a single canonical successor for fairseq. URML's manifest declaration risks rot if the successor URL is wrong.
- **Two Spec RFCs prerequisite.** Translation-engine-class (shared with sibling RFCs) and model-license declaration (novel) both need to land for the manifest fields to be meaningful.

## Alternatives considered

1. **Skip NLLB-200 entirely; OPUS-MT (RFC-0157) already covers URML's reserved languages.** Rejected. NLLB-200's 200-language breadth is qualitatively different; URML benefits from documenting how a non-commercial model fits in the manifest schema even if the v0.1 default avoids it.
2. **Engage Meta at a different repo (`facebookresearch/seamless_communication` or `large_concept_model`).** Considered. These are active surfaces but their scope is broader than NLLB-200; the URML-fit framing is less clean. Engagement here can follow if Meta points at one as the successor.
3. **Bundle this RFC with RFC-0157 (OPUS-MT) as one "multilingual NL" RFC.** Rejected. Helsinki and Meta are different teams; the license and archive friction are NLLB-specific.
4. **Cross-citation only.** Considered. The model-license declaration is novel enough that an explicit RFC is the right shape.

## Prior art

- [`facebookresearch/fairseq`](https://github.com/facebookresearch/fairseq) — the archived upstream repo.
- [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) — HuggingFace model card.
- [`facebookresearch/seamless_communication`](https://github.com/facebookresearch/seamless_communication) — Meta's active multilingual-communication surface (candidate successor).
- [RFC-0157 (Helsinki-NLP OPUS-MT)](0157-opus-mt-train-outreach.md) — sibling Move-12 RFC, MIT-clean alternative.
- [RFC-0158 (Argos Translate)](0158-argos-translate-outreach.md) — sibling Move-12 RFC, offline runtime.
- [RFC-0159 (Marian-NMT)](0159-marian-dev-outreach.md) — sibling Move-12 RFC, runtime backbone.
- [RFC-0168 (LibreTranslate)](0168-libretranslate-outreach.md) — sibling Tier B Move-12 RFC, AGPL friction (parallel friction shape).

## Unresolved questions

For the Meta NLLB / fairseq maintainers:

1. **Successor surface.** With `facebookresearch/fairseq` archived, where should downstream projects engage on NLLB-200 going forward? `seamless_communication`? `large_concept_model`? HuggingFace community? Direct contact?
2. **Model-license-declaration shape.** URML's manifest will declare `translation_model_license: cc_by_nc_4_0`. Is this the right level of granularity, or does Meta have a finer-grained license-classification convention?
3. **Commercial-use boundary.** Does Meta have a path for commercial use of NLLB-200 weights (e.g., an enterprise license), or is non-commercial the canonical and only path?
4. **Engagement channel.** Given fairseq is archived, where would Meta prefer URML's outreach Issue to land? Or is a public Issue the wrong shape, and direct communication the right one?
5. **Conformance listing.** Even with archived-upstream, would Meta consider a README link in the successor-surface repo (whichever it is) to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0167 ships as a single RFC document PR (Move-12 batch 2 — translation cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`facebookresearch/fairseq` has Issues enabled even while archived. URML's planned channel: open a single Issue on `facebookresearch/fairseq` framed as "NLLB-200 successor-surface question + URML manifest declaration", pointing to this RFC. If Meta replies with a successor-surface URL, the engagement migrates there.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT code / CC-BY-NC weights, 32.2k stars, Issues enabled, last commit 2025-09-30, **isArchived: true**).
- [x] Tier B friction notes called out up front (archived upstream + non-commercial model weights).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (archived velocity, non-commercial weights, successor ambiguity, two Spec-RFCs prerequisite).
- [x] Sibling RFC cross-links explicit (RFC-0157 OPUS-MT, RFC-0158 Argos, RFC-0159 Marian, RFC-0168 LibreTranslate).
- [x] Novel manifest declarations (model-license + commercial-use gate) flagged for Spec RFC follow-up.
- [x] No spec change proposed in this RFC.
