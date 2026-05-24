---
rfc: 0045
title: Physical Intelligence (openpi) integration, request for comment from Physical-Intelligence/openpi maintainers
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

# RFC-0045: Physical Intelligence (openpi) integration, request for comment from Physical-Intelligence/openpi maintainers

## Summary

URML does not yet ship an openpi integration. This RFC proposes the integration shape for a future `urml-openpi-bridge` reference package that hooks into openpi's documented Inputs / Outputs extension pattern. A custom `URMLOutputs` class translates an openpi policy's action chunk into URML primitive calls before any motion reaches the substrate adapter. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the `Physical-Intelligence/openpi` maintainers.

This is a Move #2 Outreach RFC, in the precedent set by RFC-0040 (Hugging Face LeRobot). Proposal-only: no bridge code in this PR, by design.

## Motivation

openpi is the open-source release of Physical Intelligence's foundation models for robotics: π₀ (flow-based vision-language-action), π₀-FAST (autoregressive VLA), and π₀.₅ (open-world generalization). Apache 2.0, 12k+ stars at time of writing, both Issues and Discussions enabled, active maintenance. The Pi team's stated mission of "open-source models and packages for robotics" matches URML's open-core posture closely.

The integration story for URML is one sentence. An openpi policy's `policy.infer(example)["actions"]` returns a tensor of substrate-specific actions. URML's Layer-2 primitive vocabulary is the substrate-neutral abstraction one layer above that tensor. An openpi policy whose Outputs class emits URML primitives can be retargeted across ROS 2, PX4, Isaac Sim / Lab, MuJoCo, AUTOSAR Adaptive, and OPC UA Robotics by switching URML's substrate adapter, without retraining the policy.

openpi already publishes an extension pattern URML can hook into: custom `Inputs` and `Outputs` dataclasses that wrap a policy for a specific environment (e.g. `LiberoInputs` and `LiberoOutputs` in `src/openpi/policies/libero_policy.py`). URML's bridge follows that pattern, defining `URMLOutputs` as the natural extension point.

## Detailed design

URML's existing artifacts that feed into an openpi bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives a Pi policy's `URMLOutputs` would emit.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL layer above the primitives.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/), [`reference/isaac-runtime/`](../../reference/isaac-runtime/), [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): the runtimes most likely to execute a Pi-driven program.

### Proposed `urml-openpi-bridge` shape

A new `reference/openpi-bridge/` package (and a PyPI mirror `urml-openpi-bridge`), following openpi's documented Inputs / Outputs pattern verbatim. Package layout:

```
urml_openpi_bridge/
├── pyproject.toml
└── src/
    └── urml_openpi_bridge/
        ├── __init__.py
        ├── urml_outputs.py        # URMLOutputs class
        ├── urml_inputs.py         # URMLInputs class (optional, identity by default)
        └── adapters.py            # bridge to URML's substrate adapters
```

The key class:

```python
# urml_outputs.py
from dataclasses import dataclass
from openpi.policies.policy_config import PolicyOutputs  # documented base

@dataclass
class URMLOutputs(PolicyOutputs):
    """Translates a Pi policy's action chunk into URML primitive calls.

    Takes the same action tensor a downstream-environment Outputs class
    would take, batches contiguous joint-target / end-effector-pose
    chunks into `move_to`, maps gripper tokens to `grasp` / `release`,
    and emits the resulting URML program to a substrate adapter.
    """
    manifest_path: str
    substrate_brand: str = "mock"

    def __call__(self, model_output, observation):
        urml_program = self._to_urml(model_output["actions"], observation)
        return {"urml_program": urml_program, "actions": model_output["actions"]}

    def _to_urml(self, actions, observation):
        ...
```

The Outputs class preserves the raw action tensor on the return dict so existing openpi evaluation harnesses see the policy as a normal policy. URML emission lives alongside, observable but non-invasive.

### Proposed URML v0.1 to openpi mapping

| URML v0.1 primitive | openpi action realisation |
|---|---|
| `move_to` | A contiguous run of joint-target or end-effector-pose action tokens in the action chunk is collapsed into one `move_to(pose)` with a tolerance derived from `n_action_steps` and the policy's reported action horizon. |
| `grasp` / `release` | A gripper-channel transition (open to closed, or closed to open) in the action chunk maps to `grasp` / `release` with the configured gripper id. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences over `move_to` plus `grasp` / `release`. No new Protocol method. |
| `measure` | A sensor reading present in the observation dict is the read-side primitive that backs `measure`. |
| `wait_for` (event / threshold / signal) | An openpi action chunk with explicit no-op tokens surfaces as `wait_for`. |
| `report` (structured status upstream) | A labelled status token in the action chunk maps to `report`. |

### Proposed dataset annotation

openpi consumes datasets in LeRobot's `LeRobotDataset` v3 format. URML annotation discipline is identical to RFC-0040 (Hugging Face LeRobot): an optional `urml_program` sidecar Parquet file in the episode directory. Pi policies trained on URML-annotated datasets emit URML primitive sequences natively, not just raw actions.

### Proposed conformance integration

Mirror `mujoco-integration.yml` and `isaac-integration.yml` gating. A `URML_OPENPI_INTEGRATION=1` env-gated CI workflow installs `urml_openpi_bridge`, runs a Pi policy through `URMLOutputs` against a hermetic sim (the existing Libero example fixture extended with URML emission), and asserts the emitted URML primitives validate against URML's static envelope.

### Compatibility notes

