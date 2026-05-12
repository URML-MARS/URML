# ROS 2 Reference Runtime

**Status:** Phase 1 in flight. **Skeleton + substrate Protocol + hermetic MockROSAdapter + end-to-end red-mug execution landed** at `0.1.0a0` (pre-alpha). The real `rclpy`-backed adapter is the next milestone.

## What this is

The **first** URML reference runtime. Translates a validated URML program into ROS 2 actions, services, and topics; honors declared capabilities and the active safety envelope at every step.

ROS 2 is the first reference runtime because its community is the largest — *not* because it is privileged. The substrate-neutrality acid test in [`CLAUDE.md`](../../CLAUDE.md) explicitly requires that every Layer-2 primitive be implementable on a runtime with **zero** ROS dependencies. This runtime is one of many possible Layer-0 targets.

## Substrate

- **ROS 2** (Humble, Iron, Jazzy, and later LTS releases). The runtime tracks LTS releases.
- **Nav2** for navigation primitives (`move_to`).
- **MoveIt 2** for manipulation primitives (`grasp`, arm control).
- Perception pipelines per profile (object detection for `detect`).

## Language

- **C++17** for nodes on the critical path (anything per-tick or per-message).
- **Python** for orchestration, the URML-to-ROS-2 compiler, tests, and the bridge to the validator.

Both follow the conventions in [`CLAUDE.md`](../../CLAUDE.md) §Working Conventions — type annotations, `mypy --strict` for Python, concepts where reasonable for C++.

## Conformance contract

This runtime is **conformant** when it passes the published conformance suite at the declared URML spec versions. Conformance is per-spec-version: a runtime that passes Layer-2 v0.1 but not Layer-2 v0.2 declares conformance to v0.1 and is honest about it.

The runtime ships its declared conformance in a `CONFORMANCE.md` file alongside this README when the first version cuts. Example:

```yaml
declares:
  layer-1-hal: 0.1.0
  layer-2-primitives: 0.1.0
  layer-3-behavior: 0.1.0
  layer-4-nl-grammar: 0.1.0
  profiles:
    home: 0.1.0
```

## Architecture (planned)

The runtime is a thin Layer-0 translator with three responsibilities:

1. **Validate.** Before executing anything, run the URML program through [`/reference/validator/`](../validator/) against the connected robot's capability manifest. If validation fails, the runtime refuses to execute and returns the structured error to whatever produced the program (often the LLM bridge).
2. **Translate.** Compile each primitive into its ROS-2 equivalent: `move_to(kitchen)` becomes a Nav2 `NavigateToPose` goal; `grasp(target, force: gentle)` becomes a MoveIt 2 plan with a configured gripper command; `detect(object: mug)` becomes a perception-pipeline query.
3. **Honor composition.** Implement Layer-3 sequence / branch / parallel / retry / on-error against ROS-2 lifecycle and action semantics.

The validator and the runtime are **separate processes** so that bypassing the validator at runtime is structurally hard, not merely discouraged.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — what manifests this runtime reads.
- [`/spec/layer-2-primitives/`](../../spec/layer-2-primitives/) — what primitives it compiles.
- [`/spec/layer-3-behavior/`](../../spec/layer-3-behavior/) — composition semantics it implements.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
