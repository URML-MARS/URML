---
rfc: 0617
title: Multiple named, per-domain learned policies
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0617: Multiple named, per-domain learned policies

## Summary

RFC-0383 added `learned_policy`: a single block declaring the training envelope of a learned controller, so the validator can refuse a deployment whose admissible intent exceeds what the policy was trained for. One block assumes one policy. A multi-skill robot does not work that way: a quadruped may run a trained locomotion policy and a separate trained manipulation policy; an RL deployment may carry several skills, each with its own training distribution.

This RFC adds an optional `learned_policies` list: named, per-domain policies, each validated independently by the RFC-0383 logic and scoped to the command quantities it declares. It is additive (the single `learned_policy` is unchanged), not a new primitive.

**State: Implemented** (2026-06-15). Ships the schema (`name` + `governs` on `LearnedPolicy`, `CapabilityManifest.learned_policies`, a uniqueness validator), the refactored Pass-2/3 check looping over the single block and each named policy, a new `governs`-coherence code, a runnable example, unit tests, and the spec text. `manifest_version` stays `"0.1"`.

## Motivation

Surfaced by the RL-framework engagements. The Move #29 humanoid/legged wave reached rsl_rl, rl_games, and legged_gym, where the recurring question was whether a trained policy could declare the envelope it is valid within. RFC-0383 answered that for one policy. But those frameworks train *many* policies, and a real deployment composes several, each governing a different skill. With a single block you can declare only one of them; the others are invisible to the validator. Treating "the strictest across all policies" as one envelope is wrong: a manipulation policy's payload limit has nothing to say about a locomotion command, and vice versa. Each policy governs its own domain and must be checked on its own terms.

## Proposal

### Schema (Layer 1)

`LearnedPolicy` gains two optional fields:

- `name`: optional for the single top-level `learned_policy`; required and unique for every entry of `learned_policies`.
- `governs`: the skill domain the policy controls, one of `locomotion | navigation | manipulation | whole_body | all`. Optional; documentation when omitted, and the basis of a coherence check when present.

`CapabilityManifest` gains `learned_policies: list[LearnedPolicy]` alongside the existing `learned_policy`. A model validator requires each list entry to carry a unique, non-null `name`.

```yaml
learned_policies:
  - name: locomotion
    governs: locomotion
    command_ranges: [ { quantity: linear_velocity_x, min: -1.5, max: 1.5, unit: m_per_s } ]
    enforcement: reject
  - name: grasping
    governs: manipulation
    payload_range: { min: 0.0, max: 4.0, unit: kg }
    enforcement: reject
```

### Validation (Pass 2/3)

The RFC-0383 check is refactored to run over the single `learned_policy` (if present) and every entry of `learned_policies`. For each policy:

- The admissible velocity / payload ceilings (strictest of the mechanical `mobility` limit and the safety-envelope cap) are checked against that policy's `command_ranges` / `payload_range`, and `validation.terrain_fidelity` against its `terrain_classes` (`capability.learned_policy_exceeds_training` / `_terrain_mismatch`). Severity follows the policy's own `enforcement`.
- **Scoping is by the quantities the policy declares.** A locomotion policy declaring only velocity ranges is checked only on velocity; a manipulation policy declaring only a payload range is checked only on payload. They do not interfere, which is exactly what "per-domain" means in practice. No new per-command linkage syntax is needed.
- A `governs` domain whose capability is absent from the manifest (`manipulation` with no `manipulation` block, a locomotion/navigation/whole_body policy with no `mobility`) is flagged with `capability.learned_policy_governs_unsupported`.

The validator still never loads or runs a policy; `policy_ref` is opaque.

## Alternatives considered

- **Explicit per-command linkage (a program names the policy that drives it).** Rejected for v0.1: scoping by declared command quantities already separates a velocity policy from a payload policy without new syntax. A program-to-policy reference is a clean future extension (and composes with RFC-0616 `declared_intent`), but it is not needed to make multi-policy validation correct.
- **"Strictest across all policies" as a single envelope.** Rejected: it is wrong. Unrelated policies bound unrelated quantities; intersecting them would reject admissible deployments.
- **A new top-level block instead of extending `LearnedPolicy`.** Rejected: a named policy *is* a `LearnedPolicy` with a name and a domain; reusing the model keeps one schema and one check.

## Prior art

This is the multi-instance generalization of RFC-0383, the way RFC-0286 generalized a single robot to a fleet roster. The `governs`-coherence check mirrors the capability-presence pattern used by RFC-0616 `declared_intent`. The `name` + uniqueness rule follows the `manipulation.arms` (RFC-0010) and roster-member (RFC-0286) precedents.

## Implementation plan

Shipped in one slice:

- Schema: `LearnedPolicy.name` / `.governs`; `CapabilityManifest.learned_policies` + the uniqueness model-validator (`manifest.py`).
- Validator: `_check_learned_policy` refactored to loop the single block + each named policy via `_check_one_learned_policy`; path labels carry the policy name; `_GOVERNS_REQUIRES` map; one new code (`capability.learned_policy_governs_unsupported`); `_learned_policy_exceeds` parametrized by path.
- Example: `examples/legged/multiskill-policies` (a quadruped with a locomotion and a grasping policy; validates under the default policy, executes hermetically).
- Spec: Layer-1 §2.12. Tests: `reference/validator/tests/test_learned_policies_rfc0617.py` (8 cases), and the RFC-0383 suite is unchanged (back-compat).

## Open questions (deferred, not blocking)

- **Program-to-policy reference.** Letting a `Program` / `declared_intent` (RFC-0616) name the learned policy that drives it, so an opaque policy-driven program is validated against that specific policy's envelope. The natural next composition.
- **Manipulation command quantities.** `CommandRange.quantity` is velocity/yaw only today; a manipulation policy currently leans on `payload_range` and `governs`. Adding force/torque quantities is an additive extension as a fixture exercises them.