- **License.** openpi is Apache-2.0. URML is Apache-2.0. No friction. (Note: openpi's `LICENSE_GEMMA.txt` covers the Gemma model weights specifically; the package itself is Apache-2.0 and that is the license the bridge inherits.)
- **PyTorch and JAX.** openpi's policies run under both backends as of Sept 2025. URML's bridge depends on neither; the translation happens at the action-tensor boundary.
- **Origin.** Physical Intelligence is incorporated in California, US. Passes the URML US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **Remote inference.** openpi documents a websocket-based remote-inference pattern. URML's bridge can sit on either side: emit URML on the policy side (server) and execute on the robot side (client), or do both in-process.
- **No ROS dependency.** openpi has no ROS coupling. URML's substrate-neutral promise holds: a Pi policy emitting URML primitives can drive a robot with zero ROS in the loop.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/openpi-bridge/`. Not built in this PR.
- Conformance suite: proposed new `openpi-integration.yml` CI workflow and a `URML_OPENPI_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The openpi side gains a custom Outputs class that follows the published extension pattern.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants Pi-team input on the `URMLOutputs` shape and the sidecar-annotation question before writing the bridge.
- **openpi evolves quickly.** The library is young, the team is small, and the API has changed across PyTorch / JAX backend rollouts. Mitigation: the bridge depends on the documented `Inputs` / `Outputs` extension pattern, not on internal model code.
- **No public plugin convention yet.** Unlike LeRobot's "Bring Your Own Policies" docs, openpi does not (yet) publish a formal third-party-package convention. The bridge has to be either upstreamed into openpi as a reference Outputs class or shipped as a standalone PyPI package that imports openpi. Both are workable. The RFC asks Pi which they prefer.

## Alternatives considered

1. **Ship the bridge first, ask Pi later.** Rejected. Pi is a small team with strong opinions about their stack. A pre-RFC saves rework.
2. **Skip Pi, target LeRobot only (LeRobot hosts Pi via `lerobot/pi05_base` etc.).** Rejected. Pi is the policy author. Going through the policy author for the foundation model is the right asymmetric move; going through LeRobot reaches the broader ecosystem ([RFC-0040](0040-hugging-face-lerobot.md)). Both are pursued, not one or the other.
3. **Pure Outputs-class extension vs. wrapper-policy pattern.** Considered both. The Outputs class is openpi's documented extension point and adds zero surface area; the wrapper-policy pattern (RFC-0040's `URMLPolicy`) is LeRobot's idiom and does not apply cleanly here because openpi's policy is a factory product, not a subclass surface.

## Prior art

- `Physical-Intelligence/openpi`: the upstream library (12k+ stars, Apache-2.0, Issues and Discussions enabled).
- `openpi.policies.policy_config.create_trained_policy(...)`: the policy factory.
- `policy.infer(example)["actions"]`: the action-producing method.
- `src/openpi/policies/libero_policy.py` (`LiberoInputs`, `LiberoOutputs`): the documented Inputs / Outputs extension pattern.
- [RFC-0040](0040-hugging-face-lerobot.md): the parallel Move #2 RFC for LeRobot. The two are complementary because LeRobot hosts Pi models alongside other VLAs.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference, the conceptual sibling.

## Unresolved questions

Provisional pending Pi-team feedback:

1. **Extension shape.** Is a custom `URMLOutputs` (following the `LiberoOutputs` pattern) the right hook, or would Pi prefer the bridge to live as a wrapper around `policy_config.create_trained_policy(...)` that intercepts the `infer(...)` return value?
2. **Package home.** Upstream into `Physical-Intelligence/openpi` as a reference `URMLOutputs` (URML-side maintained PR), or a standalone third-party PyPI package (`urml-openpi-bridge`) that imports openpi? The LeRobot precedent ([RFC-0040](0040-hugging-face-lerobot.md)) raised the same question.
3. **Action-chunk semantics.** The proposed `move_to` collapsing rule assumes joint-target or end-effector-pose tokens are contiguous within an action chunk. Is that a safe assumption across π₀, π₀-FAST, and π₀.₅, or do their action token formats differ enough to require per-model heuristics?
4. **Remote-inference pattern.** Should `URMLOutputs` run on the policy side of the websocket (Pi's server) or the robot side (the client)? Both are technically possible; the latency vs. validation trade-off is different.
5. **Dataset annotation.** openpi consumes LeRobot v3 datasets. Is a separate URML annotator (RFC-0040's pattern) the right approach, or does Pi want a different annotation layer specific to their fine-tuning pipeline?
6. **Anything else.**

## Implementation note

RFC-0045 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/openpi-bridge/` package follows in a later session, gated on Pi-team feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from Physical-Intelligence/openpi maintainers)

1. Extension shape: `URMLOutputs` (Outputs-class hook) vs. wrapper around the policy factory.
2. Package home: upstream into openpi vs. standalone `urml-openpi-bridge` on PyPI.
3. Action-chunk semantics across π₀, π₀-FAST, π₀.₅.
4. Remote-inference placement (server-side vs. client-side URML emission).
5. Dataset annotation approach.
6. Anything else.

## How to respond

`Physical-Intelligence/openpi` has both GitHub Discussions and GitHub Issues enabled. URML's planned channel: open a Discussion in the openpi repo (Show & Tell or Ideas category, depending on what is available) pointing to this RFC, with a short cross-reference Issue in case the Discussion gets less visibility.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts about openpi (verified against the repo on 2026-05-23: 12k+ stars, Apache-2.0, Issues and Discussions both enabled, `policy.infer(example)["actions"]` API, `LiberoInputs`/`LiberoOutputs` extension pattern).
- [x] Detailed design proposes a concrete `URMLOutputs` class following openpi's documented Inputs / Outputs pattern.
- [x] At least three alternatives considered.
- [x] Drawbacks are real (proposal-only weaker artifact, library churn, no formal plugin convention).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. Mapping uses existing vocabulary.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Discussions enabled (unlike LeRobot), Issues enabled, CONTRIBUTING.md present.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
