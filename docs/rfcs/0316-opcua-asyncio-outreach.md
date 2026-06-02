---
rfc: 0316
title: opcua-asyncio (Python OPC UA stack) integration, request for comment from FreeOpcUa maintainers
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

# RFC-0316: opcua-asyncio (Python OPC UA stack) integration, request for comment from FreeOpcUa maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

opcua-asyncio is the leading async Python OPC UA stack. It matters to URML specifically because URML's validator, LLM bridge, and tooling are Python; a Python OPC UA client is the most direct path from URML's reference tooling to a real OPC UA server. URML composes above it as a validated-intent producer. This RFC **requests review from the FreeOpcUa maintainers**. LGPL-3.0, so integration is at the library boundary, no vendoring. No spec change.

## Motivation

[`FreeOpcUa/opcua-asyncio`](https://github.com/FreeOpcUa/opcua-asyncio) (LGPL-3.0, ~1.4k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the actively maintained successor to python-opcua. Because URML's reference stack is Python, this is the implementation a URML OPC UA adapter prototype would most naturally use, alongside the C (open62541) and standards (UA-.NETStandard) engagements.

## Detailed design

### URML composes above opcua-asyncio

| URML concept | opcua-asyncio / OPC UA concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | async OPC UA `call_method` / `write` | URML validated intent maps onto OPC UA services from Python. |
| Reference tooling (Python) | Python OPC UA client | The shortest path from URML's Python validator/runtime to an OPC UA server. |

### What URML v0.1 does not yet express

1. The OPC UA Robotics companion mapping (shared with RFC-0313/0314/0315). Spec RFC candidate.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- **LGPL-3.0**: any URML adapter uses opcua-asyncio at the library boundary and does not vendor it. Stated honestly.

## Alternatives considered

1. Use only the C/.NET/Java stacks. Rejected: URML's tooling is Python; a Python client is the natural prototype path and worth its own request for comment.
2. Cross-citation only. Rejected: the prototype-path relationship is concrete.

## Prior art

- [`FreeOpcUa/opcua-asyncio`](https://github.com/FreeOpcUa/opcua-asyncio).
- Sibling OPC UA RFCs: [open62541](0313-open62541-outreach.md), [UA-.NETStandard](0314-ua-dotnet-standard-outreach.md), [Eclipse Milo](0315-eclipse-milo-outreach.md).

## Unresolved questions

For the FreeOpcUa maintainers:

1. Would a URML OPC UA adapter prototype built on opcua-asyncio be welcome to reference / list?
2. What grain should a URML manifest use to map onto an OPC UA address space from Python?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`opcua-asyncio` has Issues and Discussions enabled. URML's planned channel: a single Issue or Discussion pointing to this RFC, with the LGPL boundary stated up front.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (LGPL-3.0, ~1.4k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (LGPL boundary); additive; no spec change.
- [x] Provenance: FreeOpcUa community (INTL); default policy passes.
- [x] CLAUDE.md compliance: library-boundary integration, no copyleft vendoring; composes above OPC UA; no commercial surface.
