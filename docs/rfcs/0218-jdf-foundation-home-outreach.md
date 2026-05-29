---
rfc: 0218
title: Joint Development Foundation (JDF) foundation-home inquiry, request for comment from JDF / Linux Foundation
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

# RFC-0218: JDF foundation-home inquiry

## Summary

URML's planned structural separation (per [`CLAUDE.md`](../../CLAUDE.md)) requires a long-term foundation home. The Joint Development Foundation (JDF) is the Linux Foundation Projects affiliate purpose-built for standards-track open-source projects, used by OpenUSD (Alliance for OpenUSD), OpenChain, and ~500 other member orgs. JDF is also an ISO/IEC JTC 1 PAS submitter, which is the standards-track path URML eventually targets. This RFC documents URML's foundation-home inquiry to JDF via the LF contact channel, and **requests feedback from the JDF / Linux Foundation on whether URML would be a candidate JDF Projects affiliate**. No spec change.

**This is the second of two headline Sub-wave B targets in Move-17.** Sibling RFC-0217 (OSRA) is the robotics-native option; this RFC covers the multi-domain neutral-foundation alternative. URML is engaging both concurrently to understand the structural-separation options.

## Motivation

JDF is the cleanest neutral-foundation path for an open standard. Its purpose is to operationalize the path from "open standard hosted by a maintainer" to "ISO/IEC PAS submission." Recent precedents: AOUSDF (Alliance for OpenUSD) ratified Core Spec 1.0 in 2026; OpenChain submitted ISO/IEC 5230 via JDF.

URML's long-term goal — venture-scale outcome anchored on a moat-creating standard — is exactly the shape JDF was built for. Trademarks stay with the founder until assigned; code is DCO-signed (not CLA) for clean future re-organization; the commercial surround stays out of this repo. These all match JDF's expected project shape.

URML benefits from documenting the engagement because:

