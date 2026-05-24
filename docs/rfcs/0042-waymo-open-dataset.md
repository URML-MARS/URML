---
rfc: 0042
title: Waymo Open Dataset integration, request for comment from waymo-research maintainers
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

# RFC-0042: Waymo Open Dataset integration, request for comment from waymo-research maintainers

## Summary

URML proposes to publish a public conformance demonstration encoding example scenarios from the Waymo Motion Dataset as URML behavior-composition programs, showing that URML's Layer-2 primitive vocabulary (the v0.1 set, plus `plan_path` / `follow_trajectory` once [RFC-0020](0020-autoware-av-substrate.md) ratifies) is expressive enough to describe the dataset's scenario taxonomy at the same level of detail Waymo's documentation uses. No URML spec change is proposed in this RFC, and no Waymo code or dataset content is redistributed. This RFC documents the proposed encoding shape and requests review and feedback from the `waymo-research/waymo-open-dataset` maintainers before the demonstration is published.

This is the third proposal-only outreach RFC, following RFC-0037 (OSRF / Gazebo), RFC-0040 (Hugging Face LeRobot), and RFC-0041 (ArduPilot). The ask is smaller than for the others: not a shipping adapter, but a research-courtesy review of the URML encoding plus permission to link from URML's conformance lane back to the Waymo dataset.

## Motivation

The Waymo Open Dataset is the most widely cited open autonomous-vehicle dataset, hosted at `waymo-research/waymo-open-dataset` (3,324 stars, 458 open issues, last commit 2026-05-22, default branch `master`). The Motion Dataset alone covers 103,354 scenes with object trajectories and corresponding 3D maps. `waymo-research/waymax` (1,066 stars, last commit 2026-05-21) is the hardware-accelerated companion simulator. Together they constitute the canonical research surface for evaluating any claim about how AV behavior can be described or executed.

URML's design commits to substrate-neutrality across vertically distinct robotics domains. RFC-0020 names Autoware Universe as a research-grade AV substrate target and proposes two new Layer-2 primitives (`plan_path`, `follow_trajectory`) plus an `av` profile to make AV intent expressible in URML. The honest test of whether those primitives are sufficient is not whether they sound right in a spec document. It is whether they can describe scenarios from the Waymo Motion Dataset at the level of detail Waymo's own scenario taxonomy uses.

A conformance demonstration that takes N representative Waymo Motion Dataset scenarios and shows them encoded as URML programs delivers two things URML needs and one thing it does not yet have. URML gets a public benchmark of primitive expressiveness against a community-recognized dataset, and an architectural test of whether [RFC-0020](0020-autoware-av-substrate.md) is internally consistent before its primitives ratify. The community gets a worked example of describing AV intent in a vendor-neutral grammar.

This RFC is proposal-only. The encoding plan is the deliverable; the public demonstration repository is the follow-up, contingent on `waymo-research` feedback.

## Detailed design

URML's existing artifacts that feed into the Waymo conformance demonstration:

- [`docs/rfcs/0020-autoware-av-substrate.md`](0020-autoware-av-substrate.md): the AV substrate RFC, Draft state. Adds `plan_path` and `follow_trajectory`, an `av` profile, and the `hd_map` / `odd` / `mrm` manifest blocks. The proposed demonstration uses these primitives once RFC-0020 ratifies, and uses the v0.1 vocabulary alone in the meantime.
- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the v0.1 primitive vocabulary, including `move_to`, `wait_for`, `report`, `measure`. These cover the simpler scenario types (lane following, stop-and-go, signalized intersection wait) directly.
- [`spec/layer-3-behavior/`](../../spec/layer-3-behavior/): the behavior-composition layer the demonstration programs are written in.
- [`reference/validator/`](../../reference/validator/): the static validator. Every demonstration program is parsed and validated against an `autoware_av_research` manifest before publication; programs that do not validate are not shipped.

### Proposed `waymo-conformance-demo/` package shape

Mirror the existing conformance fixture layout but as a standalone public repository rather than in-tree, since the demonstration depends on a Waymo dataset license the URML repository's contributors cannot inherit through clone.

