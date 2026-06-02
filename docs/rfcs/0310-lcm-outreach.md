---
rfc: 0310
title: LCM (Lightweight Communications and Marshalling) integration, request for comment from lcm-proj maintainers
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

# RFC-0310: LCM (Lightweight Communications and Marshalling) integration, request for comment from lcm-proj maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

LCM is a low-latency message-passing and marshalling library born in the DARPA Urban Challenge and still used across robotics labs and platforms. URML composes above it: a validated URML intent serializes onto an LCM channel. This RFC **requests review from the lcm-proj maintainers**. LCM is LGPL-2.1, so the integration is strictly at the library boundary, with no vendoring of LCM into URML's Apache-2.0 tree. No spec change.

## Motivation

[`lcm-proj/lcm`](https://github.com/lcm-proj/lcm) (LGPL-2.1, ~1.2k stars, Issues enabled, active, **not archived**, verified 2026-06-01) is a robotics-native messaging system: a UDP multicast transport plus a type-specification language. It is a distinct transport from DDS and remains in active use on real platforms. URML's substrate-neutral stance treats LCM as a valid dispatch target.

## Detailed design

### URML composes above LCM

| URML concept | LCM concept | Relationship |
|---|---|---|
| Intent dispatch (Layer 2) | LCM publish on a channel | URML emits validated intent as an LCM message on a named channel. |
| Capability manifest (Layer 1) | LCM type definitions (.lcm) | A manifest can align with the deployment's LCM type set. |

### What URML v0.1 does not yet express

1. An LCM transport-substrate declaration (channel namespace, type-package) in the manifest. Spec RFC candidate; shared with the Move #22 transport set.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- **LGPL-2.1**: integration stays at the library boundary; URML never vendors LCM. Stated honestly.
- Smaller, slower-moving project than the DDS ecosystem; engagement may be light-touch.

## Alternatives considered

1. Skip LCM as legacy. Rejected: it is still deployed and is a clean example of URML's transport neutrality beyond DDS.
2. Cross-citation only. Rejected: the publisher relationship is concrete enough to ask.

## Prior art

- [`lcm-proj/lcm`](https://github.com/lcm-proj/lcm).
- Sibling Move #22 transport RFCs ([eCAL](0309-ecal-outreach.md), [Mosquitto](0311-mosquitto-outreach.md)); the Move #16 DDS spine.

## Unresolved questions

For the lcm-proj maintainers:

1. What grain should a URML manifest use to declare LCM as the deployment transport (channel namespace, type-package)?
2. Is a validated-intent producer on LCM channels interesting, or out of scope?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`lcm-proj/lcm` has Issues enabled. URML's planned channel: a single Issue pointing to this RFC, with the LGPL boundary stated up front.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (LGPL-2.1, ~1.2k stars, Issues enabled, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (LGPL boundary, project pace); additive; no spec change.
- [x] Provenance: lcm-proj community (US academic heritage); default policy passes.
- [x] CLAUDE.md compliance: library-boundary integration, no copyleft vendoring; composes above the transport.
