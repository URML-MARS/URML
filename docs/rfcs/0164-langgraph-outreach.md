---
rfc: 0164
title: LangChain LangGraph (agent orchestration DSL) integration, request for comment from langchain-ai maintainers
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

# RFC-0164: LangChain LangGraph (agent orchestration DSL) integration, request for comment from langchain-ai maintainers

## Summary

URML does not yet ship a LangGraph manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for LangGraph — LangChain's agent-orchestration DSL for stateful multi-step planning — over [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) (MIT), and **requests review and feedback from the langchain-ai maintainers**. No spec change.

**This is URML's first agent-orchestration RFC in Move #12** (RFC-0143 huggingface/smolagents was the Move-11 sibling). LangGraph's `StateGraph` abstraction lets URML programs spawn delegated sub-agents for multi-step planning under uncertainty — a substrate URML's typed-intent layer can compose with cleanly. **Completes Move-12 batch 3** (5 robot-command-library / orchestration targets).

## Motivation

`langchain-ai/langgraph` is one of the most-active agent-orchestration surfaces (MIT, 33.2k stars, Issues enabled, last commit `2026-05-28` — daily activity, **not archived**). LangGraph's distinguishing abstractions are:

- **`StateGraph`** — typed state objects passed between nodes, with conditional edges letting the graph branch based on state.
- **Checkpointing** — every state transition is persisted; the graph can be paused, resumed, and rolled back.
- **Multi-agent composition** — graphs can call sub-graphs, enabling hierarchical agent delegation.

LangGraph is interesting to URML for three reasons:

1. **Delegated-planning substrate.** URML's Layer-3 expresses deterministic behavior composition; some robot tasks require dynamic re-planning under uncertainty (target moved, environment changed, tool failed). LangGraph's `StateGraph` is the substrate that handles the dynamic-replanning loop; URML can express the typed-intent fragments LangGraph composes.
2. **Distinct from smolagents (Move-11 RFC-0143).** smolagents is code-generation-agent (the agent emits executable Python code); LangGraph is state-graph-agent (the agent is a typed state machine). Both are general-purpose orchestration frameworks; URML's manifest can declare either as the orchestration substrate. The engagement-shapes are different.
3. **LangChain ecosystem reach.** LangChain is the dominant LLM-app ecosystem; LangGraph is its current canonical orchestration layer. URML being declarable as a LangGraph node-type puts URML programs into the largest LLM-tooling ecosystem with minimal friction.

URML's outreach here is **light-touch** (matching the smolagents engagement posture): LangGraph is general-purpose, not robot-specific, and URML's framing is "URML is one node type you can register in a StateGraph, alongside many others".

## Detailed design

### URML v0.1 capability-manifest mapping (planned `langgraph_cell.yaml` fixture — OS-level)

LangGraph is the agent-orchestration layer, not the robot. URML's manifest declares the robot; LangGraph runs above the manifest as the planning layer. The "manifest mapping" here is more about declaring LangGraph in the natural-language layer's substrate field than declaring LangGraph as a sensor / actuator.

| URML field | Maps to LangGraph attribute |
|---|---|
| `nl_layer.orchestration_framework: custom` (`langgraph`) | Declares LangGraph is the orchestration substrate above URML |
| `nl_layer.orchestration_state_class` | LangGraph's typed `State` class definition (URML's manifest references the import path) |
| `nl_layer.orchestration_node_registry: [<node-name>, ...]` | Declares the LangGraph nodes URML registers (one per URML primitive or composed behavior) |
| `nl_layer.orchestration_checkpoint_backend: memory \| sqlite \| postgres \| custom` | Declares LangGraph's checkpoint persistence backend |
| `nl_layer.orchestration_execution_model: state_graph` | Distinguishes state-graph-agents (LangGraph) from code-generation-agents (smolagents, RFC-0143) |

### What URML v0.1 does not yet express for LangGraph

1. **NL-layer orchestration-framework declaration.** URML's v0.1 has no `nl_layer.orchestration_framework` field. Spec RFC for orchestration-framework declaration is queued, shared with Move-11 RFC-0143 (smolagents) and RFC-0145 (DeepMind Gemini Robotics SDK).
2. **Typed-state-class declaration.** LangGraph's typed `State` class is the substrate URML's primitives mutate. URML's manifest needs to declare the import path.
3. **Checkpoint-backend declaration.** LangGraph's persistence backend is a deployment-defining choice URML's manifest can express for downstream observability.
4. **Execution-model enumeration.** `state_graph \| code_generation \| function_calling` distinguishes the three dominant agent-execution patterns URML can compose with. The smolagents RFC (0143) surfaced this gap; LangGraph confirms the enumeration.

### Compatibility notes

