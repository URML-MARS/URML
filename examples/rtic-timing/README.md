# RTIC timing: a declared cyclic requirement, checked and mapped

A worked example for [rtic-rs/rtic#1188](https://github.com/rtic-rs/rtic/issues/1188).

URML's RFC-0016 `realtime` block lets a robot's manifest declare the cyclic timing
a control node runs under: a control-cycle period and a watchdog deadline that
faults to a safe state if a cycle is missed. This example shows what URML does
with that declaration, and, just as importantly, what it does not.

## Run it

```
python examples/rtic-timing/run_rtic.py
```

It declares a 100 Hz control loop (10 ms cycle) with a 50 ms watchdog, and:

1. Validates the coherent declaration. The one RFC-0016 check is internal
   coherence: the watchdog must allow at least one full cycle
   (`watchdog_ms >= cyclic_period_ms`).
2. Rejects an incoherent one. A 5 ms watchdog under a 10 ms cycle would fault
   before a single cycle completes, so it is refused with
   `capability.watchdog_shorter_than_cycle`.
3. Maps the declared period and watchdog onto an RTIC task set.

The output is committed as `rtic-timing-report.txt` and byte-asserted in CI.

## What URML does, and what RTIC does

URML **declares** the timing requirement and checks that the declaration is
coherent. It does **no** scheduling, **no** WCET, and **no** schedulability
analysis. The one static check is a sanity rule, not a real-time guarantee.

RTIC is what **honors and proves** the requirement. As its maintainer laid out on
the issue, a declared period and deadline can be paired with:

- **Compile-time**: response-time and schedulability analysis for RTIC's
  fixed-priority Stack Resource Policy model, given the deadlines (which URML
  declares) and WCET (which URML cannot provide, and which symbolic execution of
  the binary is the real work behind).
- **Run-time**: a watchdog on the periodic task, and overload detection via a
  watchdog cleared in the idle task at the hyper-period.

The declared period and watchdog are the inputs those mechanisms consume. The
guarantee is RTIC's to provide.

## The mapping

Aligned with the modular compilation-pass model of
[RTIC eVo](https://github.com/zakimadaoui/rtic-mc-experiments), where a
`rtic-deadline-pass` already turns deadlines into priorities, a periodic-task and
run-time-verification pass would consume the declaration as:

- `realtime.cyclic_period_ms` becomes a periodic task released at that period.
- `realtime.watchdog_ms` becomes a run-time monitor armed to that deadline,
  cleared by the periodic task each cycle, firing on an overrun.
- `realtime.guarantee` selects the SRP scheduling regime.

URML declares; an RTIC pass generates. URML does not emit the Rust. The example
prints an illustrative sketch of the generated shape, clearly marked as
illustrative and not verified Rust.
