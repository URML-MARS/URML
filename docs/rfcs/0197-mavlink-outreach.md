---
rfc: 0197
title: MAVLink (Dronecode drone-protocol substrate) integration, request for comment from mavlink maintainers
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

# RFC-0197: MAVLink (drone-protocol substrate) integration

## Summary

URML does not yet ship a MAVLink-protocol manifest field or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the MAVLink protocol substrate over [`mavlink/mavlink`](https://github.com/mavlink/mavlink), and **requests review and feedback from the mavlink maintainers**. **License**: LGPL-3.0 with MIT generated-code exception — protocol-grammar at LGPL-3.0; generated code (`*_pb2`-equivalent) at MIT. The MIT generated-code exception makes the protocol-output layer URML-adapter-friendly while preserving copyleft on protocol modifications. No spec change.

This RFC pairs with [RFC-0196 (PX4-Autopilot)](0196-px4-autopilot-outreach.md) and [RFC-0198 (MAVSDK)](0198-mavsdk-outreach.md) on URML's drone-substrate engagement. PX4 is the autopilot; MAVLink is the protocol; MAVSDK is the high-level SDK. Same governance org (Linux Foundation Dronecode Foundation).

## Motivation

MAVLink is the foundation-governed drone communication protocol. Used by PX4, ArduPilot, and dozens of compatible autopilots; the de facto wire format between autopilot and ground station + companion-computer + telemetry. Repo at [`mavlink/mavlink`](https://github.com/mavlink/mavlink) (LGPL-3.0 + MIT generated-code exception, 2.3k stars, Issues enabled, last commit `2026-05-28` daily activity, **not archived**).

URML benefits from documenting the MAVLink manifest mapping because:

1. **MAVLink is URML's drone-control protocol class.** URML's drone-adapter dispatches via MAVLink for ROS 2 ↔ autopilot ↔ ground-station message flows. The manifest declares MAVLink as the active protocol substrate.
2. **Protocol-version + dialect declaration matters for compatibility.** MAVLink v1 / v2, plus dialects (common, ardupilotmega, ASLUAV, etc.) determine which messages a deployment can send/receive. URML's manifest cannot today declare this.
3. **LGPL-3.0 with MIT generated-code exception is structurally URML-compatible.** URML's Apache-2.0 adapter pattern composes with MAVLink's generated message code at the MIT-licensed boundary. The protocol-grammar LGPL preserves copyleft on protocol modifications; URML doesn't modify protocols, so the LGPL-grammar layer is at-arm's-length.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mavlink_protocol_cell.yaml` fixture)

`protocol` block:

| URML field | Maps to MAVLink attribute |
|---|---|
| `protocol.class: custom` (`mavlink`) | Declares MAVLink as the drone-control protocol substrate |
| `protocol.mavlink_version` | `mavlink_v1` / `mavlink_v2` |
| `protocol.dialect` | `common` / `ardupilotmega` / `ASLUAV` / etc. — declares which dialect's message set is active |
| `protocol.signing` | MAVLink 2 message signing flag (security relevant) |
| `protocol.system_id` + `protocol.component_id` | MAVLink addressing (per RFC-0008 drone profile) |
| `protocol.transport` | UDP / TCP / serial / radio-link transport class |

### What URML v0.1 does not yet express for MAVLink

1. **Protocol-substrate declaration.** URML's v0.1 has no `protocol.class: mavlink` declaration. Spec RFC queued (sibling to RFC-0199 DroneCAN as alternate-protocol declaration).
2. **MAVLink dialect declaration.** URML's manifest cannot today declare which dialect's message set governs the deployment — `common` is universal; `ardupilotmega` adds ArduPilot-specific messages; `ASLUAV` adds ETH Zurich research messages.
3. **Message-signing declaration.** MAVLink 2's signing capability is security-relevant for adversarial deployments; URML's manifest has no first-class field.
4. **Multi-system topology declaration.** MAVLink's system-ID + component-ID addressing supports multi-vehicle / multi-component deployments; URML's manifest cannot today declare such topologies.

### Compatibility notes

- **Vendor / foundation.** [`mavlink`](https://github.com/mavlink) — Linux Foundation Dronecode Foundation governance.
- **Flagship repo.** [`mavlink/mavlink`](https://github.com/mavlink/mavlink) — LGPL-3.0 with MIT generated-code exception, 2.3k stars, Issues enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** Dronecode Foundation (multi-national; foundation governance neutral). Passes US-federal default policy.
- **License fit.** LGPL-3.0 + MIT generated-code exception. The MIT-exception generated-code surface composes cleanly with URML's Apache-2.0 adapter pattern; protocol-grammar copyleft is at-arm's-length.
- **Maintainer signal.** Daily activity; foundation-direct; the standard drone communication protocol.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; protocol-substrate + MAVLink-dialect + message-signing + multi-system-topology declaration Spec RFCs queued.
- Reference runtime: future `reference/drone-runtime/MavlinkAdapter` is a candidate; composes via the MIT-licensed generated-code surface.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **LGPL-grammar at-arm's-length distinction is novel manifest territory.** URML's manifest hasn't yet declared LGPL-with-generated-code-exception license boundary semantics.
- **Multiple Spec-RFC prerequisites** (protocol substrate, dialect, signing, multi-system topology).
- **MAVLink 1 vs 2 compatibility matrix** — URML's manifest needs to declare version compatibility for downstream operator awareness.

## Alternatives considered

1. **Engage Dronecode Foundation as a single substrate-family RFC** covering PX4 / MAVLink / MAVSDK / QGroundControl. Rejected. Per-project engagement is the cleaner shape; each project has distinct maintainer audiences and engagement contexts.
2. **Skip MAVLink protocol-level engagement and engage only at the SDK layer (MAVSDK RFC-0198).** Rejected. Protocol declaration matters for low-level / embedded URML deployments that don't use MAVSDK.
3. **Bundle MAVLink + DroneCAN into one drone-protocol RFC.** Rejected. Per-protocol RFCs let conversation thread per maintainer community; the protocol-substrate Spec RFC is the shared piece.

## Prior art

- [`mavlink/mavlink`](https://github.com/mavlink/mavlink) — the upstream protocol spec.
- [RFC-0196 (PX4-Autopilot)](0196-px4-autopilot-outreach.md) — sibling Move-16 autopilot RFC; PX4 communicates via MAVLink.
- [RFC-0198 (MAVSDK)](0198-mavsdk-outreach.md) — sibling Move-16 SDK-layer RFC built on MAVLink.
- [RFC-0199 (DroneCAN)](0199-dronecan-libcanard-outreach.md) — sibling Move-16 alternate-protocol RFC.
- [RFC-0208 (QGroundControl)](0208-qgroundcontrol-outreach.md) — sibling Move-16 operator-UI RFC; QGC communicates with autopilots via MAVLink.

## Unresolved questions

For the mavlink maintainers:

1. **Protocol-substrate manifest fields.** URML's v0.1 has no `protocol.class: mavlink` declaration. Spec RFC queued. Manifest field expectations from the MAVLink perspective?
2. **Dialect declaration.** Should URML's manifest declare the active MAVLink dialect (common / ardupilotmega / ASLUAV / custom), and at what granularity?
3. **Message-signing declaration.** MAVLink 2's signing capability is security-relevant; manifest field shape?
4. **Multi-system topology declaration.** Manifest fields for system-ID + component-ID multi-vehicle / multi-component deployments?
5. **LGPL-with-MIT-generated-code-exception license-class declaration.** Should URML's manifest declare this license-boundary class for downstream operator awareness?
6. **Adapter home.** URML repo (`reference/drone-runtime/MavlinkAdapter`), MAVLink-maintained `mavlink/mavlink-urml-bridge`, or both?
7. **Conformance listing.** Would the MAVLink maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
8. **Anything else.**

## Implementation note

RFC-0197 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`mavlink/mavlink` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (LGPL-3.0 + MIT generated-code exception, 2.3k stars, Issues enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (LGPL-at-arm's-length distinction novel, multiple Spec-RFC prerequisites, version compatibility matrix).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation Dronecode (foundation-direct, multi-national); default policy passes.
- [x] CLAUDE.md compliance check passed.
