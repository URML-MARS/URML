---
rfc: 0053
title: Open-RMF multi-robot integration, request for comment from open-rmf maintainers
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

# RFC-0053: Open-RMF multi-robot integration, request for comment from open-rmf maintainers

## Summary

URML proposes a `urml-rmf-bridge` package with two complementary integration vectors against Open-RMF (Open Robotics Middleware Framework, OSRF-affiliated):

1. **URML-as-task-source vector.** URML programs compile into RMF task descriptions consumed by `rmf_ros2`'s task dispatcher.
2. **URML-as-fleet-adapter vector.** URML's substrate adapters (`SpotAdapter`, `AnymalAdapter`, `DigitAdapter`, the mobile-runtime adapters, the industrial-arm adapters) serve as RMF fleet adapters, letting Open-RMF orchestrate multiple URML-driven robots in a single facility.

This closes the multi-robot coordination gap adjacent to URML's existing warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)) and to URML's OSRF outreach ([RFC-0037](0037-osrf-gazebo-integration.md)). No URML spec change. Bridge code is not in this PR; the RFC requests review from `open-rmf` maintainers before it ships.

## Motivation

The `open-rmf` GitHub organization (81 public repositories, 814 followers, blog at `osrf.github.io/ros2multirobotbook/`, OSRF-affiliated) is the de facto open multi-robot orchestration stack. It addresses the concerns URML's single-robot adapters intentionally leave outside their scope: fleet-level traffic deconfliction, task allocation across heterogeneous robots, lift and door integration, charging logistics, and human-traffic interaction in shared facilities.

Verified surface on 2026-05-23:

- `open-rmf/rmf` (405 stars, 64 open issues, Apache-2.0, Issues enabled, `enhancement` and `question` labels present, last commit 2026-05-20): the meta-repository and the canonical entry point.
- `open-rmf/rmf_demos` (521 stars, 49 open issues, Apache-2.0, both Issues and Discussions enabled, last commit 2026-05-20): the demos surface with Discussions, the natural venue for architectural design conversations.
- `open-rmf/rmf_ros2` (112 stars, 83 open issues, Apache-2.0, last commit 2026-05-14): the ROS 2 task dispatcher and fleet-manager core.
- `open-rmf/free_fleet` (230 stars, 4 open issues): the open multi-fleet manager.
- `open-rmf/rmf_traffic_editor` (160 stars): traffic graph authoring.
- `open-rmf/rmf-web` (129 stars): the web operator UI.

URML's warehouse profile (RFC-0022 Draft) explicitly addresses mixed-traffic warehouse aisles, multi-AMR handoff at declared docks, and dynamic-obstacle pause behavior. Those concerns are exactly what Open-RMF orchestrates above the single-robot layer. URML stops at "this AMR executes this intent"; Open-RMF starts at "these N AMRs share these aisles, coordinate at these docks, queue at these lifts." The two stacks compose by design.

## Detailed design

URML's existing artifacts that feed in:

- [`docs/rfcs/0022-warehouse-domain-profile.md`](0022-warehouse-domain-profile.md): warehouse profile spec; the natural URML home for multi-AMR scenarios.
- [`docs/rfcs/0037-osrf-gazebo-integration.md`](0037-osrf-gazebo-integration.md): the OSRF/Gazebo outreach RFC. Open-RMF is the multi-robot sibling of OSRF/Gazebo; both live under the same governance umbrella.
- [`reference/legged-runtime/`](../../reference/legged-runtime/), [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/), [`reference/mobile-runtime/`](../../reference/mobile-runtime/), the industrial-arm runtimes: the per-robot adapters that would serve as RMF fleet adapters in the second vector.
- The `CompositeAdapter` pattern from [`reference/px4-runtime/`](../../reference/px4-runtime/): the architectural precedent for composing multiple adapters into one substrate-neutral surface; Open-RMF's fleet-adapter pattern is the multi-robot analog.

### Proposed `urml-rmf-bridge` package shape

```
urml-rmf-bridge/
├── pyproject.toml                  # extras: ["rmf"] -> rmf_ros2 messages + clients
└── src/
    └── urml_rmf_bridge/
        ├── __init__.py
        ├── task_source/
        │   ├── compiler.py         # URML program -> RMF task description
        │   └── dispatcher.py       # submits to rmf_ros2 dispatcher
        └── fleet_adapter/
            ├── adapter.py          # URMLFleetAdapter wraps N URML substrate adapters
            └── config.py           # RMF fleet-config schema bridging
```

The bridge does not modify Open-RMF internals; it composes with the public task-dispatcher API and the published fleet-adapter contract.

### Vector 1: URML-as-task-source

