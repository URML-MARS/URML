---
rfc: 0671
title: Dynamic-target grasping, target_motion on grasp and an interception declaration
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-10
updated: 2026-08-10
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

# RFC-0671: Dynamic-target grasping

## Summary

`grasp` gains an optional `target_motion` argument (`static | tracked | ballistic`, default `static`), and the `Gripper` model gains an optional `interception` block declaring which motion classes the hand can intercept and the numbers that make the claim honest: closing time and the perception-to-actuation latency budget. "Catch the ball" stays one sentence of intent; the catching itself stays a runtime skill. What changes is that the validator can now answer, on paper and before anything moves, whether this hand on this robot is allowed to attempt an interception at all. No new primitive: a catch is a grasp whose target refuses to sit still.

## Motivation

Foundation Robotics' tendon-driven hand catching a baseball in mid-flight ([video](https://x.com/i/status/2086497997974606087)) is the concrete instance of a class URML cannot currently express. The current `grasp` model, including the RFC-0586 dexterous extension, silently assumes a quasi-static target: nothing in the manifest states whether a hand that grasps can also intercept, and nothing in a program states that the target is moving. So today "catch the ball" either validates on a parallel-jaw gripper that has no hope of executing it, or is refused everywhere, depending on how a bridge happens to phrase it. Both outcomes are wrong in the way URML most cares about: the language cannot distinguish hardware that declares a capability from hardware that does not.

The intent layer is the right place for exactly one piece of this. The millisecond perception-prediction-closure loop is a trained reactive skill and belongs to the runtime (RFC-0383 already models it: an opaque policy behind a declared envelope). The admission decision belongs to URML: does the addressed hand declare interception for this motion class, and does the safety envelope tolerate a ballistic object in this workspace? That is the same shape as refusing a 250 N grasp on a 100 N gripper, applied to time instead of force.

Adding a `catch` primitive was considered and rejected up front. Primitives are one-way doors, and every fact a `catch` verb would carry is expressible as one argument on `grasp` plus one declaration block; sugar can be revisited later if usage demands it.

## Proposal

### Layer 2: the `target_motion` argument

`grasp` gains an optional `target_motion` from a closed set:

```yaml
- grasp:
    target: $incoming_ball
    force: firm
    grasp_type: spherical      # RFC-0586, unchanged
    target_motion: ballistic   # optional; default static
```

- `static` (default): the target is at rest or quasi-static. Identical to today's behavior; every existing program validates unchanged.
- `tracked`: the target moves on a continuous, observable path the robot can follow (a conveyor part, a handed-over object).
- `ballistic`: the target is in free flight; interception is predictive, not tracking.

Because `bimanual` (RFC-0010) decomposes into `grasp` sub-intents that flow through the same checks, a two-handed catch validates per hand with no extra machinery.

### Layer 1: the `interception` block

Any `Gripper` may declare an `interception` block. It is not restricted to `kind: dexterous`: a fast parallel-jaw gripper picking from a moving conveyor is a legitimate `tracked` interceptor, while a baseball catch will in practice require a dexterous hand, and the numbers say so.

```yaml
manipulation:
  arm_count: 1
  grippers:
    - name: phantom_hand
      kind: dexterous
      force_min_n: 0.5
      force_max_n: 30.0
      accepted_classes: [small_part, ball]
      dexterity:
        dof: 21
        finger_count: 5
        grasp_types: [power, precision, spherical]
        supports_in_hand_manipulation: true
      interception:
        modes: [tracked, ballistic]     # non-empty, from {tracked, ballistic}
        closing_time_ms: 80             # commanded-open to commanded-closed, > 0
        reaction_latency_ms: 40         # perception-to-actuation budget, > 0
        max_target_speed_m_s: 12.0      # optional; omit if uncharacterized
```

The declaration is trusted, not verified, like every manifest field (RFC-0383 states the same trust model for policy envelopes). What the block buys is that the claim exists, is machine-checkable, and is refusable: a hand that never declared `interception` cannot be asked to catch.

### Validation (Pass 2, capability)

Two new capability codes, mirroring the RFC-0586 pair:

- `capability.target_motion_not_supported`: a non-`static` `target_motion` was requested and no addressed gripper declares an `interception` block.
- `capability.target_motion_mode_not_declared`: the addressed gripper declares `interception` but not the requested mode (e.g. `tracked` declared, `ballistic` requested).

