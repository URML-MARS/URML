---
rfc: 0055
title: NVIDIA Cosmos-Reason1 integration, request for comment from nvidia-cosmos/cosmos-reason1 maintainers
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

# RFC-0055: NVIDIA Cosmos-Reason1 integration, request for comment from nvidia-cosmos/cosmos-reason1 maintainers

## Summary

URML does not yet ship an NVIDIA Cosmos integration. RFC-0050 (Isaac Lab plus GR00T) intentionally scoped Cosmos out. This RFC closes that gap with a focused proposal against `nvidia-cosmos/cosmos-reason1`, the 7B-parameter reasoning vision-language model for physical AI. The proposed `urml-cosmos-bridge` package wraps Cosmos-Reason1's inference path and constrains the model's reasoning output to URML primitive sequences. The reasoner stops emitting free-form text plans and starts emitting validated URML programs that URML's substrate adapter can execute. No spec change on URML's side. This RFC documents the integration and requests review and feedback from the `nvidia-cosmos/cosmos-reason1` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR.

## Motivation

NVIDIA Cosmos is a multi-repo family of foundation models for Physical AI. Cosmos-Reason1 (`nvidia-cosmos/cosmos-reason1`, 946 stars at time of writing, Apache 2.0 code, NVIDIA Open Model License weights, 9 open issues, Issues enabled) is the reasoning variant: a 7B-parameter vision-language model that "enables agents to reason like humans, using prior knowledge, physics understanding and common sense." Adjacent repos in the same org cover world prediction (`cosmos-predict2.5`, the migration target after `cosmos-predict2` was archived in December 2025), post-training (`cosmos-rl`), and customization (`cosmos-cookbook`). Reason 2 was announced at CES 2026.

The integration story for URML is sharper than for other VLA-style targets. Cosmos-Reason1 is not a policy. It is a reasoner. Given an image or video plus a question, it outputs a textual answer that describes what should happen next. The output is unstructured by default, so the value of a URML integration is constraining the reasoner's output space to URML primitive programs. The reasoner stops producing prose plans and starts producing programs URML's validator can gate, URML's substrate adapter can execute, and URML's predictive-safety lane ([RFC-0052](0052-meta-fair-vjepa2.md)) can simulate.

This complements the other Move #2 targets without overlapping. LeRobot (RFC-0040), openpi (RFC-0045), MolmoAct (RFC-0047), Isaac GR00T (part of RFC-0050), and TRI LBM (RFC-0054) all wrap a policy that emits actions. V-JEPA 2 (RFC-0052) is a world model that predicts state. Cosmos-Reason1 is the missing third shape: a reasoner that selects what to do. URML's primitive vocabulary is what it selects from when constrained.

## Detailed design

URML's existing artifacts that feed into a Cosmos-Reason1 bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives Cosmos-Reason1 would emit when constrained.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL grammar that ties natural-language reasoning output to URML programs.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference, including grammar-constrained decoding via GBNF (see [RFC-0021](0021-on-device-llm-bridge.md)).
- [`reference/validator/`](../../reference/validator/): the validator that gates every URML program. Cosmos-Reason1's constrained output goes through it like any other.

### Proposed `urml-cosmos-bridge` shape

A new `reference/cosmos-bridge/` package, structured as a thin adapter over Cosmos-Reason1's published inference path (`scripts/inference.py` with `transformers>=4.51.3`).

```
urml_cosmos_bridge/
├── pyproject.toml
└── src/
    └── urml_cosmos_bridge/
        ├── __init__.py
        ├── constrained_reasoner.py  # constrained-decoding wrapper over Cosmos-Reason1
        ├── prompt_templates.py      # URML-aware prompt templates
        └── adapters.py              # bridge to URML's substrate adapters
```

### The integration: constrained reasoning, not action wrapping

`URMLConstrainedCosmosReasoner` loads a Cosmos-Reason1 checkpoint and runs inference with constrained decoding against URML's grammar. The model's output is forced to fit URML's primitive vocabulary; free-form text becomes a validated URML program before the inference call returns.

