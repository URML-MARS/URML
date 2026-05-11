# URML Conformance Suite

**Status:** Pre-implementation. Phase 3 target per [`MANIFESTO.md`](../MANIFESTO.md) §Roadmap Snapshot.

## What this is

The Apache-2.0, **freely runnable** set of tests that determines whether a runtime is **URML-compatible**. The conformance suite is the bridge between the abstract specification documents in [`/spec`](../spec/) and a concrete claim of compatibility a robot maker can stand behind.

The conformance suite is part of the [Core Commitment](../CORE_COMMITMENT.md). It will always be Apache 2.0. The eventual *certification program* — the trademark *URML-Certified* — may be paid; the *tests themselves* remain free, public, and runnable by anyone. This separation is deliberate: it lets URML's compatibility claim be honest (anyone can verify it) while preserving a commercial moat in the surround (the mark is licensed, not the tests).

## How conformance is structured

Conformance is **per-specification-version**, not whole-project. A runtime that passes the Layer-2 v0.1 tests and the home-profile v0.1 tests is conformant to *those* specs at *those* versions, no more and no less. The runtime declares this in its own `CONFORMANCE.md`.

```yaml
declares:
  layer-1-hal: 0.1.0
  layer-2-primitives: 0.1.0
  layer-3-behavior: 0.1.0
  layer-4-nl-grammar: 0.1.0
  profiles:
    home: 0.1.0
```

The conformance suite ships with a runner that, given a runtime and the runtime's declared versions, runs the appropriate test set and emits a structured report.

## What the suite tests

When drafted, the suite contains tests in three categories:

### 1. Static behavior

Tests of the validator and the spec itself — independent of any particular runtime. These confirm that a given URML program, manifest, and envelope produce the documented validation outcome.

### 2. End-to-end behavior

Tests of a runtime, given a manifest and a URML program, in a controlled environment (typically a simulator wired into the runtime). These confirm that the runtime *executes* primitives per their documented semantics — `move_to(kitchen)` actually moves the robot to the kitchen, not to some other place.

### 3. Negative tests

The most important category. Confirms that the runtime correctly **rejects** programs that violate declared capability or the safety envelope. Cases include:

- Programs that require capabilities not in the manifest.
- Programs that exceed declared velocity / payload / force / altitude / geofence / cell-perimeter limits.
- Programs that violate profile-specific constraints (drone `move_to` missing altitude, industrial program requiring motion with safety-door open, home program requiring motion into a declared people-only zone).
- Programs that violate Layer-3 invariants (untyped variable references, unbounded retries, type-mismatched arguments).

A runtime that *executes* one of these programs has a critical conformance bug. The suite makes that bug visible.

## What the suite does NOT test

- Performance, latency, jitter. Those are runtime concerns, not specification concerns. A separate (non-conformance) benchmarking suite may eventually live in this directory; if so, it is clearly labeled as a benchmark, not a conformance test.
- Substrate-specific behavior. The suite tests *URML* compliance; it does not test that the runtime's chosen Layer-0 (ROS 2, PX4, ...) is also well-behaved.
- Hardware-specific behavior. The suite runs against simulators where possible. Hardware-in-the-loop is the runtime developer's own responsibility.

## How conformance is consumed

Two paths:

1. **Self-reported conformance.** A runtime developer runs the suite against their runtime, records the result, and publishes the report. This is what the open ecosystem looks like. Self-reporting is honest because anyone can re-run the suite and verify.
2. **Certified conformance** (future, Phase 3+). The URML organization (or its successor foundation) operates a paid program that issues the **URML-Certified** mark to runtimes that pass the suite. The mark is the commercial product; the test is the open standard.

## How tests are added

A spec change (RFC) that affects observable behavior must land with the corresponding conformance-suite changes in the same release. A spec change without conformance updates is incomplete and is sent back. This rule is what keeps the spec and the suite from drifting.

## Status as of Phase 0

This directory contains only this README. Drafting the suite begins in Phase 3, after the first reference runtimes have stabilized. Before then, runtimes self-test against the spec documents directly; the formal harness lands once there is enough surface to test.

## Related documents

- [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md) — the commitment that the suite stays free.
- [`/spec/`](../spec/) — the specifications the suite tests against.
- [`/reference/`](../reference/) — the reference implementations the suite is first exercised against.
- [`MANIFESTO.md`](../MANIFESTO.md) §License Direction — the trademark / conformance-mark policy that lives separately from the suite.
