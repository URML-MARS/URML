---
rfc: 0469
title: Acyclic (SDO / mailbox) operation-mode declaration in the realtime block
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

# RFC-0469: Acyclic (SDO / mailbox) operation-mode declaration in the realtime block

## Summary

The `realtime` block (RFC-0016) declares one timing regime: a fixed cyclic
period and a watchdog deadline. That describes the *cyclic* path of a fieldbus
(an EtherCAT PDO, a CANopen PDO), where the answer is immediate and the watchdog
catches a missed cycle. The same substrate almost always also carries *acyclic*
traffic (an EtherCAT SDO, a CANopen SDO, an OPC UA method call) whose return
time is not guaranteed. For that path a watchdog is the wrong instrument. This
RFC adds an optional `acyclic` sub-block to `realtime` that declares the
asynchronous regime: a transaction timeout and an explicit goal-reached check.
It is *not* a primitive and makes no claim that URML enforces a timing
guarantee.

**State: Implemented** (2026-06-12). Ships the schema sub-block, one validator
internal-coherence check (`acyclic.timeout_ms >= cyclic_period_ms`), unit tests,
and a worked example. Fully additive: a manifest without `acyclic` is
unaffected.

## Motivation

Surfaced directly by an engagement. On
[ICube-Robotics/ethercat_driver_ros2#224](https://github.com/ICube-Robotics/ethercat_driver_ros2/issues/224)
(RFC-0320 outreach), the driver's maintainer (yguel) answered the operation-mode
question precisely:

> the operation mode has huge impacts on the behaviour of the system: in a
> cyclic communication (PDOs) the answer from the bus is immediate, whereas for
> asynchronous (mailbox aka SDOs) the answer time from the bus is not
> guaranteed. The way to handle errors, checks and especially check that goal is
> reached, timeout, etc. changes completely in these cases.

URML already models the cyclic side faithfully (RFC-0016: `cyclic_period_ms`,
`watchdog_ms`, `guarantee`). It has no way to say the same substrate also serves
acyclic commands, nor how one is bounded. Two cells that differ only in whether a
command rides PDO or SDO have identical manifests, so the manifest is not the
faithful hardware description Layer 1 exists to be. This is a
capability-declaration gap, not a behavior gap, which is why it extends a
manifest-schema block rather than adding a primitive.

## Detailed design

An optional sub-block of the existing `realtime` block:

```
realtime:
  cyclic_period_ms: 10.0
  watchdog_ms: 50.0
  guarantee: soft
  acyclic:                          # optional; this RFC
    timeout_ms: <number>            # deadline for an SDO / mailbox transaction
    requires_goal_check: <bool>     # default true: confirm by read-back, not assume
```

`extra: forbid` as everywhere in Layer 1. Absent sub-block ⇒ "no declared
acyclic path" (today's behavior, unchanged).

`timeout_ms` bounds a transaction whose return time the bus does not guarantee.
Unlike `watchdog_ms` it is not a cycle deadline; it is the point past which an
asynchronous command is treated as failed.

`requires_goal_check` defaults to `true`. An asynchronous mailbox answer is not
implied by the next control cycle, so completion is confirmed by reading state
back rather than assumed. The field is an honesty declaration about how the
substrate confirms completion; URML does not police the read-back itself in
v0.1.

### Spec changes

- **Layer 1**: add the optional `AcyclicRegime` model under `realtime` in the
  capability-manifest schema and §2.15 of the Layer-1 HAL spec. No Layer 2/3/4
  change — no primitive branches on operation mode.

### Validator changes

One Pass-2 **internal-coherence** check ships: `acyclic.timeout_ms >=
cyclic_period_ms` (`capability.acyclic_timeout_shorter_than_cycle`). An acyclic
command that must return inside a single control cycle is, by definition, cyclic
traffic and belongs on the cyclic path; declaring it as acyclic is incoherent
regardless of the regime. This checks the declaration's self-consistency; it is
*not* timing enforcement. No Pass-3 rule ships.

### Reference runtime changes

None required. A runtime MAY read `acyclic` to route a command over the SDO /
mailbox channel and apply the declared timeout, but is not obligated to in v0.1.

## Alternatives considered

**A boolean `operation_mode: cyclic | acyclic` on the block.** Rejected: a
substrate is rarely one or the other; it serves cyclic process data *and*
acyclic mailbox commands at once. A sub-block that coexists with the cyclic
fields models reality; a mutually exclusive enum does not.

**Per-primitive operation-mode tags in Layer 2.** Rejected: operation mode is a
property of the substrate channel, not of the intent. A `move_to` is the same
intent whether the drive is commanded over PDO or SDO; coupling a primitive to a
bus channel would be a leaky abstraction and a one-way door.

**Doing nothing (the cyclic block is enough).** Rejected: it makes the manifest
silently wrong for the most common fieldbus topology (a drive on PDO, parameter
and mode-change commands on SDO), which is exactly the case the
ethercat_driver_ros2 maintainer raised.

## Prior art

CiA-402 (CANopen drive profile) and EtherCAT both distinguish process-data
(PDO, cyclic) from service-data (SDO, acyclic mailbox) objects; OPC UA
distinguishes cyclic subscriptions from acyclic method calls. The cyclic-versus-
acyclic split this RFC declares is the vocabulary those substrates already use.

## Implementation plan

1. `AcyclicRegime` model + `acyclic` field on `Realtime`
   (`schemas/manifest.py`). Done.
2. Error code `capability.acyclic_timeout_shorter_than_cycle` (`errors.py`) and
   the Pass-2 coherence check in `_check_realtime` (`validator.py`). Done.
3. Unit tests in `test_realtime.py` (accept, default, boundary, reject, extra-
   key). Done.
4. Worked example under `examples/fieldbus/` with a byte-asserted generator.
   Done.
5. Layer-1 HAL §2.15 spec update. Done.

## Open questions

- A future Pass-3 rule could relate `acyclic.timeout_ms` to a program's declared
  goal-check structure, the acyclic analogue of the deferred envelope-dwell rule
  in RFC-0016. Deferred to keep this change honest about what is enforced.
