---
rfc: 0199
title: DroneCAN (alternate CAN-protocol substrate for drone embedded networks) integration, request for comment from dronecan maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0199: DroneCAN (alternate CAN-protocol substrate) integration

## Summary

URML does not yet ship a DroneCAN manifest field or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the DroneCAN protocol substrate — the open CAN-bus standard for drone embedded networks — over [`dronecan/libcanard`](https://github.com/dronecan/libcanard) (MIT), and **requests review and feedback from the DroneCAN community maintainers**. No spec change.

DroneCAN is the **alternate protocol substrate to MAVLink** (RFC-0197). Where MAVLink is the serial / UDP / radio-link protocol between autopilot and ground station / companion computer, DroneCAN is the CAN-bus protocol for embedded drone networks (motor controllers, GPS, magnetometer, airspeed sensors, gimbals). URML's manifest declares which protocol class is active per layer of the deployment.

## Motivation

DroneCAN (founded 2017 as the successor to UAVCAN v0) is the open CAN-protocol standard for drone embedded networks. Maintained by the DroneCAN community; used by PX4 + ArduPilot + Pixhawk-family autopilots for sensor + actuator + peripheral communication over CAN. Repo at [`dronecan/libcanard`](https://github.com/dronecan/libcanard) (MIT, 98 stars, Issues enabled, last commit `2026-04-30`, **not archived**).

URML benefits from documenting the DroneCAN manifest mapping because:

1. **CAN-bus embedded networks are structurally different from MAVLink links.** MAVLink is autopilot ↔ companion ↔ ground-station; DroneCAN is autopilot ↔ embedded sensors / actuators / peripherals over CAN. URML's manifest declares both protocol classes independently.
2. **Pixhawk-family autopilots use DroneCAN for peripheral integration.** GPS receivers, ESCs, magnetometers commonly speak DroneCAN; URML's manifest declares the active embedded-protocol class.
3. **MIT-licensed libcanard composes cleanly with URML's Apache-2.0 adapter stance.** Cleanest license posture across Move-16's drone-autopilot sub-category.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `dronecan_embedded_network_cell.yaml` fixture)

`protocol` block:

| URML field | Maps to DroneCAN attribute |
|---|---|
| `protocol.embedded_class: custom` (`dronecan`) | Declares DroneCAN as the embedded-network protocol substrate |
| `protocol.dronecan_version` | DroneCAN protocol version |
| `protocol.node_ids` | List of DroneCAN node identifiers in the deployment |
| `protocol.dsdl_dialect` | DroneCAN DSDL message-set declaration |
| `protocol.transport: can_fd` / `can_classic` | CAN-FD vs classic CAN declaration (relevant for high-bandwidth deployments) |

### What URML v0.1 does not yet express for DroneCAN

1. **Embedded-network protocol-substrate declaration.** URML's v0.1 has no `protocol.embedded_class` field. Spec RFC queued (companion to RFC-0197 MAVLink at the embedded-network layer).
2. **DSDL dialect declaration.** DroneCAN's DSDL (Data Structure Description Language) defines per-deployment message sets; URML's manifest cannot today declare which DSDL dialect is active.
3. **Multi-node topology declaration.** DroneCAN deployments often have 5-20 nodes (GPS + multiple ESCs + magnetometer + airspeed + etc.); URML's manifest cannot today declare embedded-network topology.
4. **CAN-FD vs classic CAN substrate declaration.** Bandwidth-relevant for high-throughput sensor deployments.

### Compatibility notes

- **Community / org.** [`dronecan`](https://github.com/dronecan) — DroneCAN community open-standard (successor to UAVCAN v0).
- **Flagship repo.** [`dronecan/libcanard`](https://github.com/dronecan/libcanard) — MIT, 98 stars, Issues enabled, last commit 2026-04-30, **not archived**.
- **Origin.** Community open-standard (multi-national); no vendor-domiciled gating. Passes US-federal default policy.
- **License fit.** MIT is the cleanest license posture across Move-16's drone-autopilot sub-category.
- **Maintainer signal.** Community-maintained; active on monthly cadence; small star count reflects embedded-protocol niche (vs MAVLink's broader autopilot-ground-station audience).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; embedded-network protocol substrate + DSDL dialect + multi-node topology + CAN-FD declaration Spec RFCs queued.
- Reference runtime: future `reference/drone-runtime/DroneCanAdapter` is a candidate at the embedded-network substrate layer; complements MAVLink-layer adapter at the autopilot-ground-station layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Embedded-network protocol declaration is novel manifest territory.**
- **Multiple Spec-RFC prerequisites** (embedded substrate, DSDL dialect, multi-node topology, CAN-FD).
- **Niche audience.** DroneCAN's 98 stars vs MAVLink's 2.3k reflects the embedded-protocol specialization; engagement may be lower-velocity than sibling Move-16 Dronecode targets.

## Alternatives considered

1. **Skip DroneCAN as too niche.** Rejected. CAN-bus embedded networks are structurally distinct from MAVLink protocol; URML's manifest cannot represent both layers without declaring DroneCAN explicitly.
2. **Engage UAVCAN v1 / Cyphal upstream (DroneCAN's successor protocol).** Considered. DroneCAN remains the dominant deployment (Pixhawk-family adoption); Cyphal engagement is future work as adoption matures.
3. **Bundle DroneCAN with MAVLink into one drone-protocol RFC.** Rejected. Per-protocol engagement is the cleaner shape; the embedded-vs-autopilot layer distinction matters operationally.

## Prior art

- [`dronecan/libcanard`](https://github.com/dronecan/libcanard) — the upstream library.
- [RFC-0197 (MAVLink)](0197-mavlink-outreach.md) — sibling Move-16 protocol RFC at the autopilot-ground-station layer.
- [RFC-0196 (PX4-Autopilot)](0196-px4-autopilot-outreach.md) — sibling Move-16 autopilot RFC; PX4 communicates with DroneCAN peripherals on the embedded-network side.

## Unresolved questions

For the DroneCAN community maintainers:

1. **Embedded-network protocol-substrate manifest fields.** URML's v0.1 has no `protocol.embedded_class` declaration. Spec RFC queued. Manifest field expectations from the DroneCAN perspective?
2. **DSDL dialect declaration.** Should URML's manifest declare which DSDL dialect is active, and at what granularity?
3. **Multi-node topology declaration.** Manifest fields for declaring the embedded-network topology (node IDs, message subscriptions, redundancy schemes)?
4. **CAN-FD vs classic CAN substrate declaration.** Useful manifest field for high-bandwidth deployment awareness?
5. **UAVCAN v1 / Cyphal migration path.** Should URML's manifest declare migration-path posture for deployments transitioning between DroneCAN and Cyphal?
6. **Adapter home.** URML repo (`reference/drone-runtime/DroneCanAdapter`), DroneCAN-community-maintained `dronecan/dronecan-urml-bridge`, or external?
7. **Conformance listing.** Would the DroneCAN community consider a README link to URML's compatible-runtimes registry once a working adapter ships?
8. **Anything else.**

## Implementation note

RFC-0199 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml). **Completes the Move-16 Batch 1 drone-autopilot + protocol sub-category.**

## How to respond

`dronecan/libcanard` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 98 stars, Issues enabled, last commit 2026-04-30, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (embedded-network declaration novel, niche audience, multiple Spec-RFC prerequisites).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: DroneCAN community open-standard (multi-national); default policy passes.
- [x] CLAUDE.md compliance check passed.
