---
rfc: 0476
title: ROSPlan integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0476: ROSPlan integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition and capability manifest. Tier B.

## Summary

[`KCL-Planning/ROSPlan`](https://github.com/KCL-Planning/ROSPlan) (BSD-2-Clause, ~392 stars, maintained) is the long-running generic PDDL task-planning framework for ROS, from King's College London. Where URML's Layer-3 is *authored* control flow, a PDDL planner *synthesizes* it: given a goal and a domain, ROSPlan produces an action sequence. The two compose — a planner can emit a plan that URML validates and dispatches, or URML's primitives can be the PDDL durative-actions the planner sequences. This RFC asks how they should interop. (Distinct from the PlanSys2 engagement in the motion-planning wave; this is the KCL/PDDL lineage.)

## The mapping (URML and ROSPlan)

URML and a PDDL planner sit on either side of the plan:

- **ROSPlan plans, URML validates + dispatches.** ROSPlan synthesizes an action sequence from a goal; each action lowers to a URML primitive that is capability- and envelope-checked before dispatch, so the synthesized plan cannot ask for what the robot cannot honestly do.
- **URML primitives as PDDL actions.** A URML primitive's typed signature + capability precondition maps onto a PDDL durative-action with parameters and preconditions, so the planner reasons over the same capability surface URML validates against.

The acid test holds: ROSPlan decides *what sequence*; URML checks each step is typed, capable, and in-envelope before it runs.

## What is asked

Request for comment from the ROSPlan maintainers:

1. Is "ROSPlan plans → URML validates + dispatches each action" a sensible division, and where would the plan-to-primitive lowering live?
2. Could a URML primitive's capability/envelope precondition be expressed as a PDDL action precondition, so planning and validation share a surface?
3. Is a validated-dispatch action interface interesting for ROSPlan's plan-execution (dispatch) layer?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002), capability manifest, and safety envelope; the behavior-tree anchor (RFC-0470); the PlanSys2 task-planner engagement (Move #26, a distinct PDDL lineage). ROSPlan is the PDDL-task-planner vertex of the orchestration wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `KCL-Planning/ROSPlan` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD-2-Clause). Tracked in `examples/lighthouses/outreach-move41.yaml`.
