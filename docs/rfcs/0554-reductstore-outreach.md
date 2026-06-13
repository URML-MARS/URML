---
rfc: 0554
title: ReductStore integration — request for comment
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

# RFC-0554: ReductStore integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Opens the robot-data half of the HRI / conversational / robot-data wave (Move #50).

## Summary

[`reductstore/reductstore`](https://github.com/reductstore/reductstore) (Apache-2.0) is a time-series database for unstructured data, built for robotics and edge workloads. URML produces a natural data source for it: every validated dispatch emits a structured audit record (the intent, the validation result, the resolved arguments, the safety envelope it was checked against). This RFC asks whether that record is a useful first-class time series.

## The mapping (URML beside ReductStore)

- **The audit trail is a time series.** URML validates intent before dispatch and records what was validated and why. That stream of structured records (timestamped, typed, tied to a capability manifest) is exactly the kind of robotics time series ReductStore stores. Storing it next to sensor and telemetry data gives a queryable record of *intent*, not just *outcome*.
- **Intent-aware retention.** Because the records are typed and carry the validation verdict, retention and labeling can key on intent (every grasp, every envelope rejection), which is hard to recover from raw telemetry alone.

## What is asked

Request for comment from the ReductStore maintainers:

1. Is a typed validated-intent audit record a useful first-class time series alongside sensor/telemetry data?
2. Does intent-keyed retention/labeling fit ReductStore's model?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's execution audit trail, the five-pass validator, and the audit-trail-as-data-source framing (Move #40). Part of Move #50; the robot-data sub-cluster.

## Implementation note

Outreach only. The post is a GitHub Issue on `reductstore/reductstore` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move50.yaml`.
