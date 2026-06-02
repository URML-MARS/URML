---
rfc: 0326
title: Unity Robotics Hub (Unity <-> ROS simulation bridge) integration, request for comment from the Unity Robotics maintainers
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

# RFC-0326: Unity Robotics Hub integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's simulation bridge, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

Move #24 is URML's simulation and digital-twin wave. This RFC reaches Unity's
ROS-facing simulation surface: [`Unity-Technologies/Unity-Robotics-Hub`](https://github.com/Unity-Technologies/Unity-Robotics-Hub),
the project that bundles the ROS-TCP-Connector and the URDF-Importer so a
Unity scene can stand in for a ROS-controlled robot. It **requests review and
feedback from the Unity Robotics maintainers**, with one honest first question:
is this still maintained, and is this the right venue.

The repo's last push is 2024-11-26, roughly a year and a half stale at
verification time. URML opens this engagement as a maintenance-status check
first and an integration proposal second. If the project is dormant or has
moved, the maintainers' steer on where Unity-based URML simulation should live
is more valuable than the mapping below.

URML composes **above** the Unity bridge: URML intent -> validated Layer-2
primitives -> a ROS-TCP message over ROS-TCP-Connector -> a Unity-simulated
robot. The differentiator is **static validation against the capability
manifest and the active safety envelope before the ROS-TCP message is sent**.

## Motivation

A Unity scene driven over ROS-TCP-Connector is a fast, photoreal way to run a
URML program against a simulated robot with no hardware in the loop. The
project is a natural digital-twin target for URML because:

1. **It is a ROS boundary URML already speaks.** ROS-TCP-Connector relays ROS
   messages between a ROS node and a Unity scene. URML's
   [RFC-0200](0200-ros2-core-outreach.md) engagement already lands intent on
   ROS topics and actions; a Unity-simulated robot is one more endpoint behind
   that same boundary. The acid test holds: the primitives that drive a Unity
   robot are the same ones that drive a real ROS 2 robot or a zero-ROS runtime.
2. **The URDF-Importer aligns a model with URML's manifest.** The URDF-Importer
   brings a robot's URDF into Unity (links, joints, visuals). The same URDF is
   the natural source for a URML capability manifest's frames, joints, and
   reachable workspace, so a single robot description feeds both the simulated
   body and the declared capability the validator checks against.
3. **It is where validate-before-you-move costs nothing to demo.** A simulated
   robot is the cheapest place to show URML's contribution: a static check,
   before the first ROS-TCP message leaves the connector, that the declared
   capability and the safety envelope admit the requested intent.

Repo at [`Unity-Technologies/Unity-Robotics-Hub`](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
(2,523 stars, Issues enabled, Discussions disabled, not archived) with a last
push of 2024-11-26. License is asked as a question below (the GitHub API did not
surface an SPDX id at verification time). Origin: Unity Technologies (United
States); passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `unity_sim_cell.yaml` fixture)

| URML field | Maps to Unity Robotics Hub attribute |
|---|---|
| `robot_id`, `description` | Deployment identity (not a Unity concept; carried at the manifest envelope) |
| `frames`, `declared_locations` | Unity scene transforms / named spawn points; the URDF-Importer's link frames seed the manifest frames |
| `mobility.drive_type`, `mobility.max_velocity` | The simulated articulation body's drive, commanded over a ROS-TCP topic; velocity conjoined with the envelope |
| `manipulation.arm_count` + joints | URDF-Importer joints driven over a ROS-TCP action/topic to the Unity articulation chain |
| `manipulation.grippers[].kind` / `force_max_n` | A simulated gripper joint addressed over ROS-TCP; force bound checked statically before the message is sent |
| `perception.cameras[]` | A Unity camera publishing image messages back over ROS-TCP-Connector |
| `perception.sensors[].measurement_type` | A simulated sensor publishing the matching message type over the connector |
| Safety envelope limits (Pass 3) | URDF joint limits + URML envelope; URML conjoins strictest-wins before the ROS-TCP message |

### What URML v0.1 does not yet express for Unity Robotics Hub

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Simulator-target class hint.** URML's substrate manifest does not declare
   that a deployment targets a simulator (Unity, Webots, Genesis, Isaac Sim)
   rather than hardware. A future Spec RFC could add an optional
   simulator-target class hint so the validator and adapter can reason about a
   sim-only deployment. It would not model the simulator itself.
2. **URDF-derived manifest provenance.** The URDF-Importer and the URML manifest
   both consume the same URDF. Whether the manifest should record that its
   frames and joints were derived from a named URDF (so the two stay in sync) is
   shared with the optional `urdf_ref:` question already noted in
   [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) section 5.

### Compatibility notes

- **Vendor org.** [`Unity-Technologies`](https://github.com/Unity-Technologies)
  (Unity Technologies, the Unity game-engine company).
- **Engagement repo.** [`Unity-Technologies/Unity-Robotics-Hub`](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
  bundles ROS-TCP-Connector (the ROS <-> Unity message relay) and the
  URDF-Importer (robot model import).
- **Origin / policy.** United States (Unity Technologies). Passes US-federal
  default policy (open-source bridge tooling, no provenance gate at the
  simulation layer).
- **License fit.** Not SPDX-detected at verification time; asked below as a
  question.
- **Substrate-neutrality.** Unity is one simulation target among several; the
  same URML primitives map to Webots ([RFC-0234](0234-webots-outreach.md)),
  MuJoCo ([RFC-0060](0060-mujoco-integration.md)), or a real ROS 2 robot. The
  Unity bridge is a ROS endpoint, not a new substrate.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The simulator-target class hint and
  the URDF-derived provenance question are queued Spec RFCs.
- Reference runtime: no change. The mapping rides URML's existing ROS 2 adapter
  path ([`reference/ros2-runtime/`](../../reference/ros2-runtime/)); the Unity
  scene sits behind ROS-TCP-Connector as one more ROS endpoint. A planned
  `unity_sim_cell.yaml` fixture would document the mapping; a runnable demo
  depends on the maintenance answer below.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Apparent dormancy is a real engagement risk.** The repo's last push is
  2024-11-26. A stale project may have no active maintainer to respond, and the
  ROS-TCP-Connector message contracts may have drifted from current ROS 2
  distros. This is stated plainly because it materially lowers the odds of a
  reply, and the first question below treats it as a maintenance-status check
  rather than assuming an active integration partner.
- **Bridge, not substrate.** Unity is reached through a ROS boundary, so this
  engagement adds a simulation endpoint, not a new Layer-1 target. The value is
  a photoreal hermetic demo surface, not a new abstraction.

## Alternatives considered

1. **Fold Unity into RFC-0200 (ROS 2 core).** Rejected. The Unity bridge is a
   distinct project with its own maintainers and its own model-import story
   (URDF-Importer); it earns a dedicated request for comment even though it
   speaks ROS underneath.
2. **Skip Unity because the repo is stale.** Rejected. A maintenance-status
   check is cheap and the answer is itself useful: a confirmed-dormant or
   moved-elsewhere steer tells URML where Unity-based simulation should live,
   and a 2,500-star project is worth one honest question.
3. **Engage Unity's newer simulation tooling instead.** Rejected as the anchor.
   ROS-TCP-Connector plus the URDF-Importer is the documented ROS-facing surface
   that maps onto URML's existing ROS adapter; a newer non-ROS path would be a
   separate, larger engagement and is out of scope for this RFC.

## Prior art

- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md): the ROS
  boundary the Unity bridge relays over; URML composes above both.
- [RFC-0234 (Webots outreach)](0234-webots-outreach.md): sibling simulation
  engagement, the closest in-repo precedent for a robot-simulator target.
- [RFC-0060 (MuJoCo integration)](0060-mujoco-integration.md): sibling
  physics-simulator engagement.
- Sibling Move #24 RFCs: RFC-0322 (Genesis) and RFC-0323 (Isaac Sim), the other
  simulation and digital-twin targets in this wave.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, including the open `urdf_ref:` question (section 5)
  this engagement touches.

## Unresolved questions

For the Unity Robotics maintainers:

1. **Maintenance status and venue.** Is Unity Robotics Hub still maintained, and
   is a GitHub Issue here the right venue for an integration conversation, or has
   the ROS-facing simulation work moved to another repo, forum, or product?
2. **ROS-TCP boundary.** Is "URML intent -> validated primitive -> ROS-TCP
   message over ROS-TCP-Connector -> Unity-simulated robot" the right boundary,
   with URML staying entirely above the connector and never touching the Unity
   scene directly?
3. **URDF-Importer alignment.** Is the URDF a Unity scene imports through the
   URDF-Importer a sound single source for a URML capability manifest's frames,
   joints, and reachable workspace, or do the two diverge in ways URML should
   account for?
4. **License.** What is the current license of Unity-Robotics-Hub (the GitHub
   API did not surface an SPDX id at verification time)?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0326 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue on
[`Unity-Technologies/Unity-Robotics-Hub`](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
pointing at this RFC (Discussions are disabled on the repo). If the project has
moved or the maintainers prefer another venue, URML will follow the steer.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (2,523 stars, not archived, Issues enabled,
      Discussions disabled, last push 2024-11-26; staleness flagged up front).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, apparent dormancy as engagement risk,
      bridge not substrate).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: US (Unity Technologies); default policy passes at the
      simulation layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; Unity is one
      simulation endpoint reached over a ROS boundary, composed-above not
      assumed).