```
urml-waymo-conformance-demo/
├── pyproject.toml                  # Apache 2.0; dataset-loading utilities only
├── README.md                       # encoding methodology + Waymo license posture
├── LICENSE                         # Apache 2.0 (covers the URML code only)
├── notebooks/
│   ├── 01_scenario_taxonomy.ipynb  # Waymo Motion scene types -> URML primitive sketches
│   ├── 02_validate_encodings.ipynb # round-trip through the URML validator
│   └── 03_waymax_replay.ipynb      # optional: feed URML-encoded scenarios into Waymax sim
└── encoded/
    ├── ...
    └── manifest.yaml               # the autoware_av_research manifest under which programs validate
```

The URML repository links to the demonstration repository from `docs/research/` and from the `av` profile spec once that profile lands. No Waymo dataset content lives in the URML repository.

### Proposed Waymo scenario to URML primitive mapping

The mapping shows how Waymo Motion Dataset scenario types compose from URML's primitive vocabulary. The first column lists categories Waymo's scenario taxonomy documents (per the dataset paper and Sim Agents Challenge documentation); the second column gives the URML primitive sequence; the third notes whether the encoding uses the v0.1 vocabulary alone or needs RFC-0020 primitives.

| Waymo scenario type | URML primitive sequence | RFC-0020 needed |
|---|---|---|
| Constant-velocity lane following | `move_to(pose_along_lane)`; `wait_for(condition.distance_threshold)` | no |
| Signalized intersection, traffic-light wait | `move_to(intersection_entry)`; `wait_for(event.signal_green)`; `move_to(intersection_exit)` | no |
| Yield at unprotected left turn | `plan_path(from: current, to: post_turn, along: hd_map.lanelet_id)`; `wait_for(condition.gap_window)`; `follow_trajectory($plan)` | yes |
| Lane change with adjacent traffic | `plan_path(from: current, to: target_lane_pose, along: hd_map)`; `follow_trajectory($plan, on_off_route: replan)` | yes |
| Pedestrian crossing yield | `move_to(crosswalk_approach)`; `wait_for(condition.no_person_in_zone)`; `move_to(crosswalk_clear)` | no |
| Stop sign 4-way negotiation | `move_to(stop_line)`; `wait_for(event.arrival_order_clear)`; `move_to(intersection_exit)` | no |
| Highway merge with planner consultation | `plan_path(from: ramp_end, to: highway_lane, along: hd_map.merge_corridor, store_alt_as: $mrm_fallback)`; `follow_trajectory($plan)` | yes |
| Construction-zone detour | `plan_path(... along: hd_map.detour_corridor)`; `follow_trajectory($plan, on_off_route: abort)` | yes |
| Operational design domain exit, controlled stop | `report(status: warning, facts: { reason: odd_violation })`; `follow_trajectory($mrm_fallback)` | yes |

Each row in the demonstration repository ships a worked example. Scenarios that need RFC-0020 primitives are marked clearly and validate against a future schema; the v0.1-only scenarios validate against the current schema today.

### Proposed validation methodology

Every demonstration program passes through three layers of validation before publication:

1. Parse against the URML Layer-3 schema. Reject malformed programs.
2. Validate against the `autoware_av_research` manifest (a research-grade AV manifest with declared HD-map binding, ODD region, and MRM strategy per [RFC-0020](0020-autoware-av-substrate.md)).
3. Cross-check the encoded scenario against the Waymo Motion Dataset scene metadata it claims to represent: object roles, road graph fragment, traffic-light states. Mismatches are flagged in the notebook output and not silently smoothed.

Programs that fail any layer are documented in the notebook with the failure mode, never silently dropped or quietly fixed. Honesty about coverage is more useful to readers than a curated success rate.

### Proposed Waymax integration

Optional. `waymo-research/waymax` provides a JAX-accelerated AV simulator that can replay Waymo Motion scenes with custom agent policies. A second demonstration notebook (`03_waymax_replay.ipynb`) takes a URML-encoded scenario, derives a Waymax-compatible agent policy from the URML primitive sequence, and replays the scenario in Waymax. This is the runtime side of the conformance story: URML primitive sequence as input, Waymax simulation as the substrate that executes it.

Out of scope for this RFC if Waymax integration adds licensing or maintenance complexity Waymo Research would not want. The conformance demonstration is useful with or without the Waymax notebook.

### Compatibility notes

