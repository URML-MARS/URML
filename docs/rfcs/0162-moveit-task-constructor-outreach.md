---
rfc: 0162
title: MoveIt Task Constructor (MoveIt 2 hierarchical task planning) integration, request for comment from moveit maintainers
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

# RFC-0162: MoveIt Task Constructor (MoveIt 2 hierarchical task planning) integration, request for comment from moveit maintainers

## Summary

URML does not yet ship a MoveIt Task Constructor manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for MoveIt Task Constructor (MTC) — the MoveIt 2 framework for composing hierarchical manipulation tasks from solver stages — over [`moveit/moveit_task_constructor`](https://github.com/moveit/moveit_task_constructor) (BSD-3-Clause), and **requests review and feedback from the moveit maintainers**. No spec change.

**This is URML's first industrial-manipulation-substrate RFC.** URML's industrial profile (RFC-0013) ships the `pick_from`, `place_at`, and `swap_tool` primitives. MoveIt Task Constructor is the dominant ROS 2 framework for executing these primitives on actual manipulator arms. The mapping is concrete: each URML industrial primitive corresponds to one or more MTC stages.

## Motivation

`moveit/moveit_task_constructor` is the de facto MoveIt 2 framework for hierarchical manipulation planning (BSD-3-Clause, 271 stars, Issues + Discussions both enabled, last commit `2026-04-23`, **not archived**). It composes complex manipulation tasks (pick-and-place, tool exchange, peg-in-hole) from a library of solver stages — `GeneratePose`, `MoveTo`, `Connect`, `PickPlace`, etc. — that hand off solution proposals between each other.

MTC is interesting to URML for three reasons:

1. **Direct map onto URML industrial primitives.** URML's `pick_from(object, source)` decomposes naturally into MTC's `GeneratePose` (grasp pose) → `Connect` (approach) → `PickPlace::pick` → `Connect` (retreat) sequence. `place_at` is the mirror; `swap_tool` is `Connect` + `PickPlace::release` + tool-change message. The mapping is concrete enough to be implementable.
2. **Industrial-arm runtime path.** URML already ships an `industrial-arm-runtime` reference package. Adding MTC as a backend (alongside whatever the runtime currently uses) makes URML's industrial story land where the ROS 2 industrial community already is.
3. **Solver-stage abstraction matches URML's intent layer.** MTC's stage abstraction is conceptually similar to URML's primitive abstraction — both are typed-intent fragments that compose into larger task graphs. The mapping is structural, not just syntactic.

This RFC is **distinct from RFC-0160 (BehaviorTree.CPP)** and **RFC-0161 (py_trees)**. Behavior trees are general-purpose Layer-3 substrates; MTC is a manipulation-specific Layer-2 / Layer-3 substrate. The engagements are complementary, not duplicative.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `moveit_task_constructor_cell.yaml` fixture)

Manifest does not currently declare a manipulation-task substrate. Proposed mapping uses the `custom` escape-hatch:

| URML field | Maps to MTC attribute |
|---|---|
| `manipulation_substrate: custom` (`moveit_task_constructor`) | Declares MTC is the manipulation-task backend |
| `manipulation_substrate.moveit_planning_group: <group-name>` | Declares the MoveGroup the MTC stages target (e.g., `panda_arm`) |
| `manipulation_substrate.mtc_stages: [Pick, Place, SwapTool, ...]` | Declares the MTC stage classes URML's primitives compile to |
| `manipulation_substrate.mtc_solver: [Pipeline, RRTConnect, ...]` | Declares the solver pipeline MTC uses |
| `manipulation_substrate.mtc_planning_scene_source: ros_topic \| static_yaml` | Declares the planning-scene source MTC consumes |

### URML primitive → MTC stage mapping (proposed)

| URML primitive | MTC stage decomposition |
|---|---|
| `pick_from(object, source)` | `GeneratePose(grasp) → Connect(approach) → PickPlace::pick → Connect(retreat)` |
| `place_at(object, target)` | `GeneratePose(place) → Connect(approach) → PickPlace::release → Connect(retreat)` |
| `swap_tool(from_tool, to_tool)` | `Connect(approach_tool_changer) → PickPlace::release → Connect(rotate) → PickPlace::pick → Connect(retreat)` |

### What URML v0.1 does not yet express for MTC

1. **Manipulation-substrate declaration.** URML's v0.1 manifest has no field for declaring the manipulation-task backend.
2. **Planning-scene source declaration.** MTC consumes a `PlanningScene`; the manifest needs to declare where that scene comes from (ROS topic, static YAML, runtime construction).
3. **Solver-pipeline declaration.** MTC supports multiple motion-planning solvers (OMPL pipelines, CHOMP, STOMP, Pilz). URML's manifest should declare which pipeline is active.
4. **Stage-to-primitive mapping declaration.** URML's compilation produces specific MTC stage sequences per primitive; the manifest needs to make the mapping explicit so deployments can override individual stages.

### Compatibility notes

