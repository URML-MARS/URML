# Validator

**Status:** Pre-implementation. Phase 1 target.

## What this is

The static verification engine for URML. Given a URML program, a Layer-1 capability manifest for the target robot, and the active safety envelope, the validator returns one of two outcomes:

1. **Accepted** — the program is statically valid; the runtime may execute it.
2. **Rejected with a structured error** — the program fails one or more checks; the error is a machine-readable object that a calling tool (often the LLM bridge) can use to revise the program.

The validator is **the safety boundary**. Per [`MANIFESTO.md`](../../MANIFESTO.md) §Design Principles and [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do:

> *URML programs are executed only after static verification against the target's capability manifest and active safety envelope. Any "fast path" that skips verification is rejected on review.*

Bypassing the validator is structurally hard because the validator and the runtimes are **separate processes**. A runtime that wanted to skip validation would have to be modified, not merely flagged.

## What the validator checks

When fully implemented, the validator runs these checks against every URML program:

### Layer-3 (composition) checks

- The program parses as valid URML against the layer-3 grammar.
- Every composition operator is well-formed (no empty parallel, no retry with negative bound, no `on_error: substitute` referencing an undefined behavior).
- Every `$variable` reference resolves to a prior `store_as`.
- Types match across producer/consumer primitives.

### Layer-2 (primitive) checks

- Every primitive is in the spec (or in a profile the program declares).
- Every primitive's required arguments are present and well-typed.
- Profile-specific argument constraints are honored (e.g., drone-profile `move_to` declares altitude).

### Layer-1 (capability) checks

- The robot's manifest declares every capability the program needs (mobility, manipulation, perception, declared frames, declared locations).
- Every named location in the program resolves in the manifest or the world model the manifest references.

### Safety-envelope checks

- Every declared limit is honored: max velocity, max payload, max force, max altitude, geofence, force ceilings, no-go zones, link-loss policy.
- Profile-specific envelope checks (drone people-occupancy, industrial cell perimeter, home people-only zones) are applied for whichever profiles the program declares.

## What the validator does NOT do

- It does not execute the program. That is the runtime's job.
- It does not parse natural language. That is the LLM bridge's job.
- It does not generate the URML program. That is an LLM's job, via the LLM bridge.
- It does not monitor runtime state. Run-time safety (an unexpected obstacle, a sudden wind gust, a person walking into the cell) is the substrate's job. The validator is **static**; the substrate is **dynamic**. Both are required for safety.

## Language

- **Python**, primary implementation. `mypy --strict`. Public API fully type-annotated.
- A long-running validator service (e.g., as a sidecar to multiple runtimes in production) may eventually be backed by **Rust** for deployment ergonomics; the Python implementation remains the reference.

## API (sketch)

```python
from urml.validator import validate, ValidationResult

result: ValidationResult = validate(
    program=program_yaml,         # str or parsed dict
    manifest=manifest_yaml,        # str or parsed dict
    envelope=envelope_yaml,        # str or parsed dict
    profiles=("home",),            # which profiles the program declares
    spec_versions={
        "layer-1-hal": "0.1.0",
        "layer-2-primitives": "0.1.0",
        "layer-3-behavior": "0.1.0",
    },
)

if result.accepted:
    runtime.execute(result.program)
else:
    # result.errors is a list of structured errors,
    # designed to be readable by an LLM and used for revision.
    llm_bridge.revise(program_yaml, result.errors)
```

## Core Commitment

The validator is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. The safety guarantees of URML flow through this component; gating it behind a license would forfeit them.

## Related documents

- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema.
- [`/spec/layer-2-primitives/`](../../spec/layer-2-primitives/) — primitive contracts.
- [`/spec/layer-3-behavior/`](../../spec/layer-3-behavior/) — composition grammar.
- [`/reference/llm-bridge/`](../llm-bridge/) — the primary consumer of structured validation errors.
- [`/conformance/`](../../conformance/) — uses the validator as part of its end-to-end tests.
