---
rfc: 0383
title: learned_policy, declaring the envelope a learned controller was trained under
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-04
updated: 2026-08-20
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

# RFC-0383: `learned_policy`, declaring a learned controller's training envelope

## Summary

A growing share of URML's substrate targets are learned locomotion and manipulation policies: a neural controller trained in simulation owns the gait or the grasp, and URML sits above it as the validated-intent layer. A learned policy is only valid inside the distribution it was trained on. A biped walk policy trained for commands up to 1.0 m/s over flat-to-mild terrain has undefined behavior at 2.5 m/s on stairs. URML's static gate is the natural place to refuse intent outside that distribution, but URML v0.1 has no way for a manifest to declare what the policy was trained for. This RFC adds an optional Layer-1 manifest block, `learned_policy`, declaring the training envelope: command ranges, terrain classes, and payload range the policy was trained and validated under. The validator rejects (or warns on) Layer-2 intent whose implied command exceeds the declared training envelope. How a training framework *exports* these limits is out of scope; URML defines the declaration and two separate checks against it: a static declaration check before any program is accepted, and a per-action runtime shield (RFC-0667) at dispatch. No primitive changes. Backward compatible (additive optional block).

The surface that demanded this RFC is the recurring "learned-policy-as-substrate" framing across Move #28 and Move #29, and the specific question from the rsl_rl maintainer on [RFC-0377](0377-rsl-rl-outreach.md): could a trained policy export the limits it was trained under? Sibling threads: [RFC-0380 (rl_games)](0380-rl-games-outreach.md), [RFC-0376 (legged_gym)](0376-legged-gym-outreach.md), [RFC-0373 (Open Duck Mini)](0373-open-duck-mini-outreach.md), [RFC-0369 (OmniSafe)](0369-omnisafe-outreach.md), [RFC-0360 (robomimic)](0360-robomimic-outreach.md).

## Motivation

URML's identity is "validate before you move." For a classical controller, the manifest declares capability (max velocity, reachable workspace) and the validator checks intent against it. A learned controller breaks that cleanly: its real limit is not a mechanical maximum, it is the edge of its training distribution, and outside that edge its behavior is not just slower or weaker, it is undefined. A walk policy commanded beyond its trained speed does not gracefully saturate; it can fall.

