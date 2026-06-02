---
rfc: 0337
title: OctoMap (3D occupancy mapping) integration, request for comment from the OctoMap maintainers
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

# RFC-0337: OctoMap integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's library, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #25 is URML's SLAM and state-estimation wave, round two, extending the
Move #16 SLAM batch. Most of this wave reaches pose and transform estimators.
This RFC reaches the **occupancy side** of the same world model:
[`OctoMap/octomap`](https://github.com/OctoMap/octomap), the canonical 3D
occupancy-grid (octree) map. It **requests review and feedback from the OctoMap
maintainers**.

URML does not perform mapping. It **consumes** an occupancy map and statically
validates that a requested motion stays in free space before dispatch. URML's
Layer-1 manifest declares `frames` (ROS REP-105: `map` / `odom` / `base_link`)
and `declared_locations` (poses in a named frame); a `move_to` resolves a goal
against those, and the validator's Pass 3 safety envelope reasons about
geofence and occupancy. OctoMap is the data structure that occupancy reasoning
checks against. URML composes **above** OctoMap: occupancy estimate -> URML
world model -> static validation of intent -> dispatch. URML never reaches into
substrate internals (Layer 0); it reads the produced map, it does not build it.

This is a different fit from the pose estimators elsewhere in the wave. OctoMap
is a **map representation**, not a pose source, so it is framed as the
occupancy and world-model side of the same boundary.

## Motivation

OctoMap is the most widely used 3D occupancy representation in robotics, and
occupancy is exactly what URML's free-space reasoning needs a source for:

1. **Occupancy is what Pass 3 reasons over.** URML's safety envelope reasons
   about geofence and occupancy before any actuator moves. Today that occupancy
   is an abstract input; OctoMap is the concrete structure a deployment would
   bind it to. A `move_to` goal that lands in occupied space is a program URML
   should reject statically, before dispatch.
2. **`declared_locations` are checked against a map.** A named pose is only
   reachable if the world model says the volume around it is free. OctoMap's
   octree is the natural source for that check, so `declared_locations` and the
   occupancy map describe the same world from two sides.
3. **It is the volume side of deconfliction.** URML's volume and occupancy
   deconfliction ([RFC-0291](0291-utm-strategic-deconfliction.md)) reasons about
   occupied and free volume. A 3D occupancy octree is the representation that
   reasoning consumes; OctoMap is the reference implementation of it.
4. **It grounds substrate-neutrality.** Occupancy consumed from OctoMap must
   map the same way to a costmap, a voxel grid, or a vendor world model. OctoMap
   is one occupancy source among several; the boundary holds if the same URML
   program validates against any of them.

Repo at [`OctoMap/octomap`](https://github.com/OctoMap/octomap) (about 2,307
stars, Issues enabled, Discussions disabled, not archived, last push
2026-02-08). License: the core `octomap` library is BSD; the `octovis`
visualizer is GPL. The split is asked below as a question. Origin: University of
Freiburg lineage (Armin Hornung and colleagues), Germany / community; treated as
allied, passes US-federal default policy (open-source library, no provenance
gate at the mapping layer).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `octomap_occupancy_cell.yaml` fixture)

| URML field | Maps to OctoMap attribute |
|---|---|
| `robot_id`, `description` | Deployment identity; carried at the manifest envelope |
| `frames` (`{name, parent}`, REP-105 `map` / `odom` / `base_link`) | The frame the octree is expressed in; the map frame URML's occupancy check reads against |
| `declared_locations` (`{name, pose, frame}`) | Named goal poses a `move_to` resolves, each checked for free space against the octree |
| `mobility` | The body whose footprint / volume the occupancy check is evaluated for |
| `connectivity` | The link role over which the map estimate reaches the validator (a candidate manifest input, queued below) |
| Safety envelope occupancy / geofence (Pass 3) | Conjoined with the OctoMap free / occupied state; URML rejects a `move_to` into occupied volume before dispatch |

### What URML v0.1 does not yet express for OctoMap

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Occupancy-map source declaration.** URML has no manifest field declaring
   that an occupancy map is the source of the free-space world the envelope
   checks against. A future Spec RFC could add an optional occupancy-source
   input so the validator knows which map produced the occupancy state.
2. **REP-105 frame-convention alignment.** URML declares `frames` with `name`
   and `parent` but does not pin the ROS REP-105 convention (`map` / `odom` /
   `base_link`) normatively. A future Spec RFC could align the frame convention
   so an OctoMap frame maps to a URML frame without ambiguity.
3. **Occupancy resolution / quality threshold.** OctoMap has an octree
   resolution and per-voxel occupancy probability. URML has no envelope input
   for a minimum resolution or an occupancy-confidence threshold. A future Spec
   RFC could add a quality threshold as a candidate envelope input.

### Compatibility notes

