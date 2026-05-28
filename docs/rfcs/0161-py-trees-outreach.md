---
rfc: 0161
title: py_trees (Python behavior-tree engine for ROS 2) integration, request for comment from splintered-reality maintainers
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

# RFC-0161: py_trees (Python behavior-tree engine for ROS 2) integration, request for comment from splintered-reality maintainers

## Summary

URML does not yet ship a py_trees manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for py_trees — the Python-side de facto behavior-tree engine for ROS 2 — over [`splintered-reality/py_trees`](https://github.com/splintered-reality/py_trees) (license listed as "Other", BSD-style historically), and **requests review and feedback from the py_trees maintainer**. No spec change.

py_trees is the Python-side counterpart to RFC-0160 (BehaviorTree.CPP). Where BehaviorTree.CPP targets C++ deployments and Nav2-style production stacks, py_trees targets Python-side ROS 2 nodes — a different deployment profile that many URML users (researchers, prototyping teams, education) will reach for first. Engaging both gives URML's Layer-3 a two-language compilation story. This RFC also surfaces a **license-clarification ask**: the GitHub API reports `licenseInfo: Other`; URML needs the explicit OSI classification.

## Motivation

`splintered-reality/py_trees` is the most-adopted Python behavior-tree engine in the robotics community (license: Other, 604 stars, Issues + Discussions both enabled, last commit `2026-05-22`, **not archived**). It is the Python BT used by `py_trees_ros` for ROS 2 integration, and it is the canonical recommendation in many ROS 2 tutorials. Maintainer Daniel Stonier originated the project at Yujin Robot and has continued shepherding it through his `splintered-reality` umbrella.

py_trees is interesting to URML for three reasons:

1. **Python-side Layer-3 target.** Mirrors RFC-0160 BehaviorTree.CPP's C++ angle for Python deployments. URML's reference runtimes are Python-first (CLAUDE.md), so the Python BT engine is the natural-fit compilation target for URML's reference implementations.
2. **ROS 2 Python ecosystem.** Most academic and prototyping ROS 2 work happens in Python (`rclpy`); py_trees is the Python BT the community already reaches for. URML's Layer-3 compiling to `py_trees.behaviour.Behaviour` subclasses puts URML programs directly into the canonical ROS 2 Python BT pattern.
3. **Substrate-neutral fit.** Like BehaviorTree.CPP, py_trees runs on ROS 2 *and* standalone (the core library has no ROS dependency; `py_trees_ros` is the optional ROS 2 layer). Compiling to py_trees keeps URML's substrate-neutral promise intact.

This RFC and **RFC-0160 (BehaviorTree.CPP)** form a paired engagement; the Spec RFC for behavior-tree-runtime declaration covers both with different language tags.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `py_trees_runtime_cell.yaml` fixture)

Manifest does not currently declare a behavior-tree runtime. Proposed mapping uses the `custom` escape-hatch (parallel to RFC-0160):

