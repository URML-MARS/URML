---
rfc: 0396
title: blue (Robotic Decision Making Lab) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0396: blue (Robotic Decision Making Lab) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's shipped marine-runtime (a BlueROV adapter over ArduSub/MAVLink), its ROS 2 runtime, and the validate-before-actuate discipline. It anchors a small Robotic-Decision-Making-Lab cluster: `blue` here, with `auv_controllers` and `angler` referenced rather than posted separately.

## Summary

[`blue`](https://github.com/Robotic-Decision-Making-Lab/blue) (Robotic Decision Making Lab, MIT, ~98 stars, Issues + Discussions enabled, active) is a ROS 2 platform for underwater R&D that runs onboard a BlueROV2 over ArduSub. It is the closest external analog to URML's own marine-runtime, which is exactly why it is the anchor of URML's marine wave: URML's BlueRovAdapter dispatches validated intent into the same BlueROV2 / ArduSub substrate `blue` orchestrates. This RFC asks what an underwater capability declaration should carry and whether a validated intent layer above `blue` is interesting.

## The mapping (URML above blue)

URML sits above `blue` as a validated, natural-language intent layer; `blue` and ArduSub execute:

- URML's marine-runtime already drives a BlueROV2 via ArduSub/MAVLink, the same vehicle + flight-controller pairing `blue` targets; URML's ROS 2 runtime meets `blue` on the ROS 2 side.
- The lab's `auv_controllers` (AUV/UVMS controllers on ros2_control) is the control seam URML dispatches validated motion intent to — the same ros2_control framing URML engaged in Move #23 (RFC-0319). The lab's `angler` (underwater vehicle-manipulator systems) is where URML's manipulation primitives (`grasp`/`release`, the RFC-0010 arm work) extend underwater.
- Validate-before-actuate is the point: a command outside the declared depth rating, thruster envelope, or comms regime is refused before it reaches a thruster.

## What is asked

Request for comment from the Robotic Decision Making Lab:

1. What should a URML capability manifest declare to honestly describe an underwater vehicle — depth rating, thruster/actuator configuration, buoyancy/ballast limits, tether vs untethered comms, current/visibility constraints?
2. Is a validated natural-language intent layer above `blue` interesting for the lab's BlueROV2 / UVMS work?
3. Where is the cleanest seam for a URML → `blue` demonstration — the ROS 2 interface, or the `auv_controllers` ros2_control layer?

Nothing here asks the lab to adopt, host, or maintain anything.

## Prior art / context

URML's marine-runtime (BlueRovAdapter) and ROS 2 runtime; the ros2_control engagement (RFC-0319, Move #23) that `auv_controllers` extends; the manipulation work (RFC-0010) that `angler` would exercise underwater. ArduSub itself rides ArduPilot, which URML contacted earlier (the maintainer redirected off GitHub Issues, so ArduPilot is not re-contacted here).

## Implementation note

Outreach only. The post is a GitHub Discussion on `Robotic-Decision-Making-Lab/blue` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). The sibling `auv_controllers` / `angler` repos are referenced in the post, not posted to separately (anchor-plus-fold). Tracked in `examples/lighthouses/outreach-move32.yaml`.
