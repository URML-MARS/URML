---
rfc: 0054
title: Toyota Research Institute Large Behavior Models integration, request for comment from TRI-ML maintainers
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

# RFC-0054: Toyota Research Institute Large Behavior Models integration, request for comment from TRI-ML maintainers

## Summary

URML does not yet ship a Toyota Research Institute (TRI) integration. This RFC proposes the integration shape for a future `urml-tri-lbm-bridge` reference package that hooks into TRI-ML's `vla_foundry` framework. Two integration vectors: (a) a Large Behavior Model (LBM) inference wrapper that emits URML primitives instead of raw actions, and (b) URML-annotated training data accepted by `vla_foundry`'s `DataParams` so LBMs trained under URML annotation emit URML natively. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the `TRI-ML/vla_foundry` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR.

## Motivation

TRI's robotics work is one of the more sustained open-research programs in the field. The `TRI-ML` GitHub organization has 41+ repositories, with `vla_foundry` (383 stars, MIT) as the current home of TRI's Vision-Language-Action training framework and the documented surface for the Large Behavior Model line of work. Adjacent repos: `vidar` (643 stars; vision and perception), `chiral` (WebSocket interface for robot policy evaluation), `raiden` (toolkit for YAM robots, calibration, coordinated bimanual data collection), `dgp` (Dataset Governance Policy, MIT). Most repos updated February through April 2026.

Three things make TRI an unusually clean Move #2 target.

TRI's Large Behavior Models program is the named flagship. TRI has publicly framed LBMs as "the LLMs of robotics," reporting 60+ dexterous manipulation skills mastered through haptic-feedback training. The published architecture builds on Diffusion Policy (TRI plus Columbia plus MIT, RSS 2023, `real-stanford/diffusion_policy`, 4.2k+ stars, MIT). `vla_foundry` is the in-house framework where LBM training and deployment live.

TRI ships open. MIT-licensed code is the default. `vla_foundry` exposes a documented model-registration pattern (`@register_model_params()` decorator), nested `dataclasses` via `draccus`, separable `ModelParams` / `DataParams` / `HyperParams` blocks, and inference scripts under `vla_foundry/inference/scripts/`. The extension pattern is explicit; URML's bridge plugs in without surgical changes to internals.

TRI has a humanoid-deployment path via the Boston Dynamics partnership. The October 2024 partnership pairs TRI's LBMs with Boston Dynamics' Atlas humanoid. URML already ships `SpotAdapter` and the `spot_quadruped` manifest (RFC-0043). A URML-emitting LBM that trains on `vla_foundry` and deploys on Atlas through the TRI plus BD partnership closes a loop URML already has half-built.

## Detailed design

URML's existing artifacts that feed into a TRI bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives the bridge emits and the dataset annotation pass produces.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL layer above the primitives.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference, the natural baseline for the dataset-annotation pass.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/), [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/): the runtimes most likely to host LBM-driven policies on hardware (research arms, bimanual setups, Atlas via the TRI plus BD partnership).

### Proposed `urml-tri-lbm-bridge` shape

A new `reference/tri-lbm-bridge/` package, structured as a `vla_foundry` plugin that registers new model parameters and a data-modality block following TRI-ML's documented extension pattern.

```
urml_tri_lbm_bridge/
├── pyproject.toml
└── src/
    └── urml_tri_lbm_bridge/
        ├── __init__.py
        ├── urml_model_params.py    # @register_model_params() for URML emission head
        ├── urml_data_params.py     # DataParams subclass for URML-annotated trajectories
        ├── inference_wrapper.py    # vla_foundry/inference adapter to URML primitive emission
        └── annotation.py           # URML annotation pass over LBM training data
```

### Vector A: LBM inference emitting URML primitives

A post-inference adapter wraps the `vla_foundry/inference/scripts/` deployment path so the LBM's action chunk is translated into URML primitive calls before any motor command reaches the substrate. The translation happens at the inference boundary, not inside the model; the LBM stays a normal `vla_foundry` model that the framework's existing tooling can train, evaluate, and serve.

