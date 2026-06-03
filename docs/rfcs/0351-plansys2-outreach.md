---
rfc: 0351
title: PlanSys2 (PDDL task and temporal planning for ROS 2) integration, request for comment from the PlanSys2 maintainers
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

# RFC-0351: PlanSys2 integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's planning system, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`PlanSys2/ros2_planning_system`](https://github.com/PlanSys2/ros2_planning_system),
the PDDL2.1 task and temporal planning system for ROS 2, and **requests review
and feedback from the PlanSys2 maintainers**.

This is the closest target in the wave to URML's own altitude, and the RFC is
honest about that up front: it is a peer-layer conversation with real overlap,
not URML strictly above. PlanSys2 decomposes a goal into a plan of durative
actions and dispatches them. That is close to URML's Layer-3 behavior composition
([`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md)) and
Layer-4 natural-language intent layer.

The alignment runs at two seams. A PlanSys2 PDDL action could correspond to a
URML primitive, a validated, capability-checked unit (`move_to`, `dock`, `grasp`,
`scan`, `call_program`). A PlanSys2 plan could be expressed as, or lowered to, a
URML behavior (a Layer-3 `sequence` and its kin). The contribution URML offers is
**static capability and safety validation of each action a task planner emits,
before any action is dispatched**: a planned action outside the declared
capability, or one the safety envelope forbids, is rejected before it reaches the
executor.

URML composes alongside and below PlanSys2 at this seam, not above it: a PlanSys2
plan -> per-action URML primitives -> static capability and envelope validation
-> behavior-tree execution ([RFC-0160](0160-behaviortree-cpp-outreach.md),
[RFC-0161](0161-py-trees-outreach.md)) that PlanSys2 already dispatches into ->
`ros2_control` ([RFC-0319](0319-ros2-control-outreach.md)) executes.

## Motivation

PlanSys2 and URML overlap more than any other Move #26 target, so the honest
question is where the layers divide, not whether URML sits above:

1. **A PDDL action and a URML primitive describe the same kind of unit.** A
   PlanSys2 durative action is a named, parameterized, precondition-guarded step.
   A URML Layer-2 primitive
   ([`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md))
   is a named, typed, capability-checked step. The correspondence is direct enough
   that a PDDL action could map onto a URML primitive, with URML adding the static
   capability and envelope check the PDDL action does not carry.
2. **A plan and a behavior describe the same kind of composition.** PlanSys2
   produces a plan of ordered, timed actions and dispatches it. URML's Layer-3
   composes primitives into behaviors (`sequence` and its kin). A PlanSys2 plan
   could be expressed as or lowered to a URML behavior, so the plan a task planner
   emits gains a validation pass before execution.
3. **URML's contribution is the validation pass, not the planning.** URML does not
   plan. PlanSys2 owns goal decomposition, PDDL solving, and temporal reasoning.
   What URML adds at this seam is the static check, before dispatch, that each
   planned action is admissible against the declared capability manifest and the
   active safety envelope. The planner decides what to do; URML checks that each
   step is allowed before the robot does it.

