---
rfc: 0667
title: Envelope enforcement, evaluation semantics and a reference shield for monitorable properties
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-12
updated: 2026-07-12
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

# RFC-0667: Envelope enforcement, evaluation semantics and a reference shield for monitorable properties

## Summary

RFC-0382 gave the safety envelope a declarative temporal-logic core (`monitorable_properties`), a parser, and a boundary: URML does not run the monitor. This RFC finishes the runtime half. The satisfaction semantics of the full core (bounded and unbounded `always` / `eventually` / `until`, nested, plus the `stl_strel` spatial operators) over finite timed traces become normative, and URML ships a reference evaluator (`urml_validator.monitor`: offline `evaluate_trace`, three-valued `OnlineMonitor`) and a reference shield (`urml_ros2_runtime.shield`) with two enforcement surfaces: an optional hook in `URMLRuntime`'s per-step dispatch loop, and a `ShieldedAdapter` wrapper that guards *any* driver of a substrate adapter, including a VLA policy or an external agent that never produced a URML program. Envelope static caps (`max_velocity` and friends) compile into implicit critical `always` properties so one evaluator covers declared and derived limits. External RV backends (RTAMT, Reelay, Copilot, MoonLight) remain first-class through `compile_to_stl`; running URML's own monitor is optional.

## Motivation

The validator proves a program *may* run. Nothing in URML keeps the envelope true *while* it runs. RFC-0382 deliberately stopped at declaration: properties parse, signals resolve, and enforcement was delegated wholesale to external runtime-verification backends. That leaves two gaps, one practical and one strategic.

The practical gap: a deployment that declares "speed stays under 0.3 whenever a person is within 2 meters" gets no enforcement at all unless it separately adopts and wires an RV framework. None of the reference runtimes consume `monitorable_properties`. The declared property is documentation until something evaluates it, and the spec does not even say what evaluating it *means*: RFC-0382 defined a grammar, not semantics. Two backends could disagree about a truncated trace and both claim conformance.

The strategic gap: end-to-end learned policies (VLA models) are the direction the field is moving, and they do not emit URML programs. URML's answer cannot be "rewrite your policy as URML." It can be: whatever produces the actuation, the envelope holds. A shield that interposes between any policy and the adapter makes URML the safety boundary for stacks it does not plan for. That requires the enforcement to live at the adapter surface, not inside program execution.

## Detailed design

### Overview

```
             SafetyEnvelope
    (monitorable_properties + static caps)
                  |
        compile_envelope_monitors           urml_validator.monitor  (NEW)
                  |
                  v
   CompiledProperty[]  --> OnlineMonitor (3-valued) / evaluate_trace (offline)
                  |
                  v
               Shield                        urml_ros2_runtime.shield  (NEW)
              /      \
   URMLRuntime hook   ShieldedAdapter
   (per-step gate     (guards ANY driver:
    + telemetry)       VLA, agent, script)
                  |
        TelemetryAdapter side-protocol       substrate/base.py  (additive)
        (sample_signals() -> Sample)
```

### Normative: the trace model

A trace is a finite sequence of samples with strictly increasing timestamps, in seconds. Each sample carries the ego robot's signal values (the RFC-0382 vocabulary: `speed`, `altitude`, `payload`, `grip_force`, `person_distance`, plus declared sensors and events) and the entity set the spatial operators quantify over. An entity is an identifier, a distance from ego in meters, and its own signal map. Satisfaction of a property is judged at the first sample. Signals are piecewise-constant between samples. A property that references a signal a sample does not carry is an evaluation *error*, never silently false: a safety monitor that shrugs at absent data is not a safety monitor.

### Normative: completed-trace semantics

Quantifiers range over observed samples only. A bounded operator's window `[a, b]` is measured relative to the timestamp of the sample under evaluation.

- `always[a,b] p` holds when every observed sample in the window satisfies `p`. A truncated window cannot manufacture a violation.
- `eventually[a,b] p` requires an actual observed witness. A window that extends past the end of the trace does not excuse a missing witness (strong semantics for existential operators). This is the load-bearing choice: the safety reading of "the robot stops within 500 ms" on a trace that ends at 300 ms without a stop is *violated*, not *excused*.
- `p until[a,b] q` requires an observed witness of `q` inside the window with `p` holding at every sample from the evaluation point up to (not including) the witness.
- Boolean connectives are classical; `implies` is material.

### Normative: three-valued online verdicts

Over a growing prefix, each property is `satisfied` (no continuation can break it), `violated` (no continuation can save it), or `pending`. The reference implementation computes this by dual-mode evaluation (a pessimistic and an optimistic reading of the unobserved future; negation swaps the modes). A non-pending verdict is final and always agrees with the completed-trace verdict of any extension; `finalize()` collapses pending verdicts under completed-trace semantics. The agreement property is machine-checked in `test_monitor.py`.

