---
rfc: 0086
title: ETH Zurich Autonomous Systems Lab (ASL) integration, research-collab proposal to Roland Siegwart
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

# RFC-0086: ETH Zurich Autonomous Systems Lab (ASL) integration, research-collab proposal to Roland Siegwart

## Summary

URML proposes alignment with the ETH Zurich Autonomous Systems Lab (ASL) via the [`ethz-asl` GitHub org](https://github.com/ethz-asl) (458 public repos, 2.3k followers; led by Prof. Roland Siegwart). The ask is **research-collab** focused on SLAM + perception + path planning across ground / aerial / aquatic substrates. No spec change on URML's side. Seventh Move #6 RFC; the largest GitHub footprint of any Move #6 target.

## Motivation

ETH ASL is one of the largest academic-robotics GitHub presences in the world: 458 public repos, 2.3k followers, top-starred repos with thousands of stars. The lab spans ground, aerial, and aquatic systems with mature ROS integration going back over a decade.

Verified surface (2026-05-25):
- 458 public repos, 2.3k followers (largest follower count in Move #6).
- Top-starred: `maplab` (2.8k stars, modular mapping framework, C++), `ethzasl_msf` (1,091 stars, multi-sensor fusion with EKF, C++; Issues enabled with 58 open, last commit 2026-01-22), `wavemap` (559 stars, multi-resolution occupancy mapping, C++), `grid_map_geo` (166 stars, GDAL-based geolocalization), `data-driven-dynamics` (130 stars, Python aerial dynamics).
- License pattern: BSD-3-Clause + MIT + Apache-2.0.

Distinction worth flagging: ETH ASL is **Roland Siegwart's lab**. ETH Robotic Systems Lab (RSL, Marco Hutter) is the upstream of ANYmal. Covered indirectly by URML's [RFC-0049 (ANYbotics ANYmal)](0049-anybotics-anymal-integration.md). The two ETH labs are distinct; URML's outreach to ASL does not duplicate ANYmal work.

URML's specific value for ETH ASL:
- **SLAM + perception cross-link.** `maplab`, `wavemap`, and `ethzasl_msf` all sit below URML's intent layer. URML's `measure` primitive can dispatch to ASL state-estimation outputs.
- **Cross-substrate research.** ASL's ground / aerial / aquatic breadth is exactly URML's substrate-neutral value proposition. A URML program described once and executed across substrates is the ASL research narrative made concrete.
- **Coursework integration.** ASL's lab-based robotics projects in the ETH master's curriculum are candidate audiences for URML primitive vocabulary.

## Detailed design (light, research-collab)

URML proposes:

1. **`maplab` / `wavemap` cross-link.** Documented note that URML emits intent above mapping; ASL's mapping frameworks consume URML's `measure` outputs. Composition, not competition.
2. **Multi-sensor-fusion alignment.** URML's manifest sensor declarations align with `ethzasl_msf`'s sensor-state interface. A documented mapping is paper-worthy.
3. **Coursework integration.** ETH master's robotics projects as URML pilots. ASL's teaching team owns the pedagogy.
4. **Cross-link to [RFC-0049 (ANYmal)](0049-anybotics-anymal-integration.md).** The two ETH labs (ASL and RSL) are distinct; URML's outreach to both is explicit; readers should not collapse them.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **ETH ASL is enormous.** 458 public repos and 2.3k followers means URML's RFC competes with substantial inbound research traffic; PI and lab-manager attention is scarce.
- **Multi-substrate breadth makes the RFC abstract.** ASL's ground / aerial / aquatic span means URML's cross-substrate value proposition lands at a high level; the concrete coursework or composition pilot needs maintainer input to narrow.
- **Confusion risk with ETH RSL.** Static readers might confuse ASL (Siegwart) with RSL (Hutter); the RFC body and the cross-reference to RFC-0049 disambiguate.

## Alternatives considered

1. **Ship an `EthAslAdapter` against `maplab`.** Rejected. `maplab` is a mapping framework, not a substrate URML targets. The integration shape is composition, not adapter.
2. **Target ETH RSL (Hutter) instead.** Rejected for Move #6. RSL is already touched indirectly via ANYmal (RFC-0049). ASL is the uncovered ETH surface.

## Prior art

- `ethz-asl` GitHub org (458 public repos, 2.3k followers, BSD-3-Clause / MIT / Apache-2.0).
- `ethz-asl/maplab` (2.8k stars), `ethzasl_msf` (1,091 stars), `wavemap` (559 stars), `grid_map_geo` (166 stars), `data-driven-dynamics` (130 stars).
- ETH ASL website: `asl.ethz.ch`.
- Roland Siegwart's role: founding director of the IRIS Institute of Robotics and Intelligent Systems at ETH.
- [RFC-0049](0049-anybotics-anymal-integration.md): ANYbotics ANYmal outreach (upstream is ETH RSL, not ASL).
- [RFC-0009](0009-legged-humanoid-mobility.md), [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to ASL's research substrates.

## Unresolved questions

For Prof. Siegwart + ETH ASL team:

1. **`maplab` / `wavemap` / `ethzasl_msf` cross-link.** Is documented composition with URML's `measure` primitive a useful direction?
2. **Multi-sensor-fusion manifest alignment.** Is there a useful mapping between URML's manifest sensor declarations and `ethzasl_msf`'s sensor-state interface?
3. **Coursework integration.** Are there ETH master's robotics courses where URML primitive vocabulary would be a useful teaching artifact?
4. **ASL / RSL coordination.** Both ETH labs sit in URML's outreach landscape (ASL via this RFC, RSL via RFC-0049 ANYmal). Any ETH-internal coordination URML should be aware of?
5. **Conformance lane.** Open to a URML conformance line on `maplab` README or `asl.ethz.ch`?
6. **Anything else.**

## Implementation note

RFC-0086 ships as a single RFC document PR. No code in this PR. Research-collab framing. Seventh Move #6 RFC. Ledger entry in [`examples/lighthouses/outreach-move6.yaml`](../../examples/lighthouses/outreach-move6.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`ethz-asl/maplab` is the highest-visibility repo at 2.8k stars. `ethzasl_msf` has Issues enabled with 58 open (last commit 2026-01-22; verified 2026-05-25). URML's planned channel: open a single Issue on `ethz-asl/maplab` or `ethzasl_msf` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Prof. Siegwart via `asl.ethz.ch`.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] ASL / RSL disambiguation flagged.
- [x] Motivation grounded in verified `ethz-asl` surface and named top-starred repos.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, scale of org, multi-substrate abstraction risk, ASL/RSL confusion risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-25.
- [x] Provenance `origin: CH`; default policy passes (US treaty ally context).
- [x] CLAUDE.md compliance check passed.
