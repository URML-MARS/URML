---
rfc: 0668
title: Rehearsal, a simulated pre-execution gate (urml run and execute --rehearse)
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

# RFC-0668: Rehearsal, a simulated pre-execution gate

## Summary

Static validation proves a program is *admissible*; RFC-0667's shield keeps the envelope true *during* execution. This RFC adds the step between them: rehearsal. A validated program is rolled out on a simulation backend that records a signal trace, the trace is evaluated against the envelope's monitorable properties and static caps with RFC-0667's evaluator, and any critical violation blocks real execution. The gate ships in two CLI shapes: a `--rehearse` flag on `urml execute`, and a new end-to-end verb, `urml run "<sentence>" ...`, which chains translate, validate, rehearse, and execute. Two reference backends: a hermetic kinematic profile (zero dependencies, runs in CI) and a MuJoCo recorder (real physics, `[sim]` extra, per-tick sampling mapped to envelope signals by a declared `SignalMap`).

## Motivation

The validator catches capability violations: a ground robot asked to `take_off`, a location no manifest declares. It cannot catch "valid but envelope-breaking in motion": a patrol whose cruise speed exceeds the deployment cap, a survey whose climb passes through a forbidden altitude band, a program that never returns to rest. Today those surface either never (mock runs), or on the real robot, which is the most expensive place to learn them.

