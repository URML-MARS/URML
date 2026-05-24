---
rfc: 0052
title: Meta FAIR V-JEPA 2 integration, request for comment from facebookresearch/vjepa2 maintainers
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

# RFC-0052: Meta FAIR V-JEPA 2 integration, request for comment from facebookresearch/vjepa2 maintainers

## Summary

URML does not yet ship a V-JEPA 2 integration. This RFC proposes the integration shape for a future `urml-vjepa2-bridge` reference package with two integration vectors against the open V-JEPA 2 release from Meta FAIR: (a) URML primitive sequences as the action vocabulary V-JEPA 2-AC's planner consumes, and (b) V-JEPA 2's predicted future-state embeddings as a predictive-safety signal that URML's validator can consult before any motion executes. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the `facebookresearch/vjepa2` maintainers.

The second vector is unusual among Move #2 targets. Every other RFC in Move #2 wraps a policy that emits actions. V-JEPA 2 is a world model that predicts what comes next. URML's safety envelope plus V-JEPA 2's prediction together offer something neither does alone: pre-execution simulation of a candidate URML program against a learned model of the world.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR.

## Motivation

V-JEPA 2 (Video Joint Embedding Predictive Architecture, version 2) is Meta FAIR's open video-based world model. The original release in June 2025 (`facebookresearch/vjepa2`) shipped with V-JEPA 2.1 announced March 2026. Roughly 4k stars at time of writing, MIT licensed (with some Apache 2.0 utilities), Issues enabled (63 open, 13 PRs visible). The model is trained in two phases: self-supervised pretraining on over one million hours of video without action labels, then action-conditioned fine-tuning on 62 hours of robot video from the Droid dataset. V-JEPA 2-AC is the action-conditioned variant; it has been deployed zero-shot on Franka arms in two labs for picking and placing with 65 to 80 percent success on novel objects.

Three things make V-JEPA 2 a worthwhile Move #2 target.

It is genuinely open. MIT-licensed code, downloadable weights, PyTorch Hub integration. No waitlist, no partner program gate. Meta FAIR's research posture means there is no product to protect; engagement with researchers is the value the lab seeks.

It is the only world-model-shaped target in the Move #2 landscape. Every other open Move #2 release (LeRobot's policies, openpi's π models, MolmoAct, GR00T, RT-X) is a policy that emits actions. V-JEPA 2 predicts future state instead. URML's safety envelope has a natural use for that prediction: validate a candidate URML program by simulating its expected end state in V-JEPA 2's latent space and checking the prediction against the envelope before any motor command goes out.

The robotics fine-tuning corpus is OXE-adjacent. V-JEPA 2-AC was fine-tuned on Droid, which is part of the Open X-Embodiment ecosystem. RFC-0046 proposes URML annotation on OXE trajectories. If that annotation lands, V-JEPA 2-AC can be re-fine-tuned on URML-annotated Droid and emit URML primitive sequences natively as its action representation. The two RFCs reinforce each other.

## Detailed design

URML's existing artifacts that feed into a V-JEPA 2 bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives the bridge consumes and produces.
- [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md): the active safety envelope. Vector B extends the envelope check to consult a learned world model.
- [`reference/validator/`](../../reference/validator/): the validator that gates every URML program. Vector B adds a predictive lane.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime most likely to host V-JEPA 2-AC's Franka demos.

### Proposed `urml-vjepa2-bridge` shape

A new `reference/vjepa2-bridge/` package (and PyPI mirror `urml-vjepa2-bridge`), structured as a thin adapter over the V-JEPA 2 PyTorch Hub interface.

```
urml_vjepa2_bridge/
├── pyproject.toml
└── src/
    └── urml_vjepa2_bridge/
        ├── __init__.py
        ├── action_encoder.py       # Vector A: URML primitives to V-JEPA 2-AC action conditioning
        ├── predictive_safety.py    # Vector B: V-JEPA 2 prediction to URML envelope check
        └── droid_annotation.py     # URML annotation pass over Droid trajectories
```

### Vector A: URML programs as V-JEPA 2-AC action input

