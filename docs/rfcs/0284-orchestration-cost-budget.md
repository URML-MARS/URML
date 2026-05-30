---
rfc: 0284
title: orchestration.cost_budget — declaring per-request cost / token budgets in the Layer-1 manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-30
updated: 2026-05-30
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

# RFC-0284: `orchestration.cost_budget` and streaming declarations

## Summary

RFC-0261 declared `orchestration.framework` (LangGraph, smolagents, Gemini Robotics SDK) and deferred cost / token-budget declarations and streaming-vs-batch execution declarations. This RFC closes both deferrals: adds `orchestration.cost_budget` with per-request token limits, per-deployment monthly caps, and cost-cap-per-request limits; adds `orchestration.streaming_mode` with stream / batch / either values. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0261 deferred-question on cost / token-budget and streaming-vs-batch execution.

## Motivation

Production LLM-bridge deployments have real budget concerns:

1. **Runaway token costs are a known failure mode.** An agent stuck in a loop can issue thousands of LLM calls before an operator notices.
2. **Streaming vs batch affects user-facing latency.** A `listen` primitive followed by a streaming response is operationally different from a batch response delivered in one shot.
3. **Per-deployment monthly caps are common in production.** A deployment running with a $500/month LLM budget should declare that in the manifest so deployment-side observability can enforce.

URML's manifest cannot today declare any of these.

## Detailed design

### Field shape

`cost_budget` and `streaming_mode` are added under the existing `orchestration` block (RFC-0261).

```yaml
orchestration:                              # block defined in RFC-0261
  framework: langgraph
  execution_model: state_graph
  cost_budget:                              # NEW — this RFC
    max_tokens_per_request: 32000
    max_tokens_per_session: 256000
    max_requests_per_minute: 60
    max_concurrent_requests: 10
    monthly_cap:
      usd: 500
      tokens: 50000000
    cost_attribution:
      organization: example_research_lab
      project: urml_pilot_q3_2026
  streaming_mode: stream                    # NEW — stream | batch | either
  streaming_options:
    chunk_size_tokens: 50
    timeout_first_chunk_ms: 5000
    timeout_total_ms: 60000
  framework_options:                        # from RFC-0261
    model_provider: openai
    model_id: "hf://openai/gpt-4o@v2024-11"  # RFC-0277 hf:// scheme
```

### Cost-budget semantics

- **`max_tokens_per_request`**: hard cap; the validator enforces under `--policy` that the model's effective context window supports the cap (informational warning if the model has a smaller context). The runtime enforces by passing as a parameter to the LLM call.
- **`max_tokens_per_session`**: cumulative cap across a single conversational session.
- **`max_requests_per_minute`**: rate limit.
- **`max_concurrent_requests`**: concurrency limit.
- **`monthly_cap`**: ceiling for the deployment-wide cost over a calendar month. Informational at validate time; deployment-side observability enforces.
- **`cost_attribution`**: documentation; downstream billing tooling consumes.

### Streaming-mode semantics

| Value | Description |
|---|---|
| `stream` | Streaming responses (deltas arrive incrementally) |
| `batch` | Batch response (full response arrives in one shot) |
| `either` | Either; runtime picks based on framework default |

### Schema fragment (extending RFC-0261's orchestration block)

