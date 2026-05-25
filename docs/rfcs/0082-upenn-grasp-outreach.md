---
rfc: 0082
title: UPenn GRASP Lab integration, research-collab proposal to Vijay Kumar
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

# RFC-0082: UPenn GRASP Lab integration, research-collab proposal to Vijay Kumar

## Summary

URML proposes alignment with the UPenn GRASP Lab via the [`KumarRobotics` GitHub org](https://github.com/KumarRobotics) (93 public repos, 729 followers; led by Prof. Vijay Kumar, Nemirovsky Dean of Engineering). The ask is **research-collab** focused on multi-agent + aerial + ground-aerial heterogeneous fleets: URML's substrate-neutral primitive vocabulary is the missing intent layer above the swarm-coordination research GRASP has published for over a decade. No spec change on URML's side. Third Move #6 RFC.

## Motivation

GRASP fills a niche URML's prior outreach has not covered: **multi-agent + aerial-ground heterogeneous fleet coordination**. URML's Move #1 covered ground industrial OEMs, Move #2 covered the AI/ML layer, Move #3 covered affordable hardware, Move #4 covered adjacent niches including the [RFC-0066 (AgileX)](0066-agilex-outreach.md) mobile-base family and [RFC-0049 (ANYmal)](0049-anybotics-anymal-integration.md) quadrupeds, Move #5 covered Tier 2 promotions. None of these touched the **swarm + heterogeneous fleet** research surface where GRASP is a global leader.

Verified surface (2026-05-25):
- 93 public repos, 729 followers (the largest follower count in Move #6).
- Top-starred: `msckf_vio` (1.9k stars, "Robust Stereo Visual Inertial Odometry for Fast Autonomous Flight", C++), `kr_autonomous_flight` (771 stars, "KumarRobotics autonomous flight system for GPS-denied quadrotors", C++), `SLIDE_SLAM` (248 stars, multi-robot navigation), `MOCHA` (38 stars, multi-robot communication framework, Python), `HALO` (14 stars, language-conditioned aerial exploration, Python).
- License pattern: BSD-3-Clause predominant (kr_mav_control, air_router, SLIDE_SLAM), MIT (rotorpy), Apache-2.0 (zed-ros2-wrapper).

URML's specific value for GRASP:
- **MOCHA + SLIDE_SLAM cross-link.** MOCHA is a multi-robot communication framework; SLIDE_SLAM is sparse / decentralised metric-semantic SLAM. URML's substrate-Protocol abstraction sits at the intent layer above both. A URML program describing "scout the warehouse with three drones and a quadruped" decomposes into MOCHA-coordinated SLIDE_SLAM-aware execution on each substrate.
- **HALO cross-link.** Language-conditioned aerial exploration is exactly URML's English-to-primitive translation territory. URML's reference/llm-bridge could compose with HALO's natural-language input layer.
- **Cross-link to RFC-0053 (Open-RMF).** URML's existing Move #2 outreach to the Open-RMF multi-robot framework partly addresses the fleet-coordination story; GRASP's research-grade work complements RFC-0053's deployment-grade work.

## Detailed design (light, research-collab)

URML proposes:

1. **MOCHA + URML composition.** A documented note clarifying that URML programs can decompose into MOCHA-coordinated execution on heterogeneous fleets. Optional pilot mapping in URML's `reference/llm-bridge` showing the path from English → URML program → MOCHA dispatch.
2. **HALO + URML composition.** HALO's language-conditioned exploration as a candidate consumer of URML primitive output. The mapping is a paper-worthy thread.
3. **Coursework integration.** CIS 3960X / MEAM 5100 (Robotics & Autonomous Systems) as a candidate course for URML primitive vocabulary in undergraduate / graduate robotics teaching.
4. **Cross-link to [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md).** URML's fleet-adapter pattern from RFC-0053 is the deployment-grade counterpart to GRASP's research-grade multi-robot coordination; a documented note keeping the two threads aware of each other.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **GRASP is one of the largest robotics labs at any US institution.** PI attention is scarce; URML's RFC competes with substantial inbound research traffic.
- **Multi-agent semantics are an open URML question.** URML's Layer-2 primitive vocabulary has no explicit multi-agent `coordinate(...)` primitive (the question raised in [RFC-0047 (MolmoAct)](0047-allen-institute-molmoact.md), [RFC-0056 (ALOHA)](0056-stanford-aloha.md), [RFC-0068 (PAL Robotics)](0068-pal-robotics-outreach.md)). GRASP's outreach is the strongest case yet for a future Spec RFC adding multi-agent coordination primitives.
- **Aerial focus narrows the audience.** Many GRASP repos are quadrotor-centric. URML's PX4 substrate runtime ([RFC-0041 (ArduPilot)](0041-ardupilot-integration.md)) is the institutional bridge; URML's `move_to` semantics for aerial vehicles need to align with whatever conventions GRASP recommends.

## Alternatives considered

1. **Ship a `KumarRoboticsAdapter` consuming kr_autonomous_flight or MOCHA.** Rejected. The composition shape is a research-collab question worth maintainer input first.
2. **Fold GRASP outreach into [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md) as another multi-robot-coordination thread.** Rejected. Different audiences (Open-RMF is deployment-grade fleet management; GRASP is research-grade swarm coordination).

## Prior art

- `KumarRobotics` GitHub org (93 public repos, 729 followers).
- `KumarRobotics/msckf_vio` (1.9k stars), `kr_autonomous_flight` (771 stars), `SLIDE_SLAM` (248 stars), `MOCHA` (38 stars), `HALO` (14 stars).
- GRASP Lab website: `grasp.upenn.edu`.
- CIS 3960X / MEAM 5100 (Robotics & Autonomous Systems) course pages.
- [RFC-0041](0041-ardupilot-integration.md): ArduPilot Move #2 RFC; aerial substrate cross-link.
- [RFC-0047](0047-allen-institute-molmoact.md), [RFC-0056](0056-stanford-aloha.md), [RFC-0068](0068-pal-robotics-outreach.md): the multi-agent coordination primitive question.
- [RFC-0053](0053-open-rmf-multirobot-integration.md): Open-RMF Move #2 RFC; fleet-coordination cross-link.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For Prof. Kumar + GRASP team:

1. **MOCHA composition.** Is MOCHA an explicit composition target for URML primitive decomposition, or is the natural composition at a different level?
2. **HALO + URML language-conditioned exploration.** Is there interest in a documented mapping from URML primitives to HALO's exploration commands?
3. **Multi-agent primitive question.** Is there a coordination primitive ([RFC-0047 / RFC-0056 / RFC-0068](0047-allen-institute-molmoact.md) raise this) that GRASP's research suggests URML should adopt?
4. **Coursework integration.** Is CIS 3960X / MEAM 5100 a candidate course for URML primitive vocabulary?
5. **Open-RMF coordination.** Should URML's open RFC-0053 thread coordinate with GRASP's research direction on fleet management?
6. **Conformance lane.** Open to a URML conformance line on `kr_autonomous_flight` README or `grasp.upenn.edu`?
7. **Anything else.**

## Implementation note

RFC-0082 ships as a single RFC document PR. No code in this PR. Research-collab framing. Third Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`KumarRobotics/msckf_vio` is the highest-visibility repo at 1.9k stars (verified 2026-05-25). URML's planned channel: open a single Issue on a more lab-cross-cutting repo. `KumarRobotics/kr_autonomous_flight` (771 stars) or `KumarRobotics/MOCHA` (38 stars, multi-robot). Labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email via the GRASP Lab contact page at `grasp.upenn.edu`.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Motivation grounded in verified `KumarRobotics` surface and named top-starred repos.
- [x] Multi-agent primitive question surfaced honestly; cross-references the open URML conversation.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, PI attention scarce, multi-agent gap, aerial focus).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; multi-agent coordination flagged as future Spec RFC question.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
