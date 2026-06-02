---
rfc: 0320
title: ethercat_driver_ros2 (EtherCAT fieldbus hardware interface) integration, request for comment from the ICube-Robotics maintainers
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

# RFC-0320: ethercat_driver_ros2 integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's hardware interface, and requests
review from that target's maintainers. It does not modify URML's normative
surface.

## Summary

[RFC-0319](0319-ros2-control-outreach.md) opens URML's engagement with the
`ros2_control` framework. This sibling RFC reaches the **fieldbus** layer
directly beneath it: [`ICube-Robotics/ethercat_driver_ros2`](https://github.com/ICube-Robotics/ethercat_driver_ros2),
a `ros2_control` `SystemInterface` that drives EtherCAT modules (servo drives,
I/O, sensors) over the EtherCAT real-time bus. It **requests review and feedback
from the ICube-Robotics maintainers**.

This is a **Tier A fieldbus-substrate** engagement, distinct from RFC-0319's
framework anchor: a different org and a different mapping concern (real-time bus
topology, PDO/SDO objects, distributed clocks). The underlying master library
[`OpenEtherCATsociety/SOEM`](https://github.com/OpenEtherCATsociety/SOEM) is
tracked in the ledger and folded into this thread (engagement rides this RFC; no
separate post to SOEM).

URML composes **above** the fieldbus: URML intent → validated Layer-2 primitives
→ `ros2_control` controllers → `ethercat_driver_ros2` command interfaces → EtherCAT
slaves. URML never reaches into the bus; it validates the declared capability and
the safety envelope before any command interface is claimed.

## Motivation

EtherCAT is the dominant real-time fieldbus in industrial motion control. When a
URML program ultimately commands a servo on an EtherCAT bus, `ethercat_driver_ros2`
is the seam that maps a `ros2_control` command interface to a slave's PDO
(process-data object). URML benefits from documenting the engagement because:

1. **It grounds the substrate-neutrality claim at the bus level.** URML's acid
   test is that a primitive maps onto any Layer-1 target. EtherCAT is the
   hardest, most real-time-sensitive end of that spectrum; a clean mapping here
   is strong evidence the abstraction is not ROS-shaped by accident.
2. **It is `ros2_control`-native.** `ethercat_driver_ros2` is a
   `hardware_interface` plugin, so the RFC-0319 mapping carries straight through:
   URML primitive → controller → EtherCAT command interface. The added concern
   is *what the bus exposes* — the slave modules and their objects.
3. **The fieldbus is exactly Layer 0.** URML deliberately does not model the
   transport (RFC-0006's link roles draw that line). EtherCAT topology, distributed
   clocks, and PDO mapping are substrate configuration; URML declares capability,
   not bus wiring. This RFC is a chance to confirm that boundary with maintainers
   who live at it.

Repo at [`ICube-Robotics/ethercat_driver_ros2`](https://github.com/ICube-Robotics/ethercat_driver_ros2)
(308 stars, Issues **and** Discussions enabled, not archived). License is asked
as a question (the GitHub API did not surface an SPDX id at verification time;
understood to be Apache-2.0). ICube-Robotics is the robotics group of ICube
Laboratory, University of Strasbourg (France) — NATO-allied; passes US-federal
default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_control_ethercat_cell.yaml` fixture)

| URML field | Maps to ethercat_driver_ros2 attribute |
|---|---|
| `manipulation` joints / `mobility` drive | `ros2_control` joints whose command interfaces bind to EtherCAT servo-drive PDOs (CiA-402 control word / target position) |
| `manipulation.grippers[].kind` | A digital-output / drive slave module addressed as a command interface |
| `perception.sensors[]` (force/torque, on-bus) | EtherCAT sensor-slave state interface (PDO read) |
| `mobility.max_velocity`, envelope limits | Conjoined with the drive's configured limits; URML checks before the command interface is written |
| (substrate-config, not a URML field) | EtherCAT topology, slave addresses, PDO/SDO mapping, distributed-clock sync — Layer 0, declared in the driver's config, not the URML manifest |

### What URML v0.1 does not yet express for ethercat_driver_ros2

Manifest gaps surfaced by the mapping, flagged as *queued Spec RFCs* for separate
follow-up. **Not proposed here.**

1. **Fieldbus-class hint.** URML's substrate manifest does not declare the
   fieldbus a deployment uses (EtherCAT / CANopen / EtherNet-IP). A future Spec
   RFC could add an optional fieldbus-class hint for envelope reasoning about
   real-time guarantees (it would not model the bus itself — that stays Layer 0).
2. **Drive-profile awareness.** CiA-402 (the EtherCAT servo-drive profile) defines
   operation modes (profile position, cyclic synchronous position/velocity/torque).
   URML maps a primitive to an outcome, not a drive mode; whether the manifest
   should surface the mode is shared with RFC-0319's controller-type question.

### Compatibility notes

- **Vendor org.** [`ICube-Robotics`](https://github.com/ICube-Robotics) — ICube
  Laboratory robotics group, University of Strasbourg.
- **Engagement repo.** [`ICube-Robotics/ethercat_driver_ros2`](https://github.com/ICube-Robotics/ethercat_driver_ros2)
  — a `ros2_control` `SystemInterface` for EtherCAT.
- **Underlying library (folded into this thread).**
  [`OpenEtherCATsociety/SOEM`](https://github.com/OpenEtherCATsociety/SOEM) — the
  Simple Open EtherCAT Master the driver builds on (1.9k stars).
- **Origin.** France (ICube / University of Strasbourg). NATO-allied; passes
  US-federal default policy.
- **License fit.** Understood to be Apache-2.0; asked below. SOEM's license is a
  separate question if engagement forks to it.
- **Substrate-neutrality.** EtherCAT is one fieldbus among several; the same
  URML primitives map to CANopen ([RFC-0321](0321-ros2-canopen-outreach.md)) or a
  zero-fieldbus runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The fieldbus-class hint is a queued
  Spec RFC.
- Reference runtime: no change. The mapping rides RFC-0319's `ros2_control`
  adapter path; EtherCAT is the bus beneath the command interface, configured in
  the driver, not the URML manifest.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). RFC-0319 stands; this RFC adds the
EtherCAT fieldbus as a sibling substrate target beneath it.

## Drawbacks

- **Proposal-only.**
- **Depth without a demo.** A faithful EtherCAT demo needs real hardware or a
  slave simulator; URML's hermetic-demo posture favors `mock_components` /
  `gz_ros2_control` (RFC-0319). This RFC's value is the boundary confirmation,
  not a runnable EtherCAT example yet.
- **Two fieldbus RFCs in one wave.** RFC-0320 (EtherCAT) and RFC-0321 (CANopen)
  both exist. Justified: they are different buses with different device models,
  and each has a distinct maintainer org. The shared `ros2_control` framing
  (RFC-0319) keeps them coherent.

## Alternatives considered

1. **Fold EtherCAT into the RFC-0319 anchor.** Rejected. `ethercat_driver_ros2`
   is a different org (ICube-Robotics, not ros-controls) and a distinct
   real-time-bus mapping; it earns its own request for comment.
2. **Engage SOEM directly instead of the ROS 2 driver.** Rejected as the anchor.
   SOEM is the master library beneath the driver; the `ros2_control`-native
   driver is where URML's primitive → command-interface mapping actually lands.
   SOEM is folded in and reachable if the engagement forks.
3. **Model EtherCAT topology in the URML manifest.** Rejected. Bus wiring is
   Layer 0; modelling it would fail the substrate-neutrality acid test
   (RFC-0006 draws the same line for link transports).

## Prior art

- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md) — the
  framework anchor; this RFC is the fieldbus beneath it.
- [RFC-0321 (ros2_canopen outreach)](0321-ros2-canopen-outreach.md) — sibling
  Move #23 RFC; the CANopen fieldbus peer.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md) —
  why URML models abstract link roles, not transports; the same logic keeps the
  fieldbus at Layer 0.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) — URML's
  Hardware Abstraction layer.

## Unresolved questions

For the ICube-Robotics maintainers:

1. **Mapping boundary.** Is the right URML boundary "URML primitive → controller
   → `ethercat_driver_ros2` command interface", with the slave/PDO mapping left
   entirely in the driver's config (Layer 0)? Does anything about EtherCAT break
   that clean separation?
2. **Drive profiles.** For CiA-402 drives, should URML's manifest surface the
   operation mode (profile position vs cyclic synchronous position), or is that
   firmly substrate configuration?
3. **Real-time guarantees.** Is a fieldbus-class hint in URML's substrate manifest
   useful for envelope reasoning about real-time bounds, or is it noise at the
   intent layer?
4. **License.** What is the current license of `ethercat_driver_ros2` (the GitHub
   API did not surface an SPDX id at verification time)?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0320 ships as a single RFC document PR alongside the Move #23 ledger and post
bodies. The `OpenEtherCATsociety/SOEM` row in the ledger shares this RFC; a
dedicated row is added only if the engagement forks to SOEM.

## How to respond

The live channel is a GitHub Issue or Discussion on
[`ICube-Robotics/ethercat_driver_ros2`](https://github.com/ICube-Robotics/ethercat_driver_ros2)
pointing at this RFC (the repo has both enabled).

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (308 stars, not archived, Issues and
      Discussions enabled, last push 2026-03-06).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, no runnable EtherCAT demo, two fieldbus
      RFCs).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs.
- [x] Provenance: France / ICube; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed (substrate-neutral; EtherCAT is one
      fieldbus among many, the bus stays at Layer 0).
