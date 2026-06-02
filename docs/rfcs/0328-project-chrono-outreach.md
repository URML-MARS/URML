---
rfc: 0328
title: Project Chrono (high-fidelity multi-physics simulation) integration, request for comment from the Project Chrono maintainers
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

# RFC-0328: Project Chrono integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's simulation engine, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #24 engages the simulation and digital-twin layer: the engines where a
validated URML program can be exercised before it touches real hardware. This
RFC reaches [`projectchrono/chrono`](https://github.com/projectchrono/chrono),
a high-fidelity multibody and multi-physics engine with Chrono::Vehicle (ground
vehicles, terramechanics for deformable terrain) and Chrono::Sensor
(camera / lidar / GPS / IMU simulation). It **requests review and feedback from
the Project Chrono maintainers**.

URML's strongest fit with Chrono is **high-fidelity pre-deployment validation**:
a URML program is first checked statically against the robot's capability
manifest and active safety envelope, then the same validated intent is simulated
against rough-terrain and vehicle dynamics in Chrono before any real deployment.
URML composes **above** Chrono: URML intent -> validated Layer-2 primitives ->
a Chrono vehicle / robot model -> high-fidelity physics. The differentiator is
**static validation against the declared capability and envelope before the
high-fidelity sim runs**.

## Motivation

Chrono is one of the few open simulators built for high-fidelity multibody and
multi-physics, not just rigid-body game-grade contact. That makes it a
distinctive validation target for URML:

1. **It models the hard cases URML's envelope reasons about.** Chrono::Vehicle
   simulates ground-vehicle dynamics over deformable terrain (terramechanics):
   slip, sinkage, tipping margins. A URML `move_to` validated against a
   `max_velocity` and a payload bound is exactly the intent a roboticist wants
   to stress-test on rough terrain before committing real hardware.
2. **Its sensor stack matches URML's perception block.** Chrono::Sensor
   simulates camera, lidar, GPS, and IMU. URML's `perception` manifest declares
   cameras and sensors by `measurement_type`; Chrono is a venue to exercise
   `detect`, `scan`, `measure`, and `capture` against simulated sensor data
   before field trials.
3. **It is where "validate before you move" pays off cheaply.** A high-fidelity
   sim run is expensive; a static capability and envelope check is not. URML's
   contribution is one layer up and earlier: reject the intent the robot cannot
   safely attempt before the multibody solver ever spins, so the expensive sim
   only ever runs admissible programs.

Repo at [`projectchrono/chrono`](https://github.com/projectchrono/chrono)
(2,865 stars, Issues **and** Discussions enabled, not archived, actively
developed). License is asked as a question below (understood to be BSD-3-Clause;
the GitHub API did not surface an SPDX id at verification time). Project Chrono
is an academic project of the University of Wisconsin-Madison and the University
of Parma; international origin, passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `chrono_vehicle_cell.yaml` fixture)

| URML field | Maps to Chrono attribute |
|---|---|
| `robot_id`, `description` | Chrono system / vehicle model identity (carried at the manifest envelope, not a Chrono concept) |
| `mobility.drive_type: tracked` | A Chrono::Vehicle tracked-vehicle model over deformable or rigid terrain |
| `mobility.drive_type: ackermann` | A Chrono::Vehicle wheeled-vehicle model with Ackermann steering |
| `mobility.max_velocity` | Vehicle speed bound enforced before the sim step; conjoined with the envelope |
| `mobility.max_payload` | Sprung / payload mass in the vehicle model; the envelope's payload bound checked statically first |
| `manipulation.arm_count` + joints | Chrono multibody links / joints driven as an articulated robot model |
| `perception.cameras[]` | A Chrono::Sensor camera attached to the model frame |
| `perception.sensors[].measurement_type: distance` | A Chrono::Sensor lidar (`point_cloud`) or range sensor |
| `perception.sensors[]` (GPS / IMU) | Chrono::Sensor GPS / IMU sensors at the declared frame |
| Safety envelope limits (Pass 3) | Bounds asserted before the high-fidelity run; URML conjoins strictest-wins, then Chrono observes the dynamics under them |

### What URML v0.1 does not yet express for Chrono

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Terrain / terramechanics fidelity hint.** URML's manifest declares
   capability, not the terrain a deployment runs over. A future Spec RFC could
   add an optional terrain-fidelity hint (rigid / deformable / granular) so the
   envelope can reason about a margin Chrono will exercise, without modelling
   the terrain itself (that stays substrate configuration).
2. **Simulator-target class hint.** URML does not declare whether a deployment
   targets a high-fidelity multibody simulator, a game-grade engine, or real
   hardware. A future Spec RFC could add an optional simulator-target class hint
   so a fixture can state the fidelity it was validated against. Shared with the
   sibling Move #24 RFCs.

### Compatibility notes

- **Vendor org.** [`projectchrono`](https://github.com/projectchrono), an
  academic consortium led by the University of Wisconsin-Madison and the
  University of Parma.
- **Engagement repo.** [`projectchrono/chrono`](https://github.com/projectchrono/chrono),
  the multibody / multi-physics engine, with Chrono::Vehicle and Chrono::Sensor.
- **Origin.** International academic (United States / Italy). Passes US-federal
  default policy (open-source academic engine, no provenance gate at the
  simulation layer).
- **License fit.** Understood to be BSD-3-Clause; asked below as a question.
  BSD-3-Clause is permissive and compatible with URML's Apache-2.0 posture; a
  validated-intent mapping carries no license entanglement.
- **Substrate-neutrality.** Chrono is one simulation target among several; the
  same URML primitives map to Drake ([RFC-0059](0059-drake-model-based-robotics.md)),
  MuJoCo ([RFC-0060](0060-mujoco-integration.md)), or a zero-sim runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The terrain-fidelity and
  simulator-target hints are queued Spec RFCs.
- Reference runtime: a Chrono mapping would route a validated primitive's motion
  goal to a Chrono::Vehicle or articulated model, via the Python interface
  (PyChrono) or a ROS bridge; the planned `chrono_vehicle_cell.yaml` fixture
  would prove the mapping hermetically against a small model.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Heavyweight demo.** A faithful Chrono::Vehicle terramechanics scene is large
  and slow relative to URML's hermetic-demo posture. The value of this
  engagement is the high-fidelity validation use-case and the boundary
  confirmation, not a fast runnable example yet.
- **PyChrono vs ROS boundary is open.** Whether URML should dispatch through
  PyChrono directly or through a ROS bridge is a real architectural fork
  (question 1 below), and the answer affects how much of Chrono's API a URML
  adapter needs to touch.

## Alternatives considered

1. **Fold Chrono into a single "simulators" RFC with Genesis / Isaac Sim /
   CARLA.** Rejected. Chrono's high-fidelity multibody and terramechanics story
   is distinct from a game-grade or photoreal engine; it earns a dedicated
   request for comment, and its maintainer community is its own.
2. **Engage at the PyChrono wrapper instead of the engine.** Rejected as the
   anchor. PyChrono is the binding URML would likely dispatch through, but the
   engine repo is where the maintainers and the modelling decisions live; the
   Python boundary is a question for them, not a separate engagement.
3. **Model terrain and vehicle dynamics in the URML manifest.** Rejected.
   Terrain and dynamics are substrate configuration; modelling them in the
   capability manifest would fail the substrate-neutrality acid test, the same
   line Layer 1 draws against URDF / SDF structure.

## Prior art

- [RFC-0059 (Drake model-based robotics outreach)](0059-drake-model-based-robotics.md)
  (sibling model-based dynamics engagement; the closest peer in modelling
  altitude).
- [RFC-0060 (MuJoCo integration outreach)](0060-mujoco-integration.md)
  (sibling physics-engine engagement).
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md),
  [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md)
  (earlier simulation-layer engagements; this RFC extends the line to
  high-fidelity multibody).
- Sibling Move #24 RFCs: RFC-0322 (Genesis), RFC-0323 (Isaac Sim), RFC-0325
  (CARLA), RFC-0331 (Gymnasium).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md), URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the Project Chrono maintainers:

1. **PyChrono vs ROS boundary.** Is the right URML dispatch boundary "URML
   primitive -> PyChrono model command", or "URML primitive -> ROS bridge ->
   Chrono"? Which keeps a validated-intent demo cleanest for a maintainer to
   reproduce?
2. **Robot / vehicle model alignment.** Does URML's capability altitude
   (`mobility.drive_type`, joints, sensors) map cleanly onto a Chrono::Vehicle
   or articulated model, or does Chrono expect detail URML deliberately leaves
   to substrate configuration?
3. **High-fidelity-validation fit.** Does the use-case (static URML validation,
   then a high-fidelity Chrono run as a pre-deployment gate) resonate, or is the
   value mostly in the sensor / terramechanics realism rather than the gate?
4. **Sensor mapping.** Is Chrono::Sensor the right surface for URML's
   `perception` block (cameras, lidar as `distance` / `point_cloud`, GPS, IMU),
   and is anything in URML's sensor vocabulary missing for a faithful map?
5. **License.** What is the current license of `projectchrono/chrono` (the
   GitHub API did not surface an SPDX id at verification time; understood to be
   BSD-3-Clause)?
6. **Conformance listing.** Would Project Chrono consider a project link to
   URML's compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0328 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`projectchrono/chrono`](https://github.com/projectchrono/chrono) pointing at
this RFC (the repo has both enabled). If the maintainers prefer their own forum,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (2,865 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, heavyweight demo, PyChrono vs ROS boundary
      open).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international academic engine; default policy passes at the
      simulation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Chrono is one
      simulation target among many, composed-above not assumed).
