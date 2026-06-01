---
rfc: 0301
title: Vecna Robotics integration, research-collab proposal (off-GitHub, via the interop layer)
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

# RFC-0301: Vecna Robotics integration, research-collab proposal (off-GitHub, via the interop layer)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Vecna Robotics (pallet and material-handling warehouse AMRs, US-domiciled). The ask is research-collab + a surface question. **Engagement surface is off-GitHub** (no public developer API / GitHub org). The likely technical bridge is the **AMR interop layer** ([RFC-0297 VDA5050](0297-vda5050-outreach.md), [RFC-0298 InOrbit / MassRobotics standard](0298-inorbit-ros-amr-interop-outreach.md)); Vecna is a MassRobotics AMR Interoperability Standard working-group member.

## Motivation

Vecna Robotics (Waltham, MA, USA; default-policy pass) builds material-handling AMRs (pallet jacks, tuggers, case handling) orchestrated by its Pivotal platform, and is a documented MassRobotics AMR Interop Standard working-group member. Its pallet / case handling maps cleanly onto URML's warehouse primitives (`pick_from`, `place_at`, `move_to`, handoff via `wait_for(partner_ready)`) under the warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)). URML's value is natural-language intent plus cross-robot static validation, riding the interop standard.

Verified surface (2026-06-01):
- Company: vecnarobotics.com (US HQ Waltham MA). Pivotal orchestration platform.
- **No public developer API / SDK / GitHub org located.** Engagement is off-GitHub.
- Interop link: Vecna is a MassRobotics AMR Interop Standard working-group member.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the Vecna company contact surface**, asking whether an integration surface exists (directly or via the MassRobotics standard / VDA5050).
2. **If a surface exists or opens**, URML targets the **interop layer**: a URML program validates ([RFC-0286](0286-multi-robot-fleet-addressing.md) + [RFC-0291](0291-utm-strategic-deconfliction.md)) and emits MassRobotics-standard / VDA5050 messages, with no Vecna-private adapter and no new URML vocabulary.

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified developer surface.** Courtesy + question, not an adapter pre-design.
- **Heavy material handling.** Pallet/tugger loads imply load-handling actions that are vendor-specific (mirrors the VDA5050 action-set caveat in [RFC-0297](0297-vda5050-outreach.md)); the manifest declares them.
- **Light engagement payload.** Depth depends on Vecna's response; the interop layer is the realistic path.

## Alternatives considered

1. **Reverse-engineer Pivotal.** Rejected; brittle, validator-first posture.
2. **Skip Vecna.** Rejected; a material-handling AMR leader rounds out the wave beyond goods-to-person (Locus, [RFC-0300](0300-locus-robotics-outreach.md)).
3. **Fold into the InOrbit RFC.** Rejected; distinct vendor engagement over a shared interop bridge.

## Prior art

- vecnarobotics.com; MassRobotics AMR Interop Standard membership.
- [RFC-0298 (InOrbit / MassRobotics standard)](0298-inorbit-ros-amr-interop-outreach.md), [RFC-0297 (VDA5050)](0297-vda5050-outreach.md).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md), [RFC-0294 (Labrador)](0294-labrador-systems-outreach.md): off-GitHub courtesy precedents.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md), [RFC-0300 (Locus)](0300-locus-robotics-outreach.md).

## Unresolved questions

For Vecna Robotics:

1. **Integration surface.** Does Vecna expose (or plan) an integration surface, directly or via the MassRobotics standard / VDA5050?
2. **Engagement channel.** Company contact form, or a partnerships / dev-relations contact?
3. **Load-handling actions.** How are pallet/tugger load operations exposed for a substrate-neutral mapping?
4. **Natural-language authoring.** Is URML's intent layer of interest to the Pivotal product side?
5. **Anything else.**

## Implementation note

RFC-0301 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

Vecna's contact surface is vecnarobotics.com. URML's planned channel: a courtesy message via the company contact surface pointing at this RFC.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub framing explicit; absence of a developer surface acknowledged honestly.
- [x] Interop layer named as the realistic technical bridge (RFC-0297/0298).
- [x] Zero-new-vocabulary claim grounded in RFC-0022; load-handling-action caveat honest.
- [x] Cross-link to off-GitHub precedents, interop siblings, fleet machinery, RFC-0300.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no developer surface, vendor load actions, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01 (absence of developer surface documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