### Normative: severity mapping

A monitor enforcing a URML envelope MUST map violations by the property's declared severity: `info` is recorded; `warning` is recorded and surfaced in the audit trail; `critical` vetoes the next actuation and halts a running program. This turns RFC-0382's "advisory to URML" severity field into an enforcement contract.

### Normative: static caps compile to properties

`max_velocity`, `max_altitude`, `max_payload`, and `max_grip_force_n` derive implicit properties (`always (signal <= limit)`) at `critical` severity, named `envelope.<cap>`. One evaluator covers both the declared temporal properties and the numeric caps the validator already checks statically; the monitor's job is to keep the caps true in motion.

### Normative: spatial semantics, v1 simplifications

`somewhere[a,b] p` holds at a sample when some entity at distance within `[a, b]` satisfies `p`, with signal lookups resolving against the entity's signals first and falling back to ego's. `everywhere[a,b] p` requires every such entity to satisfy `p`, vacuously true when the band is empty. `p surround[a,b] q` is the simplified annulus form: ego satisfies `p` and every entity in the band satisfies `q`. Two declared v1 restrictions: temporal operators inside a spatial operand are rejected (entity identity across samples is not modeled), and the full STREL reach/escape formulation of `surround` is a follow-on. `dialect: custom` properties are skipped by the reference monitor: URML cannot evaluate a grammar it does not define.

### Reference: the monitor (`urml_validator.monitor`)

