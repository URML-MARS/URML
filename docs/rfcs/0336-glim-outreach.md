---
rfc: 0336
title: GLIM (LiDAR-inertial SLAM) integration, request for comment from the GLIM maintainers
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

# RFC-0336: GLIM (LiDAR-inertial SLAM) integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's pipeline, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. This RFC reaches [`koide3/glim`](https://github.com/koide3/glim),
a GPU-accelerated, factor-graph-based LiDAR-inertial SLAM stack from Kenji Koide
(AIST, Japan). It folds the older sibling
[`koide3/hdl_graph_slam`](https://github.com/koide3/hdl_graph_slam) into the same
thread, and **requests review and feedback from the GLIM maintainers**.

GLIM produces a globally-consistent map and pose estimate. URML's Layer-1
manifest declares `frames` (ROS REP-105: `map`, `odom`, `base_link`) and
`declared_locations` (poses in a named frame). GLIM is one of the substrates that
produces the `map` frame and the global pose those poses are expressed against,
and its map also feeds occupancy reasoning. URML does not perform SLAM. It
**consumes** the estimate and the map and statically validates intent against the
resulting world model **before dispatch**.

URML composes **above** GLIM: the estimator output (a globally-consistent pose
against `map`, plus the map itself) is a manifest input; the URML validator
checks a program against the declared capability and the active safety envelope;
only then does a primitive dispatch. The contrast with the sibling Move #25
target RFC-0335 (KISS-ICP) is deliberate: GLIM is full LiDAR-inertial SLAM with a
globally-consistent map, where KISS-ICP is odometry-only with drift.

## Motivation

GLIM is a state-of-the-art LiDAR-inertial SLAM stack, and a globally-consistent
map plus pose is exactly what grounds URML's `map` frame and its occupancy
reasoning:

1. **It produces the pose URML's `map` frame is expressed against.** URML's
   `frames` block declares REP-105 frames and `declared_locations` are poses in
   a named frame ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)).
   GLIM estimates the global `base_link` pose in `map` and maintains the map. The
   estimator and the manifest describe the same world model from two sides.
2. **The map feeds occupancy reasoning.** GLIM's globally-consistent map is not
   only a localization aid. It is the surface URML's safety envelope can reason
   about for occupancy and reachability before a `move_to` is admitted. A
   globally-consistent map makes that reasoning sound across a full traverse,
   not only locally.
3. **It is where consume-before-dispatch is cheap to show.** URML's
   contribution sits one layer up and earlier: a static check, before the first
   primitive dispatches, that the declared capability and the safety envelope
   admit the requested intent against the current map and pose.
4. **It grounds substrate-neutrality and the SLAM-vs-odometry distinction.** A
   localization source declared from GLIM must declare the same way from any
   other SLAM stack, and distinctly from an odometry-only source (RFC-0335). GLIM
   is one estimator among many; the acid test is that the same `frames` and
   `declared_locations` bind against any of them with no program change.

Repo at [`koide3/glim`](https://github.com/koide3/glim) (about 1,610 stars,
Issues enabled, Discussions disabled, not archived, last push 2026-05-07,
active). Sibling repo at [`koide3/hdl_graph_slam`](https://github.com/koide3/hdl_graph_slam)
(about 2,283 stars), the older LiDAR graph SLAM from the same maintainer. License
is asked as a question below (the GitHub API did not surface an SPDX id at
verification time; understood to be MIT). Origin: Japan / AIST; allied, passes
US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `glim_lidar_inertial_cell.yaml` fixture)

| URML field | Maps to GLIM output |
|---|---|
| `robot_id`, `description` | Deployment identity (not a GLIM concept; carried at the manifest envelope) |
| `frames` (`name`, `parent`) | REP-105 frame tree; GLIM estimates `base_link` -> `odom` -> `map` (the globally-consistent `map` node URML declares) |
| `declared_locations` (`name`, `pose`, `frame`) | Named poses expressed against the globally-consistent `map` frame GLIM produces |
| `perception.sensors[].measurement_type: point_cloud` | The LiDAR scans GLIM fuses with IMU in its factor graph |
| `connectivity` | The link roles a pose / map / estimate stream is carried over (RFC-0006), relevant when the estimator runs off-body |
| Localization source (queued, see below) | A LiDAR-inertial, globally-consistent SLAM source, declared as a manifest input (distinct from odometry-only) |
| Estimate covariance / quality (queued, see below) | A candidate safety-envelope threshold input from the factor graph's reported uncertainty |
| Primitives (`move_to`, `scan`, `detect`, `measure`, `report`) | Resolve against `declared_locations` in the global `map` frame; validated against map occupancy before dispatch |

### What URML v0.1 does not yet express for GLIM

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML declares sensors but not
   that a named substrate produces the pose and map its `frames` are expressed
   against, nor whether that source is odometry-only or full SLAM. A future Spec
   RFC could add an optional localization-source declaration so the manifest
   records a globally-consistent LiDAR-inertial SLAM source distinct from an
   odometry-only one (RFC-0335).
2. **REP-105 frame-convention alignment.** URML's `frames` are self-declared
   identifiers. A future Spec RFC could align them explicitly with REP-105
   (`map` / `odom` / `base_link`) so the estimator output frame and the manifest
   frame bind without ad-hoc naming.
3. **Covariance / quality envelope threshold.** GLIM's factor graph carries
   uncertainty. A future Spec RFC could add an optional safety-envelope threshold
   on estimate covariance or quality, so a primitive is rejected when the
   localization estimate is too degraded to act on.

