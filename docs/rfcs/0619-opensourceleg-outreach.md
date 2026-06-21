---
rfc: 0619
title: Open-Source Leg (opensourceleg) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-21
updated: 2026-06-21
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

# RFC-0619: Open-Source Leg (opensourceleg) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the wearable-and-assistive sub-lane of Move #59.

## Summary

[`neurobionics/opensourceleg`](https://github.com/neurobionics/opensourceleg) (LGPL-2.1, University of Michigan Neurobionics Lab) is the Python SDK for the Open-Source Leg, a powered knee-and-ankle prosthesis used widely in prosthetics research. It drives the leg's actuators (Dephy, Moteus, TMotor) and reads its sensors behind a clean device API, with declared joint and torque limits. URML is a validated-intent layer that sits above an SDK like this: a gait or assist subtask becomes a typed goal carrying the same joint and torque limits as an explicit safety envelope, which URML validates before the SDK is asked to drive the actuator. URML does not run the control loop; it declares and checks. This is a request for comment, framed as a layering relationship given the LGPL-2.1 license.

## The relationship (URML beside opensourceleg)

- **Turn the leg's declared limits into a checked envelope.** The SDK already knows the prosthesis's joint ranges and torque ceilings. URML's contribution is to lift those into a typed safety envelope that a subtask intent is validated against before it reaches the actuator, so an out-of-envelope command is refused statically rather than caught (or not) at runtime. The SDK keeps the actuator and sensor handling; URML is the pre-dispatch gate.
- **An honest, narrow fit.** A prosthesis is coupled to a person, so the value of a typed limit declaration plus a static check is concrete, not decorative. URML adds a small, runtime-neutral statement of the subtask goal and the admissible envelope, and nothing more.

## What is asked

1. Is a typed safety-envelope check (declare the leg's joint and torque limits, validate a subtask intent against them, then call the SDK) useful above opensourceleg's device API?
2. Do the leg's declared limits map onto a URML capability manifest and safety envelope cleanly, or do prosthesis dynamics need something the manifest does not yet express?
3. Would a single joint (knee or ankle) be the right place to try the mapping first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the safety-envelope validation pass, and the declare-and-check posture where the substrate keeps actuation (RFC-0020). Companion to RFC-0618 (CORC) in the wearable-and-assistive sub-lane of Move #59.

## Implementation note

Outreach only. The post is a GitHub Issue on `neurobionics/opensourceleg` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The LICENSE is LGPL-2.1; stated, not asked, and the relationship is layering only, with no shared code. Tracked in `examples/lighthouses/outreach-move59.yaml`.
