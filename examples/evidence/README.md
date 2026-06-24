# Per-capability evidence traceability (RFC-0631)

A manifest capability claim ("this gripper closes to 40 N", "this lidar reaches
25 m") is otherwise an assertion the validator is forced to trust. RFC-0631 adds
an optional `evidence` tag so a claim records **how it was established**:

| source     | meaning                                                        |
|------------|----------------------------------------------------------------|
| `verified` | confirmed by a runtime smoke test or measurement (strongest)   |
| `derived`  | extracted from a structural robot description (USD, URDF, SDF) |
| `declared` | hand-asserted by the integrator (honest, unchecked)            |
| `inferred` | guessed by an LLM or heuristic (weakest)                       |

The tag also carries an optional structured `ref` (`{kind, value}`, where `kind`
is `usd_prim` / `urdf_link` / `test` / `url`) and a free-text `note`.

This example shows both halves:

1. **Evidence is advisory.** [`usd-derived.manifest.yaml`](usd-derived.manifest.yaml)
   tags every curated capability, but with no policy the tags change no
   validation outcome.
2. **A deployment opts in.** [`evidence-policy.yaml`](evidence-policy.yaml) turns
   the tags into a gate: a gripper's force range and the mobility envelope must
   be `derived` or `verified`, a sensor's range at least `derived`, and a camera
   below that bar is flagged. The hand-declared bumper is refused; the
   LLM-inferred camera is warned about; the USD-derived and smoke-verified claims
   pass.

Run it:

```sh
python examples/evidence/trace_evidence.py
```

The output is deterministic and byte-asserted in
[`evidence-report.txt`](evidence-report.txt) by
`reference/validator/tests/test_evidence_example.py`.

Motivated by NVIDIA Isaac's review on
[isaac-sim/IsaacSim#649](https://github.com/isaac-sim/IsaacSim/issues/649): a
USD-derivation tool stamps `source: derived` with the originating prim path; a
smoke-test harness stamps `source: verified`; a hand-authored field stays honest
as `declared`.
