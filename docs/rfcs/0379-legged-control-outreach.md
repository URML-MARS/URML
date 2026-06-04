---
rfc: 0379
title: legged_control (MPC + WBC legged control framework) integration, request for comment from the legged_control maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-04
updated: 2026-06-04
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

# RFC-0379: legged_control integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #29 is URML's open humanoid and legged-robot wave, round two. This RFC
reaches [`qiayuanl/legged_control`](https://github.com/qiayuanl/legged_control),
a complete legged-robot control framework that combines Model Predictive Control
and Whole-Body Control for quadrupeds and humanoids, built on OCS2 and
ros2_control-style interfaces. It **requests review and feedback from the
legged_control maintainers**.

legged_control is a legged locomotion stack. URML is not. URML describes robot
intent and declares capability: a navigation or task-level intent (`move_to`,
`scan`, `report`), a declared platform capability, and an active safety
envelope. legged_control realizes the locomotion that satisfies that intent
through its MPC plus WBC pipeline. URML composes **above** it: URML validates
admissibility (the target is reachable, the request is within the declared
envelope) before any motion, and does not do control.

This RFC is honest about the headline gap up front. URML's Layer-1 manifest has
no legged mobility-class `drive_type` and no whole-body capability declaration,
so a quadruped or humanoid cannot yet be declared at its real altitude. That gap
is the headline *queued Spec RFC*, tied to
[RFC-0010](0010-whole-body-bimanual-manipulation.md), and is **not proposed
here**.

## Motivation

legged_control is a complete model-based MPC plus WBC stack for legged robots,
which makes it a direct test of URML's "declare and validate, do not control"
boundary at the framework altitude:

1. **It realizes locomotion that URML only describes.** URML stops at intent and
   capability. The MPC plus WBC pipeline turns a navigation goal into joint-level
   commands that keep a legged robot balanced as it moves. legged_control is
   exactly the realizing layer URML is designed to sit above, never inside.
2. **It builds on OCS2, which URML engaged separately.** legged_control is built
   on OCS2 ([RFC-0347](0347-ocs2-outreach.md)), the general switched-system
   optimal-control library. Engaging the legged-specific framework and the
   general solver as distinct threads clarifies which capability surface URML
   declares over: the legged platform, not the solver internals.
3. **It exposes the honest legged gap.** Mapping a quadruped or humanoid onto
   URML's manifest shows immediately that `drive_type` has no legged class and
   there is no whole-body capability block. Naming that gap (queued Spec RFC,
   tied to RFC-0010) is more useful than papering a legged robot into a wheeled
   class.
4. **It ties to ros2_control.** legged_control uses ros2_control-style interfaces
   ([RFC-0319](0319-ros2-control-outreach.md)), which is the controller seam a
   realized URML intent typically reaches. The mapping stays at the intent and
   capability altitude so it holds across that interface.

Repo at [`qiayuanl/legged_control`](https://github.com/qiayuanl/legged_control)
(about 1,702 stars, Issues enabled, not archived, last push 2025-02-13). Origin:
Qiayuan Liao (open-source academic). Treated as open-academic,
NATO-allied-aligned; passes US-federal default policy (open-source academic
framework, no provenance gate at the control layer).

## Detailed design

### URML v0.1 capability and intent mapping (planned `legged_control_cell.yaml` fixture)

| URML field or primitive | Maps to legged_control role |
|---|---|
| `robot_id`, `description` | The legged platform's identity (carried at the manifest envelope) |
| `frames`, `declared_locations` | The world frame and named targets a `move_to` resolves against |
| `mobility.drive_type` | The platform's locomotion class; **no legged class exists in v0.1** (see queued gap below; today declared at a coarser approximation) |
| `mobility.max_velocity` | The base velocity bound, passed down as an MPC velocity constraint |
| `mobility.max_payload` | The declared carry limit, passed down as a load bound the stack respects |
| `manipulation` (humanoid arms, when present) | The arm capability of a humanoid platform, declared separately from locomotion |
| `move_to` (Layer-2 primitive) | A navigation-level goal the MPC plus WBC pipeline realizes as whole-body motion |
| `scan`, `report` | Perception and reporting intents issued around a realized locomotion goal |
| Safety envelope limits (Pass 3) | Conjoined with the platform's declared limits before any motion; URML applies strictest-wins, the stack treats them as constraints |

### What URML v0.1 does not yet express for legged_control

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Legged mobility-class `drive_type` and a whole-body capability declaration.**
   URML's `mobility.drive_type` enumerates wheeled, tracked, and aerial classes,
   with no legged or whole-body class, so a quadruped or humanoid cannot be
   declared at its real altitude. This is the **headline** gap. A future Spec
   RFC, tied to [RFC-0010](0010-whole-body-bimanual-manipulation.md), would add a
   legged mobility class and a whole-body capability block so the manifest can
   describe a legged platform honestly.
2. **Realizing-controller class hint.** URML's manifest does not record that a
   declared platform's motion is realized by an MPC plus WBC stack rather than a
   wheeled base controller. A future Spec RFC could add an optional
   realizing-controller hint so tooling can reason about the control layer
   explicitly. It would not model the framework.

### Compatibility notes

- **Engagement repo.** [`qiayuanl/legged_control`](https://github.com/qiayuanl/legged_control):
  a complete MPC plus WBC legged control framework for quadrupeds and humanoids,
  built on OCS2 and ros2_control-style interfaces.
- **Origin / policy.** Qiayuan Liao (open-source academic). Treated as
  open-academic, NATO-allied-aligned; passes US-federal default policy (no
  provenance gate at the control layer).
- **Open-source posture.** Open-source; the relationship is cross-citation and
  composition, not vendoring.
- **OCS2 coupling.** Built on OCS2 ([RFC-0347](0347-ocs2-outreach.md)), engaged
  separately; this RFC declares over the legged platform, not the solver.
- **Substrate-neutrality.** legged_control is one realizing framework among
  several; the same URML intent maps to a learned legged policy or a different
  model-based stack with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The legged mobility class plus
  whole-body capability block (the headline gap) and the realizing-controller
  hint are queued Spec RFCs.
- Reference runtime: no change in this RFC. A legged_control mapping would route
  a validated `move_to` goal, with the declared limits attached as constraints,
  to the framework's MPC plus WBC interface over its ros2_control-style seam; the
  planned `legged_control_cell.yaml` fixture would document the admissibility
  check before any motion.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Headline gap is unfilled.** URML cannot yet declare a legged platform at its
  real altitude, so the mapping today leans on a coarse `drive_type`
  approximation. The RFC names this honestly and defers it to a queued Spec RFC
  rather than hiding it.
- **Overlap with the OCS2 engagement.** legged_control is built on OCS2, engaged
  separately (RFC-0347). The two threads risk talking past each other; this RFC
  keeps its altitude on the legged platform's capability and intent, not the
  solver, to keep the boundary clean.

## Alternatives considered

1. **Fold legged_control into the OCS2 thread (RFC-0347).** Rejected. OCS2 is a
   general switched-system solver; legged_control is a complete legged framework
   built on it. The capability surface URML declares over differs (a legged
   platform versus a solver), so the engagements stay distinct and cross-linked.
2. **Declare a legged platform as `differential` or `manipulator_base` today.**
   Rejected. It would misdescribe the platform and fail URML's honesty norm. The
   correct response is to name the missing legged class as a queued Spec RFC, not
   to force a wheeled label.
3. **Push URML down into the MPC plus WBC loop.** Rejected. URML declares intent
   and validates admissibility; it does not produce joint commands. Reaching into
   the stack would break the layered design and the substrate-neutrality acid
   test.

## Prior art

- [RFC-0347 (OCS2 outreach)](0347-ocs2-outreach.md): the general optimal-control
  library legged_control is built on; engaged separately, cross-linked here.
- [RFC-0376 (legged_gym outreach)](0376-legged-gym-outreach.md): the
  learned-policy legged contrast; legged_control is model-based where legged_gym
  learns a policy.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the Spec RFC the headline legged-capability gap ties to.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  controller-interface engagement legged_control's ros2_control-style seam ties
  to.
- [RFC-0049 (ANYbotics ANYmal integration)](0049-anybotics-anymal-integration.md):
  a related legged-platform engagement.
- Sibling Move #29 RFCs: RFC-0372 (ToddlerBot, the wave anchor), RFC-0376
  (legged_gym, learned-policy legged), RFC-0377 (rsl_rl), and RFC-0378
  (DIAL-MPC).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.

## Unresolved questions

For the legged_control maintainers:

1. **Intent-to-stack boundary.** Is "URML navigation intent plus declared
   capability -> the MPC plus WBC stack" the right seam, with URML producing a
   navigation-level goal and staying entirely above the framework?
2. **Limits as constraints.** What is the right way for URML's declared limits
   (velocity, payload, the safety envelope) to map onto the controller's
   constraints, so an admissible URML program is also a feasible control problem
   for the MPC plus WBC pipeline?
3. **Relationship to OCS2.** legged_control is built on OCS2, which URML engaged
   separately (RFC-0347). From the framework's view, is the legged platform the
   right altitude for URML to declare over, with the solver staying below the
   line?
4. **Legged capability surface.** As URML drafts a legged mobility class and a
   whole-body capability block (the queued Spec RFC tied to RFC-0010), what
   fields would an MPC plus WBC stack most want a manifest to declare for a
   quadruped or humanoid?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0379 ships as a single RFC document PR alongside the Move #29 ledger
([`examples/lighthouses/outreach-move29.yaml`](../../examples/lighthouses/outreach-move29.yaml))
and the post bodies
([`examples/lighthouses/posts-move29.md`](../../examples/lighthouses/posts-move29.md)).

## How to respond

The live channel is a GitHub Issue on
[`qiayuanl/legged_control`](https://github.com/qiayuanl/legged_control) pointing
at this RFC (the repo has Issues enabled). If the maintainers prefer another
channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified (about 1,702 stars, not archived, Issues enabled, last
      push 2025-02-13).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, unfilled headline gap, OCS2 overlap).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs (the
      legged mobility class tied to RFC-0010 is the headline), not proposed here.
- [x] Provenance: open-academic (Qiayuan Liao), NATO-allied-aligned; default
      policy passes at the control layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; URML composes above
      the framework, declares and validates, does not control).