V-JEPA 2-AC consumes an action conditioning signal and predicts future video embeddings. The bridge translates a URML primitive sequence into the action conditioning V-JEPA 2-AC expects. Each primitive maps to one or more action-conditioning tokens; the model's prediction proceeds normally over those tokens.

```python
# action_encoder.py
import torch
from vjepa2 import load_model  # documented PyTorch Hub interface

class URMLActionEncoder:
    """Encodes a URML primitive sequence as V-JEPA 2-AC action conditioning."""

    def __init__(self, manifest_path):
        self._manifest = _load_validated(manifest_path)

    def encode(self, urml_program) -> torch.Tensor:
        # Translate each primitive into the action-conditioning vector
        # V-JEPA 2-AC was fine-tuned to consume on Droid. Joint targets and
        # gripper transitions become the conditioning tokens; profile primitives
        # like wait_for and report become no-op tokens at the conditioning level.
        return _to_vjepa2_conditioning(urml_program, self._manifest)
```

### Vector B: V-JEPA 2 predictions as URML predictive safety

Before URML's validator passes a program to execution, it consults V-JEPA 2 to predict the end-state video embedding. URML's safety envelope (per [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md)) gains a predictive lane: if the predicted end state violates a workspace bound, collides with a declared obstacle in the manifest, or otherwise falls outside the envelope, the validator rejects the program before any motor command issues.

```python
# predictive_safety.py
class V_JEPA2_PredictiveSafetyCheck:
    """Validates a URML program by simulating it in V-JEPA 2's latent space."""

    def __init__(self, model_weights, manifest_path, envelope):
        self._model = load_model(model_weights)
        self._envelope = envelope

    def predict_and_validate(self, observation, urml_program) -> ValidationResult:
        predicted_end_state = self._model.predict(observation, urml_program)
        violations = self._envelope.check(predicted_end_state)
        return ValidationResult(passed=not violations, violations=violations,
                                prediction=predicted_end_state)
```

The lane is opt-in. URML's existing static validation runs first; the predictive check is an additional gate, useful when the operator wants higher confidence on a program before executing it on real hardware. The validator is non-bypassable from any URML execution surface (per [`CLAUDE.md`](../../CLAUDE.md)); the predictive lane composes with rather than replaces the existing checks.

### Proposed Droid annotation pass

`droid_annotation.py` runs URML's existing LLM bridge over the Droid trajectory language captions plus action tensors and emits URML primitive sequences per trajectory. The output is a Droid-shaped sidecar (matching the OXE annotation shape proposed in [RFC-0046](0046-open-x-embodiment.md)) that V-JEPA 2-AC can be re-fine-tuned on. The annotation pass is the bridge between the Vector A action-input story and the data needed to train the model to consume URML natively.

### Proposed URML v0.1 to V-JEPA 2-AC mapping (Vector A)

| URML v0.1 primitive | V-JEPA 2-AC conditioning |
|---|---|
| `move_to` | A contiguous run of end-effector-pose tokens at the resolution V-JEPA 2-AC was fine-tuned on (Droid frame rate). |
| `grasp` / `release` | A gripper-channel transition token. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed sequences of `move_to` plus `grasp` / `release` conditioning runs. |
| `measure` | No-op at the conditioning level; the observation already contains sensor reads. |
| `wait_for` (event / threshold / signal) | A pause token in the conditioning stream. V-JEPA 2's prediction continues evolving the world model during the wait. |
| `report` (structured status upstream) | No-op at the conditioning level; URML's report channel runs in parallel. |

### Proposed conformance integration

`vjepa2-integration.yml` env-gated by `URML_VJEPA2_INTEGRATION=1`. Two lanes: one runs Vector A on the V-JEPA 2 demo notebook scenario and asserts the action encoding round-trips against URML's primitive vocabulary, the other runs Vector B with a deliberately envelope-violating program and asserts the predictive check rejects it.

### Compatibility notes

