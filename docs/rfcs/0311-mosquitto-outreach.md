---
rfc: 0311
title: Eclipse Mosquitto (MQTT broker) integration, request for comment from Eclipse Mosquitto maintainers
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

# RFC-0311: Eclipse Mosquitto (MQTT broker) integration, request for comment from Eclipse Mosquitto maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

MQTT is how a large share of fleet and IoT robotics actually moves messages, and Mosquitto is the reference open broker. URML already composes above MQTT indirectly through VDA5050 (RFC-0297, which rides MQTT); this RFC makes the broker relationship explicit and **requests review from the Eclipse Mosquitto maintainers**. URML publishes validated intent to MQTT topics; it does not modify the broker. No spec change.

## Motivation

[`eclipse-mosquitto/mosquitto`](https://github.com/eclipse-mosquitto/mosquitto) (EPL/EDL, ~10.9k stars, Issues enabled, active, **not archived**, verified 2026-06-01) is the de-facto open MQTT broker. URML's Move #21 warehouse work already emits VDA5050 orders over MQTT; naming the broker layer directly closes the loop for any URML deployment that dispatches over MQTT rather than DDS.

## Detailed design

### URML composes above Mosquitto

| URML concept | Mosquitto / MQTT concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | publish to an MQTT topic | URML emits validated intent as an MQTT message (e.g., VDA5050 order). |
| Capability manifest (Layer 1) | topic namespace, QoS | A manifest can declare the MQTT topic structure and QoS for the deployment. |
| Fleet interop (RFC-0297 VDA5050) | VDA5050-over-MQTT | Mosquitto is a concrete broker under the existing VDA5050 mapping. |

### What URML v0.1 does not yet express

1. An MQTT transport / QoS declaration in the manifest. Spec RFC candidate; complements the VDA5050 work.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- A broker is infrastructure, not robot-specific; the maintainers may see URML as just another MQTT client (which it is, by design).

## Alternatives considered

1. Leave MQTT implicit under VDA5050 (RFC-0297). Rejected: many URML deployments use MQTT without VDA5050; the broker deserves a direct mention.
2. Engage a different broker first. Addressed by the sibling EMQX RFC (0312); Mosquitto is the reference open broker and the natural lead.

## Prior art

- [`eclipse-mosquitto/mosquitto`](https://github.com/eclipse-mosquitto/mosquitto).
- [RFC-0297 (VDA5050)](0297-vda5050-outreach.md); sibling [RFC-0312 (EMQX)](0312-emqx-outreach.md).

## Unresolved questions

For the Eclipse Mosquitto maintainers:

1. What grain should a URML manifest use to declare an MQTT deployment (topic namespace, QoS, retained/LWT)?
2. Is a validated-intent MQTT producer worth a mention in MQTT-robotics contexts, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`mosquitto` has Issues enabled. URML's planned channel: a single Issue pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (EPL/EDL, ~10.9k stars, Issues enabled, active, isArchived: false).
- [x] Alternatives (two); drawbacks real; additive; no spec change.
- [x] Provenance: Eclipse Foundation (INTL); default policy passes.
- [x] CLAUDE.md compliance: URML is an MQTT client above the broker; no broker modification; no commercial surface.
