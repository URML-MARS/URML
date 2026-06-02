---
rfc: 0325
title: CARLA (autonomous-driving simulator) integration, request for comment from the CARLA maintainers
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

# RFC-0325: CARLA autonomous-driving simulator integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's simulation framework, and
requests review from that target's maintainers. It does not modify URML's
normative surface.

## Summary

CARLA is the leading open autonomous-driving simulator: a client-server engine
that spawns vehicle and pedestrian actors into a city, attaches a configurable
sensor suite (RGB, lidar, radar, GNSS, IMU, depth, semantic segmentation), and
exposes actor control through a Python API and a ROS bridge. This RFC opens an
engagement against
[`carla-simulator/carla`](https://github.com/carla-simulator/carla) and
**requests review and feedback from the CARLA maintainers**.

URML composes **above** CARLA: URML intent → validated Layer-2 primitives →
CARLA actor control (Python API or the ROS bridge) → the simulated vehicle. The
differentiator is **static validation of the intent against the declared vehicle
capability and the active safety envelope before actor control is applied**.

This RFC is honest about scope. CARLA's domain is autonomous driving, which is a
**subset** of robotics: ground vehicles with Ackermann steering and a
driving-grade sensor suite. URML maps the part of its mobility and perception
vocabulary that fits that subset and does **not** yet have a full driving
profile. The gaps are flagged below as queued Spec RFCs, not proposed here.

## Motivation

CARLA is where URML's "validate before you actuate" check meets the most
safety-laden robotics subset, ground vehicles, with full repeatability and no
real car on the road:

1. **The mobility vocabulary already fits a vehicle.** URML's
   `mobility.drive_type: ackermann`, `max_velocity`, and `service_ceiling`
   describe a steered ground vehicle directly. A CARLA vehicle actor is exactly
   that, so the declared-capability check has a concrete actor to validate intent
   against before any control is applied.
2. **The perception manifest matches CARLA's sensor suite.** URML's
   `perception.cameras[]` and `perception.sensors[{measurement_type}]` align with
   CARLA's RGB cameras and its lidar / radar / GNSS / IMU sensors. The
   `measurement_type` enum (`distance`, `point_cloud`, and friends) covers the
   common CARLA sensors, which makes `detect`, `scan`, `measure`, and `capture`
   meaningful against a simulated AV.
3. **It is a clean client-server substrate.** CARLA's actor control reaches the
   simulator over a client-server transport (the Python API) or a ROS bridge.
   URML treats that transport as Layer 0, the same way RFC-0006 keeps link
   transports out of the manifest, and validates the intent before it crosses
   that boundary.

Repo at [`carla-simulator/carla`](https://github.com/carla-simulator/carla)
(~14,022 stars, Issues **and** Discussions enabled, not archived, last push
2026-06-02, very active). CARLA originated at the Computer Vision Center
(Barcelona) and Intel and is now community-developed; treated as international
and allied, passing US-federal default policy. License is asked as a question
below (understood to be MIT; the GitHub API did not surface an SPDX id at
verification time).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `carla_vehicle_cell.yaml` fixture)

| URML field | Maps to CARLA actor / sensor attribute |
|---|---|
| `robot_id`, `description` | The spawned vehicle actor identity (carried at the manifest envelope; not a CARLA concept) |
| `frames`, `declared_locations` | The map's coordinate frame and named spawn / waypoint poses in the CARLA town |
| `mobility.drive_type: ackermann` | A CARLA vehicle actor under Ackermann control |
| `mobility.max_velocity` | The vehicle's commanded speed limit; conjoined with the envelope before control is applied |
| `mobility.service_ceiling` | Not meaningful for a ground vehicle; declared only where a profile uses it (left unset for CARLA cars) |
| `perception.cameras[]` | CARLA RGB / depth / semantic-segmentation camera sensors; `capture` reads these |
| `perception.sensors[{measurement_type: point_cloud}]` | CARLA lidar (and semantic lidar) |
| `perception.sensors[{measurement_type: distance}]` | CARLA radar / GNSS / IMU positioning sensors; `measure`, `detect` read these |
| `perception.object_vocabulary` | The simulated actors `detect.object` may name (vehicle, pedestrian, traffic_sign, ...) |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins with the declared vehicle limits before actor control |
| (substrate-config, not a URML field) | CARLA map, weather, traffic manager, and the client-server transport: Layer 0, declared in CARLA, not the URML manifest |

### What URML v0.1 does not yet express for CARLA

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Driving / road profile.** URML has no driving profile: no lane, road, route,
   or waypoint-following vocabulary, and no road-relative geometry. A future Spec
   RFC could add an optional driving profile so AV intent (follow a route, keep a
   lane) is first-class rather than approximated through `move_to`.
2. **Traffic-rule envelope.** URML's safety envelope reasons about velocity,
   payload, geofence, and altitude, not traffic rules (speed limits per road
   segment, right-of-way, signal state). A future Spec RFC could add a
   traffic-rule envelope dimension for the driving subset.
3. **Simulator-target class hint.** As with the sibling Move #24 simulator RFCs,
   URML's manifest does not declare that a deployment targets a simulator or
   which engine. This hint is shared across the wave (RFC-0322 Genesis, RFC-0323
   Isaac Sim, RFC-0324 O3DE) and should be designed once.

### Compatibility notes

- **Vendor org.** [`carla-simulator`](https://github.com/carla-simulator) (the
  CARLA open-source community).
- **Engagement repo.** [`carla-simulator/carla`](https://github.com/carla-simulator/carla)
  (the simulator; this thread's anchor).
- **Origin.** Originated at the Computer Vision Center (Barcelona) and Intel; now
  community-developed. International and allied; passes US-federal default policy
  (open-source simulator, no provenance gate at the simulation layer).
- **License fit.** Understood to be MIT; asked below as a question (the GitHub
  API did not surface an SPDX id at verification time).
- **Substrate-neutrality.** CARLA is one Layer-0 simulation target among several;
  the same primitives map to O3DE ([RFC-0324](0324-o3de-outreach.md)), Webots
  ([RFC-0234](0234-webots-outreach.md)), MuJoCo
  ([RFC-0060](0060-mujoco-integration.md)), and a zero-ROS runtime. CARLA's AV
  focus is a domain subset, not a coupling.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The driving profile, the traffic-rule
  envelope, and the simulator-target hint are queued Spec RFCs.
- Reference runtime: a CARLA mapping routes a primitive's goal to CARLA actor
  control over the Python API, or over the ROS bridge to the same ROS 2
  interfaces URML's existing
  [`reference/ros2-runtime/`](../../reference/ros2-runtime/) adapter speaks. The
  planned `carla_vehicle_cell.yaml` fixture would prove the validated-intent path
  against a simulated vehicle.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Domain subset.** CARLA is AV-specific (cars), a subset of robotics. URML maps
  its mobility and perception subset and is open that it lacks a driving profile.
  The fit is partial by design, and a maintainer may reasonably ask whether a
  general-robot language belongs in an AV simulator at all (question 2 below).
- **Two control paths.** CARLA exposes both a Python API and a ROS bridge. URML
  can land on either, but the right adapter boundary is genuinely open
  (question 1 below), and choosing wrong would add friction.

## Alternatives considered

1. **Wait for a URML driving profile before engaging CARLA.** Rejected. The
   mobility and perception subset already maps cleanly, and the maintainers' view
   on whether a driving profile is wanted is exactly the input this RFC seeks.
   Engaging now, honestly scoped, is better than engaging later with assumptions
   baked in.
2. **Engage only through the ROS bridge (treat CARLA as a ROS 2 target).**
   Rejected as the sole framing. The ROS bridge is one path, but CARLA's native
   surface is the Python API; pinning URML to the bridge alone would understate
   the engine and pre-decide question 1 for the maintainers.
3. **Fold CARLA into the O3DE or Webots simulation RFC.** Rejected. CARLA is a
   distinct simulator with a distinct (AV) domain, its own maintainers, and its
   own actor / sensor model; it earns a dedicated request for comment alongside
   the sibling sim RFCs rather than a footnote on one of them.

## Prior art

- [RFC-0324 (O3DE outreach)](0324-o3de-outreach.md): sibling Move #24
  simulation engagement; same composed-above framing against a general 3D engine.
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling simulation
  engagement.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): sibling
  physics-engine simulation engagement.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  why URML models abstract link roles, not transports; the same logic keeps
  CARLA's client-server transport at Layer 0.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md): the ROS 2 seam
  CARLA's ROS bridge speaks; URML composes above both.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md):
  the capability and primitive surfaces this engagement exercises.
- Sibling Move #24 simulator RFCs (referenced by number): RFC-0322 (Genesis) and
  RFC-0323 (Isaac Sim) share the simulator-target class-hint question.

## Unresolved questions

For the CARLA maintainers:

1. **Actor-control boundary.** Is the right URML boundary "URML primitive → CARLA
   actor control", and should that land on the Python API directly or on the ROS
   bridge (the same ROS 2 interfaces URML already targets)? Which would the
   maintainers point a validated-intent integration at first?
2. **AV-vs-general-robot framing.** CARLA is AV-domain; URML is a general-robot
   language mapping a mobility / perception subset. Is that framing welcome, and
   would a URML driving / road profile (queued Spec RFC) be useful to CARLA, or
   out of scope for the project?
3. **Sensor-suite manifest alignment.** Does URML's perception manifest
   (`cameras[]`, `sensors[{measurement_type}]`) cover CARLA's sensor suite (RGB,
   lidar, radar, GNSS, IMU, depth, semantic) cleanly, or are there CARLA sensors
   that do not fit the `measurement_type` enum?
4. **Traffic rules.** Should URML's safety envelope grow a traffic-rule dimension
   (speed limits, right-of-way, signal state) for the driving subset, or is that
   firmly CARLA's traffic manager (Layer 0)?
5. **License.** What is the current license of `carla-simulator/carla` (the
   GitHub API did not surface an SPDX id at verification time; understood to be
   MIT)?
6. **Conformance listing.** Would CARLA consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0325 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`carla-simulator/carla`](https://github.com/carla-simulator/carla) pointing at
this RFC (the repo has both enabled). If the maintainers prefer the CARLA forum
or another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (~14,022 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, AV domain subset, two control paths).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (driving profile, traffic-rule
      envelope, simulator-target hint) flagged as queued Spec RFCs, not proposed
      here.
- [x] Provenance: CARLA open-source community (CVC Barcelona / Intel origin);
      international and allied; default policy passes at the simulation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; CARLA is one Layer-0
      simulation target among many, AV focus is a domain subset not a coupling,
      composed-above not assumed).