1. **JDF is the neutral-standards-path foundation.** Not robotics-native (that's OSRA, sibling RFC-0217), but standards-track-native. Useful precedents: OpenUSD, OpenChain.
2. **ISO/IEC JTC 1 PAS submission path.** JDF is a recognized PAS submitter; URML's long-term standards-track plan benefits from sitting on the JDF rails rather than reinventing the path.
3. **Linux Foundation alignment.** LF-domiciled, US-aligned. Composable with URML's other LF engagements (ELISA RFC-0213, OpenSSF SLSA RFC-0215, OpenSSF Scorecard RFC-0216, ROS-Industrial earlier sub-wave / future).

## Detailed design

### Why JDF is the cleanest neutral path

JDF's project-formation flow:

1. Project proposers draft a charter (governance model, IP policy, trademark assignment, member tiers).
2. JDF/LF reviews and approves; project gets a JDF Projects affiliate registration.
3. Project operates under JDF charter; LF provides legal / financial / operational substrate.
4. When ready, project can submit standards (e.g., to ISO/IEC JTC 1) via JDF's PAS submitter status.

This matches URML's planned arc: spec ↔ reference runtimes ↔ conformance suite ↔ eventual ISO/IEC standardization.

### What URML proposes (an inquiry, not a commitment)

This RFC documents an inquiry, not a spec or governance change. It proposes:

1. **JDF Projects affiliate orientation.** URML inquires about typical project-formation flow, charter templates, IP-assignment expectations, and timeline.
2. **PAS submission orientation.** URML asks about JDF's process for downstream ISO/IEC JTC 1 PAS submission, and what project-maturity threshold is typical.
3. **Comparison with OSRA path.** URML transparently flags that it is engaging both JDF (this RFC) and OSRA (sibling RFC-0217) concurrently, to understand the structural-separation options.
4. **Timing question.** URML asks JDF / LF about project-maturity threshold for affiliate registration (community size, governance maturity, US-domiciled co-sponsor expectations).

### What URML does NOT propose

- URML does not propose moving to JDF today. Phase-1 URML is a single-maintainer project; foundation affiliate registration typically expects more community maturity.
- URML does not commit to JDF as the structural-separation target. The OSRA sibling inquiry is also open.
- URML does not propose making the JDF charter robotics-specific. JDF is multi-domain by design; URML's robotics scope would be a project-level concern, not a foundation-level one.

### Compatibility notes

- **Engagement surface.** [jointdevelopment.org](https://jointdevelopment.org/) — JDF contact channel; alternative is Linux Foundation member-services email.
- **Governance.** Linux Foundation (501(c)(6) industry association; Delaware-domiciled). JDF is a Projects affiliate of the LF.
- **Origin.** US-domiciled (Linux Foundation Delaware). Passes US-federal alignment per [`CLAUDE.md`](../../CLAUDE.md). Multi-national membership.
- **License fit.** License-agnostic at the JDF level; URML's Apache-2.0 stance is standard for JDF affiliates.
- **Maintainer signal.** Active; 500+ member orgs; OpenUSD AOUSDF Core Spec 1.0 ratified 2026; OpenChain on JDF.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** This is a foundation-home orientation inquiry.
- Reference runtime: no change; URML's repo would continue to host the open-source spec / runtime / validator / conformance suite per the Core Commitment.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Inquiry, not commitment.** URML is not committing to JDF as the structural-separation target; this RFC is reconnaissance.
- **Not robotics-native.** JDF is multi-domain; URML would not benefit from co-located robotics-community network effects the way it would at OSRA.
- **Phase-1 timing.** Project-formation typically expects more community maturity than URML has today.
- **Competing inquiry.** Sibling RFC-0217 (OSRA) is concurrently open. JDF / LF may reasonably ask why URML is engaging both — the honest answer is that URML wants to understand the options before committing.

## Alternatives considered

1. **Engage only OSRA (robotics-native) and skip JDF.** Rejected. OSRA is ROS-coded; URML's substrate-neutrality could be diluted. JDF preserves the neutrality.
2. **Engage CNCF instead of JDF.** Rejected. CNCF has no robotics SIG; a CNCF Robotics SIG would need to be proposed first, which is structurally different from JDF Projects affiliate registration (per Move-17 research file Tier C documentation).
3. **Engage Apache Software Foundation instead of JDF.** Rejected. Apache has zero robotics-relevant repos in 3,131 surveyed; not a fit (per Move-17 research file Tier C documentation).
4. **Engage Eclipse Foundation as a foundation-home candidate (beyond Move-16 + Move-17 Sub-wave A cross-citations).** Rejected for now. Eclipse Foundation is non-US-domiciled (BE), which is a soft mismatch with [`CLAUDE.md`](../../CLAUDE.md)'s preference for US-domiciled foundation. Cross-citation engagements (Move-16 + Move-17 Sub-wave A) are appropriate; foundation-home is not the right framing for Eclipse.

## Prior art

- [Joint Development Foundation](https://jointdevelopment.org/) — JDF homepage.
- [JDF 10 years (Linux Foundation press)](https://www.linuxfoundation.org/press/joint-development-foundation-celebrates-10-years-of-high-impact-open-standards-innovation-and-development).
- [JDF as ISO/IEC JTC 1 PAS submitter](https://www.linuxfoundation.org/press/press-release/joint-development-foundation-adds-a-path-for-formal-international-standardization).
- [AOUSDF (Alliance for OpenUSD) Core Spec 1.0 ratified 2026](https://www.linuxfoundation.org/press/alliance-for-openusd-announces-core-specification-1.0-the-universal-language-for-building-3d-worlds).
- [`CLAUDE.md`](../../CLAUDE.md) structural-separation clause.
- [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) — what stays Apache-2.0 forever.
- [RFC-0217 (OSRA foundation-home outreach)](0217-osra-foundation-home-outreach.md) — sibling Move-17 Sub-wave B headline RFC; robotics-native alternative.

## Unresolved questions

For the JDF / Linux Foundation maintainers:

1. **Project-formation threshold.** What's the typical project-maturity threshold for JDF Projects affiliate registration (community size, governance maturity, US-domiciled co-sponsor expectation, time-since-v1.0)?
2. **Charter template orientation.** Are there JDF charter templates URML could adopt (with URML-specific governance overlay), or does each affiliate write its own?
3. **PAS submission path orientation.** What's JDF's typical timeline + threshold for downstream ISO/IEC JTC 1 PAS submission? URML's eventual standards-track goal includes PAS submission.
4. **IP + trademark assignment expectations.** URML's trademark is in the founder's name and assignable per [`CLAUDE.md`](../../CLAUDE.md). What's JDF's expectation for trademark + IP assignment to the affiliate?
5. **Multi-domain composition.** URML's scope is robotics; JDF's scope is multi-domain. Is there benefit (or constraint) to JDF affiliate registration for a domain-specific project like URML?
6. **Comparison with sponsored-project foundations (OSRA, CNCF, Apache).** URML is engaging both JDF (this RFC) and OSRA (sibling RFC-0217). Are there scenarios where JDF would recommend a robotics-native foundation over JDF for URML's specific needs?
7. **Geographic / domicile considerations.** URML maintainer is Israel-domiciled; JDF / LF are US-domiciled. Are there domicile constraints on affiliate maintainers, or is it project-org-level?
8. **Anything else.**

## Implementation note

RFC-0218 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

Engagement channel: JDF contact via [jointdevelopment.org](https://jointdevelopment.org/) — likely jdfsupport@linuxfoundation.org (verify at draft time). Founder-action sending under maintainer identity. Draft artifact in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (JDF active; 500+ member orgs; OpenUSD AOUSDF Core Spec 1.0 ratified 2026; OpenChain on JDF).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (inquiry-not-commitment, not robotics-native, Phase-1 timing, competing inquiry to OSRA).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation US-domiciled Delaware; default policy passes.
- [x] CLAUDE.md compliance check passed — structural-separation reconnaissance is the documented direction.
