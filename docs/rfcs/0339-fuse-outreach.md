---
rfc: 0339
title: fuse (ROS sensor-fusion / state-estimation framework) integration, request for comment from the fuse maintainers
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

# RFC-0339: fuse integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

> **Maintainer-correction note (2026-06-08):** @svwilliams (fuse maintainer)
> engaged and confirmed two points folded in here. The license is
> **BSD-3-Clause** (confirmed, not just inferred). And fuse's per-estimate
> **covariance is an opt-in advisory signal, explicitly NOT safety-rated**, so
> URML must not treat it as a safety gate. URML therefore models fuse as a
> config-dependent **pose source** beside robot_localization, and any future
> covariance-quality threshold stays an advisory hint, never a safety guarantee.

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. This RFC reaches
[`locusrobotics/fuse`](https://github.com/locusrobotics/fuse), a graph-based
sensor-fusion and state-estimation framework for ROS, and **requests review and
feedback from the fuse maintainers**.

fuse produces a fused state estimate: a pose, a transform, and the covariance
those carry. URML's Layer-1 manifest declares `frames` (ROS REP-105 convention:
`map`, `odom`, `base_link`) and `declared_locations` (named poses in a named
frame). A state-estimation framework like fuse is what those frames and poses
are expressed against. URML does not perform estimation. It consumes the
estimate and statically validates intent against the resulting world model
before dispatch.

URML composes **above** fuse: a validated primitive (`move_to`, `scan`,
`detect`, `measure`, `report`) resolves a target against `declared_locations` in
a declared `frame`, and that frame is grounded by the fused estimate fuse
publishes. The differentiator is **static validation against the capability
manifest and the active safety envelope before dispatch**, against the world
model the estimator produced. fuse is one state-estimation framework among
several; the same primitive runs unchanged on any runtime that produces a pose.

This is the wave anchor robot_localization's modern, plugin-based sibling. See
[RFC-0332](0332-robot-localization-outreach.md) for the anchor framing; this RFC
maps the same pose-source role onto fuse's graph-based design.

## Motivation

fuse is a general, extensible sensor-fusion framework built around a constraint
graph, positioned as a modern alternative to the filter-based
robot_localization. A state-estimation framework is exactly where URML's frames
and poses get their meaning:

1. **It produces the world model URML validates against.** URML's
   `declared_locations` are poses in a `frame`, and a primitive's target is
   resolved in that frame. fuse is one source of the estimate that grounds the
   frame. URML consumes the estimate; it does not compute it.
2. **Its output frames are URML's frames.** fuse publishes a state estimate
   expressed in the REP-105 frame tree (`map`, `odom`, `base_link`). URML's
   Layer-1 `frames` block ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
   declares the same frames at a coarser altitude. The two describe the same
   frame tree from two sides: fuse fills it, URML validates against it.
3. **A pose source is a missing manifest input.** URML declares sensors under
   `perception.sensors[].measurement_type`, but it does not declare which
   estimator turns those measurements into a pose. fuse is a clean instance of
   the localization / pose-source declaration URML lacks. This is a queued Spec
   RFC, flagged below, not proposed here.
4. **Covariance is a candidate envelope input.** fuse carries estimate
   covariance through its graph. URML's safety envelope could one day treat
   estimate quality as an admission threshold: reject a `move_to` when the
   localization covariance exceeds a declared bound. That is a queued Spec RFC,
   not proposed here. The estimator stays Layer 0; URML never reaches into the
   graph.

Repo at [`locusrobotics/fuse`](https://github.com/locusrobotics/fuse) (about 868
stars, Issues enabled, Discussions disabled, not archived, last push
2026-05-06). License is asked as a question below (the GitHub API did not surface
an SPDX id at verification time; understood to be BSD-3-Clause). Origin: Locus
Robotics (United States); passes US-federal default policy.

