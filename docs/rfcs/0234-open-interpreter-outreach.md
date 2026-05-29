---
rfc: 0234
title: Open Interpreter (natural-language agent) integration as a verified robot-action layer, request for comment from Open Interpreter maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0234: Open Interpreter integration as a verified robot-action layer

## Summary

URML does not yet document a relationship to a general-purpose natural-language agent. This RFC documents how URML can serve as the **verified, capability-gated robot-action layer** beneath [`OpenInterpreter/open-interpreter`](https://github.com/openinterpreter/open-interpreter) (AGPL-3.0), and **requests review and feedback from the Open Interpreter maintainers**. No spec change.

**This is a Move-18 frame-break RFC, and the batch's conceptual-peer reframe.** Open Interpreter is URML's closest sibling outside robotics: it turns natural language into executed action. The difference is the safety boundary. Open Interpreter runs arbitrary code; URML validates intent against a capability manifest and safety envelope before anything executes. The reframe is that URML is not a competitor to such an agent, it is the layer that makes its robot actions safe.

## Motivation

Open Interpreter lets a language model run code on a machine to accomplish a natural-language request. Repo at [`OpenInterpreter/open-interpreter`](https://github.com/openinterpreter/open-interpreter) (AGPL-3.0, 63.7k stars, Issues enabled, last commit 2026-05-17, **not archived**).

URML benefits from documenting this relationship because:

1. **It is the same problem URML solves, minus the boundary.** Both turn language into action. URML's contribution to an agent like Open Interpreter is precisely what the agent lacks for robots: static validation against a manifest before execution. This is the cleanest articulation of why URML exists.
2. **It generalizes the agent-tool pattern URML already uses.** URML has framed itself as a registered tool for ROSA (RFC-0108), smolagents (RFC-0143), and LangGraph (RFC-0164). Open Interpreter is the general-purpose, highest-reach instance of that pattern.
3. **Reach.** Open Interpreter is one of the most-starred NL-to-action projects in existence. A documented "use URML for the robot parts" path puts URML in front of a very large agent-building audience.

## Detailed design

### The integration shape, stated plainly

This is **not** a substrate adapter and **not** a manifest mobility mapping. URML exposes itself as a tool the agent calls when the request is "control a robot." The agent plans; URML validates and executes.

```
user NL request --> Open Interpreter (plans) --> calls URML tool with a URML program
                                              --> URML validates against manifest + safety envelope
                                              --> URML executes on the substrate (or refuses)
```

| URML concept | Role in the Open Interpreter relationship |
|---|---|
| URML program | The typed, validated artifact the agent emits for robot actions instead of raw `rospy` / shell code |
| Capability manifest | The declaration of what the target robot can do; the agent cannot exceed it |
| Safety envelope | The static gate that refuses an unsafe or out-of-capability action before execution |
| Tool / function interface | How URML advertises itself to the agent (a callable that takes a URML program, returns a validated execution result) |

### What URML v0.1 does not yet express

1. **Agent-tool registration declaration.** URML has no declared, reusable description of itself as a callable action layer (tool schema, input contract, refusal semantics). This is shared with the agent-tool RFCs (RFC-0108 / RFC-0143 / RFC-0164) and is a queued Spec RFC.
2. **Plan-versus-execute boundary semantics.** The contract for what the agent is allowed to decide (the plan) versus what URML owns (validation and execution) is not formalized.
3. **Confidence / confirmation gating.** When the agent is uncertain, URML has no field to require human confirmation before a validated-but-consequential action runs.

### Compatibility notes

- **Project.** [`OpenInterpreter/open-interpreter`](https://github.com/openinterpreter/open-interpreter) — Open Interpreter, US. AGPL-3.0.
- **Engagement repo.** AGPL-3.0, 63.7k stars, Issues enabled, last commit 2026-05-17, **not archived**.
- **Origin.** US-domiciled. Passes US-federal default policy (OSS, no covered-list vendor).
- **License fit.** AGPL-3.0 is network-copyleft and does **not** compose into URML's Apache-2.0 by code vendoring. Integration stays at the client / IPC boundary: URML is invoked as a tool over a process or API boundary, with no Open Interpreter code in the URML repo. Same boundary discipline as RFC-0168 (LibreTranslate, AGPL) and RFC-0166 (piper1-gpl).
- **Maintainer signal.** Very large community, active issue tracker.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; agent-tool registration declaration + plan-versus-execute boundary + confirmation gating are queued Spec RFCs (shared with the agent-tool RFC set).
- Reference runtime: a future thin bridge exposing URML's validate-then-execute path as an Open Interpreter tool is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Not a runtime adapter.** Like RFC-0230 (OpenBCI), this is a positioning / cross-pollination RFC. URML does not run inside Open Interpreter; it is called by it. The RFC should not be read as claiming a substrate.
- **Spec-RFC prerequisites** (tool registration, plan-execute boundary, confirmation gating).
- **AGPL boundary** constrains integration to the client / IPC boundary; no shared-code path.
- **Positioning risk.** A reader could hear "URML is the safe layer you lack" as a competitive claim. URML's framing is collaborative: the agent keeps planning, URML owns the robot-safety gate.

## Alternatives considered

1. **Engage via Anthropic MCP / Agent Skills only (RFC-0048).** Rejected as a substitute. MCP is one transport; Open Interpreter is a concrete, high-reach agent worth engaging directly. The two are complementary.
2. **Treat Open Interpreter as out of scope (not robotics).** Rejected. It is the clearest external example of URML's own thesis (language to action) and the sharpest place to articulate the safety boundary URML adds.
3. **Propose embedding URML inside Open Interpreter.** Rejected. AGPL plus URML's Apache-2.0 stance means the relationship is tool-call at a boundary, never embedding.

## Prior art

- [`OpenInterpreter/open-interpreter`](https://github.com/openinterpreter/open-interpreter) — the upstream agent.
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — the closest sibling; URML as a validated tool an NL-to-ROS agent registers.
- [RFC-0143 (smolagents)](0143-huggingface-smolagents-outreach.md) + [RFC-0164 (LangGraph)](0164-langgraph-outreach.md) — the agent-tool / orchestration RFC set this generalizes.
- [RFC-0168 (LibreTranslate)](0168-libretranslate-outreach.md) — the AGPL client-boundary integration shape.
- [RFC-0230 (OpenBCI / BrainFlow)](0230-openbci-brainflow-outreach.md) — sibling Move-18 non-adapter bridge (intent input; this RFC is the agent / output side).

## Unresolved questions

For the Open Interpreter maintainers:

1. **Tool contract.** If URML exposed itself as a tool (takes a URML program, validates against a robot manifest, executes or refuses), what tool / function interface would fit Open Interpreter's model best?
2. **Plan-versus-execute boundary.** Are you comfortable with a division where the agent plans and emits a URML program, but URML owns validation and execution (including refusal)?
3. **Refusal semantics.** How should a validation refusal surface back to the agent so it can re-plan rather than retry blindly?
4. **Confirmation gating.** For consequential robot actions, should the tool require explicit human confirmation, and how would that fit your interaction loop?
5. **License boundary.** URML stays Apache-2.0 and integrates at the client / IPC boundary with no Open Interpreter code vendored. Does that match your expectation?
6. **Bridge home.** URML repo (a thin Open-Interpreter-tool bridge), an Open Interpreter example, or neither?
7. **Interest.** Is a "use URML for the robot-safety parts" path something your users would want, or is robot control too far from Open Interpreter's center of gravity to matter?
8. **Anything else.**

## Implementation note

RFC-0234 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`OpenInterpreter/open-interpreter` has Issues enabled. URML's planned channel: a single GitHub Issue (labelled `question` or `enhancement`) pointing to this RFC. If a maintainer prefers another venue or human-only correspondence, that preference is welcome and URML will route to it.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (AGPL-3.0, 63.7k stars [63738], Issues enabled, last commit 2026-05-17, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (not a runtime adapter, Spec-RFC prerequisites, AGPL client-only boundary, positioning risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: US-domiciled OSS; AGPL integration at the client / IPC boundary; default policy passes.
- [x] CLAUDE.md compliance check passed.
