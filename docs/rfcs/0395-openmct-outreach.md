---
rfc: 0395
title: Open MCT (NASA) integration — request for comment on surfacing validated-intent state
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

# RFC-0395: Open MCT (NASA) integration — request for comment on surfacing validated-intent state

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It builds on URML's validator output (the audit trail) and safety-envelope state.

## Summary

[Open MCT](https://github.com/nasa/openmct) (NASA Ames, Apache-2.0, ~13k stars) is a mission-control framework for visualizing telemetry and operations data. Unlike the other targets in this wave, URML does **not** sit above Open MCT — Open MCT is an observability surface, not a substrate. The honest framing is integration / visibility: URML's validation results, dispatched-intent audit trail, and safety-envelope state are themselves a telemetry source that an Open MCT operator might want to see. This RFC asks the maintainers whether that is interesting.

## The mapping (URML as a telemetry source for Open MCT)

URML produces inspectable operational state that maps naturally onto Open MCT's telemetry model:

- Every URML execution emits an audit trail (which primitive dispatched, the resolved bindings, the adapter calls) and a pass/fail validation record. Surfaced as an Open MCT telemetry source, an operator could watch "what intent was requested, did it validate, what did it dispatch."
- Safety-envelope state (the active caps, whether a request was refused and why) is exactly the kind of operations data Open MCT exists to display.
- This is an integration at the observability layer, not a control relationship: URML does not drive Open MCT and Open MCT does not drive URML.

## What is asked

Request for comment from Open MCT maintainers:

1. Would a URML validated-intent / safety-envelope telemetry source be a sensible Open MCT integration, or is that outside the framework's intended scope?
2. What is the cleanest way to expose an external operational-state source to Open MCT (the telemetry adapter / plugin API)?
3. Is there interest in a small example plugin surfacing a URML execution's audit trail?

Nothing here asks Open MCT to adopt, host, or maintain anything.

## Prior art / context

URML's validator audit trail and safety-envelope model; the monitorable-properties envelope ([RFC-0382](0382-monitorable-temporal-logic-envelope.md)) as the kind of state worth surfacing. Open MCT is the observability vertex of the space wave — included with an honest "adjacent integration" framing rather than a substrate claim.

## Implementation note

Outreach only. The post is a GitHub Discussion on `nasa/openmct` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
