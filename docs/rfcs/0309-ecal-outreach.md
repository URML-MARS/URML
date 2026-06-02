---
rfc: 0309
title: eCAL (Eclipse enhanced Communication Abstraction Layer) integration, request for comment from Eclipse eCAL maintainers
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

# RFC-0309: eCAL (Eclipse enhanced Communication Abstraction Layer) integration, request for comment from Eclipse eCAL maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

eCAL is a high-performance pub/sub middleware widely used in automotive and robotics, sitting beside DDS as a transport choice. URML composes above the transport: a validated URML intent can be published on an eCAL topic exactly as it can on DDS. This RFC **requests review from the Eclipse eCAL maintainers**. Apache-2.0 on both sides; no spec change.

## Motivation

[`eclipse-ecal/ecal`](https://github.com/eclipse-ecal/ecal) (Apache-2.0, ~1k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is a mature inter-process / inter-host pub/sub layer with a strong automotive-robotics user base. URML's Move #16 covered DDS implementations; eCAL is a distinct, equally-valid transport under URML's substrate-neutral stance, and the clean Apache-2.0 license composes without friction.

## Detailed design

### URML composes above eCAL

| URML concept | eCAL concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | eCAL publisher / subscriber, services | URML emits validated intent on eCAL topics/services. |
| Capability manifest (Layer 1) | eCAL topic/type registry (monitoring) | A manifest can align with the eCAL registry for the deployment. |
| Substrate neutrality | eCAL as one transport among DDS, Zenoh, ... | URML treats eCAL as a first-class substrate, not a special case. |

### What URML v0.1 does not yet express

1. A transport-substrate declaration distinguishing eCAL from DDS/Zenoh in the manifest. Spec RFC candidate; shared with the Move #16 transport work.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- eCAL is transport; the manifest substrate-declaration that would make this concrete is a follow-up Spec RFC.

## Alternatives considered

1. Treat eCAL as covered by the Move #16 DDS work. Rejected: eCAL is a separate project and transport with its own maintainers.
2. Cross-citation only. Rejected: the publisher relationship is concrete; a direct request for comment is warranted.

## Prior art

- [`eclipse-ecal/ecal`](https://github.com/eclipse-ecal/ecal).
- Move #16 transport spine (Fast DDS, Cyclone DDS, Zenoh, iceoryx); sibling Move #22 transport RFCs ([LCM](0310-lcm-outreach.md), [Mosquitto](0311-mosquitto-outreach.md)).

## Unresolved questions

For the Eclipse eCAL maintainers:

1. What is the most useful grain for a URML manifest to declare eCAL as the deployment transport?
2. Is a validated-intent producer on eCAL topics interesting to mention or list?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`eclipse-ecal/ecal` has Issues and Discussions enabled. URML's planned channel: a single Issue or Discussion pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (Apache-2.0, ~1k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real; additive; no spec change.
- [x] Provenance: Eclipse Foundation / Continental heritage (DE/EU); default policy passes.
- [x] CLAUDE.md compliance: composes above the transport; reinforces substrate neutrality; no commercial surface.
