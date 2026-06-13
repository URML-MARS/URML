---
rfc: 0547
title: OpenRTM-aist integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0547: OpenRTM-aist integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the swarm / multi-robot / alternative-framework wave (Move #49).

## Summary

[`OpenRTM/OpenRTM-aist`](https://github.com/OpenRTM/OpenRTM-aist) (LGPL-2.1, ~25 stars, active, AIST Japan) is RT-Middleware: an implementation of the OMG Robotic Technology Component (RTC) standard, a non-ROS component middleware with a long industrial and academic history. URML is substrate-neutral by design, and an RT-Middleware system is exactly the kind of non-ROS substrate URML should be able to dispatch validated intent to. This RFC asks whether the mapping is useful.

## The mapping (URML beside OpenRTM-aist)

- **A non-ROS substrate.** URML validates an intent against the robot's declared capabilities and a safety envelope, then dispatches to whatever substrate the deployment uses. An RT-Middleware (RTC) system is one such substrate: URML produces the validated call, the RTC components execute it. URML is the typed intent + validation layer; OpenRTM-aist is the component runtime.
- **RTC ports toward a manifest.** An RTC's declared data ports and service ports describe what a component exposes, which maps toward a URML capability manifest the validator can check against.

## What is asked

Request for comment from the OpenRTM-aist maintainers:

1. Is "URML validates intent, then dispatches to RT-Middleware (RTC) components" a sensible substrate mapping?
2. Could an RTC's declared ports inform a URML capability manifest?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's substrate-neutral dispatch model and the decide-then-do split (RFC-0002); the alternative-middleware engagements (RobotRaconteur, RFC-0501). Part of Move #49.

## Implementation note

Outreach only. The post is a GitHub Issue on `OpenRTM/OpenRTM-aist` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is LGPL-2.1; state it, do not ask). Tracked in `examples/lighthouses/outreach-move49.yaml`.