```python
# constrained_reasoner.py
from transformers import AutoModelForCausalLM, AutoTokenizer
from urml_validator.grammar import gbnf_for_profile  # URML's existing grammar export

class URMLConstrainedCosmosReasoner:
    """Constrains Cosmos-Reason1's reasoning output to URML primitive programs."""

    def __init__(self, checkpoint_path, manifest_path, profile):
        self._model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
        self._tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        self._grammar = gbnf_for_profile(manifest_path, profile)
        self._manifest = _load_validated(manifest_path)

    def reason(self, video_path, question):
        # Cosmos-Reason1's documented inference path, with URML grammar constraints
        # injected into the decoder. The output is guaranteed parseable as a URML
        # program and is validated against the manifest before return.
        prompt = self._make_prompt(question, video_path)
        program_text = self._model.generate(
            prompt,
            grammar=self._grammar,           # URML GBNF, profile-scoped
            max_new_tokens=1024,
        )
        program = self._tokenizer.decode(program_text)
        return _validate(program, self._manifest)
```

The pattern is closer to URML's existing LLM-bridge ([`reference/llm-bridge/`](../../reference/llm-bridge/)) than to the wrapper bridges for LeRobot, openpi, MolmoAct, GR00T, and TRI LBM. Cosmos-Reason1 is the LLM-bridge side of the integration story for URML; it produces programs rather than actions.

### Proposed prompt templates

`prompt_templates.py` ships URML-aware prompts that elicit Cosmos-Reason1's strongest reasoning on physical scenarios while staying inside URML's grammar:

- **Plan-from-image-goal:** "Given the current image plus the goal image, emit a URML program that takes the robot from the current state to the goal."
- **Plan-from-natural-language:** "Given the current image plus the instruction `<text>`, emit a URML program."
- **Plan-with-constraints:** "Given the current image, the instruction, and the additional constraint `<X>`, emit a URML program that respects the constraint."

The templates make explicit which URML primitives Cosmos-Reason1 should prefer for which observation patterns. Tuning the templates is empirical work that URML and the Cosmos community would do together.

### Proposed URML v0.1 to Cosmos-Reason1 mapping

| URML v0.1 primitive | Cosmos-Reason1 emission |
|---|---|
| `move_to` | Reasoner emits explicit pose targets in the URML grammar; constrained decoding ensures the emitted tokens parse. |
| `grasp` / `release` | Reasoner emits gripper-id-tagged primitive calls. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Reasoner emits Layer-3 compositions over the lower-level primitives. |
| `measure` | Reasoner emits a `measure` call for the sensor of interest before any action sequence; the validator checks the sensor exists in the manifest. |
| `wait_for` (event / threshold / signal) | Reasoner emits explicit `wait_for` calls when its reasoning indicates a precondition needs to hold. |
| `report` (structured status upstream) | Reasoner emits a `report` for status checkpoints. |

The mapping is bidirectional. The bridge can also parse human-written URML programs and feed them back to Cosmos-Reason1 as context, letting the reasoner extend or modify them.

### Proposed conformance integration

Mirror the LLM-bridge conformance lanes documented under [RFC-0021](0021-on-device-llm-bridge.md). A `URML_COSMOS_INTEGRATION=1` env-gated CI workflow installs `urml_cosmos_bridge`, runs Cosmos-Reason1 over a fixed set of scenario videos (the existing red-mug fixture and the warehouse profile fixture) with constrained decoding, and asserts the emitted URML programs validate.

### Compatibility notes

