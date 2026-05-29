---
rfc: 0220
title: NIST EL Intelligent Systems Division Robotics Community Feedback memo, request for comment from program manager
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

# RFC-0220: NIST EL Intelligent Systems Division Robotics Community Feedback memo

## Summary

NIST Engineering Lab Intelligent Systems Division (NIST EL ISD) owns the US measurement-science work behind robotics performance testing — agility, manipulation, mobility, perception categories. Their published Modular Open-Source Robotics Testbed (MORT) and ARIAC competition surface measurement-science needs that URML's manifest + validator + conformance suite are structurally positioned to inform. This RFC documents URML's proposed 1-2 page feedback memo to NIST EL ISD program manager Craig Schlenoff, via the [Robotics Community Feedback](https://www.nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback) page, and **requests review and feedback from NIST EL ISD**. No spec change.

## Motivation

NIST EL ISD's Robotics Community Feedback page is the explicit US-federal channel for community input on measurement-science needs. Program manager Craig Schlenoff also chairs ASTM Committee F45 (sibling RFC-0221), which makes the engagement strategically coherent: NIST EL ISD informs the measurement-science research; ASTM F45 standardizes the outputs.

URML's manifest declares capability surfaces; URML's validator gates execution against that manifest; URML's conformance suite asserts substrate-vs-manifest match. These three together map onto NIST EL ISD's existing performance categories cleanly:

| URML surface | Maps to NIST EL ISD performance category |
|---|---|
| Mobility primitives (`move_to`, `dock`, `scan_area`) | Mobility performance category |
| Manipulation primitives (`pick_from`, `place_at`, `grasp`, `release`, `swap_tool`) | Manipulation + agility performance categories |
| Perception manifest (lidar / camera / radar declarations) + sibling SLAM enum from RFCs 0205-0207 + 0211 | Perception performance category |
| `safety_envelope` manifest field | Safety performance category |

URML benefits from documenting the engagement because:

1. **Measurement-science alignment.** NIST EL ISD is the US institutional home for robotics measurement standards. Warming the relationship now positions URML's future structural-separation (501(c)(6) / SDO / sponsored project) for credibility.
2. **MORT cross-citation opportunity.** NIST's Modular Open-Source Robotics Testbed (MORT) is a public testbed; URML's reference runtimes could compose against MORT, providing concrete measurement instances.
3. **ARIAC cross-citation opportunity.** Agile Robotics for Industrial Automation Competition (ARIAC) is a NIST-run competition; URML's industrial profile (RFC-0013) primitives could be expressed in ARIAC scenario terms.

## Detailed design

### URML proposed feedback memo content (drafted in founder-actions-move17.md)

The 1-2 page memo to Craig Schlenoff will cover:

1. **URML introduction (1 paragraph).** Substrate-neutral robotics-intent language, Apache-2.0 forever per Core Commitment, US-federal-aligned default policy file (RFC-0003).
2. **Measurement-science mapping (1-2 paragraphs + table).** URML's manifest + validator + conformance suite mapped onto NIST EL ISD's performance categories (agility / manipulation / mobility / perception / safety).
3. **MORT + ARIAC cross-citation interest (1 paragraph).** URML's reference runtimes could compose against MORT; URML's industrial profile primitives align with ARIAC scenario vocabulary.
4. **Future engagement orientation (1 paragraph).** URML's planned structural separation (per CLAUDE.md) and how a warming NIST EL ISD relationship would inform that.
5. **Asks (3-5 specific questions).** Measurement-science fit; MORT collaboration channel; ARIAC URML-language framing; structural-separation orientation.

The memo carries the URML RFC link as appendix. Email cover (sent to craig.schlenoff [at] nist.gov, secondary CC RobotTestMethods [at] nist.gov) is one paragraph + memo attached.

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Send a feedback memo to NIST EL ISD program manager.** Founder-action via direct email.
2. **Cross-citation in URML measurement-related docs.** URML's conformance-suite documentation references NIST EL ISD performance categories as related-art mapping.
3. **MORT / ARIAC orientation conversation.** If NIST EL ISD is interested, URML can explore composing reference runtimes against MORT or expressing industrial-profile primitives in ARIAC scenario terms.

### Compatibility notes

- **Engagement surface.** [nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback](https://www.nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback) — explicit US-federal community feedback channel.
- **Contact.** Craig Schlenoff (craig.schlenoff [at] nist.gov), program manager NIST EL ISD. Secondary CC: RobotTestMethods [at] nist.gov.
- **Governance.** NIST (US federal, Department of Commerce).
- **Origin.** US federal. Passes US-federal default policy (URML is itself US-federal-aligned).
- **License fit.** NIST published outputs are typically public-domain US government works. URML's Apache-2.0 cross-citation is clean.
- **Maintainer signal.** Active program; MORT + ARIAC + ASTM F45 connections.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** Cross-citation only.
- Reference runtime: future MORT-composition is candidate work (not in scope here).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Federal-engagement cadence.** NIST program managers receive substantial inbound; URML's memo competes for attention. Email cover must be precise.
- **Israeli-founder caveat.** URML maintainer is Israel-domiciled; NIST EL ISD engagement is community feedback (no citizenship gate), but downstream MORT / ARIAC collaboration may have considerations.
- **Cross-citation does not equal endorsement.** URML cannot represent NIST EL ISD review as endorsement; the engagement is informational feedback exchange.

## Alternatives considered

1. **Skip NIST EL ISD; engage only ASTM F45 (sibling RFC-0221).** Rejected. NIST EL ISD and ASTM F45 are paired engagements (NIST informs the science; ASTM standardizes the outputs); engaging both is the right shape.
2. **Engage NIST CAISI (AI agent standards) instead of EL ISD.** Considered. CAISI is the AI-agent-specific surface and has an open RFI track; URML's LLM bridge maps onto agent-system patterns. CAISI is tracked in Sub-wave C federal-docket-watch (no current URML-shaped window). EL ISD is the right Sub-wave B target because it's the always-open community-feedback channel and aligns with measurement-science framing.
3. **Engage NIST via Federal Register comment docket only.** Rejected. NIST EL ISD's explicit community-feedback page is a lower-friction first contact than a Federal Register docket comment.
4. **Defer NIST EL ISD until URML has US-domiciled co-author for the memo.** Considered. The community-feedback channel is open without US-domiciled co-author requirement; orientation can happen now.

## Prior art

- [NIST Robotics Community Feedback page](https://www.nist.gov/el/intelligent-systems-division-73500/robotics-community-feedback).
- [NIST Mobile Robotics Standards page](https://www.nist.gov/el/intelligent-systems-division-73500/mobile-robotics-systems-research-and-standard-test-methods).
- [NIST Modular Open-Source Robotics Testbed (MORT)](https://www.nist.gov/el/intelligent-systems-division-73500/modular-open-source-robotics-testbed-mort).
- ARIAC (Agile Robotics for Industrial Automation Competition).
- [RFC-0221 (ASTM F45.04 outreach)](0221-astm-f45-04-outreach.md) — sibling Sub-wave B US-standards engagement; same NIST staff co-chair via Roger Bostelman.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — URML's US-federal posture.

## Unresolved questions

For NIST EL ISD program manager Craig Schlenoff:

1. **Measurement-science fit.** Does URML's manifest + validator + conformance-suite framing map usefully onto NIST EL ISD's performance categories (agility / manipulation / mobility / perception / safety)?
2. **MORT collaboration channel.** Is there a NIST EL ISD path for an external project (URML) to compose reference runtimes against MORT, contribute measurement scenarios, or both?
3. **ARIAC URML-language framing.** URML's industrial profile primitives (`pick_from`, `place_at`, `swap_tool`) align with ARIAC industrial-automation scenario vocabulary. Is there interest in expressing ARIAC scenarios in URML language as a related-art reference?
4. **Structural-separation orientation.** URML plans structural separation per CLAUDE.md (501(c)(6) / SDO / sponsored project). Is there NIST EL ISD guidance on US-federal-aligned foundation structures for robotics-standards projects?
5. **ASTM F45 + NIST EL ISD coordination.** Sibling RFC-0221 engages ASTM F45.04 (which Craig Schlenoff is associated with via the broader F45 committee). Is the engagement-pair pattern (NIST EL ISD + ASTM F45) the right shape, or are there other coordination channels URML should engage?
6. **Conformance-listing reciprocal.** Would NIST EL ISD consider noting URML in any community-resource list once URML's manifest + validator + conformance-suite is reviewable?
7. **Anything else.**

## Implementation note

RFC-0220 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Memo draft + email cover in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: single email to craig.schlenoff [at] nist.gov with 1-2 page memo attached + secondary CC RobotTestMethods [at] nist.gov. Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (NIST EL ISD Robotics Community Feedback page live; MORT + ARIAC active).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (federal-engagement cadence, Israeli-founder caveat, cross-citation-not-endorsement).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: NIST US federal (Department of Commerce); default policy passes.
- [x] CLAUDE.md compliance check passed — US-federal alignment + measurement-science engagement is documented direction.
