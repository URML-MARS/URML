---
rfc: 0558
title: opendbc integration — request for comment
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

# RFC-0558: opendbc integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the AV / ADAS / off-road wave (Move #51). opendbc is the cleanest Layer-1 fit in the wave: it is, in effect, a vehicle actuation HAL.

## Summary

[`commaai/opendbc`](https://github.com/commaai/opendbc) (MIT) is the project that documents and exposes how to read a car's state and actuate steering, gas, and brakes over CAN, across a very large set of vehicles. URML's Layer-1 is exactly the abstraction that wants a HAL like this underneath it: URML validates an intent against a vehicle's declared capabilities and a safety envelope, then dispatches to whatever actuation substrate the vehicle uses. opendbc is that substrate for cars. This RFC asks whether the mapping is useful.

## The mapping (URML beside opendbc)

- **opendbc is the actuation HAL; URML is the validated-intent layer above it.** URML does not define CAN messages and never will; that is opendbc's domain and it does it better than a language ever should. What URML adds is the typed, statically-validated intent that sits above actuation: an intent is checked (argument typing, capability against a manifest, safety envelope, bindings, policy) before any actuation command is produced. opendbc then turns the validated command into CAN.
- **The capability manifest mirrors a vehicle's actuation envelope.** A car's actuatable ranges and supported controls (the kind of thing opendbc encodes per platform) map onto a URML Layer-1 capability manifest, so an intent can be rejected before it reaches the bus if the vehicle cannot do it.

## What is asked

Request for comment from the opendbc maintainers:

1. Is a typed, statically-validated intent layer above a vehicle actuation HAL useful, or does the safety story already live entirely at the controls layer?
2. Could a vehicle's actuation envelope (as opendbc encodes it per platform) inform a URML Layer-1 capability manifest?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-1 hardware abstraction, the capability manifest, the five-pass validator, and the substrate-neutral dispatch model. Anchor of Move #51; opendbc is the clearest vehicle-actuation HAL seam found in the 2026-06-13 candidate search.

## Implementation note

Outreach only. The post is a GitHub Issue on `commaai/opendbc` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move51.yaml`.
