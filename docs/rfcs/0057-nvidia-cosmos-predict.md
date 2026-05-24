---
rfc: 0057
title: NVIDIA Cosmos-Predict2.5 integration, request for comment from nvidia-cosmos/cosmos-predict2.5 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-23
updated: 2026-05-23
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

# RFC-0057: NVIDIA Cosmos-Predict2.5 integration, request for comment from nvidia-cosmos/cosmos-predict2.5 maintainers

## Summary

URML does not yet ship a Cosmos-Predict integration. RFC-0055 (Cosmos-Reason1) flagged Cosmos-Predict as a future RFC; this is it. The proposed `urml-cosmos-predict-bridge` package wires `cosmos-predict2.5` into URML's predictive-safety lane: before any motion executes, the world model predicts the post-execution video state, and URML's safety envelope checks the prediction. The integration is the NVIDIA-side parallel of RFC-0052 (V-JEPA 2 Vector B). No spec change on URML's side. This RFC documents the integration and requests review and feedback from the `nvidia-cosmos/cosmos-predict2.5` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR.

## Motivation

Cosmos-Predict2.5 (`nvidia-cosmos/cosmos-predict2.5`, 1.2k stars, Apache 2.0 code, NVIDIA Open Model License weights, 21 open issues, Issues enabled, latest release v1.5.1 on April 3, 2026) is the active migration target after `cosmos-predict2` was archived in December 2025. It unifies Text2World, Image2World, and Video2World into a single flow-based generative world foundation model. Inference variants ship for base, auto / multiview, and robot. Cosmos-Predict2.5 uses Cosmos-Reason1 as its text encoder, so [RFC-0055](0055-nvidia-cosmos-reason.md) and this RFC compose: URML programs run through Reason1's constrained decoder become text input to Predict2.5's world simulation.

Two reasons to land this RFC alongside the V-JEPA 2 Vector B work (RFC-0052) rather than instead of it.

The two world models cover different physical scenarios. V-JEPA 2-AC was fine-tuned on 62 hours of Droid (Franka manipulation). Cosmos-Predict2.5's robot variant trains on a wider span (NVIDIA's robotics datasets plus the unified Text2World corpus). URML's predictive-safety lane benefits from being able to query both; different programs route to whichever world model has the right coverage.

The composition with Cosmos-Reason1 is unique. Cosmos-Reason1 (RFC-0055) emits URML programs from images and questions; Cosmos-Predict2.5 takes those URML programs as text input and renders predicted future video. Together they form a closed loop: reason about what to do, predict what the world will look like if it happens, validate the prediction against the safety envelope, execute or reject. No other Move #2 target offers this combined shape.

## Detailed design

URML's existing artifacts that feed in:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives.
- [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md): the active safety envelope, extended by the predictive lane.
- [`reference/validator/`](../../reference/validator/): the validator that gates every URML program.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference, the basis for Reason1's text input to Predict2.5.

### Proposed `urml-cosmos-predict-bridge` shape

A new `reference/cosmos-predict-bridge/` package, structured as a thin wrapper over the published Cosmos-Predict2.5 inference variants (base, auto / multiview, robot).

```
urml_cosmos_predict_bridge/
├── pyproject.toml
└── src/
    └── urml_cosmos_predict_bridge/
        ├── __init__.py
        ├── predictive_safety.py   # URML predictive-safety lane against Cosmos-Predict2.5
        ├── urml_to_prompt.py      # URML program to Cosmos-Predict2.5 text input
        └── adapters.py            # bridge to URML's substrate adapters
```

### The integration: predictive-safety lane

Before URML's validator passes a program to execution, the predictive-safety lane invokes `cosmos-predict2.5` with the current observation and the candidate URML program serialized as the model's text input. The model returns a predicted future video. URML's safety envelope (per [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md)) checks the prediction: workspace bounds, declared obstacle envelopes, end-state object positions. If the prediction violates the envelope, the validator rejects the program before any motor command issues.

```python
# predictive_safety.py
from cosmos_predict import load_world_model  # representative; actual import follows v1.5.1
from urml_validator.envelope import SafetyEnvelope

class CosmosPredictSafetyCheck:
    """URML predictive-safety lane backed by Cosmos-Predict2.5."""

    def __init__(self, checkpoint, manifest_path, variant="robot"):
        self._model = load_world_model(checkpoint, variant=variant)
        self._envelope = SafetyEnvelope.from_manifest(manifest_path)

    def predict_and_validate(self, observation, urml_program):
        prompt = _urml_program_to_prompt(urml_program)  # via urml_to_prompt.py
        predicted_video = self._model.predict(observation, prompt)
        violations = self._envelope.check(predicted_video)
        return _ValidationResult(passed=not violations, violations=violations,
                                 prediction=predicted_video)
```

