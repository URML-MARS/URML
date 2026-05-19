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

# Conformance Declaration

The `urml-ros2-runtime` package declares the following URML spec versions covered by the public conformance suite. This file is the format every URML-compatible runtime ships at the root of its repository; see [`docs/registry/SUBMISSION.md`](../../docs/registry/SUBMISSION.md) in the main URML repo for the submission flow.

```yaml
declares:
  layer-1-hal: 0.1.0
  layer-2-primitives: 0.1.0
  layer-3-behavior: 0.1.0
  layer-4-nl-grammar: 0.1.0
  profiles:
    home: 0.1.0
    drone: 0.1.0
```

## How to verify

From the repository root:

```bash
pip install -e reference/validator
pip install -e reference/ros2-runtime
pip install -e conformance
urml conformance run --output conformance-report.json
```

A passing run produces a JSON `ConformanceReport` with `all_passed: true` and one `CaseResult` per fixture. The bundled fixture set covers home, drone, and one industrial case (driven through the core primitives).

## Substrate

This is the ROS 2 reference runtime. It uses the hermetic `MockROSAdapter` by default. A real `RclpyAdapter` is in flight (see [`reference/ros2-runtime/INTEGRATION.md`](INTEGRATION.md)) and will share the same fixture set when it lands.

## Status

Phase 1 in flight. This declaration tracks the runtime's actual coverage; if a fixture starts failing for any of the declared layers or profiles, this file is updated in the same PR that fixes (or accepts) the change.

## Why this file lives here

`CONFORMANCE.md` is the public record a third-party reviewer reads when deciding whether a runtime's conformance claim is honest. It must match the JSON report from the most recent suite run and the runtime's commit at which the report was produced. Mismatches between this file, the JSON report, and the runtime's actual behavior are bugs.

## Registry status

This runtime is the reference runtime and is intentionally **not** listed in [`docs/compatible-runtimes.md`](../../docs/compatible-runtimes.md) during Phase 0. The registry exists for third-party runtimes; listing the reference runtime as the only entry would defeat the purpose. The reference runtime will be added once at least one third-party submission is merged.
