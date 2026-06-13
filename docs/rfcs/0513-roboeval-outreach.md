---
rfc: 0513
title: RoboEval integration — request for comment
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

# RFC-0513: RoboEval integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`Robo-Eval/RoboEval`](https://github.com/Robo-Eval/RoboEval) (Apache-2.0, ~60 stars, fresh / active, University of Washington + Allen Institute for AI) is a structured, scalable benchmark for bimanual manipulation, with per-skill diagnostic metrics over thousands of demonstrations. URML is interesting at the boundary between the diagnostics and a deployment: the skills a benchmark measures map onto declared capability stages a deployment can be bounded against. This RFC asks whether the mapping is useful.

## The mapping (URML beside RoboEval)

- **Skills as declared capabilities.** RoboEval's per-skill structure (and its bimanual focus) lines up with URML's manipulation model — a two-arm task declares its arms (`manipulation.arms`) and uses the `bimanual` primitive (RFC-0010). The skill a policy is measured on is the capability a deployment declares it can do.
- **Learned-policy envelope.** A policy evaluated on RoboEval can carry, via URML's `LearnedPolicy` declaration (RFC-0383), the obs/action spaces and task distribution it was scored in, so a deployment is validated against that envelope.

## What is asked

Request for comment from the RoboEval maintainers:

1. Do RoboEval's per-skill, bimanual diagnostics map cleanly onto URML's declared capabilities (`manipulation.arms` + the `bimanual` primitive)?
2. Is declaring a scored policy's evaluation envelope as a URML `LearnedPolicy` useful?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's whole-body / bimanual manipulation model (RFC-0010), the `LearnedPolicy` declaration (RFC-0383), and the decide-then-do split (RFC-0002). Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `Robo-Eval/RoboEval` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
