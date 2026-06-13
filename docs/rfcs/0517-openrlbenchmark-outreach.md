---
rfc: 0517
title: openrlbenchmark integration — request for comment
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

# RFC-0517: openrlbenchmark integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. **Completes** the AI / robot-learning wave (Move #46).

## Summary

[`openrlbenchmark/openrlbenchmark`](https://github.com/openrlbenchmark/openrlbenchmark) (MIT, ~260 stars, active) is tooling to track and compare reinforcement-learning experiment metrics across libraries. It is one layer removed from deployment, but it shares URML's premise: a policy should be described by the conditions it was trained and evaluated under. URML's `LearnedPolicy` declaration captures exactly those conditions for the deployment side. This RFC asks whether there is a useful connection.

## The mapping (URML beside openrlbenchmark)

- **From tracked metrics to a declared envelope.** openrlbenchmark records the environments, configurations, and results of RL runs. The same metadata that makes a run comparable (the env, the spaces, the domain) is what a URML `LearnedPolicy` envelope (RFC-0383) carries to the deployment so a policy is validated against the conditions it was trained and measured under.
- **A shared discipline.** Both projects insist that a policy is only meaningful relative to a declared setup. openrlbenchmark makes that explicit for comparison; URML makes it explicit for safe deployment.

## What is asked

Request for comment from the openrlbenchmark maintainers:

1. Is there a useful path from the run metadata openrlbenchmark tracks to a URML `LearnedPolicy` deployment envelope?
2. Is the shared "a policy is defined by its declared training/eval setup" framing worth a cross-reference for users who go from benchmark to deployment?
3. Which connection, if any, is worth pursuing?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the general-purpose RL-framework wave (Move #43: stable-baselines3, cleanrl and others — several of whose runs openrlbenchmark tracks). Completes Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `openrlbenchmark/openrlbenchmark` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
