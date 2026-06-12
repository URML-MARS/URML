---
rfc: 0464
title: Rerun integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-12
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

# RFC-0464: Rerun integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail.

## Summary

[`rerun-io/rerun`](https://github.com/rerun-io/rerun) (Apache-2.0 + MIT, ~10.9k stars, active) is a tool to visualize, query, and stream multimodal robotics data along a timeline. URML is interesting to it as a *data source*: every URML dispatch is validated before it actuates and produces a structured, timestamped audit record (the intent, the validator verdict, the substrate calls) that sits naturally on a Rerun timeline next to the poses, images, and point clouds already logged. This RFC asks whether logging that validated-intent stream is interesting.

## The mapping (URML logged to Rerun)

URML sits beside, not below, the visualization tool:

- A URML runtime logs one entity per step on the timeline: the typed intent, the validation verdict (and the failing pass + error code when refused), and the dispatched substrate calls. Rerun's time-aligned, multimodal model is a good fit for "what was intended, whether it was allowed, what was sent" alongside sensor data.
- A refused intent (out-of-capability, out-of-envelope) is a first-class timeline event, making validate-before-actuate legible in replay.

## What is asked

Request for comment from the Rerun maintainers:

1. Is URML's validated-intent audit stream a useful thing to log to a Rerun timeline?
2. What is the idiomatic Rerun shape for "intent + verdict + dispatch" events (a custom archetype, scalars + text, a structured log)?
3. Is there interest in a small reference logger that emits URML audit records as Rerun entities?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator + audit trail; the Open MCT telemetry engagement (RFC-0395); the Lichtblick anchor (RFC-0463). Rerun is the multimodal-timeline vertex of the developer-tooling wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `rerun-io/rerun` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0 + MIT). Tracked in `examples/lighthouses/outreach-move40.yaml`.