The pattern is identical in shape to the V-JEPA 2 Vector B predictive-safety lane proposed in RFC-0052. The differences are the input format (Cosmos-Predict2.5 takes text plus image; V-JEPA 2-AC takes action conditioning plus video) and the coverage (Cosmos's robot variant trains on a wider corpus than V-JEPA 2-AC's Droid-only fine-tune).

### Composition with Cosmos-Reason1 (RFC-0055)

Cosmos-Predict2.5 uses Cosmos-Reason1 as its text encoder. URML programs generated by Reason1's constrained decoder (RFC-0055) flow into Predict2.5 as text input. The closed loop:

1. Observation plus question goes into Cosmos-Reason1 with URML grammar constraints.
2. Reason1 emits a candidate URML program.
3. URML validator runs the static checks (manifest, capability, compliance).
4. Cosmos-Predict2.5 takes the observation and the URML program as text input.
5. Predict2.5 returns a predicted future video.
6. URML safety envelope checks the prediction.
7. If validation passes, the program executes; if not, Reason1 is asked for a revised program (next iteration of the loop).

The loop runs entirely on NVIDIA infrastructure if the operator chooses, or distributed across providers, or fully offline (since both Cosmos repos ship weights downloadable under the NVIDIA Open Model License).

### Proposed conformance integration

`URML_COSMOS_PREDICT_INTEGRATION=1` env-gated CI workflow installs `urml_cosmos_predict_bridge`, runs the predictive lane against a deliberately-envelope-violating program, and asserts the lane rejects it. A second test runs a known-good program and asserts the lane accepts it.

### Compatibility notes

- **License.** Cosmos-Predict2.5 source is Apache 2.0; model weights are under the NVIDIA Open Model License (custom licensing via `cosmos-license@nvidia.com`). URML is Apache 2.0. The bridge ships Apache 2.0. Model-weight boundary documented.
- **Compute.** Cosmos-Predict2.5 inference is heavier than policy bridges (it generates video, not actions). The predictive-safety lane is opt-in and CPU/latency-aware; it does not run on every program by default.
- **Coverage.** The robot inference variant is the relevant one for URML; base and auto / multiview variants are out of scope for this RFC.
- **Cosmos-Reason1 dependency.** Predict2.5 uses Reason1 as text encoder. URML's bridge inherits that dependency, which is fine because RFC-0055 already integrates Reason1.
- **Origin.** NVIDIA is incorporated in Santa Clara, CA, US. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: the predictive-safety lane is a future spec RFC (also flagged in RFC-0052). Both Cosmos-Predict2.5 and V-JEPA 2 would be backends for the same lane mechanism; the spec defines the contract, the bridges provide the implementations.
- Reference runtime: proposed new package `reference/cosmos-predict-bridge/`. Not built in this PR.
- Conformance suite: proposed new `cosmos-predict-integration.yml` workflow gated by `URML_COSMOS_PREDICT_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants NVIDIA Cosmos input on the text-input encoding (URML program serialization for Predict2.5's prompt) before writing code.
- **Inference cost.** Generating predicted video is computationally expensive. The predictive-safety lane is intentionally opt-in, but operators will need to choose when to spend the compute. The RFC asks for guidance on cost-aware deployment patterns.
- **Multiple-NVIDIA-RFC concern.** RFC-0050 (Isaac Lab plus GR00T), RFC-0055 (Cosmos-Reason1), and now this RFC are three NVIDIA RFCs. The mitigation: each targets a genuinely different surface, and the closed-loop composition with Reason1 makes the Predict2.5 work qualitatively additive rather than redundant.
- **V-JEPA 2 overlap.** Both this RFC and RFC-0052 propose predictive-safety lanes. The RFC names this overlap and frames the two as complementary backends to a shared spec mechanism, not competing approaches.

## Alternatives considered

1. **Ship the bridge first, ask NVIDIA later.** Rejected. The URML-program-to-prompt encoding is a design choice worth surfacing.
2. **Combine RFC-0055 (Cosmos-Reason1) and this RFC into one Cosmos RFC.** Rejected. The two cover genuinely different integration shapes (constrained reasoning output vs. world-state predictive safety); a single RFC would dilute both feedback asks. They compose at deployment but stay separate at the RFC level.
3. **Skip Predict2.5, route the predictive-safety lane through V-JEPA 2 only (RFC-0052).** Rejected. V-JEPA 2-AC's Droid-only fine-tune limits coverage. Predict2.5 plus V-JEPA 2 covers more.
4. **Wait for Predict 3.** Rejected. v1.5.1 is recent (April 2026) and stable; the integration is worth landing on the current surface.

## Prior art

- `nvidia-cosmos/cosmos-predict2.5`: the upstream repo (1.2k stars, Apache 2.0 code, NVIDIA Open Model License weights, 21 open issues, Issues enabled, Discussions not visible, v1.5.1 released 2026-04-03, unifies Text2World plus Image2World plus Video2World, robot inference variant, uses Cosmos-Reason1 as text encoder).
- `nvidia-cosmos/cosmos-predict2`: archived in December 2025 (the predecessor).
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): NVIDIA Isaac (Isaac Lab plus GR00T). Different stack, complementary.
- [RFC-0052](0052-meta-fair-vjepa2.md): V-JEPA 2 integration. The Meta-side parallel of the predictive-safety lane. This RFC is the NVIDIA-side parallel.
- [RFC-0055](0055-nvidia-cosmos-reason.md): Cosmos-Reason1 integration. Composes with this RFC into the Reason1-plus-Predict2.5 closed loop.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's LLM-to-URML reference. Reason1's constrained decoder is a specialization.
- [`reference/validator/`](../../reference/validator/): the validator the predictive-safety lane extends.

## Unresolved questions

Provisional pending NVIDIA Cosmos maintainer feedback:

1. **URML-to-prompt encoding.** How should a URML program be serialized as text input to Predict2.5? A natural-language paraphrase, the raw YAML, a structured grammar Predict2.5 was trained to expect, or something else?
2. **Robot inference variant.** Predict2.5 ships base, auto / multiview, and robot variants. Is the robot variant the right entry point for URML's predictive-safety lane, or should the bridge support multiple variants?
3. **Cost-aware deployment.** What are NVIDIA's recommendations for when to invoke the predictive-safety lane vs. when to skip it? Per program? Per session? Per hardware operator?
4. **V-JEPA 2 coexistence.** URML's predictive-safety lane (future spec RFC) is intended to support multiple backends including V-JEPA 2 (RFC-0052) and Cosmos-Predict2.5 (this RFC). Are there alignment opportunities between the two integrations that the maintainers see?
5. **Closed-loop with Reason1.** RFC-0055 plus this RFC describes a Reason1-plus-Predict2.5 closed loop. Is there NVIDIA infrastructure (Omniverse, NIM, hosted endpoints) where that loop is already a supported deployment pattern?
6. **Distillation guides and quantization.** The repo mentions February 2026 distillation guides and December 2025 distilled checkpoints. Should the bridge target full-precision or distilled checkpoints by default?
7. **Anything else.**

## Implementation note

RFC-0057 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/cosmos-predict-bridge/` package follows in a later session, gated on NVIDIA Cosmos maintainer feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from nvidia-cosmos/cosmos-predict2.5 maintainers)