`Sample` / `Entity` (the trace model), `evaluate_trace(node, trace) -> bool`, `OnlineMonitor` (observe / finalize / verdicts / violations), and `compile_envelope_monitors(envelope) -> list[CompiledProperty]`. Lives in the validator package, beside the RFC-0382 parser, deliberately dependency-free: any runtime (and workstream RFC-0668's rehearsal gate) consumes it without pulling in ros2-runtime. The online monitor re-evaluates pending properties on the full prefix per sample: correctness over performance, stated openly; incremental algorithms are what the RFC-0382 backend ecosystem is for.

### Reference: the shield (`urml_ros2_runtime.shield`)

`Shield(envelope)` compiles the properties and arms an `OnlineMonitor`. `gate(primitive)` raises `ShieldViolationError` while any critical property stands violated; `observe(sample)` feeds telemetry; `audit_entries()` renders violations in the runtime audit-log shape. The shield never reads a clock; timestamps come from the adapter's samples, keeping runs reproducible.

`URMLRuntime(adapter, shield=...)` (additive, default `None`, no behavior change without it) gates each step pre-dispatch and, when the adapter implements `TelemetryAdapter`, samples after each step; a fresh critical violation halts through the existing `_ExecutionHalt` path so `RuntimeResult` reports failure and the audit log carries the violation entries.

`ShieldedAdapter(inner, shield)` interposes on every guarded adapter method (the frozen RFC-0014 surface plus the optional side-protocol actuation verbs). Attribute access delegates to the wrapped adapter, so the wrapper exposes exactly the capability surface the inner adapter has. This is the policy-agnostic form: the driver on top can be anything that calls adapter methods, and URML guards actuation it never saw as a program.

### Reference: the telemetry seam (`TelemetryAdapter`)

A new optional side-protocol in `substrate/base.py`, following the `TrajectoryAdapter` / `RelativeMotionAdapter` / `OutputAdapter` precedent; the frozen `ROSAdapter` Protocol (RFC-0014) is untouched. `sample_signals() -> Sample` returns the current timestamped signal sample. `MockROSAdapter` implements it with a scriptable queue (benign synthesized samples when unscripted) so the hermetic suite exercises every path. Step-boundary sampling is honest but coarse: a spike inside one long blocking command is invisible until the command returns. Substrates with an internal control loop should push samples at their native cadence via `Shield.observe`; the RFC says this plainly rather than overclaiming coverage.

### Spec changes

`spec/layer-3-behavior/v0.2.0.md` gains §7b (envelope enforcement semantics): the trace model, completed-trace and three-valued semantics, the severity mapping, static-cap derivation, and the v1 spatial simplifications. No Layer-2 primitive is added; no schema field changes (RFC-0382's schema is consumed as-is).

### Validator changes

A new module, no changed checks: `urml_validator.monitor` is additive and exported from the package root. Static validation behavior is untouched.

### Reference runtime changes

`urml_ros2_runtime`: new `shield.py`; `TelemetryAdapter` side-protocol and `MonitorSample` re-export in `substrate/base.py`; `MockROSAdapter.set_telemetry` / `sample_signals`; `URMLRuntime` gains the optional `shield=` parameter and the two hook points in `_exec_step`; audit snapshot extended with shield entries. Other runtimes adopt `TelemetryAdapter` as they grow real state readback; nothing is required of them to remain conformant.

### Conformance suite changes

None in this PR. The conformance fixture schema cannot script telemetry yet, so enforcement behavior is pinned by the package suites (`test_monitor.py` as the executable semantics, `test_shield.py` for both enforcement surfaces). A fixture-level `telemetry:` lane is follow-on work, noted in Unresolved questions.

## Backward compatibility

Fully additive. `URMLRuntime` without a shield behaves byte-for-byte as before; the new constructor parameter is keyword-only with a `None` default. `SafetyEnvelope` is unchanged. RFC-0382's "URML does not run the monitor" sentence is superseded by "URML ships an optional reference monitor; external backends remain first-class," which relaxes a self-imposed restriction rather than breaking a user-facing surface.

## Drawbacks

Owning evaluation semantics means owning their bugs: a semantics defect in `monitor.py` is now a safety defect in URML rather than in a third-party backend, which raises the review bar on that module permanently. Step-boundary sampling gives real but coarse coverage, and naming the mechanism a "shield" invites reading more protection into it than a per-step monitor provides; the docstrings and spec text state the coverage limits explicitly. The naive re-evaluation monitor is O(trace × property) per sample and will not survive high-rate control loops, which is acceptable for a reference implementation but must not be sold as a real-time monitor (RFC-0016's cyclic-timing block is the eventual home of cadence guarantees). The simplified `surround` semantics may diverge from published STREL; it is declared as such rather than silently normative.

## Alternatives considered

**Keep the RFC-0382 boundary: integrate an external backend instead of shipping an evaluator.** Embedding RTAMT or Reelay as a dependency violates the reference runtimes' zero-heavy-dependency posture and picks a winner among backends URML deliberately courts as integration partners (Moves #28's engaged targets include Ogma and monitor authors). Defining semantics plus a small reference evaluator keeps backends first-class while making the envelope enforceable out of the box.

**Enforce only inside `URMLRuntime` (no `ShieldedAdapter`).** Rejected: it would tie enforcement to URML being the planner, exactly the assumption the VLA trajectory invalidates. The adapter surface is where actuation converges regardless of who plans.

**A reduced predicate-only v1 (thresholds plus `always`/`never`/`within`).** Rejected by explicit founder decision: the RFC-0382 grammar already ships parsed and signal-checked; defining semantics for a subset would strand declared properties in an unenforceable middle state.

**A `stop()` method on the adapter protocol for active braking on violation.** The `ROSAdapter` Protocol is frozen per RFC-0014, and a portable "stop" is itself a hard cross-substrate design problem (motors-off vs. controlled stop vs. hover). v1 vetoes the *next* dispatch and halts the program; active stopping is substrate-specific and out of scope, stated plainly.

## Prior art

RFC-0382 (the grammar, parser, and signal vocabulary this RFC gives semantics to); RFC-0016 (cyclic timing and the deferred envelope-dwell rule, the natural home of monitor-cadence guarantees); RFC-0383 (learned-policy training envelopes, the static half of the VLA story whose runtime half is the shield); RFC-0014 (the frozen adapter protocol and the side-protocol extension pattern). Outside URML: LTL3 three-valued runtime verification (Bauer, Leucker, Schallhart) is the model for the online verdicts; STL monitoring as practiced by RTAMT and Reelay; STREL (Bartocci et al.) for the spatial operators; the "shield synthesis" literature (Bloem et al.) for the interposition pattern, though URML's shield vetoes rather than substitutes actions; simplex-architecture runtime assurance in aviation for the gate-and-halt posture.

## Unresolved questions

- Full STREL `surround` (reach/escape) semantics, and spatial operands with temporal depth once entity identity across samples is modeled.
- A conformance-fixture `telemetry:` lane so envelope-violation traces become declarative conformance cases rather than package tests.
- Quantitative (robustness) semantics alongside the Boolean ones; backends already speak robustness and a future certification story may want margins, not just verdicts.
- Mid-command sampling for long blocking primitives: adapter-pushed samples exist (`Shield.observe` is public) but no reference adapter pushes yet.
- Whether the richer signal vocabulary question from RFC-0382 (its Unresolved Question 2) should resolve before v1.0 freezes the built-in list.

## Implementation note

One vertical-slice PR: this RFC, `urml_validator.monitor` plus its semantics table tests (the executable spec), the shield and its tests, the `TelemetryAdapter` seam, the `URMLRuntime` hook, and the Layer-3 §7b spec text. RFC-0668 (rehearsal) consumes `evaluate_trace` and `compile_envelope_monitors` from this PR, which is why the evaluator lives in the validator package rather than beside the shield.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] This RFC adds no Layer-2 primitive (substrate-neutrality acid test not applicable; the shield attaches at the adapter surface every substrate already implements).
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
