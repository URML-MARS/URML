---
rfc: 0506
title: libcyphal (Cyphal) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0506: libcyphal (Cyphal) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`OpenCyphal-Garage/libcyphal`](https://github.com/OpenCyphal-Garage/libcyphal) (MIT, ~320 stars, active) is the portable C++ reference implementation of the Cyphal protocol stack for embedded and Linux nodes (the UAVCAN successor, common over CAN). URML is a layer well above a wire protocol: it validates intent against a capability manifest and dispatches to a substrate. Cyphal is one of the low-level transports a validated actuation command ultimately rides. This RFC asks whether the seam is worth describing.

## The mapping (URML beside Cyphal)

- **Below URML's Layer 1.** URML's Layer-1 hardware abstraction sits above the bus. A validated URML actuation command, once it has passed the capability/envelope check, reaches an actuator node over a transport like Cyphal. URML does not replace the bus; it is the typed, statically-validated intent above it.
- **Cyphal data types toward a manifest.** Cyphal's registered, typed interfaces (subjects/services with versioned DSDL types) are a clean, declarative source a URML capability manifest could reference for what a node actually exposes.

## What is asked

Request for comment from the OpenCyphal maintainers:

1. Is "URML validates intent, then dispatches to a Cyphal node" a sensible description of the layering (intent above, bus below)?
2. Could Cyphal's typed DSDL interfaces inform a URML capability manifest for an actuator node?
3. Which is the cleaner first seam, and is this even the right altitude to engage (protocol vs integrator)?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-1 hardware abstraction and the substrate-transport engagements (Move #16 / #22: DDS, Zenoh, micro-ROS, eCAL — URML composes above the transport). Part of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `OpenCyphal-Garage/libcyphal` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
