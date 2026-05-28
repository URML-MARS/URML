---
rfc: 0144
title: DeepMind MuJoCo Playground (GPU robot-learning env) integration, request for comment from google-deepmind maintainers
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

# RFC-0144: DeepMind MuJoCo Playground (GPU robot-learning env) integration, request for comment from google-deepmind maintainers

## Summary

URML does not yet ship a MuJoCo Playground manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for `google-deepmind/mujoco_playground` — the GPU-accelerated MuJoCo robot-learning environment — over [`google-deepmind/mujoco_playground`](https://github.com/google-deepmind/mujoco_playground) (Apache-2.0), and **requests review and feedback from the google-deepmind maintainers**. No spec change.

This RFC is **distinct from Move-2 RFC-0060 (`google-deepmind/mujoco`)** which engaged the MuJoCo simulator core. `mujoco_playground` is the env+policy harness above the simulator core; the two layers benefit from separate engagement threads.

## Motivation

`mujoco_playground` provides JAX/MJX-accelerated robot environments and reference policy implementations for the MuJoCo physics engine. Repo at [`google-deepmind/mujoco_playground`](https://github.com/google-deepmind/mujoco_playground) (Apache-2.0, 2k stars, Issues + Discussions both enabled, last commit `2026-05-27` daily activity, **not archived**).

URML's perception manifests can target MuJoCo Playground as the **simulation conformance lane**: a manifest declares its expected sim env, URML's adapter dispatches the same primitives onto both the sim and real-robot substrate, and conformance tests run in MuJoCo Playground without GPU-cluster hardware via JAX's CPU fallback.

The distinction from Move-2 RFC-0060 matters: the simulator core (`google-deepmind/mujoco`) is the physics engine; `mujoco_playground` is the curated set of robot-learning envs + reference policies built on that engine. URML adapters compose at the env layer, not the physics layer.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mujoco_playground_cell.yaml` fixture)

| URML field | Maps to MuJoCo Playground attribute |
|---|---|
| `name` | Deployment handle (`mujoco_playground_default`) |
| `simulation.env: custom` (`mujoco_playground_<env_name>`) | Declares which env (`G1JoystickFlatTerrain`, `Go1JoystickFlat`, etc.) |
| `simulation.acceleration: gpu_jax` | Declares the JAX/MJX execution backend |
| `simulation.observation_space` | Maps to the env's observation-space spec |
| `simulation.action_space` | Maps to the env's action-space spec |

### What URML v0.1 does not yet express for MuJoCo Playground

1. **Simulation-env declaration.** URML's manifest does not today have a `simulation.env` field. Spec RFC for simulation-substrate declaration is queued; this is the natural place MuJoCo Playground's envs would slot in.
2. **JAX-acceleration declaration.** GPU-acceleration is a deployment property URML's manifest does not today declare.
3. **Observation / action space alignment with manifest actuator declarations.** The env's action-space and the manifest's actuator-space must align for URML adapters to dispatch correctly; the constraint is not today first-class.

### Compatibility notes

- **Vendor / org.** [`google-deepmind`](https://github.com/google-deepmind) — vendor-direct.
- **Flagship repo.** [`google-deepmind/mujoco_playground`](https://github.com/google-deepmind/mujoco_playground) — Apache-2.0, 2k stars, Issues + Discussions both enabled, last commit 2026-05-27, **not archived**.
- **Origin.** Google DeepMind, US / UK. Passes US-federal default policy.
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active (daily commits); DeepMind robotics team is the maintainer signal.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; simulation-substrate declaration Spec RFC queued in parallel (shared with Move-2 RFC-0050 Isaac-Lab, RFC-0051 CARLA, RFC-0060 MuJoCo-core).
- Reference runtime: future `reference/sim-runtime/MuJoCoPlaygroundAdapter` is a candidate; complements the existing `reference/ros2-runtime/` real-robot adapter pattern by exercising the same URML primitives in sim.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Simulation-substrate Spec RFC prerequisite.** Same gap as Move-2 sim engagements (RFC-0050 / RFC-0051 / RFC-0060).
- **Move-2 RFC-0060 overlap.** `google-deepmind/mujoco` is already engaged; this is a sibling repo in the same org. Engagement framing must be explicit that the env layer is distinct from the simulator-core layer.

## Alternatives considered

1. **Skip MuJoCo Playground as duplicate with RFC-0060 mujoco-core.** Rejected. The env layer is the natural URML adapter integration point; mujoco-core is the physics engine. Different abstractions.
2. **Bundle MuJoCo Playground + Isaac-Lab (Move-2 RFC-0050) into one sim-env RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Engage `google-deepmind/control` (older DeepMind suite) instead.** Considered. `mujoco_playground` is the actively-maintained successor; `dm_control` is historically important but lower velocity.

## Prior art

- [`google-deepmind/mujoco_playground`](https://github.com/google-deepmind/mujoco_playground) — the upstream repo.
- [RFC-0060 (MuJoCo core)](0060-mujoco-outreach.md) — Move-2 engaged the simulator core; this RFC engages the env layer above.
- [RFC-0050 (NVIDIA Isaac)](0050-nvidia-isaac-outreach.md) — Move-2 engaged Isaac-Sim / Isaac-Lab (sibling sim-env surface).
- [RFC-0051 (CARLA)](0051-carla-outreach.md) — Move-2 engaged CARLA sim (sibling sim surface).

## Unresolved questions

For the mujoco_playground maintainers:

1. **Simulation-env manifest fields.** URML's v0.1 has no `simulation.env` declaration. A Spec RFC adding it is queued. What manifest fields would a Playground deployment expect (env-name, version, observation-space, action-space, JAX backend)?
2. **Adapter shape.** Should URML's adapter ship as (a) a contributed example in `mujoco_playground/examples/`, (b) an external `urml-mujoco-playground-bridge` package, or (c) `reference/sim-runtime/` under URML repo?
3. **Engagement-level boundary with mujoco-core (Move-2 RFC-0060).** Are the two engagement threads coordinated, or independent?
4. **Conformance listing.** Would the maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
5. **Anything else.**

## Implementation note

RFC-0144 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml). Cross-reference to [RFC-0060 mujoco-core](0060-mujoco-outreach.md) Move-2 engagement noted explicitly.

## How to respond

`google-deepmind/mujoco_playground` has Issues + Discussions both enabled. Discussions is the preferred surface for design-discussion. URML's planned channel: open a single Discussion (Ideas category), pointing to this RFC, with the engagement-level boundary vs RFC-0060 mujoco-core explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 2k stars, Issues + Discussions enabled, last commit 2026-05-27 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (sim-substrate Spec-RFC prerequisite, Move-2 RFC-0060 overlap on the same org).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Google DeepMind US/UK; default policy passes.
- [x] CLAUDE.md compliance check passed.
