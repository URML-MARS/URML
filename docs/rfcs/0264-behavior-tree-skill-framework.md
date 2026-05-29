---
rfc: 0264
title: behavior_tree_runtime / skill_framework / knowledge_graph_substrate — declaring Layer-3 composition substrates
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

# RFC-0264: `behavior_tree_runtime` / `skill_framework` / `knowledge_graph_substrate`

## Summary

URML's Layer-3 behavior composition compiles to substrate-side composition engines: BehaviorTree.CPP, py_trees, MoveIt Task Constructor, SkiROS2. URML's manifest has no place today to declare which Layer-3 composition substrate the deployment composes against, nor the adjacent knowledge-graph substrate that skill frameworks rely on, nor the skill-grounding mode. This RFC adds three sibling fields under a new top-level `composition` block, with closed enums and `composition_options`. Optional. Backward compatible.

The surfaces that demanded this RFC are Move-12 RFCs 0160 (BehaviorTree.CPP), 0161 (py_trees), 0162 (MoveIt Task Constructor), and 0163 (SkiROS2).

## Motivation

URML's Layer-3 composes URML's Layer-2 primitives into sequences, branches, and recoveries. Production deployments dispatch Layer-3 composition through substrate-side engines: BehaviorTree.CPP for C++ ROS 2 deployments, py_trees for Python ROS 2 deployments, MoveIt Task Constructor for industrial-manipulation pipelines, SkiROS2 for skill-based knowledge-augmented composition.

Three concrete consequences of the gap:

1. **Layer-3 dispatch is undeclared.** URML's `reference/ros2-runtime/` cannot tell whether a Layer-3 sequence compiles to a BehaviorTree.CPP XML tree or a py_trees Python module without manifest declaration.
2. **Knowledge-graph substrate is novel.** SkiROS2 introduces a knowledge-graph substrate as a Layer-3 dependency. URML's manifest has no place to declare it; the manifest extends to make the dependency explicit.
3. **Skill-grounding mode is operationally critical.** SkiROS2 distinguishes pre-grounded skills (URML primitive ↔ specific implementation at validate time) from dynamically-grounded skills (resolved at runtime via knowledge graph). URML's validator needs to know which mode to apply.

## Detailed design

### Field shape

```yaml
composition:                                # NEW — this RFC, top-level optional
  behavior_tree_runtime: behaviortree_cpp   # behaviortree_cpp | py_trees | none | custom
  skill_framework: skiros2                  # skiros2 | moveit_task_constructor | none | custom
  knowledge_graph_substrate: rdf            # rdf | neo4j | in_memory | none | custom
  skill_grounding_mode: pre_grounded        # pre_grounded | runtime_grounded | hybrid
  composition_options:
    behavior_tree:
      language: cpp                          # cpp | python (matches runtime)
      tree_format: xml                       # xml | yaml
      tree_path: /etc/urml/trees/mission.xml
    skill_framework:
      skill_library_path: /etc/urml/skills/
      knowledge_graph_uri: file:///etc/urml/kg.ttl
```

### Allowed values

**Behavior-tree runtime:**

| Value | Description | Reference |
|---|---|---|
| `behaviortree_cpp` | BehaviorTree.CPP (canonical C++ engine) | Move-12 RFC-0160 |
| `py_trees` | py_trees (Python engine for ROS 2) | Move-12 RFC-0161 |
| `none` | Deployment doesn't use a behavior-tree engine; URML Layer-3 composes directly | n/a |
| `custom` | Vendor-specific | escape hatch + `behavior_tree_runtime_note` required |

**Skill framework:**

| Value | Description | Reference |
|---|---|---|
| `skiros2` | SkiROS2 (knowledge + skills framework for ROS 2) | Move-12 RFC-0163 |
| `moveit_task_constructor` | MoveIt Task Constructor (industrial-manipulation hierarchical task planning) | Move-12 RFC-0162 |
| `none` | No skill framework; primitives dispatch directly to Layer-1 HAL | n/a |
| `custom` | escape hatch |

**Knowledge-graph substrate:**

