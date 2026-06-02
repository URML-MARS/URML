---
rfc: 0308
title: micro-ROS (MCU-class ROS 2 over micro-XRCE-DDS) integration, request for comment from micro-ROS maintainers
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

# RFC-0308: micro-ROS (MCU-class ROS 2 over micro-XRCE-DDS) integration, request for comment from micro-ROS maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

micro-ROS puts ROS 2 on microcontrollers over the micro-XRCE-DDS wire protocol. URML already has a micro-class robot story (the `microbit_edu` manifest, RFC-0018, and the educational profile, RFC-0011); micro-ROS is the substrate that carries that intent down to a real MCU agent. This RFC **requests review from the micro-ROS maintainers** and extends the Move #16 DDS spine to the MCU tier. URML composes above micro-ROS; no spec change.

## Motivation

[`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup) (Apache-2.0, ~494 stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) brings the ROS 2 graph to MCUs via a micro-ROS Agent bridging micro-XRCE-DDS to DDS. URML's Move #16 engaged the full-fat DDS layer (Fast DDS, Cyclone DDS); micro-ROS is the same story one tier down, where URML's educational and embedded manifests actually live. The wire protocol, [`eProsima/Micro-XRCE-DDS`](https://github.com/eProsima/Micro-XRCE-DDS) (Apache-2.0), is maintained by eProsima, already engaged via Fast DDS in Move #16; this RFC cross-cites rather than re-pitches that vendor.

## Detailed design

### URML composes above micro-ROS

| URML concept | micro-ROS concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | micro-ROS pub/sub/service on the MCU | URML validated intent reaches the MCU via the micro-ROS Agent. |
| Capability manifest (Layer 1) | MCU resource profile + entities | A manifest declares the MCU-tier substrate; refines the `microbit_edu` pattern. |
| Educational profile (RFC-0011) | classroom MCU platforms | The conservative defaults map directly onto MCU-class robots. |

### What URML v0.1 does not yet express

1. An MCU-transport substrate class (micro-XRCE-DDS / agent topology) in the manifest. Spec RFC candidate; sibling to the Move #16 DDS declarations.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- The interesting work (an MCU-transport manifest class) is a follow-up Spec RFC, not delivered here.

## Alternatives considered

1. Fold into the Move #16 DDS RFCs. Rejected: the MCU tier (resource limits, agent topology) is a distinct substrate and a distinct maintainer group.
2. Engage eProsima Micro-XRCE-DDS directly instead. Rejected: micro-ROS is the community-facing surface; the wire protocol is cross-cited.

## Prior art

- [`micro-ROS/micro_ros_setup`](https://github.com/micro-ROS/micro_ros_setup), [`eProsima/Micro-XRCE-DDS`](https://github.com/eProsima/Micro-XRCE-DDS).
- [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-capability-subset.md), [RFC-0011 (educational profile)](0011-educational-profile.md); the Move #16 DDS spine (Fast DDS / Cyclone DDS).

## Unresolved questions

For the micro-ROS maintainers:

1. What grain should a URML manifest use to declare the MCU-tier substrate (just naming micro-ROS, or the agent topology and transport)?
2. Does an English-to-validated-intent layer above micro-ROS interest you for classroom / embedded on-ramps?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`micro_ros_setup` has Issues and Discussions enabled. URML's planned channel: a single Issue or Ideas Discussion pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (Apache-2.0, ~494 stars, Issues + Discussions, active, isArchived: false; Micro-XRCE-DDS Apache-2.0).
- [x] Alternatives (two); drawbacks real; additive; no spec change.
- [x] Provenance: micro-ROS community consortium (EU-led, OFERA/Bosch heritage); default policy passes.
- [x] CLAUDE.md compliance: composes above the substrate; extends the substrate-neutral story to MCUs; no commercial surface.
