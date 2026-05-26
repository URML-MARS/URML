---
rfc: 0095
title: UCLA AgriCruiser integration, research-collab proposal to agri-cruiser maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0095: UCLA AgriCruiser integration, research-collab proposal to agri-cruiser maintainers

## Summary

URML proposes alignment with the AgriCruiser project via the [`agri-cruiser/agri-cruiser` repo](https://github.com/agri-cruiser/agri-cruiser) (15 stars, GPL-3.0, C++ 100%, 2 open issues, 168 commits). The ask is **research-collab**: a documented mapping between URML's substrate-neutral primitive vocabulary and AgriCruiser's open-source over-the-row navigation platform, with optional coursework integration. No spec change on URML's side. No adapter shipping (license-fit nuance: AgriCruiser is GPL-3.0; URML's `reference/` is Apache-2.0; cross-citation rather than direct adapter code). Fourth Move #7 RFC, first Tier B research-collab in this wave.

## Motivation

AgriCruiser anchors **open-source academic agriculture-rover research** in URML's Move #7 wave. The project is USDA-funded (NIFA grants 2024-67021-42528, 2022-67022-37021, 2021-67022-34200), targets over-the-row navigation (1.42–1.57m adjustable track width), and ships precision-spraying / weed-management demonstrations. It is the closest US-academic counterpart to RFC-0096's INRAE Romea (FR) in the URML outreach landscape.

Verified surface (2026-05-26):
- Single repo `agri-cruiser/agri-cruiser`: 15 stars, **GPL-3.0**, C++ 100%, 168 commits, 2 open issues.
- README acknowledges USDA grants; identifies "UCLA" once in the mechanical-design section regarding in-house fabrication.
- No explicit PI / lab affiliation listed in the repo; engagement-channel question (Issue thread vs. courtesy email) is documented in this RFC's Unresolved questions.

URML's specific value for AgriCruiser:
- **Substrate-neutral coursework artifact.** Students using AgriCruiser for over-the-row navigation experiments could write URML programs in URML's natural-language layer; URML compiles to primitives that an AgriCruiser controller dispatches. The teaching value is the abstraction level above C++ control code.
- **Cross-link to RFC-0096 (INRAE Romea)** + **RFC-0067 (FarmBot)** + **RFC-0092 (Acorn)**: URML's substrate-neutral story across the agriculture vertical lets a research group writing programs for one platform retarget to the others by manifest swap. AgriCruiser's USDA-funded open-source posture is exactly the audience URML's primitive vocabulary serves.

## Detailed design (light, research-collab)

URML proposes:

1. **Documented mapping from URML primitives to AgriCruiser's C++ control surface.** No adapter code shipped in URML's `reference/` (license-fit: AgriCruiser is GPL-3.0; URML's `reference/` is Apache-2.0; cross-citation only). A documented mapping in URML's `reference/agriculture-runtime/README.md` shows how an AgriCruiser deployment would integrate URML at the intent layer.
2. **Coursework integration.** URML primitive vocabulary as a teaching artifact for the UCLA agricultural-engineering audience.
3. **Cross-link to [RFC-0096 (INRAE Romea)](0096-inrae-romea-outreach.md).** US + EU academic ag-rover counterparts; documented note that URML programs are portable between them by manifest swap.
4. **Optional: a future `spec/profiles/agriculture/` co-design.** RFC-0067 raised this as an open question; AgriCruiser's research surface is a candidate input to the future Spec RFC.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 licensing on AgriCruiser.** URML's `reference/` is Apache-2.0. Direct code reuse is not in scope; the integration is documentation and cross-citation, not adapter code. Same license-fit nuance as RFC-0085 (Northwestern MurpheyLab, GPL-3.0).
- **PI / lab affiliation not surfaced from the repo.** The README identifies UCLA once but does not name a PI; URML's RFC documents this and asks the maintainers to confirm.
- **Single-repo footprint.** AgriCruiser is one C++ repo; URML's RFC body keeps the scope narrow (no multi-platform manifest split).
- **Repo cadence.** 168 commits and 2 open issues signal real but small-team development; URML's RFC respects the bandwidth and frames asks lightly.

## Alternatives considered

1. **Ship an `AgriCruiserAdapter` in URML's reference/ directly.** Rejected; license-fit. URML's reference is Apache-2.0; AgriCruiser is GPL-3.0; the documentation-and-cross-citation pattern is the established URML approach for license-asymmetric academic projects (RFC-0085 Northwestern MurpheyLab is the precedent).
2. **Fold AgriCruiser into RFC-0096 (INRAE Romea) as one ag-rover-academic RFC.** Rejected; different countries, different PIs, different funding sources; conflating them obscures both engagements.

## Prior art

- `agri-cruiser/agri-cruiser` GitHub repo (15 stars, GPL-3.0, C++ 100%, 168 commits, 2 open issues).
- USDA NIFA grants 2024-67021-42528, 2022-67022-37021, 2021-67022-34200.
- UCLA fabrication context (mentioned once in the README's mechanical-design section).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Twisted Fields Acorn)](0092-twisted-fields-acorn-outreach.md): agriculture-vertical precedents.
- [RFC-0096 (INRAE Romea)](0096-inrae-romea-outreach.md): parallel EU academic ag-rover RFC in the same Move #7 wave.
- [RFC-0085 (Northwestern MurpheyLab)](0085-northwestern-crb-outreach.md): license-fit precedent (GPL-3.0 academic, URML Apache-2.0, cross-citation only).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For the AgriCruiser maintainers:

1. **PI / lab affiliation.** Could you confirm the lab + PI behind `agri-cruiser/agri-cruiser`? UCLA agricultural-engineering or a different department?
2. **License-fit posture.** AgriCruiser is GPL-3.0; URML's `reference/` is Apache-2.0. Cross-citation is URML's proposal. Any concerns?
3. **Coursework integration.** Is AgriCruiser used in any specific UCLA course (or other institution) where URML primitive vocabulary would be a useful teaching artifact?
4. **Agriculture-profile co-design.** RFC-0067 raised the future `spec/profiles/agriculture/` question (plant / water / weed / scout Layer-3). Interest in coordinating?
5. **Conformance lane.** Open to a URML conformance line on `agri-cruiser/agri-cruiser` README?
6. **Anything else.**

## Implementation note

RFC-0095 ships as a single RFC document PR. No code in this PR. Research-collab framing; no adapter in URML's `reference/` due to GPL-3.0 vs Apache-2.0 license-fit. Fourth Move #7 RFC. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`agri-cruiser/agri-cruiser` has Issues enabled (2 open at outreach time; verified 2026-05-26). URML's planned channel: open a single Issue on `agri-cruiser/agri-cruiser` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] License-fit GPL-3.0 vs Apache-2.0 surfaced honestly.
- [x] PI / lab affiliation gap acknowledged.
- [x] Cross-link to RFC-0067 + RFC-0092 + RFC-0096 + RFC-0085 (license-fit precedent) explicit.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, GPL licensing, PI not surfaced, single-repo, cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
