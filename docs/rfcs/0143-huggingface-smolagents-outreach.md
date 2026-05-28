---
rfc: 0143
title: HuggingFace smolagents (Apache-2.0 agent framework) integration, request for comment from huggingface smolagents maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0143: HuggingFace smolagents (Apache-2.0 agent framework) integration, request for comment from huggingface maintainers

## Summary

URML does not yet ship a smolagents manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for HuggingFace smolagents — the code-generation agent framework — over [`huggingface/smolagents`](https://github.com/huggingface/smolagents) (Apache-2.0), and **requests review and feedback from the huggingface smolagents maintainers**. No spec change.

This RFC is **distinct from Move-2 RFC-0040 (HuggingFace LeRobot)**. LeRobot is HuggingFace's robotics-policy library; smolagents is the agent-framework layer that orchestrates LLM tool-call composition. URML's natural-language-bridge (RFC-0021) composes naturally with smolagents through a registrable `urml_tool` that emits validated programs.

## Motivation

`huggingface/smolagents` is one of the most-active developer-facing agent surfaces (27.5k stars, Issues + Discussions both enabled, last commit `2026-05-26` — daily activity, **not archived**). The framework's distinguishing feature is that agents emit **executable Python code** rather than JSON tool-call objects, which means a `urml_tool` that the agent invokes can compose other URML primitives in the same generated code block.

This composition shape — agent emits code → code calls `urml_tool(...)` → URML validates against manifest → URML dispatches to substrate adapter — is the natural integration shape for URML's NL story. The high-leverage angle is that smolagents's tool registration is one of the cleanest LLM-tool-surface conventions in the agent ecosystem.

URML's outreach is light-touch: smolagents is general-purpose (not robot-specific) and the URML-fit framing is "URML is one tool you can register among many".

## Detailed design

### URML v0.1 capability-manifest mapping (planned `huggingface_smolagents_cell.yaml` fixture — speculative, OS-level)

smolagents is the agent framework, not the robot. URML's manifest declares the robot; smolagents runs above the manifest as the NL layer. The "manifest mapping" here is more about declaring smolagents in the natural-language layer's substrate field than declaring smolagents as a sensor / actuator.

| URML field | Maps to smolagents attribute |
|---|---|
| `nl_layer.framework: custom` (`huggingface_smolagents`) | Declares smolagents is the agent framework above URML |
| `nl_layer.tool_registration_class` | smolagents `Tool` class registration (Python-code-emitting) |
| `nl_layer.execution_model: code_generation` | smolagents emits executable Python, not JSON tool-calls |

### What URML v0.1 does not yet express for smolagents

1. **NL-layer substrate declaration.** URML's v0.1 has no `nl_layer.framework` field. The natural-language layer (RFC-0021) is described conceptually but does not have a manifest declaration today. Spec RFC for NL-layer-substrate declaration is queued (shared with RFC-0108 ROSA-style engagements + RFC-0145 Gemini Robotics SDK).
2. **Code-generation execution model declaration.** smolagents's code-execution model is distinct from JSON-tool-call agents (Anthropic MCP, OpenAI function-calling); the manifest cannot today distinguish.
3. **Robotics-tool registration shape.** smolagents has no built-in robot-tool registry; URML's `urml_tool` would be a contributed addition.

### Compatibility notes

- **Vendor org.** [`huggingface`](https://github.com/huggingface) — vendor-direct.
- **Flagship repo.** [`huggingface/smolagents`](https://github.com/huggingface/smolagents) — Apache-2.0, 27.5k stars, Issues + Discussions both enabled, last commit 2026-05-26 daily activity, **not archived**.
- **Origin.** HuggingFace HQ Paris (FR) / multi-national. Passes US-federal default policy (NATO allied; HQ EU member).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active surface (27.5k stars and growing; daily commits). High community velocity.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; NL-layer-substrate declaration Spec RFC queued in parallel.
- Reference runtime: future `reference/llm-bridge/UrmlTool` (a smolagents-compatible `Tool` subclass) is the natural integration shape; composes above the existing `reference/llm-bridge/` package.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **smolagents is general-purpose, not robotics-specific.** URML-fit is "one tool among many"; engagement is light-touch.
- **NL-layer-substrate Spec RFC prerequisite** (shared with RFC-0108 ROSA + RFC-0145 Gemini Robotics SDK).

## Alternatives considered

1. **Engage HuggingFace at the LeRobot level only.** Move-2 RFC-0040 already did this; smolagents is a distinct framework with its own developer audience.
2. **Cross-citation only.** Considered. The `urml_tool` registration shape is concrete enough that a contributed example in `smolagents/examples/` may be the natural integration; cross-citation is the fallback.
3. **Bundle smolagents + Anthropic MCP (Move-2 RFC-0048) into one agent-framework RFC.** Rejected. Move-2 already engaged MCP separately; smolagents has its own developer surface.

## Prior art

- [`huggingface/smolagents`](https://github.com/huggingface/smolagents) — the upstream repo.
- [`huggingface/lerobot`](https://github.com/huggingface/lerobot) — RFC-0040 Move-2 engaged HuggingFace's robotics-policy library (distinct).
- [RFC-0048 (Anthropic MCP)](0048-anthropic-mcp-outreach.md) — Move-2 engaged Anthropic's MCP framework (sibling agent-tool surface).
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — URML's NL-bridge engagement on the agent-tool layer.
- [RFC-0021 (NL layer)](0021-on-device-llm-bridge.md) — URML's NL substrate that composes with smolagents.

## Unresolved questions

For the huggingface smolagents maintainers:

1. **Tool-registration shape.** Should URML's `urml_tool` ship as (a) a contributed example in `smolagents/examples/`, (b) an external `urml-smolagents-bridge` package, or (c) cross-citation only?
2. **NL-layer substrate declaration.** URML's manifest could declare smolagents as the agent-framework substrate. Useful for downstream observability, or unnecessary friction?
3. **Code-generation execution-model declaration.** Should URML's manifest distinguish code-generating agents (smolagents) from JSON-tool-calling agents (MCP, function-calling), and at what granularity?
4. **Bridge home.** URML repo (`reference/llm-bridge/`), HuggingFace-contributed example, or external?
5. **Conformance listing.** Would the smolagents maintainers consider a README link to URML's compatible-runtimes registry once a working tool ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0143 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`huggingface/smolagents` has Issues + Discussions both enabled. Discussions is the preferred surface for design-discussion (per the framework's documentation style). URML's planned channel: open a single Discussion in the Ideas category, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 27.5k stars, Issues + Discussions enabled, last commit 2026-05-26 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (general-purpose framework not robot-specific, NL-layer Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: HuggingFace FR/multi; default policy passes.
- [x] CLAUDE.md compliance check passed.
