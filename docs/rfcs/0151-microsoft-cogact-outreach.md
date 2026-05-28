---
rfc: 0151
title: Microsoft CogACT (VLA for dexterous control) integration, request for comment from microsoft cogact maintainers
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

# RFC-0151: Microsoft CogACT (VLA for dexterous control) integration, request for comment from microsoft cogact maintainers

## Summary

URML does not yet ship a CogACT manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Microsoft's CogACT — a vision-language-action model for dexterous control published at CVPR 2025 — over [`microsoft/CogACT`](https://github.com/microsoft/CogACT) (MIT), and **requests review and feedback from the microsoft cogact maintainers**. No spec change.

This RFC pairs with [RFC-0138 (OpenVLA)](0138-openvla-outreach.md) and [RFC-0139 (Octo)](0139-octo-outreach.md) on URML's action-head class Spec-RFC gap. CogACT's distinct contribution is the **cognition-action joint architecture** trained for dexterous manipulation.

## Motivation

`microsoft/CogACT` is the CVPR 2025 publication of a VLA architecture jointly trained for cognitive reasoning and dexterous action. MIT license, 427 stars, Issues enabled, last commit `2025-10-30` (~7mo from 2026-05-28 cutoff; borderline-stale on research cadence), **not archived**.

CogACT is research-direct from Microsoft Research. Distinct from RFC-0150 microsoft/psi (temporal-streams infrastructure) — CogACT is at the VLA layer where URML's primitive vocabulary is the natural typed substrate consuming the policy's action output.

The URML-fit framing is: URML's manifest declares the VLA controller class is CogACT-compatible; URML's validator gates the action sequences CogACT emits against the active capability manifest before publish. Same pre-flight-check pattern as RFC-0138 OpenVLA.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `microsoft_cogact_cell.yaml` fixture)

| URML field | Maps to CogACT attribute |
|---|---|
| `name` | Deployment handle (`microsoft_cogact_default`) |
| `controller_class: custom` (`cogact_vla`) | Declares CogACT VLA is in the loop |
| `controller_class: custom` (`action_head: dexterous_grip`) | Declares the dexterous-control action head |
| `controller_class: custom` (`cognition_action_joint`) | Declares the joint-architecture training mode |
| `controller_class: custom` (`input_modalities: rgb+language`) | Declares supported input modalities |

### What URML v0.1 does not yet express for CogACT

1. **Action-head class declaration.** Same gap as RFC-0138 / RFC-0139; action-head Spec RFC queued.
2. **Cognition-action joint-architecture declaration.** CogACT's distinguishing feature is joint training; URML's manifest does not today distinguish joint-trained vs separately-trained controllers.
3. **Dexterous-control action-space declaration.** Dexterous-control action-spaces (multi-finger gripper configurations) are not first-class in URML's v0.1 actuator vocabulary.

### Compatibility notes

- **Vendor / org.** [`microsoft`](https://github.com/microsoft) — vendor-direct (Microsoft Research).
- **Flagship repo.** [`microsoft/CogACT`](https://github.com/microsoft/CogACT) — MIT, 427 stars, Issues enabled, last commit 2025-10-30, **not archived**.
- **Origin.** Microsoft, US. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** CVPR 2025 publication anchor; Microsoft Research engagement.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; action-head class declaration Spec RFC queued (shared with RFC-0138 / RFC-0139).
- Reference runtime: future `reference/vla-bridge/CogACTBridge` is a candidate.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Borderline-stale push date.** ~7mo at 2026-05-28; light-touch engagement expected.
- **Action-head class Spec RFC prerequisite** (shared with RFC-0138 / RFC-0139).
- **Dexterous-control action-space novelty.** Multi-finger gripper / dexterous configurations are a v0.1 vocabulary gap.

## Alternatives considered

1. **Bundle CogACT + PSI (RFC-0150) into one Microsoft-broader RFC.** Rejected. Different layers (VLA vs temporal-streams), different teams.
2. **Skip CogACT as duplicate with OpenVLA / Octo.** Rejected. Cognition-action joint architecture is a distinct contribution.
3. **Defer until action-head Spec RFC lands.** Rejected. CogACT maintainer input informs the Spec RFC.

## Prior art

- [`microsoft/CogACT`](https://github.com/microsoft/CogACT) — the upstream repo.
- [RFC-0138 (OpenVLA)](0138-openvla-outreach.md), [RFC-0139 (Octo)](0139-octo-outreach.md) — sibling generalist VLA RFCs sharing the action-head Spec-RFC gap.
- [RFC-0150 (Microsoft PSI)](0150-microsoft-psi-outreach.md) — sibling Microsoft research engagement (different layer).

## Unresolved questions

For the microsoft cogact maintainers:

1. **Repository status.** Is `microsoft/CogACT` actively maintained, or paper-publication-only?
2. **Action-head + dexterous-control manifest fields.** URML's v0.1 has neither. Spec RFCs queued. Manifest field expectations from CogACT perspective?
3. **Cognition-action joint-architecture declaration.** Should URML's manifest declare joint-trained controllers as a distinct class?
4. **Bridge home.** URML repo (`reference/vla-bridge/CogACTBridge`), Microsoft-maintained, or external?
5. **Conformance listing.** Would the maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
6. **Anything else.**

## Implementation note

RFC-0151 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`microsoft/CogACT` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 427 stars, Issues enabled, last commit 2025-10-30, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (borderline staleness, action-head Spec-RFC prerequisite, dexterous-control action-space novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Microsoft US; default policy passes.
- [x] CLAUDE.md compliance check passed.