1. URML-program-to-prompt encoding.
2. Robot inference variant scoping.
3. Cost-aware deployment guidance.
4. V-JEPA 2 coexistence alignment.
5. Reason1-plus-Predict2.5 closed-loop infrastructure.
6. Distillation and quantization default.
7. Anything else.

## How to respond

`nvidia-cosmos/cosmos-predict2.5` has Issues enabled. Discussions are not visible. URML's planned channel: file an Issue on the repo referencing this RFC, scoped to the URML-program-to-prompt encoding (Q1) and the closed-loop infrastructure question (Q5) so the maintainers see the questions most directly relevant to them. Optional cross-post on the Cosmos-Reason1 Issue thread (filed under RFC-0055) to maintain visibility of the closed-loop story. Optional escalation via `cosmos-license@nvidia.com` if distribution or licensing questions need to escalate beyond the repo maintainers.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only. The predictive-safety lane framing and the composition with RFC-0055 are explicit.
- [x] Motivation grounded in verified facts (verified against the repo on 2026-05-23: nvidia-cosmos/cosmos-predict2.5 1.2k stars, Apache 2.0 + NVIDIA Open Model License, Issues enabled with 21 open, Discussions not visible, v1.5.1 released 2026-04-03, unifies Text2World / Image2World / Video2World, robot inference variant, uses Cosmos-Reason1 as text encoder, predecessor cosmos-predict2 archived December 2025).
- [x] Detailed design proposes a concrete predictive-safety lane that mirrors the V-JEPA 2 Vector B pattern in RFC-0052 and composes with Reason1 in RFC-0055.
- [x] Four alternatives considered.
- [x] Drawbacks are real (proposal-only, inference cost, multiple-NVIDIA-RFC concern, V-JEPA 2 overlap).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Issues enabled, Discussions not visible, v1.5.1 release date verified, archival status of cosmos-predict2 noted.
- [x] V-JEPA 2 overlap acknowledged as complementary rather than competing.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
