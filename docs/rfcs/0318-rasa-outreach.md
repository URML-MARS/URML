---
rfc: 0318
title: Rasa (open dialogue-management framework) integration, request for comment from Rasa maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-01
updated: 2026-06-01
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

# RFC-0318: Rasa (open dialogue-management framework) integration, request for comment from Rasa maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

Rasa manages multi-turn conversation: it tracks dialogue state and decides what to do next. URML is the opposite end of that pipe: given a decided action, it validates it against a robot's real capabilities and dispatches it safely. A Rasa custom action that emits a validated URML intent lets Rasa own the conversation and URML own the safe robot dispatch. This RFC **requests review from the Rasa maintainers**. Apache-2.0 both sides; no spec change.

## Motivation

[`RasaHQ/rasa`](https://github.com/RasaHQ/rasa) (Apache-2.0, ~21k stars, Issues enabled, active, **not archived**, verified 2026-06-01) is the leading open dialogue-management framework. URML's Move #12 engaged the speech I/O layer (STT/TTS); Rasa sits one layer up, at conversation management. The clean division of labor is concrete: Rasa decides *what the user wants across a conversation*, URML decides *whether the robot can safely do it and then does it*.

## Detailed design

### URML composes below Rasa's decision, above the robot

| URML concept | Rasa concept | Relationship |
|---|---|---|
| Validated intent dispatch (Layer 2) | custom action (`Action.run`) | A Rasa action emits a URML program; URML validates and dispatches it. |
| Capability manifest (Layer 1) | action availability | A manifest tells a Rasa bot which robot actions are even possible. |
| Fail-closed validation | dialogue fallback | A URML validation failure becomes a Rasa fallback utterance ("I can't do that here, because ..."). |

### What URML v0.1 does not yet express

1. A conversation-context handle (multi-turn state feeding a single URML dispatch). Likely no spec change needed; URML stays single-intent and Rasa owns state. Flagged for confirmation.

### Spec / validator / runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; additive (RFC document only).

## Drawbacks

- Proposal-only.
- Both projects touch natural language; the post must be clear that URML is not a dialogue manager and does not overlap Rasa, it is the safe-dispatch target a Rasa action calls.

## Alternatives considered

1. Treat Rasa as covered by the Move #12 speech work. Rejected: Move #12 is speech I/O; Rasa is dialogue management, a distinct layer and maintainer group.
2. Position URML as a Rasa alternative. Rejected and wrong: URML is single-intent robot dispatch, not conversation management; the honest framing is complementary.

## Prior art

- [`RasaHQ/rasa`](https://github.com/RasaHQ/rasa).
- The Move #12 STT/TTS cluster (Whisper, piper1-gpl); [RFC-0048 (Anthropic MCP / Agent Skills)](0048-anthropic-mcp-and-agent-skills.md) as the agent-tool prior art; sibling [RFC-0317 (openWakeWord)](0317-openwakeword-outreach.md).

## Unresolved questions

For the Rasa maintainers:

1. Is a documented pattern for a Rasa custom action that emits validated URML robot intent interesting to reference?
2. Does the division "Rasa owns dialogue state, URML owns validated robot dispatch" match how you would expect robotics users to wire Rasa to a robot?
3. Anything else.

## Implementation note

Single RFC document. Ledger entry in [`outreach-move22.yaml`](../../examples/lighthouses/outreach-move22.yaml).

## How to respond

`RasaHQ/rasa` has Issues enabled. URML's planned channel: a single Issue pointing to this RFC, framed as a complementary custom-action pattern.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-01 (Apache-2.0, ~21k stars, Issues enabled, active, isArchived: false).
- [x] Alternatives (two); drawbacks real (NL-overlap framing risk); additive; no spec change.
- [x] Provenance: Rasa (DE); default policy passes.
- [x] CLAUDE.md compliance: complementary layer, not a dialogue manager; composes above the robot, below Rasa's decision; no commercial surface.
