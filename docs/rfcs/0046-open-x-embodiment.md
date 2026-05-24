---
rfc: 0046
title: Open X-Embodiment integration, request for comment from OXE governance
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

# RFC-0046: Open X-Embodiment integration, request for comment from OXE governance

## Summary

URML proposes a substrate-neutral action-vocabulary annotation layer for the Open X-Embodiment (OXE) dataset, complementing the existing per-embodiment action tensors with optional URML primitive sequences. Models trained on URML-annotated OXE episodes can emit URML directly, making cross-embodiment policy transfer not only embodiment-aware but substrate-aware. No spec change on URML's side. This RFC documents the proposed annotation shape and requests review and feedback from the OXE governance and the `google-deepmind/open_x_embodiment` maintainers.

Move #2 Outreach RFC. Proposal-only: no annotation tooling or dataset upload in this PR.

This RFC also serves as URML's primary public touch with Google DeepMind. The Gemini Robotics SDK is currently waitlist-gated and does not expose a public Issue surface for community proposals; OXE is the open collaborative surface DeepMind already maintains, and a Pi-style alignment here flows upstream into the Gemini Robotics ecosystem through the trusted-tester partner network.

## Motivation

OXE is the canonical large-scale cross-embodiment robotic-learning dataset. The official landing page (`robotics-transformer-x.github.io`) describes a multi-institutional effort: 21 institutions, 34 robotic research labs, 60 aggregated datasets, 527 distinct manipulation skills, over 1 million trajectories spanning 22 robot platforms. RT-X models trained on OXE generalize across embodiments precisely because the dataset spans embodiments.

The integration story for URML is one sentence. OXE's per-trajectory action tensors are still embodiment-specific: a Franka joint-target tensor is not a UR joint-target tensor is not a quadruped wrench command. URML's Layer-2 primitive vocabulary is what those tensors agree on at the intent level. An OXE episode that carries an optional URML primitive sequence alongside its raw actions becomes substrate-neutral training data: a model can learn to emit URML and let URML's substrate adapter handle the per-embodiment translation.

This is complementary to OXE's existing cross-embodiment training paradigm. Embodiment-conditioning still happens at the model side; URML adds an additional invariant signal at the dataset side.

## Detailed design

URML's existing artifacts that feed into an OXE annotation effort:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives an OXE annotator would emit per trajectory.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): the Hardware Abstraction Layer that maps OXE's per-platform action shapes onto URML's substrate-neutral abstractions.
- [`reference/validator/`](../../reference/validator/): the validator that would accept URML-annotated trajectories.

### Proposed annotation shape

For each OXE trajectory, an optional `urml_program` field:

```
trajectory:
  observation: <unchanged>
  action: <unchanged, embodiment-specific tensor>
  ...
  urml_program:
    - primitive: move_to
      pose: {x: ..., y: ..., z: ..., qx: ..., qy: ..., qz: ..., qw: ...}
      tolerance: 0.05
      start_step: 0
      end_step: 47
    - primitive: grasp
      gripper_id: 0
      start_step: 47
      end_step: 52
    - primitive: move_to
      pose: {...}
      start_step: 52
      end_step: 119
    - primitive: release
      gripper_id: 0
      start_step: 119
      end_step: 124
```

`start_step` and `end_step` are indices into the trajectory's action timeline, so URML annotations align with the raw action tensor without requiring resampling. The format is additive: episodes without the field continue to work unchanged.

### Proposed annotation source

Annotation is the harder problem than schema. Three paths:

1. **Programmatic from action structure.** The annotator inspects each trajectory's action tensor and infers URML primitive boundaries from joint-rest patterns, gripper-state transitions, and end-effector velocity profiles. Cheap, deterministic, lossy.
2. **Programmatic from natural-language captions.** Many OXE datasets carry natural-language task descriptions per episode. URML's existing LLM bridge ([`reference/llm-bridge/`](../../reference/llm-bridge/)) translates English to URML; running the bridge over OXE captions plus action tensors emits URML programs grounded in both.
3. **Human-in-the-loop verification on a subset.** A sampled subset gets human annotation. The programmatic annotators are evaluated against the human labels. Public quality metrics are reported.

URML's preference, subject to OXE governance feedback: ship (1) as a baseline annotator, demonstrate (2) on a small subset using existing LLM bridges (Anthropic, OpenAI, open-weights), reserve (3) for a future evaluation pass once the value is clear.

### Compatibility notes

- **Repository.** `google-deepmind/open_x_embodiment`. Note the disclaimer on the repo: "not an official Google product." Outreach addresses the OXE community, not a Google product team.
- **License and access.** The dataset itself is open per the original paper. Specific dataset components carry their contributing labs' licenses. URML annotations would be released under the same license as the underlying trajectory (per-dataset).
- **Origin.** OXE is a multi-institutional consortium with 21 institutions. URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) applies per dataset, depending on the contributing lab's origin. The annotation layer itself adds no new origin coupling.
- **OXE-AugE precedent.** A recent paper (arxiv 2512.13100, "OXE-AugE: A Large-Scale Robot Augmentation of OXE") shows the OXE ecosystem already accepts augmentation layers. URML's annotation is a different augmentation but the precedent that the dataset is amenable to layered enrichment is useful.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: a new optional URML-annotated-trajectory schema (`spec/layer-1-hal/oxe-annotation.md`) would be drafted as a future spec RFC if this RFC accepts, defining the `urml_program` field. Not included in this PR.
- Reference annotator: proposed new package `tools/oxe-annotator/`. Not built in this PR.
- Conformance: optional gated CI workflow that re-validates a sampled URML-annotated OXE episode against URML's static envelope.

