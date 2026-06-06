---
rfc: 0384
title: whole_body, declaring a legged robot's kinematic structure and stability limits
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-04
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

# RFC-0384: whole_body, declaring a legged robot's kinematic structure and stability limits

## Summary

A humanoid is a biped ([RFC-0009](0009-legged-humanoid-mobility.md): `drive_type: biped`) with two arms ([RFC-0010](0010-whole-body-bimanual-manipulation.md): `manipulation.arms`). URML can now say *that a robot is legged* and *that it has named arms*, but nothing in between: it cannot declare the robot's kinematic structure (which limbs it has) or its stability envelope (whether it can hold a pose, carry while walking, the ground it can handle, where its mass sits). This RFC adds an optional `whole_body` block to the Layer-1 manifest that declares both, and the validator checks it. The change is additive, backward compatible, and ships with its implementation (the RFC-0009 pattern: a manifest widening with no semantic fork).

## Motivation

This is the design question six maintainers asked, in their own words, during the Move #29 open-humanoid outreach. ToddlerBot, K-Scale, PAL (TALOS), Open Duck Mini, legged_gym, and legged_control each replied to "what should a bipedal-humanoid capability declaration contain?" with the same shortlist: a legged mobility class, whole-body kinematic structure, balance or stability constraints, and the split between locomotion and manipulation. RFC-0009 answered the first item and RFC-0010 the manipulation surface. The structural and stability items are this RFC.

Concretely, before this RFC a manifest for Agility Digit could declare `drive_type: biped` and two arms, but a reader (and the validator) could not tell that Digit is a two-leg, two-arm, one-torso machine, nor whether asking it to carry a tote while walking is even admissible. Those are exactly the questions a validated-intent layer should be able to answer before dispatch.

## Detailed design

A new optional `whole_body` block on the manifest, a sibling of `mobility` and `manipulation`:

```yaml
whole_body:
  chains:
    - { name: left_leg,  kind: leg,   dof: 6 }
    - { name: right_leg, kind: leg,   dof: 6 }
    - { name: left_arm,  kind: arm,   dof: 7, arm_ref: left }
    - { name: right_arm, kind: arm,   dof: 7, arm_ref: right }
    - { name: torso,     kind: torso, dof: 1 }
  static_stable: true
  can_carry_while_moving: true
  max_incline_deg: 15.0
  max_tilt_deg: 10.0
  center_of_mass: { x: 0.0, y: 0.0, z: 0.9 }
  support_polygon:
    - { x: -0.20, y: -0.15 }
    - { x:  0.20, y: -0.15 }
    - { x:  0.20, y:  0.15 }
    - { x: -0.20, y:  0.15 }
```

**Kinematic structure.** `chains` is a list of `KinematicChain` — `{name, kind ∈ leg|arm|torso|head|other, dof ≥ 1, arm_ref?}`. An `arm` chain may set `arm_ref` to the `manipulation.arms[].name` it realizes, tying the whole-body structure to the manipulation surface (RFC-0010) so the two cannot drift.

**Stability as declared limits.** `static_stable` (can it hold a pose without continuously stepping), `can_carry_while_moving`, `max_incline_deg`, and `max_tilt_deg` are limits a request is validated against. `center_of_mass` and `support_polygon` declare the nominal static-stability geometry.

**The altitude line.** RFC-0010 drew it: URML declares intent and the limits a request is checked against; realizing balance is the substrate's job. This RFC holds that line even for the richer geometric fields. `center_of_mass`, `support_polygon`, and `max_tilt_deg` are **static declarations the validator verifies**, not a runtime controller model. They earn their place through a real check (a declared CoM must lie within the declared support polygon); they are not a dynamics simulator and URML never integrates them over time.

### Validator changes

A whole-program Pass-2 check (`_check_whole_body_caps`) plus one gate on `move_to`:

- leg-chain count matches a legged `drive_type` (`biped` = 2, `quadruped` = 4) → `capability.whole_body_inconsistent`;
- each `arm` chain's `arm_ref` resolves to a declared `manipulation.arms[].name` → `capability.whole_body_inconsistent`;
- a declared `center_of_mass` (x, y) lies within the declared `support_polygon` (ray-casting point-in-polygon) → `capability.whole_body_unstable_com`;
- `move_to(carrying: …)` on a legged platform whose `whole_body.can_carry_while_moving` is false → `capability.cannot_carry_while_moving`.

