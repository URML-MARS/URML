---
rfc: 0299
title: openTCS integration, request for comment from the openTCS (Fraunhofer IML) maintainers
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

# RFC-0299: openTCS integration, request for comment from the openTCS (Fraunhofer IML) maintainers

No spec change is proposed here. This is an Outreach RFC: it proposes a mapping from URML v0.1 to an existing target's control system, not a change to URML's normative surface. Third Move #21 interop RFC.

## Summary

URML proposes a documented mapping from its intent vocabulary onto **openTCS** (the open Transportation Control System by Fraunhofer IML), a vendor-neutral control system that dispatches transport orders to, and routes, fleets of AGVs / AMRs. A URML program describes warehouse intent; URML compiles to validated primitives; those render as openTCS **transport orders** submitted through the openTCS kernel API. openTCS in turn drives vehicles via its comm-adapters (including a VDA5050 comm-adapter, linking this RFC to [RFC-0297](0297-vda5050-outreach.md)). URML composes above openTCS: URML is the intent layer; openTCS is the dispatch/routing layer. Engagement surface is [`openTCS/opentcs`](https://github.com/openTCS/opentcs) (Issues enabled).

## Motivation

openTCS is a mature, widely used open-source control system for driverless transport vehicles, maintained by Fraunhofer IML (Germany). It already abstracts vehicles behind comm-adapters and dispatches transport orders — the same dispatch boundary URML's warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)) and Open-RMF bridge ([RFC-0053](0053-open-rmf-multirobot-integration.md)) target. A clean URML → openTCS transport-order mapping gives URML users a fully open, on-premises fleet-control stack: URML intent → openTCS routing → VDA5050 (or vendor) comm-adapter → vehicle.

Verified surface (2026-06-01):
- [`openTCS/opentcs`](https://github.com/openTCS/opentcs): Fraunhofer IML, Issues enabled, not archived, active (last push 2026-05-26), ~510 stars. Java; kernel + control center + comm-adapter architecture.
- Ecosystem: `openTCS/opentcs-commadapter-vda5050` (a VDA5050 comm-adapter), tying openTCS to [RFC-0297](0297-vda5050-outreach.md).
- Origin: Germany (Fraunhofer IML); allied, default-policy pass.

URML's specific value above openTCS:
- **Natural-language and validated intent → transport orders.** A warehouse operator authors intent in plain language; URML compiles to validated primitives and submits openTCS transport orders, instead of hand-authoring order/route definitions.
- **Cross-robot static guarantees before dispatch.** openTCS routes and avoids collisions at runtime; URML adds a static pre-dispatch layer (`validate_fleet`, [RFC-0286](0286-multi-robot-fleet-addressing.md); geometric clearance, [RFC-0291](0291-utm-strategic-deconfliction.md)) that rejects ill-formed multi-AMR plans before they reach the kernel.
- **Fully open, offline stack.** openTCS + a VDA5050 comm-adapter + URML is an end-to-end open, on-premises path with no cloud dependency — matching URML's offline-after-validation posture.

## Detailed design (research-collab)

1. **Engage on `openTCS/opentcs`** with a documented URML → transport-order mapping, mirroring [RFC-0053](0053-open-rmf-multirobot-integration.md)'s task-source vector (URML compiles to a fleet-control system's task/order schema).
2. **If engagement signals interest**, ship an adapter/bridge that submits openTCS transport orders via the kernel API, with hermetic fake-kernel tests ([RFC-0073](0073-robotical-marty-outreach.md) pattern).
3. **Compose with [RFC-0297 (VDA5050)](0297-vda5050-outreach.md)**: document the full URML → openTCS → VDA5050 → vehicle stack as the open reference path.

### Proposed mapping (sketch)

| URML primitive | openTCS realisation |
|---|---|
| `move_to(named_location)` | A transport order with drive-to destinations at named points in the openTCS model. |
| `pick_from` / `place_at` | Transport-order operations at locations with the relevant location-type operations. |
| `wait_for(event)` | A dependent transport order or a kernel-side gate. |
| `dock(service: charge)` | A transport order to a charge location with a charge operation. |
| `report(status)` | Subscribe to kernel/vehicle state; append to a per-session log. |

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Java kernel surface.** openTCS is Java; URML's reference runtimes are Python. A bridge targets the kernel API (e.g. its web/RMI interface) across a language boundary; the RFC names this.
- **Model-binding.** openTCS requires a plant model (points, paths, locations); URML named locations must bind to model elements. The mapping assumes a pre-built model; the RFC scopes the order-submission side first.
- **License clarification.** The repository's license is one of the unresolved questions below.

## Alternatives considered

1. **Engage only Open-RMF and skip openTCS.** Rejected; openTCS is a distinct, widely deployed open control system with its own community and a VDA5050 comm-adapter; covering it completes the open-fleet-control picture alongside RMF and VDA5050.
2. **Add openTCS-specific primitives.** Rejected; RFC-0022's core twelve already express the intent. A transport-order-shaped primitive would be leaky.
3. **Ship a bridge before engaging.** Rejected; the kernel-API boundary and model-binding benefit from maintainer signal first.

## Prior art

- [`openTCS/opentcs`](https://github.com/openTCS/opentcs) (Fraunhofer IML) and `openTCS/opentcs-commadapter-vda5050`.
- [RFC-0297 (VDA5050)](0297-vda5050-outreach.md), [RFC-0298 (InOrbit ros_amr_interop)](0298-inorbit-ros-amr-interop-outreach.md), [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md): Move #21 interop siblings + orchestration peer.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md).
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): engagement → adapter + fake-substrate pattern.

## Unresolved questions

For the openTCS maintainers:

1. **Integration boundary.** Is the kernel API (web/RMI) the right surface for submitting URML-compiled transport orders?
2. **Model binding.** What is the recommended way to bind URML named locations to openTCS model points/locations?
3. **Adapter home.** URML repo, a contributed openTCS integration, or both?
4. **License.** What is the current license of `openTCS/opentcs`, for URML's `license_alignment` manifest field?
5. **VDA5050 path.** Is URML → openTCS → VDA5050 the recommended open end-to-end stack to document?
6. **Anything else.**

## Implementation note

RFC-0299 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

`openTCS/opentcs` has Issues enabled (verified 2026-06-01). URML's planned channel: open a single Issue pointing to this RFC.

This RFC and its accompanying outreach post are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Compose-above framing explicit (URML intent → openTCS transport orders → VDA5050 → vehicle).
- [x] Cross-robot static-validation differentiator surfaced (pre-dispatch validate_fleet vs runtime routing).
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] License left as an honest open question (gh did not surface an SPDX license).
- [x] Cross-link to RFC-0297/0298/0053 (siblings), RFC-0022/0286/0291, RFC-0073 (pattern).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, Java boundary, model-binding, license).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01.
- [x] Provenance `origin: DE`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
