---
rfc: 0217
title: Open Source Robotics Alliance (OSRA) foundation-home inquiry, request for comment from OSRA Project Management Committee
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

# RFC-0217: OSRA foundation-home inquiry

## Summary

URML's planned structural separation (per [`CLAUDE.md`](../../CLAUDE.md): "a non-profit foundation owning the standard ... a 501(c)(6) industry association, an SDO with strong US ties, or a sponsored project under an existing US-domiciled foundation") needs a long-term home. The Open Source Robotics Alliance (OSRA) is the closest robotics-native foundation-home candidate. This RFC documents URML's foundation-home inquiry to OSRA via the alliance contact channel at [osralliance.org](https://osralliance.org/), and **requests feedback from the OSRA Project Management Committee on whether URML would be a candidate sponsored-project under OSRA**. No spec change.

**This is one of two headline Sub-wave B targets in Move-17.** Sibling RFC-0218 (JDF) is the neutral / multi-domain alternative. OSRA is the robotics-native option; JDF is the multi-domain-foundation option. URML is engaging both to understand the structural-separation options before committing.

## Motivation

OSRA is the alliance governance body over ROS / Gazebo / Open-RMF, with a meritocratic + mixed-membership model. 2026 inaugural Platinum members include NVIDIA, Intrinsic, and Qualcomm. The alliance is OSRF-domiciled (US, Mountain View CA) and is the natural robotics-foundation answer in the US.

URML's open-source-forever Core Commitment (per [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) plus the planned non-commercial-in-repo discipline (commercial surround is out of this repo) match the OSRA charter shape. URML's substrate-neutrality (ROS 2 is the *first* reference runtime, not the only one) is the open question for OSRA fit.

URML benefits from documenting the engagement because:

1. **OSRA is the robotics-native foundation candidate.** Closest existing foundation-home match for URML's structural-separation plan.
2. **Substrate-neutrality vs ROS-alignment is the key fit question.** URML composes onto ROS 2 + PX4 + others; OSRA's existing projects are ROS / Gazebo / Open-RMF. The fit question is whether OSRA's charter accommodates a substrate-neutral robotics-intent-language alongside its ROS-aligned projects.
3. **Phase-1 timing.** URML is single-maintainer Phase-1; this RFC is an orientation inquiry, not a sponsored-project application. The right time for an application is when URML has measured-adoption data and / or US-domiciled co-sponsors.

## Detailed design

### URML structural-separation context (recap from CLAUDE.md)

Per [`CLAUDE.md`](../../CLAUDE.md):
- "Trademarks are filed in the founder's name initially and assignable"
- "Code is contributed under DCO sign-off (not CLA) so future re-organization is clean"
- "No commercial features are merged into this repository"
- "A non-profit foundation owning the standard (the moat) and a for-profit company selling adjacent products (the revenue)"
- "The realistic foundation target is US-domiciled and aligned with US federal law"

OSRA fits the US-domiciled + US-aligned criteria. OSRF (which underlies OSRA) is a 501(c)(3) public charity domiciled in California; OSRA itself is the alliance governance layer over OSRF's projects.

### What URML proposes (an inquiry, not a spec change)

This RFC documents an inquiry, not a spec or governance change. It proposes:

1. **OSRA membership-tier orientation.** URML inquires about Associate / Sponsor / Platinum membership tiers, fees, and obligations.
2. **Sponsored-project candidate orientation.** URML asks whether OSRA's charter accommodates a sponsored-project candidacy for a substrate-neutral robotics-intent language (URML), distinct from but composable with OSRA's existing ROS-aligned projects.
3. **Timing question.** URML asks the OSRA PMC about the typical project-maturity threshold for sponsored-project candidacy (community size, adoption metrics, time-since-v1.0) — this informs URML's roadmap for when a formal candidacy would be realistic.

### What URML does NOT propose

- URML does not propose moving to OSRA today. Phase-1 URML lacks the measured adoption + US-domiciled co-sponsor pattern that would make a sponsored-project candidacy substantive.
- URML does not propose a ROS-only realignment. URML's substrate-neutrality is core; engagement with OSRA is conditional on accommodating it.
- URML does not commit to any specific structural-separation target. Sibling RFC-0218 (JDF) covers the neutral-foundation alternative; both are open inquiries until a decision lands.

### Compatibility notes

- **Engagement surface.** [osralliance.org](https://osralliance.org/) — alliance contact form / direct email to OSRF executive contact.
- **Governance.** OSRF (501(c)(3) public charity, California-domiciled) underlies OSRA; OSRA is the alliance layer.
- **Origin.** US-domiciled (Mountain View CA). Passes US-federal alignment per [`CLAUDE.md`](../../CLAUDE.md).
- **License fit.** OSRF-stewarded projects are Apache-2.0 (ROS / Gazebo) and Apache-2.0 / BSD-3 (Open-RMF). Clean URML Apache-2.0 fit.
- **Maintainer signal.** Active; 2026 inaugural Platinum members NVIDIA / Intrinsic / Qualcomm; alliance governance documented publicly.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none.** This is a foundation-home orientation inquiry.
- Reference runtime: URML's `reference/ros2-runtime/` would naturally align with OSRA-governed projects; no change required.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Inquiry, not commitment.** URML is not committing to OSRA as the structural-separation target; this RFC is reconnaissance.
- **ROS-alignment risk.** OSRA's existing projects are ROS-aligned; URML's substrate-neutral identity could be diluted by hosting in a ROS-coded foundation. The whole Move-16 substrate-spine wave just engaged the substrate-neutral identity explicitly; OSRA fit needs to preserve that.
- **Phase-1 timing.** Sponsored-project candidacy typically requires community + adoption metrics URML does not yet have. The inquiry is an orientation, not an application.
- **Competing inquiry.** Sibling RFC-0218 (JDF) covers the neutral-foundation alternative; both are concurrently open. OSRA may reasonably ask why URML is engaging both — the honest answer is that URML wants to understand the options before committing.

## Alternatives considered

1. **Engage OSRA after URML has measured adoption.** Considered. Orientation inquiry can happen now without committing; substantive candidacy can wait for later. This RFC is the orientation step.
2. **Engage only JDF (neutral foundation) and not OSRA.** Rejected. OSRA is the robotics-native option; not engaging it would close off the robotics-foundation lane prematurely.
3. **Skip foundation-home reconnaissance and stay founder-owned.** Rejected. Per [`CLAUDE.md`](../../CLAUDE.md), structural separation is the planned target; reconnaissance starts now even if execution is later.
4. **Engage at the OSRF (underlying 501(c)(3)) level rather than OSRA (alliance).** Considered. OSRA is the project-governance layer URML would compose into; OSRF is the legal underlying. Engaging OSRA is the right entry point; OSRF can be a downstream conversation.

## Prior art

- [Open Source Robotics Alliance launch](https://osralliance.org/open-robotics-launches-the-open-source-robotics-alliance-2/) — the alliance formation.
- [OSRA announcement (OSRF, March 2024)](https://www.openrobotics.org/blog/2024/3/18/announcing-the-open-source-robotics-alliance-osra).
- [`CLAUDE.md`](../../CLAUDE.md) structural-separation clause — URML's foundation-home roadmap.
- [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) — what stays Apache-2.0 forever.
- [RFC-0218 (JDF foundation-home outreach)](0218-jdf-foundation-home-outreach.md) — sibling Move-17 Sub-wave B headline RFC; neutral-foundation alternative.

## Unresolved questions

For the OSRA Project Management Committee:

1. **Substrate-neutrality accommodation.** Does the OSRA charter accommodate a sponsored-project candidacy for a substrate-neutral robotics-intent-language (URML) distinct from OSRA's existing ROS-aligned projects? Or is OSRA explicitly ROS-aligned and URML would need to declare ROS as the primary substrate?
2. **Project-maturity threshold.** What's the typical project-maturity threshold for sponsored-project candidacy (community size, adoption metrics, time-since-v1.0, US-domiciled co-sponsor requirement)?
3. **Membership-tier orientation.** Associate / Sponsor / Platinum tiers — fees, obligations, voting rights? What's the realistic tier for a Phase-1 single-maintainer project as a first engagement?
4. **Trademark + IP assignment.** URML's trademark is in the founder's name and assignable per [`CLAUDE.md`](../../CLAUDE.md). What's OSRA's trademark + IP-assignment expectation for sponsored projects?
5. **Foundation-host vs alliance-membership distinction.** OSRA hosts sponsored projects (ROS / Gazebo / Open-RMF). Is "foundation-home" the right framing, or is "alliance-membership for a separately-stewarded project" the intermediate step?
6. **Geographic / domicile considerations.** URML maintainer is Israel-domiciled; OSRA / OSRF are US-domiciled. Does the alliance have domicile constraints on sponsored-project maintainers, or is it project-org-level?
7. **Substrate-spine engagement context.** URML Move-16 (RFCs 0196-0211) explicitly engaged substrate maintainers (PX4 / ROS 2 core / DDS / SLAM) including ROS 2 core itself (RFC-0200). Is OSRA aware of those engagements and would they alter the fit conversation?
8. **Anything else.**

## Implementation note

RFC-0217 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

Engagement channel: [osralliance.org](https://osralliance.org/) contact form, with founder-action sending under maintainer identity. Draft artifact in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (OSRA alliance live; 2026 Platinum members announced).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (inquiry-not-commitment, ROS-alignment risk, Phase-1 timing, competing inquiry to JDF).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OSRA / OSRF US-domiciled California; default policy passes.
- [x] CLAUDE.md compliance check passed — structural-separation reconnaissance is the documented direction.
