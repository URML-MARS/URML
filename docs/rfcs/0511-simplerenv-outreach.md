---
rfc: 0511
title: SimplerEnv integration — request for comment
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

# RFC-0511: SimplerEnv integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`simpler-env/SimplerEnv`](https://github.com/simpler-env/SimplerEnv) (MIT, ~1.1k stars, active) provides simulated environments to reproduce real-robot manipulation policy evaluations (RT-1, Octo, and others, on the Google Robot and WidowX / Bridge setups). URML is interesting to an evaluation harness at the deployment boundary: the embodiment and task a policy was evaluated in is exactly the envelope a deployment should be validated against. This RFC asks whether the mapping is useful.

## The mapping (URML beside SimplerEnv)

- **Eval setup as a declared envelope.** The embodiment, observation/action spaces, and task distribution a policy is scored in under SimplerEnv map onto a URML `LearnedPolicy` envelope (RFC-0383). A deployment can then be validated against the setup the policy's numbers were actually obtained in.
- **Validated deployment.** With the envelope declared, URML checks each proposed action against the robot's declared capabilities and the active safety envelope before dispatch (the decide-then-do split), so an out-of-eval-distribution action is caught before it reaches hardware.

## What is asked

Request for comment from the SimplerEnv maintainers:

1. Does declaring a policy's evaluation setup (embodiment + obs/action spaces + task distribution) as a URML deployment envelope make sense?
2. Is a validated-intent gate that checks a deployment matches the eval setup interesting?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) consume the policies these benchmarks evaluate. Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `simpler-env/SimplerEnv` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
