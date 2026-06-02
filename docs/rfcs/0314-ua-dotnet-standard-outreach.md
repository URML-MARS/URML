---
rfc: 0314
title: OPC Foundation UA-.NETStandard (OPC UA reference stack) integration, request for comment from OPC Foundation maintainers
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

# RFC-0314: OPC Foundation UA-.NETStandard (OPC UA reference stack) integration, request for comment from OPC Foundation maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

UA-.NETStandard is the OPC Foundation's own reference implementation of OPC UA, maintained by the standards body that also publishes the OPC UA Robotics companion specification. Engaging here reaches the standard itself, not just one implementation. URML composes above OPC UA as a validated-intent producer. This RFC **requests review from the OPC Foundation maintainers** and states the license boundary honestly. No spec change.

## Motivation

[`OPCFoundation/UA-.NETStandard`](https://github.com/OPCFoundation/UA-.NETStandard) (OPC Foundation reciprocal community license, "other"; ~2.3k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the canonical reference stack. The OPC Foundation stewards the OPC UA Robotics companion spec, which is the precise surface URML's manifesto names. The highest-leverage OPC UA conversation is with the standards body, alongside the open62541 engineering engagement (RFC-0313).

### Licensing, stated up front

The repository carries the **OPC Foundation reciprocal community license** (members-only redistribution terms, not a standard OSI license). URML's relationship is at-arms-length: URML maps intent onto the OPC UA protocol and never vendors or redistributes the reference stack. The license is recorded so the boundary is unambiguous.

## Detailed design

### URML composes above OPC UA (reference stack)

| URML concept | OPC UA concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | method call / variable write | URML validated intent maps onto OPC UA services. |
| Capability manifest (Layer 1) | OPC UA Robotics companion nodeset | A manifest can align with the robotics companion-spec types. |

### What URML v0.1 does not yet express

1. An OPC UA Robotics companion-spec mapping in the manifest. Spec RFC candidate (shared with RFC-0313).

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- **Reciprocal community license / standards-body cadence**: engagement may be formal and slower; integration stays at the protocol boundary.

## Alternatives considered

1. Engage only open62541 (RFC-0313). Rejected: the standards body owns the OPC UA Robotics companion spec URML wants to map; the reference stack is the right door to it.
2. Approach the OPC Foundation off-GitHub. Considered; the GitHub repo is the open public channel and the right first touch, with a foundation-level conversation to follow if directed.

## Prior art

- [`OPCFoundation/UA-.NETStandard`](https://github.com/OPCFoundation/UA-.NETStandard).
- Sibling [RFC-0313 (open62541)](0313-open62541-outreach.md), [RFC-0315 (Eclipse Milo)](0315-eclipse-milo-outreach.md), [RFC-0316 (opcua-asyncio)](0316-opcua-asyncio-outreach.md).

## Unresolved questions

For the OPC Foundation maintainers:

1. Is the OPC UA Robotics companion spec the right nodeset for a URML manifest to target, and is a mapping interesting to the Foundation?
2. Is the GitHub repo the right channel, or should this go to a working group?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`UA-.NETStandard` has Issues and Discussions enabled. URML's planned channel: a single Issue or Discussion pointing to this RFC, with the license/standards-body note up front.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (OPC Foundation RCL "other", ~2.3k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (RCL, standards-body cadence); additive; no spec change.
- [x] Provenance: OPC Foundation (international standards body, US-incorporated); default policy passes.
- [x] CLAUDE.md compliance: protocol-boundary engagement, no redistribution; advances the OPC UA Robotics substrate goal; no commercial surface.
