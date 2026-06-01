---
rfc: 0302
title: Seegrid integration, research-collab proposal (off-GitHub, via the interop layer)
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

# RFC-0302: Seegrid integration, research-collab proposal (off-GitHub, via the interop layer)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Seegrid (vision-guided warehouse AMRs/AGVs, US-domiciled). The ask is research-collab + a surface question. **Engagement surface is off-GitHub** (no public developer API / GitHub org). The likely technical bridge is the **AMR interop layer** ([RFC-0297 VDA5050](0297-vda5050-outreach.md), [RFC-0298 InOrbit / MassRobotics standard](0298-inorbit-ros-amr-interop-outreach.md)); Seegrid is a MassRobotics AMR Interoperability Standard working-group member.

## Motivation

Seegrid (Pittsburgh, PA, USA; default-policy pass) builds vision-guided AMRs (its Palion lift and tow products) that navigate without fixed infrastructure (no magnetic tape or markers), orchestrated by a fleet management layer. Its tow/lift transport pattern maps onto URML's warehouse primitives (`move_to`, `pick_from`/`place_at` at declared docks, handoff via `wait_for`) under the warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)). URML's value is natural-language intent + cross-robot static validation, riding the interop standard.

Verified surface (2026-06-01):
- Company: seegrid.com (US HQ Pittsburgh PA). Vision-guided AMRs + fleet management.
- **No public developer API / SDK / GitHub org located.** Engagement is off-GitHub.
- Interop link: Seegrid is a MassRobotics AMR Interop Standard working-group member.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the Seegrid company contact surface**, asking whether an integration surface exists (directly or via the MassRobotics standard / VDA5050).
2. **If a surface exists or opens**, URML targets the **interop layer**: validate ([RFC-0286](0286-multi-robot-fleet-addressing.md) + [RFC-0291](0291-utm-strategic-deconfliction.md)) and emit MassRobotics-standard / VDA5050 messages, no Seegrid-private adapter, no new URML vocabulary.

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified developer surface.** Courtesy + question, not an adapter pre-design.
- **Vision-guided navigation specifics.** Seegrid's infrastructure-free navigation is internal; URML maps to named locations / docks, not to Seegrid's perception. Named honestly.
- **Light engagement payload.** Depth depends on Seegrid's response; the interop layer is the realistic path.

## Alternatives considered

1. **Reverse-engineer the Seegrid fleet surface.** Rejected; brittle, validator-first posture.
2. **Skip Seegrid.** Rejected; a vision-guided AMR/AGV leader complements goods-to-person (Locus) and material handling (Vecna) in the wave.
3. **Fold into the InOrbit RFC.** Rejected; distinct vendor engagement over a shared interop bridge.

## Prior art

- seegrid.com; MassRobotics AMR Interop Standard membership.
- [RFC-0298 (InOrbit / MassRobotics standard)](0298-inorbit-ros-amr-interop-outreach.md), [RFC-0297 (VDA5050)](0297-vda5050-outreach.md).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md), [RFC-0294 (Labrador)](0294-labrador-systems-outreach.md): off-GitHub courtesy precedents.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md), [RFC-0300 (Locus)](0300-locus-robotics-outreach.md), [RFC-0301 (Vecna)](0301-vecna-robotics-outreach.md).

## Unresolved questions

For Seegrid:

1. **Integration surface.** Does Seegrid expose (or plan) an integration surface, directly or via the MassRobotics standard / VDA5050?
2. **Engagement channel.** Company contact form, or a partnerships / dev-relations contact?
3. **Fleet boundary.** Where does a third party submit transport intent to a Seegrid fleet?
4. **Natural-language authoring.** Is URML's intent layer of interest to the Seegrid product side?
5. **Anything else.**

## Implementation note

RFC-0302 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

Seegrid's contact surface is seegrid.com. URML's planned channel: a courtesy message via the company contact surface pointing at this RFC.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub framing explicit; absence of a developer surface acknowledged honestly.
- [x] Interop layer named as the realistic technical bridge (RFC-0297/0298).
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] Cross-link to off-GitHub precedents, interop siblings, fleet machinery, RFC-0300/0301.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no developer surface, vision-guided specifics, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01 (absence of developer surface documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
