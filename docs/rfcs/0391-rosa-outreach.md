---
rfc: 0391
title: ROSA (JPL) integration — request for comment on a validate-before-dispatch layer
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

# RFC-0391: ROSA (JPL) integration — request for comment on a validate-before-dispatch layer

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target, and asking its maintainers for feedback. It builds on URML's validator (the five-pass validate-before-actuate discipline) and the provider-agnostic LLM bridge.

## Summary

[ROSA](https://github.com/nasa-jpl/rosa) (JPL, Apache-2.0, ~1.5k stars) is an LLM agent for ROS: it turns natural language into ROS 1/2 calls via a LangChain toolset. It is the closest conceptual neighbor to URML, and the relationship is complementary rather than competitive: ROSA *generates* actions from language; URML is the typed-intent, capability-manifest, and safety-envelope layer that *validates* an action before it reaches an actuator. This RFC asks the ROSA maintainers whether a validate-before-dispatch layer between the agent and the robot is interesting.

## The mapping (ROSA emits, URML validates)

The two compose cleanly at the boundary between "the model decided" and "the robot moves":

- ROSA (or any LLM agent) emits intent. URML's job is to turn that into a typed primitive and run it through the five passes — argument typing, capability check against the manifest, safety-envelope check, variable-binding resolution, compliance policy — so an action the robot cannot do, or must not do, never dispatches.
- URML is provider-agnostic at the language layer (its LLM bridge is not bound to any model), so it does not compete with ROSA's agent; it sits beneath the agent's output as the guardrail.
- The framing is "ROSA emits, URML validates before dispatch": the agent keeps its reasoning and toolset; URML adds the typed, inspectable, refuse-if-out-of-capability contract that a flight context wants.

## What is asked

Request for comment from ROSA maintainers:

1. Is a typed validate-before-dispatch layer between an LLM agent and ROS useful in your view, or does ROSA's own tool-call validation already cover it?
2. Where would the seam sit — URML validating ROSA's proposed ROS calls, or ROSA targeting URML primitives as its tool surface?
3. Is there interest in a small joint demonstration (a language request → ROSA → URML validation → a Space-ROS / ROS 2 robot)?

Nothing here asks ROSA to adopt, host, or maintain anything.

## Prior art / context

URML's validator (`reference/validator/`) and provider-agnostic LLM bridge (`reference/llm-bridge/`); the natural-language Layer-4 grammar. ROSA is the one target in this wave that is a peer at the *language* layer rather than a substrate below it, which is why the framing is composition, not "URML sits above it."

## Implementation note

Outreach only. The post is a GitHub Discussion on `nasa-jpl/rosa` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
