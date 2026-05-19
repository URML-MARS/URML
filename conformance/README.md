# URML Conformance Suite

**Status:** v0.1 shipped. **Declarative fixture model + ConformanceRunner + 7 fixture cases + parametrized pytest harness** at pre-alpha `0.1.0a0`. Pulls earlier from the [MANIFESTO Roadmap](../MANIFESTO.md) (which named Phase 3 for the suite v1) so that every URML-compatible runtime has a target to build toward from day one.

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

## Quickstart (v0.1 — hermetic, no ROS 2 needed)

```bash
cd conformance
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ../reference/validator
pip install -e ../reference/ros2-runtime
pip install -e ".[dev]"
pytest
```

Use the runner programmatically:

```python
from urml_conformance import ConformanceRunner

runner = ConformanceRunner()
report = runner.run()
assert report.all_passed, report.render()
```

## Authoring a new fixture

Drop a YAML file under `conformance/fixtures/<profile>/`:

```yaml
name: profile/my_case
description: One-line summary.
manifest: turtlebot4_home      # name from MANIFEST_REGISTRY
envelope: home_default         # optional; name from ENVELOPE_REGISTRY
profiles: [home]

program:
  profile: home
  behavior:
    type: sequence
    steps: [ ... ]

adapter_overrides:             # optional: pre-configure MockROSAdapter
  navigation: { success: false, reason: path_blocked }

expected_validation:
  accepted: true               # or false + error_codes for rejection tests

expected_execution:            # omit for validator-only cases
  success: true
  steps_executed: 5
  audit_methods: [send_navigation_goal, ...]
  bindings_contains:
    target_mug: { class: mug }
```

The fixture is picked up automatically by `discover_fixtures()` and exercised by the next `pytest` run.

## What's in the v0.1 fixture set

A representative selection (the full set is discovered automatically from
`conformance/fixtures/**/*.yaml` by `discover_fixtures()` and has grown well
beyond the rows below as profiles and runtimes landed — run `urml conformance
run` for the live count):

| Fixture | Exercises |
|---|---|
| `home/red_mug_positive` | Canonical red-mug fetch end to end. |
| `home/red_mug_nav_failure` | Adapter failure → `abort_and_report` halts the sequence. |
| `home/missing_location_rejected` | Validator-only: undeclared location → `capability.missing_location`. |
| `home/branch_on_color` | Branch composition + `$ref.field.subfield` condition evaluation. |
| `home/retry_until_confidence` | Retry composition with `until` short-circuit. |
| `home/parallel_first_to_succeed` | Parallel composition with `first_to_succeed` mode. |
| `industrial/pick_red_positive` | Industrial pick-and-place written with the core twelve (composition-equivalent). |
| `industrial/pick_from_positive` | RFC-0013: `pick_from` + `place_at`; the picked-object binding flows between them. |
| `industrial/swap_tool_positive` | RFC-0013: `swap_tool` rides the docking-service path (`send_docking_goal`). |
| `industrial/swap_tool_undeclared_service_rejected` | RFC-0013 negative: `swap_tool` at a non-station → `capability.missing_docking_station`. |

## Related documents

- [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md) — the commitment that the suite stays free.
- [`/spec/`](../spec/) — the specifications the suite tests against.
- [`/reference/`](../reference/) — the reference implementations the suite is first exercised against.
- [`MANIFESTO.md`](../MANIFESTO.md) §License Direction — the trademark / conformance-mark policy that lives separately from the suite.
