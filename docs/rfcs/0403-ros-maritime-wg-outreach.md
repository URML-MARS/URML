---
rfc: 0403
title: ROS Maritime Working Group integration — request for comment
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

# RFC-0403: ROS Maritime Working Group integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its community for feedback. It builds on URML's ROS 2 runtime, marine-runtime, and the substrate-neutral capability-manifest model.

## Summary

The [ROS Maritime Working Group](https://github.com/ros-maritime) is the standards-altitude target of URML's marine wave: it stewards [`maritime_interfaces`](https://github.com/ros-maritime/maritime_interfaces) (MIT, standard maritime-autonomy ROS 2 interfaces), an `awesome-maritime-robotics` landscape, and a community charter / monthly meeting. Rather than a single vehicle, the WG is where the field agrees on shared interfaces — exactly the layer a substrate-neutral intent vocabulary should align with. This RFC asks the WG whether URML's typed-intent layer maps cleanly onto the maritime interfaces and whether alignment is of interest.

## The mapping (URML aligned with the maritime interfaces)

URML is a layer above the ROS 2 maritime stack, not a competing interface set:

- URML primitives (`move_to`, `detect`, `measure`, `report`, and the marine vehicle path) lower onto ROS 2 actions/services; where `maritime_interfaces` standardizes those messages, URML should target the standard rather than invent its own, exactly as it targets Nav2 / ros2_control elsewhere.
- URML adds the typed-intent + capability-manifest + safety-envelope validation layer above the interfaces: a natural-language request becomes a typed primitive, is validated against what the vessel declares it can do, and only then dispatches over the standard interfaces.
- The capability-manifest question (what an underwater / surface vessel must declare — depth rating, thruster config, comms regime, environmental limits) is one the WG is well-placed to shape.

## What is asked

Request for comment from the ROS Maritime WG:

1. Does URML's typed-intent layer map cleanly onto `maritime_interfaces`, and where should it target the standard interfaces rather than a generic ROS surface?
2. What should a URML capability manifest declare to describe a maritime vehicle in a way the WG would consider faithful?
3. Is alignment between URML and the maritime interfaces of interest to the group (a Discourse thread or a meeting agenda item)?

Nothing here asks the WG to adopt, host, or maintain anything; this is an alignment conversation.

## Prior art / context

URML's ROS 2 runtime and marine-runtime; the Nav2 (Move #16) and ros2_control (Move #23) engagements as the pattern of targeting standard ROS interfaces rather than inventing parallel ones. This is a working-group engagement (like URML's ROS-Industrial and Eclipse iceoryx touches): the venue is the WG's channels, not a cold vehicle-repo issue.

## Implementation note

Outreach only. The venue is the WG's preferred channel: an Issue on `ros-maritime/maritime_interfaces` (the `community` repo's Issues are disabled) or the ROS Discourse Maritime category / monthly meeting. Posted under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move32.yaml`.