Repo at [`PlanSys2/ros2_planning_system`](https://github.com/PlanSys2/ros2_planning_system)
(about 483 stars, Issues **and** Discussions enabled, not archived, last push
2026-05-30, active). License is asked as a question below (the GitHub API did not
surface an SPDX id at verification time; understood to be Apache-2.0, a clean fit
with URML's own license). Origin: Intelligent Robotics Lab, Rey Juan Carlos
University, Madrid (Spain, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 mapping (conceptual; planned `plansys2_action_cell.yaml` fixture)

The mapping is at the action-and-plan altitude, the highest-fit altitude in the
wave. URML does not solve PDDL; it validates each action a PlanSys2 plan emits.

| URML field | Relation to PlanSys2 |
|---|---|
| Layer-2 primitive (`move_to`, `dock`, `grasp`, `scan`, `call_program`) | A PlanSys2 PDDL durative action; URML adds the static capability and envelope check the action does not carry |
| `programs` / `call_program` | A composite PlanSys2 action or sub-plan invoked as a single named unit at URML's altitude |
| `frames`, `declared_locations` | The PDDL objects and the named poses an action's parameters resolve against, frame-resolved via RFC-0290 |
| Layer-3 behavior (`sequence` and kin) | A PlanSys2 plan of ordered, timed actions, expressed as or lowered to a URML behavior |
| `mobility` / `manipulation` capability | The capability surface each planned action is statically checked against before dispatch |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins per planned action; URML applies the envelope before the action reaches the executor |

### What URML v0.1 does not yet express for PlanSys2

These are **gaps surfaced by the mapping**, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Temporal and durative-action surface.** URML's Layer-3 composes behaviors but
   does not carry the durative timing, action overlap, and temporal constraints a
   PDDL2.1 plan expresses. A future Spec RFC could add an optional temporal surface
   so a PlanSys2 plan lowers to a URML behavior without losing its timing.
2. **Plan-provenance marker.** A behavior lowered from a task planner is not the
   same trust artifact as one a developer authored directly. A future Spec RFC
   could add an optional marker recording that a behavior was lowered from an
   external planner, so a downstream consumer can tell a planner-emitted plan from
   a hand-authored one.

### Compatibility notes

- **Vendor org.** [`PlanSys2`](https://github.com/PlanSys2) (Intelligent Robotics
  Lab, Rey Juan Carlos University, Madrid).
- **Engagement repo.**
  [`PlanSys2/ros2_planning_system`](https://github.com/PlanSys2/ros2_planning_system),
  the PDDL2.1 task and temporal planning system for ROS 2.
- **Origin / policy.** Spain (Rey Juan Carlos University, NATO-allied). Passes
  US-federal default policy (open-source academic planning system, no provenance
  gate at the planning layer).
- **License fit.** Understood to be Apache-2.0, a clean fit with URML's own
  Apache-2.0; not SPDX-detected at verification time, so asked below as a
  question.
- **Layer overlap.** Unlike the rest of the wave, PlanSys2 sits at URML's own
  altitude. URML does not claim to be above it; the engagement is a peer-layer
  conversation about where task planning, intent validation, and behavior
  execution divide.
- **Substrate-neutrality.** PlanSys2 dispatches into behavior-tree executors
  (RFC-0160, RFC-0161); the URML primitive a planned action maps onto is the same
  unit that runs on a zero-ROS runtime, so the action-level validation holds
  independent of the executor.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The temporal and durative-action surface
  and the plan-provenance marker are queued Spec RFCs.
- Reference runtime: no change in this RFC. A PlanSys2 mapping would validate each
  planned action as a URML primitive before dispatch; the planned
  `plansys2_action_cell.yaml` fixture would document the PDDL-action-to-primitive
  correspondence and the per-action capability check.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Peer-layer overlap.** PlanSys2 and URML overlap at the action and plan
  altitude, so the relationship is not the clean "URML above the substrate" of the
  rest of the wave. The engagement is honest that the layers genuinely overlap and
  that the boundary is the open question, not a settled given.
- **Temporal gap.** URML's Layer-3 does not yet carry the durative timing a PDDL2.1
  plan expresses, which is exactly the temporal surface gap queued above. Lowering
  a full temporal plan to a URML behavior today would lose its timing, so the
  mapping is honest about what does not survive the lowering yet.

## Alternatives considered

1. **Treat PlanSys2 as a substrate URML sits above.** Rejected. It would
   misrepresent the altitude. PlanSys2 plans and dispatches actions, which is
   URML's Layer-3 and Layer-4 territory. The honest framing is a peer-layer
   conversation about division of labor, with URML offering per-action validation,
   not a claim of being above.
2. **Have URML emit PDDL directly.** Rejected. Authoring the domain, solving the
   PDDL problem, and reasoning about temporal constraints are PlanSys2's core
   competence, below and beside URML's intent layer rather than something URML
   should replace. URML validates the actions a plan emits; it does not solve the
   plan.
3. **Model the PDDL domain and problem in the URML manifest.** Rejected. The PDDL
   domain, its predicates, and the solver are PlanSys2's surface. URML declares
   capability over the robot and validates each action against it; modelling the
   full PDDL domain would duplicate PlanSys2 and fail the substrate-neutrality acid
   test.

## Prior art

- [RFC-0160 (BehaviorTree.CPP outreach)](0160-behaviortree-cpp-outreach.md): the
  behavior-execution sibling PlanSys2 dispatches into; the closest precedent for
  the execution layer below this seam.
- [RFC-0161 (py-trees outreach)](0161-py-trees-outreach.md): the other
  behavior-execution sibling PlanSys2 dispatches into.
- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor; the
  goal-and-constraint declaration contract this RFC sits above.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that runs the result a dispatched action produces.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  resolution a planned action's parameters depend on.
- [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the behavior-composition and primitive surfaces this engagement overlaps.

## Unresolved questions

For the PlanSys2 maintainers:

1. **Action-to-primitive correspondence.** Is a PlanSys2 PDDL durative action
   to URML primitive correspondence sound and useful, with URML adding a static
   capability and envelope check each action does not carry today?
2. **Plan as a lowered behavior.** Could URML serve as a validation and lowering
   layer for PlanSys2 plans, expressing a plan as a URML behavior so each action is
   validated before dispatch, or does the temporal structure of a PDDL2.1 plan
   resist that lowering?
3. **Where the layers divide.** Given the overlap, where is the right division:
   task planning (PlanSys2), intent validation (URML), and behavior execution
   (BehaviorTree.CPP, py-trees)? Is per-action validation the right contribution
   for URML to offer, or does it belong elsewhere?
4. **Temporal surface.** PlanSys2 plans are temporal and durative. URML's Layer-3
   does not yet carry that timing (the gap queued above). Is the durative-timing
   surface something a lowering layer must carry, or can a first engagement stay at
   the untimed-sequence altitude?
5. **License.** What is the current license of `ros2_planning_system` (the GitHub
   API did not surface an SPDX id at verification time; understood to be
   Apache-2.0)?
6. **Conformance listing.** Would PlanSys2 consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0351 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`PlanSys2/ros2_planning_system`](https://github.com/PlanSys2/ros2_planning_system)
pointing at this RFC (the repo has both enabled). If the maintainers prefer
another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 483 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-30).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, peer-layer overlap, temporal gap).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; gaps (temporal and durative-action surface,
      plan-provenance marker) flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: Spain (Rey Juan Carlos University, NATO-allied); default policy
      passes at the planning layer.
- [x] CLAUDE.md compliance check passed (honest peer-layer framing, not a claim of
      being above; URML offers per-action validation, the layer division is the
      open question, composed alongside not assumed).
