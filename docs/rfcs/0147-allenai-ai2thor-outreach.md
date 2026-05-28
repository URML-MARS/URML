---
rfc: 0147
title: Allen AI AI2-THOR (visual interactive simulation) integration, request for comment from allenai maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0147: Allen AI AI2-THOR (visual interactive simulation) integration, request for comment from allenai maintainers

## Summary

URML does not yet ship an AI2-THOR manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest cross-citation for AI2-THOR — Allen AI's visual interactive simulation platform — over [`allenai/ai2thor`](https://github.com/allenai/ai2thor) (Apache-2.0), and **requests review and feedback from the allenai maintainers**. No spec change.

This RFC is **distinct from Move-2 RFC-0047 (allenai/molmoact)**. MolmoAct is the VLA model; AI2-THOR is the household-task simulation platform. URML adapters can target AI2-THOR as a conformance lane for household-manipulation primitives.

## Motivation

`allenai/ai2thor` is Allen AI's interactive 3D environment for embodied AI research. Apache-2.0, 1.7k stars, Issues + Discussions both enabled, last commit `2025-11-04` (~7mo from 2026-05-28 cutoff; borderline-recent but on a slower research cadence), **not archived**.

URML's home-runtime profile (RFC-0072 / `examples/home/` manifests) targets household-manipulation tasks. AI2-THOR is structurally the simulation harness those primitives can exercise in sim before reaching real-robot deployments. Cross-citation framing is appropriate because:

- AI2-THOR is research-platform, not vendor-OEM.
- URML's adapter at the sim-substrate layer is one of many sim-env candidates (Move-2 RFC-0050 Isaac, RFC-0051 CARLA, RFC-0144 mujoco_playground); AI2-THOR is the household-specific env.
- Cross-citation lets the conversation thread per env without claiming bundled-adapter commitment.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ai2thor_household_cell.yaml` fixture, cross-citation framing)

| URML field | Maps to AI2-THOR attribute |
|---|---|
| `name` | Deployment handle (`ai2thor_household_default`) |
| `simulation.env: custom` (`ai2thor_scene_<scene_id>`) | Declares which AI2-THOR scene the manifest exercises (FloorPlan1 etc.) |
| `simulation.task_class: custom` (`ai2thor_object_navigation` / `ai2thor_object_manipulation`) | Maps to AI2-THOR task class |
| `cameras` block | AI2-THOR rendered RGB / depth from agent perspective |
| `mobility.drive_type: custom` (`ai2thor_discrete_actions`) | AI2-THOR's discrete action space (URML's continuous mobility model doesn't fit directly) |

### What URML v0.1 does not yet express for AI2-THOR

1. **Simulation-env declaration.** Same gap as RFC-0144 mujoco_playground; sim-substrate Spec RFC queued.
2. **Discrete-action mobility class.** URML's `mobility.drive_type` enum is continuous (differential / omnidirectional / etc.); AI2-THOR's discrete-action API does not map cleanly. Spec RFC for discrete-action mobility class queued.
3. **Household-task vocabulary.** URML's primitive vocabulary maps to physical robot actions; AI2-THOR has higher-level task-class semantics (`PickupObject`, `OpenObject`). The mapping is one-way (URML primitives → AI2-THOR action) and is the cross-citation interest.

### Compatibility notes

- **Vendor / org.** [`allenai`](https://github.com/allenai) — research-org-direct.
- **Flagship repo.** [`allenai/ai2thor`](https://github.com/allenai/ai2thor) — Apache-2.0, 1.7k stars, Issues + Discussions both enabled, last commit 2025-11-04 (~7mo), **not archived**.
- **Origin.** Allen Institute for AI (Seattle, WA, US). Passes US-federal default policy.
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active research surface; slower cadence than vendor-OEM repos but durable.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; sim-substrate + discrete-action-mobility Spec RFCs queued.
- Reference runtime: cross-citation framing recommended; future `reference/sim-runtime/AI2THORAdapter` is a candidate **only if** engagement settles on the adapter shape and if URML's home-runtime profile expansion warrants it.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Cross-citation framing.** AI2-THOR is research-platform, not vendor-OEM; the engagement is appropriate at cross-citation depth rather than bundled-adapter commitment.
- **Two Spec-RFC prerequisites** (sim-substrate + discrete-action-mobility class).
- **Slower research cadence.** Engagement may be light-touch.

## Alternatives considered

1. **Skip AI2-THOR as duplicate with Move-2 RFC-0047 (MolmoAct).** Rejected. MolmoAct is the VLA; AI2-THOR is the sim env. Different layers of Allen AI's stack.
2. **Bundle AI2-THOR + ProcThor + Holodeck (Allen AI's sim ecosystem) into one Allen-AI-broader RFC.** Considered. Per-flagship RFC is the cleaner shape; broader-org engagement can be future work if AI2-THOR engagement opens that door.
3. **Defer AI2-THOR until home-runtime profile is RFC-formalized.** Rejected. The cross-citation engagement informs the home-runtime profile design.

## Prior art

- [`allenai/ai2thor`](https://github.com/allenai/ai2thor) — the upstream repo.
- [RFC-0047 (Allen AI MolmoAct)](0047-allen-institute-molmoact-outreach.md) — Move-2 engaged Allen AI's VLA; this RFC is the sim-env layer.
- [RFC-0050 (NVIDIA Isaac)](0050-nvidia-isaac-outreach.md), [RFC-0051 (CARLA)](0051-carla-outreach.md), [RFC-0144 (DeepMind MuJoCo Playground)](0144-deepmind-mujoco-playground-outreach.md) — sibling sim-env RFCs.
- URML's home-runtime profile (existing `examples/home/` manifest set).

## Unresolved questions

For the allenai ai2thor maintainers:

1. **Repository status.** Is `allenai/ai2thor` actively maintained, dormant-but-supported, or has the active development moved to a successor (ProcTHOR, Holodeck, etc.)?
2. **Sim-substrate manifest fields.** URML's v0.1 has no `simulation.env` field. A Spec RFC adding it (shared with sibling sim-env RFCs) is queued. Manifest field expectations from the AI2-THOR perspective?
3. **Discrete-action mobility class.** URML's mobility schema is continuous; AI2-THOR's API is discrete. Spec RFC adding `discrete_action` class queued. Manifest field expectations?
4. **Bridge home.** Cross-citation only (recommended), URML repo (`reference/sim-runtime/`), or AllenAI-maintained?
5. **Conformance listing.** Would AllenAI consider a README link to URML's compatible-runtimes registry once a working cross-citation ships?
6. **Anything else.**

## Implementation note

RFC-0147 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml). Cross-citation framing recommended.

## How to respond

`allenai/ai2thor` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion in Ideas category, pointing to this RFC, with cross-citation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 1.7k stars, Issues + Discussions enabled, last commit 2025-11-04, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (cross-citation appropriate, two Spec-RFC prerequisites, slower research cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Allen Institute for AI (Seattle US); default policy passes.
- [x] CLAUDE.md compliance check passed.
