---
rfc: 0324
title: O3DE (Open 3D Engine) ROS 2 robotics simulation integration, request for comment from the O3DE maintainers
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

# RFC-0324: O3DE ROS 2 robotics simulation integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's simulation framework, and
requests review from that target's maintainers. It does not modify URML's
normative surface.

## Summary

O3DE (Open 3D Engine) is a Linux Foundation governed open 3D engine. Its
robotics surface is the **ROS 2 Robotics Gem**, which lives in the sibling repo
[`o3de/o3de-extras`](https://github.com/o3de/o3de-extras) and turns O3DE into a
simulation substrate for ROS 2 robots: it imports a robot (URDF), spawns it into
a scene, and bridges the simulated robot to ROS 2 topics, services, and actions.
This RFC opens that engagement against
[`o3de/o3de`](https://github.com/o3de/o3de) and **requests review and feedback
from the O3DE maintainers**.

This RFC addresses the engine and its robotics Gem as one conversation. The
engine repo `o3de/o3de` is the anchor; the ROS 2 Robotics Gem in `o3de-extras`
is named here and folded into this thread (the Gem-specific follow-up may move
to `o3de-extras` if the maintainers prefer, see the unresolved questions). No
separate post is opened against `o3de-extras`.

URML composes **above** the O3DE ROS 2 Gem: URML intent → validated Layer-2
primitives → the Gem's ROS 2 interfaces → the simulated robot. The
differentiator is **static validation against the capability manifest and the
active safety envelope before the Gem actuates the simulated robot**.

## Motivation

A simulation engine is where "validate before you move" is cheapest to
demonstrate and safest to iterate on: no real hardware, full repeatability, and
the same ROS 2 seam a deployed robot would speak. O3DE is a strong fit for that
demonstration:

1. **It is a real ROS 2 simulation substrate.** The ROS 2 Robotics Gem imports a
   URDF, spawns the robot as an O3DE entity, and exposes the simulated robot over
   standard ROS 2 interfaces. That is the same Layer-0 seam URML's reference
   ROS 2 runtime already targets, so a URML primitive that lands on a real robot
   lands the same way on an O3DE simulated one.
2. **The imported robot is the capability surface.** O3DE's URDF import and the
   Gem's spawnable describe what the simulated robot is and can do. URML's
   capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares the
   same capability at the intent altitude, which gives the validator something
   concrete to check the intent against before the Gem moves the robot.
3. **It keeps the substrate-neutrality claim honest.** O3DE joins Webots
   ([RFC-0234](0234-webots-outreach.md)) and MuJoCo
   ([RFC-0060](0060-mujoco-integration.md)) as sibling simulation engagements.
   The acid test holds: the same primitives that map onto O3DE map onto those
   engines and onto a zero-ROS runtime. O3DE is one Layer-0 simulation target
   among several, not a privileged one.

Repo at [`o3de/o3de`](https://github.com/o3de/o3de) (~9,257 stars, Issues **and**
Discussions enabled, not archived, last push 2026-06-01, very active). The
robotics Gem lives in [`o3de/o3de-extras`](https://github.com/o3de/o3de-extras)
(~81 stars). License is asked as a question below (O3DE is understood to be
Apache-2.0 / MIT dual; the GitHub API did not surface an SPDX id at verification
time).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `o3de_sim_cell.yaml` fixture)

| URML field | Maps to O3DE ROS 2 Gem attribute |
|---|---|
| `robot_id`, `description` | The spawned simulated-robot identity (carried at the manifest envelope; not an engine concept) |
| `frames`, `declared_locations` | Scene coordinate frames and named spawn / goal poses in the O3DE level, aligned with the imported URDF frames |
| `mobility.drive_type` (`differential` / `ackermann` / `tracked` / ...) | The Gem's vehicle / robot-control component for the imported robot's base |
| `mobility.max_velocity`, `max_payload`, `service_ceiling` | Limits checked against the requested intent before the Gem actuates; conjoined with the envelope |
| `manipulation.arm_count` + joints, `grippers[]` | URDF joints driven through the Gem's ROS 2 controller interfaces (`move_to`, `grasp`, `release`) |
| `perception.cameras[]`, `sensors[{measurement_type}]` | O3DE sensor components the Gem publishes to ROS 2 (camera, lidar, IMU, contact); `detect`, `scan`, `measure`, `capture` read these |
| `perception.object_vocabulary` | The simulated objects `detect.object` may name in the scene |
| Safety envelope limits (Pass 3) | Conjoined strictest-wins with the imported robot's joint / velocity limits before any sim motion |

### What URML v0.1 does not yet express for O3DE

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Simulator-target class hint.** URML's substrate manifest does not declare
   that a deployment targets a simulator rather than hardware, nor which engine
   (O3DE / Webots / MuJoCo / Isaac Sim / Genesis). A future optional
   simulator-target hint would let the envelope reason differently about a sim
   run (for example, relaxing a real-world geofence). This hint is **shared with
   the sibling Move #24 simulator RFCs** (RFC-0322 Genesis, RFC-0323 Isaac Sim);
   it should be designed once across all of them, not per engine.
2. **URDF cross-reference.** URML v0.1 declares capability independently of the
   robot's kinematic structure and does not cross-check the manifest against a
   referenced URDF (see Layer-1 spec section 5). O3DE's URDF import makes this a
   natural place to revisit an optional `urdf_ref:`, queued as a separate Spec
   RFC.

### Compatibility notes

- **Vendor org.** [`o3de`](https://github.com/o3de) (the Open 3D Foundation, a
  Linux Foundation project; community governance).
- **Engagement repo.** [`o3de/o3de`](https://github.com/o3de/o3de) (the engine;
  this thread's anchor).
- **Robotics surface (folded into this thread).**
  [`o3de/o3de-extras`](https://github.com/o3de/o3de-extras) is home of the ROS 2
  Robotics Gem, the simulation substrate URML actually targets. Named here; a
  dedicated `o3de-extras` follow-up opens only if the maintainers route the
  Gem-specific discussion there.
- **Origin.** Linux Foundation (international, allied). Passes US-federal default
  policy (open-source engine, no provenance gate at the simulation layer).
- **License fit.** Understood to be Apache-2.0 / MIT dual; asked below as a
  question.
- **Substrate-neutrality.** O3DE is one Layer-0 simulation target among several;
  the same primitives map to Webots, MuJoCo, Isaac Sim, and a zero-ROS runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The simulator-target hint and the
  optional URDF cross-reference are queued Spec RFCs.
- Reference runtime: URML's existing
  [`reference/ros2-runtime/`](../../reference/ros2-runtime/) adapter speaks to
  ROS 2 action / topic / service interfaces. The O3DE mapping routes a
  primitive's goal to the same ROS 2 interfaces the Gem exposes; the planned
  `o3de_sim_cell.yaml` fixture would prove it against an imported simulated
  robot.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Engine-plus-Gem in one thread.** Naming the ROS 2 Robotics Gem
  (`o3de-extras`) inside an `o3de/o3de` thread risks landing on the wrong repo
  for the maintainers who own the Gem. Justified by keeping one conversation
  rather than two parallel posts; the thread offers to move the Gem-specific part
  to `o3de-extras` if they prefer (question 3 below).
- **Sim-only value at first.** The immediate payoff is a hermetic validated-intent
  demo against a simulated robot, not a hardware deployment. That is the intended
  scope of a simulation engagement, but it is worth stating plainly.

## Alternatives considered

1. **Post directly to `o3de-extras` (the Gem) instead of the engine.** Rejected
   as the anchor. The engine repo is the project's front door and the higher
   traffic surface; the Gem is named and the thread offers to move there. Opening
   on the Gem alone would under-serve the broader engine maintainers who govern
   the project.
2. **Two separate posts (engine and Gem).** Rejected. Two posts to one Linux
   Foundation org in a day is the carpet-bombing pattern that has drawn
   AI-content closes elsewhere. One anchor thread that names the Gem is more
   respectful and just as discoverable.
3. **Fold O3DE into the Webots or MuJoCo simulation RFC.** Rejected. O3DE is a
   distinct engine with its own maintainers, its own URDF-import path, and its
   own Gem architecture; it earns a dedicated request for comment alongside the
   sibling sim RFCs rather than a footnote on one of them.

## Prior art

- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling simulation
  engagement; same composed-above framing against a different engine.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): sibling
  simulation engagement; physics-engine peer.
- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md):
  adjacent simulation / learning engagement in the NVIDIA stack.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md): the ROS 2 seam
  the O3DE Gem speaks; URML composes above both.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.
- Sibling Move #24 simulator RFCs (referenced by number): RFC-0322 (Genesis) and
  RFC-0323 (Isaac Sim) share the simulator-target class-hint question.

## Unresolved questions

For the O3DE maintainers:

1. **ROS 2 Gem integration boundary.** Is the right URML boundary "URML primitive
   → the Gem's ROS 2 interface (topic / service / action) → the simulated robot",
   with O3DE scene and physics configuration left entirely below URML (Layer 0)?
   Does anything about the Gem's spawnable model break that clean separation?
2. **Robot-import (URDF) alignment.** O3DE imports a robot from URDF. Should
   URML's capability manifest align to the imported URDF's frames and joints (a
   future optional `urdf_ref:`), or stay at the capability-block altitude and let
   the adapter resolve structure from the imported robot?
3. **Venue for the Gem-specific follow-up.** This thread is on `o3de/o3de`. Would
   the maintainers prefer the ROS 2 Robotics Gem discussion move to
   [`o3de/o3de-extras`](https://github.com/o3de/o3de-extras), or is the engine
   repo the right place to keep one conversation?
4. **Simulator-target hint.** Would a small, optional "this deployment targets a
   simulator (and which engine)" hint in URML's manifest be useful for envelope
   reasoning, or is it noise at the intent layer? (Designed once across O3DE,
   Genesis, Isaac Sim, Webots, MuJoCo.)
5. **License.** What is the current license of `o3de/o3de` and `o3de/o3de-extras`
   (the GitHub API did not surface an SPDX id at verification time; understood to
   be Apache-2.0 / MIT dual)?
6. **Conformance listing.** Would O3DE consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0324 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).
The `o3de/o3de-extras` row shares this RFC; a dedicated ledger row is added only
if the engagement forks to the Gem repo.

## How to respond

The live channel is a GitHub Issue or Discussion on
[`o3de/o3de`](https://github.com/o3de/o3de) pointing at this RFC (the repo has
both enabled). If the maintainers prefer to route the ROS 2 Robotics Gem part to
[`o3de/o3de-extras`](https://github.com/o3de/o3de-extras), URML will move that
follow-up there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (~9,257 stars on o3de/o3de, ~81 on
      o3de-extras, not archived, Issues and Discussions enabled, last push
      2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, engine-plus-Gem in one thread, sim-only
      value at first).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Linux Foundation open-source engine; default policy passes at
      the simulation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; O3DE is one Layer-0
      simulation target among many, composed-above not assumed).
