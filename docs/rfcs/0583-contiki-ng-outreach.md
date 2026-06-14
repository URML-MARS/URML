---
rfc: 0583
title: Contiki-NG integration — request for comment
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

# RFC-0583: Contiki-NG integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). This is the most exploratory note in the wave, and the most honest about a thin seam.

## Summary

[`contiki-ng/contiki-ng`](https://github.com/contiki-ng/contiki-ng) (BSD-3-Clause) is an operating system for resource-constrained IoT devices, strong on low-power wireless networking. Contiki-NG's center of gravity is sensing and networking rather than actuation, so the overlap with a robot-intent language is genuinely small. The one place it is real is the same as for the other networked-node OSes: a Contiki-NG node that also actuates can run a pre-validated intent and be a member of a URML-addressed fleet.

## The relationship (URML beside Contiki-NG)

- **A small, honest seam.** Where a Contiki-NG node drives an actuator, a minimal URML executor (RFC-0018 minimal_node) could run a pre-validated intent on it, and the node could be one member of a URML roster. Where a node only senses and forwards, there is no seam, and that is fine.
- **Sensing into intent.** The more interesting indirect link is that Contiki-NG sensor data is the kind of fact a URML intent elsewhere conditions on; URML consumes such facts, it does not produce them.

## What is asked

1. In deployments where a Contiki-NG node actuates (not only senses), is a small pre-validated intent executor a sensible component, or is that outside what Contiki-NG nodes typically do?
2. Is the sensor-data-as-a-fact-an-intent-conditions-on framing a more natural connection than node-side execution?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's minimal_node MCU execution shape (RFC-0018), the multi-robot roster (RFC-0286), and the consume-the-fact model. Part of Move #53; the low-power-IoT target of the wave, posted with an explicit note that the seam is thin.

## Implementation note

Outreach only. The post is a GitHub Issue on `contiki-ng/contiki-ng` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move53.yaml`.
