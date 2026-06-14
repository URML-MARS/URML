---
rfc: 0574
title: Robocode Tank Royale integration — request for comment
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

# RFC-0574: Robocode Tank Royale integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52). This is a lighter-touch conceptual note.

## Summary

[`robocode-dev/tank-royale`](https://github.com/robocode-dev/tank-royale) (Apache-2.0) is the modern successor to Robocode: a programming game where players write bots that battle, used widely to teach programming. URML is a language for robot intent, and while a game bot is virtual, the shared idea is interesting: a declarative, checkable way to state what a bot should try to do. This RFC is a conceptual note, not an integration ask.

## The relationship (URML beside Tank Royale)

- **Declarative intent, even for a game bot.** A Tank Royale bot is written imperatively against an API. URML's angle is a declarative, typed intent layer that states a goal and is validated against the actor's declared capabilities. For a teaching game, an optional declarative-intent mode could be a gentle on-ramp before learners write full imperative bots, and it makes "what is this bot allowed to do" explicit.
- **Honest scope.** This is exploratory; a battle game is not a physical robot, and the value, if any, is pedagogical.

## What is asked

Request for comment from the Tank Royale maintainers:

1. Is a declarative, typed intent layer an interesting on-ramp or teaching aid alongside imperative bot programming?
2. Does the "declare what the bot should try to do, validated against its capabilities" idea map onto how Tank Royale bots are written?
3. Which aspect, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's small typed primitive vocabulary (RFC-0002), the Layer-4 natural-language grammar, and the educational profile (RFC-0011). Part of Move #52; the programming-game peer of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `robocode-dev/tank-royale` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move52.yaml`.
