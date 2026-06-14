---
rfc: 0590
title: Bluesky (NSLS-II) integration — request for comment
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

# RFC-0590: Bluesky (NSLS-II) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54).

## Summary

[`bluesky/bluesky`](https://github.com/bluesky/bluesky) (BSD-3-Clause, Brookhaven NSLS-II) is an experiment-specification and run-engine library: an experiment is written as a declarative *plan* that the run engine executes against instruments and detectors. That declarative-plan-then-execute shape is exactly URML's loop, in the scientific-instrument domain. This RFC is a note between two declare-then-execute designs.

## The relationship (URML beside Bluesky)

- **Two declare-then-execute loops.** A Bluesky plan declares what an experiment should do; the run engine dispatches it to hardware. A URML program declares what a robot should do; the validator checks it and the runtime dispatches it. The structural similarity is strong. The candidate difference URML brings is the explicit pre-dispatch validation pass against a declared device capability manifest and operating envelope.
- **Honest scope.** Bluesky already owns experiment specification and execution at beamlines and labs, and does it well. URML is not proposing to replace the run engine; the question is only whether a typed capability/envelope check ahead of a plan is meaningful for instrument safety and admissibility, or whether Bluesky's design already places that elsewhere.

## What is asked

1. Is a pre-dispatch validation pass (a plan checked against declared instrument capabilities and limits) a meaningful addition to the Bluesky plan/run-engine model?
2. Do Bluesky's device abstractions map toward a URML-style capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's decide-then-do split (RFC-0002), the capability manifest, and the safety-envelope validation. Part of Move #54; the declarative-experiment peer of the wave (with the orchestration frameworks RFC-0588, RFC-0591).

## Implementation note

Outreach only. The post is a GitHub Issue on `bluesky/bluesky` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move54.yaml`.
