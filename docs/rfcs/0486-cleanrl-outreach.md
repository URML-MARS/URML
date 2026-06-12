---
rfc: 0486
title: CleanRL integration — request for comment
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

# RFC-0486: CleanRL integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's `LearnedPolicy` declaration (RFC-0383) and its decide-then-do split (RFC-0002). Part of the reinforcement-learning / policy-training wave (Move #43).

## Summary

[`vwxyzjn/cleanrl`](https://github.com/vwxyzjn/cleanrl) (MIT, ~9.9k stars, active) is high-quality single-file Deep RL — each algorithm is one readable file with explicit observation/action handling. That readability is exactly why it is an interesting place to ask URML's question: when a policy trained by a single-file PPO/SAC is deployed on a robot, what declares the bounds it was trained inside, and what checks a deployment stays within them? URML's `LearnedPolicy` declaration (RFC-0383) is built for that, and CleanRL's single-file clarity makes it an ideal worked example. This RFC asks for comment.

## The mapping (URML beside CleanRL)

- **A single-file envelope example.** A CleanRL training script knows its `envs.single_observation_space` / `single_action_space` and the domain it trained in. A few lines emitting a URML `LearnedPolicy` envelope (obs/action ranges + training-domain bounds) alongside the saved weights would be a clean, copy-pasteable reference for "how do I declare what my policy was trained for" — the kind of worked example CleanRL exists to provide.
- **Validated deployment.** With the envelope declared, URML is the typed gate between the trained policy and the robot: each proposed action is validated against declared capabilities and the safety envelope before dispatch (decide-then-do). The policy decides; URML does.

## What is asked

Request for comment from the CleanRL maintainers:

1. Would a single-file example that emits a URML `LearnedPolicy` envelope (obs/action spaces + training-domain bounds) next to a trained policy be a useful reference for the deployment side?
2. Is the validated-deployment gate (action checked against declared capabilities + envelope before dispatch) interesting, or out of scope for a single-file-algorithms project?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `LearnedPolicy` declaration (RFC-0383) and the decide-then-do split (RFC-0002). The VLA / robot-learning engagements (Moves #11, #38) at the foundation-model layer; this wave is the general-purpose RL layer below. Sibling RFC-0485 (Stable-Baselines3) anchors Move #43.

## Implementation note

Outreach only. The post is a GitHub Discussion in the **Ideas** category on `vwxyzjn/cleanrl` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (the LICENSE is MIT; it bundles adapted-component licenses but the primary license is MIT). Tracked in `examples/lighthouses/outreach-move43.yaml`.