Gripper addressing resolves exactly as the force and `grasp_type` checks do (named arm, else `any` falls back to all declared grippers). Schema-level coherence: `interception.modes` is non-empty and drawn from the closed set; `closing_time_ms` and `reaction_latency_ms` are required positive numbers; `max_target_speed_m_s` is optional and positive.

### Runtime

The Protocol method gains an optional `target_motion` parameter, threaded from `GraspArgs` into `send_manipulation_goal` and recorded in the audit trail, the same shape as RFC-0010's `arm` and RFC-0586's `grasp_type`. A substrate that runs interception as a learned policy dispatches on it; a substrate that cannot ignores it, safe because the parameter is only ever set after validation confirmed the declaration. `MockROSAdapter` accepts and records it, which keeps every hermetic suite and conformance fixture runnable.

### What this deliberately does not do

- No new primitive, no `catch` verb.
- No trajectory or timing validation. The validator never answers "will the catch succeed", only "is the attempt admissible on declared hardware".
- No envelope schema change in this RFC. A ballistic object near people is a real safety question; v1 leans on the existing people-occupancy and workspace rules, and a dedicated envelope treatment (e.g. a projectile clause) is left as an open question rather than smuggled in here.

## Alternatives considered

- **A `catch` primitive.** Rejected: one-way door, zero information beyond `grasp + target_motion`, and it would fork the force/`grasp_type`/arm machinery that `grasp` already carries.
- **Interception inside the `dexterity` block.** Rejected: conveyor-tracking parallel grippers are real, and gating `tracked` on `kind: dexterous` would misclassify them. The block sits on `Gripper`, beside `dexterity`.
- **A boolean `dynamic_interception: true`.** Rejected: a bare boolean invites overclaiming. Requiring `closing_time_ms` and `reaction_latency_ms` makes the declaration falsifiable by inspection, and gives future envelope rules numbers to bind against.
- **Deferring entirely to RFC-0383 learned-policy envelopes.** Rejected as the whole answer: the policy envelope says what the skill was trained for; it says nothing about the hand. Both declarations are needed, and they compose (a deployment can pair a `ballistic`-declaring hand with a policy whose envelope covers the throw speeds it trained on).

## Prior art

- RFC-0586 established the exact extension shape reused here: a Layer-1 declaration block, a Layer-2 optional closed-set argument, two Pass-2 capability codes, runtime threading with audit-trail visibility.
- RFC-0010 (bimanual) supplies the per-hand decomposition this rides.
- RFC-0383 (learned-policy training envelope) models the skill side; this RFC models the hardware side of the same attempt.
- Foundation Robotics' tendon-driven hand demo is the motivating hardware; the urml.dev post [A robot hand that catches a baseball](https://urml.dev/blog/a-robot-hand-that-catches-a-baseball/) is the public statement of the gap this closes.
- The Move #27 manipulation outreach wave (dexterous-hand RFCs) surfaced multi-DoF declaration as the recurring manifest gap; this continues that thread into dynamics.

## Implementation plan

On acceptance, one PR meeting the Layer-2 bar:

1. Schema: `TargetMotion` closed set on `GraspArgs`; `Interception` model on `Gripper`; coherence rules.
2. Validator: the two Pass-2 codes plus schema tests.
3. Runtime: `target_motion` through the Protocol and `MockROSAdapter`, audit-trail record.
4. Conformance: `manipulation/` fixtures, positive (declared hand accepts `ballistic`) and negative (undeclared hand refused with `capability.target_motion_not_supported`).
5. A runnable example and a spec section in Layer-2 with the updated JSON Schema.

## Open questions

- **Envelope treatment of ballistic objects.** Should an envelope be able to forbid `target_motion: ballistic` outright in occupied workspaces, or bind `max_target_speed_m_s` against a workspace rule? Deferred to its own RFC once there is a deployment to calibrate against.
- **`thrown` as a distinct outbound class.** Throwing is the dual of catching and is not `grasp` at all; out of scope here, noted so the closed set's future growth is on record.
- **Policy-envelope cross-check.** When a deployment declares both an `interception` block and an RFC-0383 policy envelope, should the validator warn if the policy's declared speed range exceeds the hand's `max_target_speed_m_s`? Cheap to add, deferred until both fields appear together in a real manifest.
