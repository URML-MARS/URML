---
rfc: 0356
title: GraspNet (6-DoF grasp pose detection) integration, request for comment from the GraspNet maintainers
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

# RFC-0356: GraspNet integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #27 is URML's manipulation and grasping wave. This RFC reaches
[`graspnet/graspnet-baseline`](https://github.com/graspnet/graspnet-baseline),
the GraspNet-1Billion baseline: a 6-DoF grasp-pose-detection network plus the
`graspnetAPI`, originating from the MVIG lab at Shanghai Jiao Tong University. It
**requests review and feedback from the GraspNet maintainers**.

GraspNet detects 6-DoF grasp poses from a point cloud. In URML's terms it is a
**grasp-pose source**. URML declares the gripper capability (kind, force range,
accepted object classes) and the target object; GraspNet proposes candidate
grasp poses; URML statically validates a chosen candidate against the declared
gripper before the grasp runs, then consumes the result.

URML composes **above** GraspNet: URML `grasp` intent -> validated gripper
capability and object class -> GraspNet proposes candidate poses -> a chosen
candidate is checked for admissibility -> `ros2_control`
([RFC-0319](0319-ros2-control-outreach.md)) executes. The differentiator is the
**static admissibility check (force within the gripper's range, object class in
`accepted_classes`) before the grasp runs**. GraspNet is one grasp-pose source
among several; the same `grasp` primitive runs unchanged on a different detector
or on a fixed grasp.

## Motivation

GraspNet is a reference baseline for data-driven 6-DoF grasp detection, and a
grasp-pose source is exactly the seam URML's `grasp` primitive needs filled
underneath it:

1. **It produces what `grasp` consumes.** URML's `grasp` declares intent plus a
   target object class; it does not detect a physical grasp pose. GraspNet
   detects 6-DoF candidate poses from a point cloud. GraspNet is the perception
   step that turns "grasp the bottle" into a concrete pose to attempt.
2. **It is where the admissibility check earns its keep.** URML's contribution
   sits one layer up: before a candidate pose is attempted, a static check that
   the declared gripper can close on it (requested force within
   `[force_min_n, force_max_n]`, object class in `accepted_classes`) and that
   the safety envelope admits it. A pose that the declared gripper cannot
   service is rejected before any motion.
3. **It grounds the grasp-pose-source manifest gap.** Mapping GraspNet surfaces
   a real gap: URML has no first-class way to declare which grasp-pose source a
   deployment binds to, or the interface contract it returns. The mapping makes
   that gap concrete and queues it as a Spec RFC.
4. **It keeps the stack substrate-neutral.** A `grasp` primitive that consumes a
   GraspNet candidate must also consume a candidate from another detector, or a
   fixed grasp, with no change to the program. GraspNet is one source among many;
   the execution still routes through MoveIt 2
   ([RFC-0202](0202-moveit2-outreach.md)) and `ros2_control`.

Repo at [`graspnet/graspnet-baseline`](https://github.com/graspnet/graspnet-baseline)
(about 952 stars, Issues enabled, not archived, last push 2025-02-17, so roughly
a year and a few months since the last push). It remains a widely cited reference
baseline for 6-DoF grasp detection; the mild staleness is noted lightly and does
not change its standing as the reference to map against.

## Detailed design

### URML v0.1 mapping (planned `graspnet_source_cell.yaml` fixture)

| URML field or primitive | Maps to GraspNet attribute |
|---|---|
| `manipulation.grippers[].kind` | The gripper geometry a candidate pose is filtered against (parallel-jaw, vacuum, and so on) |
| `manipulation.grippers[].force_min_n` / `force_max_n` | The closing-force window a requested `grasp` force is checked against before a candidate is attempted |
| `manipulation.grippers[].accepted_classes` | The object classes the gripper may service; a candidate on an out-of-set class is rejected |
| `manipulation.reachable_workspace_m` | The workspace a returned 6-DoF candidate pose must fall inside to be admissible |
| `perception.object_vocabulary` | The object classes `detect` may name as the `grasp` target before GraspNet proposes poses for it |
| `grasp` (target object) | The intent that triggers a GraspNet detection pass over the point cloud, scoped to the target object |
| GraspNet candidate pose + width + score | The 6-DoF pose, gripper width, and quality URML reads to pick and validate a candidate |
| Safety envelope limits (Pass 3) | Conjoined with the gripper and workspace bounds; URML applies strictest-wins before the grasp |

### What URML v0.1 does not yet express for GraspNet

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Grasp-pose-source declaration.** URML has no first-class way to declare that
   a deployment binds to a grasp-pose source (a detector like GraspNet) and what
   interface contract it returns (pose, gripper width, score, frame). A future
   Spec RFC could add an optional grasp-pose-source declaration so the validator
   can reason about the source the `grasp` intent draws candidates from.
2. **Candidate-feasibility fields.** URML's gripper model carries a single force
   range and class list. Filtering GraspNet candidates also wants gripper width
   and approach-direction limits. A future Spec RFC could enrich the gripper
   declaration with the width and approach fields a candidate filter needs.

### Compatibility notes

- **Vendor org.** [`graspnet`](https://github.com/graspnet) (MVIG lab, Shanghai
  Jiao Tong University; academic, open-source).
- **Engagement repo.** [`graspnet/graspnet-baseline`](https://github.com/graspnet/graspnet-baseline):
  the GraspNet-1Billion 6-DoF grasp-detection baseline plus `graspnetAPI`.
- **Origin / policy.** International (academic lab). Treated as INTL; passes
  US-federal default policy (open-source perception model, no provenance gate at
  the grasp-detection layer; URML composes above it and validates before motion).
- **License note.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring.
- **Substrate-neutrality.** GraspNet is one grasp-pose source among several; the
  same `grasp` primitive consumes a candidate from another detector or a fixed
  grasp with no change to the program, and execution still routes through MoveIt 2
  and `ros2_control`.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The grasp-pose-source declaration and
  the candidate-feasibility fields are queued Spec RFCs.
- Reference runtime: no change in this RFC. A GraspNet mapping would route a
  validated `grasp` intent to a detection pass, read the returned candidates, and
  validate a chosen candidate against the declared gripper; the planned
  `graspnet_source_cell.yaml` fixture would prove the admissibility check
  hermetically against a recorded candidate set.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Coarse gripper model.** URML's gripper declaration is a single force range
  plus a class list. Filtering GraspNet candidates cleanly wants width and
  approach limits the model does not yet carry; the candidate-feasibility fields
  are queued, not present.
- **Staleness of the baseline.** The baseline's last push is 2025-02-17. The
  mapping is described at the candidate-interface altitude (pose, width, score)
  to stay robust if the repo stays quiet or a successor takes over.

## Alternatives considered

1. **Detect grasp poses inside URML.** Rejected. Grasp-pose detection is a
   substrate / perception concern; URML declares the gripper capability and the
   target object and validates a candidate. Detecting poses in URML would fail
   the substrate-neutrality acid test and duplicate what GraspNet already does.
2. **Skip the source declaration and hard-wire GraspNet.** Rejected. Hard-wiring
   one detector would couple `grasp` to a single source. The grasp-pose-source
   declaration is queued precisely so a deployment can name any source behind the
   same primitive.
3. **Model the full point cloud in the URML manifest.** Rejected. The point
   cloud and the detection network are Layer 0 / substrate; URML declares
   capability over the gripper and the object class, not the sensor stream.

## Prior art

- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md): the motion-planning
  layer a validated grasp pose is executed through.
- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md): the
  execution layer the grasp motion ultimately drives.
- [RFC-0010 (whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md):
  the related manipulation spec surface the gripper capability lives under.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  surface a returned 6-DoF candidate pose is resolved against.
- Sibling Move #27 RFCs: RFC-0352 (TRAC-IK, the inverse-kinematics anchor) and
  RFC-0358 (Shadow Robot dexterous hand).
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  and [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the
  `grasp` primitive and the gripper-capability surface this engagement exercises.

## Unresolved questions

For the GraspNet maintainers:

1. **Capability-plus-target boundary.** Is "URML declares the gripper capability
   and the target object class, GraspNet proposes candidate poses, URML filters a
   chosen candidate for feasibility" the right boundary, with URML staying above
   the detector and never detecting poses itself?
2. **Gripper parameters for filtering.** Which gripper parameters should URML
   declare so a returned candidate can be checked for feasibility: closing-force
   window, gripper width, approach direction, anything else?
3. **Stable candidate interface.** Does the grasp-detection output have a stable
   interface (pose, gripper width, score, reference frame) that URML could target
   as the contract for a grasp-pose-source declaration?
4. **Point-cloud and frame conventions.** What reference frame and units does a
   returned 6-DoF pose use, so URML resolves it consistently against the
   declared workspace and the frame graph?
5. **Conformance listing.** Would GraspNet consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0356 ships as a single RFC document PR alongside the Move #27 ledger
([`examples/lighthouses/outreach-move27.yaml`](../../examples/lighthouses/outreach-move27.yaml))
and the post bodies
([`examples/lighthouses/posts-move27.md`](../../examples/lighthouses/posts-move27.md)).

## How to respond

The live channel is a GitHub Issue on
[`graspnet/graspnet-baseline`](https://github.com/graspnet/graspnet-baseline)
pointing at this RFC (the repo has Issues enabled). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-03 (about 952 stars, not archived, Issues enabled,
      last push 2025-02-17; mild staleness noted lightly).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, coarse gripper model, baseline staleness).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international academic lab; default policy passes at the
      grasp-detection layer (URML composes above and validates before motion).
- [x] CLAUDE.md compliance check passed (substrate-neutral; GraspNet is one
      grasp-pose source among many, the same `grasp` primitive runs on another
      source or a fixed grasp, composed-above not assumed).
