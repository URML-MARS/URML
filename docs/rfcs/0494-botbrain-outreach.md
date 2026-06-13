---
rfc: 0494
title: BotBrain integration — request for comment
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

# RFC-0494: BotBrain integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`botbotrobotics/BotBrain`](https://github.com/botbotrobotics/BotBrain) (MIT, ~220 stars, active) is a modular open "brain" for legged robots, bundling teleoperation, navigation, and mapping on ROS 2. URML is interesting to a robot-brain runtime as the validated-intent layer that sits above it: a high-level command is turned into a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched into BotBrain's existing nav / teleop modules. This RFC asks whether the mapping is useful.

## The mapping (URML beside BotBrain)

- **Capability manifest.** The legged platform BotBrain drives declares its mobility (a legged `drive_type`), its `whole_body` stability limits (RFC-0384), and its named locations. URML validates a program against that manifest.
- **Intent above the brain, then dispatch.** A natural-language or higher-level command becomes a typed URML primitive, validated, then routed to BotBrain's navigation or teleop path (the decide-then-do split). URML is the typed gate and intent record; BotBrain stays the runtime that moves the legs.

## What is asked

Request for comment from the BotBrain maintainers:

1. Does a URML manifest for the legged platform (legged `drive_type` + `whole_body` limits + locations) fit how BotBrain models its robot?
2. Is a validated-intent layer above BotBrain's nav / teleop modules interesting, or already covered by something in the stack?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's legged `drive_type`, the `whole_body` declaration (RFC-0384), and the decide-then-do split (RFC-0002). Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `botbotrobotics/BotBrain` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
