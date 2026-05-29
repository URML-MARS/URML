---
rfc: 0261
title: orchestration.framework — declaring agent orchestration substrate in the Layer-1 manifest
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

# RFC-0261: `orchestration.framework` — declaring agent orchestration substrate

## Summary

URML's LLM bridge composes against agent-orchestration frameworks: LangGraph, Hugging Face smolagents, Gemini Robotics SDK, and others. Each implements a different `execution_model` (state graph, code generation, function calling) and a different boundary between URML's typed-intent layer and the orchestration framework's free-form agent reasoning. URML's manifest has no place today to declare which orchestration framework the deployment composes with. This RFC adds an `orchestration` block to the Layer-1 manifest with a closed `framework` enum, an `execution_model` sub-field, and `framework_options`. Optional. Backward compatible.

The surfaces that demanded this RFC are Move-11 RFC-0143 (smolagents), RFC-0145 (Gemini Robotics SDK), and Move-12 RFC-0164 (LangChain LangGraph).

## Motivation

URML's LLM bridge prompt contracts let language models reliably emit valid URML. The bridge composes against orchestration frameworks that handle the LLM-side of the pipeline (prompt construction, function-call dispatch, multi-step reasoning, tool selection). Three frameworks dominate the Move-11/12 outreach surface:

- **LangGraph** (LangChain) — state-graph execution model. URML programs spawn LangGraph sub-agents for delegated planning.
- **smolagents** (Hugging Face) — code-generation execution model. The agent emits Python; URML constrains the function set the code can call.
- **Gemini Robotics SDK** (Google) — function-calling execution model. The agent calls structured functions; URML's primitives are the function set.

Each framework's execution model affects how URML's validator can reason about the agent's output. State-graph agents produce traces URML can validate post-hoc. Code-generation agents produce Python URML can't fully validate (the validator is not a Python interpreter). Function-calling agents produce structured calls URML can validate at the function boundary.

Three concrete consequences:

1. **Bridge dispatch correctness.** URML's LLM bridge must know which framework to compose against; the manifest declaring it lets the bridge select the right prompt contract and validation strategy.
2. **Validator strategy varies per execution model.** URML's static-validation pass works differently against state-graph traces (replayable) vs code-generation outputs (parseable but not validate-able). The manifest tells the validator what to expect.
3. **Tool / function-set declaration.** Function-calling and code-generation models need the URML primitive set as their tool / function inventory. Declaring the framework lets the bridge auto-generate the appropriate tool spec.

The Move-11/12 outreach surface (~5 RFCs total touching orchestration) all surface this gap.

## Detailed design

### Field shape

```yaml
orchestration:                              # NEW — this RFC, top-level optional
  framework: langgraph                       # langgraph | smolagents | gemini_robotics_sdk | custom | none
  execution_model: state_graph               # state_graph | code_generation | function_calling | custom
  framework_options:
    model_provider: openai                   # informational; provider field
    model_id: gpt-4o                         # informational; specific model identifier
    tool_inventory_source: urml_primitives   # urml_primitives | manual | hybrid
    validator_strategy: replay               # replay | parse_only | function_boundary | none
    timeout_ms: 30000
```

### Allowed values

**Framework:**

| Value | Execution model | Reference |
|---|---|---|
| `langgraph` | state_graph | Move-12 RFC-0164 |
| `smolagents` | code_generation | Move-11 RFC-0143 |
| `gemini_robotics_sdk` | function_calling | Move-11 RFC-0145 |
| `custom` | declare via `execution_model` | escape hatch + `framework_note` required |
| `none` | URML programs run without orchestration framework (direct primitive dispatch) | n/a |

**Execution model:**

| Value | Description |
|---|---|
| `state_graph` | Replayable execution traces; URML can validate post-hoc |
| `code_generation` | Agent emits code; URML constrains the function set the code can call |
| `function_calling` | Agent calls structured functions; URML validates at function boundary |
| `custom` | Free-form; deployment maintainer documents in `framework_note` |

### Schema fragment (Layer-1)

```jsonc
{
  "orchestration": {
    "type": "object",
    "properties": {
      "framework": {
        "enum": ["langgraph", "smolagents", "gemini_robotics_sdk", "custom", "none"]
      },
      "framework_note": { "type": "string" },
      "execution_model": {
        "enum": ["state_graph", "code_generation", "function_calling", "custom"]
      },
      "framework_options": {
        "type": "object",
        "properties": {
          "model_provider": { "type": "string" },
          "model_id": { "type": "string" },
          "tool_inventory_source": {
            "enum": ["urml_primitives", "manual", "hybrid"]
          },
          "validator_strategy": {
            "enum": ["replay", "parse_only", "function_boundary", "none"]
          },
          "timeout_ms": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "if": {
      "properties": { "framework": { "const": "custom" } }
    },
    "then": {
      "required": ["framework_note", "execution_model"]
    }
  }
}
```

### Validator behavior

