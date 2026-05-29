---
rfc: 0223
title: DIN/DKE German AI Standardization Roadmap — URML contribution, request for comment from DIN/DKE roadmap coordinators
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

# RFC-0223: DIN/DKE German AI Standardization Roadmap contribution

## Summary

DIN (Deutsches Institut für Normung) and DKE (German Commission for Electrical, Electronic and Information Technologies) co-publish the German AI Standardization Roadmap, currently in its 2nd edition (English available). The roadmap explicitly invites contributions from "industry, science, the public sector and civil society" and feeds into CEN-CENELEC JTC 21 and ISO/IEC JTC 1/SC 42. This RFC documents URML's proposed contribution to the DIN/DKE roadmap, engaged via [din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap), and **requests review and feedback from the DIN/DKE roadmap coordinators**. No spec change.

## Motivation

The German AI Standardization Roadmap is one of the most-cited national AI-standards-roadmap documents internationally. Contributing URML's substrate-neutral robotics-intent-language framing into the roadmap surfaces URML as a concrete instance of structured-AI-intent for the DE national position into JTC 21 and SC 42. The civil-society invitation removes the domicile gate at the roadmap-contribution stage; deeper DIN committee participation would require DIN membership (Phase 2).

URML benefits from documenting the engagement because:

1. **DE national position into JTC 21 + SC 42.** DIN/DKE's roadmap feeds the German position into the EU and international AI standards bodies. URML contribution travels via the national-position file.
2. **Civil-society contribution channel is open.** No domicile gate at the roadmap-contribution stage; Israeli-domiciled URML maintainer can contribute.
3. **Sibling AFNOR (FR) cross-fertilization.** Sibling RFC-0224 contributes URML to the French AFNOR Grand Défi AI consultation. The two contributions are parallel national-position files into JTC 21; cross-fertilization is intentional.

## Detailed design

### URML proposed contribution content (drafted in founder-actions-move17.md)

The 1-2 page roadmap contribution memo will cover:

1. **URML introduction (0.5 page).** Substrate-neutral robotics-intent language; Apache-2.0; relevance to AI-on-systems including robotics.
2. **Structured-AI-intent pattern (0.5-1 page).** URML's NL → primitive translation + manifest-validated dispatch + validator static-verification as a concrete instance of structured AI intent for the DE roadmap's catalogue.
3. **Cross-citation with JTC 21 + SC 42 work (0.25 page).** URML's parallel JTC 21 public-enquiry engagement (RFC-0222) and how the DIN/DKE national-position file feeds JTC 21 directly.
4. **Asks (3-5 specific questions for DIN/DKE coordinators).** Roadmap-catalogue inclusion criteria; DE national-position contribution channel; downstream JTC 21 + SC 42 routing; future DIN committee participation orientation.

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Submit URML contribution to DIN/DKE AI Standardization Roadmap.** Founder-action via roadmap participation channel.
2. **Cross-citation in URML German-language docs (if any).** URML's natural-language layer is multilingual; German translation is future work.
3. **Future DIN committee participation orientation.** Phase 2 — DIN committee membership requires sustained engagement.

### Compatibility notes

- **Engagement surface.** [din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap).
- **Governance.** DIN (Deutsches Institut für Normung; DE national standards body) + DKE (joint commission of DIN + VDE).
- **Origin.** Germany. NATO-allied; EU member.
- **License fit.** Roadmap is publicly published in English; contributions are accepted per the civil-society invitation. URML's Apache-2.0 cross-citation is clean.
- **Maintainer signal.** Active; 2nd edition published in English; explicit civil-society invitation; Indo-German bilateral surface shows openness to non-EU contributions.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Roadmap contribution only.
- Reference runtime: no change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Contribution, not committee work.** Roadmap contribution is at the position-file level; deeper DIN committee participation requires sustained engagement URML cannot do at Phase 1.
- **Roadmap-catalogue acceptance is uncertain.** URML's robotics-intent-language framing may or may not fit the roadmap's structured-AI-intent catalogue criteria.
- **German-language outreach future work.** URML's natural-language layer is multilingual but German translation of URML docs is not Phase 1; outreach to a DE-coordinated channel could benefit from a DE-language summary in future.

## Alternatives considered

1. **Engage AFNOR (sibling RFC-0224) only, skip DIN/DKE.** Rejected. DE national position is the strongest single EU-member AI-standards lane into JTC 21 + SC 42; engaging both DE + FR doubles the national-position-file footprint into JTC 21.
2. **Engage DIN robotics-specific committees directly rather than the AI roadmap.** Considered. DIN's robotics committees exist but engagement requires DIN membership (Phase 2); roadmap contribution is the lower-friction Phase-1 surface.
3. **Defer DIN/DKE until URML has German-language translation.** Rejected. The civil-society invitation accepts English contributions; German translation is future work.
4. **Engage DIN/DKE via Indo-German bilateral surface.** Considered. The bilateral surface is a route; the roadmap participation channel is the direct route. Both are compatible.

## Prior art

- [DIN/DKE German AI Standardization Roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap).
- [RFC-0222 (CEN-CENELEC JTC 21 outreach)](0222-cen-cenelec-jtc-21-outreach.md) — sibling EU-level engagement; DIN/DKE national-position file feeds JTC 21 directly.
- [RFC-0224 (AFNOR Grand Défi AI outreach)](0224-afnor-grand-defi-ai-outreach.md) — sibling FR national position into JTC 21.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — URML's federal-alignment posture; DE engagement broadens to transatlantic.

## Unresolved questions

For DIN/DKE roadmap coordinators:

1. **Roadmap-catalogue inclusion criteria.** What's the inclusion criteria for the AI Standardization Roadmap catalogue? URML's structured-intent pattern as concrete instance of AI-on-systems — does it fit the catalogue scope?
2. **DE national-position contribution channel.** Beyond the roadmap, what's the channel for an external project (URML) to feed into the DE national-position file for JTC 21 + SC 42?
3. **Civil-society contribution depth.** The roadmap invites civil-society contributions; how deeply does civil-society participation extend (single contribution, ongoing engagement, ad-hoc consultations)?
4. **DIN committee participation orientation.** What's the path for an external project to participate in DIN robotics-related committees (Phase 2 question; URML at Phase 1 is roadmap-contribution-only)?
5. **Indo-German bilateral surface relevance.** Is the Indo-German bilateral surface a relevant channel for URML's contribution, or is roadmap-direct the right entry?
6. **Cross-reference to sibling AFNOR + JTC 21 engagements.** URML is concurrently engaging FR (AFNOR) and JTC 21 directly. Is cross-reference between DIN/DKE + AFNOR + JTC 21 contributions appropriate?
7. **Anything else.**

## Implementation note

RFC-0223 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Roadmap contribution memo draft in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: DIN/DKE roadmap participation portal at [din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap](https://www.din.de/en/innovation-and-research/artificial-intelligence/ai-roadmap). Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (DIN/DKE AI Roadmap 2nd ed. English active; civil-society invitation explicit).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (contribution-vs-committee, catalogue-acceptance uncertain, German-language future work).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: DIN/DKE Germany (NATO-allied EU member); default policy passes.
- [x] CLAUDE.md compliance check passed — international standards-track engagement is documented direction.