- **License.** Cosmos-Reason1 ships Apache 2.0 code with NVIDIA Open Model License for weights (custom licensing available via `cosmos-license@nvidia.com`). URML is Apache 2.0. The bridge is Apache 2.0. Model-weight license boundary documented per the URML conventions.
- **Provider neutrality.** URML's Core Commitment ([`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) prohibits LLM-vendor lock-in. Cosmos-Reason1 is one LLM among the providers URML already supports (Anthropic, OpenAI, open-weights, on-device). The Cosmos bridge is additive; URML's `reference/llm-bridge/` continues to support all providers.
- **transformers dependency.** Cosmos-Reason1 documents `transformers>=4.51.3`. URML's bridge inherits that floor.
- **Origin.** NVIDIA is incorporated in Santa Clara, CA, US. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **Other Cosmos repos.** `cosmos-predict2.5` (the active migration target after `cosmos-predict2` was archived) is a world-state predictor and is out of scope for this RFC. A future RFC may wire `cosmos-predict2.5` into URML's predictive-safety lane (the [RFC-0052](0052-meta-fair-vjepa2.md) Vector B pattern) once the 2.5 surface stabilizes. `cosmos-transfer1` and `cosmos-rl` are similarly out of scope here.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. URML's existing GBNF export already handles grammar-constrained decoding.
- Reference runtime: proposed new package `reference/cosmos-bridge/`. Not built in this PR.
- Conformance suite: proposed new `cosmos-integration.yml` workflow gated by `URML_COSMOS_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Cosmos-Reason1 is unaffected: the bridge consumes its published inference path with documented `transformers` API extensions for grammar-constrained decoding.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants NVIDIA Cosmos input on the constrained-decoding shape and the prompt-template direction before writing code, especially because the prompt templates encode design decisions about which URML primitives Cosmos should prefer for which observation patterns.
- **Constrained decoding can degrade reasoning quality.** Forcing a reasoner's output through a grammar reduces its expressive surface. URML's primitive vocabulary is intentionally small (20 primitives), which keeps the grammar tractable but also means some Cosmos-Reason1 outputs may not translate cleanly. The RFC asks NVIDIA what the empirical degradation looks like and how to mitigate it.
- **Cosmos is iterating fast.** Reason 2 was announced at CES 2026. The bridge depends on the documented `transformers`-based inference path, which is stable, but URML may need to track Reason 2 specifically once it ships.
- **Two-NVIDIA-RFC concern.** RFC-0050 already covers Isaac Lab plus GR00T. Adding Cosmos here makes two NVIDIA RFCs in Move #2. The mitigation: the two cover genuinely different surfaces (Isaac Lab is a learning framework, Cosmos-Reason1 is a reasoner), and the integration code does not duplicate.

## Alternatives considered

1. **Ship the bridge first, ask NVIDIA later.** Rejected. Constrained-decoding choices and prompt-template direction benefit from pre-RFC input.
2. **Target `cosmos-predict2.5` instead of `cosmos-reason1`.** Rejected for now. cosmos-predict2.5 is a world-state predictor whose URML integration parallels V-JEPA 2 (RFC-0052). The predict surface is also still settling after cosmos-predict2's December 2025 archival. cosmos-reason1's reasoner is the more distinctive integration angle and the more stable surface. Predict can be a future RFC.
3. **Target the broader Cosmos ecosystem (predict plus reason plus transfer plus rl) in one RFC.** Rejected. Four sub-targets in one RFC dilutes the ask and the feedback. Per-target RFCs preserve clarity.
4. **Combine Cosmos-Reason1 with RFC-0050 (Isaac Lab plus GR00T).** Rejected. RFC-0050 explicitly scoped Cosmos out. The strategic-positioning conversation there (URML sits above Isaac Lab) is different enough from the reasoning-integration conversation here that combining them would muddle both feedback asks.

## Prior art

- `nvidia-cosmos/cosmos-reason1`: the upstream repo (946 stars, Apache 2.0 code, NVIDIA Open Model License weights, 9 open issues, Issues enabled, Discussions not visible, 7B-parameter reasoning VLM for physical AI).
- `nvidia-cosmos/cosmos-predict2.5`: the active migration target after `cosmos-predict2` archived December 2025. Out of scope for this RFC.
- `nvidia-cosmos/cosmos-rl` (post-training) and `nvidia-cosmos/cosmos-cookbook` (customization): the ecosystem repos Cosmos-Reason1's README references.
- Cosmos CES 2026 announcement of Reason 2 and Predict 2.5 (January 6, 2026).
- [RFC-0021](0021-on-device-llm-bridge.md): URML's on-device LLM bridge with GBNF grammar-constrained decoding. The mechanism the Cosmos bridge inherits.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): URML's Isaac Lab plus GR00T integration. The other NVIDIA RFC; explicitly scoped Cosmos out so this one could land.
- [RFC-0052](0052-meta-fair-vjepa2.md): URML's V-JEPA 2 integration. World-model parallel; cosmos-predict2.5 is the future Cosmos parallel.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. The Cosmos bridge is a Cosmos-specific specialization of the same pattern.

## Unresolved questions

Provisional pending NVIDIA Cosmos maintainer feedback:

1. **Constrained-decoding integration.** Is grammar-constrained decoding via the standard `transformers` API the right path, or does NVIDIA recommend a Cosmos-specific decoder hook (e.g., something exposed through `cosmos-cookbook`)?
2. **Prompt-template direction.** What prompt shapes elicit Cosmos-Reason1's best reasoning when constrained to URML's primitive vocabulary? The bridge ships templates; NVIDIA's tuning expertise would land them better.
3. **Reason 2 timeline.** When Reason 2 ships, what is the migration path for the bridge? Should it coexist with Reason 1 or replace it?
4. **Bridge home.** Standalone `urml-cosmos-bridge` on PyPI (URML-side), contributed example in `nvidia-cosmos/cosmos-cookbook` (NVIDIA-side), or both?
5. **Cosmos-Predict integration.** When cosmos-predict2.5 stabilizes, would NVIDIA welcome a second RFC wiring it into URML's predictive-safety lane (the [RFC-0052](0052-meta-fair-vjepa2.md) Vector B pattern applied to Cosmos)?
6. **Evaluation alignment.** Cosmos-Reason1's published evaluations include video-plausibility judgment. Would a URML-conformance evaluation lane be a useful addition?
7. **Anything else.**

## Implementation note

RFC-0055 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/cosmos-bridge/` package follows in a later session, gated on NVIDIA Cosmos maintainer feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from nvidia-cosmos/cosmos-reason1 maintainers)