- **Vendor org.** [`OctoMap`](https://github.com/OctoMap), the University of
  Freiburg lineage (Armin Hornung and colleagues) and community.
- **Engagement repo.** [`OctoMap/octomap`](https://github.com/OctoMap/octomap),
  the 3D occupancy-grid (octree) mapping library.
- **Origin / policy.** Germany / community (allied). Passes US-federal default
  policy (open-source mapping library, no provenance gate at the mapping layer).
- **License fit.** The core `octomap` library is BSD; the `octovis` visualizer
  is GPL. URML's interest is the core BSD library (the map representation), not
  the GPL visualizer. The split is confirmed below as a question.
- **Substrate-neutrality.** OctoMap is one occupancy representation among
  several (costmaps, voxel grids, vendor world models); the same URML program
  validates against any occupancy source with no change.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The occupancy-source declaration, the
  REP-105 frame-convention alignment, and the occupancy quality threshold are
  queued Spec RFCs.
- Reference runtime: no change in this RFC. An OctoMap mapping would feed the
  octree's free / occupied state into the Pass 3 occupancy check; the planned
  `octomap_occupancy_cell.yaml` fixture would document that a `move_to` into
  occupied volume is rejected before dispatch.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Map-representation fit, not a pose source.** OctoMap supplies occupancy, not
  the pose the occupancy is expressed against. The full free-space check needs
  both a map (OctoMap) and a pose source (the estimators elsewhere in this
  wave). This RFC is honest that OctoMap covers one half of the world model.
- **License split.** The BSD core and the GPL visualizer mean URML must be
  precise about which component it consumes. The mapping reads the BSD library
  only, but the split needs confirmation so the boundary is not assumed wrong.

## Alternatives considered

1. **Treat occupancy as purely an envelope-time input and never name a source.**
   Rejected. Production deployments care which map produced the free-space
   estimate; leaving it unnamed makes the occupancy check unauditable.
2. **Model the octree contents in the URML manifest.** Rejected. The octree and
   its voxels are substrate / Layer 0 data; URML declares capability and named
   locations, not map contents. Modelling the octree would fail the
   substrate-neutrality acid test.
3. **Fold OctoMap into one of the pose-estimator RFCs in this wave.** Rejected.
   OctoMap is a map representation with a distinct community and a BSD / GPL
   license split, not a pose estimator. A separate thread keeps the occupancy
   conversation clean.

## Prior art

- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  URML's volume and occupancy deconfliction, the closest precedent for occupancy
  reasoning.
- Move #16 SLAM RFCs: [RFC-0205 (Cartographer)](0205-cartographer-outreach.md),
  [RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md),
  [RFC-0207 (RTAB-Map)](0207-rtabmap-outreach.md),
  [RFC-0211 (Stella VSLAM)](0211-stella-vslam-outreach.md): the round-one SLAM
  substrate engagements this wave extends.
- [RFC-0290 (frame transform graph)](0290-frame-transform-graph.md): the frame
  and transform surface OctoMap's map frame binds against.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-role surface over which a map estimate reaches the validator.
- Sibling Move #25 RFCs: RFC-0332 (robot_localization, the wave anchor),
  RFC-0333 (GTSAM), RFC-0336 (GLIM).
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing norm this engagement points at.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the `frames` and `declared_locations` surface this
  engagement exercises.

## Unresolved questions

For the OctoMap maintainers:

1. **Occupancy-map alignment.** Is matching URML's occupancy check against an
   OctoMap octree (free / occupied state) the right alignment, and at what octree
   resolution is that check meaningful for free-space validation?
2. **Frame conventions.** What frame is the octree expressed in, and does the ROS
   REP-105 convention (`map` / `odom` / `base_link`) map cleanly onto URML's
   declared `frames` for an OctoMap deployment?
3. **World-model boundary.** Is "URML reads the produced occupancy map and
   validates intent above it" the right boundary, with URML staying entirely out
   of map construction and substrate internals?
4. **BSD / GPL split.** Can the maintainers confirm the license split (core
   `octomap` BSD, `octovis` GPL), so URML's mapping correctly consumes only the
   BSD core?
5. **License.** Is the core library's current license BSD (the GitHub API
   surfaced the repo without a single SPDX id given the component split)?
6. **Conformance listing.** Would the OctoMap project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0337 ships as a single RFC document PR alongside the Move #25 ledger
([`examples/lighthouses/outreach-move25.yaml`](../../examples/lighthouses/outreach-move25.yaml))
and the post bodies
([`examples/lighthouses/posts-move25.md`](../../examples/lighthouses/posts-move25.md)).

## How to respond

The live channel is a GitHub Issue on
[`OctoMap/octomap`](https://github.com/OctoMap/octomap) pointing at this RFC
(Discussions are disabled on the repo). If the maintainers prefer another venue,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 2,307 stars, not archived, Issues
      enabled, Discussions disabled, last push 2026-02-08).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, map-representation-not-pose-source fit,
      license split).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Germany / community (allied); default policy passes at the
      mapping layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; OctoMap is one
      occupancy representation among several, URML consumes the map and never
      builds it).
