---
rfc: 0297
title: VDA5050 integration, request for comment from the VDA5050 standard maintainers
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

# RFC-0297: VDA5050 integration, request for comment from the VDA5050 standard maintainers

No spec change is proposed here. This is an Outreach RFC: it proposes a mapping from URML v0.1 to an existing target's interface, not a change to URML's normative surface. First Move #21 RFC; opens the warehouse / intralogistics AMR wave.

## Summary

URML proposes a documented mapping from its intent vocabulary onto **VDA5050**, the open interface standard for communication between a master control (fleet manager) and automated guided vehicles / autonomous mobile robots. A URML program describes warehouse intent ("take the pallet from staging to dock 4, then return to charge"); URML compiles to validated Layer-2 primitives; a future `VDA5050Adapter` (or master-control-side emitter) renders those primitives as VDA5050 `order` and `instantAction` messages on the standard's MQTT topics. URML composes **above** VDA5050, not against it: VDA5050 standardizes the vehicle interface, URML standardizes the human-and-machine-readable intent that produces VDA5050 orders. No spec change on URML's side. Engagement surface is [`VDA5050/VDA5050`](https://github.com/VDA5050/VDA5050) (Issues enabled).

## Motivation

VDA5050 (published by the German VDA / VDMA, vendor-neutral, widely adopted across European and global intralogistics) is the de-facto interoperability interface for mixed-vendor AMR fleets: one master control speaks VDA5050 to vehicles from many manufacturers. That is exactly the layer URML's warehouse domain profile ([RFC-0022](0022-warehouse-domain-profile.md)) was designed to sit above.

Verified surface (2026-06-01):
- [`VDA5050/VDA5050`](https://github.com/VDA5050/VDA5050): the canonical standard repository (JSON message schemas + protocol docs), Issues enabled, not archived, active (last push 2026-05-21), ~430 stars.
- Ecosystem URML can lean on: `ipa320/vda5050_msgs` (Fraunhofer IPA ROS 2 messages), `openTCS/opentcs` master-control with a VDA5050 comm-adapter ([RFC-0299](0299-opentcs-outreach.md)), `inorbit-ai/vda5050_adapter_examples` ([RFC-0298](0298-inorbit-ros-amr-interop-outreach.md)).
- Origin: Germany (VDA / VDMA); allied, default-policy pass.

URML's specific value above VDA5050:
- **Natural-language and validated intent that compiles to VDA5050 orders.** A warehouse operator writes intent in plain language; URML compiles it to validated primitives and emits VDA5050 `order` nodes/edges. The Layer-4 path is a ladder above hand-authoring order JSON.
- **Cross-robot static guarantees VDA5050 does not express.** VDA5050 is a per-vehicle interface; it does not statically check that two AMRs will not contend for the same aisle segment or that a handoff partner is declared. URML's `validate_fleet` ([RFC-0286](0286-multi-robot-fleet-addressing.md)) catches `fleet.concurrent_shared_workspace` and missing handoff `partner_ready` declarations, and geometric deconfliction ([RFC-0291](0291-utm-strategic-deconfliction.md)) checks clearance volumes, before any order is emitted.
- **Zero new vocabulary.** RFC-0022 already covers warehouse motion and manipulation with the core primitives (`move_to`, `pick_from`, `place_at`, `wait_for`, `dock`, `report`) — zero new primitives, zero manifest-schema fields, zero validator changes. A VDA5050 target needs no URML extension.

## Detailed design

URML's existing artifacts that feed a VDA5050 mapping:
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md), [RFC-0022](0022-warehouse-domain-profile.md) (warehouse profile), [`spec/profiles/warehouse/`](../../spec/profiles/warehouse/).
- [RFC-0053](0053-open-rmf-multirobot-integration.md): the two-vector bridge pattern (task-source + fleet-adapter) URML would mirror for VDA5050.
- `reference/mobile-runtime/` (`HuskyAdapter` / `JackalAdapter`, differential-drive bases) and `FleetRuntime` (`reference/ros2-runtime/src/urml_ros2_runtime/fleet.py`).

### Proposed mapping (sketch)

| URML primitive | VDA5050 realisation |
|---|---|
| `move_to(named_location)` | An `order` with `nodes` at declared map positions + connecting `edges`. Named locations map to VDA5050 node IDs. |
| `pick_from` / `place_at` | An `order` node carrying a load-handling `action` (vendor action set), at a declared station/dock. |
| `wait_for(event)` | A blocking `action` or a master-control-side gate keyed to a vehicle `state` field (e.g. handoff `partner_ready`). |
| `dock(service: charge)` | An `order` ending at a charge node with a `startCharging` action. |
| `report(status)` | Subscribe to the vehicle `state`/`connection` topics; append to a per-session log. |

The adapter targets VDA5050's MQTT topic structure (`order`, `instantActions`, `state`, `connection`, `factsheet`). Hermetic tests inject a fake MQTT broker (same fake-substrate pattern as [RFC-0073](0073-robotical-marty-outreach.md)).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: a proposed `VDA5050Adapter` in `reference/mobile-runtime/` (or a master-control-side emitter). Not built in this PR.
- Conformance: hermetic suite first (fake broker); hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Action sets are vendor-specific.** VDA5050 standardizes the envelope but leaves load-handling `actions` to each vendor; a URML `pick_from` maps to a vendor-declared action, not a universal one. The manifest declares the action set; the RFC names this honestly.
- **Master-control vs vehicle boundary.** URML naturally emits orders (master-control side). Driving an individual vehicle's VDA5050 client is a different integration; the RFC scopes the master-control-intent side first.
- **MQTT transport assumption.** VDA5050 rides MQTT; a URML deployment using the adapter needs broker connectivity. URML programs still validate fully offline; only dispatch needs the broker.

## Alternatives considered

1. **Map URML only to Open-RMF and ignore VDA5050.** Rejected; VDA5050 is the dominant vendor-facing vehicle interface in intralogistics, and many fleets speak it directly without RMF. Covering both ([RFC-0053](0053-open-rmf-multirobot-integration.md) + this) is the complete story.
2. **Add VDA5050-specific primitives to URML.** Rejected; RFC-0022 already covers the semantics with the core twelve. A leaky VDA5050-shaped primitive would violate substrate-neutrality.
3. **Ship a `VDA5050Adapter` before engaging.** Rejected; the master-control-vs-vehicle scoping and the action-set mapping benefit from maintainer signal first.

## Prior art

- [`VDA5050/VDA5050`](https://github.com/VDA5050/VDA5050) standard repository.
- [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md): the multi-robot orchestration sibling; RMF and VDA5050 are complementary (RMF can drive VDA5050 fleets).
- [RFC-0022 (warehouse profile)](0022-warehouse-domain-profile.md), [RFC-0286 (fleet addressing)](0286-multi-robot-fleet-addressing.md), [RFC-0291 (deconfliction)](0291-utm-strategic-deconfliction.md).
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the engagement → adapter-shipment + fake-substrate hermetic-test pattern.

## Unresolved questions

For the VDA5050 maintainers:

1. **Master-control-intent framing.** Is "URML compiles to VDA5050 `order` / `instantActions`" the right integration boundary, or is a vehicle-client-side mapping more useful to the community?
2. **Action-set conventions.** Is there a recommended convention for mapping a generic `pick_from` / `place_at` intent onto vendor action sets?
3. **Conformance lane.** Would a worked URML → VDA5050 example be welcome as a community contribution or referenced from the standard's docs?
4. **Relationship to Open-RMF.** Is the RMF-drives-VDA5050 path the expected multi-fleet orchestration story, and where does URML add the most value?
5. **Anything else.**

## Implementation note

RFC-0297 ships as a single RFC document PR. No adapter code in this PR. First Move #21 RFC. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

`VDA5050/VDA5050` has Issues enabled (verified 2026-06-01). URML's planned channel: open a single Issue pointing to this RFC.

This RFC and its accompanying outreach post are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Compose-above framing explicit (URML intent → VDA5050 orders), not a competing standard.
- [x] Cross-robot static-validation differentiator surfaced (validate_fleet + deconfliction vs per-vehicle VDA5050).
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] Cross-link to RFC-0053 (RMF sibling), RFC-0022/0286/0291, RFC-0073 (pattern), RFC-0298/0299 (Move #21 siblings).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, vendor action sets, master-control boundary, MQTT transport).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01.
- [x] Provenance `origin: DE`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
