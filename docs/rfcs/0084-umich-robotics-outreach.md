---
rfc: 0084
title: UMich Robotics integration, research-collab proposal to Maani Ghaffari + Jessy Grizzle
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

# RFC-0084: UMich Robotics integration, research-collab proposal to Maani Ghaffari + Jessy Grizzle

## Summary

URML proposes alignment with the University of Michigan Robotics Department via the [`UMich-CURLY` GitHub org](https://github.com/UMich-CURLY) (Computational Autonomy and Robotics Laboratory, 78 public repos, 197 followers; led by Prof. Maani Ghaffari) plus the broader UMich Robotics Department curriculum (ROB 101 / ROB 102 / ROB 401, championed by Prof. Jessy Grizzle and the department leadership). The ask is **research-collab plus the strongest coursework-integration opportunity in Move #6**: UMich Robotics is the only university in this wave with a dedicated undergraduate robotics degree program built from the ground up since 2023. No spec change on URML's side. Fifth Move #6 RFC.

## Motivation

UMich Robotics is the **most teaching-pipeline-ready URML target in Move #6**. The department launched ROB 101 (Computational Linear Algebra for Robotics) and ROB 102 (Intro to AI and Programming for Robotics) as part of a new undergraduate robotics major in 2023. The curriculum is robot-agnostic by design. Exactly the audience URML's substrate-neutral primitive vocabulary serves.

Verified surface (2026-05-25):
- `UMich-CURLY`: 78 public repos, 197 followers. Top-starred: `drift` (176 stars, "Dead Reckoning In Field Time: Symmetry-Preserving State Estimation Library", C++), `Debias_IMU` (122 stars), `deep-contact-estimator` (113 stars, contact estimation for quadruped robots), `3DMapping` (92 stars), `unified_cvo` (81 stars, GPU point-cloud registration).
- License pattern: BSD-3-Clause + MIT.
- Department website: `robotics.umich.edu`.
- ROB 101 and ROB 102 are the foundational undergraduate courses; ROB 401 is autonomous vehicles.
- Jessy Grizzle's bipedal-locomotion research (Cassie / Digit) plus Maani Ghaffari's perception research are the lab's flagship surfaces.

URML's specific value for UMich Robotics:
- **ROB 101 / ROB 102 coursework integration.** Robot-agnostic undergrad robotics curriculum is exactly where URML's primitive vocabulary belongs. A documented lecture module on substrate-neutral programming is a one-semester pilot.
- **CURLY + URML composition.** CURLY's perception and state-estimation libraries (`drift`, `unified_cvo`, `3DMapping`) sit below URML's intent layer. URML's `measure` primitive can dispatch to CURLY's published state-estimation outputs.
- **Bipedal-locomotion cross-link.** Grizzle's Cassie / Digit work is a research-grade complement to URML's existing [RFC-0009 (legged-humanoid mobility)](0009-legged-humanoid-mobility.md) capability schema. URML's Move #4 already touched the Cassie audience via [RFC-0050 (Isaac Lab)](0050-nvidia-isaac-lab-integration.md), but UMich's research-side surface is distinct.

## Detailed design (light, research-collab)

URML proposes:

1. **ROB 101 / ROB 102 coursework module.** A single lecture + lab on URML's primitive vocabulary, taught with URML's existing `examples/` directory. UMich faculty own the pedagogy.
2. **CURLY + URML composition.** Documented note that URML's `measure` primitive can consume CURLY's state-estimation outputs (`drift`, `3DMapping`, `unified_cvo`). The cross-link is documentation, not code.
3. **Bipedal-locomotion research cross-link to [RFC-0009](0009-legged-humanoid-mobility.md).** Cassie / Digit URDFs as candidate URML manifest reference geometries. Optional cross-coordination with URML's open [RFC-0050 (NVIDIA Isaac Lab)](0050-nvidia-isaac-lab-integration.md) outreach since UMich Robotics frequently publishes against Isaac.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **CURLY is one lab in a multi-lab department.** URML's RFC targets CURLY's GitHub surface plus the department-level curriculum, but other UMich robotics labs (e.g., Dawn Tilbury's automation lab, ROAHM lab) are not covered by this RFC; future Move #7 candidates if signal warrants.
- **Coursework integration depends on department-level decisions.** URML cannot influence ROB 101 / 102 curriculum directly; the department leadership decides.
- **Academic-calendar cadence.** Summer break (June through August at UMich) means the 14-day wait window URML uses for vendor RFCs will likely extend; a polite follow-up at +30d is realistic.

## Alternatives considered

1. **Ship the adapter first.** Rejected. URML does not need a "CURLYAdapter". CURLY's repos are libraries that compose with URML, not substrates URML targets.
2. **Target ROAHM Lab (Ram Vasudevan) or Bezzo Lab (Ella Atkins) instead.** Held back. UMich Robotics is broad; CURLY + the department curriculum is the strongest single entry point.

## Prior art

- `UMich-CURLY` GitHub org (78 public repos, 197 followers).
- `UMich-CURLY/drift` (176 stars), `Debias_IMU` (122 stars), `deep-contact-estimator` (113 stars), `3DMapping` (92 stars), `unified_cvo` (81 stars).
- UMich Robotics Department website: `robotics.umich.edu`.
- ROB 101 / ROB 102 / ROB 401 course pages.
- [RFC-0009](0009-legged-humanoid-mobility.md): URML's legged-humanoid capability schema.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): the NVIDIA Isaac Lab outreach; bipedal sim research cross-link.
- [RFC-0011](0011-educational-profile.md): URML educational profile.

## Unresolved questions

For Prof. Ghaffari + Prof. Grizzle + UMich Robotics team:

1. **ROB 101 / ROB 102 coursework integration.** Are these courses (or successors) candidates for URML primitive vocabulary as a teaching artifact?
2. **CURLY + URML composition.** Is documenting URML's `measure` primitive consuming CURLY state-estimation outputs (`drift`, `3DMapping`, `unified_cvo`) a useful direction?
3. **Bipedal-locomotion research cross-link.** Are Cassie / Digit URDFs candidate URML manifest reference geometries?
4. **Isaac Lab cross-coordination.** UMich publishes against Isaac; is coordinating with URML's open [RFC-0050](0050-nvidia-isaac-lab-integration.md) outreach useful?
5. **Other UMich Robotics labs.** Which other labs (ROAHM, others) would benefit from a separate URML outreach in a future Move #7?
6. **Conformance lane.** Open to a URML conformance line on `UMich-CURLY` repo READMEs or `robotics.umich.edu`?
7. **Anything else.**

## Implementation note

RFC-0084 ships as a single RFC document PR. No code in this PR. Research-collab framing. Fifth Move #6 RFC; the most teaching-pipeline-ready of the wave per the plan. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`UMich-CURLY/drift` is the highest-visibility CURLY repo at 176 stars (verified 2026-05-25). URML's planned channel: open a single Issue on `UMich-CURLY/drift` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Ghaffari + Prof. Grizzle via `robotics.umich.edu`. Department-level coursework discussion may need a separate thread to the ROB 101 / 102 instructor team.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] ROB 101 / ROB 102 / ROB 401 curriculum value highlighted; teaching-pipeline-ready angle.
- [x] CURLY + URML composition framed honestly (libraries that compose, not substrates URML targets).
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, multi-lab department, curriculum decisions are department-level, academic cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
