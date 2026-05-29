---
rfc: 0226
title: OECD AI Policy Observatory — URML policy submission, request for comment from observatory team
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

# RFC-0226: OECD AI Policy Observatory submission

## Summary

The OECD AI Policy Observatory (OECD.AI) catalogues 850+ AI policies across 80+ jurisdictions and is the primary international-norms surface for AI policy aligned with the OECD AI Principles and the Hiroshima Process. URML, as an open-source robotics-intent-language with US-federal-aligned default policy + multi-national engagement footprint, fits the catalogue's open-source / structured-AI-intent / national-policy-initiative scope. Israel is an OECD member, so submission is direct. This RFC documents URML's proposed submission to the OECD AI Policy Observatory, engaged via [oecd.ai](https://oecd.ai/en/), and **requests review and feedback from the OECD AI Policy Observatory team**. No spec change.

**This RFC closes Sub-wave B of Move-17 (RFCs 0217-0226). Sub-wave B-with-RFC is complete; Sub-wave B membership-only (IIA, euRobotics, ADRA) is in the founder-actions-move17.md skeleton with no RFC needed.**

## Motivation

The OECD AI Policy Observatory is the single most-cited international-norms catalogue for AI policy. Listed policies feed into OECD member-country implementation discussions, the OECD AI Principles updates, and the Hiroshima Process work. URML's substrate-neutral robotics-intent language + US-federal alignment + multi-national open-source posture is exactly the shape an international-norms catalogue values.

Israel is a full OECD member; URML submission via Israeli national channel (Ministry of Innovation) is available as Phase 2 routing, but direct policy-submission to the observatory does not require national-channel routing.

URML benefits from documenting the engagement because:

1. **International-norms surface presence.** Submission to the OECD AI catalogue places URML on the international-norms map cited across OECD member countries.
2. **OECD AI Principles + Hiroshima Process alignment.** URML's open-source + transparency + structured-intent posture aligns with OECD AI Principles (human-centred values, transparency, robustness, accountability) and the Hiroshima Process's open-source-friendly framing.
3. **ONE.AI (OECD Network of Experts) orientation.** ONE.AI seat requires Israeli national nomination via Ministry of Innovation (Phase 2); observatory submission is the Phase-1 surface.

## Detailed design

### URML proposed observatory submission content (drafted in founder-actions-move17.md)

The observatory submission is a structured form fill + supporting document:

1. **Structured submission form fields.** Initiative title, originating jurisdiction (Israel + multi-national open-source), policy lever type (open standard), description, URL, contact. Approximate fields per current OECD.AI submission schema.
2. **Supporting document (1-2 pages).** URML introduction; OECD AI Principles + Hiroshima Process alignment narrative; sibling US-federal alignment (NDAA 889 / EO 14307 / FCC Covered List / SLSA cross-citations); EU engagement (JTC 21 + DIN/DKE + AFNOR + BSI); UK engagement (BSI AI Hub). Demonstrates URML's multi-national footprint as a credible open-source AI initiative.

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Submit URML to the OECD AI Policy Observatory catalogue.** Founder-action via OECD.AI submission form + supporting document.
2. **Cross-citation in URML international-policy-related docs.** URML's federal-alignment + international-engagement docs reference OECD AI Principles + Hiroshima Process where relevant.
3. **Future ONE.AI orientation.** Phase 2 — ONE.AI seat requires Israeli national nomination; observatory listing is the Phase-1 surface that opens the orientation conversation.

### Compatibility notes

- **Engagement surface.** [oecd.ai/en](https://oecd.ai/en/) — AI Policy Observatory submission portal.
- **Governance.** OECD (Organisation for Economic Co-operation and Development; Paris HQ, multilateral member organization).
- **Origin.** Multilateral; Israel is full OECD member. Passes US-federal default policy (US is also OECD member; OECD-cited norms are US-aligned).
- **License fit.** OECD.AI catalogues policies; no license conflict for cross-citation.
- **Maintainer signal.** Active; 850+ policies catalogued across 80+ jurisdictions; AI Wonk community open; ONE.AI Network of Experts active.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Observatory submission only.
- Reference runtime: no change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Submission-not-endorsement.** Observatory listing is catalogue inclusion, not OECD endorsement. URML must avoid over-claiming.
- **ONE.AI seat is Phase 2.** Observatory listing is the Phase-1 surface; deeper Network of Experts participation requires Israeli national nomination via Ministry of Innovation.
- **Multi-national framing requires care.** URML's US-federal default policy alignment + Israeli-domiciled maintainer + multi-national open-source posture must be framed clearly to avoid misrepresenting URML's national alignment to the observatory.

## Alternatives considered

1. **Skip OECD; engage only US + EU + UK national channels.** Rejected. International-norms surface presence is the strategic value-add; OECD catalogue is the canonical international-norms surface for AI policy.
2. **Engage OECD via Israeli Ministry of Innovation nomination only.** Rejected for Phase 1. Direct observatory submission is open; national-channel nomination is Phase 2 for ONE.AI seat.
3. **Engage UN AI bodies (UN AI Advisory Body, UNESCO AI ethics) instead.** Considered as future work; OECD AI Policy Observatory is the higher-leverage Phase-1 international-norms surface. UN bodies may be Move-18+ candidates.
4. **Wait for v1.0 before OECD submission.** Rejected. Observatory listing is open to Phase-1 open-source initiatives; structured-intent + validator-gated-execution is a real published artifact even at v0.1.0.

## Prior art

- [OECD AI Policy Observatory home](https://oecd.ai/en/).
- [OECD ONE.AI Network of Experts](https://oecd.ai/en/network-of-experts).
- [OECD National Robotics Initiative entry (example listed policy)](https://oecd.ai/en/dashboards/policy-initiatives/national-robotics-initiative-3118).
- [RFC-0222 (CEN-CENELEC JTC 21 outreach)](0222-cen-cenelec-jtc-21-outreach.md), [RFC-0223 (DIN/DKE outreach)](0223-din-dke-ai-roadmap-outreach.md), [RFC-0224 (AFNOR outreach)](0224-afnor-grand-defi-ai-outreach.md), [RFC-0225 (BSI AI Hub outreach)](0225-bsi-ai-standards-hub-outreach.md) — sibling Sub-wave B EU + UK standards engagements.
- [RFC-0220 (NIST EL ISD outreach)](0220-nist-el-isd-feedback-outreach.md), [RFC-0221 (ASTM F45.04 outreach)](0221-astm-f45-04-outreach.md) — sibling Sub-wave B US standards engagements.

## Unresolved questions

For the OECD AI Policy Observatory team:

1. **Observatory catalogue inclusion criteria for open-source initiatives.** Is URML's open-source robotics-intent-language framing a fit for the observatory catalogue, or does the catalogue prefer government-issued policies?
2. **Multi-national framing.** URML maintainer is Israeli-domiciled; default policy is US-federal-aligned; engagement footprint is multi-national. What's the observatory's preferred framing for cross-national initiatives?
3. **OECD AI Principles + Hiroshima Process alignment narrative.** URML's structured-intent + validator-gated-execution posture aligns with several OECD AI Principles (transparency, robustness, accountability). Is this framing observatory-relevant, or does it require formal AI Principles compliance assertion?
4. **ONE.AI Network of Experts orientation.** What's the realistic path for a Phase-1 open-source initiative to engage ONE.AI? Israeli national nomination via Ministry of Innovation is one route; are there alternatives?
5. **AI Wonk community engagement.** Is the AI Wonk community an appropriate channel for URML to publish related-art posts cross-referencing observatory-listed policies?
6. **Cross-reference to sibling EU + UK + US engagements.** Is the observatory submission strengthened by cross-referencing URML's parallel JTC 21 + DIN/DKE + AFNOR + BSI + NIST + ASTM engagements?
7. **Update cadence.** What's the typical update cadence for observatory-listed entries? URML's structural-separation arc and v1.0 milestone are future events worth signaling.
8. **Anything else.**

## Implementation note

RFC-0226 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Observatory submission form-fill + supporting document draft in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

This RFC closes Sub-wave B of Move-17 (RFCs 0217-0226 are now complete). Sub-wave B membership-only targets (IIA, euRobotics, ADRA) have no RFCs and live only in the founder-actions-move17.md skeleton. Sub-wave C (4 docket-watch + ~15 Tier B) require no RFCs in this wave.

## How to respond

Engagement channel: OECD AI Policy Observatory submission form at [oecd.ai/en](https://oecd.ai/en/). Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (OECD.AI active; 850+ policies catalogued; ONE.AI Network of Experts active).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (submission-not-endorsement, ONE.AI Phase 2, multi-national framing care).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OECD (multilateral, Paris HQ); Israel is full OECD member; US is OECD member; default policy passes.
- [x] CLAUDE.md compliance check passed — international-norms engagement is documented direction (multi-lingual NL layer + US-federal-aligned default policy are compatible with multilateral cataloguing).