1. **Optional.** Missing block acceptable; deployment runs without LLM-bridge orchestration declaration.
2. **Framework ↔ execution_model consistency.** If `framework: langgraph`, `execution_model` should be `state_graph`. The validator emits a warning when an unusual pairing is declared (e.g., `langgraph + function_calling` is supported in LangGraph but uncommon; the warning surfaces the choice for review).
3. **Custom requires both framework_note and execution_model.** `framework: custom` plus missing either field fails.
4. **Validator-strategy ↔ execution_model.** `validator_strategy: replay` requires `execution_model: state_graph`; `validator_strategy: function_boundary` requires `execution_model: function_calling`. Mismatch fails validation.
5. **Model-provider declaration is informational.** The validator does not check that the model provider is reachable or that the model exists. Documentation only.
6. **Forward-compat.** Closed enums.

### Reference-runtime behavior

Reference runtimes read `orchestration.framework` to select the LLM-bridge dispatch path. The bridge's prompt contract for each framework lives in `reference/llm-bridge/contracts/{framework}.md`. When the manifest declares `framework: langgraph`, the bridge auto-loads the LangGraph-specific contract. When `framework: none`, the bridge dispatches Layer-2 primitives directly.

### Conformance test additions

`conformance/tests/test_manifest_orchestration.py`:

1. Manifest without `orchestration` block passes (optional).
2. Manifest with `framework: langgraph + execution_model: state_graph` passes.
3. Manifest with `framework: langgraph + execution_model: code_generation` passes with warning (unusual pairing).
4. Manifest with `framework: custom` and no `execution_model` fails.
5. Manifest with `validator_strategy: replay + execution_model: function_calling` fails (inconsistent).

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **Framework enum will need to grow.** LangGraph, smolagents, Gemini Robotics SDK are today's main targets. Future RFCs add new frameworks as URML's LLM-bridge outreach surfaces them. The `custom` escape hatch holds the line.
- **Execution-model enum is opinionated.** Three named values plus `custom`. Some frameworks (LangGraph) support multiple execution models; the manifest's single-value declaration captures the deployment's primary mode.
- **Validator-strategy ↔ execution-model consistency check is partial.** Some combinations are theoretically valid that the strict consistency rules in this RFC don't accept. The strict-by-default posture preserves the validator-as-static-gate property; loosening can come via future RFC if real cases surface.
- **No standard for `tool_inventory_source: hybrid` resolution.** When the deployment mixes URML primitives with manual tool definitions, URML's manifest doesn't say how the merge happens. Documentation only at v0.1.

## Alternatives considered

1. **Skip `execution_model`; let `framework` imply it.** Rejected. Some frameworks support multiple execution models; the explicit field captures the deployment's choice.
2. **Make `orchestration.framework: none` the default rather than missing block.** Considered. The current shape uses missing-block as "no declaration"; `none` is an explicit declaration. The distinction matters for validators reasoning about whether to expect orchestration metadata downstream.
3. **Per-primitive orchestration declaration.** Rejected for v0.1. Most deployments are framework-uniform within a deployment; per-primitive granularity is over-engineering.
4. **Nest under `language` block (RFC-0260).** Rejected. Orchestration spans Layer-3 + Layer-4 (intent composition + NL grammar); placing under `language` would narrow the scope incorrectly.

## Prior art

- [Move-11 RFC-0143 (smolagents)](0143-smolagents-outreach.md), [Move-11 RFC-0145 (Gemini Robotics SDK)](0145-gemini-robotics-sdk-outreach.md), [Move-12 RFC-0164 (LangGraph)](0164-langgraph-outreach.md) — the outreach RFCs that surfaced this field.
- [RFC-0260 (language engine classes)](0260-language-engine-classes.md) — sibling Spec RFC; language engines may be invoked by orchestrated agents.
- URML Layer-2 primitive set — the function inventory orchestrated agents target.
- URML LLM bridge prompt contracts (in `reference/llm-bridge/`) — the per-framework contract this RFC's `framework` field selects.

## Unresolved questions

1. **Multi-framework deployments.** Some deployments use multiple orchestration frameworks (LangGraph for high-level planning, smolagents for code-generation sub-tasks). v0.1 of this field is single-framework.
2. **Cost / token-budget declaration.** Orchestration frameworks have per-deployment cost characteristics. URML's manifest could declare token-budget or cost-cap. Future RFC.
3. **Streaming-vs-batch execution.** Some frameworks support streaming output; others are batch-only. URML's manifest does not capture the distinction today.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks (consistency, custom-requires-fields, etc.).
3. Conformance tests.
4. Update LLM-bridge contracts to align per-framework prompt files.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (enum growth, opinion, partial consistency check, hybrid merge undefined).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to Move-11/12 outreach RFCs + sibling RFC-0260.
- [x] CLAUDE.md compliance: enum closure preserves moat; framework-neutrality preserved (URML doesn't pick a winner among LangGraph / smolagents / Gemini); LLM-provider neutrality preserved.
