---
rfc: 0341
title: Kimera (metric-semantic visual-inertial SLAM) integration, request for comment from the MIT SPARK maintainers
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

# RFC-0341: Kimera integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's estimator, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round 2, extending the Move
#16 SLAM batch. This RFC reaches
[`MIT-SPARK/Kimera-VIO`](https://github.com/MIT-SPARK/Kimera-VIO), a
metric-semantic visual-inertial SLAM stack from the MIT SPARK Lab (Luca
Carlone), and **requests review and feedback from the MIT SPARK maintainers**.

URML's Layer-1 capability manifest declares `frames` (ROS REP-105: `map`,
`odom`, `base_link`), `declared_locations` (poses in a named frame), and a
perception `object_vocabulary`. Kimera produces both a VIO pose estimate and a
metric-semantic mesh. URML does not perform SLAM. It consumes the estimate and
statically validates intent against the resulting world model before dispatch.
The differentiator is **static validation against the capability manifest and
the active safety envelope before a single primitive is dispatched**.

Kimera offers two alignment surfaces. The first is the same as the rest of the
wave: the VIO pose grounds the frames URML's intent is expressed against. The
second is more speculative: Kimera's per-element semantic labels could align
with URML's perception `object_vocabulary`, and a semantic place could become a
named `declared_location`. This RFC is honest that the second surface is the
more uncertain of the two.

## Motivation

Kimera is a real-time metric-semantic VIO and SLAM stack, and a state estimator
is precisely the substrate that grounds the frames URML declares intent against:

1. **It produces what URML's `frames` are expressed against.** URML's Layer-1
   manifest ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
   declares coordinate frames and named locations. Kimera's VIO produces the
   `odom -> base_link` (and onward `map`) pose those frames resolve to at
   runtime. The manifest and the estimator describe the same world model from
   two sides.
2. **The pose source is a missing manifest input.** URML declares sensors,
   cameras, and frames, but not which estimator produces the pose its frames
   track. Naming the pose source is the gap this engagement surfaces, shared
   across the whole Move #25 wave.
3. **The semantic mesh is a second, more speculative surface.** Kimera attaches
   semantic labels to mesh elements. URML's perception `object_vocabulary` is
   the set of class Identifiers `detect.object` may name, and a `declared_location`
   is a named pose. A labelled semantic place could in principle become a named
   location, and Kimera's label set could inform `object_vocabulary`. This is
   the less certain of the two alignments and is raised as a question, not a
   claim.
4. **It grounds substrate-neutrality.** A frame mapping that works against
   Kimera must also work against robot_localization (RFC-0332), KISS-ICP
   (RFC-0335), GLIM (RFC-0336), or the Move #16 SLAM upstreams. The estimator is
   one pose source among many; the same primitive runs unchanged on each.

Repo at [`MIT-SPARK/Kimera-VIO`](https://github.com/MIT-SPARK/Kimera-VIO) (about
1,870 stars, Issues enabled, Discussions disabled, not archived, last push
2025-03-01, mildly stale at roughly 14 months). License is asked as a question
below (the GitHub API did not surface an SPDX id at verification time;
understood to be BSD). Origin: MIT SPARK Lab (United States).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `kimera_vio_cell.yaml` fixture)

| URML field | Maps to Kimera attribute |
|---|---|
| `robot_id`, `description` | The estimated body's identity (carried at the manifest envelope) |
| `frames{name, parent}` | REP-105 frame tree (`map` -> `odom` -> `base_link`); the published frame Kimera's VIO produces the transform for |
| `declared_locations{name, pose, frame}` | Named poses resolved in the frame Kimera grounds; a Kimera semantic place is a candidate source for a named location (speculative, see gaps) |
| `perception.cameras[]` | The stereo / mono camera(s) feeding the visual front-end (declared capability; calibration is Layer 0) |
| `perception.sensors[{measurement_type}]` | The IMU and camera measurement streams Kimera fuses (declared as capability, not configured by URML) |
| `perception.object_vocabulary` | Kimera's per-element semantic label set as a candidate source for the class Identifiers `detect.object` draws from (speculative, see gaps) |
| Pose source (candidate manifest input) | Kimera named as the estimator producing the `odom -> base_link` pose URML's frames track |
| Estimate quality (candidate envelope input) | A VIO health or covariance signal as a localization-quality threshold checked statically before a `move_to` |
| Safety envelope limits (Pass 3) | Conjoined with the estimate-quality threshold; URML applies strictest-wins before dispatch |

### What URML v0.1 does not yet express for Kimera

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Localization / pose-source declaration.** URML's manifest declares sensors
   and frames but not which estimator produces the pose its frames track. A
   future Spec RFC could add an optional pose-source declaration so a manifest
   records Kimera (or any estimator) as the localization input.
2. **REP-105 frame-convention alignment.** URML declares `frames{name, parent}`
   but does not yet pin them to REP-105 semantics (`map`, `odom`, `base_link`
   roles). A future Spec RFC could align the frame convention so a `map`-frame
   pose and an `odom`-frame pose are distinguishable in the manifest.
