---
rfc: 0222
title: CEN-CENELEC JTC 21 on AI — URML public-enquiry submission, request for comment from JTC 21 secretariat
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

# RFC-0222: CEN-CENELEC JTC 21 public-enquiry submission

## Summary

CEN-CENELEC JTC 21 (Joint Technical Committee on Artificial Intelligence) is the EU standards body for AI, with national-mirror committees feeding into JTC 21 across ~20 member countries (300+ experts). EU AI Act enforcement is driving multiple public-enquiry windows on prEN (preliminary European Norm) drafts through 2026. URML's intent layer + validator-gated execution is concrete structured-AI-intent worth submitting as related-art reference. This RFC documents URML's proposed public-enquiry submission to JTC 21, engaged via [jtc21.eu](https://jtc21.eu/) and routed via SII (Israel's national mirror) for downstream committee work, and **requests review and feedback from the JTC 21 secretariat + national-mirror coordinators**. No spec change.

## Motivation

JTC 21 has 300+ experts across 20+ countries and feeds EU AI Act standards implementation. URML's NL-to-primitive translation + manifest-validated dispatch is a concrete structured-AI-intent pattern relevant to several JTC 21 work items (transparency, high-risk classification, AI-on-systems standards). The recent prEN 18286 public enquiry (Oct-Dec 2025) demonstrates the JTC 21 cadence; further public enquiries are flagged for 2026.

Israel routes to JTC 21 via SII (Standards Institution of Israel, CEN affiliate). URML maintainer can submit public-enquiry comments without active committee seat; active TC seat at JTC 21 requires SII national-mirror committee participation (Phase 2 consideration).

URML benefits from documenting the engagement because:

1. **EU AI Act-adjacent standards-track presence.** JTC 21's public enquiries are the formal EU AI-standards-shaping surface. URML's structured-intent pattern fits the standards-shaping conversation.
2. **Related-art reference framing.** URML is not an AI safety standard; it is an open-source language with structured intent + validator-gated execution. Submitting as related-art reference is honest framing.
3. **Israeli national-mirror routing.** SII is the Israeli channel for JTC 21; engaging SII routes URML into the formal mirror-committee process. Phase 2.

## Detailed design

### URML proposed public-enquiry submission content (drafted in founder-actions-move17.md)

The 2-4 page comment submission (sent during next URML-relevant prEN public enquiry window) will cover:

1. **URML introduction (0.5 page).** Substrate-neutral robotics-intent language; Apache-2.0; relevance to AI-on-systems.
2. **Structured-intent + validator-gated-execution pattern (1-1.5 pages).** URML's NL → Layer-2 primitive translation + Layer-1 capability manifest + validator static-verification stage as concrete EU-AI-Act-related structured-intent example.
3. **Related-art reference (0.5-1 page).** Cross-citation with the JTC 21 work item under public enquiry; specific clause references where possible.
4. **Asks (3-5 specific questions).** Related-art framing acceptable; further public-enquiry cycles; SII national-mirror routing orientation.

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Submit a public-enquiry comment to next URML-relevant JTC 21 prEN window.** Founder-action via cencenelec.eu public-enquiry form.
2. **Establish SII national-mirror routing.** Phase 2 — SII committee participation requires more sustained engagement than Phase-1 URML supports.
3. **Cross-citation in URML EU-related docs.** URML's federal-alignment + EU AI Act compatibility framing references JTC 21 work as related-art.

### Compatibility notes

- **Engagement surface.** Public-enquiry portal on [jtc21.eu](https://jtc21.eu/) + [cencenelec.eu](https://www.cencenelec.eu/) — window-dependent for prEN drafts. Israeli national-mirror channel: SII (Standards Institution of Israel).
- **Governance.** CEN-CENELEC; JTC 21 secretariat under CEN-CENELEC management.
- **Origin.** EU (multi-national). NATO-allied; Horizon Europe associated countries (including Israel) participate.
- **License fit.** prEN drafts are CEN-CENELEC-purchase-licensed; URML's public-enquiry submission is URML's own work. No license conflict.
- **Maintainer signal.** Active; recent prEN 18286 public enquiry Oct-Dec 2025; further 2026 enquiry cycles flagged.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Public-enquiry comment submission only.
- Reference runtime: no change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Window-dependent.** Public-enquiry windows are ad-hoc; URML can draft the submission in advance but cannot submit until the next URML-relevant window opens.
- **Related-art-reference framing.** URML is not a safety standard or AI-act-compliance product; framing must avoid over-claiming relevance.
- **National-mirror committee participation is Phase 2.** Active TC seat at JTC 21 via SII requires Israeli national-mirror committee participation; URML at Phase 1 cannot sustain this.
- **EU AI Act enforcement is downstream.** URML's intent layer is not EU AI Act compliance material directly; the submission is related-art only.

## Alternatives considered

1. **Skip JTC 21; engage only Sub-wave B US-side (RFCs 0220 + 0221).** Rejected. EU-side engagement broadens URML's standards-track narrative across regulatory frames.
2. **Engage JTC 21 secretariat directly outside of public-enquiry windows.** Considered. Public-enquiry windows are the formal channel; direct secretariat engagement is informal. The two are compatible; this RFC focuses on the public-enquiry channel.
3. **Engage CEN TC 310 (Robotics) instead of JTC 21 (AI).** Considered. TC 310 is the dedicated robotics committee; JTC 21 covers AI-on-systems including robotics. URML's structured-intent pattern fits JTC 21's AI-on-systems scope better. Future Move-17 follow-up could engage TC 310 separately.
4. **Engage SII (Israeli mirror) first as gateway to JTC 21.** Considered. SII engagement is Phase 2 in the current ledger; engaging the public-enquiry portal first is lower-friction for Phase 1.

## Prior art

- [CEN-CENELEC JTC 21 home](https://jtc21.eu/).
- [CEN-CENELEC AI standards landing](https://www.cencenelec.eu/areas-of-work/cen-cenelec-topics/artificial-intelligence/).
- [SII Standards Institution of Israel](https://www.sii.org.il/) — Israeli national mirror to CEN-CENELEC.
- [RFC-0223 (DIN/DKE outreach)](0223-din-dke-ai-roadmap-outreach.md), [RFC-0224 (AFNOR outreach)](0224-afnor-grand-defi-ai-outreach.md) — sibling Sub-wave B RFCs feeding national-positions into JTC 21.
- [RFC-0225 (BSI AI Standards Hub outreach)](0225-bsi-ai-standards-hub-outreach.md) — UK-side AI standards engagement.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — URML's federal-alignment posture; EU JTC 21 engagement broadens to transatlantic.

## Unresolved questions

For the CEN-CENELEC JTC 21 secretariat + national-mirror coordinators:

1. **Related-art-reference acceptability.** Is URML's structured-intent + validator-gated-execution framing acceptable as related-art reference in JTC 21 public enquiries, or does JTC 21 expect submissions to be standard-conformance-claims?
2. **2026 enquiry calendar.** What's the JTC 21 2026 public-enquiry calendar for robotics-AI-relevant prEN drafts beyond what's been published?
3. **SII national-mirror routing.** What's the typical pathway for SII (Israel) to actively participate in JTC 21 working groups, and what's the threshold for that to be substantively meaningful (project-maturity, sustained engagement requirements)?
4. **EU AI Act compliance framing.** URML is not EU AI Act compliance material; how should URML's submission frame related-art reference to avoid misrepresenting AI-Act compliance posture?
5. **Cross-referencing DIN/DKE + AFNOR submissions.** URML is concurrently engaging DE (DIN/DKE) and FR (AFNOR) national channels feeding JTC 21. Is there value in cross-referencing those national-position files in the URML public-enquiry submission?
6. **TC 310 (Robotics) coordination.** Should URML's structured-intent framing engage CEN TC 310 in addition to JTC 21, or does JTC 21 cover the AI-on-systems including robotics scope sufficiently?
7. **Anything else.**

## Implementation note

RFC-0222 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Public-enquiry comment draft in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: public-enquiry portal on cencenelec.eu when next URML-relevant prEN window opens. Parallel routing via SII (Israeli national mirror). Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (JTC 21 active; 300+ experts; recent prEN 18286 public enquiry Oct-Dec 2025; further 2026 enquiry cycles flagged).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (window-dependent, related-art framing discipline, national-mirror Phase 2 constraint).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: CEN-CENELEC EU (multi-national, NATO-allied); Israel routes via SII (Horizon Europe associated country); default policy passes.
- [x] CLAUDE.md compliance check passed — international standards-track engagement is documented direction.
