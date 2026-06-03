---
rfc: 0360
title: robomimic (imitation-learning manipulation framework) integration, request for comment from the robomimic maintainers
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

# RFC-0360: robomimic integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`ARISE-Initiative/robomimic`](https://github.com/ARISE-Initiative/robomimic), a
framework for learning manipulation policies from demonstrations. It **requests
review and feedback from the robomimic maintainers**.

URML's manipulation primitives (`move_to` to a pose, `grasp`, `release`) declare
**intent** plus a target and the arm's capability: the gripper kind and force
bounds, and `manipulation.reachable_workspace_m`. A robomimic policy learned from
demonstrations is a **manipulation controller URML can dispatch to**: it consumes
the current observation and emits an action that drives the arm and gripper. URML
does not learn the policy. It declares the target and the capability, statically
validates that the request is admissible (the target lies within the declared
reachable workspace, the grasp is within the gripper force range and accepted
classes, and the active safety envelope holds) **before** the policy is invoked,
then consumes the actions the policy produces and bounds what it is allowed to
attempt.

The stack is: URML intent -> validated target plus capability -> a robomimic
policy realizes the manipulation -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes. The differentiator is
**static admissibility and envelope checking before the policy acts**, and a
declared capability that **bounds the action space a learned policy may explore**.
This is newer ground than an analytic solver: a learned controller is statistical,
not closed-form, so the value of a hard pre-action admissibility bound around it
is exactly the question this RFC puts to the maintainers.

## Motivation

robomimic is a widely used imitation-learning framework for manipulation, and a
learned policy is a sharp test of URML's "declare the capability, bound what the
substrate may attempt" line:

1. **A learned policy is a manipulation substrate URML can dispatch to.** Like an
   IK solver or a planner, a trained robomimic policy turns intent into motion.
   URML treats it as one more manipulation substrate: the language declares the
   admissible target and capability, the policy realizes it. This mirrors the
   learned-controller-as-substrate framing URML used for Brax in Move #24.
2. **The declared capability can bound a policy's action space.** A learned policy
   emits actions sampled from a distribution. URML's declared
   `reachable_workspace_m`, gripper `force_max_n`, and `accepted_classes` give a
   static, inspectable boundary the policy's commanded action can be checked
   against before it reaches the actuator. The language is the guardrail around
   the learned controller, not a competitor to it.
3. **Admissibility is cheap and early at this seam.** Before a policy rollout
   begins, URML can statically reject a target outside the declared workspace or a
   grasp outside the gripper's force range. A rollout that cannot be admitted
   within the declared capability never starts.
4. **It grounds substrate-neutrality.** The same `move_to` and `grasp` intent maps
   onto an analytic solver ([RFC-0352](0352-trac-ik-outreach.md),
   [RFC-0353](0353-pink-outreach.md)), a planning query, or a learned robomimic
   policy. The learned controller is one manipulation substrate among several; the
   URML intent is unchanged across them.

