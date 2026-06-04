---
rfc: 0381
title: Simulation-fidelity manifest hints, terrain_fidelity and simulator_target_class
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
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

# RFC-0381: Simulation-fidelity manifest hints

## Summary

URML validates a program statically against a capability manifest and a safety envelope, then a simulator can exercise the same validated intent before real deployment. URML v0.1 has no way to record two facts that the simulation layer needs and that a reader of a fixture wants to know: what terrain class the deployment runs over, and what fidelity tier the intent was validated against. This RFC adds an optional Layer-1 manifest block, `validation`, with two closed-enum fields, `terrain_fidelity` and `simulator_target_class`. Both are advisory metadata. The validator checks enum membership and surfaces the values in its report; it does not simulate dynamics. No primitive changes. Backward compatible (additive optional block).

The surface that demanded this RFC is the Move #24 simulation wave, and [RFC-0328](0328-project-chrono-outreach.md) (Project Chrono) explicitly queued both fields as future Spec RFCs. The shipped `reference/chrono-runtime/` (RFC-0328 follow-up) records the same two gaps in its `SPEC-GAPS.md`.

## Motivation

URML's identity is "validate before you move." A high-fidelity simulator like Project Chrono, Isaac Sim, or Genesis is where a validated program gets stress-tested against dynamics before it touches hardware. Two facts that matter at that boundary have no home in URML today.

1. **Terrain class.** Chrono::Vehicle reasons about deformable-terrain terramechanics: slip, sinkage, tipping margins. A URML `move_to` validated against `max_velocity` and a payload bound is exactly the intent a roboticist wants to stress-test on rough terrain. URML deliberately does not model the terrain itself (that stays substrate configuration, the line Layer 1 draws against URDF/SDF structure). But a one-word hint, "this deployment runs over deformable terrain," lets a sim runtime select the right terrain model and lets the envelope reason about a margin the sim will exercise. Today that hint lives nowhere, so a Chrono adapter has to guess or be hand-configured out of band.

2. **Fidelity tier.** A fixture validated only against a rigid-body game-grade engine is a weaker claim than one validated against high-fidelity multibody, which is weaker than one validated on hardware. URML has no way for a fixture or manifest to state the fidelity it was validated against. A reader cannot tell, and a conformance run cannot assert, whether "validated" meant a kinematic check, a rigid-body sim, or a terramechanics sim. The claim is ambiguous exactly where URML's credibility depends on it being precise.

