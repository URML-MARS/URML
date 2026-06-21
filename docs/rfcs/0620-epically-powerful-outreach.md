---
rfc: 0620
title: epically-powerful (Georgia Tech EPIC Lab) integration — request for comment
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

# RFC-0620: epically-powerful integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the wearable-and-assistive sub-lane of Move #59.

## Summary

[`gatech-epic-power/epically-powerful`](https://github.com/gatech-epic-power/epically-powerful) (AGPL-3.0, Georgia Tech EPIC Lab) is a Python framework that commands quasi-direct-drive actuators over CAN (CubeMars AK, RobStride, CyberGear) for exoskeletons and sensor suits, with safety monitoring built in. It already carries a notion of safe operation around the actuation it drives. URML is a validated-intent layer that complements that: where the framework monitors the actuation at runtime, URML declares the admissible envelope up front and validates a subtask intent against it before dispatch, so the same safety properties exist as a static pre-check and a runtime monitor rather than only the latter. URML does not run actuation or monitoring; it declares and checks. This is a request for comment, framed as cross-citation given the AGPL-3.0 license.

## The relationship (URML beside epically-powerful)

- **Static envelope check before, runtime monitor during.** A declared limit on actuator torque or speed is a property that can be checked twice: once statically, when URML validates that a subtask intent stays inside the declared envelope, and once at runtime, by the framework's own safety monitoring. The two reinforce each other. URML's pre-dispatch validation is the layer that refuses an inadmissible intent before the actuator ever sees it; the runtime monitor remains the framework's.
- **A clean seam on a QDD actuator stack.** Because the framework speaks to well-defined actuators over CAN, the per-actuator limits are concrete and declarable. That makes the envelope mapping unusually tractable: the manifest states the actuators and their ceilings, and the validator checks intent against them.

## What is asked

1. Is a static pre-dispatch envelope check useful alongside the framework's existing runtime safety monitoring, or does the runtime monitor already cover the cases a static check would catch?
2. Do per-actuator limits (torque, speed, position) map onto a URML capability manifest and safety envelope cleanly for a QDD-over-CAN stack?
3. Which actuator family would be the most natural first mapping to try?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's safety-envelope validation, the capability manifest, and the framing (from URML's runtime-verification outreach, Move #28) that static pre-dispatch validation complements a runtime monitor rather than replacing it. Companion to RFC-0618 and RFC-0619 in the wearable-and-assistive sub-lane of Move #59.

## Implementation note

Outreach only. The post is a GitHub Issue on `gatech-epic-power/epically-powerful` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is AGPL-3.0; stated, not asked, and the relationship is cross-citation only, with no shared code. Tracked in `examples/lighthouses/outreach-move59.yaml`.
