---
rfc: 0080
title: UC Berkeley AUTOLAB integration, research-collab proposal to Ken Goldberg
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

# RFC-0080: UC Berkeley AUTOLAB integration, research-collab proposal to Ken Goldberg

## Summary

URML proposes alignment with the UC Berkeley AUTOLAB ([`BerkeleyAutomation` GitHub org](https://github.com/BerkeleyAutomation), 183 public repos, 241 followers; led by Prof. Ken Goldberg). The ask is **research-collab**, not vendor outreach: URML's substrate-neutral Layer-2 vocabulary as a teaching artifact in Berkeley EECS 206A/B and as a substrate-neutral target for AUTOLAB's manipulation-focused tools (dex-net, gqcnn, autolab_core, yumipy). No spec change on URML's side. No adapter against an AUTOLAB-specific platform. This is the first **Move #6** RFC.

## Motivation

AUTOLAB anchors the manipulation-research-with-warehouse-and-surgical-applications niche at Berkeley. Top-starred repos: `dex-net` (363 stars), `gqcnn` (342 stars), `python-fcl` (269 stars), `sd-maskrcnn` (215 stars), `autolab_core` (84 stars). License mix: MIT, Apache-2.0, BSD-3-Clause. The lab teaches EECS 206A/B (Kinematics, Dynamics, Multi-Robot Control), which is exactly the audience URML's primitive vocabulary serves: substrate-neutral robot programming above ROS 2 / Isaac / MuJoCo.

URML's specific value for AUTOLAB:
- Programs written against AUTOLAB's YuMi or Franka deployments retarget across substrates (UR, WLKATA, Trossen Interbotix, Robotnik mobile manipulator) via URML's manifest swap.
- The English-to-primitive translation path ([RFC-0021](0021-on-device-llm-bridge.md), reference/llm-bridge) lets coursework convert natural-language assignments into validated programs without students writing ROS code from scratch.
- URML's static-verification ([RFC-0014](0014-substrate-conformance.md) Draft) gives a grading surface: programs that validate against the manifest are syntactically correct before execution.

Distinction worth flagging: AUTOLAB is Ken Goldberg's lab. Pieter Abbeel's RAIL / BAIR Robotics is a separate Berkeley robotics surface, not covered by this RFC. URML's RFC-0069 (Berkeley Humanoid Lite, Hybrid Robotics Lab under Koushil Sreenath) is also distinct.

## Detailed design (light, research-collab)

This is not a vendor RFC. URML does not ship a `BerkeleyAutomationAdapter`. Instead, URML proposes:

1. **Coursework integration.** A documented EECS 206 module on URML's primitive vocabulary, taught in a single lecture + lab. URML's existing `examples/` directory provides starting code. AUTOLAB's instructor team owns the pedagogy.
2. **Research-collab on dex-net / gqcnn output mapping.** URML's `grasp` and `pick_from` primitives ([RFC-0013](0013-industrial-layer2-primitives.md)) sit one layer above gqcnn's grasp-quality output. A documented mapping (dex-net grasp candidate → URML primitive sequence → substrate adapter) is a paper-worthy thread.
3. **autolab_core cross-link.** URML's manifest schema and `autolab_core`'s utility set serve adjacent concerns (URML: capability declaration; autolab_core: perception/control utilities). A cross-link is documentation, not code.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. URML ships no code in this RFC.

## Drawbacks

- **Proposal-only.** No engagement payload beyond the RFC + Issue.
- **Berkeley is a large university.** AUTOLAB is one robotics lab among several at Berkeley; URML's outreach to AUTOLAB does not generalise to RAIL, Hybrid Robotics Lab ([RFC-0069](0069-berkeley-humanoid-lite-outreach.md)), or Berkeley Robotic Mobility lab.
- **PI attention is scarce.** Prof. Goldberg's lab is heavily-cited and busy; URML's RFC competes with substantial inbound research traffic.
- **Coursework integration depends on instructor adoption.** URML cannot push curriculum changes; the lab decides.

## Alternatives considered

1. **Ship a `BerkeleyAutomationAdapter` consuming gqcnn output.** Rejected for now; the integration shape is worth maintainer input first. A future adapter-PR follows engagement, not precedes it.
2. **Target Pieter Abbeel's RAIL instead.** Held back for a possible Move #7. RAIL's focus is RL and policy learning, distinct enough from AUTOLAB's manipulation-with-classical-control focus.

## Prior art

- `BerkeleyAutomation` GitHub org (183 public repos, 241 followers).
- `BerkeleyAutomation/dex-net` (363 stars), `gqcnn` (342 stars), `python-fcl` (269 stars), `sd-maskrcnn` (215 stars), `autolab_core` (84 stars).
- AUTOLAB website: `autolab.berkeley.edu`.
- EECS 206A/B course pages.
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives URML's `grasp` / `pick_from` cite.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): the URML profiles relevant to coursework integration.
- [RFC-0069](0069-berkeley-humanoid-lite-outreach.md): Berkeley Humanoid Lite (Hybrid Robotics Lab, different Berkeley lab; distinct outreach).

## Unresolved questions

For Prof. Goldberg + AUTOLAB team:

1. **Coursework integration interest.** Is EECS 206A/B (or a successor) a candidate for a URML primitive-vocabulary lecture + lab module?
2. **dex-net / gqcnn output mapping.** Is there interest in a documented mapping from gqcnn grasp output to URML `grasp` primitive emission?
3. **autolab_core cross-link.** Open to a documented note in `autolab_core` README acknowledging URML as a complementary primitive-layer?
4. **Conformance lane.** Open to a URML conformance line on AUTOLAB's documentation surface?
5. **Anything else.**

## Implementation note

RFC-0080 ships as a single RFC document PR. No code in this PR. Research-collab framing; the actual coursework module + dex-net mapping documentation follows engagement. First Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

`BerkeleyAutomation` org has 183 public repos and 241 followers (verified 2026-05-25). The most-active manipulation-research repos are `dex-net`, `gqcnn`, and `autolab_core`. URML's planned channel: open a single Issue on `BerkeleyAutomation/autolab_core` (the cross-cutting utility repo, most-likely-to-be-read by lab leadership) labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Goldberg via the `goldberg@berkeley.edu` address on `autolab.berkeley.edu`.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] PI attribution corrected (Goldberg, not Abbeel).
- [x] Motivation grounded in verified surface (183 repos, named top-starred repos, EECS 206A/B course).
- [x] Cross-link to RFC-0069 (Berkeley Humanoid Lite) explicit; different Berkeley lab.
- [x] At least one alternative considered (two: ship-first, target-RAIL-instead).
- [x] Drawbacks real (proposal-only, multi-lab Berkeley, PI attention, instructor adoption).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
