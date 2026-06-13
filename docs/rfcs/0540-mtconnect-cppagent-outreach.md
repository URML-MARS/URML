---
rfc: 0540
title: MTConnect (cppagent) integration — request for comment
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

# RFC-0540: MTConnect (cppagent) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48). MTConnect is a US manufacturing-interop **standards body**.

## Summary

[`mtconnect/cppagent`](https://github.com/mtconnect/cppagent) (Apache-2.0, active, MTConnect Institute / AMT) is the reference C++ agent for MTConnect, the US manufacturing interoperability standard for reading data off machine tools and equipment. URML's relationship is at the data / interop boundary: MTConnect reports equipment state; URML declares and validates intent for a robot that operates alongside that equipment. This RFC asks whether describing the seam is useful (and complements URML's OPC UA work without re-touching it).

## The mapping (URML beside MTConnect)

- **Equipment state as a fact intent conditions on.** An MTConnect agent reports machine state (availability, mode, condition). A URML program for a robot in that cell can condition a typed intent on that state, validated against the robot's capabilities and a safety envelope before dispatch. URML consumes the equipment data as a fact; it does not replace MTConnect.
- **Standards-to-standards.** URML (robot intent) and MTConnect (equipment data) are complementary standards at the shop-floor; naming the boundary helps an integrator compose them.

## What is asked

Request for comment from the MTConnect maintainers:

1. Is "MTConnect reports equipment state, a URML robot intent conditions on it" a sensible interop boundary on a shop floor?
2. Is there value in a documented URML-beside-MTConnect pattern for robot-plus-machine cells?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's industrial profile, the OPC UA Robotics engagements (Move #22: open62541, UA-.NETStandard, Milo, opcua-asyncio), and the decide-then-do split (RFC-0002). Part of Move #48; a manufacturing-interop standards body.

## Implementation note

Outreach only. The post is a GitHub Issue on `mtconnect/cppagent` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
