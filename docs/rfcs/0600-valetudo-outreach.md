---
rfc: 0600
title: Valetudo integration — request for comment
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

# RFC-0600: Valetudo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the service-robotics wave (Move #56).

## Summary

[`Hypfer/Valetudo`](https://github.com/Hypfer/Valetudo) (Apache-2.0) is the cloud-free firmware that puts a local control plane on a large family of consumer and commercial cleaning robots, exposing a documented local REST and MQTT API. A cleaning task is a goal plus constraints (clean these zones, go to this room, avoid this no-go area, at this suction), which is exactly the shape URML declares as a typed intent and validates against a robot's capabilities before dispatch. The local API and the per-model capability picture make this an unusually clean fit, which is why it leads the wave.

## The mapping (URML beside Valetudo)

- **A validated cleaning intent over the local API.** URML would map a clean-zone / go-to-room / spot-clean intent onto Valetudo's REST capabilities, validated against a per-model capability manifest (which suction modes, segment cleaning, zones, mop present) before any command is sent. URML adds the typed pre-dispatch check and a natural-language front door; Valetudo stays the firmware and the local control plane.
- **Per-model capability picture.** Valetudo already exposes what a given model supports as capabilities. That maps directly onto a URML capability manifest, so an intent a particular robot cannot honor (a zone clean on a model without zone support) is rejected before dispatch. The same approach extends across the Valetudo ecosystem (the RE fork and the firmware builders) without per-model special-casing.

## What is asked

1. Is a typed, validated cleaning-intent layer (an intent checked against a per-model capability manifest, then dispatched over the local REST/MQTT API) useful above Valetudo?
2. Does Valetudo's per-model capability exposure map cleanly onto a URML capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-1 capability manifest, the Layer-4 natural-language grammar, and the substrate-neutral dispatch model (a RobotVacuumAdapter would sit beside the existing adapters). Anchor of Move #56; the cloud-free cleaning-robot control plane of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `Hypfer/Valetudo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move56.yaml`.
