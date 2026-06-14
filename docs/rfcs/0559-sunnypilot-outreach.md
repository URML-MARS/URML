---
rfc: 0559
title: sunnypilot integration — request for comment
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

# RFC-0559: sunnypilot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51).

## Summary

[`sunnypilot/sunnypilot`](https://github.com/sunnypilot/sunnypilot) (MIT) is an actively-maintained driver-assistance system (an openpilot fork) running on real vehicles. Every ADAS stack has an operational design domain: the conditions and maneuvers under which it is allowed to act. URML's safety envelope and capability manifest are a way to declare those bounds and validate a maneuver against them before it executes. This RFC asks whether that mapping is useful.

## The mapping (URML beside sunnypilot)

- **The safety envelope is an ODD.** A driver-assistance system acts only within an operational design domain. URML expresses an active safety envelope (speed, geometry, conditions) plus a capability manifest, and validates an intended maneuver against both before dispatch. The idea is not to replace the controls stack but to give the "is this maneuver allowed right now" check a typed, declarative form.
- **Validated intent, then the stack executes.** URML declares and checks the maneuver intent; sunnypilot plans and actuates it. URML does not drive; it gates.

## What is asked

Request for comment from the sunnypilot maintainers:

1. Is a typed, declarative operational-design-domain (safety-envelope) check a useful layer in front of an ADAS maneuver?
2. Does URML's capability manifest map onto how sunnypilot reasons about what a given vehicle is allowed to do?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's safety-envelope validation, the capability manifest, and the decide-then-do split (RFC-0002). Part of Move #51; sibling to the opendbc actuation-HAL framing (RFC-0558).

## Implementation note

Outreach only. The post is a GitHub Issue on `sunnypilot/sunnypilot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move51.yaml`.
