---
rfc: 0319
title: ros2_control (hardware-interface and controller framework) integration, request for comment from the ros2_control maintainers
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

# RFC-0319: ros2_control integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

[RFC-0200](0200-ros2-core-outreach.md) (Move #16) engaged the ROS 2 substrate
spine: the core stack, the DDS layer, SLAM, autopilots. It deliberately did not
touch the layer where URML's Layer-1 Hardware Abstraction actually lands on
hardware: **`ros2_control`**, the framework that owns the seam between a
controller and a real (or simulated) actuator. This RFC opens that engagement
against [`ros-controls/ros2_control`](https://github.com/ros-controls/ros2_control)
and **requests review and feedback from the ros2_control maintainers**.

`ros2_control` is the anchor for URML's actuation-control engagement. This RFC
addresses the framework family as one conversation: the `hardware_interface`
(command/state interfaces), the `controller_manager` and `resource_manager`
(interface claiming and arbitration), and the sibling repos that orbit them —
[`ros2_controllers`](https://github.com/ros-controls/ros2_controllers),
[`gz_ros2_control`](https://github.com/ros-controls/gz_ros2_control),
`control_toolbox`, `realtime_tools`, `control_msgs`, `kinematics_interface`.
Those siblings are tracked in the ledger but not posted separately; the
engagement rides this thread (the maintainer community is shared).

URML composes **above** `ros2_control`: URML intent → validated Layer-2
primitives → `ros2_control` controllers and command interfaces → hardware. The
differentiator is **static validation against the capability manifest and the
active safety envelope before any command interface is claimed**.

## Motivation

`ros2_control` is the de-facto hardware abstraction and real-time control
framework for ROS 2. It is exactly the substrate layer URML's Layer-1
([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) abstracts
over, which makes it the single highest-fit substrate engagement still open:

1. **It owns the actuator seam.** A `hardware_interface` plugin exports
   `command_interfaces` and `state_interfaces` (position, velocity, effort, …)
   per joint; the `controller_manager` loads controllers that claim those
   interfaces; the `resource_manager` arbitrates the claims. This is precisely
   the boundary URML's manifest declares capability over and the validator
   guards before motion.
2. **It is substrate-shaped the way URML needs.** `ros2_control` already
   separates *what the hardware exposes* (the `<ros2_control>` description) from
   *what realizes a motion* (the controller). URML's Layer-1 / Layer-2 split
   mirrors that separation. The acid test holds: a URML primitive that maps onto
   a `ros2_control` controller must still map onto a zero-ROS runtime, and it
   does — `ros2_control` is one Layer-1 target among many.
3. **It is where "validate before you move" pays off.** `resource_manager`
   arbitrates interface claims at runtime. URML's contribution is one layer up
   and earlier: a static check, before any controller is activated, that the
   declared capability and the safety envelope admit the requested intent.

Repo at [`ros-controls/ros2_control`](https://github.com/ros-controls/ros2_control)
(909 stars, actively developed, Issues enabled, Discussions disabled — design
questions go to Issues / the ROS Control Working Group). License is asked as a
question below (the org's repos are understood to be Apache-2.0; the GitHub API
did not surface an SPDX id at verification time).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_control_cell.yaml` fixture)

| URML field | Maps to ros2_control attribute |
|---|---|
| `robot_id`, `description` | Deployment identity (not a `ros2_control` concept; carried at the manifest envelope) |
| `mobility.drive_type: differential` | `diff_drive_controller` (`ros2_controllers`) over two velocity command interfaces |
| `mobility.drive_type: omnidirectional` / `ackermann` | `mecanum_drive_controller` / `ackermann_steering_controller` |
| `mobility.max_velocity` | Controller velocity limit (URDF joint limits + controller parameters); conjoined with the envelope |
| `manipulation.arm_count` + joints | `<ros2_control>` hardware joints driven by a `joint_trajectory_controller` |
| `manipulation.grippers[].kind` / `force_max_n` | `gripper_action_controller` / `forward_command_controller` over the gripper command interface; force bound checked statically |
| `perception.sensors[]` | `ros2_control` `SensorInterface` state interfaces (force/torque, IMU) where the sensor is on the control bus |
| Safety envelope limits (Pass 3) | URDF joint limits + the `joint_limits` interface; URML conjoins strictest-wins before motion |

### What URML v0.1 does not yet express for ros2_control

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Per-joint command/state-interface declaration.** URML declares capability
   blocks (`mobility`, `manipulation`), not the `position | velocity | effort`
   command/state interfaces a `<ros2_control>` tag enumerates per joint. A
   future Spec RFC could add an optional interface-granularity declaration.
2. **Controller-type declaration.** URML maps a primitive to an *outcome*
   (`move_to`, `grasp`), not to a named controller. Whether the manifest should
   declare which controllers a deployment exposes (so the adapter's
   primitive → controller binding is checkable) is an open Spec question.
3. **ros2_control version / ROS distro declaration.** `ros2_control` spans ROS 2
   distros (Humble, Jazzy, Rolling). URML's substrate manifest does not yet
   declare the distro / framework version it targets.

### Compatibility notes

- **Vendor org.** [`ros-controls`](https://github.com/ros-controls) — community
  governance, ROS Control Working Group.
- **Engagement repo.** [`ros-controls/ros2_control`](https://github.com/ros-controls/ros2_control)
  — actively developed; the framework anchor.
- **Family repos (folded into this thread).** `ros2_controllers`,
  `gz_ros2_control` (the simulation-side hardware interface; the natural vehicle
  for a hermetic validated-intent demo without real hardware), `control_toolbox`,
  `realtime_tools`, `control_msgs`, `kinematics_interface`, `ros2_control_demos`.
- **Origin.** Community / multi-national, ROS 2 ecosystem. Passes US-federal
  default policy (open-source framework, no provenance gate at the framework
  layer).
- **License fit.** Understood to be Apache-2.0; asked below as a question.
- **Substrate-neutrality.** `ros2_control` is one Layer-1 target among many;
  the same primitives map to PX4, a vendor SDK, or a zero-ROS runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The interface-granularity,
  controller-type, and distro-version declarations are queued Spec RFCs.
- Reference runtime: URML's existing [`reference/ros2-runtime/`](../../reference/ros2-runtime/)
  adapter speaks to ROS 2 action/topic interfaces. A `ros2_control` mapping
  would route a primitive's motion goal to a `controller_manager`-managed
  controller; the planned `ros2_control_cell.yaml` fixture would prove it
  hermetically against `mock_components` / `gz_ros2_control`.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Family-as-one-thread.** Folding `ros2_controllers` / `gz_ros2_control` /
  `control_toolbox` into one Issue risks under-serving a repo whose maintainers
  would prefer a dedicated thread. Justified by the shared maintainer community
  and to avoid spamming one org; the ledger records each sibling, and a fork is
  cheap if a maintainer asks for it.
- **Interface-granularity tension.** URML's capability-block altitude is coarser
  than `ros2_control`'s per-joint interfaces. The right granularity for URML's
  manifest is genuinely open (question 1 below).

## Alternatives considered

1. **Fold ros2_control into RFC-0200 (ROS 2 core).** Rejected. `ros2_control` is
   a distinct framework with its own maintainers and its own
   hardware-abstraction story; it deserves a dedicated request for comment, not
   a footnote on the core-stack thread.
2. **One RFC per ros-controls repo (ros2_control, ros2_controllers,
   gz_ros2_control, …).** Rejected. Carpet-bombing one org with four-plus Issues
   in a day is the pattern that has drawn AI-content closes elsewhere. One anchor
   thread that names the family is more respectful and just as discoverable.
3. **Engage at the controller level (ros2_controllers) instead of the
   framework.** Rejected as the anchor. The framework (`hardware_interface` +
   `controller_manager` + `resource_manager`) is the abstraction URML's Layer-1
   maps onto; controllers are the realizers below it.

## Prior art

- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent
  substrate engagement; this RFC is the actuation-control layer it deferred.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md) — motion planning
  *above* `ros2_control`; URML composes above both.
- [RFC-0038 (ROS-Industrial outreach)](0038-ros-industrial-consortium.md) — sibling
  ROS-ecosystem engagement; see also [RFC-0322](0322-ros2-canopen-outreach.md).
- [RFC-0321 (ros2_canopen outreach)](0321-ros2-canopen-outreach.md),
  [RFC-0320 (ethercat_driver_ros2 outreach)](0320-ethercat-driver-ros2-outreach.md)
  — sibling Move #23 RFCs: the fieldbus hardware interfaces *under*
  `ros2_control`.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) — URML's
  Hardware Abstraction layer, the spec surface this engagement exercises.

## Unresolved questions

For the ros2_control maintainers:

1. **Interface-declaration granularity.** Should URML's capability manifest
   declare command/state interfaces per joint (`position | velocity | effort`)
   to mirror the `<ros2_control>` description, or stay at the capability-block
   altitude and let the adapter resolve interfaces from the robot's URDF?
2. **Primitive → controller binding.** URML maps a primitive (`move_to`,
   `grasp`) to an outcome, not a controller. Is the right adapter boundary
   "URML primitive → `controller_manager` activate + a
   `joint_trajectory_controller` goal", and should the manifest declare which
   controllers a deployment exposes?
3. **Static vs runtime arbitration.** URML validates statically, before any
   command interface is claimed; `resource_manager` arbitrates claims at runtime.
   Do these complement cleanly, or is there overlap we should avoid?
4. **Hermetic demo vehicle.** Is `gz_ros2_control` (or `mock_components`) the
   right vehicle for a hermetic URML demo — validated intent → controller →
   simulated hardware — with no real robot in the loop?
5. **Version / distro declaration.** How should URML's substrate manifest declare
   the ROS 2 distro and `ros2_control` version a deployment targets?
6. **License.** What is the current license of the `ros-controls` repos (the
   GitHub API did not surface an SPDX id at verification time)?
7. **Conformance listing.** Would `ros2_control` consider a project link to
   URML's compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0319 ships as a single RFC document PR alongside the Move #23 ledger
([`examples/lighthouses/outreach-move23.yaml`](../../examples/lighthouses/outreach-move23.yaml))
and the post bodies
([`examples/lighthouses/posts-move23.md`](../../examples/lighthouses/posts-move23.md)).
The sibling `ros-controls` repos share this row; a dedicated ledger row is added
only if the engagement forks to one of them.

## How to respond

The live channel is a GitHub Issue on
[`ros-controls/ros2_control`](https://github.com/ros-controls/ros2_control)
pointing at this RFC (Discussions are disabled on the repo). If the maintainers
prefer the ROS Control Working Group or ROS Discourse, URML will move the thread
there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (909 stars, not archived, Issues enabled,
      Discussions disabled, last push 2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, family-as-one-thread, interface-granularity
      tension).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: community ROS 2 framework; default policy passes at the
      framework layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; `ros2_control` is one
      Layer-1 target among many, composed-above not assumed).
