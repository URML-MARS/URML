---
rfc: 0300
title: Locus Robotics integration, research-collab proposal (off-GitHub, via the interop layer)
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-01
updated: 2026-06-01
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

# RFC-0300: Locus Robotics integration, research-collab proposal (off-GitHub, via the interop layer)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Locus Robotics (goods-to-person warehouse AMRs, US-domiciled). The ask is research-collab: how URML's intent vocabulary would compose with a Locus fleet, and a question about whether an integration surface exists. **Engagement surface is off-GitHub**: Locus publishes no public developer API or GitHub org (consistent with the Move #15 finding that the major AMR makers have closed surfaces); the channel is the company contact surface. The likely technical bridge is the **AMR interop layer** ([RFC-0297 VDA5050](0297-vda5050-outreach.md), [RFC-0298 InOrbit / MassRobotics standard](0298-inorbit-ros-amr-interop-outreach.md)), to which Locus is connected as a MassRobotics AMR Interoperability Standard participant.

## Motivation

Locus Robotics (Wilmington, MA, USA; default-policy pass) is a category leader in goods-to-person picking AMRs, deployed at 350+ sites. It is a documented participant in the MassRobotics AMR Interoperability Standard working group, which is precisely the layer URML composes above ([RFC-0298](0298-inorbit-ros-amr-interop-outreach.md)). URML's value for a Locus customer is natural-language intent authoring plus cross-robot static validation, riding the interop standard rather than requiring a Locus-specific SDK.

Verified surface (2026-06-01):
- Company: locusrobotics.com (US HQ Wilmington MA; EU office Amsterdam). LocusOne fleet management.
- **No public developer API / SDK / GitHub org located.** Engagement is off-GitHub.
- Interop link: Locus is a MassRobotics AMR Interop Standard participant.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the Locus company contact surface.** URML's identity, motivation, and one question: does Locus expose (or plan) an integration surface — directly or via the MassRobotics standard / VDA5050 — that a substrate-neutral intent layer could target?
2. **If a surface exists or opens**, URML targets the **interop layer** rather than a Locus-private API: a URML program validates ([RFC-0286](0286-multi-robot-fleet-addressing.md) `validate_fleet` + [RFC-0291](0291-utm-strategic-deconfliction.md) clearance) and emits MassRobotics-standard / VDA5050 messages a Locus fleet already understands. Zero new URML vocabulary ([RFC-0022](0022-warehouse-domain-profile.md)).

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified developer surface.** Locus has not published an API / SDK / GitHub org. This RFC is a courtesy + question, not an adapter pre-design.
- **Goods-to-person model.** Locus AMRs follow a goods-to-person picking pattern; URML's mapping is region-based mobility + reporting, not free manipulation. Named honestly.
- **Light engagement payload.** Depth depends on Locus's response; the interop layer ([RFC-0297](0297-vda5050-outreach.md)/[RFC-0298](0298-inorbit-ros-amr-interop-outreach.md)) is the realistic technical path.

## Alternatives considered

1. **Reverse-engineer the LocusOne surface.** Rejected; brittle and contrary to URML's validator-first posture.
2. **Skip Locus and engage only the interop standards.** Considered; a courtesy touch to the category leader is worthwhile and reinforces the interop-layer RFCs with a named vendor.
3. **Fold Locus into the InOrbit RFC.** Rejected; Locus is a distinct vendor engagement, even though the technical bridge is the shared interop layer.

## Prior art

- locusrobotics.com; MassRobotics AMR Interop Standard participation.
- [RFC-0298 (InOrbit / MassRobotics standard)](0298-inorbit-ros-amr-interop-outreach.md), [RFC-0297 (VDA5050)](0297-vda5050-outreach.md): the interop bridge.
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md), [RFC-0294 (Labrador Systems)](0294-labrador-systems-outreach.md): off-GitHub courtesy precedents.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md).

## Unresolved questions

For Locus Robotics:

1. **Integration surface.** Does Locus expose (or plan) an integration surface, directly or via the MassRobotics standard / VDA5050?
2. **Engagement channel.** Is the company contact form the right surface, or is there a partnerships / dev-relations contact?
3. **Interop participation.** Is the MassRobotics AMR Interop Standard the expected third-party integration path for a Locus fleet?
4. **Natural-language authoring.** Is URML's intent layer of interest to the LocusOne product side?
5. **Anything else.**

## Implementation note

RFC-0300 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

Locus's contact surface is locusrobotics.com. URML's planned channel: a courtesy message via the company contact surface pointing at this RFC. If Locus responds with an integration surface or a specific contact, URML pivots accordingly.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub framing explicit; absence of a developer surface acknowledged honestly (Move #15 closed-surface finding cited).
- [x] Interop layer named as the realistic technical bridge (RFC-0297/0298), not a Locus-private API.
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] Cross-link to RFC-0102/0294 (off-GitHub precedents), interop siblings, fleet machinery.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no developer surface, goods-to-person model, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01 (absence of developer surface documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