- **Code license.** The conformance demonstration code is Apache 2.0, matching URML's license. URML's [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) keeps all reference work under Apache 2.0 permanently.
- **Dataset license.** The Waymo Open Dataset is distributed under the Waymo Open Dataset License Agreement, which restricts use to non-commercial research and forbids redistribution. The demonstration repository does not redistribute any Waymo dataset content. Notebooks load dataset files from the user's local Waymo distribution (the standard pattern for Waymo Open Dataset research code) and the README states the license posture clearly.
- **Python.** Waymo Open Dataset code targets Python 3.10+; `waymax` targets 3.10+. URML's reference packages target the same range. No dependency-band friction.
- **Origin.** Waymo LLC is a US entity (incorporated in California, Mountain View). URML's default US-federal compliance policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) operates at the manifest provenance level, not at the dataset level, and is not engaged by a conformance demonstration that loads dataset files.
- **Citation.** URML cites the Waymo Open Dataset paper (Sun et al., CVPR 2020) in the demonstration repository and in any downstream publication. The RFC asks for the preferred citation form.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: none in this RFC. The conformance demonstration consumes the existing validator and the `autoware_av_research` manifest scaffold from [RFC-0020](0020-autoware-av-substrate.md).
- Conformance suite: a new `docs/research/waymo-conformance.md` page in the URML repository points readers at the external demonstration repository when it publishes. The external repository is not part of the URML conformance suite proper.

## Backward compatibility

Pre-v1.0. Purely additive. No URML artifact changes. The external demonstration repository depends on URML's published packages, not the other way around.

## Drawbacks

- **Proposal-only is a weaker artifact than a published demonstration.** The honest framing matches RFC-0040 and RFC-0041: URML wants Waymo Research input on the encoding methodology and the citation form before publishing the demonstration repository, because both are choices the dataset community has stronger opinions on than URML's small team does.
- **The encoding is interpretive.** Waymo's scenarios are recordings of real driving; URML primitives describe declared intent. The mapping in the table above is URML's reading of the recorded behavior, not Waymo's ground truth about what the vehicle's planner intended. The demonstration calls this out explicitly in every notebook.
- **RFC-0020 has not ratified.** Several scenario types in the mapping table need primitives that are still in Draft. The demonstration ships in two phases: v0.1-vocabulary scenarios first, full coverage when RFC-0020 reaches Implemented state.
- **Dataset license is restrictive.** Anyone reproducing the demonstration must accept Waymo's dataset license. URML's Apache 2.0 reference work cannot bundle the dataset, only describe how to use it.

## Alternatives considered

1. **Publish the demonstration without consulting Waymo Research.** Rejected. The encoding is interpretive enough that a pre-RFC saves likely rework on the mapping table, and a downstream link from `waymo-open-dataset` to the demonstration is meaningfully more useful than a one-way citation.
2. **Use `waymo-research/waymax` instead of the Motion Dataset.** Rejected as the primary target. The Motion Dataset is the broader artifact and more community members work with it directly. Waymax is the optional second notebook.
3. **Skip Waymo and write the demonstration against Argoverse or nuScenes.** Rejected. Both are credible alternatives and the demonstration may extend to them later; Waymo is first because the dataset is the largest single AV research surface and because [RFC-0020](0020-autoware-av-substrate.md)'s primitives are most directly testable against Motion Dataset scenarios.
4. **Defer the demonstration until RFC-0020 ratifies.** Rejected. The v0.1 vocabulary already covers the simpler Waymo scenario types (constant-velocity lane following, signalized intersection wait, pedestrian crossing, stop sign), so publishing the v0.1-only scenarios first creates an artifact and surfaces RFC-0020's expressiveness gaps in concrete terms rather than abstract debate.

## Prior art

- `waymo-research/waymo-open-dataset`: the dataset and tooling repository (3,324 stars, 458 open issues, Apache 2.0 for code, separate dataset license, last commit 2026-05-22).
- `waymo-research/waymax`: the JAX-accelerated AV simulator (1,066 stars, last commit 2026-05-21).
- Sun et al., "Scalability in Perception for Autonomous Driving: Waymo Open Dataset", CVPR 2020: the canonical citation.
- Ettinger et al., "Large Scale Interactive Motion Forecasting for Autonomous Driving: The Waymo Open Motion Dataset", ICCV 2021: the Motion Dataset citation.
- WOD Challenges (Interaction Prediction, Sim Agents, Scenario Generation, Vision-Based End-to-End Driving): the leaderboard surface URML's demonstration does not enter.
- [RFC-0020](0020-autoware-av-substrate.md): the AV substrate RFC that defines `plan_path` / `follow_trajectory` / `hd_map` / `odd` / `mrm`.
- [RFC-0040](0040-hugging-face-lerobot.md): proposal-only outreach precedent (AI/ML layer).
- [RFC-0041](0041-ardupilot-integration.md): proposal-only outreach precedent (substrate).