URML programs declare intent. RMF tasks declare what should happen across a fleet (a delivery from A to B, a patrol of a set of waypoints, a charging cycle). The compiler maps URML primitive sequences into RMF task descriptions, validates them against URML's manifest and safety envelope, and submits the resulting task to RMF's dispatcher. The dispatcher then performs traffic deconfliction, robot allocation, and execution scheduling using its existing logic.

| URML primitive sequence | RMF task |
|---|---|
| `move_to(location_a); move_to(location_b)` | `Delivery` task with named pickup and dropoff locations |
| `move_to(patrol_a); move_to(patrol_b); move_to(patrol_a)` | `Patrol` task over the waypoint list |
| `move_to(dock); dock(service: charge)` | `ChargeBattery` task |
| `move_to(location); wait_for(condition); report(...)` | `CustomTask` with the URML program as the action sequence |

### Vector 2: URML-as-fleet-adapter

Open-RMF integrates heterogeneous robot fleets via fleet adapters: per-vendor or per-fleet adapters that translate between RMF's coordination layer and the robot's native interface. URML's substrate adapters already implement the URML `ROSAdapter` Protocol uniformly across legged, humanoid, mobile, and industrial-arm robots. A `URMLFleetAdapter` wraps N URML adapters behind one RMF fleet adapter interface, letting RMF orchestrate (Spot + Digit + Husky + ANYmal) as one fleet through one bridge.

This is the higher-leverage vector. RMF's fleet-adapter library is the integration surface most third-party robot vendors target today; URML offering a single fleet adapter that covers the entire URML adapter family means every URML-supported substrate gains multi-robot coordination for free.

### Compatibility notes

- **License.** Open-RMF repositories are Apache-2.0 across the family. URML is Apache 2.0. Clean.
- **ROS 2.** Open-RMF is ROS 2 native (uses `rclpy` and `rclcpp`). URML's adapters that already speak ROS 2 (`AnymalAdapter`, `DigitAdapter`, the industrial-arm adapters) integrate without an extra translation layer. The non-ROS adapters (`SpotAdapter` via `bosdyn`, `PX4Adapter` via MAVLink) need a thin ROS 2 shim at the fleet-adapter boundary, which is the standard RMF integration pattern for non-native fleets.
- **Traffic schedule.** RMF's traffic schedule is the canonical conflict-avoidance surface. The URML fleet adapter participates in the schedule; URML manifests need no schedule-specific fields (the schedule reasons over the adapter's reported trajectories).
- **Origin.** Open-RMF is community-developed under OSRF's umbrella; same governance as Gazebo (RFC-0037). No origin-policy friction at the manifest or adapter level.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No URML artifact changes. Open-RMF gains a new fleet adapter through its public adapter interface.

## Drawbacks

- **Proposal-only.** Same posture as RFC-0040 / RFC-0044 / RFC-0050 / RFC-0051: the bridge shape is concrete, the package is not yet shipped, maintainer feedback informs the implementation.
- **Two-vector scope is wider than typical.** Task-source and fleet-adapter are different audiences inside Open-RMF (the task team vs the fleet-adapter team). Mitigation: the RFC's "How to respond" section maps each vector to its primary surface.
- **RMF's mapping model.** RMF expects building-level traffic graphs authored in `rmf_traffic_editor`. URML's manifest declares per-robot locations and frames. Bridging the two declarations is real work; Q3 below asks for maintainer guidance.
- **Single-robot edge cases.** A URML program for one robot does not need RMF; routing through the bridge for single-robot deployments is unnecessary overhead. The bridge supports a passthrough mode where single-robot URML programs go directly to the underlying adapter, bypassing RMF.

## Alternatives considered

1. **Single-vector RFC (task-source only or fleet-adapter only).** Rejected. The two vectors target the same maintainer org and share the same package. Splitting them would double the review thread without splitting the audience.
2. **Skip Open-RMF and build URML-native multi-robot orchestration.** Rejected. Open-RMF is the de facto open multi-robot stack with five years of operator deployments. URML's substrate-neutrality story strengthens by composing with mature orchestration, not by competing.
3. **Bundle Open-RMF coverage into the warehouse profile RFC (RFC-0022).** Rejected. RFC-0022 is a spec change to URML; this RFC is an outreach proposal to Open-RMF. Different document kinds with different lifecycles.
4. **Ship the bridge first.** Rejected. RMF's fleet-adapter interface and task description schema have observable choices URML should validate with maintainers before code lands.

## Prior art