1. Constrained-decoding integration path.
2. Prompt-template direction for URML-constrained reasoning.
3. Reason 2 migration path.
4. Bridge home (URML-side vs. NVIDIA-side vs. both).
5. Cosmos-Predict2.5 follow-on RFC appetite.
6. Evaluation alignment with URML conformance.
7. Anything else.

## How to respond

`nvidia-cosmos/cosmos-reason1` has Issues enabled. Discussions are not visible. URML's planned channel: file an Issue on the repo referencing this RFC, scoped to the constrained-decoding integration (Q1) and the prompt-template direction (Q2) so the maintainers see the questions most directly relevant to them. Optional cross-post on the NVIDIA Developer Forum for visibility, and a parallel courtesy email to `cosmos-license@nvidia.com` if the licensing or distribution questions need to escalate beyond the repo maintainers.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only. The reasoning-vs-policy distinction is named explicitly.
- [x] Motivation grounded in verified facts (verified against the repo on 2026-05-23: nvidia-cosmos/cosmos-reason1 946 stars, Apache 2.0 + NVIDIA Open Model License, Issues enabled with 9 open, Discussions not visible, 7B-parameter reasoning VLM, transformers>=4.51.3 inference path via scripts/inference.py, sibling repos cosmos-predict2.5, cosmos-rl, cosmos-cookbook, cosmos-predict2 archived December 2025). Reason 2 announced at CES 2026.
- [x] Detailed design proposes a concrete constrained-decoding wrapper that builds on URML's existing GBNF grammar export.
- [x] Four alternatives considered.
- [x] Drawbacks are real (proposal-only, constrained-decoding quality, fast iteration, two-NVIDIA-RFC concern).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added. The mapping uses existing primitives.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Issues enabled, Discussions not visible, `transformers` inference path documented, Cosmos ecosystem repos catalogued, archival status of cosmos-predict2 noted.
- [x] Provider neutrality framing explicit: Cosmos-Reason1 is one provider among URML's multi-provider llm-bridge surface; the Cosmos bridge does not displace others.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
