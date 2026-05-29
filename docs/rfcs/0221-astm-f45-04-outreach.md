---
rfc: 0221
title: ASTM F45.04 System Communication and Interoperability — URML position paper, request for comment from subcommittee
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

# RFC-0221: ASTM F45.04 interoperability position paper

## Summary

ASTM Committee F45 (Robotics, Automation, and Autonomous Systems) is the live US standards venue for industrial / autonomous robotics, co-chaired by NIST staff (Roger Bostelman). Subcommittee F45.04 (System Communication and Interoperability) is the URML-aligned subcommittee — it's the standardization surface where URML's Layer-1 HAL / Layer-2 intent boundary would naturally feed into. This RFC documents URML's proposed individual ASTM membership + F45.04 position paper, engaged via [astm.org/membership-participation/technical-committees/committee-f45](https://www.astm.org/membership-participation/technical-committees/committee-f45), and **requests review and feedback from ASTM F45.04 subcommittee members**. No spec change.

**This is the highest-leverage US SDO move in Move-17.** ASTM F45 is the active US standards venue (twice-yearly meetings, NIST staff co-chair) where URML's structural-separation arc most cleanly lands as standards-track contribution.

## Motivation

ASTM F45.04 is exactly the SDO surface URML would eventually feed its spec into. Subcommittees F45.02 (A-UGV Docking and Navigation), F45.05 (Grasping and Manipulation), and F45.06 (Legged Robot Systems) cover URML primitive scopes adjacent to F45.04's interoperability mandate. Paired engagement with NIST EL ISD (sibling RFC-0220) is the strategically coherent shape: NIST measurement-science work informs the standards; ASTM F45 standardizes the outputs.

ASTM membership is open internationally (Israel-domiciled participation is normal) at the individual / organizational tier; subcommittee participation is open to ASTM members. Membership has a paid annual fee (verify current cost at draft time).

URML benefits from documenting the engagement because:

1. **F45.04 is the right SDO surface.** Interoperability subcommittee scope matches URML's substrate-neutrality framing precisely.
2. **NIST EL ISD pairing.** Sibling RFC-0220 engages NIST EL ISD; F45's NIST staff co-chair (Roger Bostelman) makes the engagement-pair strategically coherent.
3. **Standards-track arc.** ASTM standards have downstream ANSI / ISO pickup paths. URML's structural-separation arc benefits from ASTM standards-track presence well before formal foundation candidacy.

## Detailed design

### URML proposed position paper content (drafted in founder-actions-move17.md)

The 3-5 page position paper to ASTM F45.04 will cover:

1. **URML introduction (0.5 page).** Substrate-neutral robotics-intent language, Apache-2.0 forever per Core Commitment, US-federal-aligned default policy file (RFC-0003), v0.1.0 shipped 2026-05-22.
2. **Interoperability problem statement (1 page).** Robotics deployments compose multiple runtime substrates (ROS 2 / PX4 / DDS / SLAM / sensor SDKs); URML's Layer-1 HAL declares the capability boundary, Layer-2 primitives the intent boundary. The interoperability standardization target is the Layer-1 ↔ Layer-2 boundary — what a manifest declares about a capability surface.
3. **Concrete URML manifest schema (1-2 pages).** URML's manifest YAML schema as a candidate interoperability layer; mapping to substrates covered by F45.02 (A-UGV navigation), F45.05 (grasping + manipulation), F45.06 (legged).
4. **Composability with existing standards (0.5-1 page).** URML composes against OPC UA Robotics (RFC-0214), ROS 2 (Move-16 RFC-0200), MoveIt 2 (Move-16 RFC-0202), Nav2 (Move-16 RFC-0201), MAVLink (Move-16 RFC-0197). Standards-cross-reference framing.
5. **Asks (3-5 specific questions for subcommittee).** F45.04 scope-fit; subcommittee participation; collaborative document development; downstream ANSI / ISO PAS pickup interest.

### What URML proposes (not a spec change, but a concrete adoption step)

This RFC does not propose a URML spec change. It proposes:

1. **URML maintainer takes ASTM individual membership.** Paid annual fee; verify current cost at draft time.
2. **URML submits a position paper to F45.04 subcommittee.** Founder-action via subcommittee chair contact obtained on becoming an F45 member.
3. **URML monitors F45.04 subcommittee work** going forward, contributing where URML's substrate-neutral interoperability framing applies.

### Compatibility notes