```python
# inference_wrapper.py
from vla_foundry.inference import load_lbm_checkpoint  # documented inference path

class URMLEmittingLBMWrapper:
    """Wraps a vla_foundry LBM inference handle and emits URML primitives."""

    def __init__(self, checkpoint_path, manifest_path):
        self._inner = load_lbm_checkpoint(checkpoint_path)
        self._emitter = _make_emitter(manifest_path)

    def act(self, observation):
        action_chunk = self._inner.predict(observation)
        primitives = self._emitter(action_chunk, observation)
        return action_chunk, {"urml_program": primitives}
```

The pattern matches the wrapper precedents in [RFC-0040](0040-hugging-face-lerobot.md) (LeRobot), [RFC-0045](0045-physical-intelligence-openpi.md) (openpi), and [RFC-0047](0047-allen-institute-molmoact.md) (MolmoAct). URML emission rides alongside the raw action; TRI's evaluation harness sees a normal handle.

### Vector B: URML-annotated training via vla_foundry's DataParams

A custom `DataParams` subclass for URML-annotated trajectories. The block accepts datasets that include the `urml_program` sidecar shape proposed in [RFC-0046](0046-open-x-embodiment.md) (Open X-Embodiment) and [RFC-0047](0047-allen-institute-molmoact.md) (Ai2 two-armed tabletop dataset). Training under this DataParams produces an LBM that emits URML primitives natively as part of its action output, eliminating the need for the Vector A inference-time translation step on URML-annotated trajectories.

```python
# urml_data_params.py
from vla_foundry.config import DataParams
from draccus import register_subclass

@register_subclass(DataParams, name="urml_annotated")
class URMLAnnotatedDataParams(DataParams):
    """DataParams for trajectories carrying URML primitive sequences."""

    urml_sidecar_path: str
    manifest_path: str
    # ... draccus-style fields aligned with existing DataParams patterns
```

### Proposed URML v0.1 to LBM mapping

| URML v0.1 primitive | LBM action realisation |
|---|---|
| `move_to` | A contiguous run of end-effector-pose or joint-target tokens in the LBM's diffusion-policy action chunk. |
| `grasp` / `release` | A gripper-channel transition in the action chunk. LBM's bimanual training (YAM robots, Atlas) needs the gripper id (left vs. right). |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences. No new Protocol method. |
| `measure` | A sensor reading present in the LBM's observation input is the read-side primitive that backs `measure`. |
| `wait_for` (event / threshold / signal) | A condition-gated pause inside the LBM's action chunk (action-masked timesteps) surfaces as `wait_for`. |
| `report` (structured status upstream) | A labelled status token in the LBM's output maps to `report`. |

### Proposed conformance integration

Mirror `mujoco-integration.yml` and `isaac-integration.yml`. A `URML_TRI_LBM_INTEGRATION=1` env-gated CI workflow installs `urml_tri_lbm_bridge`, runs a `vla_foundry` LBM inference through `URMLEmittingLBMWrapper` against a hermetic sim, and asserts the emitted URML primitives validate against URML's static envelope.

### Compatibility notes

