---
rfc: 0312
title: EMQX (MQTT broker platform) integration, request for comment from EMQX maintainers
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

# RFC-0312: EMQX (MQTT broker platform) integration, request for comment from EMQX maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

EMQX is a high-scale, clustered MQTT broker used in large IoT and fleet deployments. As with Mosquitto (RFC-0311), URML composes above it as an MQTT client publishing validated intent. This RFC **requests review from the EMQX maintainers** and states the licensing boundary honestly. No spec change.

## Motivation

[`emqx/emqx`](https://github.com/emqx/emqx) (~16k stars, Issues + Discussions enabled, active, **not archived**, verified 2026-06-01) is the broker of choice when an MQTT deployment needs clustering and scale beyond a single Mosquitto instance. For URML, the relationship is identical to any MQTT broker: validated intent in, broker untouched. EMQX is the high-scale counterpart to the Mosquitto reference engagement.

### Licensing and provenance, stated up front

EMQX's broker is offered under a **Business Source License (BSL)** for parts of the platform (not a standard OSI license), and EMQ Technologies is **China-domiciled**. Neither blocks an at-arms-length client relationship: URML is an MQTT publisher and never embeds or redistributes EMQX. URML's US-federal default policy governs *deployed hardware provenance*, not which open communities URML requests comment from; engaging EMQX for feedback is consistent with prior non-US OSS engagements. The BSL and origin are recorded here so the relationship is unambiguous.

## Detailed design

### URML composes above EMQX

| URML concept | EMQX / MQTT concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | publish to an MQTT topic on the EMQX cluster | URML emits validated intent as MQTT messages. |
| Capability manifest (Layer 1) | topic namespace, QoS, cluster endpoint | A manifest declares the MQTT deployment shape. |

### What URML v0.1 does not yet express

1. The same MQTT transport/QoS declaration as RFC-0311. Spec RFC candidate (shared).

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- **BSL license** on the broker platform and **CN provenance**: recorded; integration stays at the MQTT-client boundary, so neither affects URML's Apache-2.0 tree.
- Overlaps the Mosquitto RFC (0311) at the MQTT-client layer; the post states the high-scale-clustering distinction.

## Alternatives considered

1. Cover MQTT with Mosquitto alone (RFC-0311). Rejected: EMQX serves the clustered/high-scale deployments Mosquitto does not, a distinct audience.
2. Skip on BSL grounds. Rejected: a client relationship does not touch the BSL terms; the engagement is a request for comment, not adoption.

## Prior art

- [`emqx/emqx`](https://github.com/emqx/emqx).
- Sibling [RFC-0311 (Mosquitto)](0311-mosquitto-outreach.md); [RFC-0297 (VDA5050-over-MQTT)](0297-vda5050-outreach.md).

## Unresolved questions

For the EMQX maintainers:

1. What grain should a URML manifest use to declare a clustered MQTT deployment (cluster endpoint, topic namespace, QoS)?
2. Is a validated-intent MQTT producer interesting to mention in robotics/fleet contexts, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`emqx/emqx` has Issues and Discussions enabled. URML's planned channel: a single Issue or Discussion pointing to this RFC, with the BSL/provenance note up front.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (BSL platform license, ~16k stars, Issues + Discussions, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (BSL, CN provenance, Mosquitto overlap); additive; no spec change.
- [x] Provenance: EMQ Technologies, CN. Client-boundary engagement only; default policy (hardware provenance) unaffected; recorded honestly.
- [x] CLAUDE.md compliance: URML is an MQTT client above the broker; no embedding; no commercial surface.
