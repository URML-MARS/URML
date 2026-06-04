---
rfc: 0010
title: Whole-body and bimanual manipulation
author: URML Maintainers (maintainers@urml.dev)
state: Implemented
created: 2026-05-17
updated: 2026-06-04
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

# RFC-0010: Whole-body and bimanual manipulation

## Summary

URML's manipulation vocabulary assumes one arm acting on one detected object: `grasp`/`release` take a single `target: VarRef` and the manifest declares an `arm_count` but no per-arm addressing. Humanoids (Agility Digit, and the manifest-only Optimus/Apollo/NEO) and dual-arm cobots cannot express two-arm-coordinated actions (lift a tote with both arms, hold-with-one/work-with-other, hand-off between arms). This RFC specifies the vocabulary for multi-arm manipulation.

**State: Implemented** (resolved 2026-06-04, the casting-to-building build). The core fork is resolved in favor of **Option A** — an `arm` selector on `grasp`/`release` plus a `bimanual` coordination primitive. The Draft deliberately deferred this one-way-door decision (RFC-0002 primitive-economy principle); it is now made and shipped as a single vertical slice (spec → schema → validator → runtime → conformance → runnable example). See the [Resolution](#resolution-2026-06-04) and [Implementation note](#implementation-note) below.

## Motivation

Concrete and already in-tree: the humanoid reference runtime (PR #65) scopes Digit to the locomotion subset and returns `not_supported_on_humanoid[digit]` for `grasp`/`release`, with a comment that whole-body/bimanual manipulation is a deferred RFC. That deferral is this RFC. Until it resolves, every two-armed robot on the multi-brand list is locomotion-only in URML, which is most of the humanoid value proposition unaddressed.

Single-arm `grasp` cannot express the load-bearing cases:

```text
# Lift a tote that needs two hands (neither arm can do it alone):
grasp(target=$tote)            # which arm? both? URML can't say.

# Hold a panel with the left arm while the right drives screws:
# two simultaneous, different manipulation intents on one robot —
# inexpressible: grasp has no arm selector and the sequence/parallel
# operators coordinate behaviors, not arms within one manipulation.
```

## Detailed design

The design space, with the recommended direction. The fork was the main open question in Draft; it is resolved to **Option A** (see [Resolution](#resolution-2026-06-04)). This section keeps the full menu for the decision record.

**Option A (recommended) — an `arm` selector plus a `bimanual` coordination block.** Extend `GraspArgs`/`ReleaseArgs` with an optional `arm: Literal["left","right","any"] | Identifier` (default `any`, fully backward compatible — every existing program keeps meaning). Add one new Layer-2 primitive `bimanual` that wraps two manipulation sub-intents with a coordination mode (`together` for a single shared payload, `independent` for hold-and-work). Layer 1 gains an optional `Manipulation.arms: list[{name, gripper_ref}]` so the validator can check an addressed arm exists; `arm_count` stays and `arms` is the richer optional form.

**Option B — generalize `grasp.target` to a list.** `target: VarRef | list[VarRef]`. Smallest schema delta, but it conflates "two arms, one object" with "one arm, two objects sequentially" and gives no place for coordination semantics. Rejected as the primary mechanism; the `arm` selector subsumes its useful part.

**Option C — composition only.** Say bimanual is `parallel { grasp(arm:left) ; grasp(arm:right) }` and add nothing but the `arm` selector. Attractive (no new primitive), but `parallel` coordinates *behaviors* with independent success/failure; a two-arm lift of one payload needs joint success and force coordination that behavior-level parallelism does not express. The `arm` selector from Option A is still needed here, so C is really "A without the `bimanual` primitive" and is the natural fallback if `bimanual` proves under-specified.

### Spec changes

- **Layer 2**: optional `arm` argument on `grasp`/`release`; new `bimanual` primitive (Option A). Documented in `spec/layer-2-primitives/` and RFC-0002's vocabulary list.
- **Layer 1**: optional `Manipulation.arms` (per-arm name + gripper reference); `arm_count` retained.
- **Profiles**: industrial (dual-arm cells) and a future humanoid profile reference it; home/drone unaffected.

### Validator changes

A new check: an addressed `arm` must exist in the manifest (`arms[].name`, or be `left`/`right`/`any` when `arm_count >= 2`). `bimanual` requires `arm_count >= 2`. Force-ceiling and envelope checks apply per-arm. No change to any existing pass for single-arm programs.

### Reference runtime changes

`ROSAdapter.send_manipulation_goal` gains an optional `arm` parameter (keyword, default preserves today's behavior). **Decided:** the runtime **decomposes** `bimanual` into two arm-addressed `send_manipulation_goal(arm=...)` calls (left then right) rather than adding a `send_bimanual_goal` Protocol method — so every existing adapter gains `bimanual` for free the moment it accepts the `arm` keyword, and the audit shows one goal per arm. A future optional `send_bimanual_goal` remains open for substrates that do genuine joint force control (see Resolution Q2). `DigitAdapter` is flipped out of `not_supported` for manipulation in this build; a dual-arm UR/Franka cell follows the same shape mechanically.

### Conformance suite changes

New fixtures (shipped in this build): a humanoid two-arm tote lift (`biped/06_digit_bimanual_lift_positive`), an `arm`-addressed single grasp (`biped/07_digit_arm_addressed_positive`), an `arm: left` on a single-arm manifest (`biped/08_arm_not_declared_rejected` → `capability.arm_not_declared`), and `bimanual` on `arm_count: 1` (`industrial/47_bimanual_one_arm_rejected` → `capability.bimanual_requires_two_arms`). Plus the runnable `examples/humanoid/digit-tote-lift` slice and validator unit tests for both error codes.

## Backward compatibility

Fully compatible if Option A is taken: `arm` defaults to `any` (today's behavior), `bimanual` is net-new, `Manipulation.arms` is an optional sibling of `arm_count`. Every existing program, manifest, fixture, and the four shipped industrial/legged/humanoid runtimes are unaffected. Pre-v1.0, so even were a break needed it would be permitted; none is.

## Drawbacks

`bimanual` is the first primitive whose semantics are about *intra-robot resource coordination* rather than a single intent. That is a genuine expansion of what a primitive is, and it risks being the thin end of a wedge (next: tri-manual? leg-assisted manipulation? whole-body loco-manipulation?). Mitigation: scope this RFC strictly to two-arm coordination of `grasp`/`release`; anything beyond is explicitly out and needs its own RFC. If even two-arm proves to need a control-theoretic model URML should not own, Option C (composition + `arm` selector only) is the honest smaller answer and this RFC should retreat to it rather than over-reach.

## Alternatives considered

Options B and C above (rejected / fallback, with reasons). Also considered and rejected: a free-form `manipulation_script` escape hatch (deletes the validator's ability to reason about manipulation — defeats the point of URML); pushing bimanual entirely into the adapter as a vendor concern (makes it unportable and unvalidatable, violating substrate-neutrality).

## Prior art

MoveIt 2 dual-arm planning groups and the `moveit_msgs` multi-group interface; ROS 2 `control_msgs` per-controller addressing; whole-body control / task-space inverse dynamics (TSID, OpenSoT) for humanoids; the Agility Digit manipulation API (per-arm addressing); behavior-tree dual-arm coordination nodes. URML-internal: RFC-0002 (primitive economy — adding is a one-way door, which is why this is RFC-first); RFC-0009 (the immediately prior Layer-1 widening, whose additive discipline this follows).

## Resolution (2026-06-04)

The four Draft questions, decided when this shipped:

- **The core fork (Option A vs C):** **Option A.** A two-arm lift of one shared payload needs joint success and a place to declare coordination *mode* that behavior-level `parallel` does not give (Option C's own text concedes this). The `arm` selector that Option C keeps is included regardless, so Option A is a strict superset that adds exactly one primitive for the case the others cannot express. The named retreat path to C stays valid if `bimanual` ever proves under-specified.
- **Protocol shape:** **runtime decomposition.** `bimanual` lowers to two arm-addressed `send_manipulation_goal(arm=...)` calls; no new Protocol method. This gives every adapter the primitive for free and keeps the result model substrate-agnostic. A future optional `send_bimanual_goal` is left open for substrates that do genuine joint force control — adding it is backward compatible.
- **Arm naming:** **both.** `left`/`right` resolve on any `arm_count >= 2` manifest (the humanoid common case); a manifest-declared `manipulation.arms[].name` is addressable by name (the N-arm industrial case). `any` (default) preserves all pre-RFC programs.
- **Force/grasp coordination:** **intent only.** URML declares the bimanual *intent and mode*; true joint force coordination for a shared payload is a substrate concern. The reference runtime issues the two goals and reports combined success. This is the honest scope line — URML should not own a control-theoretic whole-body model.

## Implementation note

The Draft shipped RFC-first (document only, `state: Draft`) so the one-way-door fork would not bake an unreviewed decision into the surface. This build resolves the fork to Option A and ships the whole slice in one PR, in the sequence the Draft set out: (1) `arm` selector + Layer-1 `Manipulation.arms` + the two new validator checks (`capability.arm_not_declared`, `capability.bimanual_requires_two_arms`); (2) the `bimanual` primitive + runtime decomposition + conformance fixtures + the `examples/humanoid` slice; (3) `DigitAdapter` flipped out of `not_supported` for manipulation. Fully additive: `arm` defaults to `any`, `arms` is optional, `bimanual` is net-new, `manifest_version` stays `"0.1"`, and every existing program/manifest/fixture/runtime is unchanged. (Contrast RFC-0009, a single closed-enum widening that shipped RFC + implementation together; this one had a real semantic fork, so the Draft correctly came first.)

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed and that it is Draft, implementation-deferred.
- [x] The Motivation is grounded in a concrete, in-tree deferral (PR #65's `DigitAdapter`), not a hypothetical.
- [x] More than one alternative is genuinely considered; the recommended one is marked and the fallback named.
- [x] Backward compatibility is explicit (Option A is fully additive, pre-v1.0).
- [x] Drawbacks are honest, including the "what is a primitive" expansion and a named retreat path.
- [x] The core fork (Option A vs C) is resolved — Option A, per the [Resolution](#resolution-2026-06-04); shipped as a full vertical slice.
