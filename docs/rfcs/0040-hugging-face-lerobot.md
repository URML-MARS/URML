---
rfc: 0040
title: Hugging Face LeRobot integration, request for comment from huggingface/lerobot maintainers
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

# RFC-0040: Hugging Face LeRobot integration, request for comment from huggingface/lerobot maintainers

## Summary

URML does not yet ship a LeRobot integration. This RFC proposes the integration shape for a future `lerobot_policy_urml` package that follows LeRobot's published "Bring Your Own Policies" plugin convention (`huggingface.co/docs/lerobot/bring_your_own_policies`). The package would wrap any `PreTrainedPolicy` subclass and translate its `select_action(...)` / `predict_action_chunk(...)` output into URML primitive calls before any motion reaches the substrate adapter. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the `huggingface/lerobot` maintainers.

This is the first Move #2 RFC. Move #1 (RFCs 0023–0038) targeted robot OEMs and component vendors. Move #2 turns the same outreach pattern upward, from substrate vendors to the AI/ML layer whose models drive them. RFC-0040 is proposal-only, in the precedent set by RFC-0037 (OSRF / Gazebo) and RFC-0020 (Autoware AV): no shipping bridge, by design, until the maintainers weigh in.

## Motivation

LeRobot is the canonical Apache 2.0 robot-learning library: 24.3k+ stars at time of writing, latest release v0.5.1 (2026-04-07), led by Remi Cadene (`@cadene`, ex-Tesla, founded the project at Hugging Face in March 2024), backed by Hugging Face's Pollen Robotics acquisition. It hosts PyTorch policies (ACT, Diffusion, VQ-BeT, Multitask DiT; HIL-SERL, TDMPC; Pi0Fast, Pi0.5, GR00T N1.5, SmolVLA, XVLA) and defines the `LeRobotDataset` v3 format (MP4 video plus Parquet state/action). Most public open-weights robotics releases of 2025 and 2026 are reachable through LeRobot.

The integration story for URML is one sentence. A `PreTrainedPolicy`'s `select_action(...)` returns a `torch.Tensor` of substrate-specific actions (joint targets, end-effector poses, tokenized controls). URML's Layer-2 primitive set is the substrate-neutral vocabulary one layer above that tensor. A LeRobot policy whose post-processor emits URML primitives can be retargeted across ROS 2, PX4, Isaac Sim / Lab, MuJoCo, AUTOSAR Adaptive, and OPC UA Robotics by switching URML's substrate adapter, without retraining the policy.

Two things make this RFC concrete rather than aspirational. First, LeRobot already publishes a formal plugin convention ("Bring Your Own Policies") that names exactly the extension points URML needs: `PreTrainedConfig.register_subclass`, `PreTrainedPolicy`, and the `make_<name>_pre_post_processors` discovery hook. Second, an external `lerobot_policy_*` package precedent already exists (`danielsanjosepro/lerobot_policy_ditflow`), so URML's package would not be the first third-party plugin, only the first that targets a substrate-neutral output vocabulary instead of a new model architecture.

Hugging Face's posture is the open-standards posture: Apache 2.0, public datasets governance, model cards by default, plus an explicit plugin convention. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. LeRobot does not compete with URML for the "common action vocabulary" role. LeRobot is the library that hosts the policy. URML is the spec the policy's post-processor can target. The two are orthogonal.

## Detailed design

URML's existing artifacts that would feed into a LeRobot plugin:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives a LeRobot policy's post-processor would emit.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL layer above the primitives. Relevant when a LeRobot policy is conditioned on language.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the existing LLM-to-URML translation reference. LeRobot's policies plug into the same conceptual slot, with a different input modality.
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/) and [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): the sim siblings that already evaluate URML programs in physics.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime most likely to host LeRobot-trained policies on hardware (Franka, UR, SO-100, and the rest of the research-arm population).

### Proposed `lerobot_policy_urml` package shape

Following LeRobot's published "Bring Your Own Policies" convention verbatim. Package layout:

```
lerobot_policy_urml/
├── pyproject.toml                 # name = "lerobot_policy_urml", requires-python >= 3.12
└── src/
    └── lerobot_policy_urml/
        ├── __init__.py
        ├── configuration_urml.py  # URMLPolicyConfig(PreTrainedConfig), @register_subclass("urml")
        ├── modeling_urml.py       # URMLPolicy(PreTrainedPolicy), name = "urml"
        └── processor_urml.py      # make_urml_pre_post_processors(...)
```

