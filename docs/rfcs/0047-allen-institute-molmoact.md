---
rfc: 0047
title: Allen Institute MolmoAct integration, request for comment from Ai2 Embodied AI initiative
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

# RFC-0047: Allen Institute MolmoAct integration, request for comment from Ai2 Embodied AI initiative

## Summary

URML does not yet ship a MolmoAct integration. This RFC proposes the integration shape for a future `urml-molmoact-bridge` reference package that wraps MolmoAct's action output and translates it into URML primitive calls, and proposes URML annotation for Ai2's newly released open-source two-armed tabletop manipulation dataset. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the Ai2 Embodied AI initiative and the `allenai/molmoact` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code or dataset annotation in this PR.

## Motivation

The Allen Institute for AI (Ai2) is a US-domiciled open-science nonprofit. MolmoAct is Ai2's open-source Action Reasoning Model that converts 2D images to 3D visualizations, previews motions before acting, and supports human in-the-loop correction. Apache 2.0, Issues enabled, repo at `allenai/molmoact`. Ai2 released MolmoAct 2 in May 2026 along with what Ai2 describes as the largest open-source dataset for two-armed tabletop robot manipulation.

The Ai2 Embodied AI initiative is led by Dieter Fox (since March 2026; formerly a longtime professor at the University of Washington, with prior leadership at NVIDIA Research). The initiative's open-science posture matches URML's open-core posture closely: Ai2 is an unusual venue for AI research in that openness is its mission, not a competitive concession.

The integration story for URML is one sentence. MolmoAct's action output is, like every VLA's, embodiment-specific by default. URML's Layer-2 primitive vocabulary is the substrate-neutral abstraction one layer above it. A MolmoAct policy whose post-processor emits URML can be retargeted across ROS 2, PX4, Isaac Sim / Lab, MuJoCo, AUTOSAR Adaptive, and OPC UA Robotics by switching URML's substrate adapter, without retraining.

The annotation story matches RFC-0046 (Open X-Embodiment): the newly released Ai2 two-armed tabletop dataset would benefit from optional URML primitive sequences alongside the raw action tensors, making it a substrate-aware training corpus from day one rather than retrofitting later.

## Detailed design

URML's existing artifacts that feed into a MolmoAct bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL layer. MolmoAct's natural-language conditioning maps naturally onto URML's NL surface.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime most likely to host MolmoAct-trained policies on hardware (research arms, bimanual tabletop setups).

### Proposed `urml-molmoact-bridge` shape

