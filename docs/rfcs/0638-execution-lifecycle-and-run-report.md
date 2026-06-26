---
rfc: 0638
title: Execution lifecycle, progress, and a structured run report
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-26
updated: 2026-06-26
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

# RFC-0638: Execution lifecycle, progress, and a structured run report

**Kind: Spec.** Extends the runtime contract (RFC-0014), not the program/manifest/
envelope schemas. This RFC scopes the design and leaves open questions for the
maintainer; no code ships until it is accepted.

## Summary

URML defines a *validated program*. It says almost nothing, normatively, about how
a runtime *executes* one over time: whether a long sequence can be cancelled from
the outside, whether progress can be observed while it runs, and what a finished
(or aborted) run reports back. Today the reference `URMLRuntime` returns a
`RuntimeResult` with `success`, `steps_executed`, the final `bindings`, an
`audit_log`, and the `last_outcome`. That is a good completion summary and nothing
more: there is no cancel, no pause/resume, no progress event, and no structured,
runtime-neutral place for execution telemetry (durations, retries, recoveries).

This RFC proposes a small, optional, substrate-neutral **execution contract** so
that lifecycle (cancel, optionally pause/resume), progress (a step identifier and
the current primitive), and a structured **run report** are defined once, the same
way the substrate Protocol is defined once. It adds no Layer-2 primitive and no
manifest field. Any runtime MAY implement it; a runtime that does not is still
conformant for what it does support.

**State: Draft.** Design proposal with open questions (see the end). Nothing is
implemented yet.

## Motivation

The motivation is a live design conversation with an active user building on a
GoPiGo3 and a TurtleBot4 clone
([Discussion #526](https://github.com/URML-MARS/URML/discussions/526)). Three
needs surfaced, in his words:

> Is there a mechanism to pause/resume and a mechanism to cancel mid-urml-sequence
> with summary of executed primitives or step identifier?

> ... interruption with completion report, monitoring progress, start/stop times,
> replanning a path under the path follower ...

> report(pose, accuracy, duration, # recoveries and time spent in recoveries)

These are not language questions. They are runtime-lifecycle and
runtime-telemetry questions, and the user correctly identified that the vendor
runtime owns which hooks exist. The risk, without a neutral contract, is that
every runtime invents its own cancel, its own progress event, and its own result
shape, so an autonomy layer (the mastermind, per RFC-0010's line) cannot interrupt
or monitor a URML run portably. The point of URML is that one program runs on a
GoPiGo3, a TurtleBot, or a drone without rewriting; the same should be true of
*driving and watching* that run.

A structured run report is also the right home for the per-substrate telemetry the
user listed. Nav2 reports navigation duration and the number of recovery
behaviours it ran; URML cannot and should not standardize "recoveries" as a
concept (it is meaningless on a drone), but it can give a runtime a typed,
neutral envelope (`per_step` outcomes plus a free-form `telemetry` map) so that
information travels back in a predictable shape.

## Why not the existing surface

**`RuntimeResult`.** It is a completion summary, returned only once, at the end. It
has no per-step timing, no retry/recovery count, and no hook to cancel or observe a
run in flight. It is the right seed; this RFC widens it.

**`on_error` (abort / continue / retry).** That governs how a run reacts to a step
*failing*, internally. It is not an external cancel, and it is not progress.

**The substrate Protocol (RFC-0014).** It is per-primitive (one call, one result).
Lifecycle and progress are about the *run*, a level above a single primitive call.

So this is a genuine gap, at the runtime-contract layer, and the right shape is a
small optional contract beside the substrate Protocol.

## Proposal (sketch)

Three optional, separable pieces. A runtime may implement any subset.

1. **Lifecycle.** An execution handle exposing `cancel()` and, optionally,
   `pause()` / `resume()`. `cancel()` stops at the next safe boundary (between
   primitives, never mid-actuation) and yields the run report below.
   `pause`/`resume` are a higher bar and explicitly optional; many runtimes will
   support cancel and not pause.

2. **Progress.** While a run executes, the runtime MAY emit progress events:
   a stable **step identifier** (a path into the behaviour tree), the primitive
   being executed, and its status (started / succeeded / failed / skipped). This
   is the "monitoring progress" and "step identifier" the user asked for.

3. **Run report.** A structured result that extends today's `RuntimeResult`:
   `success`, `steps_executed`, `bindings`, plus a `per_step` list (each: step id,
   primitive, status, and an optional duration), an overall `duration`, and a
   free-form `telemetry` map for substrate-specific numbers (where Nav2's
   recovery count and recovery time would land, a drone's RTH trigger would land,
   and so on). URML defines the envelope; the runtime fills `telemetry`.

### What stays out (substrate-neutrality)

Runtime-specific knobs do **not** become part of this contract or of a primitive's
arguments. A TurtleBot/Nav2 user might want `move_to` to carry goal tolerance, a
rotation-shim trigger angle, a pause-for-moving-obstacles flag, and replan-vs-
plan-once. Most of those are Nav2 concepts; baking them into `move_to` would make
`move_to` unimplementable on a frameless GoPiGo3, which is the leaky-primitive
failure mode CLAUDE.md forbids. They belong in the **ROS 2 adapter's deployment
config** (the same place the OPC UA and Isaac adapters keep their substrate
detail), not in the URML program. The one arguably-neutral exception is goal
*precision* (every mapped mobile base has a notion of "close enough"); whether that
earns a place on `move_to` is an open question below, not a given.

## Prior art / context

- The reference `URMLRuntime.execute` and its `RuntimeResult` (the seed).
- RFC-0014 (substrate conformance) — this extends that contract.
- ROS 2 action lifecycle (goal accept / cancel / feedback / result) and Nav2's
  result feedback are the concrete prior art for lifecycle + progress + telemetry.
- The motivating discussion, #526 (the autonomy/mastermind boundary, RFC-0010).

## Implementation plan (only after acceptance)

1. A typed `RunReport` (extends `RuntimeResult`: `per_step`, `duration`,
   `telemetry`), backward compatible (the extra fields default empty).
2. An optional `ExecutionHandle` Protocol (`cancel`, optional `pause`/`resume`),
   kept apart from the frozen substrate Protocol, the way `RelativeMotionAdapter`
   is (RFC-0630).
3. An optional progress-callback hook on `URMLRuntime.execute`.
4. A conformance note: these are optional capabilities; a runtime advertises which
   it supports, and the suite tests the report shape where claimed.
5. A worked example: a cancel-mid-sequence run that returns a report naming the
   primitives that ran before the cancel.

## Open questions (for the maintainer)

1. **Scope for v0.x.** All three (lifecycle + progress + report), or start with the
   run report alone (lowest-risk, immediately useful) and defer cancel/progress?
2. **Cancel vs pause/resume.** Standardize `cancel()` only (pause/resume left to
   runtimes), or define all three with pause/resume explicitly optional?
3. **Telemetry shape.** Free-form `telemetry: dict[str, Any]`, or a small typed
   core (duration, retries, recoveries) plus a free-form overflow?
4. **Progress transport.** A synchronous callback on `execute`, an iterator/stream,
   or out of scope for v0.x?
5. **Goal precision on `move_to`.** Add an optional, neutral precision/tolerance to
   `move_to` (a separate small Spec change), or keep all tolerance in adapter
   config? This is the one place the Nav2 wishlist touches the language surface.
