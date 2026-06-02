---
rfc: 0334
title: OpenVINS (visual-inertial odometry / state estimation) integration, request for comment from the OpenVINS maintainers
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

# RFC-0334: OpenVINS integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's estimator, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round 2, extending the Move
#16 SLAM batch. This RFC reaches
[`rpng/open_vins`](https://github.com/rpng/open_vins), an MSCKF-based
visual-inertial estimator from the University of Delaware Robot Perception and
Navigation Group, and **requests review and feedback from the OpenVINS
maintainers**.

URML's Layer-1 capability manifest declares `frames` (ROS REP-105: `map`,
`odom`, `base_link`) and `declared_locations` (poses in a named frame). A
visual-inertial estimator like OpenVINS produces the pose, transform, and
trajectory those frames are expressed against. URML does not perform
visual-inertial odometry. It consumes the estimate and statically validates
intent against the resulting world model before dispatch. The differentiator is
**static validation against the capability manifest and the active safety
envelope before a single primitive is dispatched**.

URML composes **above** OpenVINS: the estimator emits a VIO pose in a published
frame, URML declares that pose source as a manifest input and resolves
`move_to`, `detect`, `scan`, `measure`, and `report` against the world model
the estimate grounds. The camera-IMU calibration and the filter internals are
substrate configuration (Layer 0); URML never reaches into them.

## Motivation

OpenVINS is a widely cited, filter-based visual-inertial estimator, and a state
estimator is precisely the substrate that grounds the frames URML declares
intent against:

1. **It produces what URML's `frames` are expressed against.** URML's Layer-1
   manifest ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
   declares coordinate frames and named locations. OpenVINS produces the
   `odom -> base_link` (and onward `map`) pose estimate those frames resolve to
   at runtime. The manifest and the estimator describe the same world model from
   two sides.
2. **The pose source is a missing manifest input.** URML declares sensors,
   cameras, and frames, but it does not declare which estimator produces the
   pose its frames track. Naming the pose source is the gap this engagement
   surfaces, shared across the whole Move #25 wave.
3. **Covariance is a candidate envelope input.** OpenVINS publishes a state
   covariance with its pose. URML's safety envelope is evaluated statically
   before dispatch; a localization-quality threshold (covariance trace, or a
   filter-health flag) is a natural candidate envelope input, so a `move_to` is
   admitted only when the estimate is trustworthy.
4. **It grounds substrate-neutrality.** A frame mapping that works against
   OpenVINS must also work against robot_localization (RFC-0332), KISS-ICP
   (RFC-0335), GLIM (RFC-0336), or the Move #16 SLAM upstreams. The estimator is
   one pose source among many; the same primitive runs unchanged on each.

Repo at [`rpng/open_vins`](https://github.com/rpng/open_vins) (about 2,922
stars, Issues enabled, Discussions disabled, not archived, last push
2025-11-30, reasonably recent). License is asked as a question below (the GitHub
API did not surface an SPDX id at verification time; OpenVINS is understood to
be GPL-3.0, which is treated explicitly under license fit). Origin: University
of Delaware Robot Perception and Navigation Group (United States).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `openvins_vio_cell.yaml` fixture)

| URML field | Maps to OpenVINS attribute |
|---|---|
| `robot_id`, `description` | The estimated body's identity (carried at the manifest envelope) |
| `frames{name, parent}` | REP-105 frame tree (`map` -> `odom` -> `base_link`); the published frame OpenVINS produces the transform for |
| `declared_locations{name, pose, frame}` | Named poses resolved in the frame OpenVINS grounds; the estimate is what makes a named location addressable at runtime |
| `perception.cameras[]` | The camera(s) feeding the visual front-end (declared capability; calibration is Layer 0) |
| `perception.sensors[{measurement_type}]` | The IMU and camera measurement streams the filter fuses (declared as capability, not configured by URML) |
| Pose source (candidate manifest input) | OpenVINS named as the estimator producing the `odom -> base_link` pose URML's frames track |
| Estimate covariance / filter health (candidate envelope input) | State covariance trace or health flag as a localization-quality threshold checked statically before a `move_to` |
| Safety envelope limits (Pass 3) | Conjoined with the estimate-quality threshold; URML applies strictest-wins before dispatch |

### What URML v0.1 does not yet express for OpenVINS

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML's manifest declares sensors
   and frames but not which estimator produces the pose its frames track. A
   future Spec RFC could add an optional pose-source declaration so a manifest
   records OpenVINS (or any estimator) as the localization input.
2. **REP-105 frame-convention alignment.** URML declares `frames{name, parent}`
   but does not yet pin them to REP-105 semantics (`map`, `odom`, `base_link`
   roles). A future Spec RFC could align the frame convention so a `map`-frame
   pose and an `odom`-frame pose are distinguishable in the manifest.
