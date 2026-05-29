---
rfc: 0224
title: AFNOR Grand Défi AI — URML consultation submission, request for comment from AFNOR AI standardization
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0224: AFNOR Grand Défi AI consultation submission

## Summary

AFNOR (Association française de normalisation) is France's national standards body and operates the Grand Défi AI consultation platform. AFNOR explicitly invites international participation in shaping European AI standards via the consultation platform; the French national position feeds into CEN-CENELEC JTC 21 (sibling RFC-0222). This RFC documents URML's proposed consultation submission, engaged via [afnor.org/en/news/shaping-european-ai-leadership/](https://www.afnor.org/en/news/shaping-european-ai-leadership/), and **requests review and feedback from AFNOR AI standardization**. No spec change.

## Motivation

AFNOR's Grand Défi AI consultation platform is the FR-side parallel to the DIN/DKE roadmap (sibling RFC-0223). Both feed CEN-CENELEC JTC 21; URML engaging both DE + FR doubles the national-position footprint and demonstrates URML's cross-national interest in EU AI standards work.

URML benefits from documenting the engagement because:

1. **FR national position into JTC 21.** Sibling to DIN/DKE RFC-0223 and JTC 21 direct RFC-0222; AFNOR's consultation platform is the FR-side surface.
2. **Open consultation platform.** AFNOR ships English-language docs and explicitly invites international participation; no domicile gate at the consultation-submission stage.
3. **Cross-fertilization with DE national position.** Submitting URML to both DIN/DKE (RFC-0223) and AFNOR (this RFC) demonstrates URML's broad EU-member engagement and creates cross-referencing material when JTC 21 work surfaces the topic.

## Detailed design

### URML proposed consultation submission content (drafted in founder-actions-move17.md)

The 1-2 page consultation submission will mirror the DIN/DKE roadmap contribution (sibling RFC-0223) — same shape, different target:

1. **URML introduction (0.5 page).** Substrate-neutral robotics-intent language; Apache-2.0; relevance to AI-on-systems.
2. **Structured-AI-intent pattern (0.5-1 page).** URML's NL → primitive translation + manifest-validated dispatch + validator static-verification as concrete instance of structured AI intent for the FR consultation.
3. **Cross-citation with JTC 21 work + sibling DIN/DKE engagement (0.25 page).** URML's parallel JTC 21 public-enquiry engagement (RFC-0222) and DIN/DKE roadmap contribution (RFC-0223); transparent cross-referencing.
4. **Asks (3-5 specific questions).** Grand Défi AI consultation acceptance; FR national-position contribution channel; downstream JTC 21 routing; AFNOR committee participation orientation (Phase 2).

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Submit URML consultation to AFNOR Grand Défi AI platform.** Founder-action via consultation portal.
2. **Cross-reference with sibling DIN/DKE + JTC 21 engagements.** Transparent cross-reference in the submission file itself.
3. **Future AFNOR committee participation orientation.** Phase 2 — AFNOR committee membership requires sustained engagement.

### Compatibility notes

- **Engagement surface.** [afnor.org/en/news/shaping-european-ai-leadership/](https://www.afnor.org/en/news/shaping-european-ai-leadership/) — Grand Défi AI consultation platform.
- **Governance.** AFNOR (Association française de normalisation; FR national standards body).
- **Origin.** France. NATO-allied; EU member.
- **License fit.** AFNOR ships English-language consultation docs; URML's Apache-2.0 cross-citation is clean.
- **Maintainer signal.** Active; explicit international participation invitation; Grand Défi AI consultation platform live.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Consultation submission only.
- Reference runtime: no change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Parallel-with-DIN/DKE risk of repetition.** AFNOR and DIN/DKE both feed JTC 21; URML's submissions may be seen as duplicative if not cross-referenced clearly.
- **French-language outreach future work.** URML's natural-language layer is multilingual but French translation of URML docs is not Phase 1; AFNOR ships EN docs so this is not blocking.
- **Consultation-platform acceptance uncertain.** URML's submission framing as related-art reference may or may not fit AFNOR's consultation scope expectations.

## Alternatives considered

1. **Engage DIN/DKE (RFC-0223) only, skip AFNOR.** Rejected. Doubling EU-member national-position footprint is the explicit goal.
2. **Engage AFNOR committee directly rather than Grand Défi AI consultation platform.** Considered. AFNOR committee membership is Phase 2; the consultation platform is the open Phase-1 surface.
3. **Bundle AFNOR + DIN/DKE submissions in a single document.** Rejected. Per-national-body submissions are the cleaner shape and don't risk confusing the national-position files.
4. **Defer AFNOR until URML has French-language translation.** Rejected. AFNOR ships English consultation docs; FR translation is future work, not blocking.

## Prior art

- [AFNOR — Artificial Intelligence](https://www.afnor.org/en/artificial-intelligence/).
- [AFNOR — Shaping European AI Leadership](https://www.afnor.org/en/news/shaping-european-ai-leadership/).
- [RFC-0222 (CEN-CENELEC JTC 21 outreach)](0222-cen-cenelec-jtc-21-outreach.md) — sibling EU-level engagement.
- [RFC-0223 (DIN/DKE outreach)](0223-din-dke-ai-roadmap-outreach.md) — sibling DE national-position engagement.

## Unresolved questions

For AFNOR AI standardization coordinators:

1. **Grand Défi AI consultation acceptance.** Is URML's structured-AI-intent pattern an acceptable consultation contribution, or does the platform expect French-domiciled contributors?
2. **FR national-position contribution channel.** Beyond Grand Défi AI consultation, what's the channel for an external project (URML) to feed into the FR national position for JTC 21?
3. **Sibling DIN/DKE cross-reference appropriateness.** URML's submission cross-references the parallel DIN/DKE engagement; is this useful or distracting?
4. **AFNOR committee participation orientation.** Phase 2 question — what's the path for an external project to participate in AFNOR robotics-AI committees?
5. **French-language requirements.** Are AFNOR submissions accepted in English (Grand Défi AI ships EN), or do AFNOR committees expect FR-language work products?
6. **Anything else.**

## Implementation note

RFC-0224 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Consultation submission draft in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: AFNOR Grand Défi AI consultation platform at [afnor.org/en/news/shaping-european-ai-leadership/](https://www.afnor.org/en/news/shaping-european-ai-leadership/). Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (AFNOR Grand Défi AI consultation platform active; international participation invitation explicit; EN docs).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (parallel-with-DIN risk-of-repetition, French-language future work, consultation-platform acceptance uncertain).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: AFNOR France (NATO-allied EU member); default policy passes.
- [x] CLAUDE.md compliance check passed — international standards-track engagement is documented direction.
