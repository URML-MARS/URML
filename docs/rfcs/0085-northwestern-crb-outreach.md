---
rfc: 0085
title: Northwestern CRB integration, research-collab proposal to Todd Murphey, Ed Colgate, Kevin Lynch
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-25
updated: 2026-05-25
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

# RFC-0085: Northwestern Center for Robotics and Biosystems (CRB) integration, research-collab proposal

## Summary

URML proposes alignment with the Northwestern Center for Robotics and Biosystems (CRB), via the [`MurpheyLab` GitHub org](https://github.com/MurpheyLab) (44 public repos, 62 followers; led by Prof. Todd Murphey) and the broader CRB faculty (Prof. Ed Colgate, Prof. Kevin Lynch). The ask is **research-collab** anchored on CRB's dexterous-manipulation focus and the NSF HAND Engineering Research Center ($52M, 10-year funding). No spec change on URML's side. Sixth Move #6 RFC.

## Motivation

Northwestern CRB anchors **dexterous manipulation across medical, soft, and industrial robotics** at URML's Move #6 wave. CRB's research breadth (Murphey's ergodic / information-theoretic control, Colgate's haptics and cobotics, Lynch's classical robotics textbook authorship) plus the HAND ERC's $52M / 10-year scale make it the largest-budget academic-research target in this Move.

Verified surface (2026-05-25):
- `MurpheyLab`: 44 public repos, 62 followers.
- Top-starred: `MaxDiffRL` (84 stars, Jupyter Notebook), `ergodic-control-sandbox` (53 stars, "T-RO, ICRA 2024"), `lqr-flow-matching` (53 stars, "RSS 2025"), `brne` (38 stars, IJRR publication), `DPGO` (34 stars, distributed pose graph optimization).
- License pattern: **GPL-3.0 predominant** (note: copyleft; URML's `reference/` is Apache-2.0, so direct code reuse would require careful license analysis. The URML adapter would not consume MurpheyLab code directly. The integration is documentation and cross-citation).
- CRB website: `robotics.northwestern.edu`.
- ME 495 (Robotics) is the lab-affiliated course.
- HAND ERC ($52M / 10y) is the institutional context.

URML's specific value for Northwestern CRB:
- **Ergodic control + URML primitive composition.** Murphey's ergodic-control work generates exploration policies. URML's `measure` primitive plus `wait_for(threshold)` plus the LLM-bridge are the user-facing layer above ergodic-policy execution.
- **HAND ERC scale.** A documented mention of URML in the HAND ERC's developer-outreach materials (if the ERC's communications team is interested) reaches a multi-institution audience URML cannot reach directly.
- **Kevin Lynch's textbook lineage.** Lynch's *Modern Robotics: Mechanics, Planning, and Control* is the standard textbook in many global robotics courses; an adopted URML chapter or appendix would be enormous distribution. Speculative ask, not a base case.

## Detailed design (light, research-collab)

URML proposes:

1. **Cross-citation in `ergodic-control-sandbox` or `MaxDiffRL` README.** A documented note that URML emits primitives at the intent layer; MurpheyLab repos consume those primitives for ergodic-policy execution.
2. **ME 495 coursework integration.** URML primitive vocabulary as a teaching artifact in Northwestern's graduate robotics course.
3. **HAND ERC outreach materials.** Optional URML mention in ERC developer-outreach (a courtesy ask, contingent on ERC-leadership receptivity).
4. **Lynch textbook outreach.** A speculative ask: would *Modern Robotics* (Lynch, Park) consider a URML appendix or worked example in a future edition? URML expects this is far below the base case but documents the ask honestly.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 licensing on MurpheyLab repos.** URML's `reference/` is Apache-2.0. Direct code reuse is not in scope; URML's integration with MurpheyLab work is documentation and cross-citation, not adapter code.
- **HAND ERC is a $52M multi-institution program.** PI attention is allocated against institutional partners; URML's RFC competes with substantial commitments.
- **Textbook outreach is speculative.** Lynch's textbook is established and stable; URML cannot plausibly expect a major edition revision for a young open-source spec.

## Alternatives considered

1. **Ship an adapter against MurpheyLab repos.** Rejected. License-incompatibility risk + research-stage code.
2. **Target Colgate or Lynch individually instead of Murphey.** Rejected. The three faculty plus the HAND ERC are best engaged as one institutional surface; the RFC's framing is CRB-level.

## Prior art

- `MurpheyLab` GitHub org (44 public repos, 62 followers, GPL-3.0 predominant).
- `MurpheyLab/MaxDiffRL` (84 stars), `ergodic-control-sandbox` (53 stars, T-RO + ICRA 2024), `lqr-flow-matching` (53 stars, RSS 2025), `brne` (38 stars, IJRR), `DPGO` (34 stars).
- Northwestern CRB website: `robotics.northwestern.edu`.
- HAND Engineering Research Center ($52M / 10 years, NSF-funded).
- Lynch & Park, *Modern Robotics: Mechanics, Planning, and Control* (the global standard textbook).
- ME 495 course page.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md), [RFC-0013](0013-industrial-layer2-primitives.md): URML profiles and industrial primitives.

## Unresolved questions

For Prof. Murphey + Prof. Colgate + Prof. Lynch + CRB team:

1. **Ergodic-control + URML composition.** Is documenting URML's `measure` plus `wait_for` plus LLM-bridge composition with ergodic-policy execution useful?
2. **Coursework integration.** Is ME 495 a candidate for URML primitive vocabulary?
3. **HAND ERC outreach.** Is there interest in mentioning URML in HAND ERC developer-outreach materials (where ERC leadership decides)?
4. **License-fit.** GPL-3.0 on MurpheyLab vs Apache-2.0 on URML. Any cross-citation arrangements URML should be aware of?
5. **Lynch textbook.** A speculative ask: would *Modern Robotics* consider a URML appendix or worked example in a future edition?
6. **Conformance lane.** Open to a URML conformance line on `ergodic-control-sandbox` README or `robotics.northwestern.edu`?
7. **Anything else.**

## Implementation note

RFC-0085 ships as a single RFC document PR. No code in this PR. Research-collab framing. Sixth Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`MurpheyLab/MaxDiffRL` is the most-starred repo (84 stars; verified 2026-05-25). URML's planned channel: open a single Issue on `MurpheyLab/MaxDiffRL` or `MurpheyLab/ergodic-control-sandbox` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Murphey + Prof. Lynch via `robotics.northwestern.edu`. HAND ERC outreach goes through ERC leadership separately.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] License-fit GPL-3.0 vs Apache-2.0 surfaced honestly.
- [x] HAND ERC scale and Lynch textbook framing kept proportional (speculative asks documented as such).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, GPL licensing, HAND ERC PI attention, textbook speculation).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
