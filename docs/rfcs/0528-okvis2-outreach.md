---
rfc: 0528
title: OKVIS2 integration — request for comment
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

# RFC-0528: OKVIS2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. **Completes** the perception / SLAM / mapping / reconstruction wave (Move #47).

## Summary

[`ethz-mrl/okvis2`](https://github.com/ethz-mrl/okvis2) (BSD-3-Clause, ~210 stars, active, ETH Zurich) is Open Keyframe-based Visual-Inertial SLAM, version 2 — it produces a real-time pose estimate from cameras and an IMU. URML consumes such an estimate; it does not compute it. An OKVIS2 pose is the localized state a URML deployment's frames and constraints resolve against. This RFC asks whether the seam is useful.

## The mapping (URML beside OKVIS2)

- **The VIO estimate, consumed.** OKVIS2 yields a visual-inertial pose estimate. URML resolves its frames (RFC-0290) and validates intent against the active safety envelope using that pose. URML consumes the estimate; OKVIS2 is the VIO that produces it.

## What is asked

Request for comment from the OKVIS2 maintainers:

1. Is "OKVIS2 produces the VIO pose estimate, URML consumes it to resolve frames and validate intent" a sensible consumer relationship?
2. Is there a clean output (pose, covariance, frame) a robot deployment would feed a URML manifest / envelope?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's frame-transform graph (RFC-0290), the safety envelope, and the "URML consumes your estimate" posture (Move #25). Completes Move #47.

## Implementation note

Outreach only. The post is a GitHub Issue on `ethz-mrl/okvis2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move47.yaml`.
