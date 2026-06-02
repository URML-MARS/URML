---
rfc: 0323
title: NVIDIA Isaac Sim (Omniverse robotics simulator) integration, request for comment from the Isaac Sim maintainers
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

# RFC-0323: NVIDIA Isaac Sim integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

This Move #24 RFC engages [`isaac-sim/IsaacSim`](https://github.com/isaac-sim/IsaacSim),
NVIDIA's Omniverse-based robotics simulator, now open-sourced. It **requests
review and feedback from the Isaac Sim maintainers**.

This is **distinct from [RFC-0050](0050-nvidia-isaac-lab-integration.md)** (NVIDIA
Isaac Lab, the reinforcement-learning training framework that builds on top of
Isaac Sim). Isaac Sim is the simulator application; Isaac Lab is a framework
layered on it. This is a separate repo and a separate conversation, **not a
re-pitch of the NVIDIA relationship** already opened in RFC-0050. NVIDIA Warp
(the differentiable-simulation kernel library) is tracked but folded under this
Isaac engagement; it is not opened as a third NVIDIA thread.

URML's fit with Isaac Sim is the same hermetic-demo shape as the rest of Move #24:
a validated English sentence becomes a URML primitive, the primitive drives a
simulated robot in Isaac Sim through the ROS 2 bridge / Action Graph, and the
robot moves in the simulator with no hardware in the loop. The URML capability
manifest aligns with the USD robot description.

URML composes **above** Isaac Sim: URML intent -> validated Layer-2 primitives ->
the ROS 2 bridge / Action Graph -> a simulated robot in Isaac Sim. The
differentiator is **static validation against the capability manifest and the
active safety envelope before the ROS 2 bridge carries a single command**.

## Motivation

Isaac Sim is the highest-fidelity, USD-native robotics simulator in wide use, and
it speaks ROS 2 natively, which makes it a clean hermetic-demo target for URML:

1. **It closes the demo loop through a real bridge.** Isaac Sim's ROS 2 bridge
   and Action Graph carry commands to a simulated robot. URML's headline path
   (one English sentence moves a robot) runs end to end: validated intent ->
   primitive -> ROS 2 bridge -> simulated motion, no hardware needed.
2. **Its USD robot description is what URML's manifest declares over.** Isaac Sim
   describes robots in USD. URML's Layer-1 capability manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) declares the
   same capability surface (joints, grippers, sensors) at a coarser altitude. The
   manifest and the USD description describe the same robot from two sides.
3. **It is where static validation pays off through the bridge.** The ROS 2
   bridge will carry whatever command is issued. URML's contribution sits one
   layer up and earlier: a static check, before any command crosses the bridge,
   that the declared capability and the safety envelope admit the intent.
4. **It reuses URML's existing ROS 2 path.** URML already speaks ROS 2 action /
   topic interfaces ([RFC-0200](0200-ros2-core-outreach.md)). An Isaac Sim
   mapping rides that path: the bridge is the seam, the simulated robot is the
   target, and the demo is hermetic.

Repo at [`isaac-sim/IsaacSim`](https://github.com/isaac-sim/IsaacSim) (about 3,345
stars, Issues **and** Discussions enabled, not archived, last push 2026-03-31,
now open-sourced). License is asked as a question below (the GitHub API did not
surface an SPDX id at verification time).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `isaac_sim_cell.yaml` fixture)

| URML field | Maps to Isaac Sim attribute |
|---|---|
| `robot_id`, `description` | The simulated robot's stage / prim identity (carried at the manifest envelope) |
| `frames`, `declared_locations` | Stage frames and named target poses a `move_to` resolves against |
| `mobility.drive_type` / `max_velocity` | The simulated base's control mode and velocity command bounds carried over the ROS 2 bridge |
| `manipulation.arm_count` + joints | The arm joints of the USD robot prim, driven via the Action Graph / ROS 2 controllers |
| `manipulation.grippers[].kind` / `force_max_n` | The gripper articulation of the USD prim; force bound checked statically before a `grasp` command crosses the bridge |
| `perception.cameras[]` / `sensors[]` | Isaac Sim render / sensor prims a `capture` / `detect` / `measure` reads through the bridge |
| `perception.object_vocabulary` | The object classes present as prims in the stage that `detect` may name |
| Safety envelope limits (Pass 3) | Conjoined with the USD articulation joint and velocity limits; URML applies strictest-wins before the bridge carries a command |

### What URML v0.1 does not yet express for Isaac Sim

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **USD robot-description alignment.** URML declares capability blocks
   (`mobility`, `manipulation`), not a USD articulation graph. A future Spec RFC
   could add an optional declaration that aligns the manifest with a referenced
   USD robot description (a USD counterpart to the URDF question deferred in
   Layer 1 section 5).
2. **Simulator-target class hint.** URML's substrate manifest does not declare
   that a deployment targets a simulator rather than hardware. A future Spec RFC
   could add an optional simulator-target class hint (shared with RFC-0322).

### Compatibility notes

