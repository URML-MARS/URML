---
rfc: 0529
title: OSGAR integration — request for comment
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

# RFC-0529: OSGAR integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It is the anchor of the domain / standards / conceptual-peer wave (Move #48), the final lane of the 2026-06-13 candidate search.

## Summary

[`robotika/osgar`](https://github.com/robotika/osgar) (MIT, active, Czech Republic) is Team Robotika's open framework for a heterogeneous fleet of wheeled, tracked, and flying robots — built for underground mapping and search (DARPA SubT). URML is interesting as the intent layer above a multi-robot, multi-substrate fleet: a high-level mission becomes typed, per-robot intents, validated against each robot's declared capabilities and the fleet's coordination constraints. This RFC asks whether the mapping is useful.

## The mapping (URML beside OSGAR)

- **Fleet roster + per-robot manifests.** A heterogeneous OSGAR fleet maps onto URML's multi-robot roster (RFC-0286): each robot is a member with its own capability manifest, and a mission addresses members or the fleet. Cross-robot deconfliction (RFC-0291) is the kind of constraint underground operations need.
- **Validated intent, then dispatch.** URML validates a mission against the members' capabilities and the coordination constraints, then dispatches to OSGAR's nodes. URML is the typed intent + fleet-coordination gate; OSGAR stays the runtime driving the robots.

## What is asked

Request for comment from the OSGAR maintainers:

1. Does a URML fleet roster (per-robot manifests + cross-robot constraints) fit a heterogeneous SubT-style fleet?
2. Is a validated mission-intent layer above OSGAR's nodes interesting for underground / search operations?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot fleet addressing (RFC-0286) and cross-robot deconfliction (RFC-0291), and the decide-then-do split (RFC-0002). Anchor of Move #48, the domain / standards wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `robotika/osgar` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
