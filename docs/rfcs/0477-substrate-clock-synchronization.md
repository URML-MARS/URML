---
rfc: 0477
title: Substrate clock / time-synchronization declaration
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0477: Substrate clock / time-synchronization declaration

## Summary

A fieldbus clock cannot always be hidden. The moment a deployment must
synchronize events caught *outside* the bus, the bus and the rest of the system
have to share a time reference. The capability manifest has no way to declare
that regime. This RFC adds an optional `substrate.clock` block declaring how the
substrate's clock relates to the user / system clock: the bus clock as the
reference, or a master clock synchronized to the user clock. It is *not* a
primitive and makes no claim that URML enforces a timing guarantee.

**State: Implemented** (2026-06-12). Ships the schema block, two Pass-2
internal-coherence checks, unit tests, and a worked example. Additive: a
manifest without `substrate.clock` is unaffected.

## Motivation

Surfaced directly by an engagement. On
[ICube-Robotics/ethercat_driver_ros2#224](https://github.com/ICube-Robotics/ethercat_driver_ros2/issues/224)
(RFC-0320 outreach), the driver's maintainer (yguel) wrote:

> at some point clock mechanisms cannot be hidden: this happens when the bus
> clock has some consequences on the rest of the system, which arises as soon as
> you need to synchronize events that are caught outside of the bus. As this is
> the very reason we all use ROS 2 [...] interface wise, it only means that a
> synchronization mechanism should be shared between bus user and bus.

He named two ways to share it: (1.1) the bus clock is directly the reference
clock (the strongest real-time guarantee, especially when a slave has dedicated
timing hardware such as IEEE-1588 acceleration, GPS, or an atomic clock); or
(1.2) the bus clock uses the master clock, synchronized to the user clock, with
constraints on the user clock.

URML has a per-sensor `time_sync_methods` field (RFC-0039), but nothing that
declares the substrate's clock *architecture*: who holds the reference, what
protocol carries it, and what bound the user clock must hold. Two cells that
differ only in their time-sync topology have identical manifests, so the
manifest is not the faithful hardware description Layer 1 exists to be.

## Detailed design

An optional sub-block of the existing `substrate` block:

```
substrate:
  clock:
    reference: bus | master_synced            # who holds the time reference
    sync_protocol: ieee1588 | gptp | ethercat_dc | ptp | gps | none   # optional
    hardware_timestamping: <bool>             # dedicated slave timing hardware
    user_clock_max_offset_ms: <number>        # optional; master_synced only
    note: <string>                            # optional
```

`extra: forbid` as everywhere in Layer 1. Absent block ⇒ "unspecified clock"
(today's behavior, unchanged).

`reference: bus` models flavor 1.1: the bus clock *is* the reference. The
GPS / IEEE-1588-on-a-slave case is captured by `hardware_timestamping: true`.
`reference: master_synced` models flavor 1.2: the bus rides the master clock,
synchronized to the user clock, which requires a sync mechanism and bounds the
user clock's drift.

### Spec changes

- **Layer 1**: add the optional `ClockSync` model under `substrate` in the
  capability-manifest schema and §2.14a of the Layer-1 HAL spec. No Layer
  2/3/4 change.

### Validator changes

Two Pass-2 **internal-coherence** checks ship:

- `reference == master_synced` requires `sync_protocol` set and not `none`
  (`capability.clock_sync_protocol_required`): the bus cannot be synchronized to
  the user clock without a mechanism.
- `user_clock_max_offset_ms` is only applicable when `reference ==
  master_synced` (`capability.clock_offset_not_applicable`): when the bus clock
  is the reference there is no user-clock offset to bound.

Both check the declaration's self-consistency; neither is timing enforcement.

### Reference runtime changes

None required. A runtime MAY read `substrate.clock` to configure its DC /
gPTP / PTP session but is not obligated to in v0.1.

## Alternatives considered

**Reuse the per-sensor `time_sync_methods` list (RFC-0039).** Rejected: that
field is per-sensor timestamping metadata; the clock *reference architecture* is
a substrate-level fact (one per bus), not a per-sensor list. They complement
each other.

**A free-form string.** Rejected: a closed enum on `reference` and
`sync_protocol` is what makes the coherence checks possible and keeps the
declaration comparable across deployments.

## Prior art

IEEE-1588 (PTP) and gPTP define the master / reference clock distinction
directly; EtherCAT distributed clocks (DC) make one slave the reference and
discipline the others to it. The two flavors this RFC declares are the
vocabulary those standards already use.

## Implementation plan

1. `ClockSync` model + `clock` field on `Substrate`
   (`schemas/manifest.py`). Done.
2. Two error codes + `_check_substrate_clock` (`errors.py`, `validator.py`).
   Done.
3. Unit tests in `test_substrate_clock_bringup.py`. Done.
4. Worked example under `examples/fieldbus/`. Done.
5. Layer-1 HAL §2.14a spec update. Done.

## Open questions

- A future rule could relate `user_clock_max_offset_ms` to a `realtime`
  cyclic period (an offset larger than a control cycle is suspect). Deferred to
  keep this change honest about what is enforced.
