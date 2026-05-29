---
rfc: 0219
title: IEEE P1872.2 Autonomous Robotics Ontology (AuR) cross-citation, request for comment from IEEE-RAS Standing Committee for Standards
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

# RFC-0219: IEEE P1872.2 AuR ontology cross-citation

## Summary

URML's Layer-2 primitives + Layer-3 behavior composition vocabulary maps cleanly onto the IEEE 1872 ontology family (1872-2015 Core Ontology for Robotics + Automation; P1872.2 Autonomous Robotics Ontology extension; P1872.3 multi-robot reasoning). This RFC documents URML's proposed cross-citation with the IEEE P1872.2 Working Group, engaged via the IEEE-SA Working Group portal at [sagroups.ieee.org/1872-2](https://sagroups.ieee.org/1872-2/) and the [IEEE-RAS Standing Committee for Standards](https://sagroups.ieee.org/ras-sc/), and **requests review and feedback from the IEEE P1872.2 Working Group**. No spec change.

## Motivation

URML's vocabulary (`move_to`, `dock`, `pick_from`, `place_at`, `grasp`, `release`, `swap_tool`, `scan_area`, `query_detection`, etc.) is informally aligned with the IEEE 1872 ontology family but not formally cross-mapped. Formal cross-citation lets URML compose against IEEE 1872 / AuR / multi-robot reasoning vocabulary as related-art rather than parallel-but-disconnected reinvention.

P1872.2 has 80+ active members across NA/SA/EU/Asia/Africa; sister WG P1872.3 (multi-robot reasoning) is also active. IEEE-RAS Standing Committee for Standards oversees both. URML's robotics-intent-language framing is precisely the consumer-of-ontology shape IEEE 1872's authors had in mind.

URML benefits from documenting the engagement because:

1. **Vocabulary cross-mapping.** URML's primitive set + behavior composition vocabulary cross-maps to IEEE 1872 ontology terms; explicit citation lets downstream URML adopters reference the IEEE ontology directly.
2. **Standards-academic cross-citation.** IEEE 1872 / AuR is academically + standards-side recognized robotics ontology. URML's cross-citation strengthens URML's standards-track narrative.
3. **Future multi-robot extension.** URML's multi-robot direction ([RFC-0006](0006-multi-robot.md)) will benefit from formal cross-mapping with IEEE P1872.3 multi-robot reasoning ontology.

## Detailed design

### URML v0.1 cross-citation proposal

| URML surface | Maps to / cross-cites IEEE 1872 / AuR |
|---|---|
| Layer-2 primitives | Cross-mapping with IEEE 1872 Core Ontology terms (Agent / Action / Task / Capability) |
| Layer-3 behavior composition | Cross-mapping with P1872.2 AuR autonomous-action vocabulary |
| Layer-1 HAL capability manifest | Cross-mapping with IEEE 1872 Capability concept |
| Future multi-robot manifest ([RFC-0006](0006-multi-robot.md)) | Cross-mapping with P1872.3 multi-robot reasoning ontology |
| `safety_envelope` manifest field | Cross-mapping with IEEE 1872 constraints / safety vocabulary |

### What URML proposes (not a spec change)

This RFC does not propose a URML spec change. It proposes:

1. **Cross-citation in URML spec docs** — URML's Layer-2 and Layer-3 spec documentation references IEEE 1872 / P1872.2 / P1872.3 vocabulary mapping.
2. **WG cross-attendance.** URML maintainer signs up on sagroups.ieee.org/1872-2 to monitor WG progress and contribute cross-mapping observations.
3. **Future Spec RFC for explicit ontology mapping.** Out of scope here; surfaces the requirement for a follow-up Spec RFC (URML primitive → IEEE 1872 term cross-reference table).

### Compatibility notes

- **Engagement surface.** [sagroups.ieee.org/1872-2](https://sagroups.ieee.org/1872-2/) — IEEE-SA Working Group portal. Standing Committee oversight via [sagroups.ieee.org/ras-sc](https://sagroups.ieee.org/ras-sc/).
- **Governance.** IEEE-SA (Standards Association); P1872.2 + P1872.3 under IEEE-RAS (Robotics and Automation Society) standing committee.
- **Origin.** IEEE-SA US-domiciled; 80+ international members.
- **License fit.** IEEE 1872 / P1872.2 / P1872.3 are IEEE standards (purchase-licensed). URML's cross-citation does not embed the standard text; it cross-references vocabulary terms. Clean fit.
- **Maintainer signal.** Active WG; sister WG P1872.3 also active; IEEE-RAS Standing Committee oversight.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** Future Spec RFC for explicit ontology mapping table is queued.
- Reference runtime: future docs may reference IEEE 1872 vocabulary terms alongside URML primitives. No code change.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **IEEE standards are purchase-licensed.** URML cannot embed IEEE 1872 text in Apache-2.0 docs; cross-citation works at the term-mapping level only.
- **Ontology-mapping discipline.** Formal mapping requires sustained academic-engagement effort URML may not have bandwidth for at Phase 1. Mapping table itself is future work.
- **Standards-body classical channel.** IEEE-SA participation typically expects member-organization affiliation; URML is single-maintainer Phase-1. WG cross-attendance may be open but voting / contribution rights may not be.

## Alternatives considered

1. **Skip ontology cross-citation; rely on URML's own vocabulary.** Rejected. IEEE 1872 / AuR is the standards-side recognized robotics ontology; ignoring it leaves URML's standards-track narrative parallel-but-disconnected.
2. **Engage IEEE 1872 (parent) rather than P1872.2 (AuR extension).** Considered. P1872.2 is the active extension WG; engaging there reaches the active maintainer group and indirectly the parent. P1872.3 multi-robot reasoning is also active; future Move-17 follow-up could engage P1872.3 separately.
3. **Engage IEEE-RAS Standing Committee directly rather than the WG.** Considered. The Standing Committee oversees the WGs; engaging the WG first preserves the maintainer-direct framing.
4. **Wait for URML v1.0 before engaging IEEE.** Rejected. Cross-citation can happen before v1.0; mapping refinement is exactly the kind of work the WG would help with.

## Prior art

- [IEEE P1872.2 Working Group home](https://sagroups.ieee.org/1872-2/) — the WG engagement anchor.
- [IEEE P1872.3 Ontology Reasoning for Multiple Autonomous Robots](https://www.ieee-ras.org/industry-government/standards/active-projects/p1872-3-ontology-reasoning-for-multiple-autonomous-robots) — sister WG.
- [IEEE-RAS Standing Committee for Standards](https://sagroups.ieee.org/ras-sc/).
- IEEE 1872-2015 Core Ontology for Robotics and Automation — the parent standard.
- URML Layer-2 + Layer-3 spec docs (in `spec/` directory).
- [RFC-0006 (multi-robot)](0006-multi-robot.md) — URML's multi-robot direction; relevant for future P1872.3 cross-mapping.

## Unresolved questions

For the IEEE P1872.2 Working Group + IEEE-RAS Standing Committee:

1. **Cross-mapping format preference.** What's the preferred format for URML primitive → IEEE 1872 / P1872.2 vocabulary mapping? Inline citation in URML spec docs, separate cross-reference table, or both?
2. **P1872.2 vs P1872.3 split.** URML's current scope is single-robot; multi-robot is RFC-0006 future work. Should cross-citation be split — P1872.2 for single-robot, P1872.3 for multi-robot — or treated together?
3. **WG participation.** Are non-member observers welcome at P1872.2 WG calls? URML maintainer would benefit from monitoring WG progress.
4. **Ontology mapping work.** Is there interest in jointly scoping a URML-to-IEEE-1872 mapping table as collaborative work, or should URML draft a proposal independently and submit for WG review?
5. **IEEE-RAS standing committee context.** Are there parallel IEEE-RAS standards efforts URML should be aware of beyond P1872.2 / P1872.3?
6. **Conformance listing.** Would IEEE-RAS / P1872.2 consider a working-group page link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once cross-citation stabilizes?
7. **IEEE membership orientation.** What IEEE-SA membership tier (individual / corporate / standards-association) is realistic for a Phase-1 single-maintainer project? Is this a Phase-2 consideration?
8. **Anything else.**

## Implementation note

RFC-0219 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move17.yaml`](../../examples/lighthouses/outreach-move17.yaml).

## How to respond

Engagement channel: IEEE-SA WG sign-up at [sagroups.ieee.org/1872-2](https://sagroups.ieee.org/1872-2/) + email to IEEE-RAS Standing Committee for Standards. Founder-action sending under maintainer identity. Draft artifact in [`examples/lighthouses/founder-actions-move17.md`](../../examples/lighthouses/founder-actions-move17.md).

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (P1872.2 WG active; 80+ members; P1872.3 sister WG also active).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (IEEE standards purchase-licensed, ontology-mapping discipline, IEEE-SA member-organization expectation).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: IEEE-SA US-domiciled; international WG membership; default policy passes.
- [x] CLAUDE.md compliance check passed — standards-track cross-citation is documented direction.
