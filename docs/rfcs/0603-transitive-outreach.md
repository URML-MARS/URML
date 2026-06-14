---
rfc: 0603
title: Transitive (robot fleet management) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0603: Transitive (robot fleet management) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the service-robotics wave (Move #56).

## Summary

[`transitiverobotics/transitive`](https://github.com/transitiverobotics/transitive) (Apache-2.0) is an open full-stack framework for building web-based robot management and mission-control applications across a fleet. A fleet dashboard that dispatches missions to many robots is precisely the layer URML's multi-robot roster speaks to. This RFC asks where the two meet.

## The mapping (URML beside Transitive)

- **A validated-intent layer a dashboard dispatches.** Transitive provides the web-and-cloud plumbing to build a fleet mission-control app. URML's candidate role is the typed, validated intent that such an app dispatches: declare the mission per robot, validate it against each robot's declared capabilities and a safety envelope, address the fleet through a roster with cross-robot constraints (RFC-0286 / RFC-0291), then send it through Transitive's transport. Transitive keeps the app framework and the connectivity; URML is the checkable intent that travels over it.
- **Fleet as a roster.** A managed fleet maps onto URML's roster directly, which is what makes a multi-robot mission validatable before it is dispatched from the dashboard.

## What is asked

1. Is a typed, validated intent layer (a per-robot mission checked against each robot's capabilities, addressed via a fleet roster) a useful thing for a Transitive-built mission-control app to dispatch?
2. Does URML's multi-robot roster map onto how Transitive models a managed fleet?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot roster (RFC-0286), cross-robot deconfliction (RFC-0291), the capability manifest, and the safety-envelope validation. Part of Move #56; the fleet-management framework of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `transitiverobotics/transitive` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move56.yaml`.