A new `reference/molmoact-bridge/` package, structured as a thin adapter that imports `olmo.hf_model.molmoact` (MolmoAct's HuggingFace model conversion module per the upstream layout) and wraps the action-producing call.

```
urml_molmoact_bridge/
├── pyproject.toml
└── src/
    └── urml_molmoact_bridge/
        ├── __init__.py
        ├── wrapper.py             # MolmoActURMLWrapper class
        ├── post_processor.py      # action-tensor to URML primitive translation
        └── adapters.py            # bridge to URML's substrate adapters
```

The wrapper composes MolmoAct's model, lets it do inference, and inserts a URML translation step between the action tensor and the substrate adapter. The model itself stays untouched; URML emission is observable but non-invasive.

### Proposed URML v0.1 to MolmoAct mapping

| URML v0.1 primitive | MolmoAct action realisation |
|---|---|
| `move_to` | A contiguous run of end-effector-pose or joint-target actions is collapsed into one `move_to(pose)` with a tolerance derived from MolmoAct's reported reasoning steps. |
| `grasp` / `release` | A gripper-channel transition in the action output maps to `grasp` / `release` with the configured gripper id. MolmoAct's bimanual setup needs the gripper id to disambiguate left vs. right. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences. No new Protocol method. |
| `measure` | A sensor reading present in the policy's observation is the read-side primitive that backs `measure`. |
| `wait_for` (event / threshold / signal) | MolmoAct's human-in-the-loop pause surfaces as `wait_for(human_signal)`. The model's "preview before acting" capability fits this primitive especially well. |
| `report` (structured status upstream) | A status token in the model's output maps to `report`. |

MolmoAct's published differentiator is "reason in 3D, preview before acting, allow human correction." URML's `wait_for` and `report` primitives are the natural surface for that preview-and-correct loop: URML programs that emit a `report(preview)` plus a `wait_for(human_signal)` before executing each segment can carry MolmoAct's correction loop through any substrate without per-robot bespoke UI.

### Proposed two-armed dataset annotation

Ai2's newly released open-source two-armed tabletop manipulation dataset is the largest of its kind. Annotation follows the same shape as RFC-0046 (OXE): an optional `urml_program` sidecar field per episode, indexed by `start_step` and `end_step`. Bimanual coordination becomes explicit at the URML level: a `move_to` on gripper id 0 paired with a `wait_for(other_arm_ready)` on gripper id 1.

### Proposed conformance integration

Mirror `mujoco-integration.yml` and `isaac-integration.yml` gating. A `URML_MOLMOACT_INTEGRATION=1` env-gated CI workflow runs a MolmoAct model through `MolmoActURMLWrapper` against a hermetic sim and asserts the emitted URML primitives validate.

### Compatibility notes

- **License.** MolmoAct is Apache 2.0. URML is Apache 2.0. Ai2 is a US 501(c)(3) nonprofit; its open-science mission aligns with URML's open-core commitment.
- **Origin.** Allen Institute for AI is incorporated in Seattle, WA, US. Passes the URML US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging. Combined with Dieter Fox's leadership (a longtime US academic), the institutional alignment is clean.
- **PyTorch and HuggingFace.** MolmoAct uses the HuggingFace transformers stack (`olmo/hf_model/molmoact/`). URML's bridge depends on the publicly documented HuggingFace inference API, not on MolmoAct internals.
- **No ROS dependency.** Like openpi and LeRobot, MolmoAct has no ROS coupling. URML's substrate-neutral promise holds.
- **Preview-and-correct UX.** MolmoAct's "preview before acting" is the model's signature feature. URML's `wait_for` and `report` primitives carry this loop across substrates. Conversely, naive URML emission that strips the preview step would lose MolmoAct's value; the bridge must preserve it.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/molmoact-bridge/`. Not built in this PR.
- Conformance suite: proposed new `molmoact-integration.yml` CI workflow and a `URML_MOLMOACT_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. MolmoAct is unaffected: the bridge is a thin downstream wrapper.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants Ai2 input on the wrapper shape and especially on the preview-and-correct loop semantics before writing code.
- **MolmoAct 2 is recent.** Released May 2026. The model and dataset APIs are likely to change as the team iterates. Mitigation: depend on the published HuggingFace inference surface, not internals.
- **No formal plugin convention.** MolmoAct does not document a third-party-package contract. The bridge would either land as a contributed example in `allenai/molmoact` (Ai2-side maintained) or as a standalone PyPI package (URML-side maintained).
- **Bimanual coordination is harder.** Mapping two simultaneous action streams onto two URML primitive sequences with explicit synchronization points is more work than single-arm mapping. The RFC names this as an open question rather than presuming a solution.

## Alternatives considered

1. **Ship the bridge first, ask Ai2 later.** Rejected. Ai2's open-science posture means a pre-RFC is likely to land well; bypassing it is unforced rudeness.
2. **Skip MolmoAct, target LeRobot (LeRobot will eventually host MolmoAct alongside other VLAs).** Rejected. Going to the model author for the foundation model is the right asymmetric move ([RFC-0040](0040-hugging-face-lerobot.md) covers the ecosystem channel); going only through LeRobot would skip the dataset-annotation opportunity and the conversation with Dieter Fox's initiative.
3. **Combine with RFC-0046 (OXE) into a single Ai2-and-Google-DeepMind RFC.** Rejected. OXE and Ai2 are different organizations with different governance. One combined RFC would muddle both feedback asks.

## Prior art

- `allenai/molmoact`: the upstream repo (Apache 2.0, Issues enabled).
- The MolmoAct paper and the MolmoAct 2 blog post on `allenai.org/blog/molmoact2`.
- Ai2's Embodied AI initiative page at `allenai.org/embodied-ai`.
- Dieter Fox's prior leadership at NVIDIA Research and the University of Washington as the institutional bridge.
- [RFC-0040](0040-hugging-face-lerobot.md): URML's LeRobot bridge (the policy-wrapper precedent).
- [RFC-0045](0045-physical-intelligence-openpi.md): URML's openpi bridge (the Inputs / Outputs extension precedent).
- [RFC-0046](0046-open-x-embodiment.md): URML's OXE annotation (the dataset-annotation precedent).
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's NL-to-URML reference.

## Unresolved questions

Provisional pending Ai2 Embodied AI initiative feedback:

1. **Wrapper home.** Should `urml-molmoact-bridge` live as a contributed example in `allenai/molmoact` (Ai2-side maintained) or as a standalone third-party PyPI package (URML-side maintained)?
2. **Preview-and-correct semantics.** Is the `wait_for(human_signal)` + `report(preview)` pattern the right URML expression for MolmoAct's preview-before-acting capability, or does Ai2 see a cleaner mapping?
3. **Bimanual coordination.** How should URML primitive sequences express explicit synchronization between two arms (gripper id 0 and gripper id 1)? URML's current vocabulary is single-arm-oriented and may need a Layer-3 extension specific to bimanual.
4. **Dataset annotation.** Is the `urml_program` sidecar field (indexed by `start_step` / `end_step`) acceptable for the new two-armed tabletop dataset, or would Ai2 prefer a separate annotation companion?
5. **Conformance lane.** Would Ai2 publish a URML conformance run on each MolmoAct release's model card, similar to the eval lanes the model card already supports?
6. **Cross-listing with OXE.** RFC-0046 proposes URML annotation on OXE. Should Ai2's dataset be included in that pass, or kept separate to preserve the dataset's standalone identity?
7. **Anything else.**

## Implementation note

RFC-0047 ships as a single RFC document PR. No bridge code and no dataset annotation in this PR. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from Ai2 Embodied AI initiative and `allenai/molmoact` maintainers)