Locus Robotics was engaged earlier on a distinct surface: the warehouse
coordination side, off GitHub, in Move #21
([RFC-0300](0300-locus-robotics-outreach.md)). This RFC is a **separate
conversation** about their open-source `fuse` state-estimation framework. It
cross-links RFC-0300 for context only and does not re-pitch the warehouse
relationship.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `fuse_state_estimate_cell.yaml` fixture)

| URML field | Maps to fuse attribute |
|---|---|
| `robot_id`, `description` | Deployment identity (not a fuse concept; carried at the manifest envelope) |
| `frames[].name` / `frames[].parent` | The REP-105 frames fuse publishes its estimate over (`map` -> `odom` -> `base_link`) |
| `declared_locations[].frame` | The frame a named pose is expressed in; grounded by fuse's fused estimate |
| `declared_locations[].pose` | A named target pose `move_to` resolves against, in fuse's estimated frame |
| `perception.sensors[].measurement_type` | The measurement sources (odometry, IMU, GPS, lidar pose) fuse fuses into the estimate |
| Pose / localization source (no field yet) | fuse itself as the declared pose source; the localization / pose-source declaration is a queued Spec RFC |
| Estimate covariance (no field yet) | fuse's per-estimate covariance; a candidate envelope quality threshold, a queued Spec RFC |
| `connectivity` | The transport the estimate is published over; URML reasons about link loss, not graph internals |
| Safety envelope limits (Pass 3) | Conjoined with the declared frame and pose; URML applies strictest-wins before dispatch |

### What URML v0.1 does not yet express for fuse

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML declares sensors but not the
   estimator that turns them into a pose. A future Spec RFC could add an optional
   pose-source field so the manifest names which state-estimation framework
   grounds its `frames` (fuse, robot_localization, a SLAM stack). It would name
   the source, not model the graph.
2. **REP-105 frame-convention alignment.** URML's `frames` block is self-declared
   today and does not pin to REP-105 names or assert a `map` / `odom` /
   `base_link` tree. A future Spec RFC could align the convention so a fused
   estimate's frames bind cleanly to the manifest.
3. **Covariance / quality envelope threshold.** URML's safety envelope has no
   notion of estimate quality. A future Spec RFC could add an optional covariance
   or quality threshold so a primitive is rejected when localization confidence
   falls below a declared bound.

### Compatibility notes

- **Vendor org.** [`locusrobotics`](https://github.com/locusrobotics) (Locus
  Robotics, United States), the open-source home of the `fuse` framework.
