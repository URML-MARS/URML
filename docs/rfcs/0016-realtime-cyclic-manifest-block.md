---
rfc: 0016
title: Real-time / cyclic timing declaration in the capability manifest
author: Ido Yahalomi (ido@jacob-ai.com)
state: Draft
created: 2026-05-19
updated: 2026-05-19
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

# RFC-0016: Real-time / cyclic timing declaration in the capability manifest

## Summary

Fieldbus and OPC UA substrates operate under a *cyclic timing
contract*: a fixed update period, a watchdog deadline, a requested
packet interval (RPI). The Layer-1 capability manifest has no way to
declare any of this, so a runtime cannot state — and the validator
cannot check — the timing regime a deployment runs under. This RFC is
filed as a **Draft for maintainer decision** by the spec-gap loop
(RFC-0014); the `urml-opcua-runtime` build surfaced it. It proposes an
optional `realtime:` declaration block. It is *not* a primitive and
makes no claim that URML enforces real-time guarantees.

## Motivation

An OPC UA Robotics cell is commissioned with a cyclic period and a
watchdog: violate the period and the cell faults to a safe state. Today
that fact lives only in deployment config (`opcua_adapter.yaml`),
invisible to URML. Two concrete consequences: (1) a manifest cannot
express "this cell is a 10 ms cyclic system with a 50 ms watchdog," so
a validator cannot warn when an envelope or a program's structure is
obviously incompatible with it; (2) two cells that differ only in
timing regime have identical manifests, so the manifest is not a
faithful description of the hardware — the thing Layer 1 exists to be.
This is a capability-declaration gap, not a behavior gap, which is why
it is a manifest-schema RFC and not a primitive.

## Detailed design

An optional block in the Layer-1 capability manifest:

```
realtime:
  cyclic_period_ms: <number>        # nominal control cycle
  watchdog_ms: <number>             # deadline before safe-state fault
  requested_packet_interval_ms: <number>   # optional, fieldbus RPI
  guarantee: best_effort | soft | hard     # honesty about the regime
```

`extra: forbid` as everywhere in Layer 1. Absent block ⇒ "unspecified
timing" (today's behavior, unchanged). `guarantee` is deliberately
explicit so a manifest cannot *imply* a hard-real-time promise URML
does not police.

### Spec changes

- **Layer 1**: add the optional `realtime` model to the capability
  manifest schema + spec section. No Layer 2/3/4 change — no primitive
  branches on timing.

### Validator changes

Schema parse only in v0.1 (the same staging RFC-0011/0013 used:
declare now, enforce later). A *future* RFC may add a Pass-3 check
("envelope dwell shorter than `watchdog_ms`"); v0.1 deliberately does
not, to keep this change small and honest about what is enforced.

### Reference runtime changes

None required. A runtime MAY read `realtime` to configure its substrate
session (the OPC UA adapter would map `requested_packet_interval_ms` to
its subscription) but is not obligated to in v0.1.

### Conformance suite changes

A manifest-acceptance fixture proving a `realtime`-bearing manifest
parses and validates; no execution semantics to test in v0.1.

## Backward compatibility

Fully compatible. Purely additive optional block; every existing
manifest is still valid. Pre-v1.0.

## Drawbacks

Declaring timing the validator does not enforce risks a reader assuming
enforcement — the same documented-vs-enforced hazard RFC-0011 called
out. Mitigation: the `guarantee` field and an explicit spec note that
v0.1 is parse-only. A deeper drawback: real-time systems are a deep
rabbit hole (jitter, priority, WCET) and a half-modeled `realtime`
block could invite scope creep toward guarantees URML should never
make. The block is intentionally four fields and explicitly
"description, not contract" to resist that; whether even that is too
much is a fair objection for review.

## Alternatives considered

1. **Leave it in deployment config (status quo).** Rejected: it makes
   the manifest an unfaithful description of the hardware and blocks
   any future timing-aware validation. But it is the conservative
   option and a legitimate "do nothing in v0.1" choice the maintainer
   may prefer.
2. **Put timing in the safety envelope, not the manifest.** Rejected:
   cyclic period/watchdog are *capabilities of the hardware*, not
   deployment safety choices; the envelope is the wrong home. (A future
   envelope rule may *reference* it.)
3. **A full real-time model (priorities, WCET, jitter).** Rejected as
   massive scope for v0.1; the four-field descriptive block is the
   minimum that makes the manifest faithful without overpromising.

## Prior art

EtherCAT/PROFINET cycle-time declarations; OPC UA PubSub publishing
interval & the Robotics companion-spec timing parameters; AUTOSAR
timing extensions; ROS 2 `rmw` QoS deadline. URML-internal: RFC-0006
(connectivity as an abstract declared capability — the model this
follows: declare the contract, don't implement the transport) and
RFC-0011 (the declare-now/enforce-later staging).

## Unresolved questions

- Whether `guarantee` belongs here or is over-engineering for v0.1.
- Whether `requested_packet_interval_ms` is OPC-UA-specific enough that
  it should be a generic `link` field instead.
- The eventual Pass-3 enforcement rule (explicitly out of scope here).

## Implementation note

Draft only — no code lands until the maintainer decides. The
`urml-opcua-runtime` ships with timing as deployment config in
`opcua_adapter.yaml` (unchanged) and does **not** read a manifest
`realtime` block, because none exists yet. If accepted, landing is a
single Layer-1-only change (schema + spec + one acceptance fixture) —
no multi-layer coordination, but still an RFC because it changes the
manifest schema.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). — N/A: this RFC adds no primitive; it is an optional Layer-1 manifest declaration only.
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