- **Engagement surface.** [astm.org/membership-participation/technical-committees/committee-f45](https://www.astm.org/membership-participation/technical-committees/committee-f45) — ASTM Committee F45 information; F45.04 subcommittee.
- **Governance.** ASTM International (US-domiciled SDO; West Conshohocken, PA; international membership).
- **Origin.** US-domiciled SDO. Passes US-federal default policy.
- **License fit.** ASTM standards are purchase-licensed; URML's position paper is URML's own work submitted to F45.04, which becomes ASTM-owned upon adoption. URML's open-source spec / runtime / validator stay Apache-2.0; the ASTM standards-track output is the separately-licensed work-product.
- **Maintainer signal.** Active; twice-yearly meetings; NIST staff co-chair (Roger Bostelman).
- **Cost.** ASTM individual membership has a paid annual fee.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** Future ASTM-driven standardization may inform URML spec evolution.
- Reference runtime: no change.
- Conformance suite: future ASTM F45.04 standards-track output may inform URML conformance-test design.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Cost.** Paid ASTM individual membership fee; recurring annual.
- **Sustained engagement requirement.** F45.04 subcommittee work is sustained (twice-yearly meetings + between-meeting work); URML maintainer time investment is real.
- **Standards-track licensing.** ASTM standards are purchase-licensed; URML's contribution becomes ASTM-owned upon adoption. This is the standard SDO arrangement and matches URML's structural-separation arc.
- **Israeli-founder caveat.** ASTM membership is international (Israeli-domiciled OK); some downstream US-federal procurement effects of ASTM standardization may have considerations URML should track.

## Alternatives considered

1. **Skip ASTM F45; engage only NIST EL ISD (sibling RFC-0220).** Rejected. NIST informs the science; ASTM standardizes the outputs. Engaging both is the strategic shape.
2. **Engage ANSI / RIA R15.08 instead of ASTM F45.** Rejected. R15.08 is the A3 (Automate.org) industrial-mobile-robot safety standard; URML's interoperability framing is broader than mobile-robot safety. F45.04 is the right interoperability scope.
3. **Defer ASTM until URML has more community.** Rejected. ASTM individual membership is open at Phase 1; position paper submission is open. Sustained engagement can scale up as URML's community grows.
4. **Engage F45 parent committee directly rather than F45.04 subcommittee.** Rejected. The interoperability scope is F45.04-specific; per-subcommittee engagement is the right shape. F45 parent committee oversight reaches indirectly.

## Prior art

- [ASTM Committee F45](https://www.astm.org/membership-participation/technical-committees/committee-f45) — Robotics, Automation, and Autonomous Systems.
- [ASTM Committee F45 Subcommittees](https://www.astm.org/membership-participation/technical-committees/committee-f45/subcommittee-f45) — F45.02 / F45.04 / F45.05 / F45.06.
- [RFC-0220 (NIST EL ISD outreach)](0220-nist-el-isd-feedback-outreach.md) — sibling Sub-wave B US-standards engagement; same NIST staff Roger Bostelman is F45 co-chair.
- URML Layer-1 HAL + Layer-2 primitives spec docs (in `spec/` directory).
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md), [RFC-0214 (OPC UA Robotics outreach)](0214-opc-foundation-ua-nodeset-outreach.md) — sibling industrial-interoperability engagements URML cross-references.

## Unresolved questions

For ASTM F45.04 subcommittee members + F45 committee chair:

1. **F45.04 scope-fit.** Does URML's substrate-neutral manifest + Layer-1 / Layer-2 boundary match F45.04's interoperability mandate, or is the scope different in ways URML should adjust framing to address?
2. **Subcommittee participation channel.** What's the typical channel for an individual ASTM member to contribute a position paper + propose collaborative document development at F45.04?
3. **Collaborative document development.** Is F45.04 interested in scoping a URML-position-paper-driven standards-track document, or does subcommittee prefer URML contribute to existing F45.04 documents?
4. **Downstream ANSI / ISO PAS pickup.** What's the typical ASTM → ANSI → ISO PAS pickup path for F45 standards? URML's structural-separation arc benefits from downstream pickup orientation.
5. **NIST EL ISD pairing.** Sibling RFC-0220 engages NIST EL ISD; F45 NIST staff co-chair Roger Bostelman is the natural cross-engagement contact. Is the engagement-pair pattern (NIST EL ISD + ASTM F45.04) the right shape?
6. **Cross-references with adjacent subcommittees.** F45.02 (A-UGV Navigation), F45.05 (Grasping + Manipulation), F45.06 (Legged) cover URML primitive scopes; should URML's F45.04 position paper cross-reference adjacent subcommittees, or stay scoped to F45.04?
7. **Israeli-domiciled-member orientation.** Are there practical considerations for Israeli-domiciled individual members participating in F45.04 work?
8. **Anything else.**

## Implementation note

RFC-0221 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml). Position paper draft + ASTM membership-application supporting statement in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## How to respond

Engagement channel: ASTM individual membership at [astm.org/membership-participation/membership-options](https://www.astm.org/membership-participation/membership-options) + F45.04 subcommittee chair contact obtained on becoming a member. Founder-action sending under maintainer identity.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (ASTM F45 active; F45.04 subcommittee scope confirmed; NIST staff co-chair Roger Bostelman).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (cost, sustained engagement, standards-track licensing, Israeli-founder caveat).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: ASTM US-domiciled SDO (West Conshohocken PA); international membership; default policy passes.
- [x] CLAUDE.md compliance check passed — standards-track engagement is documented direction.