| URML field | Maps to py_trees attribute |
|---|---|
| `behavior_layer.runtime: custom` (`py_trees`) | Declares py_trees is the Layer-3 compile target |
| `behavior_layer.runtime_language: python` | Declares the language family (parallel to RFC-0160's `cpp`) |
| `behavior_layer.runtime_version` | Declares the py_trees semver |
| `behavior_layer.bt_python_module: <module-path>` | Declares the Python module URML's Layer-3 compilation produces |
| `behavior_layer.bt_behaviour_registry: [<class-name>, ...]` | Declares the custom `Behaviour` subclasses URML registers (one per URML primitive) |
| `behavior_layer.bt_ros2_integration: py_trees_ros \| standalone` | Declares whether the deployment uses `py_trees_ros` (ROS 2 wrappers) or standalone py_trees |

### What URML v0.1 does not yet express for py_trees

1. **Behavior-tree runtime declaration.** Shared with RFC-0160. URML's v0.1 manifest has no `behavior_layer.runtime` field.
2. **Python module-path declaration.** URML's compilation produces a Python module; the manifest needs to declare its import path.
3. **`Behaviour` subclass registry declaration.** URML primitives become `py_trees.behaviour.Behaviour` subclasses. The manifest needs to enumerate them.
4. **ROS 2 integration tier declaration.** Whether the deployment uses `py_trees_ros` or standalone py_trees is a deployment-shape concern URML's manifest can declare for downstream observability.

### Compatibility notes

- **Vendor org.** [`splintered-reality`](https://github.com/splintered-reality) — vendor-direct (Daniel Stonier's umbrella).
- **Flagship repo.** [`splintered-reality/py_trees`](https://github.com/splintered-reality/py_trees) — license Other (BSD-style historically — **clarification ask below**), 604 stars, Issues + Discussions both enabled, last commit `2026-05-22`, **not archived**.
- **Companion repos.** [`splintered-reality/py_trees_ros`](https://github.com/splintered-reality/py_trees_ros) (ROS 2 integration); [`splintered-reality/py_trees_ros_tutorials`](https://github.com/splintered-reality/py_trees_ros_tutorials).
- **Origin.** Daniel Stonier (NZ / AU, Yujin Robot lineage). Passes US-federal default policy (allied / Five Eyes-adjacent).
- **License fit.** BSD-style historically composes with URML's Apache-2.0 stance; **license-clarification ask** to confirm OSI classification.
- **Maintainer signal.** Active surface (weekly commits). Sole-maintainer pattern (mirror of RFC-0160).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; behavior-tree-runtime declaration Spec RFC queued (shared with RFC-0160). License-classification follow-up depends on the maintainer's response.
- Reference runtime: future `reference/bt-bridge/UrmlToPyTrees` (a Layer-3 → py_trees Python-module compiler) is the natural integration; composes cleanly above URML's Python-first reference runtimes without the C++ codegen requirement RFC-0160 introduces.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License clarification gate.** URML cannot ship a reference adapter until the OSI classification is confirmed. The RFC asks; the adapter waits.
- **Behavior-tree-runtime Spec RFC prerequisite** (shared with RFC-0160).
- **Sole-maintainer engagement-velocity.** Daniel Stonier maintains py_trees alongside other work; engagement may be slower than a vendor-org project. URML should not block on rapid response.
- **`py_trees_ros` is a separate repo with separate release cadence.** URML's manifest declares the runtime tier (standalone vs. py_trees_ros); the user must align the runtime versions correctly.

## Alternatives considered

1. **Engage only BehaviorTree.CPP (RFC-0160) and have URML's Python users wrap it via pybind.** Rejected. py_trees is the Python community's already-chosen BT engine; forcing a pybind wrapper around a C++ engine adds unnecessary friction and breaks URML's "compile to existing substrates, don't replace them" posture.
2. **Bundle this RFC with RFC-0160.** Rejected. Different maintainers, different language families, different release cadences. The shared Spec RFC for behavior-tree-runtime declaration captures the commonality; per-target engagement covers the differences.
3. **Cross-citation only.** Considered. The license-clarification ask alone makes a direct RFC worth maintainer time.

## Prior art

- [`splintered-reality/py_trees`](https://github.com/splintered-reality/py_trees) — the upstream repo.
- [`splintered-reality/py_trees_ros`](https://github.com/splintered-reality/py_trees_ros) — ROS 2 integration.
- [RFC-0160 (BehaviorTree.CPP)](0160-behaviortree-cpp-outreach.md) — sibling Move-12 RFC, C++ BT engine.
- [RFC-0162 (moveit/moveit_task_constructor)](0162-moveit-task-constructor-outreach.md) — sibling Move-12 RFC, MoveIt-side industrial task planner.

## Unresolved questions

For the splintered-reality py_trees maintainer:

1. **License clarification.** GitHub reports `licenseInfo: Other`. What is the explicit OSI license URML should cite? (BSD-2-Clause? BSD-3-Clause? Some project-specific BSD variant?)
2. **Behavior-tree-runtime declaration shape.** Is `py_trees` the right slug for URML's manifest, or does the maintainer prefer a different naming convention?
3. **`Behaviour` subclass registry declaration.** URML compilation produces custom `Behaviour` subclasses (one per URML primitive). Is the enumerated registry the right manifest shape?
4. **ROS 2 integration tier.** Is the `py_trees_ros \| standalone` distinction the right granularity for URML's manifest, or does the maintainer see additional tiers (`py_trees_ros_interfaces`, custom-ROS-wrapper) worth enumerating?
5. **Adapter home.** URML-side compiler in URML's `reference/bt-bridge/`, contributed example in `py_trees/examples/`, or external bridge repo?
6. **Conformance listing.** Would the py_trees maintainer consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0161 ships as a single RFC document PR (Move-12 batch 3 — robot-command-library cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`splintered-reality/py_trees` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `splintered-reality/py_trees`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license Other — clarification ask, 604 stars, Issues + Discussions enabled, last commit 2026-05-22 active, isArchived: false).
- [x] License-clarification ask flagged up front.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (license gate, Spec-RFC prerequisite, sole-maintainer velocity, py_trees_ros separate cadence).
- [x] Sibling RFC cross-links explicit (RFC-0160 BehaviorTree.CPP, RFC-0162 MoveIt TC).
- [x] No spec change proposed in this RFC.
