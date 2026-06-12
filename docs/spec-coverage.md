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

# URML spec-coverage audit

This document is the auditable proof that the URML standard is complete and
self-consistent: every construct the validator enforces has, per
[`CLAUDE.md`](../CLAUDE.md) §Code ("the bar"), all five legs —

> a spec document section, a JSON Schema, a reference implementation in at
> least one runtime, conformance tests, and a runnable example.

It is the spec-side analogue of [`docs/launch/claims-audit.md`](launch/claims-audit.md):
a claim ("the standard is complete") mapped cell-by-cell to the artifact that
backs it. It grows one layer at a time; regenerate the relevant section
whenever a construct is added or a leg moves.

- **[Layer 1 — capability manifest](#layer-1--capability-manifest)** — 12/12 covered.
- **[Layer 2 — intent primitives](#layer-2--intent-primitives)** — 20/20 covered.
- **[Layer 3 — behavior composition](#layer-3--behavior-composition)** — 6/6 covered.
- **[Layer 4 — natural-language prompt contract](#layer-4--natural-language-prompt-contract)** — 6/6 covered. *(Completes the layer set; URML is now normative end to end.)*

---

# Layer 2 — intent primitives

## Method

The authoritative primitive set is `PRIMITIVE_MODELS` in
[`reference/validator/src/urml_validator/schemas/primitives.py`](../reference/validator/src/urml_validator/schemas/primitives.py)
— twenty verbs: twelve core (RFC-0002) plus eight profile-scoped
(`speak`/`listen` home, `take_off`/`land`/`return_to_home` drone,
`pick_from`/`place_at`/`swap_tool` industrial — RFC-0013). Each leg is
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
  twenty). PX4 coverage is the RFC-0002-defined drone subset; see Notes.
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

All twenty-four primitives are fully covered. Fixture column cites one
representative fixture; most primitives have several (positive and negative).
The `arm` selector on `grasp`/`release` (RFC-0010) rides their existing rows;
it has its own fixtures (`biped/07_digit_arm_addressed_positive`,
`biped/08_arm_not_declared_rejected`).

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
| 18 | `pick_from` | v0.1.0 §3.6 | `PickFromArgs` | `exec_pick_from` | `industrial/04_pick_from_positive` | `industrial/pick-place-tool-change` |
| 19 | `place_at` | v0.1.0 §3.7 | `PlaceAtArgs` | `exec_place_at` | `industrial/04_pick_from_positive` | `industrial/pick-place-tool-change` |
| 20 | `swap_tool` | v0.1.0 §3.8 | `SwapToolArgs` | `exec_swap_tool` | `industrial/05_swap_tool_positive` | `industrial/pick-place-tool-change` |
| 21 | `call_program` | v0.1.0 §3.9 | `CallProgramArgs` | `exec_call_program` | `industrial/10_kawasaki_call_program_positive` | `industrial/kawasaki-as-program` |
| 22 | `bimanual` | v0.1.0 §3.10 | `BimanualArgs` | `exec_bimanual` | `biped/06_digit_bimanual_lift_positive` | `humanoid/digit-tote-lift` |
| 23 | `plan_path` | v0.1.0 §3.11 | `PlanPathArgs` | `exec_plan_path` | `av/01_plan_follow_positive` | `av/robotaxi-trip` |
| 24 | `follow_trajectory` | v0.1.0 §3.12 | `FollowTrajectoryArgs` | `exec_follow_trajectory` | `av/01_plan_follow_positive` | `av/robotaxi-trip` |
| 25 | `set_output` | v0.1.0 §3.13 | `SetOutputArgs` | `exec_set_output` | `actuation/01_set_output_digital_positive` | `cobot/glue-bead` |

## Notes (honest deferrals, not gaps)

- **PX4 runtime is a deliberate subset.** RFC-0002 §Reference-runtime-changes
  requires a drone runtime to implement only `move_to`, `hover`, `wait`,
  `wait_for`, `scan`, `capture`, `report`, `dock`, `measure`, plus the drone
  profile verbs; `grasp`/`release`/object-pickup `detect` are out of the drone
  profile by design. The "at least one runtime" bar is met by ros2-runtime for
  all twenty.
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
suite remain green (that PR does not touch runtime code).

---

# Layer 3 — behavior composition

The authoritative construct set is the composition schema in
[`reference/validator/.../schemas/composition.py`](../reference/validator/src/urml_validator/schemas/composition.py)
— four operators plus the `on_error` model and the variable system; condition
expressions are the sublanguage of `branch.condition` / `retry.until`. Legs:

- **Spec** — a normative section in
  [`spec/layer-3-behavior/v0.1.0.md`](../spec/layer-3-behavior/v0.1.0.md)
  (Layer 3 has no dedicated RFC; RFC-0002 deferred the formal grammar, so the
  spec is transcribed from the shipped implementation).
- **Schema** — a Pydantic model in `composition.py`
  (`Sequence`/`Branch`/`Parallel`/`Retry`/`Step`/`OnError`), part of the
  JSON-Schema export.
- **Impl** — a `_exec_*` method in
  [`reference/ros2-runtime/.../runtime.py`](../reference/ros2-runtime/src/urml_ros2_runtime/runtime.py),
  with the condition evaluator in `conditions.py` and binding resolution in
  `bindings.py`.
- **Conformance** — at least one fixture in
  [`conformance/fixtures/`](../conformance/fixtures/).
- **Example** — at least one runnable program in [`examples/`](../examples/),
  validated end-to-end with `urml validate`.

## What this audit found and closed

One real gap, closed in the PR that adds this section: **`branch`,
`parallel`, and `retry` had no runnable example.** Every shipped example
program was a flat `sequence`. Two new scenarios close it:
[`examples/home/patient-fetch`](../examples/home/patient-fetch.urml.yaml)
(retry + branch + nested sequence + variables + condition expressions) and
[`examples/drone/parallel-watch`](../examples/drone/parallel-watch.urml.yaml)
(parallel / `first_to_succeed` + wait_for). Both pass `urml validate`
end-to-end including the Pass-5 default policy. The sweep also wrote the
missing normative spec (`spec/layer-3-behavior/v0.1.0.md`) and corrected a
stale "Sequence-only skeleton" docstring in `runtime.py` that the code had
long outgrown.

## The matrix

All six constructs are fully covered.

| Construct | Spec | Schema | Impl (ros2) | Conformance | Example |
|---|---|---|---|---|---|
| `sequence` | v0.1.0 §2.1 | `Sequence` | `_exec_sequence` | `home/01_red_mug_positive` | `home/red-mug` |
| `branch` | v0.1.0 §2.2 | `Branch` | `_exec_branch` | `home/04_branch_on_color` | `home/patient-fetch` |
| `parallel` | v0.1.0 §2.3 | `Parallel` | `_exec_parallel` | `home/06_parallel_first_to_succeed` | `drone/parallel-watch` |
| `retry` | v0.1.0 §2.4 | `Retry` | `_exec_retry` | `home/05_retry_until_confidence` | `home/patient-fetch` |
| `on_error` | v0.1.0 §3 | `OnError` | `_exec_sequence` | `home/02_red_mug_nav_failure` | `home/red-mug` |
| variables (`store_as`/`$ref`) | v0.1.0 §4–5 | Pass 4 / `conditions.py` | `bindings.py` | `home/04_branch_on_color` | `home/patient-fetch` |

## Notes (honest deferrals, not gaps)

- **`on_error: substitute(other_behavior)`** is sketched in the README but
  **not** in v0.1; the shipped `OnError` enum is exactly
  `abort_and_report | continue | retry`. `v0.1.0.md` §3 says so plainly.
- **Condition expressions are not statically validated in v0.1.** A malformed
  `condition`/`until` is caught at execution, not by the validator. Documented
  future tightening (`v0.1.0.md` §5–6), not a hidden gap.
- **Definite-assignment across branch/parallel/retry arms** is approximated by
  a permissive linear walk in Pass 4; the stricter analysis is deferred
  (`v0.1.0.md` §4, §6).
- **JSON-LD encoding** named in the README is deferred; YAML is the only
  normative surface in v0.1.

## Verification

```
# new Layer-3 examples validate end-to-end (incl. Pass-5 policy)
urml validate examples/home/patient-fetch.urml.yaml \
  -m examples/home/patient-fetch.manifest.yaml --profile home
urml validate examples/drone/parallel-watch.urml.yaml \
  -m examples/drone/parallel-watch.manifest.yaml --profile drone
```

Both print `Validation passed`. The validator and conformance suites remain
green; the only runtime touch is a docstring correction in `runtime.py`.

---

# Layer 1 — capability manifest

The authoritative block set is the manifest schema in
[`reference/validator/.../schemas/manifest.py`](../reference/validator/src/urml_validator/schemas/manifest.py)
(plus `connectivity.py`). "Construct" here is a manifest block. Legs:

- **Spec** — a normative section in
  [`spec/layer-1-hal/v0.1.0.md`](../spec/layer-1-hal/v0.1.0.md); the Pass-5
  policy that consumes `provenance` is specified in
  [`spec/layer-1-hal/policy.md`](../spec/layer-1-hal/policy.md).
- **Schema** — a Pydantic model in `manifest.py` / `connectivity.py`.
- **Consumer** — the validator pass that enforces the block (Pass 2 capability
  / Pass 3 envelope / Pass 5 policy), in
  [`reference/validator/.../validator.py`](../reference/validator/src/urml_validator/validator.py).
- **Conformance** — a fixture manifest that exercises the block.
- **Example** — an example manifest in [`examples/`](../examples/) that
  declares the block, validated end-to-end with `urml validate`.

## What this audit found and closed

One real gap, closed in the PR that adds this section: **no example manifest
declared a `connectivity:` block.** Eleven of the twelve blocks appeared in
the nine shipped example manifests; `connectivity:` (RFC-0006) appeared in
zero, though it is schema-defined, validator-enforced (Pass 2 + Pass 3), and
covered by validator fixtures. A new scenario closes it:
[`examples/drone/link-aware-patrol`](../examples/drone/link-aware-patrol.urml.yaml)
— a manifest declaring a required `command_link` plus a companion
`*.envelope.yaml` declaring a `return_to_home` link-loss policy; it passes
`urml validate` end-to-end including the Pass-5 default policy.

## The matrix

All twelve blocks are covered.

| Block | Spec | Schema | Consumer | Conformance | Example |
|---|---|---|---|---|---|
| `manifest_version` / `robot_id` | v0.1.0 §2 | `CapabilityManifest` | Pass 1 | all manifests | `home/red-mug` |
| `frames` | v0.1.0 §2.1 | `Frame` | Pass 2 | all manifests | `home/red-mug` |
| `declared_locations` | v0.1.0 §2.2 | `DeclaredLocation` | Pass 2 | all manifests | `home/red-mug` |
| `declared_events` | v0.1.0 §2.3 | `CapabilityManifest` | Pass 2 (`wait_for`) | `home/11_emergency_stop_handling` | `home/evening-routine` |
| `mobility` | v0.1.0 §2.4 | `Mobility` | Pass 2 (`move_to`/`hover`/…) | all motion fixtures | `home/red-mug` |
| `manipulation` | v0.1.0 §2.5 | `Manipulation`/`Gripper` | Pass 2 (`grasp`/`release`) | `home/01_red_mug_positive` | `home/red-mug` |
| `perception` | v0.1.0 §2.6 | `Perception`/`Camera`/`Sensor` | Pass 2 (`detect`/`scan`/…) | `drone/06_measure_positive` | `drone/bridge-survey` |
| `docking_stations` | v0.1.0 §2.7 | `DockingStation` | Pass 2 (`dock`) | `home/13_dock_positive` | `home/evening-routine` |
| `outputs` (`named_endpoints`) | v0.1.0 §2.8 | `Outputs` | Pass 2 (`report`/`speak`) | `industrial/01_pick_red_positive` | `home/evening-routine` |
| `outputs.lines` (RFC-0017) | v0.2.0 §2.8 | `OutputLine` | Pass 2 (`set_output`) | `actuation/01_set_output_digital_positive` | `cobot/glue-bead` |
| `provenance` | v0.1.0 §2.9 + `policy.md` | `Provenance` | Pass 5 | `home/07_policy_country_denied` | `home/red-mug` |
| HBOM-content predicates (RFC-0005) | `policy.md` Predicates | `RulePredicate.hbom_no_components_from_*` / `hbom.py` | Pass 5 (HBOM sub-pass) | `compliance/02_hbom_cn_chip_rejected` | `compliance/hidden-cn-chip` |
| `connectivity` | v0.1.0 §2.10 | `Connectivity`/`DeclaredLink` | Pass 2 + Pass 3 | `drone/10_link_role_undeclared_rejected` | `drone/link-aware-patrol` |
| `link_loss_policy` (envelope side) | v0.1.0 §2.10 | `LinkLossRule` | Pass 3 | `drone/13_link_loss_rth_positive` | `drone/link-aware-patrol` |
| `minimal_node` (RFC-0018) | v0.2.0 §2.17 | `MinimalNode` | Pass 2 (mobility XOR, output/sensor cross-ref) | `educational/08_minimal_node_led_positive` | `educational/blink-the-led` |

## Notes (honest deferrals, not gaps)

- **No URDF/SDF cross-reference.** The manifest has no `urdf_ref:` and the
  validator performs no manifest↔URDF frame check. Stated in `v0.1.0.md` §5;
  a candidate future RFC, not a hidden gap.
- **Safety envelope is a separate artifact.** Specified at deployment time
  (`envelope.py` + profile defaults), referenced by Layer 1, not part of
  `CapabilityManifest` (`v0.1.0.md` §1.2). The `link_loss_policy` row above is
  the envelope side, included because Pass 3 conjoins it with the manifest
  `connectivity` block.
- **HBOM opaque, hash unverified, `manifest_version` fixed `"0.1"`.** Recorded
  in `v0.1.0.md` §5; deliberate v0.1 scope lines.

## Verification

```
urml validate examples/drone/link-aware-patrol.urml.yaml \
  -m examples/drone/link-aware-patrol.manifest.yaml \
  --envelope examples/drone/link-aware-patrol.envelope.yaml --profile drone
```

Prints `Validation passed`. The validator and conformance suites remain
green; this section's PR touches no runtime code.

---

# Layer 4 — natural-language prompt contract

The authoritative surface is [`reference/llm-bridge/`](../reference/llm-bridge/)
— the published, provider-neutral contract for translating natural language
into validated URML. "Construct" here is a contract element. Legs:

- **Spec** — a normative section in
  [`spec/layer-4-nl-grammar/v0.1.0.md`](../spec/layer-4-nl-grammar/v0.1.0.md)
  (Layer 4 has no dedicated RFC; the contract is the shipped bridge).
- **Schema/contract artifact** — the Pydantic/code surface in
  `reference/llm-bridge/src/urml_llm_bridge/`.
- **Impl** — the same module (the bridge *is* the reference implementation).
- **Conformance** — a test in
  [`reference/llm-bridge/tests/`](../reference/llm-bridge/tests/).
- **Example** — a runnable artifact: the paired
  [`examples/`](../examples/) `*.en.txt` ↔ `*.urml.yaml` scenarios (the
  human-facing few-shot fixtures) and the hermetic walkthrough
  [`docs/demos/bridge-roundtrip.md`](demos/bridge-roundtrip.md).

## What this audit found and closed

One real gap, closed in the PR that adds this section: **no runnable
walkthrough of the prompt contract / bridge round-trip.** The validator has
`docs/demos/compliance-walkthrough.md` and `safety-rejection.md`; Layer 4 had
no equivalent — `urml emit-prompt` and the hermetic `urml translate --provider
echo` shipped but were undiscoverable. [`docs/demos/bridge-roundtrip.md`](demos/bridge-roundtrip.md)
closes it: a verified, no-network walkthrough (emit the contract → echo-backed
round-trip → the revision-loop reference). The sweep also wrote the missing
normative spec and corrected two stale status claims (the `llm-bridge`
README's "Phase 1 in flight / 0.1.0a0 pre-alpha / CLI is next milestone", and
its item 7 over-promising an interactive disambiguation protocol).

## The matrix

All six contract elements are covered.

| Construct | Spec | Artifact | Impl | Conformance | Example |
|---|---|---|---|---|---|
| Program JSON Schema (emission target) | v0.1.0 §2 | `urml_validator.export_schema` | `bridge.py` (`_schema`) | validator schema-export guard | all 8 `examples/*` pairs |
| System-prompt assembly | v0.1.0 §2 | `prompt.py` | `build_system_prompt` | `test_emit_prompt_cli` | `docs/demos/bridge-roundtrip.md` |
| Few-shot library | v0.1.0 §2.2 | `few_shot.py` | `few_shots_for` | `test_few_shot_library` | `examples/home/red-mug` (+ profile sets) |
| Validator-feedback revision loop | v0.1.0 §3 | `bridge.py` | `Bridge.translate` | `test_bridge` | `docs/demos/bridge-roundtrip.md` |
| Provider-neutral interface | v0.1.0 §1 | `providers/base.py` | `LLMProvider` + echo/anthropic/openai | `test_providers_*` | `EchoProvider` (the demo) |
| Policy short-circuit (RFC-0004) | v0.1.0 §3 | `bridge.py` | `BridgePolicyViolation` | `test_bridge` | `home/red-mug` (compliant manifest) |

## Notes (honest deferrals, not gaps)

- **No interactive disambiguation protocol in v0.1.** The README family
  described "structured questions the LLM asks when ambiguous"; the shipped
  bridge is one-shot emit + the deterministic validator-feedback loop.
  Ambiguity → manifest-grounded default, or `report(status: failure)`. Stated
  in `v0.1.0.md` §5; the `llm-bridge` README item 7 was corrected to match.
- **Multilingual is structural, not content.** `<scenario>.<lang>.txt` slots
  are reserved; v0.1 content is English-only. The contract is
  language-agnostic; no schema/loop change is needed for non-English input.
- **The bridge does not execute URML.** It returns validated programs;
  execution is the caller's job.

## Verification

```
# the contract the model is given (no network)
urml emit-prompt -m examples/home/red-mug.manifest.yaml --profile home

# a hermetic NL -> validated-URML round-trip (no API key)
urml translate "Bring me the red mug from the kitchen." \
  -m examples/home/red-mug.manifest.yaml --profile home \
  --provider echo --echo-response-file /tmp/echo_redmug.json
```

The second prints `Translation accepted after 0 revision(s)`. The
llm-bridge, validator, and conformance suites remain green; this section's
PR touches no runtime code.

---

*The layer set is complete: Layers 1–4 each have a normative `v0.1.0.md`, a
schema, a reference implementation, conformance tests, and a runnable example.
URML is normative end to end, and every public completeness claim is
cell-backed here.*
