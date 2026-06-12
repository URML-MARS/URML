---
rfc: 0466
title: MCAP integration — request for comment
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

# RFC-0466: MCAP integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's validate-before-actuate audit trail.

## Summary

[`foxglove/mcap`](https://github.com/foxglove/mcap) (MIT, ~970 stars, active) is a serialization-agnostic container file format for pub/sub and robotics logging — the format Lichtblick, Foxglove, and a growing ROS 2 ecosystem record into. URML is interesting to it as a *recordable stream*: every URML dispatch is validated before it actuates and produces a structured audit record. Recording the validated-intent trail as a first-class MCAP channel makes it replayable, diffable, and visualizable in any MCAP-aware tool. This RFC asks whether that mapping is sound.

## The mapping (URML audit trail recorded as MCAP)

URML records into, it is not a runtime for, MCAP:

- A URML runtime writes one MCAP channel of audit messages: per step, the typed intent, the validator verdict (failing pass + error code when refused), and the dispatched substrate calls, each with a log time.
- Because MCAP is serialization-agnostic, the audit schema can be JSON Schema (the same program/manifest schemas URML already exports) or protobuf — no new format invented.
- A recorded `.mcap` then opens directly in Lichtblick (RFC-0463) or any MCAP reader, so the validated-intent stream is portable across the whole ecosystem rather than tool-specific.

## What is asked

Request for comment from the MCAP maintainers:

1. Is recording URML's validated-intent audit trail as a dedicated MCAP channel the right pattern (schema-encoded messages on their own channel)?
2. Should the audit schema be advertised as JSON Schema or protobuf for best cross-tool support?
3. Any conventions for an "intent + verdict" message channel that would make it idiomatic for MCAP readers? (The Foxglove SDK is the natural live-streaming complement; this RFC engages MCAP as the on-disk format.)

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's five-pass validator + audit trail; the schema export the validator already ships; the Open MCT telemetry engagement (RFC-0395); the Lichtblick anchor (RFC-0463). MCAP is the on-disk-logging-format vertex of the developer-tooling wave; the sibling `foxglove/foxglove-sdk` (live streaming) is referenced, not posted to separately.

## Implementation note

Outreach only. The post is a GitHub Discussion on `foxglove/mcap` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move40.yaml`.