- **Vendor org.** [`langchain-ai`](https://github.com/langchain-ai) — vendor-direct (LangChain Inc).
- **Flagship repo.** [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) — MIT, 33.2k stars, Issues enabled, Discussions disabled, last commit `2026-05-28` (daily activity), **not archived**.
- **Companion repos.** [`langchain-ai/langchain`](https://github.com/langchain-ai/langchain) (broader LangChain framework); [`langchain-ai/langsmith-sdk`](https://github.com/langchain-ai/langsmith-sdk) (observability SDK).
- **Origin.** LangChain Inc (US). Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active surface (daily commits, 33.2k stars). LangChain Inc is well-funded; engagement-velocity should be high.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; orchestration-framework declaration Spec RFC queued (shared with RFC-0143 smolagents + RFC-0145 Gemini Robotics SDK).
- Reference runtime: future `reference/orchestration-bridge/UrmlToLangGraphNode` (a LangGraph-compatible node class wrapping URML primitives + a `urml_validate` conditional edge that gates state transitions on URML's static checker) is the natural integration shape.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **LangGraph is general-purpose, not robotics-specific.** URML-fit is "one node type among many"; engagement is light-touch.
- **Orchestration-framework Spec RFC prerequisite** (shared with Move-11 RFCs 0143 / 0145).
- **LangChain dependency footprint.** LangGraph pulls in the broader LangChain dependency tree; URML's reference adapter would inherit that.
- **Checkpoint backend complexity.** Persistence-backend choices (memory / sqlite / postgres / custom) are deployment-shape concerns that URML's manifest cannot fully validate without knowing the deployment context.

## Alternatives considered

1. **Engage HuggingFace smolagents (Move-11 RFC-0143) only as the canonical orchestration substrate.** Rejected. smolagents and LangGraph address different agent-execution patterns; URML's manifest should support both.
2. **Treat LangGraph as out-of-scope; have URML's NL layer handle orchestration itself.** Rejected explicitly per CLAUDE.md: "sit above existing runtimes". LangGraph is the dominant orchestration runtime in the LLM ecosystem; URML compiles to it.
3. **Bundle this RFC with smolagents (RFC-0143).** Rejected. Different ecosystems, different engagement channels. The shared Spec RFC for orchestration-framework declaration captures the commonality.
4. **Engage LangChain core (`langchain-ai/langchain`) instead of LangGraph specifically.** Rejected. LangChain core has many surfaces; LangGraph is the focused orchestration layer URML's mapping targets directly.
5. **Cross-citation only.** Considered. The state-graph execution model is concrete enough that an explicit RFC is worth maintainer time.

## Prior art

- [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) — the upstream repo.
- [`langchain-ai/langchain`](https://github.com/langchain-ai/langchain) — broader framework.
- [RFC-0143 (HuggingFace smolagents)](0143-huggingface-smolagents-outreach.md) — Move-11 sibling, code-generation-agent framework (distinct execution model).
- [RFC-0145 (DeepMind Gemini Robotics SDK)](0145-deepmind-gemini-robotics-sdk-outreach.md) — Move-11 sibling, multimodal-VLA tool-call surface.
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — URML's NL-bridge agent-tool surface engagement.
- [RFC-0021 (On-device LLM bridge)](0021-on-device-llm-bridge.md) — URML's NL substrate that LangGraph composes above.

## Unresolved questions

For the langchain-ai maintainers:

1. **Orchestration-framework declaration shape.** Is `langgraph` the right slug for URML's manifest, or does the team prefer a specific naming convention?
2. **Typed-state-class declaration.** Is the import-path field the right shape for declaring URML's `State` reference, or is a different mechanism preferable?
3. **Execution-model enumeration.** Is `state_graph \| code_generation \| function_calling` the right tri-state, or does the LangChain team see this differently?
4. **Checkpoint-backend declaration.** Is the `memory \| sqlite \| postgres \| custom` enumeration the right granularity?
5. **Node-vs-graph hosting.** URML can register as either a single LangGraph node or a sub-graph. Which framing matches LangChain's preferred extension pattern?
6. **Adapter home.** URML-side adapter in URML's `reference/orchestration-bridge/`, contributed example in `langgraph/examples/`, or external bridge repo?
7. **Conformance listing.** Would the langchain-ai maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0164 ships as a single RFC document PR (Move-12 batch 3 — robot-command-library cluster). **Completes the Tier A half of Move-12** (RFCs 0153-0164 drafted). Ledger entry in [`examples/lighthouses/outreach-move12.yaml`](../../examples/lighthouses/outreach-move12.yaml).

## How to respond

`langchain-ai/langgraph` has Issues enabled (Discussions disabled). URML's planned channel: open a single Issue on `langchain-ai/langgraph` framed as "URML manifest declaration + orchestration-substrate integration shape, design RFC", pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 33.2k stars, Issues enabled, last commit 2026-05-28 daily, isArchived: false).
- [x] Distinction from smolagents (Move-11 RFC-0143) called out (state-graph vs. code-generation execution models).
- [x] At least one alternative considered (five).
- [x] Drawbacks real (general-purpose framework, Spec-RFC prerequisite, LangChain dependency footprint, checkpoint-backend complexity).
- [x] Sibling RFC cross-links explicit (RFC-0143 smolagents, RFC-0145 Gemini SDK, RFC-0108 ROSA).
- [x] Completes-Tier-A framing noted.
- [x] No spec change proposed in this RFC.