3. **Covariance / quality envelope threshold.** URML's envelope has no
   localization-quality input. A future Spec RFC could add an optional
   covariance or estimate-health threshold so motion is gated on a trustworthy
   estimate.

### Compatibility notes

- **Vendor org.** [`rpng`](https://github.com/rpng) (University of Delaware
  Robot Perception and Navigation Group).
- **Engagement repo.** [`rpng/open_vins`](https://github.com/rpng/open_vins):
  MSCKF-based visual-inertial estimator; Issues enabled, Discussions disabled,
  not archived, last push 2025-11-30.
- **Origin / policy.** United States (University of Delaware). Passes US-federal
  default policy (open-source academic estimator, no provenance gate at the
  estimation layer).
- **License fit.** Understood to be GPL-3.0. URML stays Apache-2.0. The
  relationship is **runtime consumption and cross-citation, not code
  vendoring**: URML consumes the estimate OpenVINS publishes at runtime and
  cross-cites the project, and it does not vendor or link OpenVINS source into
  the Apache-2.0 core. The copyleft boundary is flagged explicitly and confirmed
  as a question below.
- **Substrate-neutrality.** OpenVINS is one pose source among many; the same
  URML frames and primitives map to robot_localization, KISS-ICP, GLIM, or the
  Move #16 SLAM upstreams with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The pose-source declaration, the
  REP-105 frame-convention alignment, and the covariance / quality envelope
  threshold are queued Spec RFCs.
- Reference runtime: no change in this RFC. A mapping would consume the OpenVINS
  pose at runtime and resolve a validated primitive's goal against the grounded
  world model; the planned `openvins_vio_cell.yaml` fixture would document the
  frame and pose-source manifest, not vendor estimator code.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Copyleft boundary to keep clean.** OpenVINS is understood to be GPL-3.0 and
  URML is Apache-2.0. The engagement is consume-at-runtime and cross-cite only;
  any future adapter must respect that boundary, and the mapping is documented
  at the published-estimate altitude to avoid touching estimator internals.
- **Consumer-shaped fit.** URML benefits from naming a trusted pose source more
  than OpenVINS benefits from being named. The engagement is honest about that
  asymmetry.

## Alternatives considered

1. **Treat the pose source as opaque and skip declaring it.** Rejected. A
   manifest that declares frames but not the estimator producing them is
   incomplete; a downstream consumer cannot reason about localization trust
   without knowing the source.
2. **Model OpenVINS filter internals (state vector, feature tracks) in the
   manifest.** Rejected. The filter and the camera-IMU calibration are Layer 0
   substrate concern; modelling them would fail the substrate-neutrality acid
   test and could not map onto a non-filter estimator.
3. **Bundle every Move #25 estimator into one SLAM-substrate RFC.** Rejected.
   Different licenses (GPL-3.0 here versus permissive elsewhere), different
   communities, and different estimation modalities (filter-based VIO versus
   lidar odometry versus EKF fusion) mean per-target RFCs let each conversation
   thread cleanly.

## Prior art

- [RFC-0205 (Cartographer outreach)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3 outreach)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map outreach)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md): the Move
  #16 SLAM batch this wave extends.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the
  frame-graph surface this engagement exercises.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the envelope-input lineage a localization-quality threshold would extend.
- Sibling Move #25 RFCs: RFC-0332 (robot_localization, the wave anchor),
  RFC-0335 (KISS-ICP), RFC-0336 (GLIM).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the OpenVINS maintainers:

1. **Frame / pose-source alignment.** Is naming OpenVINS as the manifest pose
   source, and mapping URML's `frames{name, parent}` onto the published REP-105
   transform (`map` -> `odom` -> `base_link`), the right boundary?
2. **Published-estimate seam.** What is the right seam for "URML consumes the
   OpenVINS estimate": the published pose plus covariance topic, or a different
   interface you would point URML at?
3. **Covariance as an envelope input.** Is the published state covariance (or a
   filter-health flag) a useful localization-quality signal for URML to gate
   motion on, and what threshold shape would you consider meaningful?
4. **GPL-3.0 boundary.** Does runtime consumption of the OpenVINS estimate plus
   cross-citation, with no vendoring of OpenVINS source into URML's Apache-2.0
   core, match your reading of the GPL-3.0 boundary?
5. **License.** What is the current license of `open_vins` (the GitHub API did
   not surface an SPDX id at verification time; understood to be GPL-3.0)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0334 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`rpng/open_vins`](https://github.com/rpng/open_vins) pointing at this RFC
(Discussions are disabled on the repo). If the maintainers prefer another
channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 2,922 stars, not archived, Issues
      enabled, Discussions disabled, last push 2025-11-30).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, copyleft boundary, consumer-shaped fit).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (University of Delaware); default policy passes at the
      estimation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; OpenVINS is one pose
      source among many, the estimate is consumed at runtime not vendored,
      composed-above not assumed).
