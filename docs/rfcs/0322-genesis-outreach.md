---
rfc: 0322
title: Genesis (generative / differentiable physics robotics simulator) integration, request for comment from the Genesis maintainers
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

# RFC-0322: Genesis integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #24 opens URML's engagement with the simulation / digital-twin layer. This
RFC reaches the highest-momentum target in that layer:
[`Genesis-Embodied-AI/Genesis`](https://github.com/Genesis-Embodied-AI/Genesis)
(canonical name `genesis-world`), a generative and differentiable physics engine
for embodied-AI and robotics. It **requests review and feedback from the Genesis
maintainers**.

URML's strongest fit with Genesis is as a **hermetic demo vehicle**: a validated
English sentence becomes a URML primitive, the primitive drives a robot entity
inside a Genesis scene, and the scene steps a simulated motion, with no hardware
in the loop. The URML capability manifest aligns with the imported robot model
(URDF / MJCF), and the primitives (`move_to`, `grasp`, `release`, `scan`,
`detect`) map onto commands issued to a Genesis robot entity.

URML composes **above** Genesis: URML intent -> validated Layer-2 primitives ->
a Genesis robot entity's control API -> a stepped simulation. The differentiator
is **static validation against the capability manifest and the active safety
envelope before the simulator takes a single step**. Genesis is one simulator
among many; the same primitive runs unchanged on real hardware.

## Motivation

Genesis is the fastest-rising generative / differentiable physics simulator in
the embodied-AI community, and a simulator is the cleanest place to demonstrate
URML's "validate before you move" promise without owning a robot:

1. **It is the ideal hermetic-demo substrate.** URML's headline path is one
   English sentence moving a robot. A simulator closes that loop on any laptop:
   validated intent -> primitive -> robot entity in a scene -> simulated motion.
   No real actuator, no safety risk, fully reproducible by a developer.
2. **Its robot model is exactly what URML's manifest declares over.** Genesis
   imports robots from URDF / MJCF. URML's Layer-1 capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares
   the same capability surface (joints, grippers, sensors) at a coarser altitude.
   The manifest and the imported model describe the same robot from two sides.
3. **It is where static validation is cheap to show.** Genesis steps physics
   forward. URML's contribution sits one layer up and earlier: a static check,
   before the first step, that the declared capability and the safety envelope
   admit the requested intent. A rejected program never enters the sim loop.
4. **It grounds substrate-neutrality.** A primitive that maps onto a Genesis
   entity must also map onto MuJoCo, Webots, real hardware. Genesis is one
   simulator target among many; demonstrating the same primitive across several
   is the evidence that the abstraction is not engine-shaped by accident.

Repo at [`Genesis-Embodied-AI/Genesis`](https://github.com/Genesis-Embodied-AI/Genesis)
(about 29,168 stars, Issues **and** Discussions enabled, not archived, last push
2026-06-02, very active). License is asked as a question below (the GitHub API
did not surface an SPDX id at verification time; understood to be Apache-2.0).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `genesis_scene_cell.yaml` fixture)

| URML field | Maps to Genesis attribute |
|---|---|
| `robot_id`, `description` | The robot entity's identity in the scene (carried at the manifest envelope) |
| `frames`, `declared_locations` | Scene frames and named target poses a `move_to` resolves against |
| `mobility.drive_type` / `max_velocity` | The robot entity's base control mode and velocity command bounds in the stepped sim |
| `manipulation.arm_count` + joints | The arm joints of the imported URDF / MJCF entity, driven by Genesis joint control |
| `manipulation.grippers[].kind` / `force_max_n` | The gripper DOF of the entity; force bound checked statically before a `grasp` command is issued |
| `perception.cameras[]` / `sensors[]` | Genesis scene cameras and sensors a `capture` / `detect` / `measure` reads from the rendered or simulated state |
| `perception.object_vocabulary` | The object classes present as entities in the scene that `detect` may name |
| Safety envelope limits (Pass 3) | Conjoined with the entity's joint and velocity limits; URML applies strictest-wins before the sim steps |

### What URML v0.1 does not yet express for Genesis

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Simulator-target class hint.** URML's substrate manifest does not declare
   that a deployment targets a simulator rather than hardware. A future Spec RFC
   could add an optional simulator-target class hint (shared with RFC-0323), so
   the validator and tooling can reason about a sim deployment explicitly.
2. **Sim-vs-real provenance marker.** A program validated against a simulated
   robot is not the same trust artifact as one validated against hardware. A
   future Spec RFC could add an optional sim-vs-real marker to provenance so a
   downstream consumer can tell a simulated run from a real one.

### Compatibility notes

- **Vendor org.** [`Genesis-Embodied-AI`](https://github.com/Genesis-Embodied-AI)
  (open-source embodied-AI community, a multi-national / academic consortium).
- **Engagement repo.** [`Genesis-Embodied-AI/Genesis`](https://github.com/Genesis-Embodied-AI/Genesis)
  (`genesis-world`): generative and differentiable physics simulator; very
  active.
- **Origin / policy.** International (community / academic consortium). Treated
  as INTL; passes US-federal default policy (open-source framework, no provenance
  gate at the simulator layer).
- **License fit.** Understood to be Apache-2.0; asked below as a question.
- **Substrate-neutrality.** Genesis is one simulator (and one Layer-1 target)
  among many; the same URML primitives map to MuJoCo, Webots, or real hardware
  with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The simulator-target class hint and
  the sim-vs-real provenance marker are queued Spec RFCs.
- Reference runtime: no change in this RFC. A Genesis mapping would route a
  validated primitive's motion goal to a Genesis robot entity's control API; the
  planned `genesis_scene_cell.yaml` fixture would prove it hermetically against
  an imported URDF / MJCF robot in a scene.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Demo-shaped fit.** URML's value to Genesis is mostly as a hermetic-demo
  target, not as a control framework Genesis itself needs. The engagement is
  honest about that asymmetry: URML benefits from the showcase more than Genesis
  benefits from the mapping.
- **Fast-moving target.** Genesis is very actively developed; a control-API
  boundary documented today may drift. The mapping is described at the entity /
  primitive altitude to stay robust to internal churn.

## Alternatives considered

1. **Skip simulators and demo only against hardware adapters.** Rejected. A
   simulator is the only way to make the one-sentence-moves-a-robot loop
   reproducible by any developer on any OS with no hardware, which is exactly the
   adoption path URML optimizes for.
2. **Pick a single simulator and standardize on it.** Rejected. Locking the demo
   to one engine would contradict substrate-neutrality. Genesis is engaged
   alongside MuJoCo (RFC-0060) and Webots (RFC-0234) precisely so the same
   primitive is shown across engines.
3. **Model the Genesis scene graph in the URML manifest.** Rejected. The scene
   and the physics are Layer 0 / substrate concern; URML declares capability over
   the robot entity, not the scene. Modelling the scene would fail the
   substrate-neutrality acid test.

## Prior art

- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): sibling
  simulator engagement; the same hermetic-demo posture.
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling simulator
  engagement; one engine among many.
- [RFC-0059 (Drake model-based robotics)](0059-drake-model-based-robotics.md):
  related model-based-simulation engagement.
- [RFC-0144 (DeepMind MuJoCo Playground outreach)](0144-deepmind-mujoco-playground-outreach.md):
  related embodied-AI simulation engagement.
- Sibling Move #24 RFCs: RFC-0323 (NVIDIA Isaac Sim), RFC-0324 (O3DE),
  RFC-0325 (CARLA), RFC-0330 (Eclipse Ditto digital twin).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the Genesis maintainers:

1. **Scene / robot description alignment.** Genesis imports robots from URDF /
   MJCF. Is matching URML's capability manifest against the imported model (joints,
   grippers, sensors) the right alignment, or is there a richer Genesis-native
   robot description URML should read instead?
2. **Control-API boundary.** What is the right seam for "URML primitive ->
   Genesis entity command"? Should a `move_to` resolve to a joint / base control
   call on the entity, and is there a stable control API URML should target?
3. **Hermetic-demo interest.** Would Genesis be interested in being a documented
   hermetic-demo target for URML (validated English intent -> primitive -> robot
   entity in a scene -> simulated motion), and is there a preferred example scene
   or robot to anchor it on?
4. **Differentiability.** Genesis is differentiable. URML's contract is static
   validation before motion, not gradient flow. Is there a useful intersection
   (for example, validated intent as a constraint on a differentiable rollout),
   or is that out of scope for a first engagement?
5. **License.** What is the current license of `Genesis` (the GitHub API did not
   surface an SPDX id at verification time)?
6. **Conformance listing.** Would Genesis consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0322 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`Genesis-Embodied-AI/Genesis`](https://github.com/Genesis-Embodied-AI/Genesis)
pointing at this RFC (the repo has both enabled). If the maintainers prefer
another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 29,168 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, demo-shaped fit, fast-moving target).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international community / academic consortium; default policy
      passes at the simulator layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Genesis is one
      simulator among many, the same primitive runs on real hardware).
