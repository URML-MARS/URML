---
rfc: 0359
title: RLBench (robot manipulation benchmark) integration, request for comment from the RLBench maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-03
updated: 2026-06-03
state: Draft
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

# RFC-0359: RLBench integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`stepjam/RLBench`](https://github.com/stepjam/RLBench), a large-scale robot
manipulation benchmark of roughly 100 tasks built on CoppeliaSim and PyRep. It
**requests review and feedback from the RLBench maintainers**.

RLBench defines manipulation tasks (open the drawer, stack the blocks) with
explicit success conditions. That is close to what a URML behavior describes at
the intent level: a sequence of typed primitives (`detect`, `move_to`, `grasp`,
`release`) over a target, validated against a capability manifest and a safety
envelope before anything runs. The proposed alignment is conceptual: an RLBench
task could be expressed as a URML behavior over validated primitives, and URML
would add a capability-and-safety-validated description of each task's actions.

URML composes **above** the benchmark: URML behavior -> validated primitives over
a declared manipulation capability -> an RLBench task on CoppeliaSim / PyRep ->
the benchmark's own success check. The differentiator is static admissibility
(force range, accepted classes, reachability) checked before the task action.
This RFC is honest about scope: this is a conceptual and benchmark-mapping
conversation, not a runtime adapter.

## Motivation

RLBench is a widely used manipulation benchmark, and its task layer sits at the
same altitude as a URML behavior, which makes the mapping worth examining:

1. **A benchmark task is close to a URML behavior.** An RLBench task names an
   action over objects with a success condition. A URML behavior names a sequence
   of typed primitives over a target. The two describe the same thing from two
   sides: RLBench from the success-condition side, URML from the
   validated-intent side. A task like "stack the blocks" reads naturally as
   `detect` then `grasp` then `move_to` then `release`, repeated.
2. **URML adds static admissibility to a task description.** Before a task runs,
   URML checks the declared manipulation capability (`grippers` force range,
   `accepted_classes`, `reachable_workspace_m`) and the safety envelope against
   each primitive in the behavior. A capability-checked task description is
   something a benchmark of grasping tasks does not have today.
3. **It exercises the manipulation manifest against real tasks.** RLBench's
   object set and task structure give `perception.object_vocabulary` and
   `manipulation.grippers` something concrete to bind against, rather than a toy
   manifest. The acid test holds: the same primitives drive real hardware or a
   zero-ROS runtime, so an RLBench task is one more intent-level mapping.

Repo at [`stepjam/RLBench`](https://github.com/stepjam/RLBench) (about 1,777
stars, Issues enabled, not archived, last push 2025-01-25, over a year since the
last push, still a widely used benchmark). Origin: Stephen James and the Dyson
Robotics Lab at Imperial College London (United Kingdom, NATO-allied); passes
US-federal default policy.

## Detailed design

### URML v0.1 behavior-to-task mapping (planned `rlbench_task_cell.yaml` fixture)

| URML field | Maps to RLBench attribute |
|---|---|
| `robot_id`, `description` | The benchmark arm's identity in the manifest envelope (the task's robot) |
| `frames`, `declared_locations` | The task scene's frame and named target poses a `move_to` resolves against |
| `manipulation.arm_count` + `reachable_workspace_m` | The benchmark arm and its workspace, checked statically before a `move_to` |
| `manipulation.grippers[].kind` / `force_min_n` / `force_max_n` | The task gripper and its force bound, checked before a `grasp` |
| `manipulation.grippers[].accepted_classes` | The object classes a task grasp admits, conjoined with the task's object set |
| `perception.object_vocabulary` | The task's object / semantic categories a `detect` may name |
| A URML behavior (sequence of `detect` / `move_to` / `grasp` / `release`) | One RLBench task's action sequence; the success condition stays the benchmark's |
| Safety envelope limits (Pass 3) | Conjoined with the task scene bounds; URML applies strictest-wins before the action |

### What URML v0.1 does not yet express for RLBench

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **A benchmark-task to primitive mapping.** URML has no declared format for a
   capability-checked task description (a named task, its action sequence, its
   success condition) that a benchmark could consume. A future Spec RFC could add
   an optional task-description format so a behavior can carry a benchmark task's
   identity and success criterion alongside the validated primitives.
2. **Named grasp-type primitives.** RLBench tasks imply different grasp classes
   (a power grasp on a handle, a pinch on a peg). URML expresses `grasp object`,
   not the grasp class. A future Spec RFC could add named grasp types so a task's
   intent can name the grasp it needs.

### Compatibility notes

- **Maintainer / org.** [`stepjam`](https://github.com/stepjam) (Stephen James,
  Dyson Robotics Lab, Imperial College London).
