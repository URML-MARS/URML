---
rfc: 0487
title: skrl integration — request for comment
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

# RFC-0487: skrl integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). Part of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`Toni-SM/skrl`](https://github.com/Toni-SM/skrl) (MIT, ~1.1k stars, active, Mondragon Unibertsitatea) is a modular RL library with first-class Isaac Lab, MuJoCo Playground, and Gymnasium support, and it keeps a dedicated **Sim2Real** discussion category. That sim-to-real focus is exactly where URML's question lives: a policy trained in a simulated domain has bounds it must not be trusted outside of on the real robot, and the gap between "trained here" and "deployed there" is the deployment-validity problem URML's `LearnedPolicy` declaration (RFC-0383) is built to make explicit. This RFC asks for comment.

## The mapping (URML beside skrl)

- **The sim2real envelope.** A skrl policy trained in Isaac Lab knows its observation/action spaces and the simulated domain it saw. Declaring that as a URML `LearnedPolicy` envelope (obs/action ranges + training-domain bounds) makes the sim-to-real boundary a typed, checkable artifact rather than an implicit assumption: the validator can refuse to dispatch the policy outside the domain it was trained for.
- **Validated deployment.** URML sits between the trained policy and the real robot, checking each proposed action against the robot's declared capabilities and the active safety envelope before dispatch (decide-then-do). On a sim2real deployment, that gate is where an out-of-distribution action gets caught before it reaches hardware.

## What is asked

Request for comment from the skrl maintainers:

1. For a sim2real deployment, is a declared envelope (the simulated training domain a policy must stay within on the real robot) a useful, typed artifact to emit alongside a trained skrl agent?
2. Is the validated-deployment gate (action checked against declared capabilities + envelope before dispatch) interesting for the real-robot side of sim2real?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). Connects to the Isaac / simulation engagements (Move #24) and the legged-RL libraries (Move #29, rsl_rl / legged_gym / rl_games), whose maintainers were asked a closely related question about a trained policy exporting its capability envelope. Sibling RFC-0485 anchors Move #43.

## Implementation note

Outreach only. The post is a GitHub Discussion on `Toni-SM/skrl` (the **Ideas** category, with the project's **Sim2Real** category as the natural alternative) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move43.yaml`.