- **License.** V-JEPA 2 is MIT licensed for the majority of code with Apache 2.0 for some utility files. URML is Apache 2.0. The bridge is Apache 2.0. Compatible.
- **PyTorch and Hub.** V-JEPA 2 ships PyTorch Hub integration. URML's bridge consumes the documented Hub interface, not internals.
- **Origin.** Meta is incorporated in Menlo Park, CA, US. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **Research posture.** Meta FAIR's stated posture is research, not product. The integration is a research-collaboration shape, not a commercial-partnership shape. Outreach language reflects that.
- **No ROS dependency.** V-JEPA 2 has no ROS coupling. URML's substrate-neutral promise holds: a V-JEPA 2-AC-driven workflow can target any URML substrate via the substrate adapter.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: a future spec RFC would document the predictive-safety lane formally (predictive-validation contract, what counts as a violation in latent space, how the world model's confidence is exposed to the validator). Not included in this PR.
- Reference runtime: proposed new package `reference/vjepa2-bridge/`. Not built in this PR.
- Conformance suite: proposed new `vjepa2-integration.yml` workflow gated by `URML_VJEPA2_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. V-JEPA 2 is unaffected: the bridge consumes its published interfaces.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants FAIR input on the action-conditioning encoding and on the predictive-safety lane before writing code, especially since both vectors interact with model internals more deeply than a standard policy-wrapper bridge does.
- **Predictive safety is novel and unproven.** No URML target currently uses learned-world-model prediction as a safety gate. The RFC names this as an open research direction, not a shipping feature. If the FAIR community pushes back on the framing, Vector B can be scoped down to evaluation use only (visualize predicted end states without gating execution on them).
- **Action-conditioning quality depends on Droid coverage.** V-JEPA 2-AC was fine-tuned on 62 hours of Droid. Its action-conditioning vocabulary reflects what Droid covers. URML primitives that fall outside Droid's covered behaviors (e.g., bimanual coordination, walking gaits, drone maneuvers) will not be well represented until URML-annotated trajectories outside Droid are added.
- **Research-only target.** V-JEPA 2 has no product surface; outreach will not unlock partner-program access or anything similar. Engagement value is academic credibility and a foothold in the world-model branch of robotics research.

## Alternatives considered

1. **Ship the bridge first, ask FAIR later.** Rejected. FAIR's research posture is collaborative; pre-RFC is the right shape.
2. **Vector A only, skip Vector B.** Rejected. Vector B is what makes V-JEPA 2 uniquely interesting to URML; without it the bridge is a redundant action wrapper similar to RFC-0045 (openpi) or RFC-0040 (LeRobot).
3. **Vector B only, skip Vector A.** Rejected. Vector A is the data path that connects URML programs to V-JEPA 2's training; without it Vector B remains a one-shot evaluation tool without a clear loop.
4. **Bundle the Droid annotation pass into RFC-0046 (OXE) rather than this RFC.** Considered. The annotation lives logically in either place. Keeping it here keeps the V-JEPA 2 RFC self-contained, and the cross-reference to RFC-0046 carries the connection.
5. **Wait for V-JEPA 3.** Rejected. V-JEPA 2.1 is recent (March 2026) and the surface is stable enough to engage on now. Waiting forfeits the early-collaboration opportunity.

## Prior art

- `facebookresearch/vjepa2`: the upstream V-JEPA 2 repo (MIT plus Apache 2.0, Issues enabled, V-JEPA 2 released 2025-06-25, V-JEPA 2.1 announced 2026-03-16, PyTorch Hub integration, demo notebook `vjepa2_demo.ipynb`).
- `facebookresearch/jepa`: the original V-JEPA repo (3.9k stars, Issues enabled, the predecessor; useful for citation continuity).
- V-JEPA 2 arxiv paper: 2506.09985.
- V-JEPA 2-AC: the action-conditioned variant. Fine-tuned on 62 hours of Droid; deployed zero-shot on Franka in two labs.
- Authors: Adrien Bardes, Quentin Garrido, Jean Ponce, Xinlei Chen, Michael Rabbat, Yann LeCun, Mahmoud Assran, Nicolas Ballas (per the original V-JEPA paper; V-JEPA 2 carries forward a substantially overlapping author list).
- [RFC-0046](0046-open-x-embodiment.md): URML's OXE annotation RFC. Droid is OXE-adjacent and the annotation passes share their shape.
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0045](0045-physical-intelligence-openpi.md): URML's other Move #2 policy-wrapper bridges. V-JEPA 2 is a different shape (world model, not policy) but the package layout follows the same convention.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's NL-to-URML reference, the basis for the Droid annotation pass.

## Unresolved questions

Provisional pending FAIR maintainer feedback:

1. **Action-conditioning encoding.** What is the right token-level encoding for URML primitives in V-JEPA 2-AC's action conditioning? The Droid action representation (joint targets, gripper channel) is straightforward; the URML-primitive boundaries are the new question.
2. **Predictive-safety framing.** Is using V-JEPA 2 predictions as a pre-execution validation gate (Vector B) a use case FAIR finds defensible, or would the lab prefer the integration stay at evaluation-only (visualize predictions, do not gate execution)?
3. **Droid annotation pass.** Is the URML annotation on Droid trajectories an additive sidecar (matching the [RFC-0046](0046-open-x-embodiment.md) OXE shape) acceptable to the Droid maintainers, or does FAIR see this differently?
4. **Bridge home.** Standalone `urml-vjepa2-bridge` on PyPI (URML-side), contributed example in `facebookresearch/vjepa2` (FAIR-side), or both?
5. **Research collaboration shape.** Is there a workshop, benchmark, or paper FAIR is planning where a URML conformance lane would be a useful contribution?
6. **Future model versions.** V-JEPA 2.1 is the current version. How tightly should the bridge couple to the 2.1 interface vs. anticipating a 3.x evolution?
7. **Anything else.**

## Implementation note

RFC-0052 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/vjepa2-bridge/` package and the predictive-safety spec addendum follow in later sessions, gated on FAIR feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from facebookresearch/vjepa2 maintainers)

