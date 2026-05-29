---
rfc: 0269
title: simulation.substrate — declaring the simulation substrate in the Layer-1 manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0269: `simulation.substrate` — declaring the simulation substrate

## Summary

URML deployments today run against either hardware or simulation. URML's manifest has no place to declare the simulation substrate when the deployment is simulated. This RFC adds a `simulation` block with a closed substrate enum (Gazebo / Isaac Sim / MuJoCo / Webots / mujoco_playground / none), per-substrate `simulation_options`, and a `sim_vs_hardware` flag for downstream tooling to distinguish. Optional. Backward compatible.

The surfaces that demanded this RFC are Move-2 RFC-0037 (Gazebo), RFC-0050 (Isaac Sim), Move-11 RFC-0144 (mujoco_playground), and Move-18 RFC-0234 (Webots; staged in user's Move-18 batches).

## Motivation

Simulation substrates are not interchangeable. Gazebo's physics, Isaac Sim's NVIDIA-PhysX acceleration, MuJoCo's contact model, and Webots's plant-simulation focus all produce different runtime behavior. URML programs targeting a Gazebo deployment may run differently in Isaac Sim. URML's manifest needs a place to declare the simulation substrate so downstream tooling can:

1. **Distinguish sim from hardware at validate time.** Conformance tests run against simulation; production runs against hardware. URML's manifest declaring `simulation.substrate: gazebo` vs hardware deployment lets downstream tooling fork the validation strategy.
2. **Surface sim-substrate-specific configuration.** Each simulation substrate has its own world-file format, physics-parameter set, and asset-path conventions. URML's manifest captures the substrate identity; deployment-side tooling consumes the configuration.
3. **Cross-citation with substrate-spine engagements.** Move-2 engaged Gazebo and Isaac Sim; Move-11 engaged mujoco_playground; Move-18 engaged Webots. URML's manifest currently has no field to declare which simulation substrate the deployment composes against.

## Detailed design

### Field shape

```yaml
simulation:                                 # NEW — this RFC, top-level optional
  substrate: gazebo                          # gazebo | isaac_sim | mujoco | webots | mujoco_playground | none | custom
  sim_vs_hardware: simulation                # simulation | hardware | hybrid
  simulation_options:
    world_file: worlds/lab.world             # substrate-specific config
    physics_engine: ode                       # ode | bullet | dart (Gazebo)
    realtime_factor: 1.0                      # 0.1 .. 10.0
    gpu_acceleration: false                   # for Isaac Sim, mujoco_playground
```

### Allowed values for `substrate`

| Value | Description | Reference |
|---|---|---|
| `gazebo` | Gazebo (Classic and Sim) | Move-2 RFC-0037 |
| `isaac_sim` | NVIDIA Isaac Sim | Move-2 RFC-0050 |
| `mujoco` | DeepMind MuJoCo | Cross-reference; URML's primitives compose against MuJoCo bindings |
| `webots` | Cyberbotics Webots | Move-18 RFC-0234 (staged) |
| `mujoco_playground` | DeepMind mujoco_playground | Move-11 RFC-0144 |
| `none` | Hardware deployment (no simulation) | n/a |
| `custom` | Vendor-specific or experimental simulator | escape hatch + `substrate_note` required |

### Allowed values for `sim_vs_hardware`

| Value | Description |
|---|---|
| `simulation` | Pure simulation deployment (no hardware in the loop) |
| `hardware` | Pure hardware deployment (no simulation) |
| `hybrid` | Hardware-in-the-loop / software-in-the-loop / digital-twin deployment |

### Schema fragment (Layer-1)

```jsonc
{
  "simulation": {
    "type": "object",
    "properties": {
      "substrate": {
        "enum": ["gazebo", "isaac_sim", "mujoco", "webots", "mujoco_playground", "none", "custom"]
      },
      "substrate_note": { "type": "string" },
      "sim_vs_hardware": {
        "enum": ["simulation", "hardware", "hybrid"]
      },
      "simulation_options": {
        "type": "object",
        "properties": {
          "world_file": { "type": "string" },
          "physics_engine": { "enum": ["ode", "bullet", "dart", "physx", "mujoco", "custom"] },
          "realtime_factor": { "type": "number", "minimum": 0.0 },
          "gpu_acceleration": { "type": "boolean" }
        }
      }
    },
    "if": {
      "properties": { "substrate": { "const": "custom" } }
    },
    "then": {
      "required": ["substrate_note"]
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing block is acceptable; deployment treated as hardware by default (consistent with sim_vs_hardware defaulting to `hardware` when block is missing).
2. **`substrate: gazebo + physics_engine: physx` warning.** Gazebo doesn't support PhysX natively; the validator surfaces the unusual combination.
3. **`substrate: none` implies `sim_vs_hardware: hardware`.** Cross-check; mismatch fails.
4. **`gpu_acceleration: true` ↔ substrate compatibility.** Isaac Sim and mujoco_playground support GPU acceleration; declaring GPU acceleration with Gazebo Classic emits a warning.
5. **`realtime_factor` sanity range.** Must be `> 0`. A factor of 1.0 is realtime; 0.5 is half-realtime; 2.0 is double-realtime.
6. **Custom requires note.** `substrate: custom` requires `substrate_note`.
7. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read `simulation.substrate` to select the dispatch path. The runtime composes against the simulator's ROS 2 bridge (gazebo_ros, isaac_ros, mujoco_ros, webots_ros2). URML's manifest declaring the substrate lets the runtime auto-load the right bridge package.

The `sim_vs_hardware` field is used by conformance test runners to fork the test strategy (sim tests may relax timing tolerances).

### Conformance test additions

`conformance/tests/test_manifest_simulation.py`:

1. Manifest without `simulation` block passes (defaults to hardware).
2. Manifest with `simulation.substrate: gazebo + sim_vs_hardware: simulation` passes.
3. Manifest with `substrate: gazebo + physics_engine: physx` passes with warning.
4. Manifest with `substrate: none + sim_vs_hardware: simulation` fails (inconsistent).
5. Manifest with `substrate: custom` and no note fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests treated as hardware deployments by default.

## Drawbacks

- **Six-substrate enum is opinionated.** Gazebo Classic vs Gazebo Sim (formerly Ignition) are arguably distinct substrates; URML's enum collapses them. Future RFC could split.
- **`sim_vs_hardware: hybrid` is the messy case.** Hardware-in-the-loop deployments vary widely; URML's manifest declares the general category but the specifics live in `simulation_options`.
- **`physics_engine` enum partly substrate-specific.** ODE/Bullet/DART are Gazebo physics engines; PhysX is Isaac Sim's; MuJoCo is its own. Declaring a physics_engine inconsistent with the substrate is a warning, not an error.
- **No explicit declaration of asset-path conventions.** Each simulator has its own asset structure; URML's `world_file` field captures one of many configuration files. Future RFC may extend.

## Alternatives considered

1. **Skip `simulation.substrate`; let `substrate.class` carry the simulation choice (`ros2_gazebo`, `ros2_isaac`).** Rejected. Simulation and runtime substrate are different axes; conflating loses precision.
2. **Treat `sim_vs_hardware` as a deployment-wide field outside `simulation`.** Considered. Placing it inside `simulation` keeps the simulation-related state together; the field would arguably belong under `deployment` (RFC-0268) if URML's deployment metadata block grows. v0.1 keeps it under `simulation`.
3. **Per-component sim_vs_hardware (sim base + hardware arm).** Rejected for v0.1. Deployment-wide is sufficient; per-component is future work.
4. **Skip the simulation block; let downstream tooling infer from runtime configuration.** Rejected. URML's manifest is the contract; inferring loses the audit trail.

## Prior art

- [Move-2 RFC-0037 (Gazebo)](0037-gazebo-outreach.md), [Move-2 RFC-0050 (Isaac Sim)](0050-isaac-sim-outreach.md), [Move-11 RFC-0144 (mujoco_playground)](0144-mujoco-playground-outreach.md) — outreach RFCs that surfaced these substrates.
- Move-18 RFC-0234 (Webots; staged in batches 2-4) — adds Webots to the enum.
- [RFC-0268 (deployment.commercial_use)](0268-deployment-commercial-use-flag.md) — sibling deployment metadata; may converge into shared deployment block in future.

## Unresolved questions

1. **Gazebo Classic vs Gazebo Sim distinction.** Gazebo Classic (ROS 2 Foxy / Galactic compatibility) and Gazebo Sim (formerly Ignition; ROS 2 Humble+ compatibility) are arguably distinct. URML collapses them; future RFC could split.
2. **Multi-simulator deployments.** Some research deployments run multiple simulators concurrently (Gazebo for visualization + MuJoCo for physics). v0.1 of this field is single-simulator-per-deployment.
3. **Digital-twin metadata.** Hybrid `hardware + simulation` deployments may need richer metadata (which hardware components are real, which are simulated). Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with six checks (consistency, custom-requires-note, physics-engine compatibility, etc.).
3. Conformance tests (five).
4. Update example manifests under `examples/` to declare `simulation.substrate` where applicable.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (enum opinions, hybrid case complexity, physics-engine partial enum, asset-path future work).
- [x] Backward compatibility additive (defaults to hardware).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to Move-2 / Move-11 / Move-18 outreach + sibling RFC-0268.
- [x] CLAUDE.md compliance: enum closure preserves moat; substrate-neutrality preserved (URML doesn't prefer one simulator over another).
