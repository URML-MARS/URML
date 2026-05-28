---
rfc: 0145
title: DeepMind Gemini Robotics SDK (multimodal VLA developer surface) integration, request for comment from google-deepmind maintainers
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

# RFC-0145: DeepMind Gemini Robotics SDK (multimodal VLA developer surface) integration, request for comment from google-deepmind maintainers

## Summary

URML does not yet ship a Gemini Robotics SDK manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for `google-deepmind/gemini-robotics-sdk` — DeepMind's multimodal VLA developer surface — over [`google-deepmind/gemini-robotics-sdk`](https://github.com/google-deepmind/gemini-robotics-sdk) (Apache-2.0), and **requests review and feedback from the google-deepmind maintainers**. No spec change.

**This is URML's highest-value Move-11 target.** Gemini Robotics is Google DeepMind's headline VLA. The SDK is a developer-facing tool-call surface that composes naturally with URML's natural-language layer (RFC-0021) and `query_detection` primitive — structurally similar to the cuvis-ai-agentic-skills pattern URML engaged in [RFC-0123 (Cubert)](0123-cubert-hyperspectral-outreach.md).

## Motivation

The `gemini-robotics-sdk` repo is the actively-maintained developer surface for Gemini Robotics models. Apache-2.0, 582 stars, Issues enabled, last commit `2026-05-23` very active, **not archived**. The repo is the URML-facing layer regardless of how the underlying model weights are licensed.

**Why this is the highest-value Move-11 target:**

1. **Multimodal VLA tool-call surface** — Gemini Robotics emits tool-calls; URML's primitive vocabulary is the natural typed substrate the calls dispatch to. The composition shape is what URML was designed for.
2. **Same agentic-skills pattern URML engaged in RFC-0123 (Cubert).** Cubert's cuvis-ai-agentic-skills is a small-scale LLM-tool surface for hyperspectral classification; Gemini Robotics is the planet-scale equivalent for generalist VLA.
3. **DeepMind's developer-relations surface is open** — Issues enabled, vendor email behind google.com, Apache-2.0 license. No friction blockers.

URML's RFC engages the multimodal-VLA tool-call surface declaration question. The Spec RFC is shared with RFC-0143 smolagents (code-generation agent surface) and RFC-0108 ROSA (Langchain-tool surface).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `gemini_robotics_cell.yaml` fixture)

