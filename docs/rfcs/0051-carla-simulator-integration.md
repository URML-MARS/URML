---
rfc: 0051
title: CARLA simulator integration, request for comment from carla-simulator maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-23
updated: 2026-05-23
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

# RFC-0051: CARLA simulator integration, request for comment from carla-simulator maintainers

## Summary

URML proposes a `reference/carla-runtime/` adapter and a conformance lane that runs URML autonomous-vehicle programs inside CARLA. The proposal completes the AV triangle URML currently covers via two adjacent RFCs: [RFC-0042](0042-waymo-open-dataset.md) (Waymo Motion Dataset, the recorded-driving vertex) and [RFC-0020](0020-autoware-av-substrate.md) (Autoware substrate, the runtime vertex). CARLA is the simulator vertex. No URML spec change. The adapter code is not in this PR; the RFC requests review from `carla-simulator/carla` maintainers before it ships.

## Motivation

`carla-simulator/carla` (13,980 stars, 1,180 open issues, MIT license, both Issues and Discussions enabled, `feature request` and `question` labels present, last commit 2026-05-22, default branch `ue5-dev`) is the dominant open AV simulator in research and industry training pipelines. It exposes a Python API for spawning vehicles, configuring sensors, running scenarios, and replaying logged drives. The community is large enough that any vendor-neutral AV language has to demonstrate it works in CARLA to be credible.

URML's AV story is real but spread across spec and dataset work. RFC-0020 proposes the `av` profile and the `plan_path` / `follow_trajectory` primitives. RFC-0042 proposes a conformance demonstration against the Waymo Motion Dataset. RFC-0051 closes the loop by binding URML programs to CARLA's executable sim, so an AV-profile URML program can be authored against the spec, validated against a manifest, executed in CARLA, and cross-checked against Waymo-derived scenarios.

## Detailed design

URML's existing AV-adjacent artifacts:

- [`docs/rfcs/0020-autoware-av-substrate.md`](0020-autoware-av-substrate.md): the AV substrate RFC (Draft). Adds `plan_path`, `follow_trajectory`, the `av` profile, and the `hd_map` / `odd` / `mrm` manifest blocks.
- [`docs/rfcs/0042-waymo-open-dataset.md`](0042-waymo-open-dataset.md): the Waymo Motion Dataset conformance-demo RFC.
- [`reference/px4-runtime/`](../../reference/px4-runtime/), [`reference/marine-runtime/`](../../reference/marine-runtime/): the structural templates for a vendor-specific runtime package with lazy imports and a no-ROS posture.
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/), [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): the simulator-runtime templates.

### Proposed `reference/carla-runtime/` package shape

```
reference/carla-runtime/
├── pyproject.toml                # extras = ["carla"] -> carla
└── src/
    └── urml_carla_runtime/
        ├── __init__.py
        ├── adapter.py            # CarlaAdapter implements ROSAdapter Protocol
        ├── config.py             # CarlaAdapterConfig (host, port, world)
        └── _version.py
```

`CarlaAdapter` lazily imports the `carla` Python client (the standard CARLA PythonAPI), connects to a running CARLA server, and translates URML primitives into CARLA actor commands. The package mirrors `px4-runtime` and `marine-runtime` exactly: lazy dependency, no ROS 2 requirement, failures returned not raised.

### Proposed URML primitive to CARLA mapping

| URML primitive | CARLA realisation |
|---|---|
| `move_to(pose)` | spawn or relocate the ego vehicle; `apply_control` to drive toward target |
| `plan_path` (per RFC-0020) | CARLA's built-in global route planner over the map's road graph |
| `follow_trajectory` (per RFC-0020) | per-tick `apply_control` along the planned waypoints |
| `wait_for(condition.traffic_light)` | observe `TrafficLight` actors and predicate on state |
| `wait_for(condition.distance_threshold)` | observe actor positions and predicate on relative pose |
| `measure(what)` | read attached `Sensor` (lidar, camera, GNSS, IMU, collision) |
| `report(facts, ...)` | structured record to a local sink |

The not-applicable primitives (`grasp`, `release`, `dock`, `take_off`, `land`, `return_to_home`) return brand-scoped not-supported tags.

### Proposed conformance lane

A new `conformance/lanes/carla/` directory mirrors RFC-0044's `conformance/lanes/aws-worlds/` shape. Each lane fixture pairs a CARLA scenario (Town01 intersection, Town04 highway merge, etc.) with the URML programs that validate against the AV profile and execute correctly under CarlaAdapter. The lane is gated behind a `URML_CARLA_LANE=1` env flag.

### Compatibility notes