The ML ecosystem URML is engaging makes this concrete. When URML reached rsl_rl (ETH's on-policy RL library behind many Isaac locomotion policies), the maintainer's substantive answer was that the training-limits metadata (terrain, command ranges) belongs alongside the policy, exported from the task definition. legged_gym, rl_games, Open Duck Mini, OmniSafe, and robomimic all sit at the same boundary: the trained policy is the substrate, and URML bounds the intent handed to it. Across all of them the same question recurs, framed in this RFC's terms: what should a manifest declare so URML can refuse intent the policy was never trained to handle?

Three concrete consequences of the gap:

1. **URML cannot honestly bound a learned substrate.** It can check intent against a mechanical `max_velocity`, but the policy's *trained* velocity is a tighter and more meaningful bound that URML has no field for. The static gate is checking the wrong limit, and nothing at runtime is checking the policy's actual outputs against the right one.
2. **The learned-policy engagements have no anchor.** Every "learned-policy-as-substrate" RFC pitches URML as the layer that respects the policy's competence boundary. That pitch needs a manifest field to be real.
3. **It is the same move URML already makes, applied to a new substrate.** URML declares capability and refuses intent that exceeds it. A training envelope is just the capability of a learned controller, expressed in the terms that controller's validity is defined by.

## Detailed design

### Field shape

Add an optional `learned_policy` block to the Layer-1 capability-manifest schema. It declares the envelope a learned controller was trained and validated under.

```yaml
learned_policy:
  policy_ref: "isaac-lab://anymal-flat-v3"      # opaque handle to the policy
  command_ranges:
    - quantity: linear_velocity_x
      min: -0.5
      max: 1.0
      unit: m_per_s
    - quantity: yaw_rate
      min: -1.0
      max: 1.0
      unit: rad_per_s
  terrain_classes: [rigid, deformable]           # reuses RFC-0381's terrain enum
  payload_range: { min: 0.0, max: 5.0, unit: kg }
  enforcement: reject                            # reject | warn
```

The `learned_policy` block is **optional**. A manifest without it validates exactly as today. A manifest that declares it opts the deployment into training-envelope checking.

| Field | Type | Meaning |
|---|---|---|
| `policy_ref` | string | Opaque handle to the policy artifact (URI, registry id, file path); documentation, not parsed |
| `command_ranges` | list | Per-quantity `{quantity, min, max, unit}` the policy was trained over |
| `terrain_classes` | list of RFC-0381 `terrain_fidelity` values | Terrain the policy was trained and validated on |
| `payload_range` | `{min, max, unit}` (optional) | Payload mass range the policy was trained under |
| `enforcement` | `reject` / `warn` | Whether out-of-envelope intent is a validation error or a warning |

`quantity` is drawn from a small closed set of command quantities (`linear_velocity_x`, `linear_velocity_y`, `yaw_rate`, and the manipulation analogs as they are needed), so the validator can map a Layer-2 intent's implied command to a declared range.

### Validator behavior

`urml validate` adds, when `learned_policy` is present:

1. **Command-range check.** For each Layer-2 primitive whose dispatch implies one of the declared command quantities (a `move_to` implying a commanded velocity, for example), the validator checks the implied command against the declared range. An intent that exceeds the range fails (when `enforcement: reject`) or warns (when `warn`), with a clear message naming the quantity, the requested value, and the trained bound, and pointing to this RFC.
2. **Terrain coherence.** If the manifest also declares `validation.terrain_fidelity` (RFC-0381), the validator checks it is within `learned_policy.terrain_classes`; a deployment running a policy on terrain it was not trained for is flagged.
3. **Strictest-wins with mechanical limits.** The training envelope conjoins with the manifest's mechanical `mobility.max_velocity` and the safety envelope's `max_velocity`, strictest-wins (the existing Pass-3 machinery). The trained bound is usually the tightest, which is the point.
4. **Enum and shape checks.** `quantity`, `terrain_classes`, and units are validated against their closed sets; unknown values fail.

The validator does **not** load, run, or introspect the policy. `policy_ref` is opaque. The static check compares *declarations* against *declarations*; whether the declaration is true is the training framework's responsibility, exactly as a manifest's `max_velocity` is trusted today. What the policy actually emits at runtime is the second check's job, below.

### Two checks, not one

This RFC and RFC-0667 together describe **two separate mechanisms**, and earlier text here read as if there were one. Stated plainly (amended 2026-08-20, prompted by the ExecuTorch maintainers' review on [pytorch/executorch#20268](https://github.com/pytorch/executorch/issues/20268)):

1. **Check 1, static, this RFC.** `_check_learned_policy` runs in Pass 3 before any program is accepted. It reads only declarations: the trained `command_ranges`, `terrain_classes`, and `payload_range` against the deployment's admissible ceilings (the strictest of `mobility.max_velocity`, the safety envelope's caps, and `validation.terrain_fidelity`). It catches a *deployment* that could ask the policy for more than it was trained for. It never sees a policy output.
2. **Check 2, runtime, RFC-0667.** The shield gates each action the policy proposes at dispatch and observes the telemetry stream; an out-of-envelope output is vetoed even when every declaration was coherent. It catches a *policy* that emits more than the deployment allows, which a static check cannot, because the output does not exist until the policy runs.

Neither subsumes the other. A coherent declaration does not make a network's outputs bounded, and a runtime veto does not make an over-scoped deployment honest. The worked example at `examples/executorch-policy/` runs both on one policy: the static check refuses an over-scoped envelope, and the shield vetoes a single out-of-range output under a coherent one.

### Reference runtime changes

No reference runtime must change to stay conformant. A learned-policy substrate adapter (a future Isaac Lab / rsl_rl runtime) reads `learned_policy` for documentation and may surface it. The static enforcement is the validator's, before any program is accepted; per-action enforcement at dispatch is the RFC-0667 shield's, optional and substrate-side (`ShieldedAdapter` wraps any adapter). The block is substrate-neutral: it describes the policy's competence boundary, not how any framework trained it.

### Conformance suite changes

`conformance/tests/test_manifest_learned_policy.py` adds:

1. A manifest declaring `learned_policy` with a `move_to` implying a velocity inside the range passes.
2. The same with a velocity beyond the trained `max` fails (`enforcement: reject`) with the RFC-0383 error naming quantity, requested, and bound.
3. The same with `enforcement: warn` validates with a warning, not an error.
4. A manifest whose `validation.terrain_fidelity` is outside `learned_policy.terrain_classes` is flagged.
5. A manifest omitting `learned_policy` validates unchanged.

A `learned_policy_biped` fixture manifest is added to exercise the block against a biped-walk intent.

## Backward compatibility

Pre-v1.0. Additive: the `learned_policy` block is optional, every existing manifest validates unchanged, no Layer-2 program changes. A manifest that adopts the block opts into a stricter check; that is the deployment's choice.

## Drawbacks

- **The declaration is trusted, not verified.** URML cannot confirm a policy was actually trained for the declared ranges; it checks intent against what the manifest claims. A wrong declaration produces false confidence. This is the same trust model as every manifest field, but the stakes are higher because a learned policy fails unpredictably outside its envelope. The honest framing is that URML makes the boundary explicit and checkable; getting the boundary right is the training side's job.
- **Mapping intent to an implied command is non-trivial.** A `move_to` does not literally carry a velocity; the validator must infer the implied command quantity from the primitive and the envelope. The inference is modest for navigation (speed) but gets harder for richer intents. This RFC scopes the check to quantities with a clear mapping and defers the rest.
- **Command-quantity vocabulary is a new closed set.** `linear_velocity_x`, `yaw_rate`, and friends are a small taxonomy URML now owns and must grow by RFC. The mitigation is to ship only the quantities a real fixture exercises.
- **Export is out of scope, so the field may sit empty.** URML defines the declaration, but a training framework has to emit it for the field to carry real data. Until rsl_rl / Isaac Lab export training limits, the block is authored by hand. That is acceptable (hand-authored is the status quo for every manifest field) but it means the value lands before the automated export does.

## Alternatives considered

1. **Reuse `mobility.max_velocity` and the safety envelope; add no new block.** Rejected. The mechanical maximum and the trained maximum are different numbers with different meanings, and a learned policy's terrain and command-distribution limits have no existing field at all. Overloading `max_velocity` to mean "trained max" would lose the distinction exactly where it matters.
2. **A free-text `training_notes` string.** Rejected for the static-gate reason: free text is not checkable. The whole point is that the validator refuses out-of-envelope intent, which requires structured ranges.
3. **Put the training envelope in the safety envelope, not the manifest.** Rejected as the primary home. The training envelope is a property of the policy artifact (the capability), not a deployment-time policy choice. It travels with the policy across deployments; the manifest is where capability lives. A deployment can still *tighten* it via the safety envelope's strictest-wins velocity cap.
4. **Wait for the training frameworks to define an export format, then mirror it.** Rejected as the lead. URML defining the declaration first is what gives the frameworks a target to export *to*; the rsl_rl maintainer's answer pointed at exactly this division of labor (limits exported from the task side, consumed somewhere). URML is the consumer that needs a schema.

## Prior art

- [RFC-0377 (rsl_rl)](0377-rsl-rl-outreach.md), the maintainer question that surfaced this; training-limits metadata exported alongside the policy.
- [RFC-0380 (rl_games)](0380-rl-games-outreach.md), [RFC-0376 (legged_gym)](0376-legged-gym-outreach.md), [RFC-0373 (Open Duck Mini)](0373-open-duck-mini-outreach.md), sibling learned-policy-as-substrate engagements.
- [RFC-0369 (OmniSafe)](0369-omnisafe-outreach.md), [RFC-0360 (robomimic)](0360-robomimic-outreach.md), safe-RL and imitation-learning peers at the same boundary.
- [RFC-0381 (simulation-fidelity manifest hints)](0381-simulation-fidelity-manifest-hints.md), the `terrain_fidelity` enum this block reuses for `terrain_classes`.
- [RFC-0009 (legged/humanoid mobility)](0009-legged-humanoid-mobility.md), the `biped`/`quadruped` drive types most learned-policy substrates use.
- Distributional-shift and operational-design-domain (ODD) literature; the training envelope is URML's manifest-level ODD for a learned controller.

## Unresolved questions

1. **Command-quantity taxonomy.** Which quantities ship in v1 (navigation velocities and yaw rate are clear; manipulation command quantities are murkier)? The lean is to ship only what a fixture exercises and grow by RFC.
2. **Intent-to-command inference.** How far should the validator go in inferring an implied command from a primitive? Navigation speed is tractable; richer intents may need the policy substrate to declare the mapping. Possibly a follow-on.
3. **`enforcement` default.** Should an undeclared `enforcement` default to `reject` (safe, strict) or `warn` (gentle adoption)? The lean is `warn` until export tooling exists, then `reject`.
4. **Coverage / confidence.** Should the block carry a coverage or confidence measure (how well-sampled the training distribution was), or is min/max enough? Deferred; min/max first.

## Implementation plan

1. Land the `learned_policy` block and the command-quantity enum in `reference/validator/src/urml_validator/schemas/manifest.py`.
2. Land the command-range check, terrain coherence, and strictest-wins conjunction in `reference/validator/` (Pass 2 + Pass 3).
3. Land the conformance tests and the `learned_policy_biped` fixture.
4. Update the Layer-1 spec doc to document the block.
5. Coordinate with the learned-policy engagements (rsl_rl, Isaac Lab) on an export shape in a separate, later effort; this RFC does not depend on it.

All validator and conformance work lands in a single PR. This RFC depends on RFC-0381 only for the shared `terrain_fidelity` enum; if 0381 is not yet landed, `terrain_classes` ships with its own copy of the enum and is reconciled when 0381 lands.

## How to respond

This is a Spec RFC. Comments belong in the RFC's PR thread on `URML-MARS/URML`.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed.
- [x] Motivation grounded in a concrete failure (a walk policy commanded past its trained speed) and a concrete maintainer ask (rsl_rl).
- [x] Detailed design names every affected component and the validator checks.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (trusted-not-verified, intent-to-command inference, new taxonomy, export lag).
- [x] Backward compatibility honest (additive, optional, opt-in stricter check).
- [x] No Layer-2 primitive added; the block is substrate-neutral (describes the policy's boundary, not any framework).
- [x] Implementation note explains how it lands and its only dependency (RFC-0381's enum).
- [x] Re-read CLAUDE.md §What Claude Should Never Do; closed enums preserve the gate, no framework is embedded, no cloud dependency, no telemetry.

## Implementation status

Implemented 2026-06-04. Landed: the `LearnedPolicy` / `CommandRange` / `PayloadRange` models + the optional `learned_policy` field on `CapabilityManifest`; the `_check_learned_policy` Pass-2/3 coherence check (terrain within the trained classes; the admissible velocity and payload ceiling, strictest of `mobility` and the safety envelope, against the trained maxima) with severity routed by `enforcement` (`reject` to errors, `warn` to warnings) and two error codes (`capability.learned_policy_terrain_mismatch`, `capability.learned_policy_exceeds_training`); integration tests; and Layer-1 spec §2.12.

The shipped check is the manifest/envelope ceiling form (it catches the case where admissible intent could exceed training regardless of any specific program). Per-primitive intent-to-command inference (reading an explicit `move_to` speed against a command range) and the manipulation command quantities are the documented follow-ons (Unresolved questions 1 and 2). `terrain_classes` reuses the RFC-0381 `terrain_fidelity` enum, now landed.

Amended 2026-08-20: the Detailed design now states explicitly that the static declaration check (this RFC) and the per-action runtime shield (RFC-0667) are two separate mechanisms; earlier wording read as one. Prompted by the ExecuTorch maintainers' review on pytorch/executorch#20268. `examples/executorch-policy/` is the worked example exercising both. The conformance fixture this RFC promised (`learned_policy_biped`) has still not landed and remains a follow-on.
