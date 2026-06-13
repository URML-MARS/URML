---
rfc: 0512
title: CALVIN integration — request for comment
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

# RFC-0512: CALVIN integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`mees/calvin`](https://github.com/mees/calvin) (MIT, ~940 stars, active, University of Freiburg) is a benchmark for language-conditioned, long-horizon manipulation policy learning. CALVIN sits squarely on URML's main seam: language in, robot action out. URML formalizes the middle of that pipeline — a language instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope — and a CALVIN-trained policy can declare the task envelope it learned. This RFC asks whether the mapping is useful.

## The mapping (URML beside CALVIN)

- **Typed intent on the language seam.** CALVIN evaluates language-conditioned policies; URML is a typed, validatable representation of exactly that language-to-intent step. A long-horizon CALVIN task can be expressed as a URML composition of typed primitives, each checkable against the manifest.
- **Learned-task envelope.** A CALVIN-trained policy carries the observation/action spaces and the task distribution it learned. URML's `LearnedPolicy` declaration (RFC-0383) lets it publish those bounds, so a deployment is validated against the domain the policy was trained for rather than trusted blindly.

## What is asked

Request for comment from the CALVIN maintainers:

1. Is a typed, validatable representation of the language-to-intent step (URML primitives) useful alongside a language-conditioned benchmark?
2. Does declaring a trained policy's learned task envelope (obs/action spaces + domain) as a URML `LearnedPolicy` make sense?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language interface, the `LearnedPolicy` declaration (RFC-0383), and the decide-then-do split (RFC-0002). Language-conditioned manipulation is the headline URML path. Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `mees/calvin` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move46.yaml`.
