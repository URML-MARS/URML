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

# A learned policy's envelope travels with the model, and two checks gate it

Built for the ExecuTorch review on [pytorch/executorch#20268](https://github.com/pytorch/executorch/issues/20268), which described the clean integration in four steps and asked for exactly this example. No ExecuTorch change is requested or needed.

1. **Export the policy and its URML envelope together.** The manifest's `learned_policy` block (RFC-0383: trained command ranges, terrain classes, payload range) is written as a named blob under the key `urml/learned_policy.yaml` next to the `.pte`. ExecuTorch's named-data mechanism (`.pte`/`.ptd`, `NamedDataMap`) stores and returns those bytes; it attaches no robot meaning to them.
2. **Load and run with ExecuTorch.** The blob is read back by key and merged into the manifest.
3. **Interpret the outputs in the robotics application.** Here the policy maps an observation to `(linear_velocity_x, yaw_rate)`.
4. **Apply URML's checks before anything reaches the controller.** This is two checks, not one.

## The two checks

| | What it reads | What it catches | Where |
|---|---|---|---|
| **Check 1, static** | Declarations only: the trained envelope vs the deployment's admissible ceiling | A *deployment* that could ask the policy for more than it was trained for | RFC-0383, validator Pass 3, before any program is accepted |
| **Check 2, runtime** | Each action the policy proposes, plus the telemetry stream | A *policy* that emits more than the deployment allows, even when every declaration was coherent | RFC-0667 shield (`Shield` / `ShieldedAdapter`), at dispatch |

Neither subsumes the other. In this example `hot.envelope.yaml` (cap 1.5 m/s, above the trained 1.0 m/s) is refused by Check 1 with `capability.learned_policy_exceeds_training` and nothing runs. `deploy.envelope.yaml` (cap 0.8 m/s) passes Check 1, and then one observation makes the policy propose 1.2 m/s: Check 2 vetoes that single action before dispatch; the other four reach the adapter. This is the first example in the repository that exercises the RFC-0667 shield directly.

## Run it

Hermetic (no torch, no ExecuTorch; a fake bundle with the same keys, bytes, and order of operations; deterministic; the committed `executorch-policy-report.txt` is byte-asserted in CI):

```bash
python run_executorch_policy.py
```

Live (exports a real two-output `torch.nn.Module` with `executorch`, reloads it with the ExecuTorch Python runtime, reads the envelope blob back; requires `pip install torch executorch`):

```bash
python run_executorch_policy.py --live
```

First verified live run: 2026-08-20 with `executorch` 1.4.1 and `torch` 2.12 on Windows, producing the same report as the hermetic path (`NamedDataStore` for the envelope blob, `to_edge_transform_and_lower` for the export, `executorch.runtime.Runtime` for the reload and execution). The hermetic path remains the CI contract, because the live one needs a multi-gigabyte dependency set. Outputs land in `live/` (gitignored). One detail the live run taught us: a float32 model returns `0.5 * 1.6` as `0.8000000119`, which the shield correctly treats as over a 0.8 cap, so no synthetic observation sits exactly on the cap.

## Honesty lines

- ExecuTorch stores and returns bytes. The schema, the mapping from output tensors to commands, and every check are URML's responsibility, exactly as the maintainers framed it.
- The static check trusts the declaration, like every manifest field. The runtime check is what makes a wrong or incomplete declaration survivable.
- The fake policy is a fixed linear map chosen so that one observation exceeds the cap. A real policy's outputs are not this predictable, which is the whole argument for Check 2.
