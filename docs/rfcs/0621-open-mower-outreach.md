---
rfc: 0621
title: OpenMower (open_mower_ros) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-21
updated: 2026-06-21
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

# RFC-0621: OpenMower (open_mower_ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the outdoor-mobile sub-lane of Move #59.

## Summary

[`ClemensElflein/open_mower_ros`](https://github.com/ClemensElflein/open_mower_ros) (GPL-3.0) is the software for OpenMower, an open, RTK-GPS autonomous lawn mower: a coverage planner, local navigation, and motor control that drive a real cutting machine across a defined area. It is an outdoor robot that executes physical action in a yard, near people, pets, and obstacles. URML is a validated-intent layer that sits above an autonomy stack like this: it declares the job as a typed goal (mow this area) carrying the drive type and an operating envelope (speed ceilings, keep-out and boundary constraints, blade-engagement conditions), and validates that intent against the machine's declared capabilities before the mower moves or cuts. URML does not plan coverage or drive motors; it declares and checks. This is a request for comment, framed as cross-citation given the GPL-3.0 license.

## The relationship (URML beside OpenMower)

- **Declare the job and its envelope, leave the autonomy to OpenMower.** A mow job is a goal plus constraints: an area to cover, a boundary not to cross, a speed not to exceed, conditions under which the blade may run. URML expresses that as typed intent, validates it against a capability manifest and a safety envelope, and then leaves coverage planning, navigation, and motor control entirely to OpenMower. The stack keeps the autonomy; URML is the pre-dispatch check on the job it is asked to run.
- **An outdoor machine where the envelope is concrete.** Boundaries, keep-out zones, and a blade that should only spin under defined conditions are exactly the kind of declarable, checkable constraints URML is built for. The mower's drive type and limits go in the manifest; the job intent is validated against them before anything spins.

## What is asked

1. Is a typed, validated job-intent layer (declare the area, drive type, and envelope, validate, then run OpenMower's autonomy) useful above a coverage-and-navigation stack like this?
2. Does an autonomous mower's envelope (boundaries, keep-out zones, speed ceilings, blade-engagement conditions) map onto a URML capability manifest and safety envelope cleanly?
3. Which constraint would be the most valuable to check statically before a job runs?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, safety-envelope validation, and the declare-and-consume model where the substrate keeps planning and actuation (RFC-0020). Anchor of the outdoor-mobile sub-lane of Move #59; the strongest outdoor autonomous-machine target in the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `ClemensElflein/open_mower_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is GPL-3.0; stated, not asked, and the relationship is cross-citation only, with no shared code. Tracked in `examples/lighthouses/outreach-move59.yaml`.
