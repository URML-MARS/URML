---
rfc: 0191
title: JHU dVRK (Da Vinci Research Kit, surgical robotics flagship) integration, request for comment from jhu-dvrk maintainers — CISST license-clarification ask
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0191: JHU dVRK (Da Vinci Research Kit) integration — CISST license-clarification ask

## Summary

URML does not yet ship a surgical-class manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Johns Hopkins Da Vinci Research Kit over [`jhu-dvrk/sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit), and **requests review and feedback from the jhu-dvrk maintainers**. **CISST license-clarification ask:** the repo uses a CISST custom permissive license that isn't SPDX-recognized; an explicit OSI declaration would unlock URML's Apache-2.0 downstream adapter-grade bundling. No spec change.

**This is URML's first surgical / medical-robotics RFC** (Theme D from the Move-11 backlog gap analysis). It opens a new vertical for URML's manifest vocabulary.

## Motivation

The dVRK is the open-research surface for the da Vinci surgical platform. Maintained by Johns Hopkins University's Engineering Research Center for Computer-Integrated Surgical Systems and Technology (ERC CISST), it's the canonical research surface that surgical-robotics labs worldwide use for telesurgery and computer-integrated-surgery research. Intuitive Surgical's commercial da Vinci product is closed; the dVRK is what makes academic surgical-robotics research possible at all.

Repo at [`jhu-dvrk/sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit) (CISST custom permissive license — clarification ask, 157 stars, Issues enabled, last commit `2026-04-18` active, **not archived**).

URML benefits from documenting the dVRK manifest mapping because:

1. **Surgical / medical robotics is a structural URML manifest gap.** URML's v0.1 has no surgical-class platform declaration; no manifest field for telesurgery control-loop topology; no field for surgical-instrument-class declaration. Engagement opens the class entirely.
2. **Research-lab-direct surface is the right engagement layer.** OEM-vendor engagement (Intuitive Surgical, Auris/J&J, CMR Surgical, Stryker Mako) is impossible — all closed. JHU is the proper layer for the manifest-mapping conversation.
3. **CISST license clarification matters for downstream operators.** CISST custom permissive is functionally Apache-2.0-friendly but isn't SPDX-recognized; URML's manifest-bundling rules need clarity.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `jhu_dvrk_surgical_cell.yaml` fixture)

| URML field | Maps to dVRK attribute |
|---|---|
| `name` | Specific configuration (`jhu_dvrk_si` for Si-class da Vinci, `jhu_dvrk_classic` for older) |
| `platform_class: custom` (`surgical_telesurgery`) | URML's first surgical-class platform declaration |
| `topology: custom` (`master_console_plus_patient_side_cart`) | Telesurgery master-slave topology |
| `actuators` | Patient-Side Cart manipulators (PSMs) + Endoscope-Camera Manipulator (ECM) |
| `master_devices: custom` (`master_tool_manipulators`) | Surgeon-side input devices (MTMs) |
| `safety_envelope` | Per RFC-0012; surgical envelopes need force-magnitude + position-error + foot-pedal-state constraints not in URML v0.1 |
| `regulatory_class: custom` (`research_use_only_not_for_clinical_use`) | Critical declaration — dVRK is explicitly research, NOT FDA-cleared for patient procedures |

### What URML v0.1 does not yet express for dVRK

1. **Surgical-class platform declaration.** URML's v0.1 has no `platform_class: surgical_telesurgery` enum entry. Spec RFC queued — opens the surgical-vertical vocabulary entirely.
2. **Telesurgery master-slave topology declaration.** Master-console + patient-side-cart topology is structurally distinct from URML's existing mobile-manipulator / humanoid / cobot patterns. Composite cross-block topology gap.
3. **Surgical-instrument-class declaration.** dVRK instruments are interchangeable end-effectors with specific surgical purposes (large needle driver, monopolar curved scissors, etc.) URML's manifest cannot today declare.
4. **Regulatory-class declaration.** "Research use only" vs "FDA-cleared clinical use" is a load-bearing declaration for any surgical platform. URML's v0.1 has no field; engagement may surface the safety-implication framing.
5. **CISST license OSI clarity.** CISST permissive distribution but not SPDX-recognized.