- **Vendor org.** [`moveit`](https://github.com/moveit) — vendor-direct (MoveIt community; PickNik Robotics led).
- **Flagship repo.** [`moveit/moveit_task_constructor`](https://github.com/moveit/moveit_task_constructor) — BSD-3-Clause, 271 stars, Issues + Discussions both enabled, last commit `2026-04-23`, **not archived**.
- **Companion repos.** [`moveit/moveit2`](https://github.com/moveit/moveit2) (MoveIt 2 core), [`ros-planning/moveit2_tutorials`](https://github.com/ros-planning/moveit2_tutorials).
- **Origin.** MoveIt community (DE / US — PickNik US, plus German robotics community contributors). Passes US-federal default policy.
- **License fit.** BSD-3-Clause cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface (weekly commits). Multi-maintainer community — engagement-velocity should be higher than sole-maintainer projects.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. Two Spec RFCs queued: manipulation-substrate declaration (novel; this RFC surfaces it first); URML-primitive-to-MTC-stage mapping (novel; documents the compilation; may be in spec rather than just adapter).
- Reference runtime: future `reference/industrial-arm-runtime/MTCBackend` (an MTC-backed implementation of the existing industrial-arm runtime's pick/place/swap_tool interface) is the natural integration. Cross-link to existing `reference/industrial-arm-runtime/` package.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **MoveIt 2 dependency.** A URML deployment that declares MTC as its manipulation substrate inherits the full MoveIt 2 / ROS 2 stack. Heavy dependency for non-MoveIt deployments.
- **Two Spec RFCs prerequisite.** Manipulation-substrate declaration + URML-primitive-to-stage mapping both need to land for the manifest fields to be coherent.
- **Solver-pipeline configuration is non-trivial.** MTC's solver pipeline is one of the more complex configuration surfaces in MoveIt 2; URML's manifest may surface only a high-level selector and defer the details to MoveIt's own config.
- **Tight ROS 2 coupling.** Unlike RFC-0160 (BehaviorTree.CPP) and RFC-0161 (py_trees), MTC has tight ROS 2 coupling; the substrate-neutral promise here is partial — the URML manifest still describes the abstract pick / place / swap_tool primitives; the MTC backend is one of several possible implementations.

## Alternatives considered

1. **Engage MoveIt 2 core (`moveit/moveit2`) instead of MTC specifically.** Rejected. MoveIt 2 core is a planning library; MTC is the task-composition framework above it. URML's primitives map onto MTC stages, not directly onto MoveIt 2 planners.
2. **Engage ROS-Industrial framework directly.** Considered. The MTC engagement covers the planning-side; ROS-Industrial's `industrial_core` covers the comm-side. URML may need a separate engagement for ROS-Industrial later. Out of scope here.
3. **Treat URML's industrial primitives as substrate-specific and let downstream users wire to MTC themselves.** Rejected. The pick / place / swap_tool primitives are exactly the level of abstraction MTC stages address; documenting the mapping is the value.
4. **Cross-citation only.** Considered. The primitive-to-stage mapping is concrete enough that an explicit RFC is worth maintainer time.

## Prior art

- [`moveit/moveit_task_constructor`](https://github.com/moveit/moveit_task_constructor) — the upstream repo.
- [`moveit/moveit2`](https://github.com/moveit/moveit2) — MoveIt 2 core.
- [RFC-0013 (industrial profile)](0013-industrial-profile.md) — URML's industrial primitives (`pick_from`, `place_at`, `swap_tool`) that this RFC maps to MTC stages.
- [RFC-0160 (BehaviorTree.CPP)](0160-behaviortree-cpp-outreach.md) — sibling Move-12 RFC, generic Layer-3 substrate.
- [RFC-0161 (py_trees)](0161-py-trees-outreach.md) — sibling Move-12 RFC, Python Layer-3 substrate.

## Unresolved questions

For the moveit maintainers:

1. **Manipulation-substrate declaration shape.** Is `moveit_task_constructor` the right slug for URML's manifest, or does the MoveIt team have a preferred naming convention?
2. **Primitive-to-stage mapping.** Is the proposed `pick_from → GeneratePose / Connect / PickPlace::pick / Connect` decomposition correct, or are there standard MTC patterns URML should follow instead?
3. **Planning-scene source enum.** Is `ros_topic \| static_yaml` the right granularity, or are there additional sources (database-backed, runtime-constructed) common in production?
4. **Solver-pipeline declaration.** Is a high-level selector (`Pipeline, RRTConnect, CHOMP, ...`) sufficient, or does the MoveIt team recommend a finer-grained manifest field?
5. **Adapter home.** URML-side adapter in URML's `reference/industrial-arm-runtime/`, contributed example in `moveit_task_constructor/examples/`, or external bridge repo?
6. **Conformance listing.** Would the moveit maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0162 ships as a single RFC document PR (Move-12 batch 3 — robot-command-library cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`moveit/moveit_task_constructor` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `moveit/moveit_task_constructor`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 271 stars, Issues + Discussions enabled, last commit 2026-04-23 active, isArchived: false).
- [x] First industrial-manipulation-substrate RFC framing noted up front.
- [x] Concrete primitive-to-stage decomposition tabulated.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (MoveIt 2 dependency, Spec-RFCs prerequisite, solver-config complexity, ROS 2 tight coupling).
- [x] Sibling RFC cross-links explicit (RFC-0013 industrial profile, RFC-0160 BehaviorTree.CPP, RFC-0161 py_trees).
- [x] No spec change proposed in this RFC.