| Value | Description |
|---|---|
| `rdf` | RDF / Turtle / SPARQL knowledge graph (SkiROS2's default) |
| `neo4j` | Neo4j graph database |
| `in_memory` | In-process knowledge representation (no external graph store) |
| `none` | No knowledge graph in the deployment |
| `custom` | escape hatch |

**Skill grounding mode:**

| Value | Description |
|---|---|
| `pre_grounded` | URML primitive ↔ implementation bound at validate time; manifest declares the mapping |
| `runtime_grounded` | Skill ↔ implementation resolved at runtime via knowledge graph; URML's validator cannot fully ground at validate time |
| `hybrid` | Some primitives pre-grounded; others runtime-grounded |

### Schema fragment (Layer-1)

```jsonc
{
  "composition": {
    "type": "object",
    "properties": {
      "behavior_tree_runtime": {
        "enum": ["behaviortree_cpp", "py_trees", "none", "custom"]
      },
      "behavior_tree_runtime_note": { "type": "string" },
      "skill_framework": {
        "enum": ["skiros2", "moveit_task_constructor", "none", "custom"]
      },
      "skill_framework_note": { "type": "string" },
      "knowledge_graph_substrate": {
        "enum": ["rdf", "neo4j", "in_memory", "none", "custom"]
      },
      "skill_grounding_mode": {
        "enum": ["pre_grounded", "runtime_grounded", "hybrid"]
      },
      "composition_options": { "type": "object" }
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing block acceptable. Deployments running pure direct-Layer-2-dispatch don't need the block.
2. **`skill_framework: skiros2` requires `knowledge_graph_substrate`.** SkiROS2 depends on a knowledge graph; missing field is a validator error.
3. **`skill_grounding_mode: runtime_grounded`** triggers a soft warning. The validator notes that URML's static validation is partial in this mode (cannot fully ground primitives at validate time; some checks deferred to runtime).
4. **Language consistency.** `behavior_tree_runtime: behaviortree_cpp + composition_options.behavior_tree.language: python` is inconsistent and fails (BehaviorTree.CPP is C++; py_trees is Python).
5. **MoveIt Task Constructor pairing.** `skill_framework: moveit_task_constructor` is typically paired with `substrate.class: ros2` and `manipulation.dispatch: moveit2` (RFC-0202 outreach surface). Inconsistency emits a warning.
6. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read the composition block to select Layer-3 dispatch. The runtime's behavior-tree adapter (BehaviorTree.CPP or py_trees) consumes URML's Layer-3 sequence and emits the substrate-side tree. The skill framework (SkiROS2 or MTC) consumes URML's primitives and dispatches via the framework's task model.

### Conformance test additions

`conformance/tests/test_manifest_composition.py`:

1. Manifest without `composition` block passes.
2. Manifest with `behavior_tree_runtime: behaviortree_cpp + composition_options.behavior_tree.language: cpp` passes.
3. Manifest with `behavior_tree_runtime: behaviortree_cpp + composition_options.behavior_tree.language: python` fails (inconsistent).
4. Manifest with `skill_framework: skiros2` and no `knowledge_graph_substrate` fails.
5. Manifest with `skill_grounding_mode: runtime_grounded` passes with soft warning about partial static validation.

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **Three sibling fields create coupling.** Behavior-tree runtime ↔ language ↔ skill framework ↔ knowledge graph ↔ grounding mode all interact. Documenting the interaction matrix is a maintenance cost.
- **`runtime_grounded` mode weakens URML's static-validation property.** The validator can't fully ground primitives at validate time; some checks defer to runtime. URML accepts the partial validation honestly via the soft warning; the cost is real.
- **Knowledge-graph substrate is novel for URML.** Pre-v0.1 URML treated knowledge representation as out-of-scope; SkiROS2's framework brings it back in scope. The manifest declares it but URML doesn't ship its own knowledge-graph reference implementation; deployment-side adapters are owners.
- **MoveIt Task Constructor cross-reference is in two places.** RFC-0202 (Move-16 MoveIt 2 outreach) cross-references the manipulation dispatcher; this RFC's `skill_framework: moveit_task_constructor` adds a Layer-3 composition perspective. Two valid framings; URML accepts both for orthogonal concerns (dispatch vs composition).

## Alternatives considered

1. **Separate three RFCs (one per field).** Considered. Sibling fields share `composition_options` and validator-rule interactions; bundling reads cleaner.
2. **Skip `skill_grounding_mode`; rely on framework choice alone.** Rejected. The grounding mode is an orthogonal concern (a SkiROS2 deployment can be either pre-grounded or runtime-grounded); the field surfaces the choice.
3. **Treat `knowledge_graph_substrate` as a sibling under `substrate.*`.** Rejected. Knowledge graph is a Layer-3 dependency, not a Layer-0 substrate; placing it under `composition` matches the conceptual layering.
4. **Free-string `behavior_tree_runtime` value.** Rejected. Closed enum with `custom` escape hatch per URML convention.

## Prior art

- [Move-12 RFC-0160 (BehaviorTree.CPP)](0160-behaviortree-cpp-outreach.md), [Move-12 RFC-0161 (py_trees)](0161-py-trees-outreach.md), [Move-12 RFC-0162 (MoveIt Task Constructor)](0162-moveit-task-constructor-outreach.md), [Move-12 RFC-0163 (SkiROS2)](0163-skiros2-outreach.md) — the outreach RFCs that surfaced these fields.
- [Move-16 RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md) — sibling industrial-manipulation engagement; MoveIt Task Constructor is the high-level layer above MoveIt 2.
- URML Layer-3 behavior composition spec (in `spec/layer-3-behavior/`) — the composition layer this RFC declares substrates for.

## Unresolved questions

1. **Multi-framework deployments.** A deployment may use BehaviorTree.CPP for mission-level composition and MoveIt Task Constructor for manipulation sub-tasks. v0.1 of this field is single-framework-per-class.
2. **Per-primitive grounding mode.** `skill_grounding_mode` is deployment-wide; per-primitive grounding modes are future work.
3. **Knowledge-graph schema declaration.** When `knowledge_graph_substrate: rdf`, the deployment uses some specific RDF ontology. URML's manifest could declare the ontology schema (cross-link to IEEE 1872 ontology, RFC-0219 outreach). Future RFC.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks (skiros2-requires-kg, language consistency, MTC pairing, custom-requires-note, runtime-grounded warning).
3. Conformance tests.
4. Update RFC-0202 / RFC-0162 cross-references.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (field coupling, runtime-grounded weakens static validation, knowledge-graph novelty, MTC dual-perspective).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (4 Move-12 + 1 Move-16).
- [x] CLAUDE.md compliance: enum closure preserves moat; substrate-neutrality preserved across behavior-tree-runtime / skill-framework / knowledge-graph dimensions.