- **License.** `vla_foundry` MIT, `dgp` MIT, Diffusion Policy MIT, `vidar` not surfaced in the WebFetch but TRI-ML's pattern is consistently MIT. URML is Apache-2.0. MIT and Apache-2.0 are compatible; the bridge ships Apache-2.0 by default.
- **Plugin convention.** `vla_foundry` documents `@register_model_params()` and the draccus-based config registration. The bridge follows that convention exactly.
- **Origin.** Toyota Research Institute is incorporated in Los Altos, CA, US, as a subsidiary of Toyota Motor North America. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **Boston Dynamics partnership.** TRI plus BD announced October 2024; LBM development targets Atlas. URML already ships `SpotAdapter` (RFC-0043, BD quadruped). A future humanoid-runtime extension for Atlas would let a URML-emitting LBM deploy through the TRI plus BD pipeline.
- **Drake.** TRI's `Drake` model-based toolkit (at `RobotLocomotion/drake`) is adjacent but out of scope for this RFC. Drake's role is simulation and analytical modeling; integration would be a separate RFC if there is appetite.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/tri-lbm-bridge/`. Not built in this PR.
- Conformance suite: proposed new `tri-lbm-integration.yml` workflow gated by `URML_TRI_LBM_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The TRI side gains a `vla_foundry` plugin registered through the documented extension pattern; no changes inside TRI-ML repos are required.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants TRI-ML input on the inference-wrapper shape and on the `DataParams` block convention before writing code, especially because LBM training is expensive enough that the DataParams contract should be solid before anyone trains a URML-annotated LBM at scale.
- **vla_foundry is recent.** The repo carries 383 stars and active development under TRI-ML; the API surface is stable but younger than LeRobot or openpi. The bridge depends on the documented `@register_model_params()` and DataParams pattern, not internal code paths, but the convention itself may evolve.
- **Diffusion Policy is multi-author.** Diffusion Policy is published jointly by Columbia, TRI, and MIT (Chi, Feng, Du, Xu, Cousineau, Burchfiel, Song). This RFC scopes outreach to TRI specifically (the LBM line of work). A separate Diffusion-Policy-as-such RFC routed to Columbia and MIT is a possible future Move #2 entry; this one stays focused.
- **Atlas deployment path is not yet open.** The TRI plus BD partnership targets Atlas with LBMs, but the Atlas SDK and the resulting deployment surface are not currently part of the public stack. URML's bridge can ship the training and inference vectors today; the Atlas-on-LBM deployment becomes available when BD opens that surface, not before.

## Alternatives considered

1. **Ship the bridge first, ask TRI later.** Rejected. TRI's open-research posture is collaborative; pre-RFC saves rework, especially on the DataParams convention.
2. **Combine TRI and Diffusion Policy into one RFC.** Rejected. Diffusion Policy is a Columbia plus MIT plus TRI artifact; lumping it as a TRI RFC mis-attributes the work and limits the audience.
3. **Combine TRI and Drake into one RFC.** Rejected. Drake is a model-based simulation and analysis toolkit; URML's integration story there is fundamentally different (Drake is a substrate-like backend, similar to MuJoCo or Gazebo).
4. **Route via Boston Dynamics rather than TRI for the LBM-on-Atlas angle.** Rejected. The training and inference framework lives at TRI; BD is the deployment hardware target. Going to TRI first is the correct routing for the bridge work.
5. **Skip vla_foundry, target chiral (WebSocket policy evaluation) directly.** Rejected. chiral is a single-purpose evaluation interface; the LBM training and the wider VLA workflow live in vla_foundry. URML's bridge needs the model and data abstractions vla_foundry offers.

## Prior art

- `TRI-ML/vla_foundry`: the upstream framework (383 stars, MIT, Issues enabled, Discussions not visible, draccus-based config, `@register_model_params()` decorator pattern, inference scripts under `vla_foundry/inference/scripts/`, vla_foundry citation authors Mercat, Keh, Arora, Huang, Shah, Nishimura, Iwase, Liu).
- `TRI-ML/vidar`, `TRI-ML/chiral`, `TRI-ML/raiden`, `TRI-ML/dgp`: adjacent TRI-ML repos in the same organization, useful context for the org's open posture.
- `real-stanford/diffusion_policy`: the Diffusion Policy paper repo (4.2k+ stars, MIT, RSS 2023, joint Columbia plus TRI plus MIT work; authors Chi, Feng, Du, Xu, Cousineau, Burchfiel, Song).
- TRI press materials on Large Behavior Models (October 2024 announcement, 60+ skills, haptic feedback).
- TRI plus Boston Dynamics partnership announcement (October 2024, LBM-on-Atlas).
- `RobotLocomotion/drake`: TRI's model-based robotics toolkit. Out of scope for this RFC but adjacent.
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0045](0045-physical-intelligence-openpi.md), [RFC-0047](0047-allen-institute-molmoact.md), [RFC-0050](0050-nvidia-isaac-lab-integration.md), [RFC-0052](0052-meta-fair-vjepa2.md): the other Move #2 policy and bridge RFCs.
- [RFC-0043](0043-boston-dynamics-spot-integration.md): URML's BD Spot work; future Atlas extension is the deployment-side complement to this RFC.
- [RFC-0046](0046-open-x-embodiment.md): the OXE annotation shape the URML DataParams block aligns with.

