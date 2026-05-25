---
rfc: 0091
title: QUT Centre for Robotics integration, research-collab proposal to Peter Corke
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

# RFC-0091: QUT Centre for Robotics integration, research-collab proposal to Peter Corke

## Summary

URML proposes alignment with the Queensland University of Technology Centre for Robotics via Prof. Peter Corke's [personal GitHub `petercorke`](https://github.com/petercorke) (48 public repos, 2.1k followers). The ask is **research-collab** anchored on the Peter Corke Robotics Toolbox lineage (MATLAB → Python → ROS 2) and on QUT's role as the de facto Australian ROS 2 teaching hub. No spec change on URML's side. Twelfth and final Move #6 RFC.

## Motivation

Peter Corke's *Robotics Toolbox* has been the global standard educational robotics codebase for over a decade. The MATLAB version was foundational; the Python version (`robotics-toolbox-python`) is now the standard reference in undergraduate / graduate robotics teaching globally. QUT's AuSRoS 2025 hands-on ROS 2 labs and Australia's ARC Centre of Excellence in Robotic Vision (chaired by Corke) make QUT the institutional Australian robotics hub.

Verified surface (2026-05-25):
- `petercorke` personal GitHub: 48 public repos, 2.1k followers.
- Top-starred: `robotics-toolbox-python` (3.1k stars, the canonical Python robotics teaching library), `RVC3-python` (634 stars, "Robotics, Vision and Control" 3rd edition Python companion), `spatialmath-python` (627 stars, under `bdaiinstitute` / `rai-opensource` org), `bdsim` (253 stars, block diagram simulation), `machinevision-toolbox-python` (201 stars).
- Profile location: Brisbane, Australia; personal website: `petercorke.com`.
- The QUT Centre for Robotics has institutional standing; the verified GitHub presence is via Peter Corke's personal handle, not a separate `qut-asl` or `qcr-bot` org URML could identify during verification.

URML's specific value for QUT / Peter Corke's work:
- **`robotics-toolbox-python` is the global teaching standard.** URML primitive vocabulary as a complementary teaching surface above the kinematics + dynamics math the Toolbox teaches. A documented chapter or appendix cross-link in *Robotics, Vision and Control 3* (RVC3) is the most distribution URML could plausibly receive from a single integration.
- **AuSRoS 2025 ROS 2 labs cross-link.** Australia's annual ROS-orientation workshop; URML primitive vocabulary as a candidate teaching module.
- **Centre for Robotics ARC Centre of Excellence status.** QUT's institutional reach across Australian universities is enormous; a documented URML mention in the Centre's outreach materials reaches a multi-institution audience.

Distinction worth flagging: this RFC targets Peter Corke's personal GitHub plus the QUT Centre for Robotics institutional surface. URML's verification did not find separate `qut-asl` or `qcr-bot` orgs; the engagement surface is Peter Corke's personal handle plus the Centre's `qut.edu.au/research/centre-for-robotics` website.

## Detailed design (light, research-collab)

URML proposes:

1. **`robotics-toolbox-python` cross-link.** A documented note in URML's `reference/llm-bridge/` or `reference/cobot-runtime/` README cross-citing the Toolbox as the canonical academic kinematics-dynamics layer URML primitives compose above. Vice versa, the Toolbox is invited to mention URML.
2. **RVC3 chapter / appendix discussion (speculative).** *Robotics, Vision and Control 3* (the book) is the global standard textbook. URML asks honestly whether a future edition or workshop would consider a URML primitive-vocabulary appendix or worked example. Speculative; URML expects this is below the base case but documents the ask.
3. **AuSRoS 2025+ teaching integration.** URML primitive vocabulary as a candidate teaching module in QUT's annual ROS 2 lab series.
4. **Centre for Robotics outreach materials.** Optional URML mention in the ARC Centre's outreach materials (Centre leadership decides; speculative).

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **Personal handle vs institutional org.** URML's engagement is via Peter Corke's personal GitHub (`petercorke/robotics-toolbox-python`), not a standalone QUT lab org. The cross-institutional reach depends on Corke's personal bandwidth.
- **Textbook outreach is speculative.** RVC3 is established and stable; URML cannot plausibly expect a major edition revision for a young open-source spec.
- **Australian academic-calendar cadence.** Australian academic year runs February-November; the wait window may extend across the summer break (Dec-Feb) for substantive engagement.

## Alternatives considered

1. **Ship a `RoboticsToolboxAdapter`.** Rejected. The Toolbox is a kinematics-dynamics library, not a substrate URML targets. Composition, not adapter.
2. **Target Centre for Robotics institutional surface only, not Peter Corke personally.** Rejected. The QUT Centre's public engagement surface is mostly via Corke's personal handle plus the Centre's website; targeting only the institutional level forfeits the Toolbox cross-link.
3. **Skip QUT entirely; treat Peter Corke as a personal-handle target only.** Rejected. The institutional reach of the ARC Centre of Excellence makes QUT the right framing.

## Prior art

- `petercorke` personal GitHub (48 public repos, 2.1k followers, Brisbane).
- `petercorke/robotics-toolbox-python` (3.1k stars), `RVC3-python` (634 stars), `spatialmath-python` (627 stars, under `rai-opensource` / `bdaiinstitute` org), `bdsim` (253 stars), `machinevision-toolbox-python` (201 stars).
- *Robotics, Vision and Control 3* (Corke + Park, the global standard textbook).
- QUT Centre for Robotics website: `qut.edu.au/research/centre-for-robotics`.
- AuSRoS 2025 (Australian Symposium on Robotics, hands-on ROS 2 labs).
- ARC Centre of Excellence in Robotic Vision (Corke chaired).
- [RFC-0011](0011-educational-profile.md): URML educational profile.

## Unresolved questions

For Prof. Corke + QUT Centre for Robotics team:

1. **`robotics-toolbox-python` cross-link.** Is documented cross-citation in `reference/llm-bridge/` or `cobot-runtime/` README welcome (vice versa, would the Toolbox mention URML)?
2. **RVC3 chapter / appendix (speculative).** Would a future edition or workshop of *Robotics, Vision and Control* consider URML primitive-vocabulary content?
3. **AuSRoS 2025+ teaching integration.** Is URML primitive vocabulary a candidate teaching module in QUT's annual ROS 2 labs?
4. **Centre for Robotics outreach materials.** Is URML mention in ARC Centre outreach welcome (where Centre leadership decides)?
5. **Personal handle vs institutional org.** Is `petercorke/*` the right URML engagement surface, or is there a separate Centre-level GitHub or institutional channel URML should use?
6. **Conformance lane.** Open to a URML conformance line on `robotics-toolbox-python` README or `qut.edu.au/research/centre-for-robotics`?
7. **Anything else.**

## Implementation note

RFC-0091 ships as a single RFC document PR. No code in this PR. Research-collab framing. Twelfth and final Move #6 RFC; closes the wave. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`petercorke/robotics-toolbox-python` is the highest-visibility repo at 3.1k stars (verified 2026-05-25). URML's planned channel: open a single Issue on `petercorke/robotics-toolbox-python` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Corke via `petercorke.com` or the QUT Centre's contact page.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Personal-handle vs institutional-org honesty surfaced.
- [x] RVC3 chapter ask documented as speculative.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, personal handle dependency, speculative textbook ask, Australian academic cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: AU`; default policy passes.
- [x] CLAUDE.md compliance check passed.
