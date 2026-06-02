---
rfc: 0313
title: open62541 (open-source OPC UA stack) integration, request for comment from open62541 maintainers
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

# RFC-0313: open62541 (open-source OPC UA stack) integration, request for comment from open62541 maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

OPC UA is the dominant industrial interop protocol, and "OPC UA Robotics" is named as a target substrate in URML's manifesto. open62541 is the leading open C/C++ OPC UA stack. URML composes above it: a validated URML intent maps onto OPC UA method calls / variable writes against a server's address space. This RFC **requests review from the open62541 maintainers** and opens URML's first OPC UA engagement. MPL-2.0 on your side, Apache-2.0 on URML's; no spec change.

## Motivation

[`open62541/open62541`](https://github.com/open62541/open62541) (MPL-2.0, ~3.1k stars, Issues enabled, active, **not archived**, verified 2026-06-01) is the open stack most factory-floor and robotics-arm OPC UA deployments build on. URML has named OPC UA Robotics as a substrate since the manifesto but has not engaged it; open62541 is the cleanest engineering entry point, with a permissive MPL-2.0 license that composes with URML's Apache-2.0 tooling.

## Detailed design

### URML composes above open62541

| URML concept | open62541 / OPC UA concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | `Call` method / `Write` variable on the address space | URML validated intent maps onto OPC UA service calls. |
| Capability manifest (Layer 1) | server address space / nodeset, type definitions | A manifest can align with, or be derived from, the OPC UA nodeset. |
| `call_program` escape hatch | vendor OPC UA methods | Mirrors how URML already models opaque vendor programs on other substrates. |

### What URML v0.1 does not yet express

1. An OPC UA Robotics companion-spec mapping (the robotics nodeset) in the manifest. Spec RFC candidate; URML's first OPC UA Spec work.
2. A nodeset-to-manifest derivation. Unspecified.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only; the OPC UA Robotics nodeset mapping is a follow-up Spec RFC, not delivered here.
- URML has no OPC UA reference runtime yet; this RFC is the engagement that would shape one.

## Alternatives considered

1. Engage the OPC Foundation reference stack first. Addressed by the sibling RFC-0314 (UA-.NETStandard); open62541 is the cleanest open engineering surface and the natural lead for a permissive-license mapping.
2. Wait for an OPC UA runtime before engaging. Rejected: URML's pattern is to engage at the mapping stage and let maintainer signal shape the runtime.

## Prior art

- [`open62541/open62541`](https://github.com/open62541/open62541).
- Sibling Move #22 OPC UA RFCs: [UA-.NETStandard](0314-ua-dotnet-standard-outreach.md), [Eclipse Milo](0315-eclipse-milo-outreach.md), [opcua-asyncio](0316-opcua-asyncio-outreach.md).
- [RFC-0019 (AUTOSAR Adaptive substrate)](0019-autosar-adaptive-substrate.md) as prior non-ROS substrate work.

## Unresolved questions

For the open62541 maintainers:

1. What grain should a URML manifest use to map onto an OPC UA address space (nodeset import, method/variable subset)?
2. Is an English-to-validated-intent layer above OPC UA interesting for the robotics/industrial use of open62541?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`open62541/open62541` has Issues enabled. URML's planned channel: a single Issue pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (MPL-2.0, ~3.1k stars, Issues enabled, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (no runtime yet, follow-up Spec RFC); additive; no spec change.
- [x] Provenance: open62541 community (DE/EU heritage); default policy passes.
- [x] CLAUDE.md compliance: composes above OPC UA; advances the manifesto's OPC UA Robotics substrate goal; no commercial surface.
