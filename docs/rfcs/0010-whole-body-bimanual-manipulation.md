---
rfc: 0010
title: Whole-body and bimanual manipulation
author: URML Maintainers (maintainers@urml.dev)
state: Draft
created: 2026-05-17
updated: 2026-05-17
supersedes: —
superseded-by: —
---

# RFC-0010: Whole-body and bimanual manipulation

## Summary

URML's manipulation vocabulary assumes one arm acting on one detected object: `grasp`/`release` take a single `target: VarRef` and the manifest declares an `arm_count` but no per-arm addressing. Humanoids (Agility Digit, and the manifest-only Optimus/Apollo/NEO) and dual-arm cobots cannot express two-arm-coordinated actions (lift a tote with both arms, hold-with-one/work-with-other, hand-off between arms). This RFC proposes the vocabulary for multi-arm manipulation. It is **Draft**: it fixes the problem statement and the design space, recommends a direction, and explicitly does **not** ship an implementation — new primitive semantics are a one-way door and must be agreed before code (RFC-0002 primitive-economy principle).

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

The design space, with a recommended direction. The fork is real and is the main unresolved question; this section is deliberately a menu, not a decree.

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

`ROSAdapter.send_manipulation_goal` gains an optional `arm` parameter (keyword, default preserves today's behavior). A new `send_bimanual_goal` Protocol method, or `bimanual` decomposed by the runtime into two coordinated `send_manipulation_goal` calls — itself an unresolved question (below). When implemented, `DigitAdapter` and a dual-arm UR/Franka cell move manipulation out of `not_supported`.

### Conformance suite changes

New fixtures: a humanoid two-arm tote lift (positive), a hold-and-work bimanual (positive), an `arm: left` on a single-arm manifest (rejected, new error code), `bimanual` with `arm_count: 1` (rejected). Added when this RFC reaches Accepted, not in this PR.

## Backward compatibility

Fully compatible if Option A is taken: `arm` defaults to `any` (today's behavior), `bimanual` is net-new, `Manipulation.arms` is an optional sibling of `arm_count`. Every existing program, manifest, fixture, and the four shipped industrial/legged/humanoid runtimes are unaffected. Pre-v1.0, so even were a break needed it would be permitted; none is.

## Drawbacks

`bimanual` is the first primitive whose semantics are about *intra-robot resource coordination* rather than a single intent. That is a genuine expansion of what a primitive is, and it risks being the thin end of a wedge (next: tri-manual? leg-assisted manipulation? whole-body loco-manipulation?). Mitigation: scope this RFC strictly to two-arm coordination of `grasp`/`release`; anything beyond is explicitly out and needs its own RFC. If even two-arm proves to need a control-theoretic model URML should not own, Option C (composition + `arm` selector only) is the honest smaller answer and this RFC should retreat to it rather than over-reach.

## Alternatives considered

Options B and C above (rejected / fallback, with reasons). Also considered and rejected: a free-form `manipulation_script` escape hatch (deletes the validator's ability to reason about manipulation — defeats the point of URML); pushing bimanual entirely into the adapter as a vendor concern (makes it unportable and unvalidatable, violating substrate-neutrality).

## Prior art

MoveIt 2 dual-arm planning groups and the `moveit_msgs` multi-group interface; ROS 2 `control_msgs` per-controller addressing; whole-body control / task-space inverse dynamics (TSID, OpenSoT) for humanoids; the Agility Digit manipulation API (per-arm addressing); behavior-tree dual-arm coordination nodes. URML-internal: RFC-0002 (primitive economy — adding is a one-way door, which is why this is RFC-first); RFC-0009 (the immediately prior Layer-1 widening, whose additive discipline this follows).

## Unresolved questions

- **The core fork**: Option A's `bimanual` primitive vs Option C's composition-plus-`arm`-selector. Needs one or two real dual-arm programs written both ways before Accepted.
- Protocol shape: a new `send_bimanual_goal` method vs runtime decomposition into coordinated `send_manipulation_goal(arm=...)` calls. Affects every adapter; decide before implementation.
- Arm naming: fixed `left`/`right` vs manifest-declared arm identifiers vs both. Humanoids vs N-arm industrial cells pull differently.
- Force/grasp coordination for a shared payload: does URML express joint force intent, or is that explicitly a substrate concern URML only declares the *intent* for?

## Implementation note

RFC-first by design. This PR adds **only this document in `state: Draft`** — no schema, Protocol, or runtime change, because the unresolved fork would otherwise bake an unreviewed one-way decision into the surface. Sequence once Accepted: (1) `arm` selector + Layer-1 `arms` + validator check (additive, low-risk, unblocks the common case); (2) `bimanual` primitive + Protocol + conformance fixtures; (3) flip `DigitAdapter` and a dual-arm cell out of `not_supported`. Each is its own PR. Contrast with RFC-0009, whose change was a single closed-enum widening with no semantic fork, so it shipped RFC + implementation together; this one must not.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed and that it is Draft, implementation-deferred.
- [x] The Motivation is grounded in a concrete, in-tree deferral (PR #65's `DigitAdapter`), not a hypothetical.
- [x] More than one alternative is genuinely considered; the recommended one is marked and the fallback named.
- [x] Backward compatibility is explicit (Option A is fully additive, pre-v1.0).
- [x] Drawbacks are honest, including the "what is a primitive" expansion and a named retreat path.
- [ ] The core fork (Option A vs C) is resolved — deliberately left open; that is what moving Draft → Open is for.