Intra-block well-formedness (unique chain names, `arm_ref` only on `kind: arm`, a support polygon of at least three vertices) is enforced in the schema model. No existing pass changes for a manifest without a `whole_body` block.

### Spec / runtime changes

Layer-1 spec §2.13 documents the block. No Layer-2 primitive is added (this is a capability declaration, not a new verb), and no runtime change is needed: the reference adapters (Spot, ANYmal, Digit) consume the validated manifest through the validator, not through dispatch.

## Backward compatibility

Fully additive. `whole_body` is optional; absent, behavior is identical to before. `manifest_version` stays `"0.1"`. Every existing program, manifest, fixture, and runtime is unaffected. Pre-v1.0, so a break would be permitted; none is needed.

## Drawbacks

The richer stability fields (`center_of_mass`, `support_polygon`, `max_tilt_deg`) push closer to a control-theoretic model than URML usually goes, the same over-reach RFC-0010 warned against. The mitigation is strict: they are static declarations checked statically, never integrated or simulated, and the one cross-field check (CoM in support polygon) is what keeps them honest rather than decorative. If they ever start to pull URML toward owning balance dynamics, the retreat path is to keep `chains` + the boolean/scalar limits and drop the geometry; the structure half stands on its own.

## Alternatives considered

- **Structure-only** (chains + DoF, no stability fields): smaller and safely on-altitude, but it cannot answer "can this robot carry while walking?" or validate a stability declaration, which is half of what the maintainers asked for. Chosen against deliberately; the richer model was the maintainer-facing decision.
- **Fold the fields into `mobility`**: rejected. `mobility` is the drive/velocity surface shared by every robot; whole-body structure is specific to multi-limb platforms and deserves its own optional block, the way `manipulation` is separate.
- **A full kinematic tree (joints, link transforms, URDF-style)**: rejected as out of altitude. URML is not a robot description format; it declares capability, not a model a planner would consume. `dof` per chain is the honest granularity.

## Prior art

URDF / SRDF kinematic trees and planning groups; MoveIt 2 joint-model groups; the support-polygon / ZMP stability literature for legged robots; whole-body control stacks (TSID, OCS2, OpenSoT). URML-internal: RFC-0009 (the legged `drive_type`, whose additive discipline this follows) and RFC-0010 (the arms surface this composes with, and the intent-not-control line this holds).

## Unresolved questions

- Whether `max_incline_deg` / `max_tilt_deg` should be checked against a future terrain/slope declaration in the safety envelope. They are declared and range-checked now; a request-level gate waits for an envelope that carries terrain grade.
- Whether non-legged multi-limb platforms (e.g. a dual-arm torso on a wheeled base) should use `whole_body.chains` too. The block does not forbid it; only the leg-count check is drive-type-specific.

## Implementation note

Ships as one vertical slice (spec → schema → validator → conformance → runnable example), the RFC-0009 pattern: a manifest widening with no semantic fork, so RFC and implementation land together (contrast RFC-0010, whose genuine fork required an RFC-first Draft). Schema: `WholeBody`, `KinematicChain`, `Point2`, `Point3` in the manifest module. Validator: `_check_whole_body_caps` + the `move_to` carry gate + three error codes. Conformance: a `digit_wholebody` manifest and four fixtures (one positive carry, three rejections). Example: the `examples/humanoid/digit-tote-lift` manifest gains a `whole_body` block. Validator unit tests cover all three codes plus the no-block regression.

## Self-review (Phase 0)

- [x] The Summary alone says what is added and that it ships implemented.
- [x] The Motivation is grounded in concrete maintainer requests (Move #29), not a hypothetical.
- [x] More than one alternative is genuinely considered; the chosen scope (richer model) is marked and the retreat path named.
- [x] Backward compatibility is explicit (additive, optional, pre-v1.0).
- [x] Drawbacks are honest, including the altitude risk and how the design contains it.
- [x] Every normative addition has a check, a conformance fixture, and a runnable example (the URML bar for new surface).
