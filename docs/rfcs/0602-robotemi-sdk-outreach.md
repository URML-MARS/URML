---
rfc: 0602
title: temi robot SDK integration — request for comment
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

# RFC-0602: temi robot SDK integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the service-robotics wave (Move #56); the hospitality / service-robot corner.

## Summary

[`robotemi/sdk`](https://github.com/robotemi/sdk) is the official SDK for the temi personal/hospitality robot: an Android-based platform that navigates to saved locations, follows and patrols, and runs interactive experiences. The physical-action side of temi (go to this location, patrol this route, return to home base) is exactly the goal-plus-constraints intent URML declares and validates before dispatch. This RFC asks whether a typed intent layer is useful above the temi SDK.

## The mapping (URML beside the temi SDK)

- **A validated movement intent for a service robot.** A temi skill orchestrates an interaction; its movement actions (go-to, follow, patrol) are the part URML speaks to. URML would declare that movement intent, validate it against temi's declared locations and movement capabilities, then dispatch through the SDK. The interaction and the app stay with temi; URML adds the typed, checkable movement layer and an optional natural-language path.
- **Saved locations toward a manifest.** temi's saved locations and movement capabilities map onto a URML capability manifest and declared locations, so a "go to the lobby" intent is checked against what the robot actually knows before it runs.

## What is asked

1. Is a typed, validated movement-intent layer (a go-to / patrol intent checked against temi's saved locations and capabilities, then dispatched through the SDK) useful?
2. Do temi's saved locations and movement capabilities map onto a URML capability manifest and declared locations?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, declared locations, the move_to primitive, and the Layer-4 natural-language grammar. Part of Move #56; the hospitality-robot SDK of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `robotemi/sdk` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The repository has no license file, so the post states that and makes no licensing request and proposes no code reuse. Tracked in `examples/lighthouses/outreach-move56.yaml`.