3. **Covariance / quality envelope threshold.** URML's envelope has no
   localization-quality input. A future Spec RFC could add an optional
   covariance or estimate-health threshold so motion is gated on a trustworthy
   estimate.
4. **Semantic-label binding.** URML has no mechanism to populate
   `object_vocabulary` or derive a `declared_location` from an estimator's
   semantic output. A future Spec RFC could explore binding a metric-semantic
   label set to the perception vocabulary and named locations. This is the most
   speculative gap and is explicitly out of scope for this RFC.

### Compatibility notes

- **Vendor org.** [`MIT-SPARK`](https://github.com/MIT-SPARK) (MIT SPARK Lab,
  Luca Carlone).
- **Engagement repo.** [`MIT-SPARK/Kimera-VIO`](https://github.com/MIT-SPARK/Kimera-VIO):
  metric-semantic visual-inertial SLAM; Issues enabled, Discussions disabled,
  not archived, last push 2025-03-01 (mildly stale at roughly 14 months).
- **Origin / policy.** United States (MIT SPARK Lab). Passes US-federal default
  policy (open-source academic estimator, no provenance gate at the estimation
  layer).
- **License fit.** Understood to be BSD; not SPDX-detected at verification time,
  so asked below as a question. A BSD estimator is a clean fit with URML's
  Apache-2.0 core; the relationship is runtime consumption and cross-citation.
- **Substrate-neutrality.** Kimera is one pose source among many; the same URML
  frames and primitives map to robot_localization, KISS-ICP, GLIM, OpenVINS
  ([RFC-0334](0334-openvins-outreach.md)), or the Move #16 SLAM upstreams with
  no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The pose-source declaration, the
  REP-105 frame-convention alignment, the covariance / quality envelope
  threshold, and the semantic-label binding are queued Spec RFCs.
- Reference runtime: no change in this RFC. A mapping would consume the Kimera
  pose at runtime and resolve a validated primitive's goal against the grounded
  world model; the planned `kimera_vio_cell.yaml` fixture would document the
  frame and pose-source manifest, not vendor estimator code.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Speculative second surface.** The semantic-label alignment with
  `object_vocabulary` and `declared_locations` is the more uncertain of the two
  surfaces. It is raised as a question, and the pose-grounding surface stands on
  its own if the semantic one does not pan out.
- **Mild staleness.** The repo's last push was 2025-03-01, roughly 14 months
  back. The estimator is mature, but a slower cadence may mean a longer
  response, and the mapping is documented at the published-estimate altitude to
  stay robust to that.

## Alternatives considered

1. **Engage only on the pose surface and drop the semantic alignment.** Rejected
   as the default. The pose-grounding surface is the primary ask and stands
   alone, but Kimera's distinguishing feature is the metric-semantic mesh;
   naming the speculative second surface honestly is more useful than hiding it.
2. **Model Kimera's semantic mesh structure in the URML manifest.** Rejected.
   The mesh and the VIO internals are Layer 0 substrate concern; URML would at
   most consume a label set and named places, not model the mesh, which would
   fail the substrate-neutrality acid test.
3. **Bundle every Move #25 estimator into one SLAM-substrate RFC.** Rejected.
   Different licenses, different communities, and different estimation
   modalities (metric-semantic VIO here versus filter-based VIO, lidar odometry,
   or EKF fusion elsewhere) mean per-target RFCs let each conversation thread
   cleanly.

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
  RFC-0334 (OpenVINS), RFC-0335 (KISS-ICP), RFC-0336 (GLIM).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm referenced below.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames`, `declared_locations`, and
  `object_vocabulary` surfaces this engagement exercises.

## Unresolved questions

For the MIT SPARK maintainers:

1. **Frame / pose-source alignment.** Is naming Kimera as the manifest pose
   source, and mapping URML's `frames{name, parent}` onto the published REP-105
   transform (`map` -> `odom` -> `base_link`), the right boundary?
2. **Semantic-label alignment.** Could Kimera's per-element semantic labels
   inform URML's perception `object_vocabulary`, and could a Kimera semantic
   place become a named `declared_location`? Is this a real seam or out of scope
   for a first engagement?
3. **Estimate quality as an envelope input.** Is there a VIO health or
   covariance signal Kimera publishes that would be a useful localization-quality
   threshold for URML to gate motion on?
4. **Published-estimate seam.** What is the right seam for "URML consumes the
   Kimera estimate": the published pose and mesh topics, or a different
   interface you would point URML at?
5. **License.** What is the current license of `Kimera-VIO` (the GitHub API did
   not surface an SPDX id at verification time; understood to be BSD)?
6. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0341 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`MIT-SPARK/Kimera-VIO`](https://github.com/MIT-SPARK/Kimera-VIO) pointing at
this RFC (Discussions are disabled on the repo). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 1,870 stars, not archived, Issues
      enabled, Discussions disabled, last push 2025-03-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, speculative second surface, mild
      staleness).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (MIT SPARK Lab); default policy passes at the estimation
      layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Kimera is one pose
      source among many, the estimate is consumed at runtime, composed-above not
      assumed).
