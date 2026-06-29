---
rfc: 0650
title: Vortex AUV (vortexntnu/vortex-auv) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-29
updated: 2026-06-29
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

# RFC-0650: Vortex AUV integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #65 (domain-vertical lane).

## Summary

[`vortexntnu/vortex-auv`](https://github.com/vortexntnu/vortex-auv) (Vortex NTNU, the NTNU underwater robotics team in Trondheim) is a guidance, navigation, and control stack for autonomous underwater vehicles, dispatching setpoints down to thruster control. URML is a small Apache-2.0 language for declaring what a vehicle can do and checking an intended action against that declaration before it runs. An AUV is a good fit, because underwater the cost of dispatching an inadmissible action (past depth rating, outside a geofence, beyond thruster authority) is high and recovery is hard.

## The relationship (URML beside vortex-auv)

A mission is a goal plus constraints: reach this waypoint, hold this depth, stay inside this operating volume. URML can declare the AUV's depth rating, thruster envelope, and the mission geofence, and validate a commanded setpoint against that declaration before the GNC stack drives the thrusters. It is a static admissibility check on the intent, not a controller and not a navigation filter.

URML does not do guidance, estimation, or control. It declares the vehicle's envelope and confirms a commanded action is inside it before dispatch.

## What is asked

1. For an AUV GNC stack, is a declared depth-and-thruster-and-geofence envelope check on a commanded setpoint useful before dispatch, or is that already enforced inside guidance in practice?
2. Would a small worked example mapping an AUV mission setpoint onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to an AUV guidance-navigation-control stack. MIT; Vortex NTNU (student underwater robotics team), Norway. Part of Move #65.

## Implementation note

Outreach only. The post is a GitHub Issue on `vortexntnu/vortex-auv` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move65.yaml`.