- **Engagement repo.** [`locusrobotics/fuse`](https://github.com/locusrobotics/fuse),
  the graph-based sensor-fusion and state-estimation framework.
- **Distinct prior surface.** Locus Robotics was engaged off GitHub on the
  warehouse coordination side in Move #21 ([RFC-0300](0300-locus-robotics-outreach.md)).
  This is a different repo and a different conversation, not a re-pitch.
- **Origin / policy.** United States (Locus Robotics). Passes US-federal default
  policy (open-source state-estimation framework, no provenance gate at the
  estimator layer).
- **License fit.** Understood to be BSD-3-Clause; not SPDX-detected at
  verification time, so asked below as a question.
- **Substrate-neutrality.** fuse is one state-estimation framework among several;
  the same URML primitives map to a deployment grounded by robot_localization
  ([RFC-0332](0332-robot-localization-outreach.md)), a SLAM stack, or any runtime
  that publishes a pose, with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The localization / pose-source
  declaration, the REP-105 frame-convention alignment, and the covariance /
  quality envelope threshold are queued Spec RFCs.
- Reference runtime: no change in this RFC. A fuse mapping would treat the fused
  estimate as the source that grounds the manifest's `frames`, against which a
  validated primitive's target is resolved; a planned
  `fuse_state_estimate_cell.yaml` fixture would document the pose-source binding.
- Conformance: no change. fuse is Layer 0; URML never reaches into the graph.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Pose-source field is not yet specified.** The cleanest manifest binding for
  fuse (a declared pose source) is a queued Spec RFC, not a shipped field, so the
  mapping describes a binding URML cannot yet express in a manifest.
- **Same-org, different-surface care.** Locus Robotics already has a distinct
  off-GitHub thread (RFC-0300). A second engagement, even on a separate
  open-source repo, has to be clearly scoped so it does not read as re-pitching
  the warehouse relationship.

## Alternatives considered

1. **Fold fuse into the robot_localization RFC (RFC-0332) as one pose-source
   thread.** Rejected. fuse and robot_localization are different frameworks with
   different designs (graph-based versus filter-based) and, likely, different
   licenses. A per-framework RFC lets each maintainer community thread its own
   conversation, and lets URML ask each how it positions relative to the other.
2. **Skip the pose-source mapping; let URML declare only sensors.** Rejected.
   Production deployments care which estimator grounds their frames; declaring
   the sensors but not the estimator leaves the world model URML validates
   against unanchored.
3. **Model fuse's constraint graph in the URML manifest.** Rejected. The graph,
   the constraints, and the optimization are Layer 0 / substrate concern. URML
   declares capability and consumes the estimate; modelling the graph would fail
   the substrate-neutrality acid test and couple URML to one estimator's design.

## Prior art

- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the Move #25 wave anchor; fuse is its modern, plugin-based sibling and shares
  the pose-source role.
- [RFC-0335 (KISS-ICP outreach)](0335-kiss-icp-outreach.md) and
  [RFC-0336 (GLIM outreach)](0336-glim-outreach.md): sibling Move #25 estimators
  (LiDAR odometry and globally-consistent SLAM) that ground the same frames.
- Move #16 SLAM RFCs, the round-one lineage this wave extends:
  [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md).
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the
  frame-tree spec surface a fused estimate binds to.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  how URML reasons about the transport an estimate is published over.
- [RFC-0300 (Locus Robotics outreach)](0300-locus-robotics-outreach.md): the
  distinct prior Locus Robotics warehouse engagement (different surface).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  compatible-runtimes registry referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the fuse maintainers:

1. **Frame / pose-source alignment.** Is "fuse produces the fused estimate, URML
   declares its `frames` and `declared_locations` against that estimate and
   validates above it" the right boundary, with URML staying entirely out of the
   graph?
2. **Position relative to robot_localization.** For a URML localization / pose-
   source declaration, how should fuse be named and positioned next to
   robot_localization, given fuse is the graph-based alternative? Is a single
   pose-source enum with both as values the right shape?
3. **REP-105 frame conventions.** Does fuse always publish over the REP-105
   `map` / `odom` / `base_link` tree, or are there configurations where URML
   should not assume those names?
4. **Covariance as an envelope input.** fuse carries estimate covariance. Is the
   per-estimate covariance a useful admission threshold for URML (reject a
   `move_to` when localization confidence is below a declared bound), or is that
   the wrong altitude for a static check?
5. **License.** What is the current license of `fuse` (the GitHub API did not
   surface an SPDX id at verification time; understood to be BSD-3-Clause)?
6. **Conformance listing.** Would the fuse project consider a project link to
   URML's compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0339 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`locusrobotics/fuse`](https://github.com/locusrobotics/fuse) pointing at this
RFC (Discussions are disabled on the repo), with the state-estimation /
pose-source framing explicit. If the maintainers prefer another channel, URML
will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 868 stars, not archived, Issues enabled,
      Discussions disabled, last push 2026-05-06).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, unspecified pose-source field, same-org
      different-surface care).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (Locus Robotics); default policy passes at the estimator
      layer.
- [x] Distinct from the prior Locus warehouse engagement (RFC-0300); cross-linked
      for context, not re-pitched.
- [x] CLAUDE.md compliance check passed (substrate-neutral; fuse is one
      state-estimation framework among many, URML consumes the estimate and never
      reaches into the graph).