The key class:

```python
# modeling_urml.py
from lerobot.policies.pretrained import PreTrainedPolicy
from .configuration_urml import URMLPolicyConfig

class URMLPolicy(PreTrainedPolicy):
    config_class = URMLPolicyConfig
    name = "urml"

    def __init__(self, config, dataset_stats=None):
        super().__init__(config, dataset_stats)
        self._inner = config.inner_policy  # another PreTrainedPolicy subclass

    def reset(self):
        self._inner.reset()
        # also reset URML primitive accumulator

    def get_optim_params(self) -> dict:
        return self._inner.get_optim_params()

    def forward(self, batch):
        return self._inner.forward(batch)

    def predict_action_chunk(self, batch, **kwargs):
        return self._inner.predict_action_chunk(batch, **kwargs)

    def select_action(self, batch, **kwargs):
        # 1. Get the inner policy's raw action tensor.
        raw = self._inner.select_action(batch, **kwargs)
        # 2. Translate the action chunk to URML primitives (post-processor responsibility).
        # 3. Hand the primitives to URML's substrate adapter, which executes them.
        # 4. Return the raw action tensor unchanged, so LeRobot's evaluation harness
        #    sees a normal policy.
        return raw
```

URMLPolicy is a wrapper, not a model. It composes another `PreTrainedPolicy`, lets that policy do the inference, and inserts a URML translation step between the raw action tensor and the substrate. The wrapper pattern preserves LeRobot's training and evaluation contracts (the inner policy stays trainable; eval sees a tensor the way it expects) while making the substrate-neutral routing testable in isolation.

### Proposed URML v0.1 to LeRobot mapping

The mapping is the post-processor's job. `make_urml_pre_post_processors(...)` returns a `PolicyProcessorPipeline` that, on each call, batches successive `select_action(...)` outputs into URML primitive calls.

| URML v0.1 primitive | LeRobot policy realisation |
|---|---|
| `move_to` | A run of joint-target or end-effector-pose action tensors is collapsed into one `move_to(pose)` with a tolerance derived from `config.horizon` and `config.n_action_steps`. |
| `grasp` / `release` | A gripper-close / gripper-open token in the action tensor's gripper channel maps to `grasp` / `release` with the configured gripper id. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences over `move_to` plus `grasp` / `release`. No new Protocol method. |
| `measure` | A sensor reading present in the policy's observation batch is the read-side primitive that backs `measure`. |
| `wait_for` (event / threshold / signal) | A condition-gated pause inside the policy (e.g. action mask) surfaces as an explicit `wait_for`. |
| `report` (structured status upstream) | A labelled status token in the policy's output maps to `report`. |

### Proposed dataset annotation

Optional and additive. A `LeRobotDataset` v3 episode can gain a `urml_program` sidecar in its Parquet sidecar files alongside the existing state/action columns: a list of URML primitive calls aligned to the episode's action timeline. Existing episodes without the field continue to work. Two consumers benefit. Re-training: cross-embodiment fine-tuning becomes substrate-aware, not only hardware-aware. Evaluation: a trained policy can be diff-checked against its expected URML emission, which is a coarser and more interpretable signal than raw-action error.

### Proposed conformance integration

Mirror `mujoco-integration.yml` and `isaac-integration.yml` gating. A `URML_LEROBOT_INTEGRATION=1` env-gated CI workflow installs `lerobot_policy_urml`, runs a LeRobot policy wrapped in `URMLPolicy` against a hermetic sim, and asserts that the emitted URML primitives validate against URML's static envelope. The in-tree conformance suite continues to use `MockROSAdapter`.

### Compatibility notes

