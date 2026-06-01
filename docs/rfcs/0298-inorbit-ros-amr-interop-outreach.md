---
rfc: 0298
title: InOrbit ros_amr_interop integration (+ MassRobotics AMR Interop Standard, Open-RMF fleet adapter), request for comment from inorbit-ai maintainers
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

# RFC-0298: InOrbit ros_amr_interop integration, request for comment from inorbit-ai maintainers

No spec change is proposed here. This is an Outreach RFC: it proposes a mapping from URML v0.1 to an existing target's bridge, not a change to URML's normative surface. Second Move #21 RFC; the interoperability hub of the wave.

## Summary

URML proposes alignment with [`inorbit-ai/ros_amr_interop`](https://github.com/inorbit-ai/ros_amr_interop), the open ROS 2 bridge that implements the **MassRobotics AMR Interoperability Standard** and an **Open-RMF fleet adapter** (`rmf_inorbit_fleet_adapter`), and ships VDA5050 adapter examples. This single repository is where three of URML's warehouse interest-lines converge, which makes it the natural hub for the Move #21 wave. The ask is research-collab: a documented mapping from URML's intent vocabulary onto the MassRobotics-standard message set and the RMF fleet-adapter boundary, with a future adapter once engagement confirms the shape. This RFC is **also URML's engagement vehicle for the MassRobotics AMR Interop Standard itself**, whose own spec repository ([`MassRobotics-AMR/AMR_Interop_Standard`](https://github.com/MassRobotics-AMR/AMR_Interop_Standard)) has been dormant since 2021; InOrbit's active implementation is the live surface.

## Motivation

The MassRobotics AMR Interoperability Standard (a US-origin, vendor-neutral standard from the Boston-based MassRobotics non-profit) lets AMRs from different vendors report status and coordinate in a shared facility. InOrbit's `ros_amr_interop` is the actively maintained open implementation, and the same repository carries an Open-RMF fleet adapter — so it spans both the interop-standard layer and the fleet-orchestration layer that URML's warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)) and Open-RMF bridge ([RFC-0053](0053-open-rmf-multirobot-integration.md)) target.

