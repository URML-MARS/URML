---
rfc: 0478
title: Ordered substrate bring-up and recovery sequences
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

# RFC-0478: Ordered substrate bring-up and recovery sequences

## Summary

The order in which substrate elements are brought up, configured, and recovered
is load-bearing, and the manifest has no way to declare it. This RFC adds an
optional `substrate.bringup` block: a list of bus elements with bring-up and
error-recovery ordering dependencies. The validator checks the declaration is
coherent (unique ids, declared dependencies, acyclic graphs); it does not
execute or schedule the sequence. It is *not* a primitive.

**State: Implemented** (2026-06-12). Ships the schema block, three Pass-2
internal-coherence checks (with cycle detection), unit tests, and a worked
example. Additive: a manifest without `substrate.bringup` is unaffected.

## Motivation

Surfaced directly by an engagement. On
[ICube-Robotics/ethercat_driver_ros2#224](https://github.com/ICube-Robotics/ethercat_driver_ros2/issues/224)
(RFC-0320 outreach), the driver's maintainer (yguel) named this as the most
under-specified area:

> in my opinion the area for which specification is lacking the most is how to
> address sequence of events that need a specific ordering: sequence of
> initialization, sequence of error recovery for elements on the bus [...] the
> order in which elements are accessed/configured/communicated with might be of
> tremendous importance. Therefore there are ordering issues and we do not have
> a clear view/specification.

A drive cannot init before its power bus; a gripper cannot configure before the
arm it hangs off; error recovery may need a different order than bring-up. These
are structural facts of the deployment that URML currently loses. They are
properties of the substrate, not of the intent, which is why this is a
manifest-schema block and not a Layer-3 behavior.

## Detailed design

An optional sub-block of the existing `substrate` block:

```
substrate:
  bringup:
    elements:
      - id: power_bus
      - id: drive_axis_1
        depends_on: [power_bus]          # bring-up: these come up first
        recovery_after: [power_bus]      # error recovery: recovered after these
      - id: gripper
        depends_on: [drive_axis_1]
```

`extra: forbid` as everywhere in Layer 1. Each element has a snake_case `id`,
an optional `depends_on` (bring-up order), and an optional `recovery_after`
(error-recovery order, which may differ from bring-up). Both are dependency
relations: "X depends_on Y" means Y is brought up before X. The validator
derives no schedule; the relations are a declaration the runtime may consume.

### Spec changes

- **Layer 1**: add the optional `SubstrateElement` and `Bringup` models under
  `substrate` in the capability-manifest schema and §2.14b of the Layer-1 HAL
  spec. No Layer 2/3/4 change.

### Validator changes

Three Pass-2 **internal-coherence** checks ship:

- element ids are unique (`capability.bringup_duplicate_element`);
- every `depends_on` / `recovery_after` references a declared element
  (`capability.bringup_dependency_undeclared`);
- neither the `depends_on` graph nor the `recovery_after` graph contains a
  cycle (`capability.bringup_dependency_cycle`) — a circular ordering can never
  be satisfied.

Cycle detection mirrors the frame-graph check (RFC-0290). All three check the
declaration's self-consistency; none execute the sequence.

### Reference runtime changes

None required. A runtime MAY topologically order the elements to drive its
bring-up / recovery state machine but is not obligated to in v0.1.

## Alternatives considered

**An explicit ordered list (no dependency graph).** Rejected: a flat order
cannot express that recovery differs from bring-up, nor that two independent
elements have no ordering constraint between them. A dependency graph captures
exactly the constraints that exist and nothing more.

**A Layer-3 behavior (a `sequence` of init steps).** Rejected: bring-up and
recovery order is a structural property of the hardware (power architecture,
config interdependencies), not an intent the operator authored. It belongs in
the manifest, where it is declared once and consumed by any runtime.

**Inferring order from frames / manipulation structure.** Rejected: the kinematic
parent graph is not the power / configuration dependency graph; a gripper's
frame parent is the arm, but its bring-up dependency might be a separate I/O
coupler. The two graphs are genuinely different.

## Prior art

systemd unit ordering (`After=` / `Requires=`), Kubernetes init-container
ordering, and EtherCAT state-machine bring-up (INIT → PREOP → SAFEOP → OP per
slave, gated by dependencies) all encode dependency-ordered bring-up. This RFC
declares that dependency structure at the manifest level.

## Implementation plan

1. `SubstrateElement` + `Bringup` models + `bringup` field on `Substrate`
   (`schemas/manifest.py`). Done.
2. Three error codes + `_check_substrate_bringup` with cycle detection
   (`errors.py`, `validator.py`). Done.
3. Unit tests in `test_substrate_clock_bringup.py`. Done.
4. Worked example under `examples/fieldbus/`. Done.
5. Layer-1 HAL §2.14b spec update. Done.

## Open questions

- A future rule could relate `recovery_after` to declared link-loss / fault
  policy (RFC-0006), so error recovery order is checked against the declared
  safe state. Deferred.
