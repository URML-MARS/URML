---
rfc: 0338
title: Ceres Solver (nonlinear optimization backend) integration, request for comment from the Ceres Solver maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-02
updated: 2026-06-02
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

# RFC-0338: Ceres Solver integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. This RFC reaches the deepest layer in that wave:
[`ceres-solver/ceres-solver`](https://github.com/ceres-solver/ceres-solver), a
general nonlinear least-squares optimizer that underlies a great deal of SLAM,
calibration, and bundle adjustment. It **requests review and feedback from the
Ceres Solver maintainers**.

This RFC is honest about altitude up front. Ceres is general-purpose math, not
robotics-specific, and **URML does not map onto Ceres directly**. URML's
Layer-1 manifest declares `frames` and `declared_locations`; the estimators
that produce those frames (the pose graphs, the bundle adjustments) often use
Ceres as their optimization backend. URML benefits only **indirectly**: the
estimates Ceres helps produce are what ground URML's frames. Ceres sits well
below URML's altitude, at the bottom of the substrate. URML composes far above
it, and there is no direct seam between them.

This is an ecosystem acknowledgement with a clear boundary statement, not a
mapping claim. URML records that Ceres is foundational to the estimators URML
consumes from, and asks the maintainers whether any URML-facing alignment exists
at all or whether Ceres is purely a backend below the boundary.

## Motivation

Ceres is the optimization engine many SLAM and state-estimation stacks are built
on. URML's interest is honest and modest:

1. **Ceres grounds the estimates URML consumes.** URML validates intent against
   a world model expressed in `frames` and `declared_locations`. Those frames
   come from estimators (pose graphs, bundle adjustment) that frequently run on
   Ceres. URML never touches Ceres, but the quality of what Ceres solves shapes
   the world model URML reasons over.
2. **It completes the wave's honest picture.** Move #25 engages estimators and
   occupancy maps. Naming the optimization backend that several of them share is
   an honest acknowledgement of the full stack below URML, not an attempt to map
   onto it.
3. **It is a clean boundary test.** If URML cannot find a direct seam to Ceres,
   that is the correct result and it confirms the boundary. A general optimizer
   is the substrate's substrate; URML staying out of it is the substrate-neutral
   posture working as intended.

Repo at [`ceres-solver/ceres-solver`](https://github.com/ceres-solver/ceres-solver)
(about 4,491 stars, Issues **and** Discussions enabled, not archived, last push
2026-05-31, active). License is asked as a question below (the GitHub API did not
surface an SPDX id at verification time; understood to be BSD-3-Clause). Origin:
Google (United States); passes US-federal default policy (open-source
optimization library, no provenance gate at the backend layer).

## Detailed design

### URML v0.1 capability-manifest mapping (no direct fixture)

There is no direct manifest mapping. The table records the indirect path, not a
binding.

| URML field | Relationship to Ceres |
|---|---|
| `frames` (`{name, parent}`) | Produced by estimators that may run on Ceres; URML reads the resulting frame, never Ceres |
| `declared_locations` (`{name, pose, frame}`) | Poses expressed in those produced frames; grounded indirectly by what Ceres solves |
| `mobility`, `connectivity` | Unrelated to Ceres; declared independently of the optimization backend |
| Safety envelope (Pass 3) | Reasons over the produced world model, not over any Ceres internal state |

### What URML v0.1 does not yet express for Ceres

These are noted as *queued Spec RFCs* shared with the rest of the wave. **None
is proposed in this Outreach RFC**, and none is specific to Ceres.

1. **Localization / pose-source declaration.** URML has no manifest field naming
   the estimator that produces its frames. A future Spec RFC could add one. It
   would name an estimator, never an optimization backend like Ceres.
2. **REP-105 frame-convention alignment.** URML declares `frames` with `name`
   and `parent` but does not pin the ROS REP-105 convention normatively. A future
   Spec RFC could align it. This is an estimator-output concern, below which
   Ceres sits.

### Compatibility notes

- **Vendor org.** [`ceres-solver`](https://github.com/ceres-solver), the Ceres
  Solver project (Google origin, community-maintained).
- **Engagement repo.** [`ceres-solver/ceres-solver`](https://github.com/ceres-solver/ceres-solver),
  the nonlinear least-squares optimization library.
- **Origin / policy.** United States (Google origin). Passes US-federal default
  policy (open-source optimization library, no provenance gate at the backend
  layer).
- **License fit.** Understood to be BSD-3-Clause; not SPDX-detected at
  verification time, so asked below as a question. Permissive, clean fit if
  confirmed.
- **Substrate-neutrality.** Ceres is one optimization backend among several
  (g2o, GTSAM's own backend, custom solvers). URML maps to none of them
  directly; that is the substrate-neutral result.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** No Ceres-specific manifest field is
  proposed, because there is no direct mapping.
- Reference runtime: **no change, and none anticipated.** URML would not ship a
  Ceres adapter; Ceres is below the boundary URML adapts at.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Lowest direct fit in the wave.** Ceres is general-purpose math, not
  robotics-specific. URML does not map onto it at all; the relationship is
  indirect, through the estimators that use Ceres as a backend. This RFC makes
  that explicit and does not overclaim a seam that is not there.
- **Risk of being noise to the maintainers.** Because the fit is indirect, the
  engagement risks reading as off-target to an optimization-library maintainer.
  The RFC mitigates this by stating the boundary plainly and asking, directly,
  whether any URML-facing alignment exists or whether Ceres is purely a backend.

## Alternatives considered

1. **Skip Ceres entirely.** Considered seriously. The fit is the most indirect in
   the wave. Engaging anyway is the honest move: Ceres is foundational to the
   estimators URML consumes from, and acknowledging the full stack, with the
   boundary stated, is more honest than a silent gap.
2. **Fold Ceres into the GTSAM RFC.** Rejected. GTSAM ([RFC-0333](0333-gtsam-outreach.md))
   is a factor-graph library with its own modest-fit framing; Ceres is a separate
   project with a separate community. The modest-fit posture is mirrored, but the
   thread stays its own.
3. **Claim a direct optimization-as-a-service mapping.** Rejected. It would
   overclaim. URML does no optimization and exposes no objective to a solver;
   asserting a direct seam would fail the honesty bar and the substrate-neutrality
   acid test.

## Prior art

- [RFC-0333 (GTSAM outreach)](0333-gtsam-outreach.md): the sibling backend-layer
  engagement in this wave, the closest precedent for a modest-fit posture below
  URML's altitude.
- Move #16 SLAM RFCs: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md): the round-one SLAM
  substrates, several of which use Ceres as a backend.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  surface the Ceres-backed estimators ultimately produce.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-role surface over which a produced estimate reaches the validator.
- Sibling Move #25 RFCs: RFC-0332 (robot_localization, the wave anchor),
  RFC-0336 (GLIM).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm this engagement points at.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface the
  Ceres-backed estimators ground.

## Unresolved questions

For the Ceres Solver maintainers:

1. **Any URML-facing alignment at all.** Is there any meaningful URML-facing
   alignment with Ceres, or is Ceres purely a backend below the boundary URML
   adapts at, with the relationship entirely indirect through the estimators that
   use it?
2. **Backend boundary.** Is "URML stays above the estimators, which sit above
   Ceres" the correct boundary, with URML never touching the solver?
3. **Ecosystem acknowledgement.** Would the maintainers prefer URML simply
   acknowledge Ceres as foundational to the consumed estimators, rather than
   document any mapping at all?
4. **License.** What is the current license of Ceres Solver (the GitHub API did
   not surface an SPDX id at verification time; understood to be BSD-3-Clause)?
5. **Conformance listing.** Would the Ceres project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md)), or
   is a backend library out of scope for such a listing?
6. **Anything else.**

## Implementation note

RFC-0338 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`ceres-solver/ceres-solver`](https://github.com/ceres-solver/ceres-solver)
pointing at this RFC (the repo has both enabled). If the maintainers prefer
another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 4,491 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-31).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, lowest direct fit in the wave, risk of being
      noise to the maintainers).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; no Ceres-specific manifest field proposed; the
      shared queued Spec RFCs are estimator-side, not Ceres-side.
- [x] Provenance: US (Google origin); default policy passes at the backend layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Ceres is one
      optimization backend among several, URML maps to none directly, boundary
      stated plainly).