Repo at [`ARISE-Initiative/robomimic`](https://github.com/ARISE-Initiative/robomimic)
(about 1,437 stars, Issues enabled, not archived, active, last push 2026-02-05).
Built on robosuite (recorded in Move #24 as a Tier B simulation row). Origin: the
ARISE Initiative (Stanford and UT Austin lineage, United States); passes
US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `robomimic_arm_cell.yaml` fixture)

| URML field | Maps to robomimic attribute |
|---|---|
| `robot_id`, `description` | The manipulator identity (carried at the manifest envelope; not a policy concept) |
| `frames` | The frames the observation and the action target are expressed in; the `move_to` pose is resolved here before a rollout |
| `declared_locations` | Named target poses a `move_to` resolves against before the target is handed to the policy |
| `manipulation.arm_count` | The number of arms the policy controls; one policy action group per arm |
| `manipulation.reachable_workspace_m` | The declared reachable volume; the static admissibility bound and the box the policy's commanded pose is clamped or rejected against |
| `manipulation.grippers[].kind` / `force_min_n` / `force_max_n` | The gripper capability a `grasp` / `release` consumes; force bound checked statically against the policy's gripper action, not learned |
| `manipulation.grippers[].accepted_classes` | The object classes a `grasp` may target; validated against the perception manifest before a grasp rollout |
| Safety envelope limits (Pass 3) | Conjoined with the declared capability; URML applies strictest-wins as the bound on the policy's admissible action before the rollout |

### What URML v0.1 does not yet express for robomimic

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Learned-policy-as-substrate declaration.** URML has no first-class way to
   declare that a manipulation substrate is a learned policy (its observation
   contract, action space, and the demonstration provenance it was trained on),
   distinct from an analytic solver. A future Spec RFC could add a learned-policy
   substrate declaration so the manifest can record what kind of controller is
   below the boundary and what action space the admissibility check bounds.
2. **IK-target and joint-configuration declaration.** URML declares a target pose
   and reachable workspace, but has no first-class IK-target or returned
   joint-configuration artifact. A future Spec RFC could add one so a learned or
   analytic substrate is queried from a well-posed manifest contract.
3. **Explicit joint-limit declaration.** URML defers joint limits to the safety
   envelope today. A future Spec RFC could let the manifest declare per-joint
   limits explicitly so the action-space bound on a learned policy and the
   envelope agree without round-tripping.

### Compatibility notes

- **Vendor org.** [`ARISE-Initiative`](https://github.com/ARISE-Initiative) (the
  ARISE Initiative, a Stanford and UT Austin lineage robotics-learning group).
- **Engagement repo.** [`ARISE-Initiative/robomimic`](https://github.com/ARISE-Initiative/robomimic):
  a framework for learning manipulation from demonstrations, built on robosuite;
  active.
- **Origin / policy.** United States (ARISE Initiative). Passes US-federal default
  policy (open-source learning framework, no provenance gate at the policy layer).
- **License note.** Open-source; URML's relationship is cross-citation and runtime
  composition, not code vendoring.
- **Substrate-neutrality.** A robomimic policy is one manipulation substrate among
  several; the same URML `move_to` and `grasp` intent maps onto TRAC-IK
  ([RFC-0352](0352-trac-ik-outreach.md)), Pink ([RFC-0353](0353-pink-outreach.md)),
  or an analytic planner with no change to the URML program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The learned-policy-as-substrate
  declaration, the IK-target / joint-configuration declaration, and explicit
  joint-limit declaration are queued Spec RFCs.
- Reference runtime: no change in this RFC. A robomimic mapping would route a
  validated target plus capability to a trained policy, bound the policy's
  commanded action against the declared workspace and gripper limits, and hand the
  admissible action to `ros2_control`; the planned `robomimic_arm_cell.yaml`
  fixture would document the admissibility check and the boundary hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Learned-controller-as-substrate is newer ground.** A learned policy is
  statistical, not closed-form. URML's static admissibility bound is honest about
  what it can promise: it bounds the action that reaches the actuator, it does not
  make a learned policy correct or safe inside that bound. The contribution is a
  hard outer guardrail, not a guarantee about the policy's interior behavior.
- **robosuite coupling.** robomimic builds on robosuite for its simulation and
  benchmark surface. That coupling is below URML's boundary, but a deployment that
  adopts a robomimic policy in simulation inherits the robosuite dependency.

## Alternatives considered

1. **Have URML learn or shape the policy itself.** Rejected. Learning from
   demonstrations is a substrate concern and a deep, well-served field. URML
   declares intent, capability, and admissibility and consumes a policy's actions;
   reimplementing the learning loop would couple the language to one framework and
   fail the substrate-neutrality acid test.
2. **Skip the static admissibility bound and trust the learned policy.** Rejected.
   The whole value URML adds at this seam is a hard, inspectable bound on what a
   learned controller may attempt before its action reaches the actuator. Trusting
   the policy unbounded discards URML's contribution and its safety posture.
3. **Engage robosuite (the simulator) instead of robomimic (the policy layer).**
   Rejected for this RFC. robosuite is the simulation and benchmark substrate
   (a Move #24 simulation concern); robomimic is the learned-controller layer
   where a policy becomes a manipulation substrate URML can dispatch to. The policy
   seam is the home for the learned-controller-as-substrate question.

## Prior art

- [RFC-0352 (TRAC-IK outreach)](0352-trac-ik-outreach.md): the Move #27 wave
  anchor; the analytic-solver-as-substrate contrast to a learned policy.
- [RFC-0353 (Pink outreach)](0353-pink-outreach.md): the differential-IK sibling;
  another analytic manipulation substrate URML declares intent over.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the planning-framework
  engagement above the controller layer.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the execution
  layer that consumes the admissible action a policy produces.
- [RFC-0345 (Pinocchio outreach)](0345-pinocchio-outreach.md): the rigid-body
  dynamics and kinematics library underneath the analytic solvers in this wave.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): the physics
  substrate that simulation-trained policies and benchmarks run against.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the URML manipulation surface this engagement exercises.
- Sibling Move #27 RFCs: RFC-0352 (TRAC-IK), RFC-0353 (Pink), RFC-0359 (RLBench).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  primitive and capability surfaces this engagement exercises.

## Unresolved questions

For the robomimic maintainers:

1. **Intent-to-policy boundary.** What is the cleanest seam for "URML intent plus
   declared capability -> a robomimic policy rollout"? Should URML produce the
   target pose and gripper command in the policy's observation frame and let the
   policy act, or is there an intermediate contract you would prefer?
2. **Bounding the action space.** Can URML's declared `reachable_workspace_m`,
   gripper `force_max_n`, and `accepted_classes` usefully bound a policy's
   commanded action before it reaches the actuator? Is clamping, rejecting, or
   masking the right treatment when a learned action falls outside the declared
   capability?
3. **Behavior description on a demonstration.** Could a demonstration's task carry
   a URML behavior description (the intent the demonstration realizes), so a
   learned policy and the URML program that dispatches to it share a vocabulary for
   what the task is?
4. **Sim-trained versus real deployment.** A policy trained in robosuite and one
   deployed on hardware are different trust artifacts. Should URML's admissibility
   bound differ between a simulated rollout and a real one, and how would you want
   that distinction surfaced?
5. **Conformance listing.** Would the robomimic project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0360 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`ARISE-Initiative/robomimic`](https://github.com/ARISE-Initiative/robomimic)
pointing at this RFC (Issues are enabled on the repo). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 1,437 stars, not archived, Issues
      enabled, active, last push 2026-02-05; built on robosuite).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, learned-controller newer ground, robosuite
      coupling).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (ARISE Initiative); default policy passes at the policy layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; a robomimic policy is
      one manipulation substrate among several, URML declares the capability and
      bounds the action space and does not learn the policy).