Both facts are declarative metadata, not new behavior. The cost of leaving them out is that the simulation layer URML is courting (Move #24) cannot bind cleanly, and "validated" stays an imprecise word.

## Detailed design

### Field shape

Add an optional top-level `validation` block to the Layer-1 capability-manifest YAML schema.

```yaml
validation:
  terrain_fidelity: deformable             # NEW, this RFC
  simulator_target_class: high_fidelity_multibody   # NEW, this RFC
```

Both fields are **optional**. A manifest that omits the `validation` block validates exactly as today. Neither field gates any primitive; they are read by the simulation runtimes and surfaced in the validation report.

### Allowed values

`terrain_fidelity` (the terrain the deployment runs over):

| Value | Meaning |
|---|---|
| `rigid` | Hard, non-deforming ground (indoor floor, paved surface) |
| `deformable` | Soft terrain that deforms under load (soil, sand, snow); terramechanics matters |
| `granular` | Loose granular media (gravel, regolith); discrete-element scale |
| `unmodeled` | Terrain is not characterized; no fidelity claim |

`simulator_target_class` (the fidelity tier the intent was validated against):

| Value | Meaning | Representative engines |
|---|---|---|
| `kinematic` | Geometric/reachability check only, no dynamics | IK solvers, the validator's own static pass |
| `rigid_body` | Rigid-body contact dynamics, game-grade | MuJoCo, Isaac Sim, Genesis (rigid mode) |
| `high_fidelity_multibody` | High-fidelity multibody, terramechanics, FEA | Project Chrono, Drake |
| `photoreal` | Photoreal sensor simulation emphasis | Isaac Sim sensor stack, CARLA |
| `hardware` | Validated on real hardware, not a sim | n/a |

Both enums are closed under URML's opinionated posture, the same discipline RFC-0250 applied to `substrate.autopilot_class`: adding a value requires a follow-up RFC. The enums are deliberately coarse. They are hints, not a taxonomy of every engine.

### Schema fragment (JSON Schema additions to Layer-1)

```jsonc
{
  "validation": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "terrain_fidelity": {
        "type": "string",
        "enum": ["rigid", "deformable", "granular", "unmodeled"]
      },
      "simulator_target_class": {
        "type": "string",
        "enum": ["kinematic", "rigid_body", "high_fidelity_multibody", "photoreal", "hardware"]
      }
    }
  }
}
```

### Validator behavior

`urml validate` adds two checks, both cheap:

1. **Enum membership.** A value outside either enum produces a clear validator error pointing to this RFC. Unknown values are not silently accepted; enum growth is RFC-gated.
2. **Report surfacing.** When present, both values are echoed into the structured validation report (the `--json` output) so a downstream consumer (a sim runner, a conformance harness, a human) can read the declared fidelity without parsing the manifest separately.

The validator does **not** simulate, does not check that the declared fidelity is "true," and does not gate any primitive on these fields. They are declarative. Enforcement of fidelity is the simulator's job, not the static gate's.

### Reference-runtime behavior

The simulation runtimes read `validation.terrain_fidelity` to select a terrain model where they support more than one. `reference/chrono-runtime/` is the motivating consumer: `terrain_fidelity: deformable` selects a Chrono::Vehicle terramechanics patch rather than a rigid plane. `reference/mujoco-runtime/`, `reference/isaac-runtime/`, and any future Genesis/Drake runtime may read the same field. A runtime that ignores the block stays conformant; the field is a hint, not a contract the runtime must honor.

`simulator_target_class` is read by the conformance harness and by sim runtimes that want to assert they are the declared tier (a Chrono runtime can refuse, or warn, when asked to certify a manifest that declares `hardware`).

### Conformance suite changes

`conformance/tests/test_manifest_validation_block.py` adds:

1. A manifest with a valid `validation` block passes and the values appear in the report.
2. A manifest with `terrain_fidelity: swamp` (not in the enum) fails with the RFC-0381 error.
3. A manifest omitting the block validates unchanged (backward-compat guard).

The shipped `chrono_vehicle_cell` manifest (`reference/validator/tests/fixtures/manifests/chrono_vehicle_cell.yaml`) gains `validation: { terrain_fidelity: deformable, simulator_target_class: high_fidelity_multibody }` so fixture `home/21_chrono_vehicle_terrain_positive` exercises the block end to end.

## Backward compatibility

Pre-v1.0. Purely additive: the `validation` block is optional, every existing manifest validates without change, and no Layer-2 program changes. No reference runtime is required to read the block to remain conformant.

## Drawbacks

- **Two hints, not enforcement.** These fields describe intent-validation context; they do not make the validator smarter about dynamics. A reader could over-read `simulator_target_class: high_fidelity_multibody` as a guarantee the sim ran, when it is a declaration. The mitigation is documentation and the conformance harness surfacing the value rather than asserting it.
- **Enum coarseness is opinionated.** A deployment whose terrain is "deformable but only mildly" has to round to `deformable`. That is intentional; a finer taxonomy is a manifest field that hides structure better left to substrate configuration.
- **Field placement.** `validation` is a new top-level block. An alternative is to fold both fields under an existing block; see Alternatives. The new block is the cleaner long-term home if more validation-context fields follow.

## Alternatives considered

1. **Put `terrain_fidelity` on the safety envelope instead of the manifest.** Rejected as the primary home. Terrain is a property of the deployment environment, and the envelope is the deployment-time artifact, so this is defensible. But `simulator_target_class` is about the manifest's validation provenance, not a safety limit, and splitting the two fields across manifest and envelope would fragment a single concept. Keeping both in one manifest `validation` block keeps the concept whole. A future RFC can add an envelope-level terrain constraint if a deployment needs to *tighten* terrain assumptions.
2. **One combined `fidelity` string instead of two fields.** Rejected. Terrain class and validation tier are orthogonal: a rigid-terrain deployment can be validated on high-fidelity multibody, and a deformable-terrain deployment can be validated only kinematically. Collapsing them loses that.
3. **Free-text strings, no enums.** Rejected for the RFC-0250 reason: free text defeats the static gate. Any string would validate and the field would carry no checkable meaning.
4. **Do nothing; leave fidelity to out-of-band sim config.** Rejected. That is the status quo, and it is exactly why the Move #24 simulators cannot bind cleanly and why "validated" stays ambiguous.

## Prior art

- [RFC-0328 (Project Chrono outreach)](0328-project-chrono-outreach.md), queued both fields explicitly; the shipped `reference/chrono-runtime/` is the motivating consumer.
- [RFC-0250 (substrate.autopilot_class)](0250-substrate-autopilot-class.md), the additive optional-manifest-field pattern and the closed-enum discipline this RFC mirrors.
- Sibling Move #24 simulation RFCs: [RFC-0322 (Genesis)](0322-genesis-outreach.md), [RFC-0323 (Isaac Sim)](0323-nvidia-isaac-sim-outreach.md), [RFC-0325 (CARLA)](0325-carla-outreach.md), [RFC-0059 (Drake)](0059-drake-model-based-robotics.md), [RFC-0060 (MuJoCo)](0060-mujoco-integration.md).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md), the conformance framework the new fixture-tier check extends.

## Unresolved questions

1. **Should `simulator_target_class` be a single value or a set?** A manifest might be validated against more than one tier over its life. The lean is a single value naming the strongest tier achieved; a list is a possible future iteration if maintainers want a validation history.
2. **Envelope-level terrain tightening.** Should a deployment be able to *tighten* `terrain_fidelity` in the envelope (manifest says `rigid`, a specific deployment runs over `deformable`)? Deferred; this RFC keeps both fields in the manifest. The strictest-wins envelope machinery could later host a terrain constraint.
3. **`granular` consumer.** No shipped runtime exercises `granular` (discrete-element terrain) yet. It is in the enum for completeness and for the Chrono DEM path; whether to ship it before a consumer exists, or add it later, is a maintainer call.

## Implementation plan

1. Land the `validation` block in the Layer-1 schema (`reference/validator/src/urml_validator/schemas/manifest.py`) and the JSON Schema export.
2. Land the two validator checks (enum membership, report surfacing) in `reference/validator/`.
3. Land the conformance tests in `conformance/tests/`.
4. Add the `validation` block to `chrono_vehicle_cell.yaml` and have `reference/chrono-runtime/` read `terrain_fidelity`.
5. Update the Layer-1 spec doc to document the block.

All land in a single PR to preserve atomicity.

## How to respond

This is a Spec RFC. Comments belong in the RFC's PR thread on `URML-MARS/URML`.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed.
- [x] Motivation grounded in a concrete use case (Chrono terramechanics, ambiguous "validated").
- [x] Detailed design names every affected component (schema, validator, runtimes, conformance).
- [x] At least one alternative considered (four).
- [x] Drawbacks real (hints-not-enforcement, enum coarseness, field placement).
- [x] Backward compatibility honest (additive, optional).
- [x] No Layer-2 primitive added; no substrate coupling (the block is read by any sim runtime, ignored safely by others).
- [x] Implementation note explains how it lands.
- [x] Re-read CLAUDE.md §What Claude Should Never Do; closed enums preserve the gate, no substrate lock-in, no cloud dependency.