### Compatibility notes

- **Vendor org.** [`koide3`](https://github.com/koide3), Kenji Koide (AIST,
  Japan).
- **Engagement repo.** [`koide3/glim`](https://github.com/koide3/glim), a
  GPU-accelerated, factor-graph-based LiDAR-inertial SLAM stack; active.
- **Sibling repo (folded into this thread).**
  [`koide3/hdl_graph_slam`](https://github.com/koide3/hdl_graph_slam), the older
  LiDAR graph SLAM, same maintainer. Which is the right integration surface (the
  current GLIM or the older hdl_graph_slam) is an open question below.
- **Origin / policy.** Japan (AIST). Allied; passes US-federal default policy
  (open-source SLAM stack, no provenance gate at the state-estimation layer).
- **License fit.** Understood to be MIT; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** GLIM is one estimator among many. The same `frames`
  and `declared_locations` bind against an odometry-only source (RFC-0335
  KISS-ICP), a fused estimator (RFC-0332 robot_localization, RFC-0334 OpenVINS),
  or the Move #16 SLAM stacks with no program change. URML never reaches into the
  estimator's internals (Layer 0).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The localization / pose-source
  declaration, the REP-105 frame-convention alignment, and the covariance /
  quality envelope threshold are queued Spec RFCs.
- Reference runtime: no change in this RFC. A GLIM mapping would read the global
  pose into the `map` frame URML's manifest declares and the map into occupancy
  reasoning; the planned `glim_lidar_inertial_cell.yaml` fixture would document
  the LiDAR-inertial, globally-consistent manifest, declaring the SLAM source
  honestly as distinct from odometry-only.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two-repo ambiguity.** GLIM and hdl_graph_slam split the surface under one
  maintainer. Anchoring on GLIM and folding the older repo in risks
  under-serving whichever the maintainer considers the real integration point;
  question 3 below asks for the call.
- **GPU and integration weight.** GLIM is GPU-accelerated and heavier to stand
  up than an odometry-only pipeline. A hermetic URML demo against it is more work
  to make reproducible than against KISS-ICP (RFC-0335).

## Alternatives considered

1. **Anchor on hdl_graph_slam instead of GLIM.** Rejected as the default anchor.
   GLIM is the current, actively developed LiDAR-inertial stack and the
   globally-consistent map plus pose URML consumes; hdl_graph_slam is the older
   graph SLAM. The older repo is named and folded in, and the anchor moves if the
   maintainer says it is the right surface.
2. **Two separate RFCs, one per repo.** Rejected. GLIM and hdl_graph_slam share
   one maintainer at koide3; two Issues in a day to one maintainer is the pattern
   that has drawn AI-content closes elsewhere. One anchor thread that names both
   is more respectful and just as discoverable.
3. **Model GLIM's factor-graph internals in the URML manifest.** Rejected. The
   factor graph, the IMU fusion, and the map representation are Layer 0 /
   substrate concern. URML declares the consumed pose and map and the frames they
   are expressed against, not how the estimator computes them. Modelling the
   internals would fail the substrate-neutrality acid test.

## Prior art

- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  and transform reasoning this engagement consumes a pose against.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-role surface a remote estimate or map stream is carried over.
- Move #16 SLAM RFCs: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md): the round-one SLAM
  substrates this wave extends.
- Sibling Move #25 RFCs: RFC-0332 (robot_localization, the wave anchor),
  RFC-0334 (OpenVINS), RFC-0335 (KISS-ICP, the odometry-only contrast),
  RFC-0337 (OctoMap), RFC-0340 (DLIO).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing and honest-substrate-limit norm this RFC applies.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the GLIM maintainers:

1. **Frame / pose-source alignment.** GLIM estimates a global `base_link` pose
   in `map`. Is matching that to URML's `frames` (REP-105 `map`) and expressing
   `declared_locations` against it the right alignment, or is there a different
   frame convention URML should read?
2. **Globally-consistent map vs odometry-only.** GLIM produces a
   globally-consistent map, where the sibling RFC-0335 (KISS-ICP) is
   odometry-only with drift. What is the right way for URML to declare that
   distinction as a localization-source property, and does the map feed occupancy
   reasoning the way this RFC assumes?
3. **hdl_graph_slam vs glim.** Which repo is the right integration surface: the
   current GLIM or the older hdl_graph_slam? Should the engagement stay one thread
   or fork?
4. **Estimate quality / covariance.** Does GLIM report a usable estimate
   covariance or quality signal from the factor graph that URML could read as a
   safety-envelope threshold input, so a primitive is rejected when localization
   is too degraded?
5. **Consume-not-control boundary.** Is "URML consumes the pose and map and stays
   entirely above the pipeline" the right boundary, with URML never reaching into
   the factor-graph internals?
6. **License.** What is the current license of `glim` and `hdl_graph_slam` (the
   GitHub API did not surface an SPDX id at verification time; understood to be
   MIT)?
7. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0336 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).
The `hdl_graph_slam` row in the ledger shares this RFC; a dedicated row is added
only if the engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`koide3/glim`](https://github.com/koide3/glim) pointing at this RFC (Discussions
are disabled on the repo). If the maintainer prefers hdl_graph_slam or another
venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (glim about 1,610 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-05-07; hdl_graph_slam about
      2,283 stars, named and folded in).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two-repo ambiguity, GPU and integration
      weight).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Japan (AIST); allied, default policy passes at the
      state-estimation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; GLIM is one estimator
      among many, URML consumes the estimate and map and never reaches into
      Layer 0).