1. URML-primitive encoding in V-JEPA 2-AC action conditioning.
2. Predictive-safety lane framing (gate execution vs. evaluation-only).
3. Droid annotation acceptability.
4. Bridge home (URML-side vs. FAIR-side vs. both).
5. Research-collaboration shape (workshop, benchmark, paper alignment).
6. Coupling to V-JEPA 2.1 vs. anticipating 3.x.
7. Anything else.

## How to respond

`facebookresearch/vjepa2` has Issues enabled. Discussions are not visible on the repo (verified surface 2026-05-23). URML's planned channel: file an Issue on `facebookresearch/vjepa2` referencing this RFC, framed as a research-collaboration proposal rather than a feature request, scoped to the action-conditioning encoding (Q1) and the predictive-safety lane (Q2) so the maintainers see the questions most relevant to FAIR. A parallel courtesy email to the corresponding-author addresses listed on the V-JEPA 2 arxiv paper is optional.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only. The world-model framing is named explicitly.
- [x] Motivation grounded in verified facts about V-JEPA 2 (verified against the repo on 2026-05-23: facebookresearch/vjepa2 4k+ stars, MIT plus Apache 2.0, Issues enabled, V-JEPA 2 released 2025-06-25, V-JEPA 2.1 released 2026-03-16, PyTorch Hub integration, vjepa2_demo.ipynb notebook). V-JEPA 2-AC fine-tuned on 62 hours of Droid, deployed zero-shot on Franka in two labs, 65 to 80 percent pick-and-place success per the published paper.
- [x] Detailed design proposes a concrete two-vector package with code sketches for both vectors. The world-model angle is reflected in Vector B's predictive-safety lane, which is novel and named as such.
- [x] Five alternatives considered.
- [x] Drawbacks are real (proposal-only, predictive-safety novelty, Droid-coverage limits, research-only target).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added. The mapping uses existing primitives.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Issues enabled, Discussions disabled, PyTorch Hub interface documented, author list confirmed against the V-JEPA paper.
- [x] Research-posture framing made explicit: this is a research-collaboration proposal to FAIR, not a commercial-partnership ask.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant. Provider neutrality preserved.