Every ingredient for catching them earlier already exists in the repository: real physics stepping (`MujocoAdapter`), an envelope evaluator over recorded traces (RFC-0667's `evaluate_trace` / `OnlineMonitor`), and a validation-first CLI. What is missing is the recording (the MuJoCo adapter returns only a final pose per command) and the plumbing that makes "rehearse before you run" a one-flag experience. A rehearsal gate also completes the safety lifecycle story in a way that is easy to say out loud: *checked before dispatch, rehearsed before motion, monitored during motion.*

## Detailed design

### Overview

```
urml run "survey the roof" --manifest ... --envelope ... --rehearse
    |
    |  1. translate   (LLM bridge; every emission validated)
    |  2. validate    (the accepted program, caller's policy)
    |  3. rehearse    (sim rollout -> recorded trace -> RFC-0667 evaluation)
    |        critical violation? --> exit 1, the real adapter is never constructed
    |  4. execute     (mock | ros2 | px4)
    v
```

### Normative: the gate

Given a validated program, a capability manifest, and a safety envelope:

1. The program is executed on a rehearsal backend: an adapter satisfying the frozen `ROSAdapter` Protocol (RFC-0014) that also records a signal trace (`TraceRecorder`: `samples() -> tuple[Sample, ...]`, RFC-0667's trace model).
2. The envelope compiles per RFC-0667 (`compile_envelope_monitors`: declared monitorable properties plus static caps derived to critical `always` properties) and the recorded trace is evaluated under RFC-0667's completed-trace semantics.
3. The gate **passes** when the simulated execution succeeded and no `critical` property is violated. `warning` and `info` violations are reported and do not fail the gate (the RFC-0667 severity mapping).
4. A gate failure MUST block real execution: the real substrate adapter receives nothing.
5. Two honesty rules. An envelope that compiles to zero properties gates on simulated execution success alone and MUST say so. An envelope *with* properties whose rehearsal recorded no samples fails the gate: no evidence is not passing evidence.

The gate is substrate-neutral: any adapter + recorder pair qualifies as a backend. A conformant implementation reports which motion model produced the trace, because the gate's meaning is bounded by it.

### Normative: what a passed rehearsal claims

A passed rehearsal is evidence that the program's *simulated* trace keeps the envelope under the backend's motion model. It is not a guarantee about the physical robot. CLI output carries a per-backend banner stating the model (the `_SUBSTRATE_NOTE` discipline applied to rehearsal), and the kinematic backend's profile is explicitly a set of declared assumptions.

### Reference: the kinematic backend (`urml_ros2_runtime.rehearsal`)

`KinematicRehearsalAdapter` subclasses `MockROSAdapter` and synthesizes a trace from a declared `KinematicProfile` (`dt`, `cruise_speed`, `turn_speed`, `climb_rate`, `move_duration`): translation commands emit cruise-speed samples, `take_off`/`land` ramp the altitude signal at the climb rate, every command boundary returns to rest, non-motion commands emit an at-rest sample so the trace covers the whole program. Hermetic, zero dependencies; it is the CI floor and the default `--rehearse` backend. Its honesty condition is stated in the class docstring: set the profile to the deployment's real expected values or the gate checks a fiction.

`rehearse(program, manifest, envelope, *, adapter, recorder=None, profiles, revalidate=True) -> RehearsalReport` is the library entry point; `RehearsalReport` carries `passed`, `sim_success`, `steps_executed`, `trace_len`, `properties_checked`, the violations, and notes, plus a JSON-ready `to_payload()`.

### Reference: the MuJoCo backend (`urml_mujoco_runtime.recording`)

`RecordingMujocoAdapter(MujocoAdapter)` overrides the step loop to sample the engine per tick (`sample_every_n_steps` configurable); timestamps are the engine's own `data.time`. A declared `SignalMap` maps envelope signal names to readouts: a scalar `qpos`/`qvel`/`sensordata` index, a Euclidean norm over `qvel` components (the usual "speed"), or an openly pinned constant (`person_distance: 100.0` means "this rehearsal assumes nobody is present"). The map is the honest seam: which components mean "speed" is a property of the MJCF model, so the deployment declares it, and a map that lies produces a rehearsal that lies. Requires the `[sim]` extra; the adapter raises the existing actionable error without it.

### Reference: CLI

- `--rehearse [kinematic|mujoco]` (bare flag defaults to `kinematic`) and `--rehearse-config PATH` on **both** `urml execute` and the new `urml run`. The kinematic config YAML is a `KinematicProfile`; the mujoco config carries a `mujoco:` block (`MujocoConfig`) and a `signals:` map.
- **`urml run REQUEST --manifest ... [--envelope ...] [--rehearse ...] [--adapter mock|ros2|px4] [--out PATH]`**: the end-to-end verb. Translate through the bridge (which validates every emission with the caller's policy, honoring `--no-policy` for the demo posture), optionally write the accepted program, rehearse, execute. Missing optional packages produce the CLI's usual actionable exit-2 errors.
- Gate output prints the backend banner, sample/property counts, each violation with severity and time, and `gate: PASSED` / `gate: FAILED`; failure exits 1 before the real adapter is constructed.

### Spec changes

None to Layers 1 through 4 and no schema changes. The gate semantics above are normative at the tooling/runtime layer and lean entirely on RFC-0667's normative evaluation semantics; profiles and primitives are untouched.

### Validator changes

CLI only (`cli.py`: the rehearsal argument group, `_build_rehearsal_adapter`, `_run_rehearsal`, `cmd_run`). The validation passes themselves are unchanged.

### Reference runtime changes

`urml_ros2_runtime`: new `rehearsal.py` (gate, report, kinematic backend), exported from the package root. `urml_mujoco_runtime`: new `recording.py` (`RecordingMujocoAdapter`, `SignalMap`, `SignalSpec`, `load_signal_map`), exported. No frozen-protocol changes; `TraceRecorder` is a structural protocol satisfied by having `samples()`.

### Conformance suite changes

None in this PR. Gate behavior is pinned by package tests (`test_rehearsal.py`, `test_cli_run.py`, `test_recording.py`). Whether rehearsal outcomes belong in the conformance fixture schema rides on the same fixture `telemetry:` lane RFC-0667 declared as follow-on work.

## Backward compatibility

Fully additive. `urml execute` without `--rehearse` is unchanged; `urml run` is a new verb. Library surfaces are new exports only.

## Drawbacks

The kinematic backend's fidelity is exactly its declared profile, and a bare `--rehearse` uses defaults the deployment may not match; a user who does not read the banner can over-trust a synthetic pass. Rehearsal doubles intent execution (sim then real), which is time and, for the MuJoCo path, configuration effort: the `SignalMap` must be authored per model, and authoring it wrong silently degrades the gate (a lying map is called out in the docs but cannot be detected mechanically). `urml run` grows the CLI's surface and duplicates parts of `translate` and `execute` plumbing, which is a maintenance tax accepted for the headline one-verb story.

## Alternatives considered

**Gate on static analysis of the program plus manifest limits (no simulation).** The validator already does the static half; the failures this RFC targets are exactly the ones that only appear on a time-extended trace. Rejected as already-covered-or-impossible statically.

**MuJoCo-only rehearsal (no kinematic backend).** Highest fidelity, but the gate would vanish on every host without the `[sim]` extra, including CI and the bootstrap venv. A hermetic floor that always runs beats a high-fidelity gate that usually does not run; both ship, honestly labeled.

**A separate `urml rehearse` verb instead of a flag.** Considered; rejected because rehearsal's value is being *in the path* to execution: a standalone verb invites rehearsing and then executing without the gate. The flag composes; the report is still visible.

**Isaac-based rehearsal in v1.** The isaac-runtime adapter is hermetic mock-shaped today (no real engine wiring), so an Isaac backend would be a fake physics claim. Out of scope until the adapter is real.

## Prior art

RFC-0667 (the trace model and evaluator this gate consumes; the severity mapping it mirrors), RFC-0014 (the frozen protocol the backends implement), the MuJoCo runtime RFC lineage (RFC-0323/0328 sim substrates), and the repo's `_SUBSTRATE_NOTE` honesty discipline, extended here to rehearsal banners. Outside URML: pre-flight simulation checks in aviation autopilots, digital-twin commissioning in industrial automation (validate the cell program against the twin before the line runs), Gazebo/SITL "sim-first" workflows in ROS and PX4 practice, and the VerifyLLM/SafePlan research wave arguing LLM-produced plans need machine checking before actuation.

## Unresolved questions

- `SignalMap` authoring UX: per-deployment YAML today; whether canonical maps should ship beside canonical MJCF models, or the manifest should carry a readout declaration, is open.
- Whether a passed rehearsal should emit a signed, replayable artifact (trace hash + envelope + verdict) as an input to the future certification story.
- The normative wording of the sim-pass disclaimer once a certification program exists (today: banner text; a certificate needs sharper language about what was and was not proven).
- Fleet rehearsal (RFC-0286 rosters): multi-member traces need per-member signals and a cross-member spatial story; deferred.

## Implementation note

One vertical-slice PR, stacked on RFC-0667's PR (it consumes `urml_validator.monitor`): this RFC, `rehearsal.py` + tests, `recording.py` + tests (physics test skip-gated on the `[sim]` extra, `n/a` in the audit per discipline), the CLI flag + `urml run` + tests. The founder merges RFC-0667's PR first.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] This RFC adds no Layer-2 primitive (substrate-neutrality acid test not applicable; the gate runs on the frozen adapter surface, and both a ROS-free physics backend and a dependency-free backend ship).
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
