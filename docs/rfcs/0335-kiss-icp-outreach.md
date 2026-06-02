---
rfc: 0335
title: KISS-ICP (LiDAR odometry) integration, request for comment from the KISS-ICP maintainers
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

# RFC-0335: KISS-ICP (LiDAR odometry) integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's pipeline, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. This RFC reaches
[`PRBonn/kiss-icp`](https://github.com/PRBonn/kiss-icp), a deliberately minimal
point-to-point ICP LiDAR odometry pipeline from the University of Bonn
Photogrammetry and Robotics group. It **requests review and feedback from the
KISS-ICP maintainers**.

KISS-ICP produces an odometry pose estimate. URML's Layer-1 manifest declares
`frames` (ROS REP-105: `map`, `odom`, `base_link`) and `declared_locations`
(poses in a named frame). KISS-ICP is one of the substrates that produces the
`odom` frame those poses can be expressed against. URML does not perform
odometry or SLAM. It **consumes** the estimate and statically validates intent
against the resulting world model **before dispatch**.

URML composes **above** KISS-ICP: the estimator output (a pose against `odom`)
is a manifest input; the URML validator checks a program against the declared
capability and the active safety envelope; only then does a primitive dispatch.
The honest nuance is stated up front: KISS-ICP is pure-LiDAR, odometry-only, no
IMU and no loop closure, so URML declares a LiDAR-only localization source with
drift characteristics, not a globally-consistent map.

## Motivation

KISS-ICP is the reference point for "keep it simple" LiDAR odometry, and a clean
odometry source is exactly what grounds URML's `odom` frame:

1. **It produces the pose URML's `odom` frame is expressed against.** URML's
   `frames` block declares REP-105 frames and `declared_locations` are poses in
   a named frame ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)).
   KISS-ICP estimates the `base_link` pose in `odom`. The estimator and the
   manifest describe the same world model from two sides.
2. **Odometry-only is an honest, declarable altitude.** KISS-ICP has no IMU
   fusion and no loop closure, so the estimate drifts over distance. That is not
   a flaw to hide. It is a localization-source property URML should be able to
   declare, so the validator and the operator reason about a drifting
   LiDAR-only source rather than assuming a globally-consistent map.
3. **It is where consume-before-dispatch is cheap to show.** URML's
   contribution sits one layer up and earlier: a static check, before the first
   primitive dispatches, that the declared capability and the safety envelope
   admit the requested intent against the current estimate.
4. **It grounds substrate-neutrality.** A localization source declared from
   KISS-ICP must declare the same way from a full SLAM stack. KISS-ICP is one
   estimator among many; the acid test is that the same `frames` and
   `declared_locations` bind against any of them with no program change.

Repo at [`PRBonn/kiss-icp`](https://github.com/PRBonn/kiss-icp) (about 2,205
stars, Issues **and** Discussions enabled, not archived, last push 2026-05-14,
active). License is asked as a question below (the GitHub API did not surface an
SPDX id at verification time; understood to be MIT). Origin: University of Bonn
Photogrammetry and Robotics (PRBonn, Cyrill Stachniss lab), Germany; NATO-allied,
passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `kiss_icp_odometry_cell.yaml` fixture)

| URML field | Maps to KISS-ICP output |
|---|---|
| `robot_id`, `description` | Deployment identity (not a KISS-ICP concept; carried at the manifest envelope) |
| `frames` (`name`, `parent`) | REP-105 frame tree; KISS-ICP estimates `base_link` -> `odom` (the `odom` frame node URML declares) |
| `declared_locations` (`name`, `pose`, `frame`) | Named poses expressed against the `odom` frame the odometry produces |
| `perception.sensors[].measurement_type: point_cloud` | The LiDAR scan KISS-ICP registers point-to-point to produce the odometry estimate |
| `connectivity` | The link roles a pose / estimate stream is carried over (RFC-0006), relevant when the estimator runs off-body |
| Localization source (queued, see below) | A LiDAR-only odometry source with drift characteristics, declared as a manifest input |
| Estimate covariance / quality (queued, see below) | A candidate safety-envelope threshold input from the estimator's reported uncertainty |
| Primitives (`move_to`, `scan`, `detect`, `measure`, `report`) | Resolve against `declared_locations` in the estimated `odom` frame; validated before dispatch |

### What URML v0.1 does not yet express for KISS-ICP

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML declares sensors but not
   that a named substrate produces the pose its `frames` are expressed against,
   nor whether that source is odometry-only or full SLAM. A future Spec RFC
   could add an optional localization-source declaration so the manifest records
   a LiDAR-only odometry source distinct from a globally-consistent SLAM source.
2. **REP-105 frame-convention alignment.** URML's `frames` are self-declared
   identifiers. A future Spec RFC could align them explicitly with REP-105
   (`map` / `odom` / `base_link`) so the estimator output frame and the manifest
   frame bind without ad-hoc naming.