| URML field | Maps to Gemini Robotics SDK attribute |
|---|---|
| `name` | Deployment handle (`gemini_robotics_default`) |
| `nl_layer.framework: custom` (`gemini_robotics_sdk`) | Declares the Gemini Robotics SDK is the multimodal VLA above URML |
| `nl_layer.execution_model: tool_call_with_multimodal_context` | Declares Gemini's tool-call execution model |
| `nl_layer.input_modalities` | RGB + RGB-D + language + audio (Gemini's full multimodal surface) |
| `nl_layer.tool_registration_class` | Gemini's tool-registration convention |

### What URML v0.1 does not yet express for Gemini Robotics SDK

1. **Multimodal-VLA tool-call surface declaration.** URML's v0.1 has no `nl_layer.execution_model` field. Spec RFC for NL-layer-substrate declaration is queued; this is the most natural place for Gemini's tool-call surface to slot in. Shared gap with RFC-0143 (smolagents code-generation) and RFC-0108 (ROSA Langchain-tool).
2. **Multimodal-input declaration.** URML's manifest declares sensors individually; it does not today declare that a learned multimodal VLA *consumes* multiple sensor outputs simultaneously. The cross-sensor binding is implicit today.
3. **Model-weights vs SDK-surface boundary.** Gemini Robotics weights are gated; the SDK surface is open. URML's manifest can declare the SDK binding cleanly; the model-access question is operator-side.

### Compatibility notes

- **Vendor / org.** [`google-deepmind`](https://github.com/google-deepmind) — vendor-direct.
- **Flagship repo.** [`google-deepmind/gemini-robotics-sdk`](https://github.com/google-deepmind/gemini-robotics-sdk) — Apache-2.0, 582 stars, Issues enabled, last commit 2026-05-23 active, **not archived**.
- **Origin.** Google DeepMind, US / UK. Passes US-federal default policy.
- **License fit.** Apache-2.0 SDK surface cleanly composes with URML's Apache-2.0 stance. Model weights are separately gated; the SDK binding is what URML's manifest declares.
- **Maintainer signal.** Active surface; DeepMind robotics team. Multiple DeepMind GitHub orgs engaged in Move-2 (mujoco) + this Move-11 (mujoco_playground RFC-0144 + Gemini Robotics SDK RFC-0145).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; NL-layer-substrate declaration Spec RFC queued (shared with RFC-0108 ROSA + RFC-0143 smolagents).
- Reference runtime: future `reference/llm-bridge/GeminiRoboticsBridge` is a strong candidate — Gemini Robotics's tool-call surface composes with URML's existing `reference/llm-bridge/` on-device-LLM substrate at the multimodal-VLA layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **NL-layer-substrate Spec RFC prerequisite.** Same gap as RFC-0108 / RFC-0143.
- **Model-weights access friction.** Gemini Robotics model access is gated; the SDK surface is open. URML's bridge composes with the SDK regardless, but downstream operators need separate Gemini access.
- **Multimodal-input binding is novel design territory.** Cross-sensor binding for a single VLA consumer is not first-class in URML v0.1.

## Alternatives considered

1. **Engage Google DeepMind broader instead of gemini-robotics-sdk specifically.** Rejected. The SDK is the developer surface; vendor engagement should land at the surface URML's bridge composes with.
2. **Bundle Gemini Robotics SDK + ROSA (RFC-0108) into one NL-layer RFC.** Rejected. ROSA is a Langchain ROS agent; Gemini Robotics is a multimodal VLA. Different surfaces, different audiences.
3. **Defer Gemini Robotics SDK until NL-layer-substrate Spec RFC lands.** Rejected. DeepMind's feedback informs the Spec RFC; deferral guarantees no input from the highest-value vendor in the Move-11 wave.

## Prior art

- [`google-deepmind/gemini-robotics-sdk`](https://github.com/google-deepmind/gemini-robotics-sdk) — the upstream repo.
- [RFC-0123 (Cubert cuvis-ai-agentic-skills)](0123-cubert-hyperspectral-outreach.md) — Move-10 engaged Cubert's agentic-skills surface; structurally similar pattern, different domain (hyperspectral classification vs general VLA).
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — URML's NL-bridge engagement on the agent-tool layer; sibling NL-layer-substrate target.
- [RFC-0143 (HuggingFace smolagents)](0143-huggingface-smolagents-outreach.md) — sibling agent-framework engagement (code-generation execution model).
- [RFC-0021 (NL layer)](0021-on-device-llm-bridge.md) — URML's NL substrate that composes with Gemini Robotics SDK.
- [RFC-0144 (DeepMind MuJoCo Playground)](0144-deepmind-mujoco-playground-outreach.md) — sibling DeepMind engagement on the sim-env layer.

## Unresolved questions

For the google-deepmind gemini-robotics-sdk maintainers:

1. **NL-layer substrate declaration manifest fields.** URML's v0.1 has no `nl_layer.execution_model` declaration. A Spec RFC is queued. Manifest field expectations from the Gemini perspective (tool-registration convention, multimodal-context declaration, model-access binding)?
2. **Multimodal-input cross-sensor binding.** Should URML's manifest declare that a multimodal VLA consumes specific sensors simultaneously, and at what granularity?
3. **Bridge home.** URML repo (`reference/llm-bridge/GeminiRoboticsBridge`), `google-deepmind/gemini-robotics-urml` contributed example, or external?
4. **Conformance listing.** Would the maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships?
5. **Coordination with the DeepMind broader engagement.** RFC-0060 mujoco-core, RFC-0144 mujoco_playground, and this RFC-0145 all engage DeepMind robotics surfaces. Is a single-entry-point preferred, or separate per-repo?
6. **Anything else.**

## Implementation note

RFC-0145 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml). This is the **highest-value Move-11 target**; engagement should be prioritized when posting commences.

## How to respond

`google-deepmind/gemini-robotics-sdk` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the multimodal-VLA tool-call surface declaration question front-and-centre.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 582 stars, Issues enabled, last commit 2026-05-23 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (NL-layer Spec-RFC prerequisite, model-access friction, multimodal-binding novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Google DeepMind US/UK; default policy passes.
- [x] CLAUDE.md compliance check passed.
