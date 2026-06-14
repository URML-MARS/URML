---
rfc: 0601
title: python-miio integration — request for comment
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

# RFC-0601: python-miio integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the service-robotics wave (Move #56).

## Summary

[`rytilahti/python-miio`](https://github.com/rytilahti/python-miio) (GPL-3.0) is the canonical Python library for the Xiaomi miIO/MIoT protocol, controlling a wide range of devices including robot vacuums. For the service-robot subset, it is a concrete substrate: a validated cleaning intent can be realized as python-miio device calls. This RFC is a consume / dispatch note (cross-citation only, since python-miio is GPL-3.0).

## The mapping (URML beside python-miio)

- **A concrete substrate for a validated cleaning intent.** URML validates a cleaning intent (clean these zones, fan speed, go to dock) against the robot's declared capabilities and a safety envelope, then dispatches; python-miio is one path that turns the validated intent into device commands. URML adds the typed pre-dispatch check and an optional natural-language front door; python-miio stays the protocol library.
- **Device feature flags toward a manifest.** A miIO/MIoT vacuum advertises the features it supports; that advertisement maps toward a URML capability manifest, so an unsupported intent is caught before it reaches the device. Given the GPL-3.0 license this proposes no shared code, only a dispatch relationship.

## What is asked

1. For the robot-vacuum subset, is a typed, validated intent layer above python-miio (an intent checked against the device's advertised features, then dispatched) useful?
2. Do miIO/MIoT vacuum feature flags map cleanly toward a capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the Layer-4 natural-language grammar, and the substrate-neutral dispatch model. Part of Move #56; the device-protocol substrate of the cleaning-robot cluster (with Valetudo RFC-0600).

## Implementation note

Outreach only. The post is a GitHub Issue on `rytilahti/python-miio` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move56.yaml`.
