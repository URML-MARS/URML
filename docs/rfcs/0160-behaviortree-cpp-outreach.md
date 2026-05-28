---
rfc: 0160
title: BehaviorTree.CPP (canonical C++ behavior-tree engine) integration, request for comment from BehaviorTree maintainers
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

# RFC-0160: BehaviorTree.CPP (canonical C++ behavior-tree engine) integration, request for comment from BehaviorTree maintainers

## Summary

URML does not yet ship a BehaviorTree.CPP manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for BehaviorTree.CPP — the canonical C++ behavior-tree engine in robotics — over [`BehaviorTree/BehaviorTree.CPP`](https://github.com/BehaviorTree/BehaviorTree.CPP) (MIT), and **requests review and feedback from the BehaviorTree maintainers**. No spec change.

**This is URML's first robot-command-library RFC.** URML's Layer-3 (behavior composition) needs a substrate to compile down to. BehaviorTree.CPP is the dominant C++ choice in ROS 2 and standalone robotics; Layer-3 programs expressed in URML can be compiled to BehaviorTree.CPP nodes for execution. This RFC documents that mapping.

## Motivation

`BehaviorTree/BehaviorTree.CPP` is the de facto C++ behavior-tree engine in robotics (MIT, 4.0k stars, Issues + Discussions both enabled, last commit `2026-05-22`, **not archived**). It's used inside Nav2 (ROS 2's navigation stack), in many industrial deployments, and as a standalone library outside ROS entirely. The maintainer (Davide Faconti, Italy) actively shepherds the project.

BehaviorTree.CPP is interesting to URML for three reasons:

1. **URML's Layer-3 needs a target.** Layer-3 (behavior composition) is the URML layer where parallelism, sequencing, fallbacks, and condition checks live. Behavior trees express exactly those primitives. A URML Layer-3 program can be compiled to a BehaviorTree.CPP `TreeNode` graph; the substrate is general-purpose, predictable, and well-tooled (Groot is the BT visual editor).
2. **Substrate-neutral fit.** Per CLAUDE.md, "If a primitive's specification is unimplementable on a substrate that does not use ROS, it is a leaky primitive and needs rework." BehaviorTree.CPP runs on ROS 2 *and* standalone (no `rclcpp` dependency in the core). Compiling Layer-3 to BehaviorTree.CPP keeps URML's substrate-neutral promise intact.
3. **Already-tooled visual surface.** Groot 2 provides a visual editor for BT XML files. URML programs that compile to BT XML inherit Groot's tooling for free — an unusual "URML the typed-intent language → BT the executable graph → Groot the visualizer" pipeline that any of the three layers can be the entry point for.

This RFC and **RFC-0161 (splintered-reality/py_trees)** form a paired engagement: BehaviorTree.CPP is the C++ side; py_trees is the Python side. Both target the same Layer-3 → BT compilation; the manifest's "BT target class" declaration covers both.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `behaviortree_cpp_runtime_cell.yaml` fixture)

Manifest does not currently declare a behavior-tree runtime. Proposed mapping uses the `custom` escape-hatch (parallel to the speech and translation engine declarations in Move-12 batches 1-2):