```jsonc
{
  "orchestration": {
    "properties": {
      "cost_budget": {
        "type": "object",
        "properties": {
          "max_tokens_per_request": { "type": "integer", "minimum": 1 },
          "max_tokens_per_session": { "type": "integer", "minimum": 1 },
          "max_requests_per_minute": { "type": "integer", "minimum": 1 },
          "max_concurrent_requests": { "type": "integer", "minimum": 1 },
          "monthly_cap": {
            "type": "object",
            "properties": {
              "usd": { "type": "number", "minimum": 0 },
              "tokens": { "type": "integer", "minimum": 0 }
            }
          },
          "cost_attribution": {
            "type": "object",
            "properties": {
              "organization": { "type": "string" },
              "project": { "type": "string" }
            }
          }
        }
      },
      "streaming_mode": {
        "enum": ["stream", "batch", "either"]
      },
      "streaming_options": {
        "type": "object",
        "properties": {
          "chunk_size_tokens": { "type": "integer", "minimum": 1 },
          "timeout_first_chunk_ms": { "type": "integer", "minimum": 0 },
          "timeout_total_ms": { "type": "integer", "minimum": 0 }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional fields.** Missing fields acceptable; defaults are runtime-driven.
2. **`max_tokens_per_request <= max_tokens_per_session`**. Logical consistency.
3. **`streaming_mode: stream` requires `streaming_options.timeout_first_chunk_ms`.** Streaming deployments need a first-chunk timeout. Missing emits soft suggestion.
4. **`streaming_mode: batch` + `streaming_options` declared**. Streaming options on a batch-only deployment is harmless but unusual; the validator emits an informational note.
5. **`monthly_cap.usd` consistency.** When `monthly_cap.usd > 0` AND `framework_options.model_provider` is unset, the validator emits a soft suggestion (cost-cap matters per provider).
6. **`max_tokens_per_request` vs model context.** If a specific model is declared via `framework_options.model_id` and the model has a known context limit (e.g., `gpt-4o` has 128k context), the validator can cross-check. URML's validator does not maintain a model-context database; the check is opportunistic and only when URML's documentation captures the model's context.
7. **Forward-compat.** Closed enum on streaming_mode.

### Default-policy file additions (RFC-0003)

Optional `policy_max_monthly_cap_usd: <number>` field. Unset for v0.1. When set:

- Any manifest with `orchestration.cost_budget.monthly_cap.usd` exceeding the policy maximum fails under `--policy`.
- Manifests without `orchestration.cost_budget.monthly_cap` declared fail under `--policy` (the policy requires explicit budget declaration).

### Reference-runtime behavior

Reference runtimes read cost_budget and streaming_mode to configure the LLM-bridge dispatcher. The runtime enforces `max_tokens_per_request` and `max_concurrent_requests` at dispatch time. The runtime does not implement monthly-cap enforcement; that's deployment-side observability tooling.

### Conformance test additions

`conformance/tests/test_manifest_orchestration_budget.py`:

1. Manifest without `cost_budget` passes (no budget declared).
2. Manifest with `max_tokens_per_request: 1000 + max_tokens_per_session: 500` fails (logical inconsistency).
3. Manifest with `streaming_mode: stream` and no `timeout_first_chunk_ms` passes with soft suggestion.
4. Manifest with `monthly_cap.usd: 500` and no `model_provider` passes with soft suggestion.
5. Manifest with `monthly_cap.usd: 1000` and `--policy` against policy `policy_max_monthly_cap_usd: 500` fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests unchanged. Default-policy file gains optional field unset for v0.1.

## Drawbacks

- **Cost enforcement is partly external.** URML's validator declares the budget; deployment-side observability enforces monthly caps. URML cannot prevent overruns at runtime; the manifest is documentation.
- **`streaming_mode: either` is the polite default but loses precision.** Some operators prefer explicit declaration; `either` is for prototyping.
- **Cost attribution is opt-in.** Documentation only.
- **Model-context cross-check is opportunistic.** URML's validator can only check models documented in URML; deployment-specific or self-hosted models fall back to the maintainer's declared limit.

## Alternatives considered

1. **Skip cost_budget; rely on deployment-side observability.** Rejected. The manifest is the contract; declaring intent enables consistent audit.
2. **Combine cost_budget with framework_options instead of top-level under orchestration.** Considered. The current shape keeps cost_budget visible at the orchestration top level; framework_options is for framework-specific configs.
3. **Per-tool budget instead of per-request.** Rejected for v0.1. Per-tool budget is over-engineered for the v0.1 LLM-bridge use case.
4. **Use a more granular streaming model (chunked / SSE / WebSocket).** Rejected. The high-level `stream` / `batch` / `either` enum is sufficient; transport-specific concerns belong in `framework_options`.

## Prior art

- [RFC-0261 (orchestration.framework)](0261-orchestration-framework.md) — parent Spec RFC; this RFC closes the deferred cost-budget and streaming-vs-batch questions.
- [Move-11 RFC-0143 (smolagents)](0143-smolagents-outreach.md), [Move-11 RFC-0145 (Gemini Robotics SDK)](0145-gemini-robotics-sdk-outreach.md), [Move-12 RFC-0164 (LangGraph)](0164-langgraph-outreach.md) — outreach RFCs whose frameworks consume these declarations.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — default-policy file this RFC extends.

## Unresolved questions

1. **Multi-provider cost attribution.** Some deployments switch providers based on cost / availability; URML's manifest could declare provider-fallback chains with per-provider cost caps. Future RFC.
2. **Token-vs-cost translation.** Different models have different per-token cost; URML's manifest declares the token budget but the cost is provider-dependent. Future RFC could add an internal pricing table.
3. **Per-program-run budget overrides.** A deployment may want different budgets for different programs (research vs production). Future RFC.

## Implementation plan

1. JSON Schema fragment extending RFC-0261.
2. Validator with seven checks.
3. Conformance tests (five).
4. Update example manifests.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (external enforcement, "either" loses precision, opt-in attribution, opportunistic cross-check).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0261 (parent), Move-11/12 outreach.
- [x] CLAUDE.md compliance: cost-discipline preserved; substrate-neutrality preserved (URML doesn't prefer one model provider).
