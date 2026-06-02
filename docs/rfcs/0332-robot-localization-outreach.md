---
rfc: 0332
title: robot_localization (ROS state-estimation / sensor fusion) integration, request for comment from the robot_localization maintainers
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

# RFC-0332: robot_localization integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's package, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM upstreams. This RFC is the wave anchor. It reaches
[`cra-ros-pkg/robot_localization`](https://github.com/cra-ros-pkg/robot_localization),
the canonical ROS EKF / UKF sensor-fusion and state-estimation package, and
**requests review and feedback from the robot_localization maintainers**.

robot_localization produces the fused pose estimate and the map -> odom ->
base_link transforms (following REP-105) that URML's `frames` and
`declared_locations` are expressed against. URML does not perform estimation. It
declares the localization source and its frames, consumes the resulting
estimate, and statically validates intent against that world model before
dispatch.

URML composes **above** robot_localization: a fused estimate grounds the world
model -> URML validates an English-derived primitive against the declared frames
and the active safety envelope -> a validated primitive dispatches. The
differentiator is static validation against the declared world model and the
envelope before motion, complementary to the runtime estimate the package keeps
producing.

## Motivation

robot_localization is the default ROS answer to "where is the robot," and its
output is exactly the frame and pose surface URML declares over:

1. **It produces the frames URML declares over.** URML's Layer-1 manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares
   `frames` (REP-105: map, odom, base_link) and `declared_locations` (poses in a
   named frame). robot_localization is what fills those frames with a live
   estimate and broadcasts the transforms between them. The manifest declares the
   contract; the package satisfies it.
2. **It is a pose source, not an intent layer.** A fused EKF / UKF estimate
   answers where the robot is. URML's contribution sits one layer up: given that
   estimate, does the declared capability and the safety envelope admit the
   requested `move_to`, `dock`, or `scan` before the robot moves. The two are
   complementary, not competing.
3. **It exercises the frame graph.** URML's frame-transform graph
   ([RFC-0290](0290-frame-transform-graph.md)) reasons over the same map / odom /
   base_link relationships robot_localization maintains. Aligning the convention
   keeps a `declared_location` in `map` resolvable against the estimate the
   package fuses.
4. **It grounds substrate-neutrality.** The localization-source idea must hold on
   a runtime with zero ROS dependency. robot_localization is the ROS instance of
   a pose source; the same manifest declaration must map onto a PX4 estimator or
   a vendor SDK's localization output with no change to the URML program.

Repo at [`cra-ros-pkg/robot_localization`](https://github.com/cra-ros-pkg/robot_localization)
(about 1,899 stars, Issues enabled, Discussions disabled, not archived, last push
2026-04-30, active). Maintained by Tom Moore and the ROS community. License is
asked as a question below (the GitHub API did not surface an SPDX id at
verification time; understood to be BSD). Origin: community / ROS ecosystem
(international); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `robot_localization_cell.yaml` fixture)

| URML field | Maps to robot_localization concept |
|---|---|
| `robot_id`, `description` | Robot identity (carried at the manifest envelope; not a robot_localization concept) |
| `frames` (map, odom, base_link) | The REP-105 frames robot_localization broadcasts: the world frame, the continuous odom frame, and the robot body frame |
| `frames[].parent` | The transform tree edges (map -> odom -> base_link) the fused estimate maintains |
| `declared_locations` (pose in a frame) | Named target poses a `move_to` resolves against, expressed in the frame robot_localization estimates |
| `mobility.drive_type` / `max_velocity` | The platform whose motion the filter fuses; URML bounds checked against the envelope before dispatch |
| `perception.sensors[].measurement_type` | The sensor streams feeding the filter (odometry, IMU, GPS), declared at a coarse altitude as manifest inputs |
| `connectivity.links` | The link roles a remote estimate or correction stream may ride ([RFC-0006](0006-connectivity-and-link-loss.md)) |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins with platform limits before a primitive dispatches; estimate quality is a candidate envelope input (queued, below) |

### What URML v0.1 does not yet express for robot_localization

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML's manifest names `frames` but
   does not declare which source produces the estimate those frames carry. A
   future Spec RFC could add an optional pose-source declaration so the manifest
   records that a deployment's frames are grounded by a named state estimator.
2. **REP-105 frame-convention alignment.** URML declares frames freely; it does
   not pin the map / odom / base_link convention normatively. A future Spec RFC
   could align the frame block with REP-105 so a declared frame name carries its
   conventional meaning.
3. **Covariance / quality threshold for the envelope.** A fused estimate carries
   a covariance. URML's safety envelope has no notion of estimate quality. A
   future Spec RFC could add an optional covariance or quality threshold so the
   envelope can refuse a primitive when localization confidence is below a floor.

### Compatibility notes

- **Vendor org.** [`cra-ros-pkg`](https://github.com/cra-ros-pkg) (Charles River
  Analytics and the ROS community).
- **Engagement repo.** [`cra-ros-pkg/robot_localization`](https://github.com/cra-ros-pkg/robot_localization),
  the EKF / UKF sensor-fusion and state-estimation package.
- **Origin / policy.** International (community / ROS ecosystem). Treated as INTL;
  passes US-federal default policy (open-source package, no provenance gate at the
  estimation layer).
- **License fit.** Understood to be BSD; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** robot_localization is the ROS instance of a pose
  source; the same URML frame and localization-source declaration maps onto a PX4
  estimator, a vendor SDK, or a zero-ROS runtime with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The pose-source declaration, the
  REP-105 alignment, and the covariance / quality threshold are queued Spec RFCs.
- Reference runtime: no change. A robot_localization mapping would read the fused
  pose and transforms to resolve `declared_locations` and validate `move_to`
  before dispatch; the planned `robot_localization_cell.yaml` fixture would
  document the frame and pose-source surface.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Read-side fit.** URML consumes the estimate; it does not improve it.
  robot_localization gains a downstream consumer that validates intent against
  its output, not a new estimation capability. The engagement is honest about
  that asymmetry.
- **Convention dependency.** The mapping leans on REP-105 frame names. A
  deployment that uses non-standard frame names weakens the alignment until the
  queued frame-convention Spec RFC lands.

## Alternatives considered

1. **Model the estimator internals in the URML manifest.** Rejected. The filter
   states, the sensor-fusion graph, and the covariance propagation are Layer 0 /
   substrate concern. URML declares the frames and the pose-source contract, not
   the estimator's internals. Reaching inside would fail the substrate-neutrality
   acid test.
2. **Declare the raw sensor streams as full perception entries.** Rejected as the
   anchor. The filter inputs (odometry, IMU, GPS) are upstream of URML's
   altitude; declaring them at a coarse level as manifest inputs is enough, and a
   full perception model would couple URML to one fusion topology.
3. **Skip state estimation and assume a ground-truth pose.** Rejected. A real
   deployment has no ground truth; the pose is an estimate with a covariance.
   Pretending otherwise would make the safety envelope dishonest, which is the
   opposite of URML's validate-before-you-move promise.

## Prior art

- [RFC-0290 (frame-transform graph)](0290-frame-transform-graph.md): URML's frame
  graph, the spec surface this engagement grounds.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link roles a remote estimate or correction stream may ride.
- Move #16 SLAM upstreams this round extends: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md).
- Sibling Move #25 RFCs: RFC-0333 (GTSAM), RFC-0334 (OpenVINS), RFC-0335
  (KISS-ICP), RFC-0337 (OctoMap), RFC-0338 (Ceres Solver), RFC-0339 (fuse).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, where `frames` and `declared_locations` live.

## Unresolved questions

For the robot_localization maintainers:

1. **Frame-convention alignment.** Is aligning URML's `frames` block to REP-105
   (map, odom, base_link) the right contract, so a declared frame name carries its
   conventional meaning against the transforms robot_localization broadcasts?
2. **Pose-source declaration.** Is declaring the localization source in the URML
   manifest (a named state estimator that grounds the frames) a useful and
   correct boundary, or is a frame declaration alone enough?
3. **Covariance as an envelope input.** Is the fused estimate's covariance a
   useful safety-envelope input, so URML can refuse a `move_to` when localization
   confidence is below a floor? Is there a conventional quality metric to read?
4. **Read-side boundary.** Is "URML consumes the estimate and transforms,
   validates intent, then dispatches" the right seam, with URML staying entirely
   above the filter and never reaching into estimator state?
5. **License.** What is the current license of robot_localization (the GitHub API
   did not surface an SPDX id at verification time; understood to be BSD)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0332 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`cra-ros-pkg/robot_localization`](https://github.com/cra-ros-pkg/robot_localization)
pointing at this RFC (Discussions are disabled on the repo). If the maintainers
prefer another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 1,899 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-04-30).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, read-side fit, convention dependency).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international community / ROS ecosystem; default policy passes
      at the estimation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; robot_localization is
      the ROS instance of a pose source, the same declaration maps onto a zero-ROS
      runtime, composed-above not assumed).