## Unresolved questions

Provisional pending `waymo-research` maintainer feedback:

1. **Encoding faithfulness.** Is the URML primitive sequence for each Waymo scenario type a fair description of the scenario's intent, or does Waymo's scenario taxonomy use a partition that maps less cleanly than the table suggests? The "yield at unprotected left turn" row in particular blurs perception (gap detection) and actuation (follow trajectory); a tighter representation may be possible.
2. **Citation form.** What is the preferred form for citing the dataset in URML's demonstration repository and any downstream URML publication? The "Scalability in Perception" CVPR 2020 paper, the "Large Scale Interactive Motion Forecasting" ICCV 2021 paper, the dataset website, or a combination?
3. **Downstream wiki / README link.** Would `waymo-research` be open to a one-line link from `waymo-open-dataset`'s README or wiki to the URML conformance demonstration once it publishes, similar to how the dataset README links to third-party tools today?
4. **Waymax integration.** Is a derived agent policy that consumes URML primitive sequences and runs in Waymax an artifact `waymo-research` would find useful, or is the Motion Dataset notebook alone enough?
5. **Sim Agents Challenge.** The Sim Agents Challenge is the closest existing public benchmark to URML's "do these primitives suffice" question. Would Waymo Research find a non-competing URML reference-encoding-only entry (clearly tagged as a description benchmark, not a forecasting benchmark) useful, or is that out of scope for the challenge's design?
6. **Anything else.**

## Implementation note

RFC-0042 ships as a single RFC document PR. No demonstration code in this PR. The `urml-waymo-conformance-demo` external repository is the mechanical follow-up, contingent on `waymo-research` maintainer feedback. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml) (third proposal-only outreach RFC).

## Requested feedback (from waymo-research/waymo-open-dataset maintainers)

1. Encoding-faithfulness review of the scenario-type to primitive-sequence table (Q1).
2. Preferred citation form (Q2).
3. Interest in a downstream link from the dataset README or wiki to the URML demonstration when it publishes (Q3).
4. Waymax notebook scope (Q4).
5. Sim Agents Challenge fit (Q5).
6. Any scenario type the encoding table omits that URML should add.
7. Anything else.

## How to respond

The `waymo-research/waymo-open-dataset` repository accepts public Issues. The `enhancement` and `question` labels both exist (verified via `gh api repos/waymo-research/waymo-open-dataset/labels` on 2026-05-23) and `question` is the closer fit for an RFC of this kind, since the ask is review and feedback rather than a feature request. Discussions are not enabled on the repository.

URML's planned channel: open a single Issue on `waymo-research/waymo-open-dataset` labelled `question`, pointing to this RFC. No cross-post is planned because the dataset does not have a public forum analogous to ArduPilot's `discuss.ardupilot.org`.

URML's own public Discussions for the broader conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, smaller-than-0040/0041 ask, no spec change).
- [x] Motivation grounded in verified data (3,324 stars, 458 open issues, 103,354 motion scenes, last commit 2026-05-22), not boilerplate.
- [x] Detailed design names every affected component (RFC-0020, Layer-2 v0.1, Layer-3 behavior, validator, demonstration repo) with verified file paths.
- [x] At least one alternative considered (four are).
- [x] Drawbacks are real (proposal-only weaker artifact, interpretive encoding, RFC-0020 gap, restrictive dataset license).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added. The mapping uses existing v0.1 primitives where possible and waits on RFC-0020 for the rest.
- [x] Implementation note explicitly says no demonstration code in this PR; later session contingent on feedback.
- [x] Surface ("How to respond") is verified: Issues open, `enhancement` and `question` labels exist, Discussions not enabled.
- [x] No em-dashes in the RFC body, no formulaic structure, voice consistent with RFC-0040 / RFC-0041.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. Substrate-neutral posture preserved. No cloud dependency. No telemetry. Dataset license respected (no redistribution).
