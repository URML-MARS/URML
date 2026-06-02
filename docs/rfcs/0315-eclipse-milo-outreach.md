---
rfc: 0315
title: Eclipse Milo (Java OPC UA stack) integration, request for comment from Eclipse Milo maintainers
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

# RFC-0315: Eclipse Milo (Java OPC UA stack) integration, request for comment from Eclipse Milo maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

Eclipse Milo is the leading open Java OPC UA stack, common in JVM-based industrial integration. As with open62541 (C) and UA-.NETStandard (.NET), URML composes above it: validated URML intent maps onto OPC UA service calls. This RFC **requests review from the Eclipse Milo maintainers**, covering the JVM corner of URML's OPC UA engagement. No spec change.

## Motivation

[`eclipse-milo/milo`](https://github.com/eclipse-milo/milo) (EPL-2.0, ~1.4k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the OPC UA stack JVM integrators reach for, and it sits in the Eclipse ecosystem URML already engages (Cyclone DDS, iceoryx, eCAL, Mosquitto). The same OPC UA mapping URML proposes to open62541 applies through Milo for Java deployments.

## Detailed design

### URML composes above Milo

| URML concept | Milo / OPC UA concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | OPC UA method call / write via Milo client | URML validated intent maps onto OPC UA services. |
| Capability manifest (Layer 1) | address space / companion nodeset | A manifest aligns with the OPC UA nodeset. |

### What URML v0.1 does not yet express

1. The OPC UA Robotics companion-spec mapping (shared with RFC-0313 / RFC-0314). Spec RFC candidate.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- Overlaps the other OPC UA RFCs at the protocol layer; the post states the JVM-implementation distinction.

## Alternatives considered

1. Cover OPC UA with open62541 + UA-.NETStandard only. Rejected: Milo is the JVM stack; covering C, .NET, Java, and Python (opcua-asyncio) lets the mapping be validated across the implementations integrators actually use.
2. Cross-citation only. Rejected: Milo is in URML's Eclipse engagement cluster; a direct request for comment is warranted.

## Prior art

- [`eclipse-milo/milo`](https://github.com/eclipse-milo/milo).
- Sibling OPC UA RFCs: [open62541](0313-open62541-outreach.md), [UA-.NETStandard](0314-ua-dotnet-standard-outreach.md), [opcua-asyncio](0316-opcua-asyncio-outreach.md). Eclipse-ecosystem siblings: Cyclone DDS / iceoryx (Move #16), [eCAL](0309-ecal-outreach.md), [Mosquitto](0311-mosquitto-outreach.md).

## Unresolved questions

For the Eclipse Milo maintainers:

1. What grain should a URML manifest use to map onto an OPC UA address space via Milo?
2. Is an English-to-validated-intent layer above Milo interesting for JVM industrial integration, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`eclipse-milo/milo` has Issues and Discussions enabled. URML's planned channel: a single Issue or Discussion pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (EPL-2.0, ~1.4k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (cross-implementation overlap); additive; no spec change.
- [x] Provenance: Eclipse Foundation (INTL); default policy passes.
- [x] CLAUDE.md compliance: composes above OPC UA; no embedding; no commercial surface.