- **Vendor org.** [`isaac-sim`](https://github.com/isaac-sim) (NVIDIA).
- **Engagement repo.** [`isaac-sim/IsaacSim`](https://github.com/isaac-sim/IsaacSim):
  the Omniverse-based robotics simulator application, now open-sourced.
- **Related but distinct.** Isaac Lab (RFC-0050) builds on Isaac Sim; this is the
  simulator, a separate repo and conversation. NVIDIA Warp is tracked and folded
  under this Isaac engagement, not opened as a third NVIDIA thread.
- **Origin / policy.** United States (NVIDIA). Passes US-federal default policy.
- **License fit.** Asked below as a question (the GitHub API did not surface an
  SPDX id at verification time).
- **Substrate-neutrality.** Isaac Sim is one simulator (and one Layer-1 target)
  among many; the same URML primitives map to Genesis (RFC-0322), MuJoCo
  (RFC-0060), Webots (RFC-0234), or real hardware with no change to the program.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The USD-robot-description alignment and
  the simulator-target class hint are queued Spec RFCs.
- Reference runtime: no change in this RFC. An Isaac Sim mapping rides URML's
  existing ROS 2 path ([`reference/ros2-runtime/`](../../reference/ros2-runtime/)):
  a validated primitive's goal crosses the Isaac Sim ROS 2 bridge / Action Graph
  to a simulated robot. The planned `isaac_sim_cell.yaml` fixture would prove it
  hermetically.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). RFC-0050 (Isaac Lab) stands
untouched; this RFC adds the Isaac Sim simulator as a distinct sibling target. No
existing manifest, fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two NVIDIA threads.** RFC-0050 (Isaac Lab) and this RFC both engage NVIDIA.
  Justified: they are different repos with different maintainers and a different
  mapping concern (RL training framework vs simulator application). Warp is folded
  in rather than opened as a third thread, to avoid over-posting one vendor.
- **Heavy substrate.** A faithful Isaac Sim demo needs the Omniverse runtime,
  which is heavier than the laptop-hermetic MuJoCo / Genesis path. The value here
  is the USD / ROS 2 bridge boundary confirmation; the lightest hermetic demo
  stays on a lighter engine.

## Alternatives considered

1. **Fold Isaac Sim into RFC-0050 (Isaac Lab).** Rejected. Isaac Sim is the
   simulator application and Isaac Lab is a training framework built on it: a
   different repo, a different maintainer surface, and a different mapping
   concern. It earns its own request for comment.
2. **Open a third NVIDIA thread for Warp.** Rejected. Warp is the differentiable
   kernel library beneath the simulator; carpet-bombing one vendor with three
   threads is the pattern that draws AI-content closes elsewhere. Warp is folded
   into this thread and reachable if the engagement forks.
3. **Model the USD stage in the URML manifest.** Rejected. The stage and the
   physics are Layer 0 / substrate concern; URML declares capability over the
   robot prim, not the stage. Modelling the stage would fail the
   substrate-neutrality acid test.

## Prior art

- [RFC-0050 (NVIDIA Isaac Lab integration)](0050-nvidia-isaac-lab-integration.md)
  the related-but-distinct NVIDIA engagement; the RL training framework built
  on Isaac Sim. This RFC is the simulator, not a re-pitch of that relationship.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): sibling simulator
  engagement; the lighter hermetic-demo posture.
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling simulator
  engagement; one engine among many.
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md): the ROS 2 path
  the Isaac Sim bridge mapping rides.
- Sibling Move #24 RFCs: RFC-0322 (Genesis), RFC-0324 (O3DE), RFC-0325 (CARLA),
  RFC-0330 (Eclipse Ditto digital twin).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the Isaac Sim maintainers:

1. **ROS 2 bridge boundary.** Is "URML primitive -> ROS 2 bridge / Action Graph
   -> simulated robot" the right seam, and is the ROS 2 bridge the channel URML
   should target rather than a native Omniverse API?
2. **USD robot-description alignment.** Should URML's capability manifest align
   against the USD robot prim (joints, grippers, sensors), and is there a stable
   USD convention URML should read from?
3. **Relationship to Isaac Lab (RFC-0050).** Is keeping the Isaac Sim engagement
   (this RFC) separate from the Isaac Lab engagement (RFC-0050) the right split
   from your side, or would NVIDIA prefer a single coordinated conversation?
4. **NVIDIA Warp.** Is folding Warp under this engagement (rather than a separate
   thread) sensible, or is Warp a distinct conversation with distinct maintainers?
5. **License.** What is the current license of `IsaacSim` now that it is
   open-sourced (the GitHub API did not surface an SPDX id at verification time)?
6. **Conformance listing.** Would Isaac Sim consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0323 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).
The NVIDIA Warp row in the ledger shares this RFC; a dedicated row is added only
if the engagement forks to Warp.

## How to respond

The live channel is a GitHub Issue or Discussion on
[`isaac-sim/IsaacSim`](https://github.com/isaac-sim/IsaacSim) pointing at this RFC
(the repo has both enabled). If the maintainers prefer the Isaac Lab thread
(RFC-0050) or another NVIDIA channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (about 3,345 stars, not archived, Issues and
      Discussions enabled, last push 2026-03-31, now open-sourced).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two NVIDIA threads, heavy substrate).
- [x] Backward compatibility additive; no spec change. RFC-0050 stands untouched.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: United States (NVIDIA); default policy passes.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Isaac Sim is one
      simulator among many; distinct from the Isaac Lab engagement, RFC-0050).