## Unresolved questions

Provisional pending TRI-ML maintainer feedback:

1. **DataParams contract.** Is the `urml_annotated` DataParams subclass a clean fit for `vla_foundry`'s draccus-based config registration, or would TRI prefer a different mechanism for opting trajectories into URML annotation?
2. **Inference wrapper home.** Should `URMLEmittingLBMWrapper` live URML-side (`reference/tri-lbm-bridge/` plus the PyPI mirror) or upstream as a contributed example in `TRI-ML/vla_foundry/inference/`?
3. **Action-chunk semantics across LBM versions.** TRI has indicated rapid LBM iteration. How tightly should the bridge couple to the current LBM action-chunk format, and what is the recommended way to handle version migrations?
4. **Atlas deployment path.** Is the TRI plus BD partnership in a state where a URML-emitting LBM on Atlas is a meaningful planning target for the bridge, or should the RFC stay scoped to training and inference only?
5. **chiral integration.** Should `URMLEmittingLBMWrapper` expose its primitive emission through TRI's `chiral` WebSocket evaluation interface, so URML-validated LBM policies can be evaluated through TRI's published evaluation pipeline?
6. **Annotation provenance.** TRI's data governance work (`TRI-ML/dgp`) is mature. How should the URML annotation pass document its provenance under DGP's conventions?
7. **Anything else.**

## Implementation note

RFC-0054 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/tri-lbm-bridge/` package follows in a later session, gated on TRI-ML maintainer feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from TRI-ML maintainers)

1. URML-annotated DataParams contract under draccus.
2. Inference wrapper home (URML-side standalone vs. upstreamed example).
3. LBM-version coupling and migration strategy.
4. Atlas deployment-path scoping.
5. chiral integration for evaluation.
6. Annotation provenance under DGP.
7. Anything else.

## How to respond

`TRI-ML/vla_foundry` has Issues enabled. Discussions are not visible. URML's planned channel: file an Issue on `TRI-ML/vla_foundry` referencing this RFC, scoped to the DataParams contract (Q1) and the inference wrapper home (Q2) so the maintainers see the questions most directly relevant to them. Optional parallel courtesy emails to the corresponding-author addresses on the LBM and Diffusion Policy publications (Cousineau, Burchfiel, and the vla_foundry citation authors).

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts about TRI-ML (verified against the repos on 2026-05-23: TRI-ML/vla_foundry 383 stars MIT Issues enabled, TRI-ML org has 41+ repos with consistent MIT pattern, real-stanford/diffusion_policy 4.2k+ stars MIT 90 open issues, draccus-based config registration with @register_model_params decorator, inference scripts under vla_foundry/inference/scripts/, vla_foundry citation authors Mercat / Keh / Arora / Huang / Shah / Nishimura / Iwase / Liu, Diffusion Policy authors Chi / Feng / Du / Xu / Cousineau / Burchfiel / Song). TRI plus BD partnership October 2024 verified from press materials.
- [x] Detailed design proposes a concrete two-vector package following vla_foundry's documented `@register_model_params()` plus DataParams extension pattern.
- [x] Five alternatives considered.
- [x] Drawbacks are real (proposal-only, recent framework, multi-author Diffusion Policy attribution care, Atlas surface not yet open).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: vla_foundry Issues enabled, Discussions not visible, MIT license, registration decorator pattern documented.
- [x] Cross-references to other Move #2 RFCs intact (0040, 0043, 0045, 0046, 0047, 0050, 0052).
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant. Provider neutrality preserved.