- **Engagement repo.** [`stepjam/RLBench`](https://github.com/stepjam/RLBench),
  the manipulation benchmark.
- **Origin / policy.** United Kingdom (NATO-allied). Passes US-federal default
  policy (allied-origin open benchmark, no provenance gate at the benchmark
  layer).
- **Relationship.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring. URML cites RLBench tasks as a benchmark surface a
  validated behavior could describe and does not bundle its code or scenes.
- **Substrate-neutrality.** RLBench runs on CoppeliaSim / PyRep; the same URML
  behavior and primitives map onto real hardware, MuJoCo
  ([RFC-0060](0060-mujoco-integration.md)), or a zero-ROS runtime with no change
  to the program. The CoppeliaSim / PyRep dependency is below the intent layer.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The benchmark-task to primitive mapping
  format and named grasp-type primitives are queued Spec RFCs.
- Reference runtime: no change in this RFC. An RLBench mapping would express a
  task as a URML behavior over validated primitives; the planned
  `rlbench_task_cell.yaml` fixture would document one task's manipulation
  manifest and behavior, leaving the success check and the simulation to RLBench.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Conceptual fit, not an adapter.** This is a benchmark-mapping conversation
  about whether a task and a behavior align, not a runtime adapter. URML benefits
  from the framing more than RLBench needs the mapping, and the RFC is honest
  about that.
- **Quiet repo.** The last push was 2025-01-25, over a year ago. The benchmark is
  still widely used, but maintainer attention may be limited; a slow or absent
  reply is a likely outcome.

## Alternatives considered

1. **Build a runtime adapter into RLBench instead of a conceptual mapping.**
   Rejected for a first engagement. The honest fit is at the task-and-behavior
   level; an adapter presumes a boundary the maintainers have not agreed to. The
   conceptual mapping is the right first step, and an adapter can follow if the
   correspondence holds.
2. **Map a URML behavior to RLBench task code directly.** Rejected. URML
   describes intent and capability, not task implementation. Task code, success
   checks, and the CoppeliaSim / PyRep scene are the benchmark's concern; pulling
   them into URML would fail the substrate-neutrality acid test.
3. **Skip RLBench because the repo is quiet.** Rejected. A widely used benchmark
   whose task layer matches URML's behavior altitude is worth a request for
   comment even with limited maintainer activity; the staleness is acknowledged,
   not a reason to pass.

## Prior art

- [RFC-0360 (robomimic outreach)](0360-robomimic-outreach.md): the sibling
  manipulation-benchmark and imitation-learning engagement in this wave.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the motion-planning
  engagement a task's `move_to` composes with.
- [RFC-0010 (whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the spec lineage for richer manipulation behaviors.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): a sibling
  simulator the same behavior maps onto, evidence the mapping is not
  RLBench-shaped.
- Sibling Move #27 RFCs: [RFC-0352 (TRAC-IK)](0352-trac-ik-outreach.md) (the
  manipulation-wave anchor), [RFC-0357 (LEAP Hand)](0357-leap-hand-outreach.md),
  and [RFC-0360 (robomimic)](0360-robomimic-outreach.md).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the RLBench maintainers:

1. **Task to behavior correspondence.** Is an RLBench task to a URML behavior (a
   sequence of validated primitives such as `detect`, `move_to`, `grasp`,
   `release`) a sound correspondence, or do task structure and success conditions
   resist that framing in ways URML is missing?
2. **Capability-checked task description.** Would a capability-checked task
   description format (a task's actions plus the manipulation capability they
   require, statically validated before a run) be useful to a benchmark of
   grasping tasks, or is that orthogonal to RLBench's purpose?
3. **CoppeliaSim / PyRep boundary.** Is "URML stays at the task and behavior
   level, CoppeliaSim and PyRep stay below it" the right boundary, with URML
   making no assumptions about the simulation backend?
4. **Task object sets.** RLBench tasks carry object sets and success conditions.
   Is matching `perception.object_vocabulary` and `manipulation.grippers`
   `accepted_classes` against a task's object set the right alignment?
5. **Conformance listing.** Would RLBench consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0359 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`stepjam/RLBench`](https://github.com/stepjam/RLBench) pointing at this RFC (the
repo has Issues enabled). If the maintainers prefer another channel, URML will
move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,777 stars, not archived, Issues
      enabled, last push 2025-01-25, staleness acknowledged).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, conceptual fit not an adapter, quiet repo).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (benchmark-task mapping format,
      named grasp types) flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: United Kingdom (NATO-allied); default policy passes at the
      benchmark layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; RLBench runs on
      CoppeliaSim / PyRep, the same behavior maps onto other backends and a
      zero-ROS runtime, composed-above not assumed).
