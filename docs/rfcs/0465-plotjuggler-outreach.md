---
rfc: 0465
title: PlotJuggler integration — request for comment
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

# RFC-0465: PlotJuggler integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail.

## Summary

[`PlotJuggler/PlotJuggler`](https://github.com/PlotJuggler/PlotJuggler) (MPL-2.0, ~6.0k stars, active) is a fast time-series visualization tool with a streaming + plugin model (ROS, MQTT, CSV, custom sources). URML is interesting to it as a *data source*: every URML dispatch is validated before it actuates, producing timestamped scalars and events — validator pass/verdict, per-step timing, envelope margins — that PlotJuggler is built to plot. This RFC asks whether plotting that validated-intent stream is interesting.

## The mapping (URML streamed to PlotJuggler)

URML sits beside, not below, the plotting tool:

- A URML runtime exposes timestamped series a PlotJuggler streaming plugin can consume: per-step validation verdict (accepted/refused), the failing pass when refused, dispatch latency, and envelope margins (e.g. commanded vs. declared max velocity).
- Plotting "how close each command ran to its declared envelope" turns validate-before-actuate into a quantitative, reviewable trace.

## What is asked

Request for comment from the PlotJuggler maintainers:

1. Is URML's validated-intent / envelope-margin stream a useful streaming source for PlotJuggler?
2. Is a custom streaming plugin the right seam, or is replaying a recorded log (CSV / MCAP, see RFC-0466) the cleaner first step?
3. What scalar/event shape would a "validated intent" series want to be in?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator + audit trail; the Open MCT telemetry engagement (RFC-0395); the Lichtblick anchor (RFC-0463). PlotJuggler is the time-series-plotting vertex of the developer-tooling wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `PlotJuggler/PlotJuggler` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MPL-2.0). The AGPL `plotjuggler-ros-plugins` repo is not engaged separately. Tracked in `examples/lighthouses/outreach-move40.yaml`.