### Compatibility notes

- **Vendor / lab.** [`jhu-dvrk`](https://github.com/jhu-dvrk) — Johns Hopkins University ERC CISST.
- **Flagship repo.** [`jhu-dvrk/sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit) — CISST custom permissive license (clarification ask), 157 stars, Issues enabled, last commit 2026-04-18 active, **not archived**.
- **Origin.** Johns Hopkins University, Maryland US. Passes US-federal default policy.
- **License fit.** Pending CISST → OSI clarification. URML's adapter composes at the ROS / CISST-bridge boundary regardless.
- **Maintainer signal.** Active ERC research lab; foundational surgical-robotics-research community surface.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; surgical-class platform + telesurgery master-slave topology + surgical-instrument-class + regulatory-class declaration Spec RFCs queued.
- Reference runtime: future `reference/surgical-runtime/DvrkAdapter` is a candidate — opens a new URML reference-runtime subdirectory.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **CISST license-clarification gate.** Custom permissive blocks confident Apache-2.0 downstream bundling without OSI declaration.
- **Multiple Spec-RFC prerequisites** (surgical-class platform, telesurgery topology, instrument-class, regulatory-class).
- **Research-use-only platform** — URML cannot ship a clinical-grade adapter; the manifest must declare the constraint visibly.
- **First-vertical novelty.** URML has no prior surgical / medical engagement to compose with.

## Alternatives considered

1. **Engage Intuitive Surgical directly instead.** Rejected. Intuitive Surgical's commercial product is closed; no engageable public surface. JHU dVRK is the proper open-research engagement layer.
2. **Bundle surgical with sibling medical-research RFCs (iCub).** Rejected. iCub (RFC-0192) is humanoid-with-assistive-angle, structurally different from dVRK's telesurgery topology. Per-target RFCs.
3. **Cross-citation only.** Rejected. Vendor-research-lab-direct + active + first surgical vertical argues for full manifest mapping engagement.

## Prior art

- [`jhu-dvrk/sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit) — the upstream flagship.
- [`jhu-saw`](https://github.com/jhu-saw) — JHU Surgical Automation & Advanced Robotics Lab; companion org with `sawIntuitiveDaVinci` and related repos.
- [RFC-0012 (safety envelopes)](0012-safety-envelopes.md) — URML's envelope primitives; surgical extensions need additional constraint classes.
- [RFC-0192 (IIT iCub)](0192-iit-icub-main-outreach.md) — sibling Move-15 medical-research-humanoid RFC.

## Unresolved questions

For the jhu-dvrk maintainers:

1. **CISST license clarification.** Can `jhu-dvrk/sawIntuitiveResearchKit` get an explicit OSI-recognized license declaration (or clarification that CISST is Apache-2.0-style equivalent for downstream bundling purposes)?
2. **Surgical-class platform manifest fields.** URML's v0.1 has no surgical-class declaration. Spec RFC queued. What manifest fields would a dVRK deployment expect (master-slave topology, instrument-class declaration, force/position constraints)?
3. **Regulatory-class declaration.** Should URML's manifest declare research-use-only vs FDA-cleared status as a first-class field?
4. **Telesurgery control-loop declaration.** Master-MTM + patient-PSM coupling has specific safety-and-latency constraints; manifest field shape?
5. **Adapter home.** URML repo (`reference/surgical-runtime/DvrkAdapter`), JHU-maintained `jhu-dvrk/dvrk-urml-bridge`, or both?
6. **Conformance listing.** Would the dVRK maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0191 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move15.yaml`](../../examples/lighthouses/outreach-move15.yaml).

## How to respond

`jhu-dvrk/sawIntuitiveResearchKit` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the CISST license-clarification ask explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (CISST permissive, 157 stars, Issues enabled, last commit 2026-04-18 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (CISST license-clarification gate, multiple Spec-RFC prerequisites, research-use-only constraint, first-vertical novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Johns Hopkins University US Maryland; default policy passes.
- [x] CLAUDE.md compliance check passed.
