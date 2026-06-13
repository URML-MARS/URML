---
rfc: 0552
title: Furhat skills integration — request for comment
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

# RFC-0552: Furhat skills integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the HRI / conversational / robot-data wave (Move #50). This is a lighter-touch note: Furhat is a social conversational robot, and the seam with URML is narrow but real.

## Summary

[`FurhatRobotics/example-skills`](https://github.com/FurhatRobotics/example-skills) (MIT) is the example-skill collection for the Furhat social robot SDK: conversational, face-and-voice social interaction. URML is not a conversation framework; it is the validated-intent layer for *physical* robot action. The seam appears when a Furhat skill needs to drive a physical robot (a mobile base, an arm, a connected device) as part of an interaction. This RFC asks whether that seam is worth a clean boundary.

## The relationship (URML beside Furhat skills)

- **Conversation in Furhat, validated physical action in URML.** A Furhat skill owns the social interaction. When a skill triggers a physical action on a connected robot, URML is the typed, validated representation of that action: checked against the robot's capabilities and a safety envelope before it runs. Furhat stays the conversational brain; URML is the gate on the physical limb.
- **Honest scope.** If Furhat skills never drive an external physical robot, the seam is empty and this is just a friendly note. The question is genuine.

## What is asked

Request for comment from the Furhat maintainers:

1. Do Furhat skills ever drive an external physical robot (base, arm, device) as part of an interaction?
2. If so, is a typed, validated intent layer between a skill and that physical robot useful?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's intent primitives (Layer 2), the capability manifest, and the safety-envelope validation. Part of Move #50; the social-robot edge of the conversational cluster (ROSGPT RFC-0549, DialoStack RFC-0550, retico-core RFC-0551).

## Implementation note

Outreach only. The post is a GitHub Issue on `FurhatRobotics/example-skills` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move50.yaml`.
