---
rfc: 0586
title: Dexterous (multi-fingered) hand declaration and grasp-type selection
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0586: Dexterous (multi-fingered) hand declaration and grasp-type selection

## Summary

URML's `Gripper` model describes a single-DoF end effector: a `kind`
(pneumatic, servo_electric, vacuum, magnetic, compliant), a force range, and a
set of accepted object classes. That is the right model for a parallel-jaw or
suction gripper, and it is all most manifests need. It cannot describe a
**dexterous, multi-fingered hand** (a LEAP Hand at ~16 DoF, a Shadow Hand at
~24 DoF): there is no place to state the degrees of freedom, the finger count,
or which grasp strategies the hand can perform, and `grasp` has no way to ask
for a precision pinch rather than a power grasp.

This RFC adds an optional `dexterous` gripper kind carrying a `dexterity`
block, and an optional `grasp_type` on the `grasp` primitive that is validated
against the addressed hand's declared strategies. It does **not** add a new
primitive: a dexterous grasp is still a grasp, so per URML's fewer-primitives
doctrine the capability rides an optional argument on `grasp`.

**State: Implemented** (2026-06-14). Ships the schema (`Dexterity` + the
`dexterous` kind + the `grasp_type` argument), two Pass-2 capability checks, a
manifest fixture, four conformance fixtures, a runnable example, the runtime
threading of `grasp_type` into the manipulation goal and audit, and unit tests.
Additive end to end: `grasp_type` defaults to none and `dexterity` is optional,
so every existing manifest, program, fixture, and runtime is unaffected.

## Motivation

The gap was surfaced by real engagement. The Move #27 manipulation wave reached
the LEAP Hand ([RFC-0357](0357-leap-hand-outreach.md)) and Shadow Robot
maintainers, and the honest question that came back was: what would a multi-DoF
hand declaration need? A dexterous hand differs from a parallel-jaw gripper in
two ways a manifest should capture: it has many articulated degrees of freedom
across several fingers, and it can perform qualitatively different grasps (a
power wrap, a precision pinch, a tripod). A program that wants "pick up the
connector with a precision grip" has no way to say so today, and a validator
has no way to reject that request on a two-finger gripper that cannot honor it.

## Proposal

### Layer 1: the `dexterous` kind and the `dexterity` block

`Gripper.kind` gains `dexterous`. A `dexterous` gripper carries a `dexterity`
block; a non-dexterous gripper must not (a schema-level coherence rule).

```yaml
manipulation:
  arm_count: 1
  grippers:
    - name: leap_hand
      kind: dexterous
      force_min_n: 0.5
      force_max_n: 20.0
      accepted_classes: [small_part, peg, connector]
      dexterity:
        dof: 16                 # total actuated DoF across the hand (>= 2)
        finger_count: 4         # independently actuated fingers (>= 2)
        grasp_types: [power, precision, pinch, tripod]   # non-empty
        supports_in_hand_manipulation: true              # declarative in v0.1
```

`grasp_types` is drawn from a closed set:
`power | precision | lateral | tripod | pinch | spherical | hook | custom`,
the common grasp taxonomy with `custom` as an escape hatch.

### Layer 2: the `grasp_type` argument

`grasp` gains an optional `grasp_type` from the same closed set:

```yaml
- grasp:
    target: $the_connector
    force: gentle
    grasp_type: precision     # optional; default none
```

`grasp_type` defaults to none, which works on any gripper. When set, the
addressing gripper must be dexterous and must declare the strategy.

### Validation (Pass 2, capability)

Two new capability codes:

- `capability.grasp_type_requires_dexterous`: a `grasp_type` was requested but
  no addressed gripper is dexterous.
- `capability.grasp_type_not_declared`: the addressed dexterous hand does not
  declare the requested strategy in `dexterity.grasp_types`.

The addressing gripper is resolved the same way the force check is: a named arm
(including `left`/`right` when declared in `manipulation.arms`) resolves to that
arm's bound gripper; `any` falls back to all declared grippers. Because the
`bimanual` primitive (RFC-0010) decomposes into `grasp` sub-intents that flow
through the same check, a per-hand `grasp_type` is validated there too.

### Runtime

The reference ROS 2 runtime threads `grasp_type` from `GraspArgs` into
`send_manipulation_goal` and records it in the audit trail (alongside `arm`),
so the validated intent is visible in the execution record. The Protocol method
gains an optional `grasp_type` parameter; a dexterous substrate may map the
strategy to a hand preset, and a non-dexterous substrate ignores it (it is only
ever set when validation has confirmed a dexterous hand). This mirrors how
RFC-0010 threaded `arm`.

## Alternatives considered

- **A separate `DexterousHand` model in `manipulation.hands[]`.** Rejected: a
  dexterous hand *is* a gripper (it grasps, has a force range, accepts object
  classes); splitting it into a parallel structure would duplicate those fields
  and force `grasp` to target two different things. Extending `Gripper` keeps
  one grasp surface.
- **A new `dexterous_grasp` (or `reorient`) primitive.** Rejected for the grasp
  case per the fewer-primitives doctrine: selecting a strategy is a parameter of
  grasping, not a new behavior. In-hand reorientation *is* genuinely new
  behavior, but it is deferred (see open questions) rather than shipped as a
  one-way-door primitive here.
- **A free-form string for `grasp_type`.** Rejected: a closed enum lets the
  validator check the request against the hand's declared set; `custom` covers
  the long tail without losing that check for the standard strategies.

## Prior art

The grasp taxonomy (power/precision/etc.) is standard in the manipulation
literature (Cutkosky and successors). Within URML this follows the RFC-0010
pattern exactly: an optional argument on `grasp` (`arm` there, `grasp_type`
here), validated against an optional manifest extension, threaded through the
runtime into the audit, with `bimanual` getting it for free via decomposition.

## Implementation plan

Shipped in one slice:

- Schema: `GraspType` shared enum (`common.py`); `Dexterity` model + `dexterous`
  kind + `dexterity` field + coherence validator (`manifest.py`); `grasp_type`
  on `GraspArgs` (`primitives.py`).
- Validator: `_grippers_for_arm` resolver + the `grasp_type` block in
  `_check_grasp_caps`; two `ErrorCode`s.
- Runtime: optional `grasp_type` on the manipulation Protocol, the mock
  (recorded in the call log), and the rclpy adapter; threaded from `exec_grasp`
  and the `bimanual` grasp sub-intents.
- Conformance: `leap_hand_cell` manifest fixture; four `manipulation/` fixtures
  (precision positive, requires-dexterous negative, not-declared negative,
  no-type backward-compat positive).
- Example: `examples/manipulation/dexterous-precision-grasp` (validate under the
  default policy, execute hermetically; the audit shows `grasp_type=precision`).
- Spec: Layer-1 manipulation (dexterous kind + dexterity), Layer-2 §2.6 grasp
  (grasp_type), `docs/spec-coverage.md`.
- Tests: `reference/validator/tests/test_dexterous.py`.

## Open questions (deferred, not blocking)

- **In-hand manipulation.** `supports_in_hand_manipulation` is declarative in
  v0.1. Whether in-hand reorientation deserves its own primitive (a genuine new
  behavior, hence a one-way door) is left to a future RFC informed by demand.
- **Per-finger / kinematic detail.** `dexterity` declares aggregate dof and
  finger count, not per-finger joint limits. If a use case needs finger-level
  bounds, that is an additive extension to `Dexterity`, not a change here.
- **Force per strategy.** A precision pinch and a power grasp have different
  force regimes; v0.1 keeps the gripper's single force range. Per-strategy force
  envelopes are a possible future refinement.
