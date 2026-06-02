---
rfc: 0306
title: rosbridge_suite (websocket robot bridge) integration, request for comment from RobotWebTools maintainers
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

# RFC-0306: rosbridge_suite (websocket robot bridge) integration, request for comment from RobotWebTools maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

URML turns an English sentence into a primitive, validates it against a robot's declared capabilities, then dispatches it. The most common way a browser or remote UI reaches a ROS robot today is `rosbridge_suite` over a websocket. This RFC proposes that URML's validated intent is a clean producer of rosbridge JSON, and **requests review from the RobotWebTools maintainers**. URML composes above rosbridge; it does not modify or fork it. Apache-2.0 on URML's side, BSD-3 on yours, no spec change.

## Motivation

[`RobotWebTools/rosbridge_suite`](https://github.com/RobotWebTools/rosbridge_suite) (BSD-3-Clause, ~1.2k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the de-facto websocket interface to ROS. It is exactly where a natural-language front end belongs: a user types or speaks an instruction, URML validates it, and the result is published as a rosbridge `publish` / `call_service` message. URML already validates before anything moves, which is the safety property a web-facing bridge most wants.

## Detailed design

### URML composes above rosbridge

| URML concept | rosbridge_suite concept | Relationship |
|---|---|---|
| Validated intent dispatch (Layer 2) | `publish` / `call_service` / `action` ops over websocket | URML emits rosbridge op messages after validation. |
| Natural-language layer (Layer 4) | (none today) | English-to-validated-intent as the web front door feeding rosbridge. |
| Capability manifest (Layer 1) | advertised topics/services/types | A manifest can be checked against, or derived from, the rosbridge type list. |

### What URML v0.1 does not yet express

1. A websocket/bridge transport declaration in the manifest (which substrate carries dispatch). Spec RFC candidate, not proposed here.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only; no code lands here.
- rosbridge is transport, not intent; the value is the producer relationship, which the maintainers may view as out of scope.

## Alternatives considered

1. Build a URML-specific web protocol. Rejected: rosbridge is the installed base; reusing it is the on-ethos, no-lock-in choice.
2. Cross-citation only. Rejected: the producer relationship is concrete enough to ask directly.

## Prior art

- [`RobotWebTools/rosbridge_suite`](https://github.com/RobotWebTools/rosbridge_suite).
- Sibling Move #22 RFCs: [RFC-0307 (webrtc_ros)](0307-webrtc-ros-outreach.md) and the transport / OPC UA / dialogue rows in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).
- Builds on the Move #16 DDS/transport spine (Fast DDS, Cyclone DDS, Zenoh) at the layer above the wire.

## Unresolved questions

For the RobotWebTools maintainers:

1. Is a validated natural-language producer of rosbridge messages interesting to mention or list, or out of scope for the project?
2. Would deriving a URML manifest from a rosbridge advertised-type list be useful, and at what grain?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`rosbridge_suite` has Issues and Discussions enabled. URML's planned channel: a single Issue (or Ideas Discussion) pointing to this RFC, framed as a request for comment.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (BSD-3, ~1.2k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives considered (two); drawbacks real; additive; no spec change.
- [x] Provenance: RobotWebTools community (US-led); default policy passes.
- [x] CLAUDE.md compliance: URML composes above the bridge, never embeds; no commercial surface.