## Backward compatibility

Pre-v1.0. Purely additive: episodes without `urml_program` continue to work unchanged. Existing OXE-trained models are not affected.

## Drawbacks

- **Annotation is the hard part.** URML's primitive vocabulary is small (20 primitives) but mapping a 100-step trajectory to a sequence of primitives requires either heuristic boundaries (lossy) or LLM judgment (slow and non-deterministic) or human labelling (expensive). The RFC is honest about this.
- **Quality variance across the 60 contributing datasets.** Some datasets have rich language captions, some have only action tensors. The annotation quality URML can achieve varies accordingly.
- **OXE governance is distributed.** 600+ named authors, 21 institutions, no designated coordinator on the landing page. Reaching consensus on adoption is slower than working with a single library maintainer.
- **No formal plugin convention.** Unlike LeRobot (BYOP) or openpi (Inputs / Outputs), OXE does not publish a third-party extension contract. The annotation would either land upstream into the OXE repo (the disclaimer "not an official Google product" makes this less than a Google decision) or live in a sibling repo that points back.

## Alternatives considered

1. **Annotate at the model side only (target VLA outputs), skip OXE.** Rejected. The dataset-side annotation makes the model-side emission trainable; without it, every model that wants URML emission has to re-derive the alignment.
2. **Push for URML adoption as the primary OXE action vocabulary.** Rejected. Replacing the per-embodiment action tensors would be a breaking change to every OXE consumer. The additive sidecar respects the existing contract.
3. **Build a separate URML-annotated dataset from scratch on a few platforms.** Rejected. OXE's 1M+ trajectories are the asset; rebuilding the corpus is wasteful when annotation is cheaper.

## Prior art

- `google-deepmind/open_x_embodiment`: the project repo (Apache 2.0 codebase; per-dataset licenses on the data).
- `robotics-transformer-x.github.io`: the official landing page (governance, contact, dataset enrollment).
- The original OXE paper: arxiv 2310.08864.
- OXE-AugE (arxiv 2512.13100): existing augmentation-layer precedent.
- [RFC-0040](0040-hugging-face-lerobot.md): URML's LeRobot annotation discipline (sidecar Parquet field).
- [RFC-0045](0045-physical-intelligence-openpi.md): URML's openpi integration (action-tensor translation at the model side).
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's NL-to-URML reference, the natural baseline annotator for option (2).

## Unresolved questions

Provisional pending OXE governance feedback:

1. **Schema acceptability.** Is the `urml_program` sidecar field (indexed by `start_step` / `end_step`) acceptable as an optional addition to the OXE trajectory schema, or would governance prefer a separate annotation dataset that joins back to OXE by trajectory id?
2. **Annotation quality bar.** What level of programmatic-annotation quality (precision / recall against a human-labelled subset) would the OXE community accept as a baseline before merging URML annotations upstream?
3. **Per-dataset opt-in.** Should URML annotation be applied across all 60 contributing datasets, or only to the subset whose contributing labs explicitly opt in?
4. **Foundation alignment.** Combined with [RFC-0037](0037-osrf-gazebo-integration.md), is there interest in cross-listing OXE alongside URML's conformance lane (a model trained on URML-annotated OXE could carry a URML-conformance badge on its Hugging Face model card)?
5. **DeepMind partner network.** Would the Gemini Robotics trusted-tester network (Agile Robots, Agility Robotics, Boston Dynamics, Enchanted Tools, Apptronik per published partnerships) benefit from a URML-annotated training corpus, or is that conversation better routed through DeepMind directly?
6. **Anything else.**

## Implementation note

RFC-0046 ships as a single RFC document PR. No annotation tooling and no schema spec in this PR. The actual `tools/oxe-annotator/` and the spec addendum follow in later sessions, gated on OXE governance feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from OXE governance and `google-deepmind/open_x_embodiment` maintainers)

1. Schema shape (sidecar field on trajectory vs. separate companion dataset).
2. Annotation quality bar for upstream acceptance.
3. Per-dataset opt-in vs. blanket annotation across all 60 datasets.
4. Cross-listing interest with URML conformance.
5. Routing to DeepMind's Gemini Robotics partner network.
6. Anything else.

## How to respond

The OXE landing page documents three channels:

- **General inquiries:** `open-x-embodiment@googlegroups.com` (Google Group).
- **Technical issues:** file an Issue on `google-deepmind/open_x_embodiment`.
- **Dataset contributions:** the Dataset Enrollment Form linked from the landing page.

URML's planned channel: send a primary email to `open-x-embodiment@googlegroups.com` pointing to this RFC, and file a cross-reference Issue on the GitHub repo for visibility. The email reaches the consortium; the Issue reaches the maintainers who watch the repo. (Note: `google-deepmind/open_x_embodiment` does not have Discussions enabled, per surface check 2026-05-23.)

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts about OXE (verified against the official landing page and the GitHub repo on 2026-05-23: 21 institutions, 34 labs, 60 datasets, 1M+ trajectories, 22 platforms, 527 manipulation skills).
- [x] Detailed design proposes a concrete annotation schema with worked example.
- [x] Three alternatives considered.
- [x] Drawbacks are real (annotation is the hard part, quality variance, distributed governance).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no annotation tooling or schema spec in this PR.
- [x] Surface verified: Discussions disabled, Issues enabled, Google Group + Dataset Enrollment Form documented. The "not an official Google product" disclaimer noted.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