- **License.** LeRobot is Apache 2.0. URML is Apache 2.0. No friction.
- **Python.** LeRobot's BYOP convention requires Python >= 3.12. URML's reference packages target the same lower bound, so the dependency band overlaps cleanly.
- **Hub.** Hugging Face Hub supports offline snapshot download, so URML's "validated programs run offline" rule (per [`CLAUDE.md`](../../CLAUDE.md)) holds.
- **Origin.** Hugging Face is incorporated in Delaware, US. Passes the URML US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **PyTorch dependency.** LeRobot is PyTorch-only. URML's reference runtimes are framework-agnostic. The plugin package opts in to torch. Everything else stays clean.
- **Pollen Robotics.** Hugging Face acquired Pollen Robotics in 2024 and now ships open hardware (SO-100, Reachy) alongside the library. The URML integration would benefit either way: a single plugin retargets across the Pollen lineup and other arms via URML's existing `cobot-runtime`.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/lerobot-bridge/` (which, if published, becomes the PyPI package `lerobot_policy_urml`). Not built in this PR. The RFC requests HF Robotics feedback first.
- Conformance suite: proposed new `lerobot-integration.yml` CI workflow and a `URML_LEROBOT_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The LeRobot side gains a plugin package, which by the BYOP convention does not touch LeRobot internals.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping plugin.** RFCs 0023–0036 reference real adapter code. This RFC references a proposal. The honest framing: URML wants HF input on the wrapper pattern and the dataset-annotation shape before shipping the `lerobot_policy_urml` package, because both are observable choices the BYOP convention does not pin down. The OSRF parallel (RFC-0037) covers this posture.
- **LeRobot evolves fast.** v0.5.1 just released (2026-04-07) and v3 of the dataset format is also recent. Policy interfaces and dataset schema could move while URML is integrating. Mitigation: the plugin depends on LeRobot's public BYOP-documented `PreTrainedPolicy` / `PreTrainedConfig` / processor surface, not on internal modules, and the package versions track LeRobot majors.
- **Wrapper indirection.** URMLPolicy composes another `PreTrainedPolicy` rather than implementing one. That is the right shape (URML is a routing concern, not a model) but it does mean a user training a fresh policy under `lerobot-train --policy.type urml` would need to pass the inner-policy type as configuration, which is one layer of indirection beyond the BYOP examples.
- **Dataset annotation invasiveness.** Adding a `urml_program` sidecar to LeRobotDataset v3 is invasive in spirit even if backward-compatible in practice. Mitigation: ship the annotator as a sidecar Parquet file in the same episode directory at first, not a column added to the canonical state/action Parquet.

## Alternatives considered

1. **Ship the plugin first, ask LeRobot maintainers later.** Rejected. HF's posture is collaborative and a pre-RFC saves rework, especially on the dataset-annotation surface where the choice is not pinned by the BYOP convention.
2. **Skip the plugin convention, ship URML's bridge as an independent package that imports LeRobot.** Rejected. The BYOP convention exists exactly so plugins integrate with `lerobot-train` and the CLI for free. Bypassing it would forfeit the distribution that motivated picking LeRobot in the first place.
3. **Target Physical Intelligence (openpi) directly instead of LeRobot.** Rejected for now. openpi is one policy family, hosted inside LeRobot. The leverage is higher one level up.
4. **Skip Move #2 entirely until Move #1 closes.** Rejected. Move #1 outreach is sent (per [`examples/lighthouses/outreach.yaml`](../../examples/lighthouses/outreach.yaml)) and the response window runs in parallel. The AI/ML layer is a different audience and engaging it now does not collide.

## Prior art

- `huggingface/lerobot`: the upstream library (24.3k+ stars, v0.5.1 on 2026-04-07, Apache 2.0).
- LeRobot "Bring Your Own Policies" docs: `huggingface.co/docs/lerobot/bring_your_own_policies`. The convention URML's package would follow.
- `lerobot.policies.pretrained.PreTrainedPolicy` and `lerobot.configs.policies.PreTrainedConfig`: the base classes.
- `lerobot.datasets.lerobot_dataset.LeRobotDataset`: the v3 dataset class.
- `danielsanjosepro/lerobot_policy_ditflow`: existing third-party `lerobot_policy_*` plugin, cited in the BYOP docs.
- Cadene et al., ICLR 2026 (LeRobot citation paper): the canonical citation surface.
- Hugging Face's Pollen Robotics acquisition (2024): hardware context.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. The LeRobot plugin is the policy-side sibling.
- [RFC-0021](0021-on-device-llm-bridge.md): on-device LLM bridge. Relevant to running LeRobot policies on-device under the same bridge contract.
- [RFC-0037](0037-osrf-gazebo-integration.md): proposal-only RFC precedent (sim substrate).
- [RFC-0020](0020-autoware-av-substrate.md): proposal-only RFC precedent (AV substrate).
- RFCs 0023–0038: the per-target outreach pattern this RFC inherits.

## Unresolved questions

Provisional pending HF Robotics maintainer feedback:

1. **Wrapper vs. native.** Is the `URMLPolicy(PreTrainedPolicy)` wrapper composing an inner policy the right shape, or would HF prefer URML to live entirely in a custom `PolicyProcessorPipeline` (post-processor only) without a new policy class? The wrapper makes URML observable to the LeRobot CLI and eval harness as a distinct policy type. A pure-processor shape stays out of the policy registry but limits introspection.
2. **Dataset annotation.** Is a `urml_program` sidecar Parquet file in the episode directory acceptable, or would HF prefer the annotation as a column on the existing Parquet, or a fully separate companion dataset that references LeRobotDataset by id? The BYOP convention does not pin this.
3. **Package home.** Should URML publish `lerobot_policy_urml` from the URML organization on PyPI, from a Hugging Face Hub org under `huggingface.co/urml`, or as a community plugin on a maintainer-private PyPI? The Move #1 ledger discipline (in-repo tracking of who maintains what) needs a venue.
4. **Hub presence.** Should URML publish a Hugging Face Hub organization (`huggingface.co/urml`) hosting reference programs, manifests, and the validator artifacts, or keep distribution PyPI-only for the validator and GitHub-only for the rest?
5. **Conformance lane.** Would HF be open to a downstream URML conformance run published on the Hub model card for any policy that has been validated against URML, similar to existing eval lanes?
6. **CITATION.** URML cites this RFC and links Cadene et al., ICLR 2026 once URML adopts LeRobot integration; is there a preferred citation form?
7. **Anything else.**

## Implementation note

RFC-0040 ships as a single RFC document PR. No plugin code in this PR. The actual `reference/lerobot-bridge/` package (and its PyPI mirror `lerobot_policy_urml`) follows in a later session, gated on HF Robotics feedback. Draft state. First Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from huggingface/lerobot maintainers)

1. Wrapper vs. pure post-processor: is `URMLPolicy(PreTrainedPolicy)` the right shape, or should URML stay in a `PolicyProcessorPipeline` only?
2. Dataset annotation shape (sidecar Parquet file, column on existing Parquet, separate companion dataset, none).
3. Preferred plugin home (URML PyPI org, HF Hub org under `huggingface.co/urml`, community PyPI).
4. Conformance-lane interest on the Hub model card.
5. Preferred citation form for downstream URML papers.
6. Anything else.

## How to respond

The `huggingface/lerobot` repo does not have GitHub Discussions enabled. The maintainers' published contribution surface is GitHub Issues (with the `enhancement` label for proposals) and the Hugging Face community Discord linked from [`CONTRIBUTING.md`](https://github.com/huggingface/lerobot/blob/main/CONTRIBUTING.md).

URML's planned channel: open a single Issue on `huggingface/lerobot` labelled `enhancement`, pointing to this RFC, and cross-post a short pointer on the HF Discord. URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the first Move #2 RFC).
- [x] Motivation grounded in concrete technical alignment (LeRobot hosts most open-weights robotics policies, with a published plugin convention and 24.3k stars), plus the open-source posture fit.
- [x] Detailed design uses verified class names (`PreTrainedPolicy`, `PreTrainedConfig`), verified module paths (`lerobot.policies.pretrained`, `lerobot.configs.policies`), and matches the BYOP package layout.
- [x] At least one alternative considered (four are: ship-first, skip-BYOP, target-PI-directly, defer-until-Move-1-closes).
- [x] Drawbacks are real (proposal-only weaker artifact, LeRobot version churn, wrapper indirection, annotation invasiveness).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary.
- [x] Implementation note explicitly says no plugin code in this PR; later session contingent on feedback.
- [x] Surface ("How to respond") is verified: Discussions are disabled, Issues + Discord are documented as the contribution surface, the right Issue label is `enhancement` per the visible labels on recent issues.
- [x] Maintainer attribution verified: Remi Cadene (`@cadene`), founded LeRobot at Hugging Face March 2024, ex-Tesla.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. LLM-provider-agnostic posture preserved: LeRobot is not an LLM provider, it is a library that hosts open-weights policies from many sources. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