| URML field | Maps to BehaviorTree.CPP attribute |
|---|---|
| `behavior_layer.runtime: custom` (`behaviortree_cpp`) | Declares BehaviorTree.CPP is the Layer-3 compile target |
| `behavior_layer.runtime_language: cpp` | Declares the language family (parallel to RFC-0161's `python`) |
| `behavior_layer.runtime_version` | Declares the BehaviorTree.CPP semver (the API has evolved across major versions; the manifest needs the version pin) |
| `behavior_layer.bt_xml_path: <relative>` | Declares the BT XML file URML's Layer-3 compilation produces |
| `behavior_layer.bt_node_registry: [<node-name>, ...]` | Declares the custom BT nodes URML registers (one per URML primitive) |

### What URML v0.1 does not yet express for BehaviorTree.CPP

1. **Behavior-tree runtime declaration.** URML's v0.1 manifest has no `behavior_layer.runtime` field. Spec RFC for behavior-tree-runtime declaration is queued, shared with RFC-0161 (py_trees, Python sibling). Both projects target the same Layer-3 substrate concept; the declaration covers both with different language tags.
2. **BT XML file declaration.** URML's compilation produces a BT XML; the manifest needs to declare where it lives and which BT version's schema it conforms to.
3. **Custom-node registry declaration.** URML primitives become custom BT nodes (`AsyncActionNode`, `ConditionNode`, etc.). The manifest needs to list which nodes the URML compilation registers so that Groot and other downstream tools can discover them.

### Compatibility notes

- **Vendor org.** [`BehaviorTree`](https://github.com/BehaviorTree) — vendor-direct (Davide Faconti's project umbrella).
- **Flagship repo.** [`BehaviorTree/BehaviorTree.CPP`](https://github.com/BehaviorTree/BehaviorTree.CPP) — MIT, 4.0k stars, Issues + Discussions both enabled, last commit `2026-05-22`, **not archived**.
- **Companion repo.** [`BehaviorTree/Groot2`](https://github.com/BehaviorTree/Groot2) — the visual editor (license differs from core; commercial tier exists).
- **Origin.** Davide Faconti (Italy). Passes US-federal default policy (NATO / EU allied).
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active surface (weekly commits). Sole-maintainer pattern (similar to URML's own posture) — engagement should be calibrated to a single-maintainer's bandwidth.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; behavior-tree-runtime declaration Spec RFC queued (shared with RFC-0161). BT XML compilation may surface a separate Spec RFC.
- Reference runtime: future `reference/bt-bridge/UrmlToBehaviorTreeCpp` (a Layer-3 → BT XML compiler emitting BehaviorTree.CPP-compatible XML + a C++ template that wires URML primitives to custom BT nodes) is the natural integration shape.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Behavior-tree-runtime Spec RFC prerequisite** (shared with RFC-0161).
- **C++ template generation.** URML's reference adapter would generate C++ code (the custom-node wrappers). This is a build-time dependency URML's other adapters don't have; it adds a CMake / compiler requirement on the deployment target.
- **BT XML schema versioning.** BehaviorTree.CPP's XML schema has evolved (v3 → v4 was a notable break). URML's compilation must pin to a specific schema version.
- **Groot 2 license shape.** Groot 2 ships under a commercial-tier model. URML's documentation should not assume Groot is freely available for all use cases; the manifest declares the runtime, not the editor.

## Alternatives considered

1. **Engage only py_trees (RFC-0161) as the canonical Layer-3 target.** Rejected. py_trees is Python; many production robotics stacks ship the BT runtime in C++ for performance / determinism. Both halves are necessary.
2. **Skip behavior-tree engagement; have URML's Layer-3 ship its own runtime.** Rejected explicitly. URML's posture is "sit above existing runtimes, not replace them" (CLAUDE.md). BT is the dominant runtime; URML should compile to it, not compete.
3. **Compile to ROS 2 Nav2 BT specifically rather than BehaviorTree.CPP generically.** Rejected. Nav2 uses BehaviorTree.CPP; targeting the engine rather than the Nav2-specific use lets URML serve non-Nav2 deployments too.
4. **Cross-citation only.** Considered. The Layer-3 mapping is concrete enough that an explicit RFC is worth maintainer time.

## Prior art

- [`BehaviorTree/BehaviorTree.CPP`](https://github.com/BehaviorTree/BehaviorTree.CPP) — the upstream repo.
- [`BehaviorTree/Groot2`](https://github.com/BehaviorTree/Groot2) — the visual editor.
- [`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2) — Nav2, BehaviorTree.CPP's largest single consumer.
- [RFC-0161 (splintered-reality/py_trees)](0161-py-trees-outreach.md) — sibling Move-12 RFC, Python BT engine.
- [RFC-0162 (moveit/moveit_task_constructor)](0162-moveit-task-constructor-outreach.md) — sibling Move-12 RFC, MoveIt-side industrial task planner (related but distinct surface).

## Unresolved questions

For the BehaviorTree maintainers:

1. **Behavior-tree-runtime declaration shape.** Is `behaviortree_cpp` the right slug for URML's manifest, or does the team prefer a specific naming convention for downstream-manifest declarations?
2. **BT XML schema version.** Which schema version (3.x vs. 4.x) should URML's v0.1 compilation target? Is there a forward-looking version the team would recommend pinning to?
3. **Custom-node registry declaration.** URML compilation produces custom BT nodes (one per URML primitive). Is the manifest's enumerated registry the right shape, or does the team have a preferred convention?
4. **Groot 2 boundary.** URML's manifest declares the BehaviorTree.CPP runtime, not Groot 2 (which is a separate concern). Should URML's documentation explicitly distinguish the open-source runtime from the commercial-tier editor?
5. **Adapter home.** URML-side compiler in URML's `reference/bt-bridge/`, contributed example in `BehaviorTree.CPP/examples/`, or external bridge repo?
6. **Conformance listing.** Would the BehaviorTree maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0160 ships as a single RFC document PR (Move-12 batch 3 — robot-command-library cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`BehaviorTree/BehaviorTree.CPP` has Issues + Discussions both enabled. URML's planned channel: open a single Discussion (Ideas category preferred for design-discussion) on `BehaviorTree/BehaviorTree.CPP`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 4.0k stars, Issues + Discussions enabled, last commit 2026-05-22 active, isArchived: false).
- [x] First robot-command-library RFC framing noted up front.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (Spec-RFC prerequisite, C++ codegen requirement, BT schema versioning, Groot license shape).
- [x] Sibling RFC cross-links explicit (RFC-0161 py_trees, RFC-0162 MoveIt TC).
- [x] Sole-maintainer engagement-velocity calibration noted.
- [x] No spec change proposed in this RFC.
