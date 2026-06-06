---
rfc: 0404
title: FarmBot integration — request for comment from the FarmBot community
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0404: FarmBot integration — request for comment from the FarmBot community

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its community for feedback. It builds on URML's `call_program` binding pattern ([RFC-0015](0015-control-program-invocation.md) / [RFC-0019](0019-autosar-adaptive-substrate.md)) and the validate-before-actuate discipline. It anchors a small FarmBot cluster: [`farmbot_os`](https://github.com/FarmBot/farmbot_os) here, with [`Farmbot-Web-App`](https://github.com/FarmBot/Farmbot-Web-App) referenced rather than posted separately.

## Summary

[FarmBot](https://github.com/FarmBot/farmbot_os) (MIT, ~1.2k stars on `farmbot_os` + ~967 on the Web App, active) is the canonical open-source CNC farming robot: a gantry that plants, waters, and weeds a bed, controlled by named *sequences* over a REST + MQTT API. It is the most accessible open farm robot there is, and a natural fit for a validated natural-language layer. This RFC asks the FarmBot community whether a URML intent layer above FarmBot is interesting and what a farm-bed capability declaration should carry.

## The mapping (URML above FarmBot)

URML is not ROS-bound; it dispatches to whatever a substrate exposes. FarmBot exposes named sequences and a REST/MQTT command API, so URML binds to that the same way it binds AUTOSAR `ara::com` methods (RFC-0019): a FarmBot sequence is declared in the URML manifest as a `program`, and `call_program(name, args)` invokes it after validation. A natural-language request ("water the tomatoes in bed 3") becomes a typed primitive, is validated against the declared bed geometry / tool set / plant vocabulary, and only then dispatches to the sequence API. Validate-before-actuate refuses an out-of-bounds or undeclared action (a tool the bot lacks, a coordinate outside the bed) before a motor moves.

## What is asked

Request for comment from the FarmBot community:

1. Is binding FarmBot sequences via `call_program` (sequence name + typed args) the right granularity to drive FarmBot from an outside intent layer, or is the Web App REST/MQTT API a better seam?
2. What should a URML capability manifest declare to describe a FarmBot honestly — bed/work-area geometry, mounted tools (seeder, waterer, weeder, sensor), plant/crop vocabulary, coordinate bounds?
3. Is a validated natural-language layer interesting to the FarmBot community as a research/education add-on?

Nothing here asks FarmBot to adopt, host, or maintain anything.

## Prior art / context

RFC-0015 (`call_program`) and RFC-0019 (the AUTOSAR binding this mirrors); FarmBot is the agriculture wave's anchor and one of the few open farm robots with a mature ecosystem and a clean command API.

## Implementation note

Outreach only. The post is a GitHub Issue on `FarmBot/farmbot_os` (Discussions are not enabled; an active community Forum exists as an alternative venue) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). The `Farmbot-Web-App` repo is referenced, not posted to separately. Tracked in `examples/lighthouses/outreach-move33.yaml`.
