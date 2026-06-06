---
rfc: 0016
title: Real-time / cyclic timing declaration in the capability manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-19
updated: 2026-06-06
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
cannot check — the timing regime a deployment runs under. Surfaced by the
spec-gap loop (RFC-0014) from the `urml-opcua-runtime` build, this RFC adds
an optional `realtime:` declaration block. It is *not* a primitive and makes
no claim that URML enforces real-time guarantees.

**State: Implemented** (2026-06-06). Ships the schema block, a validator
*internal-coherence* check (`watchdog_ms >= cyclic_period_ms` — a watchdog
shorter than one cycle is incoherent), conformance fixtures, and unit tests.
The maintainer chose to mature the original parse-only v0.1 scope with that
one coherence rule, which checks the declaration without asserting any
real-time guarantee. The envelope-dwell Pass-3 enforcement rule remains
explicitly deferred.

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

One Pass-2 **internal-coherence** check ships: `watchdog_ms >=
cyclic_period_ms` (`capability.watchdog_shorter_than_cycle`). A watchdog
shorter than one control cycle would fault before a cycle completes, so it is
an incoherent declaration regardless of the real-time regime. This checks the
declaration's self-consistency; it is *not* real-time enforcement. The Pass-3
*envelope-dwell* rule ("envelope hold shorter than `watchdog_ms`") remains a
future RFC, deliberately deferred to keep this change honest about what is
enforced.

### Reference runtime changes

None required. A runtime MAY read `realtime` to configure its substrate
session (the OPC UA adapter would map `requested_packet_interval_ms` to
its subscription) but is not obligated to in v0.1.

### Conformance suite changes

Two fixtures ship: a positive (`home/realtime_cyclic_positive`, a coherent
`realtime`-bearing manifest parses and validates) and a negative
(`home/realtime_watchdog_short_rejected`, watchdog < cycle →
`capability.watchdog_shorter_than_cycle`). No execution semantics to test in
v0.1. Validator unit tests in `test_realtime.py` add the boundary and no-block
cases.

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

## Resolved / unresolved questions

- `guarantee` is **kept** (a required field), exactly because it is the honesty
  knob that lets the manifest state its regime without implying enforcement.
- `requested_packet_interval_ms` is **kept on `realtime`** for v0.1; whether a
  generic `link`-level field is a better home is a possible later refinement,
  not a blocker.
- The Pass-3 *envelope-dwell* enforcement rule (an envelope hold shorter than
  `watchdog_ms`) remains **deferred** to a future RFC. The v0.1 watchdog-vs-cycle
  coherence check is internal consistency, not that enforcement.

## Implementation note

Shipped as a single Layer-1-only change: schema (`Realtime` + the optional
`realtime` field), one validator coherence check + error code, two conformance
fixtures, unit tests, and spec §2.15. No multi-layer coordination and no
runtime change. The `urml-opcua-runtime` still carries timing as deployment
config in `opcua_adapter.yaml`; it MAY now read the manifest `realtime` block
to configure its session (mapping `requested_packet_interval_ms` to its
subscription) but is not obligated to in v0.1.

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
