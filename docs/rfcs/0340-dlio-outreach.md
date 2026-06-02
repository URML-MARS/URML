---
rfc: 0340
title: DLIO (Direct LiDAR-Inertial Odometry) integration, request for comment from the DLIO maintainers
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

# RFC-0340: DLIO integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. This RFC reaches
[`vectr-ucla/direct_lidar_inertial_odometry`](https://github.com/vectr-ucla/direct_lidar_inertial_odometry)
(DLIO), a lightweight and accurate direct LiDAR-inertial odometry pipeline, and
**requests review and feedback from the DLIO maintainers**.

DLIO produces a LiDAR-inertial odometry pose estimate. URML's Layer-1 manifest
declares `frames` (ROS REP-105 convention: `map`, `odom`, `base_link`) and
`declared_locations` (named poses in a named frame). An odometry pipeline like
DLIO is what the `odom` frame, and the pose drift within it, are expressed
against. URML does not perform estimation. It consumes the estimate and
statically validates intent against the resulting world model before dispatch.

URML composes **above** DLIO: a validated primitive (`move_to`, `scan`,
`detect`, `measure`, `report`) resolves a target against `declared_locations` in
a declared `frame`, and DLIO's odometry pose grounds the `odom` frame in that
tree. The IMU-LiDAR extrinsics and the filter internals are substrate config
(Layer 0). The differentiator is **static validation against the capability
manifest and the active safety envelope before dispatch**. DLIO is one odometry
source among several; the same primitive runs unchanged on any runtime that
produces a pose.

## Motivation

DLIO is a direct LiDAR-inertial odometry pipeline from the UCLA Verifiable and
Control-Theoretic Robotics Laboratory (VECTR): tightly coupled LiDAR and IMU,
fast and accurate, producing a continuous odometry pose. An odometry source is
exactly where URML's `odom` frame gets its meaning:

1. **It grounds the `odom` frame.** URML's `declared_locations` are poses in a
   `frame`, and a primitive's target is resolved in that frame. DLIO is one
   source of the odometry estimate that grounds the REP-105 `odom` frame. URML
   consumes the estimate; it does not compute it.
2. **Its output frame is a URML frame.** DLIO publishes a pose in the REP-105
   tree (`odom` -> `base_link`). URML's Layer-1 `frames` block
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares
   the same frames at a coarser altitude. The two describe the same frame tree
   from two sides: DLIO fills the odometry link, URML validates against it.
3. **A pose source is a missing manifest input.** URML declares sensors under
   `perception.sensors[].measurement_type` (here lidar plus IMU), but it does not
   declare which pipeline turns those into a pose. DLIO is a clean instance of
   the localization / pose-source declaration URML lacks. This is a queued Spec
   RFC, flagged below, not proposed here.
4. **Drift is an honest property to declare.** A LiDAR-inertial odometry source
   is locally accurate but drifts over distance and offers no global loop
   closure. URML's safety envelope could one day treat estimate quality as an
   admission threshold. That is a queued Spec RFC, not proposed here. The
   extrinsics and the filter stay Layer 0; URML never reaches into them.

DLIO is LiDAR-inertial odometry. It sits between two siblings in this wave:
KISS-ICP ([RFC-0335](0335-kiss-icp-outreach.md)) is LiDAR-only odometry, and
GLIM ([RFC-0336](0336-glim-outreach.md)) is globally-consistent SLAM. DLIO fuses
LiDAR with IMU for odometry, without claiming global consistency.

Repo at [`vectr-ucla/direct_lidar_inertial_odometry`](https://github.com/vectr-ucla/direct_lidar_inertial_odometry)
(about 994 stars, Issues enabled, Discussions disabled, not archived, last push
2026-04-03). License is asked as a question below (the GitHub API did not surface
an SPDX id at verification time; understood to be MIT). Origin: UCLA Verifiable
and Control-Theoretic Robotics Laboratory (VECTR), United States; passes
US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `dlio_odometry_cell.yaml` fixture)

| URML field | Maps to DLIO attribute |
|---|---|
| `robot_id`, `description` | Deployment identity (not a DLIO concept; carried at the manifest envelope) |
| `frames[].name` / `frames[].parent` | The REP-105 frames DLIO publishes its odometry over (`odom` -> `base_link`) |
| `declared_locations[].frame` | The frame a named pose is expressed in; grounded by DLIO's odometry estimate |
| `declared_locations[].pose` | A named target pose `move_to` resolves against, in DLIO's estimated `odom` frame |
| `perception.sensors[].measurement_type: lidar` | The LiDAR input DLIO consumes |
| `perception.sensors[].measurement_type: imu` | The IMU input DLIO fuses for the inertial side |
| Pose / localization source (no field yet) | DLIO itself as the declared odometry source; the localization / pose-source declaration is a queued Spec RFC |
| Estimate drift / quality (no field yet) | DLIO's local accuracy without global consistency; a candidate envelope quality threshold, a queued Spec RFC |
| IMU-LiDAR extrinsics, filter internals | Substrate config (Layer 0); URML does not declare these |
| Safety envelope limits (Pass 3) | Conjoined with the declared frame and pose; URML applies strictest-wins before dispatch |

### What URML v0.1 does not yet express for DLIO

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML declares sensors but not the
   pipeline that turns them into a pose. A future Spec RFC could add an optional
   pose-source field so the manifest names which odometry or SLAM source grounds
   its `frames` (DLIO, KISS-ICP, GLIM, a filter-based estimator). It would name
   the source and its kind (odometry versus globally-consistent SLAM), not model
   the pipeline.
2. **REP-105 frame-convention alignment.** URML's `frames` block is self-declared
   today and does not pin to REP-105 names or assert an `odom` / `base_link`
   tree. A future Spec RFC could align the convention so an odometry estimate's
   frames bind cleanly to the manifest.
3. **Covariance / quality envelope threshold.** URML's safety envelope has no
   notion of estimate drift or quality. A future Spec RFC could add an optional
   covariance or quality threshold so a primitive is rejected when odometry
   confidence falls below a declared bound, which matters more for a drifting,
   non-loop-closing odometry source.

### Compatibility notes

- **Vendor org.** [`vectr-ucla`](https://github.com/vectr-ucla), the UCLA
  Verifiable and Control-Theoretic Robotics Laboratory (VECTR), United States.
- **Engagement repo.** [`vectr-ucla/direct_lidar_inertial_odometry`](https://github.com/vectr-ucla/direct_lidar_inertial_odometry),
  the direct LiDAR-inertial odometry pipeline.
- **Origin / policy.** United States (UCLA VECTR). Passes US-federal default
  policy (open-source academic odometry pipeline, no provenance gate at the
  estimator layer).
- **License fit.** Understood to be MIT; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** DLIO is one odometry source among several; the same
  URML primitives map to a deployment grounded by KISS-ICP
  ([RFC-0335](0335-kiss-icp-outreach.md)), GLIM
  ([RFC-0336](0336-glim-outreach.md)), robot_localization
  ([RFC-0332](0332-robot-localization-outreach.md)), or any runtime that
  publishes a pose, with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The localization / pose-source
  declaration, the REP-105 frame-convention alignment, and the covariance /
  quality envelope threshold are queued Spec RFCs.
- Reference runtime: no change in this RFC. A DLIO mapping would treat the
  odometry pose as the source that grounds the manifest's `odom` frame, against
  which a validated primitive's target is resolved; a planned
  `dlio_odometry_cell.yaml` fixture would document the pose-source binding.
- Conformance: no change. DLIO is Layer 0; URML never reaches into the
  extrinsics or the filter.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Pose-source field is not yet specified.** The cleanest manifest binding for
  DLIO (a declared odometry source) is a queued Spec RFC, not a shipped field, so
  the mapping describes a binding URML cannot yet express in a manifest.
- **Drift without global consistency.** A LiDAR-inertial odometry source drifts
  over distance and has no loop closure. URML can declare the source, but a
  faithful envelope treatment of drift depends on the queued quality-threshold
  Spec RFC, which does not exist yet.

## Alternatives considered

1. **Fold DLIO into one combined LiDAR-estimation RFC with KISS-ICP and GLIM.**
   Rejected. The three are different modalities (LiDAR-inertial odometry,
   LiDAR-only odometry, globally-consistent SLAM) with different communities and,
   likely, different licenses. A per-pipeline RFC lets each maintainer community
   thread its own conversation and lets URML ask each how its kind should be
   declared.
2. **Skip the pose-source mapping; let URML declare only sensors.** Rejected.
   Production deployments care which pipeline grounds their `odom` frame;
   declaring lidar and IMU but not the odometry source leaves the world model
   URML validates against unanchored.
3. **Model DLIO's IMU-LiDAR extrinsics and filter in the URML manifest.**
   Rejected. The extrinsics, the tight coupling, and the filter are Layer 0 /
   substrate config. URML declares capability and consumes the estimate;
   modelling the filter would fail the substrate-neutrality acid test and couple
   URML to one pipeline's internals.

## Prior art

- [RFC-0332 (robot_localization outreach)](0332-robot-localization-outreach.md):
  the Move #25 wave anchor; shares the pose-source role at the filter altitude.
- [RFC-0335 (KISS-ICP outreach)](0335-kiss-icp-outreach.md): sibling Move #25
  LiDAR-only odometry; the closest neighbor without the inertial side.
- [RFC-0336 (GLIM outreach)](0336-glim-outreach.md): sibling Move #25
  globally-consistent SLAM; the contrast to DLIO's drifting odometry.
- Move #16 SLAM RFCs, the round-one lineage this wave extends:
  [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md).
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the
  frame-tree spec surface an odometry estimate binds to.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  how URML reasons about the transport an estimate is published over.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  compatible-runtimes registry referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the DLIO maintainers:

1. **Frame / pose-source alignment.** Is "DLIO produces the odometry estimate,
   URML declares its `frames` and `declared_locations` against that estimate and
   validates above it" the right boundary, with URML staying entirely out of the
   extrinsics and the filter?
2. **Declaring a LiDAR-inertial odometry source.** How should URML declare DLIO
   as a pose source: as an odometry kind (locally accurate, drifting, no global
   consistency), distinct from a globally-consistent SLAM source? What
   characteristics should the declaration carry?
3. **REP-105 frame conventions.** Does DLIO always publish over the REP-105
   `odom` / `base_link` tree, or are there configurations where URML should not
   assume those names?
4. **Drift / quality as an envelope input.** Is DLIO's estimate quality a useful
   admission threshold for URML (reject a `move_to` when odometry confidence has
   drifted below a declared bound), or is that the wrong altitude for a static
   check on a pure-odometry source?
5. **License.** What is the current license of `direct_lidar_inertial_odometry`
   (the GitHub API did not surface an SPDX id at verification time; understood to
   be MIT)?
6. **Conformance listing.** Would the DLIO project consider a project link to
   URML's compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0340 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`vectr-ucla/direct_lidar_inertial_odometry`](https://github.com/vectr-ucla/direct_lidar_inertial_odometry)
pointing at this RFC (Discussions are disabled on the repo), with the
state-estimation / pose-source framing explicit. If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 994 stars, not archived, Issues enabled,
      Discussions disabled, last push 2026-04-03).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, unspecified pose-source field, drift without
      global consistency).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (UCLA VECTR); default policy passes at the estimator layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; DLIO is one odometry
      source among many, URML consumes the estimate and never reaches into the
      extrinsics or filter).
