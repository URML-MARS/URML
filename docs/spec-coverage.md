# Layer-2 primitive coverage audit

This document is the auditable proof that the URML standard is complete and
self-consistent: every Layer-2 primitive that the validator enforces has, per
[`CLAUDE.md`](../CLAUDE.md) §Code ("the bar"), all five legs —

> a spec document section, a JSON Schema, a reference implementation in at
> least one runtime, conformance tests, and a runnable example.

It is the spec-side analogue of [`docs/launch/claims-audit.md`](launch/claims-audit.md):
a claim ("Layer 2 is complete") mapped cell-by-cell to the artifact that backs
it. Regenerate it whenever a primitive is added or a leg moves.

## Method

The authoritative primitive set is `PRIMITIVE_MODELS` in
[`reference/validator/src/urml_validator/schemas/primitives.py`](../reference/validator/src/urml_validator/schemas/primitives.py)
— seventeen verbs: twelve core (RFC-0002) plus five profile-scoped
(`speak`/`listen` home, `take_off`/`land`/`return_to_home` drone). Each leg is
verified by path:

- **Spec** — a normative section in
  [`spec/layer-2-primitives/v0.1.0.md`](../spec/layer-2-primitives/v0.1.0.md),
  transcribed from the [RFC-0002](rfcs/0002-initial-primitive-vocabulary.md)
  decision record (and the profile READMEs for the five profile verbs).
- **Schema** — a Pydantic arg-model in `schemas/primitives.py`, exported as
  JSON Schema via `schema_export.py` and regression-guarded by the validator
  suite.
- **Impl** — a `PRIMITIVE_EXECUTORS` entry in
  [`reference/ros2-runtime/.../primitives.py`](../reference/ros2-runtime/src/urml_ros2_runtime/primitives.py)
  (the bar requires "at least one runtime"; ros2-runtime implements all
  seventeen). PX4 coverage is the RFC-0002-defined drone subset; see Notes.
- **Conformance** — at least one fixture in
  [`conformance/fixtures/`](../conformance/fixtures/) exercising the primitive.
- **Example** — at least one runnable program in
  [`examples/`](../examples/), validated end-to-end with `urml validate`.

## What this audit found and closed

Two real gaps, both closed in the PR that adds this document:

1. **RFC-0002 criterion 1 was unmet.** RFC-0002 §Implementation-Note requires
   a normative spec document at `/spec/layer-2-primitives/v0.1.0.md`. It was
   never written — Layer-2's normative text lived only inside the RFC and was
   mirrored ad hoc in profile READMEs. The validator (criterion 2), ros2
   runtime (3), conformance suite (4), and red-mug example header (5) were all
   done. The missing normative doc was the only thing honestly holding
   RFC-0002 at `Accepted`. `v0.1.0.md` closes it; all five criteria are now
   met and RFC-0002 advances to `Implemented`.
2. **Eight primitives had no runnable example.** `dock`, `hover`, `wait`,
   `wait_for`, `scan`, `measure`, `speak`, `listen` had conformance fixtures
   but no `/examples` program — the bar lists conformance and examples as
   distinct legs. Two new cohesive scenarios close this:
   [`examples/home/evening-routine`](../examples/home/evening-routine.urml.yaml)
   (speak/listen/wait_for/dock/wait) and
   [`examples/drone/bridge-survey`](../examples/drone/bridge-survey.urml.yaml)
   (scan/hover/measure). Both pass `urml validate` end-to-end including the
   Pass-5 default policy.

## The matrix

All seventeen primitives are fully covered. Fixture column cites one
representative fixture; most primitives have several (positive and negative).

