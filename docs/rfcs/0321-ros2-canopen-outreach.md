---
rfc: 0321
title: ros2_canopen (CANopen device-profile fieldbus) integration, request for comment from the ros-industrial / ros2_canopen maintainers
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

# RFC-0321: ros2_canopen integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

[RFC-0319](0319-ros2-control-outreach.md) opens URML's engagement with the
`ros2_control` framework; [RFC-0320](0320-ethercat-driver-ros2-outreach.md)
reaches the EtherCAT fieldbus beneath it. This sibling RFC reaches the **CANopen**
fieldbus: [`ros-industrial/ros2_canopen`](https://github.com/ros-industrial/ros2_canopen),
the CANopen driver framework for ROS 2, which exposes CANopen devices (notably
CiA-402 motion-control drives) through a `ros2_control` `SystemInterface`. It
**requests review and feedback from the ros2_canopen maintainers**.

This is a **distinct repo and conversation** from URML's prior ROS-Industrial
consortium engagement ([RFC-0038](0038-ros-industrial-consortium.md)). RFC-0038
was a consortium-level touch; this RFC is a specific technical request about the
`ros2_canopen` device-profile mapping. It cross-links RFC-0038 and does **not**
re-pitch the consortium.

The underlying CANopen stack
[`CANopenNode/CANopenNode`](https://github.com/CANopenNode/CANopenNode) is tracked
in the ledger and folded into this thread (engagement rides this RFC).

URML composes **above** the fieldbus: URML intent → validated Layer-2 primitives
→ `ros2_control` controllers → `ros2_canopen` command interfaces → CANopen
devices.

## Motivation

CANopen is the established device-profile fieldbus for motion control, I/O, and
sensors over CAN, widely used where EtherCAT is overkill or where existing CAN
infrastructure rules. `ros2_canopen` brings CANopen devices into `ros2_control`
via the CiA-402 motion-control profile. URML benefits from documenting the
engagement because:

1. **It completes the fieldbus pair.** With EtherCAT (RFC-0320) and CANopen
   (this RFC), URML's `ros2_control` mapping covers the two dominant industrial
   buses through the same primitive → controller → command-interface path. Two
   buses, one abstraction is a strong substrate-neutrality data point.
2. **CiA-402 is a clean, standardized device model.** CANopen object dictionaries
   and the CiA-402 state machine are well-specified. The mapping question is
   sharp: which parts are capability URML should declare, and which are object
   dictionary entries the driver owns?
3. **It is `ros2_control`-native.** Like `ethercat_driver_ros2`, `ros2_canopen`
   presents a `hardware_interface`, so RFC-0319's mapping carries through; the
   added concern is the CANopen object dictionary and node addressing (Layer 0).

Repo at [`ros-industrial/ros2_canopen`](https://github.com/ros-industrial/ros2_canopen)
(278 stars, actively developed, Issues enabled, Discussions disabled, not
archived). License is asked as a question (the GitHub API did not surface an SPDX
id at verification time; understood to be Apache-2.0). ros-industrial is a
US-and-allied consortium; passes US-federal default policy.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_control_canopen_cell.yaml` fixture)

| URML field | Maps to ros2_canopen attribute |
|---|---|
| `manipulation` joints / `mobility` drive | CANopen CiA-402 drive nodes whose command interfaces bind to the driver's `ros2_control` joints |
| `manipulation.grippers[].kind` / `force_max_n` | A CiA-402 drive or digital-I/O node addressed as a command interface; force bound checked statically |
| `perception.sensors[]` (on-bus) | A CANopen sensor node's TPDO mapped to a `ros2_control` state interface |
| `mobility.max_velocity`, envelope limits | Conjoined with the drive's CiA-402 limit objects; URML checks before the command interface is written |
| (substrate-config, not a URML field) | CAN bitrate, node IDs, object dictionary / EDS files, PDO mapping, NMT state — Layer 0, in the driver config, not the URML manifest |

### What URML v0.1 does not yet express for ros2_canopen

Manifest gaps surfaced by the mapping, flagged as *queued Spec RFCs* for separate
follow-up. **Not proposed here.**

1. **Fieldbus-class hint.** Shared with RFC-0320: URML's substrate manifest does
   not declare the fieldbus (CANopen / EtherCAT / …). A future optional hint is
   queued.
2. **Device-profile operation mode.** The CiA-402 mode (profile position vs
   cyclic synchronous) is, like RFC-0320's, a candidate the controller-type Spec
   question (RFC-0319) subsumes.

### Compatibility notes

- **Vendor org.** [`ros-industrial`](https://github.com/ros-industrial) — the
  ROS-Industrial consortium.
- **Engagement repo.** [`ros-industrial/ros2_canopen`](https://github.com/ros-industrial/ros2_canopen)
  — CANopen driver framework presenting a `ros2_control` `SystemInterface`.
- **Underlying stack (folded into this thread).**
  [`CANopenNode/CANopenNode`](https://github.com/CANopenNode/CANopenNode) — a
  widely used open CANopen protocol stack (1.9k stars).
- **Origin.** ROS-Industrial consortium (US and allied membership). Passes
  US-federal default policy.
- **License fit.** Understood to be Apache-2.0; asked below.
- **Substrate-neutrality.** CANopen is one fieldbus among several; the same URML
  primitives map to EtherCAT (RFC-0320) or a zero-fieldbus runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The fieldbus-class hint is the same
  queued Spec RFC referenced by RFC-0320.
- Reference runtime: no change. The mapping rides RFC-0319's `ros2_control`
  adapter path; CANopen is the bus beneath the command interface.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). RFC-0319/0320 stand; this RFC adds
the CANopen fieldbus as a sibling substrate target.

## Drawbacks

- **Proposal-only.**
- **No runnable demo yet.** Like EtherCAT, a faithful CANopen demo needs hardware
  or a CAN simulator; URML's hermetic demo path stays on `mock_components` /
  `gz_ros2_control` (RFC-0319). Value here is the boundary confirmation.
- **Adjacency to RFC-0038.** A separate touch to a ros-industrial repo risks
  reading as a re-pitch of the consortium. Mitigated by framing this strictly as
  the `ros2_canopen` device-profile mapping and cross-linking RFC-0038.

## Alternatives considered

1. **Fold CANopen into RFC-0319 or RFC-0320.** Rejected. CANopen is a distinct
   bus with a distinct device model (CiA-402 object dictionaries), and
   `ros2_canopen` is a distinct repo with its own maintainers.
2. **Treat it under the existing ROS-Industrial engagement (RFC-0038).** Rejected.
   RFC-0038 is a consortium-level conversation; the `ros2_canopen` mapping is a
   specific technical request that deserves its own thread on the repo. RFC-0038
   is cross-linked, not re-opened.
3. **Engage CANopenNode directly.** Rejected as the anchor. CANopenNode is the
   protocol stack beneath the ROS 2 driver; the `ros2_control`-native driver is
   where URML's mapping lands. CANopenNode is folded in and reachable on a fork.

## Prior art

- [RFC-0319 (ros2_control outreach)](0319-ros2-control-outreach.md) — the
  framework anchor.
- [RFC-0320 (ethercat_driver_ros2 outreach)](0320-ethercat-driver-ros2-outreach.md)
  — sibling Move #23 RFC; the EtherCAT fieldbus peer.
- [RFC-0038 (ROS-Industrial consortium)](0038-ros-industrial-consortium.md) —
  prior consortium-level engagement; cross-linked, not re-pitched.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) — URML's
  Hardware Abstraction layer.

## Unresolved questions

For the ros2_canopen maintainers:

1. **Mapping boundary.** Is "URML primitive → controller → `ros2_canopen` command
   interface" the right boundary, with node IDs, EDS/object-dictionary, and PDO
   mapping left in the driver config (Layer 0)?
2. **CiA-402 modes.** Should URML's manifest surface the CiA-402 operation mode,
   or is that firmly substrate configuration?
3. **EtherCAT vs CANopen path.** For a deployment that could use either bus, is
   there a preference for how URML should present the choice (a fieldbus-class
   hint, or no manifest distinction at all)?
4. **License.** What is the current license of `ros2_canopen` (the GitHub API did
   not surface an SPDX id at verification time)?
5. **Conformance listing.** Would the project consider a link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0321 ships as a single RFC document PR alongside the Move #23 ledger and post
bodies. The `CANopenNode/CANopenNode` row shares this RFC; a dedicated row is
added only if the engagement forks to it.

## How to respond

The live channel is a GitHub Issue on
[`ros-industrial/ros2_canopen`](https://github.com/ros-industrial/ros2_canopen)
pointing at this RFC (Discussions are disabled on the repo). If the maintainers
prefer ROS Discourse or the ROS-Industrial channels, URML will move the thread
there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (278 stars, not archived, Issues enabled,
      Discussions disabled, last push 2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, no runnable demo, RFC-0038 adjacency).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps flagged as queued Spec RFCs.
- [x] Provenance: ROS-Industrial consortium (US and allied); default policy
      passes.
- [x] CLAUDE.md compliance check passed (substrate-neutral; CANopen is one
      fieldbus among many, the bus stays at Layer 0).
