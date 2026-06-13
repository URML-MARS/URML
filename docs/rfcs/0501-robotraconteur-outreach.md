---
rfc: 0501
title: Robot Raconteur integration — request for comment
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

# RFC-0501: Robot Raconteur integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It is the anchor of the middleware / control / drivers wave (Move #45): targets URML *composes with* (a substrate, controller, transport, or interop peer below or beside it), distinct from the platforms wave (Move #44) where URML sits above a whole robot.

## Summary

[`robotraconteur/robotraconteur`](https://github.com/robotraconteur/robotraconteur) (Apache-2.0, ~78 stars, active) is a communication framework for robotics and IoT (an augmented-object protocol with bindings across many languages). URML is a layer above a transport: a person's intent is turned into a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Robot Raconteur is one of the transports URML could dispatch *over*. This RFC asks whether the seam is interesting.

## The mapping (URML beside Robot Raconteur)

- **Validate, then transport.** URML does the decide-then-do: it turns intent into a typed primitive and validates it against the capability manifest + envelope. The validated call then needs to reach the device, and Robot Raconteur's augmented-object services are a clean way to carry it. URML is the validation/intent layer; Robot Raconteur is the transport.
- **Manifest from advertised services.** A Robot Raconteur service advertises typed members (functions, properties). Those map toward a URML capability manifest, so the validator can check that a program only invokes what the service actually exposes.

## What is asked

Request for comment from the Robot Raconteur maintainers:

1. Is URML-validated intent dispatched over Robot Raconteur a sensible composition (URML validates; RR transports)?
2. Could a Robot Raconteur service's advertised members inform a URML capability manifest?
3. Which is the cleaner first seam — the dispatch transport, or the manifest-from-services mapping?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's decide-then-do split (RFC-0002) and its substrate-neutral dispatch model (a validated program runs over whatever transport the deployment uses). Anchor of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `robotraconteur/robotraconteur` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
