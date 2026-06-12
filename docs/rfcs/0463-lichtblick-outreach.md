---
rfc: 0463
title: Lichtblick integration — request for comment
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

# RFC-0463: Lichtblick integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail. It is the anchor of the developer-tooling / observability wave (Move #40).

## Summary

[`lichtblick-suite/lichtblick`](https://github.com/lichtblick-suite/lichtblick) (MPL-2.0, ~950 stars, active) is the BMW-led open fork of Foxglove Studio — an integrated robotics visualization and diagnosis platform with a panel + data-source plugin model. URML is interesting to a viz/observability tool not as a substrate but as a *data source*: every URML dispatch is validated before it actuates and produces a structured audit record (the intent, which of the five validator passes ran and their verdicts, the substrate calls). This RFC asks whether visualizing that validated-intent stream is interesting.

## The mapping (URML as a data source for Lichtblick)

URML sits beside, not below, the visualization tool:

- A URML runtime emits a structured audit event per step: the typed intent, the validation verdict (and the failing pass + error code when refused), and the dispatched substrate calls. That is a clean time-series + event stream a Lichtblick data-source plugin could ingest.
- A panel could show "intent → validated → dispatched" alongside the robot's pose/sensors already visualized, making the *why-it-did-that* legible next to the *what-it-did*.
- This is the same shape as URML's Open MCT engagement (RFC-0395): URML's audit/envelope state as a telemetry source, not a substrate claim.

## What is asked

Request for comment from the Lichtblick maintainers:

1. Is URML's validated-intent audit stream a useful data source / panel for Lichtblick?
2. What is the cleanest seam — a custom data-source plugin, an MCAP recording (see RFC-0466), or a live foxglove-protocol stream?
3. What fields would a "validated intent" panel want (intent, pass/verdict, substrate call, timing)?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator + audit trail; the Open MCT telemetry engagement (RFC-0395) as the observability-sink precedent. Lichtblick is the anchor of the developer-tooling / observability wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `lichtblick-suite/lichtblick` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MPL-2.0). Tracked in `examples/lighthouses/outreach-move40.yaml`.