- `open-rmf/rmf`: the meta-repository (405 stars, 64 open issues, Apache-2.0, last commit 2026-05-20).
- `open-rmf/rmf_demos`: the demos surface with Discussions enabled (521 stars).
- `open-rmf/rmf_ros2`: the ROS 2 dispatcher and fleet-manager core (112 stars, 83 open issues).
- `open-rmf/free_fleet`: the multi-fleet manager (230 stars).
- `open-rmf/rmf_traffic_editor`: the traffic-graph authoring tool (160 stars).
- The Open-RMF book at `osrf.github.io/ros2multirobotbook/`: the architectural overview.
- [RFC-0022](0022-warehouse-domain-profile.md): the warehouse profile, where multi-AMR mixed traffic is specified at the URML level.
- [RFC-0037](0037-osrf-gazebo-integration.md): the OSRF/Gazebo outreach. Open-RMF is the multi-robot sibling under the same governance.
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0050](0050-nvidia-isaac-lab-integration.md): the two-vector outreach precedents.

## Unresolved questions

Provisional pending Open-RMF maintainer feedback:

### Task-source vector

1. **Task description shape.** URML primitive sequences compile into RMF tasks. Should the bridge target the existing built-in task types (`Delivery`, `Patrol`, `ChargeBattery`) where they map, plus `CustomTask` for everything else, or always emit `CustomTask` for predictability?
2. **Validation handoff.** URML validates the program statically before dispatching. Should the bridge re-validate against RMF's traffic-schedule and fleet-config at submission time, or defer to RMF's dispatcher's own validation?

### Fleet-adapter vector

3. **Manifest-to-traffic-graph bridge.** URML's manifest declares per-robot frames, locations, and docking stations; RMF authors building-level traffic graphs in `rmf_traffic_editor`. What is the recommended bridge between these two declarations? A converter, a co-authoring workflow, or something else?
4. **Heterogeneous fleet adapter.** `URMLFleetAdapter` wraps multiple URML substrate adapters of different kinds (Spot + Digit + Husky + ANYmal as one fleet). Is the existing RMF fleet-adapter interface comfortable with that level of heterogeneity, or does it expect per-vendor adapters in practice?
5. **Non-ROS adapter shim.** URML adapters that bypass ROS 2 (`SpotAdapter` via bosdyn, `PX4Adapter` via MAVLink) need a thin ROS 2 shim at the fleet-adapter boundary. Is there an existing recommended shim pattern, or should the bridge ship its own?

### Shared

6. **Downstream link.** Would Open-RMF be open to a downstream link from the book or from `rmf_demos` to URML's bridge once it publishes?
7. **Anything else.**

## Implementation note

RFC-0052 ships as a single RFC document PR. No bridge code in this PR. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from open-rmf maintainers)

For the task-source team:
1. Task description shape (Q1).
2. Validation handoff (Q2).

For the fleet-adapter team:
3. Manifest-to-traffic-graph bridge (Q3).
4. Heterogeneous fleet adapter (Q4).
5. Non-ROS adapter shim pattern (Q5).

Shared:
6. Downstream link interest (Q6).
7. Anything else.

## How to respond

`open-rmf/rmf_demos` has both Issues and Discussions enabled, which is the right surface for architectural conversations. `open-rmf/rmf` is the meta-repository entry point. URML's planned channel: a Discussion on `open-rmf/rmf_demos` (Ideas or Show & Tell) pointing to this RFC for the broad architectural conversation, optionally cross-referenced from a scoped Issue on `open-rmf/rmf` labelled `enhancement` if the Discussion needs Issue visibility.

URML public Discussions for the broader conversation: https://github.com/URML-MARS/URML/discussions.

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary explains proposal-only posture and the two-vector framing.
- [x] Motivation grounded in verified data (81 repos / 814 followers in the org; rmf 405★ / rmf_demos 521★ / rmf_ros2 112★ / free_fleet 230★; labels and discussion settings confirmed).
- [x] Detailed design references existing URML artifacts (RFC-0022, RFC-0037, the legged/humanoid/mobile runtimes, the CompositeAdapter pattern).
- [x] Alternatives considered (four).
- [x] Drawbacks honest (proposal-only, two-vector scope, RMF mapping-model bridge work, single-robot edge cases).
- [x] Backward compatibility: additive.
- [x] No spec change. No Layer-2 primitive added.
- [x] Surface verified live: `enhancement` and `question` labels present on `open-rmf/rmf`; both Issues and Discussions enabled on `open-rmf/rmf_demos`.
- [x] No em-dashes in body. Voice consistent with the wave.
- [x] Re-read CLAUDE.md §What Claude Should Never Do; compliant. No cloud dependency. No telemetry. URML stays at the per-robot intent level; Open-RMF stays at fleet orchestration; clean separation.
