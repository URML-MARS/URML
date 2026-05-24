---
rfc: 0079
title: Open Bionics integration, research-collab proposal to OpenBionics maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-24
updated: 2026-05-24
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

# RFC-0079: Open Bionics integration, research-collab proposal to OpenBionics maintainers (academic) + courtesy outreach to Open Bionics Ltd (commercial)

## Summary

URML does not yet ship a prosthetics integration. This RFC proposes alignment with two distinct surfaces sharing the "Open Bionics" name and an accessibility identity:

1. The academic [`OpenBionics`](https://github.com/OpenBionics) GitHub org (`Prosthetic-Hands`, `Robot-Hands`, `Anthropomorphic-Robot-Hands`, `Body-Powered-Exoskeleton-Glove`. Research-grade open prosthetic-hand designs from the University of Bristol / academic collaborators; **org appears dormant**, last commits in 2018–2020).
2. **Open Bionics Ltd** (commercial UK company, Hero Arm myoelectric prosthetic) via their public-facing channels. No GitHub Issue surface to file against.

This RFC is a **research-collab + courtesy** proposal: substantive engagement against the academic org's published designs as a future URML reference manifest source, plus a courtesy notice to the commercial entity that URML's accessibility identity story exists. No spec change on URML's side. No code change in this PR. **This RFC is honest about the dormancy** of the academic org and the gap between the academic and commercial entities.

This is the ninth and final Move #5 RFC. It anchors URML's **accessibility identity** but does so without overclaiming.

## Motivation

URML's outreach landscape across Moves #1–#4 has covered industrial, AI/ML, affordable / educational, and adjacent-niche verticals. Accessibility (prosthetics, exoskeletons, assistive robotics) has been deliberately uncovered. The argument for engaging now: URML's natural-language layer is a meaningful accessibility primitive. "open my hand" becomes an English sentence the prosthetic listens to, with static validation between the sentence and the actuator command. The argument for staying modest: prosthetics are medical devices in most jurisdictions, with regulatory surfaces URML has no authority over.

The right Move #5 frame is **research-collab on the academic open-prosthetic-hand designs**, with a **courtesy notice** to the commercial Open Bionics Ltd. The academic surface has published designs (most-starred: `Prosthetic-Hands` at 176 stars, `Robot-Hands` at 132 stars) that URML can document as future reference manifests for a research-grade open-prosthetic adapter. The commercial Open Bionics Ltd has no public GitHub Issue surface; the courtesy outreach is best-effort via their general contact channels.

Three things make this RFC concrete despite the dormancy and the academic / commercial split. First, the academic OpenBionics GitHub org genuinely exists at github.com/OpenBionics with 4 public repos and 161 followers (verified 2026-05-24); the designs are real and citation-worthy even if the maintainer cadence is slow. Second, the prosthetics community has documented interest in open-source designs going back over a decade; URML's adapter pattern would let an academic researcher experimenting with the OpenBionics Prosthetic-Hand designs use the same English-to-program layer as URML's other targets. Third, the Open Bionics Ltd commercial entity is the most-visible UK prosthetic-arm vendor and their public posture (Hero Arm marketing, partnerships with NHS / national health systems) suggests they would welcome attention even if they cannot engage on a GitHub Issue surface.

URML's open-core commitment lands cleanly on the academic side. The commercial Open Bionics Ltd is **not** the target for a URML adapter at this stage; the courtesy outreach is institutional acknowledgement, not partnership announcement.

## Detailed design

### Two-surface engagement

This RFC's outreach is split:

**A. Academic OpenBionics GitHub org** (substantive):
- URML proposes documenting the Prosthetic-Hand and Robot-Hand designs as reference geometries for a future open-prosthetic research adapter.
- Ask the academic maintainers (if reachable given the dormancy) about: current status of the project, recommended canonical CAD / firmware files, citation form for URML's future reference manifest.

**B. Open Bionics Ltd (commercial)** (courtesy):
- URML's accessibility identity story exists; URML would welcome a conversation if the company is open to it.
- No specific ask. No adapter proposal against the commercial Hero Arm hardware. Just a documented "URML is aware of your work and our accessibility identity overlap" notice via their public-facing contact channels (URML founder's responsibility to choose the surface).

### Proposed `OpenProstheticHandAdapter` (forward-declared, not shipping)

```
reference/prosthetic-runtime/src/prosthetic_runtime/open_bionics_academic/
├── __init__.py
├── adapter.py             # OpenProstheticHandAdapter (forward-declared)
└── manifests/
    ├── openbionics_prosthetic_hand_v1_reference.yaml
    └── openbionics_robot_hand_v1_reference.yaml
```

The `_reference` suffix is intentional: the manifests are research-reference geometries, not production deployment targets. The adapter ships only if the academic-side engagement signals interest in URML's involvement.

### URML accessibility identity placement

This RFC documents that URML's strategic posture welcomes accessibility deployments without making accessibility a profile-spec commitment. A future spec RFC (Move #6+) could create `spec/profiles/accessibility/` if multiple accessibility-adjacent adapters ship. RFC-0079 does not pre-commit to that profile.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed forward-declared `reference/prosthetic-runtime/` (placement open; could also live under educational or research runtime). Not built in this PR.
- Conformance suite: deferred until adapter ships.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero changes today.

## Drawbacks

- **Academic OpenBionics org is dormant.** Last commits 2018–2020. The academic surface may not respond to outreach, in which case URML's engagement falls through.
- **Open Bionics Ltd (commercial) has no GitHub Issue surface.** The courtesy outreach is best-effort via web contact forms or LinkedIn; not the URML-standard public-thread engagement.
- **Two entities sharing the "Open Bionics" name is genuinely confusing.** URML's RFC has to disambiguate clearly to avoid being read as a partnership announcement with the commercial entity.
- **Medical-device regulatory surface is out of URML's authority.** A URML adapter against a research-grade prosthetic-hand design has no regulatory standing for clinical deployment; the RFC documents this explicitly.
- **Lightest engagement payload in Move #5.** No new adapter ships; no new manifest ships. This is a "URML's accessibility identity exists" placeholder more than an active engagement.

## Alternatives considered

1. **Skip accessibility entirely.** Rejected. URML's strategic posture benefits from a documented accessibility identity even without an active adapter.
2. **Ship a real adapter against the academic designs.** Rejected. The academic maintainer cadence is too slow for confident adapter authoring; the designs are research-stage, not deployment-stage.
3. **Frame as a Tier A vendor RFC against Open Bionics Ltd.** Rejected. Open Bionics Ltd has no GitHub Issue surface, no documented developer SDK, and is a regulated medical-device vendor; treating them as a Tier A vendor RFC would overclaim.
4. **Defer to a dedicated Move #6 accessibility wave with proper research.** Considered seriously. Deferred for now because the user explicitly promoted the parked Tier 2 list for Move #5; deferring would underdeliver. A future Move #6 can still be a vertical-specific accessibility frame once concrete additional candidates (Atom Limbs, Ottobock open-API partners, exoskeleton vendors) are surfaced.

## Prior art

- `OpenBionics` GitHub org (4 public repos, 161 followers): `Prosthetic-Hands` (176 stars, TeX, 2018-02), `Robot-Hands` (132 stars, Eagle, 2015), `Anthropomorphic-Robot-Hands` (61 stars, MATLAB, 2020), `Body-Powered-Exoskeleton-Glove` (40 stars, 2019).
- Open Bionics Ltd (commercial UK; Hero Arm; openbionics.com).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to the forward-declared adapter.
- [RFC-0070 (HEBI)](0070-hebi-robotics-outreach.md): the per-customer-geometry research-adapter pattern.

## Unresolved questions

For the **academic `OpenBionics` maintainers** (if reachable given dormancy):

1. **Project status.** Is the academic OpenBionics project active, in maintenance, or fully archived?
2. **Canonical files.** Which repos / files are the canonical reference for a research adapter?
3. **Citation form.** How should URML cite the project in any future reference-manifest documentation?
4. **Engagement willingness.** Is there interest in a documented URML cross-reference?

For **Open Bionics Ltd (commercial)** (via courtesy outreach surface):

5. **Conversation interest.** Is the company open to a future conversation about URML's accessibility identity overlap?

General:

6. **Future accessibility profile.** Should URML's roadmap explicitly include a Move #6 accessibility-themed wave with proper research?
7. **Anything else.**

## Implementation note

RFC-0079 ships as a single RFC document PR. No adapter code in this PR. Honest about the dormancy of the academic surface and the GitHub-issue-less commercial surface. Research-collab framing. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback

From academic `OpenBionics` maintainers: items 1–4 above.
From Open Bionics Ltd commercial: item 5 above (low expectation of immediate reply).
General: items 6–7.

## How to respond

`OpenBionics` GitHub org has 4 public repos (verified 2026-05-24). The most-starred `Prosthetic-Hands` repo (176 stars) has its last commit in February 2018; the org appears dormant. URML's planned channels:

- **Academic surface:** open a single Issue on `OpenBionics/Prosthetic-Hands` labelled with the closest `question` equivalent, pointing to this RFC. Acknowledge the dormancy and ask for any maintainer redirect.
- **Commercial surface:** founder to choose between `info@openbionics.com`, LinkedIn outreach to Open Bionics Ltd's product team, or the company's public contact form. URML records this as a courtesy notice rather than a substantive ask.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Two-surface engagement framed honestly (academic substantive, commercial courtesy).
- [x] Academic org's dormancy disclosed directly.
- [x] No partnership claim against Open Bionics Ltd commercial.
- [x] Research-collab framing.
- [x] At least one alternative considered (four, with the deferred-Move-6 option documented as seriously considered).
- [x] Drawbacks real (dormancy, no GitHub Issue surface for commercial, naming collision, regulatory surface out of scope, lightest engagement payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] No `spec/profiles/accessibility/` commitment.
- [x] Implementation note explicit.
- [x] Surface ("How to respond") verified against `OpenBionics` org as of 2026-05-24 with honest dormancy note.
- [x] CLAUDE.md compliance check passed; no medical-device regulatory overclaim.