3. **Covariance / quality envelope threshold.** KISS-ICP can report estimate
   uncertainty. A future Spec RFC could add an optional safety-envelope
   threshold on estimate covariance or quality, so a primitive is rejected when
   the localization estimate is too degraded to act on.

### Compatibility notes

- **Vendor org.** [`PRBonn`](https://github.com/PRBonn), the University of Bonn
  Photogrammetry and Robotics group (Cyrill Stachniss lab).
- **Engagement repo.** [`PRBonn/kiss-icp`](https://github.com/PRBonn/kiss-icp),
  a minimal point-to-point ICP LiDAR odometry pipeline; active.
- **Origin / policy.** Germany (academic). NATO-allied; passes US-federal
  default policy (open-source estimator, no provenance gate at the
  state-estimation layer).
- **License fit.** Understood to be MIT; not SPDX-detected at verification time,
  so asked below as a question.
- **Substrate-neutrality.** KISS-ICP is one estimator among many. The same
  `frames` and `declared_locations` bind against a full SLAM stack (RFC-0336
  GLIM, the Move #16 SLAM RFCs) or a fused estimator (RFC-0332 robot_localization,
  RFC-0334 OpenVINS) with no program change. URML never reaches into the
  estimator's internals (Layer 0).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The localization / pose-source
  declaration, the REP-105 frame-convention alignment, and the covariance /
  quality envelope threshold are queued Spec RFCs.
- Reference runtime: no change in this RFC. A KISS-ICP mapping would read the
  odometry pose into the `odom` frame URML's manifest declares; the planned
  `kiss_icp_odometry_cell.yaml` fixture would document the LiDAR-only,
  odometry-only manifest honestly, drift characteristics declared rather than
  papered over.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Odometry-only altitude.** KISS-ICP produces a drifting LiDAR-only estimate,
  not a globally-consistent map. URML can declare it honestly, but the demo it
  grounds is short-horizon localization, not long-horizon mapped navigation.
- **Frame-convention assumption.** The mapping assumes REP-105 frames. A
  deployment that names frames differently needs the queued alignment RFC before
  the binding is clean.

## Alternatives considered

1. **Skip odometry-only sources and engage full SLAM stacks only.** Rejected.
   Odometry-only is a real and common deployment altitude. Declaring it honestly
   (drift characteristics included) is exactly the boundary URML should make
   explicit, not hide behind a SLAM assumption.
2. **Model the ICP registration internals in the URML manifest.** Rejected. The
   point cloud registration and the local map are Layer 0 / substrate concern.
   URML declares the consumed estimate and the frames it is expressed against,
   not how the estimator computes them. Modelling the internals would fail the
   substrate-neutrality acid test.
3. **Declare a single generic "SLAM source" with no odometry-vs-SLAM
   distinction.** Rejected. Collapsing odometry-only and globally-consistent
   SLAM into one field would let a manifest claim a consistency the estimator
   does not provide. The queued localization-source RFC keeps the distinction
   (contrast RFC-0336 GLIM, globally-consistent).

## Prior art

- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  and transform reasoning this engagement consumes a pose against.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-role surface a remote estimate stream is carried over.
- Move #16 SLAM RFCs: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md): the round-one SLAM
  substrates this wave extends.
- Sibling Move #25 RFCs: RFC-0332 (robot_localization, the wave anchor),
  RFC-0334 (OpenVINS), RFC-0336 (GLIM), RFC-0337 (OctoMap), RFC-0340 (DLIO).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing and honest-substrate-limit norm this RFC applies.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the KISS-ICP maintainers:

1. **Frame / pose-source alignment.** KISS-ICP estimates `base_link` -> `odom`.
   Is matching that to URML's `frames` (REP-105 `odom`) and expressing
   `declared_locations` against it the right alignment, or is there a different
   frame convention URML should read?
2. **LiDAR-only localization-source declaration.** What is the right way for
   URML to declare a LiDAR-only, odometry-only source (with its drift
   characteristics) as distinct from a full SLAM source? Is "odometry-only,
   no loop closure" the honest label you would want surfaced?
3. **Estimate quality / covariance.** Does KISS-ICP report a usable estimate
   covariance or quality signal that URML could read as a safety-envelope
   threshold input, so a primitive is rejected when localization is too degraded?
4. **Consume-not-control boundary.** Is "URML consumes the odometry estimate and
   stays entirely above the pipeline" the right boundary, with URML never
   reaching into the registration internals?
5. **License.** What is the current license of `kiss-icp` (the GitHub API did
   not surface an SPDX id at verification time; understood to be MIT)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0335 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`PRBonn/kiss-icp`](https://github.com/PRBonn/kiss-icp) pointing at this RFC (the
repo has both enabled). If the maintainers prefer another channel, URML will move
the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 2,205 stars, not archived, Issues and
      Discussions enabled, last push 2026-05-14).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, odometry-only altitude, frame-convention
      assumption).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Germany (academic, PRBonn); NATO-allied, default policy passes
      at the state-estimation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; KISS-ICP is one
      estimator among many, URML consumes the estimate and never reaches into
      Layer 0).
