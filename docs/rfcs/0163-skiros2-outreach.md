---
rfc: 0163
title: SkiROS2 (knowledge + skills framework for ROS 2) integration, request for comment from RobotLabLTH maintainers
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

# RFC-0163: SkiROS2 (knowledge + skills framework for ROS 2) integration, request for comment from RobotLabLTH maintainers

## Summary

URML does not yet ship a SkiROS2 manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for SkiROS2 — the Lund University Robotics Lab (LTH) knowledge-and-skills framework for ROS 2 — over [`RobotLabLTH/SkiROS2`](https://github.com/RobotLabLTH/SkiROS2) (license listed as "Other"), and **requests review and feedback from the RobotLabLTH maintainers**. No spec change.

SkiROS2 is interesting to URML for a structural reason that distinguishes it from the other Move-12 robot-command-library targets: it pairs a **skill** abstraction (Layer-2-like) with a **knowledge graph** (scene + relations) that URML's manifest does not yet model. Engaging here surfaces the knowledge-graph substrate as a new manifest concern. This RFC also surfaces a **license-clarification ask** (GitHub API reports "Other") and a **repo-location correction** (URML internal notes had this at Aalborg / RVMI; the active canonical repo is at Lund University Robotics Lab).

## Motivation

`RobotLabLTH/SkiROS2` is the actively-maintained successor to the SkiROS skill-framework lineage (license: Other, 224 stars, Issues enabled, last commit `2025-06-09`, **not archived**). SkiROS pairs:

- A **skill abstraction** — composable typed-intent units that look very much like URML's Layer-2 primitives.
- A **world model** — a knowledge graph that represents scene objects, relations, and affordances, used at planning time to ground skill parameters.

Where the BT-based targets in this Move (RFC-0160 BehaviorTree.CPP, RFC-0161 py_trees) provide pure execution semantics, SkiROS adds a knowledge-grounding layer that is closer to URML's full picture of "robot intent grounded in scene context".

SkiROS2 is interesting to URML for three reasons:

1. **Skill abstraction overlaps URML Layer-2 primitives.** A SkiROS skill is parameterized, typed, composable, and has pre / post / invariant conditions. URML primitives have the same shape. Mapping is concrete: each URML primitive can be expressed as a SkiROS skill class.
2. **Knowledge-graph substrate is novel to URML.** URML's v0.1 manifest does not model scene knowledge. SkiROS engagement surfaces the gap. The Spec RFC question is whether URML should declare a knowledge-graph substrate field (allowing SkiROS, Nav2 keepout zones, semantic-segmentation outputs, RFID inventories, etc. to plug in) or treat the knowledge graph as a SkiROS-internal concern.
3. **Academic-anchored substrate.** SkiROS is Lund University Robotics Lab's framework; engagement is research-collab-direct, parallel to URML's other academic engagements (NASA-JPL ROSA RFC-0108, NUS Octopi RFC-0152).

**Repo-location correction.** URML's earlier internal notes referenced SkiROS at Aalborg University (under the `RVMI` GitHub org). The active canonical repo is at `RobotLabLTH/SkiROS2` (Lund University Robotics Lab / Department of Automatic Control, LTH = Faculty of Engineering at Lund). The Aalborg / RVMI lineage exists historically but is not the current upstream. This RFC engages the Lund team directly.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `skiros2_cell.yaml` fixture)

Manifest does not currently declare a skill-framework substrate or a knowledge-graph substrate. Proposed mapping uses the `custom` escape-hatch:

| URML field | Maps to SkiROS2 attribute |
|---|---|
| `behavior_layer.skill_framework: custom` (`skiros2`) | Declares SkiROS2 is the skill substrate |
| `behavior_layer.skill_registry: [<skill-class>, ...]` | Declares the SkiROS skill classes URML's primitives compile to |
| `behavior_layer.knowledge_graph_substrate: custom` (`skiros_world_model`) | Declares the world-model backend (novel field) |
| `behavior_layer.knowledge_graph_seed_path: <yaml-path>` | Declares the static world-model seed file |
| `behavior_layer.skill_grounding_mode: world_model \| runtime_query \| hybrid` | Declares how skill parameters get grounded (novel field) |

### URML primitive → SkiROS skill mapping (proposed)

| URML primitive | SkiROS skill shape |
|---|---|
| Layer-2 primitives (move_to, pick_from, place_at, ...) | One SkiROS skill class per primitive, with URML's typed parameters as the skill's parameter list |
| Layer-3 composition (sequence, parallel, fallback) | SkiROS sub-skill orchestration (SkiROS supports the same composition primitives) |
| Knowledge-graph queries | New URML construct: a primitive that takes a world-model query as a parameter |

### What URML v0.1 does not yet express for SkiROS2

1. **Skill-framework declaration.** URML's v0.1 manifest has no field for declaring the skill-framework substrate.
2. **Knowledge-graph substrate declaration.** Novel manifest field; SkiROS surfaces the gap. The Spec RFC must decide whether URML adopts a knowledge-graph substrate concept or treats it as substrate-internal.
3. **Skill grounding mode.** SkiROS's world-model-grounding pattern (parameters resolved against the knowledge graph at runtime) is distinct from URML's static-parameter pattern. The manifest needs to declare the grounding model.
4. **World-model seed path.** SkiROS deployments typically ship a YAML seed file declaring scene objects + relations. URML's manifest should declare its path so static validation can flag missing entries.

### Compatibility notes

- **Vendor org.** [`RobotLabLTH`](https://github.com/RobotLabLTH) — vendor-direct (Lund University Robotics Lab, Department of Automatic Control, LTH Faculty of Engineering).
- **Flagship repo.** [`RobotLabLTH/SkiROS2`](https://github.com/RobotLabLTH/SkiROS2) — license Other (**clarification ask below**), 224 stars, Issues enabled, Discussions disabled, last commit `2025-06-09`, **not archived**.
- **Companion repos.** Additional `RobotLabLTH/*` packages provide ROS 2 integration, world-model utilities, and skill libraries.
- **Origin.** Lund University Robotics Lab (Sweden). Passes US-federal default policy (EU / NATO allied).
- **License fit.** Historical SkiROS releases have shipped under BSD-3-Clause; **license-clarification ask** to confirm the current OSI classification.
- **Maintainer signal.** Quarterly commit cadence; research-lab pacing. Engagement-velocity should be calibrated to academic-research cadence.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. Three Spec RFCs queued: skill-framework declaration (parallel to behavior-tree-runtime declaration shared by RFC-0160 / RFC-0161); knowledge-graph substrate declaration (novel; this RFC surfaces it first); skill-grounding-mode declaration (novel; couples to knowledge-graph substrate).
- Reference runtime: future `reference/skill-bridge/UrmlToSkiros` (a Layer-3 / Layer-2 → SkiROS skill compiler) is the natural integration; the world-model adapter would be a separate component.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **License clarification gate.** URML cannot ship a reference adapter until the OSI classification is confirmed.
- **Three Spec RFCs prerequisite.** Knowledge-graph substrate and skill-grounding-mode are both novel manifest concerns; each may warrant its own Spec RFC.
- **Knowledge-graph generality risk.** Adopting a knowledge-graph substrate concept in URML's manifest opens a wide design surface (RDF? property graphs? typed predicates?). The Spec RFC must constrain the scope to "what SkiROS-class substrates actually need" rather than "a general knowledge representation".
- **Research-cadence engagement-velocity.** Academic timelines mean engagement may take weeks rather than days.

## Alternatives considered

1. **Engage only the BT-based Layer-3 targets (RFC-0160, RFC-0161) and skip SkiROS.** Rejected. SkiROS surfaces the knowledge-graph substrate gap which the BT engagements do not; engaging it documents a real URML design question.
2. **Engage SkiROS only at the world-model layer, treating skills as out-of-scope.** Rejected. The skill abstraction is exactly the level URML's primitives address; bypassing it loses the strongest mapping.
3. **Bundle this RFC with RFC-0160 / RFC-0161 (behavior-tree cluster).** Rejected. SkiROS is a distinct substrate with distinct concerns; the shared Spec RFC for "Layer-3 substrate declaration" can cover the commonality.
4. **Cross-citation only.** Considered. The knowledge-graph substrate question alone makes a direct RFC worth maintainer time.

## Prior art

- [`RobotLabLTH/SkiROS2`](https://github.com/RobotLabLTH/SkiROS2) — the upstream repo.
- [SkiROS papers (RAS, RAL)](https://lup.lub.lu.se/search/publication?q=SkiROS) — the academic publications grounding the framework.
- [RFC-0160 (BehaviorTree.CPP)](0160-behaviortree-cpp-outreach.md) — sibling Move-12 RFC, behavior-tree substrate.
- [RFC-0161 (py_trees)](0161-py-trees-outreach.md) — sibling Move-12 RFC, Python BT substrate.
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — academic-anchored engagement parallel.

## Unresolved questions

For the RobotLabLTH maintainers:

1. **License clarification.** GitHub reports `licenseInfo: Other`. What is the explicit OSI license URML should cite? Historical SkiROS shipped BSD-3-Clause; is that current?
2. **Repo-location confirmation.** URML's internal notes previously referenced an Aalborg / RVMI fork. Is `RobotLabLTH/SkiROS2` the canonical upstream for URML to engage going forward?
3. **Skill-framework declaration shape.** Is `skiros2` the right slug for URML's manifest, or does the team prefer a more specific naming convention?
4. **Knowledge-graph substrate declaration.** URML proposes adding a `knowledge_graph_substrate` manifest field; is this a useful abstraction for SkiROS-class deployments, or should the knowledge graph stay SkiROS-internal?
5. **Skill-grounding-mode declaration.** Is `world_model \| runtime_query \| hybrid` the right enumeration, or does the team see other modes worth declaring?
6. **World-model seed path.** Is a static YAML seed the canonical convention, or do deployments commonly use other seed sources?
7. **Adapter home.** URML-side adapter in URML's `reference/skill-bridge/`, contributed example in `SkiROS2/examples/`, or external bridge repo?
8. **Conformance listing.** Would the RobotLabLTH maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
9. **Anything else.**

## Implementation note

RFC-0163 ships as a single RFC document PR (Move-12 batch 3 — robot-command-library cluster). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`RobotLabLTH/SkiROS2` has Issues enabled (Discussions disabled). URML's planned channel: open a single Issue on `RobotLabLTH/SkiROS2`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (license Other — clarification ask, 224 stars, Issues enabled, last commit 2025-06-09 active, isArchived: false).
- [x] License-clarification ask flagged up front.
- [x] Repo-location correction (Aalborg / RVMI → RobotLabLTH / Lund LTH) cited explicitly.
- [x] Knowledge-graph substrate framed as novel URML manifest concern.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (license gate, three Spec-RFCs prerequisite, knowledge-graph generality risk, research-cadence velocity).
- [x] Sibling RFC cross-links explicit (RFC-0160 BehaviorTree.CPP, RFC-0161 py_trees, RFC-0108 ROSA academic-engagement parallel).
- [x] No spec change proposed in this RFC.