- **License.** CARLA is MIT. The `carla` Python client wheel ships under the same. URML is Apache 2.0. The adapter imports `carla` lazily through extras.
- **Engine.** CARLA's `ue5-dev` is the current development branch on Unreal Engine 5; the stable releases also run on UE4. The adapter targets the documented Python API surface which is engine-version-agnostic at the application level.
- **Sim host.** Running CARLA needs a GPU host; hermetic tests use a mock CARLA client and never connect.
- **Origin.** CARLA originated at CVC Barcelona (Spain) and is community-maintained. Spain is on no covered list. URML's bundled default policy operates at the manifest provenance level, not at the simulator level.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No URML artifact changes.

## Drawbacks

- **Proposal-only.** Same posture as RFC-0040 / RFC-0044 / RFC-0050: the adapter shape is concrete, the package is not yet shipped, maintainer feedback informs the implementation before code lands.
- **RFC-0020 not yet ratified.** `plan_path` / `follow_trajectory` are Draft. The CARLA adapter can ship a v0.1-only subset (move_to, measure, wait_for, report) before RFC-0020 ratifies and gain full coverage afterward.
- **Sim version cadence.** CARLA's UE4 → UE5 transition means the adapter has to track which UE major the deployed server runs.

## Alternatives considered

1. **Ship the adapter first.** Rejected. CARLA's scenario-runner and the Leaderboard challenge have specific conventions URML's lane should respect; a pre-RFC catches the choices.
2. **Skip CARLA, focus on Autoware sim (Awsim).** Rejected. CARLA's community is larger and its API more stable. Awsim is the Autoware-side simulator (covered indirectly by RFC-0020).
3. **Bundle CARLA into the AWS RoboMaker conformance-lane RFC.** Rejected. CARLA is its own community with its own maintainers; bundling dilutes the outreach.

## Prior art

- `carla-simulator/carla`: the upstream simulator (13,980 stars, 1,180 open issues, MIT, last commit 2026-05-22).
- CARLA Leaderboard and the Autonomous Driving Challenge.
- [RFC-0020](0020-autoware-av-substrate.md): the AV substrate RFC.
- [RFC-0042](0042-waymo-open-dataset.md): the dataset conformance-demo precedent.
- [RFC-0044](0044-aws-robotics-sim-worlds.md): the simulator-conformance-lane precedent.

## Unresolved questions

Provisional pending CARLA maintainer feedback:

1. **Scenario-runner integration.** CARLA's `scenario_runner` has its own scenario description format (OpenSCENARIO and CARLA's own). Should URML's conformance lane bridge through scenario-runner, or run URML programs as standalone Python clients against the server?
2. **Leaderboard relationship.** The CARLA Leaderboard is the canonical evaluation surface for AV stacks. Is a non-competing URML reference-execution lane relevant to the Leaderboard's scope?
3. **UE4 vs UE5.** Which engine major should URML's adapter pin against first? The `ue5-dev` branch is the active development line.
4. **Map coverage.** Towns 01-12 cover the standard test set. Are there community-recommended scenarios per map the URML lane should target first?
5. **Sensor model.** CARLA's sensor catalog (lidar, semantic-lidar, camera variants, GNSS, IMU, radar, depth, collision) maps onto URML's `Sensor` and `Camera` manifest blocks. Anything URML should declare differently?
6. **Downstream link.** Would CARLA be open to a downstream link from the docs to URML's conformance lane once it publishes?
7. **Anything else.**

## Implementation note

RFC-0051 ships as a single RFC document PR. No adapter code in this PR. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from carla-simulator maintainers)

1. Scenario-runner vs direct-client integration (Q1).
2. Leaderboard relationship (Q2).
3. UE4 vs UE5 targeting (Q3).
4. Recommended scenarios per map (Q4).
5. Sensor manifest mapping (Q5).
6. Downstream link interest (Q6).
7. Anything else.

## How to respond

`carla-simulator/carla` accepts public Issues and Discussions. `feature request` and `question` labels exist. URML's planned channel: a single Issue labelled `feature request` pointing to this RFC, with a cross-post on Discussions if the maintainers prefer design conversations there.

URML public Discussions for the broader conversation: https://github.com/URML-MARS/URML/discussions.

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary explains proposal-only posture and the AV triangle (Waymo + Autoware + CARLA).
- [x] Motivation grounded in verified data (13,980 stars, 1,180 open issues, both Issues and Discussions enabled, last commit yesterday).
- [x] Detailed design references existing artifacts (`isaac-runtime`, `mujoco-runtime`, RFC-0020, RFC-0042, RFC-0044).
- [x] Alternatives considered (three).
- [x] Drawbacks honest (proposal-only, RFC-0020 dependency, UE version cadence).
- [x] Backward compatibility: additive.
- [x] No spec change. No Layer-2 primitive added (RFC-0020's two primitives are referenced, not duplicated).
- [x] Surface verified live: `feature request` and `question` labels present.
- [x] No em-dashes in body. Voice consistent with the wave.
- [x] Re-read CLAUDE.md §What Claude Should Never Do; compliant. No cloud dependency. No telemetry.