Verified surface (2026-06-01):
- [`inorbit-ai/ros_amr_interop`](https://github.com/inorbit-ai/ros_amr_interop): BSD-3-Clause, Issues enabled, not archived, active (last push 2026-05-18), ~110 stars. Contains a MassRobotics-standard implementation + `rmf_inorbit_fleet_adapter` (a Full-Control Open-RMF fleet adapter) + demos/templates.
- [`inorbit-ai/vda5050_adapter_examples`](https://github.com/inorbit-ai/vda5050_adapter_examples): VDA5050 adapter examples ([RFC-0297](0297-vda5050-outreach.md)).
- [`MassRobotics-AMR/AMR_Interop_Standard`](https://github.com/MassRobotics-AMR/AMR_Interop_Standard): the standard's materials repo; Issues enabled but dormant since 2021.
- Origin: United States (InOrbit, Mountain View CA; MassRobotics, Boston MA); default-policy pass.

URML's specific value here:
- **One intent description, two orchestration exits.** A URML warehouse program compiles to validated primitives that can exit either as MassRobotics-standard status/coordination messages or as Open-RMF tasks via the InOrbit fleet adapter, by manifest/config choice. URML is the substrate-neutral intent layer above both.
- **Cross-robot static validation the interop standard does not perform.** The MassRobotics standard standardizes reporting and coordination signaling; it does not statically verify that a multi-AMR plan is free of shared-workspace contention or that handoffs are well-formed. URML's `validate_fleet` ([RFC-0286](0286-multi-robot-fleet-addressing.md)) + geometric deconfliction ([RFC-0291](0291-utm-strategic-deconfliction.md)) do, before dispatch.
- **Zero new vocabulary.** RFC-0022 covers warehouse intent with the core twelve primitives — no URML extension needed for this target.

## Detailed design (research-collab)

1. **Engage on `inorbit-ai/ros_amr_interop`** with a documented URML → MassRobotics-standard and URML → RMF-fleet-adapter mapping, building on [RFC-0053](0053-open-rmf-multirobot-integration.md)'s two-vector pattern (URML-as-task-source + URML-as-fleet-adapter).
2. **If engagement signals interest**, ship an adapter under `reference/mobile-runtime/` that targets the InOrbit/RMF fleet-adapter boundary, with hermetic fake-substrate tests ([RFC-0073](0073-robotical-marty-outreach.md) pattern).
3. **Cover the MassRobotics standard through this thread**, since its own repo is dormant; cross-reference an optional off-GitHub courtesy to MassRobotics the organization.

### Proposed mapping (sketch)

| URML primitive | Realisation |
|---|---|
| `move_to` / `pick_from` / `place_at` | RMF task description (`Delivery` / `CustomTask`) via the InOrbit fleet adapter, or a MassRobotics-standard coordination exchange. |
| `wait_for(partner_ready)` | A coordination gate expressed through the interop standard / RMF negotiation. |
| `dock(service: charge)` | RMF `ChargeBattery` task. |
| `report(status)` | Consume the MassRobotics-standard status report; append to a per-session log. |

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Implementer, not the standard body.** Engaging InOrbit's implementation is the pragmatic live path; the MassRobotics standard body itself is reached only via an optional off-GitHub courtesy (its spec repo is dormant). The RFC names this honestly.
- **Two exits add scoping work.** Covering both the MassRobotics-standard message set and the RMF adapter in one RFC is broad; the depth comes from maintainer signal on which exit matters most.

## Alternatives considered

1. **Post on the dormant `MassRobotics-AMR/AMR_Interop_Standard` repo.** Rejected; inactive since 2021, so a post there is low-yield (the same dormancy reasoning that routed [RFC-0292 OhmniLabs](0292-ohmnilabs-outreach.md) off-GitHub). InOrbit's active implementation is the better surface.
2. **Fold this into the Open-RMF RFC ([RFC-0053](0053-open-rmf-multirobot-integration.md)).** Rejected; RFC-0053 targets Open-RMF core, while InOrbit adds the MassRobotics-standard layer and a concrete fleet adapter — a distinct, additive surface.
3. **Skip the interop layer and engage only vendors.** Rejected; the closed-surface AMR vendors (Locus/Vecna/Seegrid/MiR, this wave's off-GitHub RFCs) are reached precisely *through* interop standards, so the interop layer is the leverage point.

## Prior art

- [`inorbit-ai/ros_amr_interop`](https://github.com/inorbit-ai/ros_amr_interop) (BSD-3) and [`inorbit-ai/vda5050_adapter_examples`](https://github.com/inorbit-ai/vda5050_adapter_examples).
- [`MassRobotics-AMR/AMR_Interop_Standard`](https://github.com/MassRobotics-AMR/AMR_Interop_Standard).
- [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md), [RFC-0297 (VDA5050)](0297-vda5050-outreach.md), [RFC-0299 (openTCS)](0299-opentcs-outreach.md): Move #21 interop siblings.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md): the warehouse + fleet machinery URML brings.

## Unresolved questions

For the inorbit-ai maintainers:

1. **Adapter boundary.** Is the `rmf_inorbit_fleet_adapter` (RMF) boundary the right place for a URML integration, the MassRobotics-standard message layer, or both?
2. **MassRobotics standard.** Is `ros_amr_interop` the canonical place to discuss the standard now that the standard's own repo is quiet, or is there a better venue?
3. **Adapter home.** URML repo (`reference/mobile-runtime/`), a contributed example in `ros_amr_interop`, or both?
4. **VDA5050 overlap.** Should a URML mapping prefer the VDA5050 path, the MassRobotics path, or treat them as parallel exits?
5. **Anything else.**

## Implementation note

RFC-0298 ships as a single RFC document PR. No adapter code in this PR. Also the engagement vehicle for the MassRobotics AMR Interop Standard. Ledger entries in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml) (the InOrbit row plus a MassRobotics row referencing this RFC).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

`inorbit-ai/ros_amr_interop` has Issues enabled (verified 2026-06-01). URML's planned channel: open a single Issue pointing to this RFC and naming the MassRobotics-standard + Open-RMF-adapter overlap.

This RFC and its accompanying outreach post are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Hub framing explicit (MassRobotics standard + RMF adapter + VDA5050 examples converge here).
- [x] MassRobotics-standard dormancy acknowledged; InOrbit named as the live engagement vehicle.
- [x] Cross-robot static-validation differentiator surfaced.
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] Cross-link to RFC-0053/0297/0299 (siblings), RFC-0022/0286/0291, RFC-0073 (pattern), RFC-0292 (dormancy precedent).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, implementer-not-standard-body, two-exit scope).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01 (InOrbit active; MassRobotics dormancy documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
