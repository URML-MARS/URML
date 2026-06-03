---
rfc: 0345
title: Pinocchio (rigid-body dynamics) integration, request for comment from the Pinocchio maintainers
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

# RFC-0345: Pinocchio integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
conceptual touch between URML v0.1 and an existing target's backend, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #26 is URML's motion-planning and navigation wave. This RFC reaches
[`stack-of-tasks/pinocchio`](https://github.com/stack-of-tasks/pinocchio), the
fast rigid-body kinematics and dynamics library that whole-body planners and
optimal-control solvers run on, and **requests review and feedback from the
Pinocchio maintainers**.

Pinocchio is a low-level backend, and the RFC is honest about that up front.
URML sits well above it and does not map onto it directly. The honest contact
point is narrow and worth naming: the kinematic and dynamic **model** Pinocchio
computes over is the ground truth that a URML capability declaration should stay
consistent with. URML's `manipulation.reachable_workspace_m` and its future
joint-limit declaration describe, at a coarse altitude, the same robot a
Pinocchio model describes precisely.

URML composes **above** the planners and controllers that use Pinocchio, not
above Pinocchio itself. A URML primitive declares intent plus a goal; a planner
or solver built on Pinocchio computes the trajectory that realizes it under the
robot's kinematics and dynamics; `ros2_control` ([RFC-0319](0319-ros2-control-outreach.md))
executes it. URML never calls Pinocchio. This RFC is an ecosystem touch plus a
consistency-and-boundary clarification, not a control mapping.

## Motivation

Pinocchio is the rigid-body engine under a large share of modern whole-body
planning and MPC stacks, including Crocoddyl (sibling RFC-0346, built directly
on Pinocchio). That makes a boundary clarification with its maintainers
worthwhile even though the direct fit is small:

1. **The model is the ground truth a URML declaration should match.** URML's
   Layer-1 manifest ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
   declares a coarse capability surface: `manipulation.arm_count`,
   `manipulation.reachable_workspace_m`, `manipulation.grippers`. A Pinocchio
   model holds the precise kinematic tree and dynamic parameters those fields
   summarize. Naming the consistency relation between the two is the point of the
   touch.
2. **It is a backend, not an intent layer.** Pinocchio answers forward and
   inverse kinematics, dynamics, and Jacobians, given a model and a
   configuration. URML's contribution is one layer up and unrelated to that math:
   given the resulting trajectory a planner produces, does the declared
   capability and the safety envelope admit the requested intent before the robot
   moves. URML declares the goal and validates admissibility; it does not plan or
   solve.
3. **It clarifies a boundary the wave needs drawn.** Several Move #26 targets are
   planners and solvers that compute over a Pinocchio model. Drawing the line
   once, with the backend's maintainers, keeps the rest of the wave honest: URML
   talks to the planner, not to Pinocchio, and consumes a trajectory, not a
   dynamics computation.

Repo at [`stack-of-tasks/pinocchio`](https://github.com/stack-of-tasks/pinocchio)
(about 3,434 stars, Issues **and** Discussions enabled, not archived, last push
2026-06-01, active). Maintained within the stack-of-tasks ecosystem at INRIA /
LAAS-CNRS. License is asked as a question below (the GitHub API did not surface
an SPDX id at verification time; understood to be BSD-2-Clause). Origin: France
(INRIA / LAAS-CNRS, NATO-allied); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (conceptual; no in-repo fixture planned)

The mapping is deliberately thin. Pinocchio is a kinematics / dynamics backend,
so the alignment is at the level of "the URML declaration should stay consistent
with the model Pinocchio computes over," not a field-by-field control mapping.

| URML field | Relation to Pinocchio |
|---|---|
| `manipulation.arm_count` + joints | Summarizes the kinematic tree a Pinocchio model holds precisely; URML declares the count and structure at a coarse altitude, never reads the model directly |
| `manipulation.reachable_workspace_m` | A coarse envelope of the workspace a Pinocchio forward-kinematics over the model would compute exactly; URML declares the bound, the planner consumes the model |
| `manipulation.grippers[].kind` | The end-effector body in the model's tree; URML names it at the capability altitude, far above the model's frames |
| `mobility.max_velocity` / `max_payload` | Platform-level bounds the dynamics parameters in a Pinocchio model relate to; declared at URML's altitude, not derived from the model today |
| Joint / dynamic limits (deferred) | Held precisely in the Pinocchio model; URML defers these to the safety envelope today, with a queued declaration below |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins against platform limits before dispatch; the trajectory a Pinocchio-based planner returns is checked against the envelope, not the model |

### What URML v0.1 does not yet express for Pinocchio

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Joint and dynamic-limit declaration.** URML's manifest declares
   `reachable_workspace_m` but not per-joint position, velocity, and torque
   limits or dynamic parameters; those live precisely in a Pinocchio model and
   are deferred to the safety envelope today. A future Spec RFC could add an
   optional joint and dynamic-limit declaration so a URML capability can be
   checked against (or derived from) the model, shared with the wave anchor
   (RFC-0342).
2. **Planner-class declaration.** URML's manifest does not record which class of
   planner or solver realizes a goal. A future Spec RFC could add an optional
   planner-class declaration so the validator can reason about the realizing
   layer (including a Pinocchio-based whole-body solver) explicitly.

### Compatibility notes

- **Vendor org.** [`stack-of-tasks`](https://github.com/stack-of-tasks)
  (INRIA / LAAS-CNRS robotics ecosystem).
- **Engagement repo.** [`stack-of-tasks/pinocchio`](https://github.com/stack-of-tasks/pinocchio),
  the rigid-body kinematics and dynamics library.
- **Origin / policy.** France (INRIA / LAAS-CNRS, NATO-allied). Passes
  US-federal default policy (open-source academic backend, no provenance gate at
  the dynamics layer).
- **License fit.** Understood to be BSD-2-Clause; not SPDX-detected at
  verification time, so asked below as a question.
- **Substrate-neutrality.** Pinocchio is a backend many planners share; URML's
  consume-the-trajectory posture is independent of which dynamics library a
  planner runs on, so the boundary holds on a zero-ROS, zero-Pinocchio runtime
  equally.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The joint and dynamic-limit
  declaration and the planner-class declaration are queued Spec RFCs, shared with
  the wave anchor.
- Reference runtime: no change. There is no Pinocchio adapter to build; URML
  declares a goal and consumes the trajectory a planner returns, not the dynamics
  computation. No in-repo fixture is planned for Pinocchio specifically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Low direct fit.** This is stated plainly: URML does not map onto Pinocchio,
  there is no adapter, and no in-repo fixture is planned. The value is a
  consistency-and-boundary clarification and an ecosystem touch, not an
  integration. URML benefits more from the conceptual clarity than Pinocchio
  benefits from the engagement.
- **Indirection.** URML's relation to Pinocchio runs through a planner or solver,
  so the touch is one layer removed. A maintainer could reasonably ask why URML
  reaches them at all; the answer is the model-consistency question and the
  boundary clarification the wave needs.

## Alternatives considered

1. **Skip Pinocchio and engage only the planners built on it.** Rejected. The
   wave draws a boundary (URML declares a goal and consumes a trajectory, not the
   dynamics computation). Naming the model-consistency relation once with the
   backend's maintainers keeps the planner engagements honest and avoids implying
   URML reaches into the dynamics library in any of them.
2. **Claim a direct URML-to-Pinocchio mapping.** Rejected. It would over-promise.
   URML has no kinematic tree, no dynamics, no solver surface; pretending
   otherwise would fail the substrate-neutrality acid test and misrepresent the
   altitude.
3. **Derive the URML manifest automatically from a Pinocchio model.** Rejected
   for now. Whether a URML capability declaration should be derivable from a model
   is a real question (asked below), but building that derivation is a queued Spec
   RFC concern, not an Outreach claim, and the model and the manifest sit at
   different altitudes by design.

## Prior art

- [RFC-0342 (OMPL outreach)](0342-ompl-outreach.md): the Move #26 wave anchor;
  the planner boundary and the goal-declaration contract this RFC defers to.
- [RFC-0346 (Crocoddyl outreach)](0346-crocoddyl-outreach.md): sibling
  whole-body optimal-control engagement built directly on Pinocchio; the closest
  coupling to this backend.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer that runs the trajectory a Pinocchio-based planner produces.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the manipulation
  planning framework the realizing layer often sits inside.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  URML's whole-body manipulation surface, where the kinematic-tree consistency
  question bites hardest.
- Sibling Move #26 RFCs: RFC-0347 (OCS2), RFC-0348 (CasADi), RFC-0349 (acados),
  several of which compute over a Pinocchio or CasADi backend.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, where the capability surface this engagement touches
  lives.

## Unresolved questions

For the Pinocchio maintainers:

1. **Model-consistency relation.** Should a URML capability declaration
   (`reachable_workspace_m`, a future joint-limit block) be derivable from, or
   statically checked against, a Pinocchio model, or is the only honest relation
   "URML declares a coarse capability and the model stays invisible to it"?
2. **Backend-vs-intent boundary.** Is "URML talks to the planner or solver, not
   to Pinocchio, and consumes a trajectory, not a dynamics computation" the right
   boundary statement from your side, or does it mischaracterize where Pinocchio
   sits?
3. **Coarse-vs-precise altitude.** URML declares capability at a coarse altitude
   on purpose. Is a coarse `reachable_workspace_m` a fair summary of what the model
   computes precisely, or does that abstraction lose something a downstream
   consumer needs?
4. **Crocoddyl coupling.** Crocoddyl (RFC-0346) builds on Pinocchio. Is engaging
   the dynamics backend and the optimal-control solver as separate, clearly
   bounded touches the right shape, or would you prefer one consolidated thread?
5. **License.** What is the current license of Pinocchio (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD-2-Clause)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0345 ships as a single RFC document PR alongside the Move #26 ledger
([`examples/lighthouses/outreach-move26.yaml`](../../examples/lighthouses/outreach-move26.yaml))
and the post bodies
([`examples/lighthouses/posts-move26.md`](../../examples/lighthouses/posts-move26.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`stack-of-tasks/pinocchio`](https://github.com/stack-of-tasks/pinocchio)
pointing at this RFC (the repo has both enabled). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 3,434 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, low direct fit, indirection).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: France (INRIA / LAAS-CNRS, NATO-allied); default policy passes
      at the dynamics layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Pinocchio is a
      backend URML never touches directly, the boundary holds on a zero-Pinocchio
      runtime, composed-above and honest about the low-fit altitude).
