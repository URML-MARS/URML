---
rfc: 0661
title: Mujin controllerclientcpp (Mujin/controllerclientcpp) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-03
updated: 2026-07-03
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

# RFC-0661: Mujin controllerclientcpp integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #68 (Japan lane).

## Summary

[`Mujin/controllerclientcpp`](https://github.com/Mujin/controllerclientcpp) (Mujin, Tokyo) is the C++ client for talking to a Mujin robot controller: it sends motion commands to the platform and reads state back. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A client that sends motion commands is a place where a pre-send check can sit, one layer above the wire.

## The relationship (URML beside controllerclientcpp)

Code that uses this client decides a motion and sends it to the Mujin controller. URML can declare the cell's envelope (reach, payload, keep-out, speed) and validate a commanded motion against that declaration before the client sends it. It is a static admissibility check on the outgoing command, not a controller and not a re-implementation of the Mujin planner.

To be honest about the fit: the Mujin controller itself does the planning and holds the real safety logic, and this repo is the client to it, so URML's role here is narrower than for an autonomy layer that generates actions. It is the same pre-dispatch check, applied to the command a caller is about to send over the client.

## What is asked

1. For a controller client, is a declared-capability and envelope check on the outgoing command a useful addition for the integrations built on it, or does that belong inside the Mujin controller rather than in front of the client?
2. Would a small worked example mapping a command sent through the client onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied in front of a robot-controller client. Apache-2.0; Mujin, Tokyo, Japan. Part of Move #68.

## Implementation note

Outreach only. The post is a GitHub Issue on `Mujin/controllerclientcpp` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move68.yaml`.
