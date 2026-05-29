---
rfc: 0225
title: BSI AI Standards Hub (BSI + Alan Turing Institute + NPL) — URML engagement, request for comment from Hub coordinators
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

# RFC-0225: BSI AI Standards Hub engagement

## Summary

The BSI AI Standards Hub is the joint BSI / Alan Turing Institute / National Physical Laboratory initiative supported by DSIT (UK Department for Science, Innovation and Technology), with explicit international remit. BSI is the UK mirror to ISO/TC 299 (Robotics) and CEN/TC 310; the Hub is the lower-friction Phase-1 surface that doesn't require active BSI committee membership. This RFC documents URML's proposed engagement with the BSI AI Standards Hub, engaged via [aistandardshub.org](https://aistandardshub.org/), and **requests review and feedback from the Hub coordinators**. No spec change.

## Motivation

The UK AI Standards Hub provides URML with a UK-side standards-track surface that does NOT require UK-domiciled organization (unlike the UK Robotics Growth Partnership funding lanes, which are UK-registered-orgs-only — Tier B deferred). The Hub's explicit international remit removes the domicile gate for URML's Phase-1 engagement.

URML benefits from documenting the engagement because:

1. **UK-side standards-track presence.** Sibling EU-side engagement (DIN/DKE RFC-0223, AFNOR RFC-0224, JTC 21 RFC-0222) covers continental Europe; BSI AI Hub covers UK with explicit international scope.
2. **BSI mirror to ISO/TC 299 + CEN/TC 310.** Hub engagement opens potential future routing into BSI's national-mirror committees for ISO TC 299 (Robotics) and CEN TC 310. Phase 2.
3. **Alan Turing Institute + NPL credibility.** The Hub's joint stewardship by BSI + ATI + NPL provides UK-side institutional credibility URML can cross-cite.

## Detailed design

### URML proposed Hub engagement content (drafted in founder-actions-move17.md)

The 2-3 page engagement note + URML maintainer registration on the Hub surface will cover:

1. **URML introduction + maintainer registration (0.5 page).** Substrate-neutral robotics-intent language; Apache-2.0; Israel-domiciled maintainer with explicit international-remit framing.
2. **Robotics-intent + AI-standards-Hub fit (1 page).** URML's structured-AI-intent pattern as concrete instance the Hub's international community could reference.
3. **Sibling EU + US engagement context (0.5 page).** URML's parallel JTC 21 + DIN/DKE + AFNOR + NIST + ASTM engagements; the Hub's international remit makes it the natural UK-side cross-citation surface.
4. **Asks (3-5 specific questions).** International-community engagement fit; future BSI national-mirror routing orientation (TC 299 / TC 310 Phase 2); Hub-published-resource cross-referencing.

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Register URML maintainer on the BSI AI Standards Hub surface.** Founder-action.
2. **Submit URML engagement note to Hub coordinators.** Founder-action via Hub engagement portal.
3. **Cross-citation in URML UK-related docs (if any).** URML's UK-side framing references the Hub.
4. **Future BSI national-mirror routing orientation.** Phase 2 — BSI ISO TC 299 / CEN TC 310 mirror committees require BSI committee membership.

### Compatibility notes

- **Engagement surface.** [aistandardshub.org](https://aistandardshub.org/) — joint BSI + Alan Turing Institute + NPL hub.
- **Governance.** BSI (British Standards Institution; UK national standards body) + Alan Turing Institute (UK national institute for data science + AI) + NPL (National Physical Laboratory). DSIT-supported.
- **Origin.** UK. NATO-allied (Five Eyes). Note: UK Robotics Growth Partnership funding lanes are UK-registered-orgs-only (Tier B deferred); the AI Standards Hub does not have this gate.
- **License fit.** BSI standards are purchase-licensed; URML's Hub engagement is at the community-resource level, not standard-text reuse. Clean.
- **Maintainer signal.** Active; international remit explicit; ATI + NPL joint stewardship.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Hub engagement only.
- Reference runtime: no change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Hub-level vs committee-level distinction.** Hub engagement is community-level; substantive standards-shaping requires BSI committee membership (Phase 2).
- **UK-side scope.** Hub is UK-anchored even with international remit; UK national-position file feeds ISO TC 299 / CEN TC 310 indirectly via BSI committee work.
- **Five Eyes context awareness.** The UK is a Five-Eyes member; URML's Israeli-domiciled maintainer is not Five-Eyes-eligible. The Hub's civilian-standards remit avoids the Five-Eyes-defense-research conflict that excludes URML from DSTL, DSTG, DRDC engagement (Tier C).

## Alternatives considered

1. **Engage BSI national-mirror committees directly rather than the Hub.** Considered. BSI committee membership is Phase 2 (sustained engagement requirement); the Hub is the Phase-1 surface.
2. **Engage UK Robotics Growth Partnership (RGP) instead.** Rejected. RGP funding is UK-registered-orgs-only (Tier B deferred); Israeli-domiciled URML cannot access funding. The Hub has international remit.
3. **Engage Alan Turing Institute or NPL separately.** Considered. The joint Hub is the integrated engagement surface; per-institution engagement is downstream conversation if the Hub engagement opens it.
4. **Skip UK side entirely; engage only EU + US.** Rejected. UK-side standards-track presence is real (BSI mirrors ISO TC 299 / CEN TC 310); the Hub's international remit makes URML's UK engagement low-friction.

## Prior art

- [BSI AI Standards Hub (via techUK)](https://www.techuk.org/what-we-deliver/events/ai-and-data-assurance-and-standards-with-the-bsi.html).
- [BSI AI Regulations page](https://www.bsigroup.com/en-GB/our-expertise/digital-trust/artificial-intelligence-adoption-and-regulation/).
- [ISO/TC 299 Robotics](https://www.iso.org/committee/5915511.html) — BSI national-mirror committee participation gates ISO TC 299 contribution.
- [RFC-0222 (CEN-CENELEC JTC 21 outreach)](0222-cen-cenelec-jtc-21-outreach.md), [RFC-0223 (DIN/DKE outreach)](0223-din-dke-ai-roadmap-outreach.md), [RFC-0224 (AFNOR outreach)](0224-afnor-grand-defi-ai-outreach.md) — sibling Sub-wave B continental Europe engagements.
- [RFC-0226 (OECD AI Policy Observatory outreach)](0226-oecd-ai-policy-observatory-outreach.md) — sibling Sub-wave B international-norms engagement.

## Unresolved questions

For the BSI AI Standards Hub coordinators:

1. **International-community engagement fit.** Is URML's Israeli-domiciled-maintainer + open-source robotics-intent-language framing a fit for the Hub's international community?
2. **Hub-published-resource cross-referencing.** Would the Hub consider listing URML as a community resource for international participants interested in structured-AI-intent patterns?
3. **Future BSI national-mirror routing orientation.** What's the path for an externally-engaged project to graduate from Hub engagement to BSI national-mirror committee participation for ISO TC 299 / CEN TC 310?
4. **DSIT linkage.** The Hub is DSIT-supported; is there DSIT-side engagement relevant for URML's international-standards posture (within UK civilian-standards scope, not defense)?
5. **Five Eyes context.** The Hub's civilian remit avoids the Five-Eyes-defense gate that excludes URML from DSTL etc. (Tier C). Is this read correct, or are there other Five-Eyes-side considerations URML should be aware of?
6. **Sibling EU + US engagement context.** URML is concurrently engaging EU (JTC 21, DIN/DKE, AFNOR) and US (NIST EL, ASTM F45.04) standards channels. Is cross-reference between the UK + EU + US engagement files useful from a Hub-coordination perspective?
7. **Anything else.**

## Implementation note

RFC-0225 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Hub engagement note draft in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: BSI AI Standards Hub portal at [aistandardshub.org](https://aistandardshub.org/) — maintainer registration + engagement-note submission. Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (BSI AI Standards Hub active; joint BSI + ATI + NPL; international remit explicit; DSIT-supported).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (Hub-vs-committee distinction, UK-side scope, Five Eyes context awareness).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: BSI + ATI + NPL UK (NATO-allied Five Eyes); civilian-standards scope avoids defense-research gate; default policy passes.
- [x] CLAUDE.md compliance check passed — international standards-track engagement is documented direction.
