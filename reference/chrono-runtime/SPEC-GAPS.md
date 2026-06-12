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

# SPEC-GAPS — urml-chrono-runtime

Per the spec-gap protocol (RFC-0014): each runtime is built strictly
against the frozen substrate Protocol; anything a substrate needs that
URML cannot express is recorded here and, if genuinely inexpressible,
promoted to a numbered RFC Draft for maintainer decision, never a
silent primitive/schema change.

## Gaps

The substrate Protocol itself is **fully implemented with zero new
vocabulary**: `move_to`/`hover`/`wait`/`measure`/`wait_for`/`report`
map onto a `ChSystem` advanced by driver inputs, and `scan` is the
documented stub. Capabilities a *bare* vehicle / terramechanics model
lacks (`grasp`/`release`, `dock`, `detect`, `capture`, `speak`,
`listen`) are returned as honest unsuccessful `SubstrateResult`s, not
gaps in URML; a Chrono::Sensor or articulated-model companion supplies
them under the unchanged program, manifest, and validator.

The Chrono **mapping** surfaced two *manifest* gaps. Neither is bolted
on here; both are queued as Spec RFCs for maintainer decision, exactly
as flagged in [RFC-0328](../../docs/rfcs/0328-project-chrono-outreach.md):

1. **Terrain / terramechanics fidelity hint.** URML's manifest declares
   capability, not the terrain a deployment runs over. An optional
   terrain-fidelity hint (rigid / deformable / granular) would let the
   envelope reason about a margin Chrono will exercise, without
   modelling the terrain itself (that stays substrate configuration in
   `chrono_adapter.yaml`).

2. **Simulator-target class hint.** URML does not declare whether a
   deployment targets a high-fidelity multibody simulator, a game-grade
   engine, or real hardware. An optional simulator-target-class hint
   would let a fixture state the fidelity it was validated against.
   Shared with the sibling Move #24 simulation RFCs.

Both hints shipped as [RFC-0381](../../docs/rfcs/0381-simulation-fidelity-manifest-hints.md)
(the optional `validation` block: `terrain_fidelity` +
`simulator_target_class`). The terramechanics scene
(`scene: terramechanics`) now reads the `terrain_fidelity: deformable`
hint and returns richer evidence (sinkage, peak contact force,
tip-stability margin) over a Chrono SCM deformable-terrain model; the
bare `ChSystem` evidence (system time, contact count, commanded driver
inputs) remains the default. The live SCM construction is the documented
calibration step in `chrono-integration.yml`: its physics getter surface
is version-sensitive, so each read degrades to an honest `unavailable`
note rather than crashing, and the pinned version is verified there.

No primitive, manifest field, or behavior-semantic change is made by
this runtime.