1. Wrapper home (Ai2-side contributed example vs. standalone PyPI package).
2. Preview-and-correct semantics in URML.
3. Bimanual coordination expression.
4. Dataset annotation shape.
5. Conformance-lane interest on the model card.
6. Cross-listing with the OXE annotation pass (RFC-0046).
7. Anything else.

## How to respond

`allenai/molmoact` has Issues enabled. Discussions are not enabled. URML's planned channel: file an Issue on the repo pointing to this RFC, and send a parallel courtesy email to the authors named in the repository (haoquanf@allenai.org, jasonl@allenai.org, jiafeid@allenai.org). Dieter Fox's role leading the broader Embodied AI initiative is recent (since March 2026); a Cc to his Ai2 address (publicly listed on `allenai.org/embodied-ai`) would be appropriate if the courtesy email expands beyond the MolmoAct authors.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts about Ai2 / MolmoAct (verified against the repo on 2026-05-23: Apache 2.0, Issues enabled, Discussions disabled, `olmo/hf_model/molmoact/` module path, author emails haoquanf/jasonl/jiafeid@allenai.org). MolmoAct 2 release date and Dieter Fox leadership verified from Ai2's published blog and press coverage (May 2026 release; Fox leads since March 2026).
- [x] Detailed design names a concrete wrapper shape and a mapping table.
- [x] Three alternatives considered.
- [x] Drawbacks are real (proposal-only weaker artifact, recent v2 release, no plugin convention, bimanual coordination complexity).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added (mapping uses existing vocabulary; bimanual coordination is flagged as an open question, not a presumed addition).
- [x] Implementation note explicitly says no bridge code or dataset annotation in this PR.
- [x] Surface verified: Issues enabled, Discussions disabled, author emails published in the repo, Dieter Fox role confirmed via published Ai2 communications.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