| # | Primitive | Spec | Schema | Impl (ros2) | Conformance (representative) | Example |
|---|---|---|---|---|---|---|
| 1 | `move_to` | v0.1.0 §2.1 | `MoveToArgs` | `exec_move_to` | `home/01_red_mug_positive` | `home/red-mug` |
| 2 | `dock` | v0.1.0 §2.2 | `DockArgs` | `exec_dock` | `home/13_dock_positive` | `home/evening-routine` |
| 3 | `hover` | v0.1.0 §2.3 | `HoverArgs` | `exec_hover` | `drone/04_hover_positive` | `drone/bridge-survey` |
| 4 | `wait` | v0.1.0 §2.4 | `WaitArgs` | `exec_wait` | `drone/13_link_loss_rth_positive` | `home/evening-routine` |
| 5 | `wait_for` | v0.1.0 §2.5 | `WaitForArgs` | `exec_wait_for` | `home/11_emergency_stop_handling` | `home/evening-routine` |
| 6 | `grasp` | v0.1.0 §2.6 | `GraspArgs` | `exec_grasp` | `home/01_red_mug_positive` | `home/red-mug` |
| 7 | `release` | v0.1.0 §2.7 | `ReleaseArgs` | `exec_release` | `home/01_red_mug_positive` | `home/red-mug` |
| 8 | `detect` | v0.1.0 §2.8 | `DetectArgs` | `exec_detect` | `home/01_red_mug_positive` | `home/red-mug` |
| 9 | `scan` | v0.1.0 §2.9 | `ScanArgs` | `exec_scan` | `drone/05_scan_positive` | `drone/bridge-survey` |
| 10 | `measure` | v0.1.0 §2.10 | `MeasureArgs` | `exec_measure` | `drone/06_measure_positive` | `drone/bridge-survey` |
| 11 | `capture` | v0.1.0 §2.11 | `CaptureArgs` | `exec_capture` | `drone/01_inspect_roof_positive` | `drone/roof-inspection` |
| 12 | `report` | v0.1.0 §2.12 | `ReportArgs` | `exec_report` | `industrial/01_pick_red_positive` | `industrial/simple-pick-and-place` |
| 13 | `speak` | v0.1.0 §3.1 | `SpeakArgs` | `exec_speak` | `home/10_speak_listen_conversation` | `home/evening-routine` |
| 14 | `listen` | v0.1.0 §3.2 | `ListenArgs` | `exec_listen` | `home/10_speak_listen_conversation` | `home/evening-routine` |
| 15 | `take_off` | v0.1.0 §3.3 | `TakeOffArgs` | `exec_take_off` | `drone/01_inspect_roof_positive` | `drone/roof-inspection` |
| 16 | `land` | v0.1.0 §3.4 | `LandArgs` | `exec_land` | `drone/01_inspect_roof_positive` | `drone/roof-inspection` |
| 17 | `return_to_home` | v0.1.0 §3.5 | `ReturnToHomeArgs` | `exec_return_to_home` | `drone/13_link_loss_rth_positive` | `drone/roof-inspection` |

## Notes (honest deferrals, not gaps)

- **PX4 runtime is a deliberate subset.** RFC-0002 §Reference-runtime-changes
  requires a drone runtime to implement only `move_to`, `hover`, `wait`,
  `wait_for`, `scan`, `capture`, `report`, `dock`, `measure`, plus the drone
  profile verbs; `grasp`/`release`/object-pickup `detect` are out of the drone
  profile by design. The "at least one runtime" bar is met by ros2-runtime for
  all seventeen.
- **`PX4Adapter.run_scan` is a v0.1 stub.** It returns a documented
  not-yet-implemented result; full waypoint-expansion + capture needs a
  companion adapter (see px4-runtime README and `CompositeAdapter`). This is
  disclosed in code, not hidden. ros2-runtime's `exec_scan` is the conformant
  reference.
- **`spec/layer-2-primitives/README.md` is orientation, not the spec.** The
  normative text is `v0.1.0.md`; the README points to it.
- **Validator passes.** RFC-0002 described four; the shipped validator runs
  five (Pass 5 / policy from RFC-0004; connectivity coherence from RFC-0006).
  `v0.1.0.md` §1.2 documents the shipped five, which is the normative
  reference.

## Verification

Reproduce this audit:

```
# primitive set
python -c "from urml_validator.schemas.primitives import PRIMITIVE_NAMES; print(PRIMITIVE_NAMES)"

# new examples validate end-to-end (incl. Pass-5 policy)
urml validate examples/home/evening-routine.urml.yaml \
  -m examples/home/evening-routine.manifest.yaml --profile home
urml validate examples/drone/bridge-survey.urml.yaml \
  -m examples/drone/bridge-survey.manifest.yaml --profile drone
```

Both print `Validation passed`. The five package suites and the conformance
suite remain green (the PR does not touch runtime code).
