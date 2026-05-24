---
rfc: 0056
title: Stanford ALOHA and Mobile ALOHA integration, request for comment from MarkFzp/mobile-aloha and tonyzhaozh/aloha maintainers
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

# RFC-0056: Stanford ALOHA and Mobile ALOHA integration, request for comment from MarkFzp/mobile-aloha and tonyzhaozh/aloha maintainers

## Summary

URML does not yet ship an ALOHA integration. This RFC proposes a `urml-aloha-bridge` reference package that hooks into ALOHA's existing teleoperation and data-collection scripts. Two integration vectors: (a) a URML-aware extension to `record_episodes.py` that captures the operator's current URML primitive alongside the raw observation and action streams, and (b) a post-hoc URML annotation pass over already-recorded ALOHA datasets. Trained policies downstream of either path can emit URML primitives natively. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the `MarkFzp/mobile-aloha` and `tonyzhaozh/aloha` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR. Research-collaboration shape, not a commercial-partnership ask.

## Motivation

ALOHA is the open-hardware reference for bimanual manipulation research. The original ALOHA (tonyzhaozh/aloha) was published from Stanford in 2023; Mobile ALOHA (MarkFzp/mobile-aloha, 4.4k stars at time of writing, MIT, Issues enabled with 16 open) extended it to whole-body bimanual mobile manipulation in January 2024. The hardware is reproducible: four ViperX 300 arms, four XM430-W350 grippers, three USB cameras, an AgileX Tracer mobile base, full system cost $32K including onboard power and compute. The Stanford Robotics Center maintains a demo and tutorial page. The published recipe is followed by labs across the OXE consortium.

Three things make ALOHA an unusually clean Move #2 target.

The hardware is the de-facto open standard for bimanual academic research. Most open-weights bimanual policies in 2026 (LeRobot's ACT and Diffusion variants, openpi's π0.5 fine-tunes, Ai2's MolmoAct 2 dataset) trace back to ALOHA recordings or ALOHA-derivative hardware. URML integration here lifts the URML primitive vocabulary into the training pipeline of every downstream bimanual policy that consumes ALOHA-shaped data.

The integration surface is teleoperation and data collection, not a runtime adapter. ALOHA's value to URML is at the data layer, not the execution layer. `record_episodes.py`, `visualize_episodes.py`, and `replay_episodes.py` are the scripts URML's bridge extends. The integration is lightweight and additive.

OXE alignment is direct. RFC-0046 proposes URML annotation on Open X-Embodiment trajectories, and many OXE-listed datasets are ALOHA-collected. A URML-aware ALOHA recording pipeline produces URML-annotated trajectories at source, which then flow into OXE and into every downstream policy that trains on OXE.

## Detailed design

URML's existing artifacts that feed into an ALOHA bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives the recorder labels with.
- [`spec/layer-4-nl-grammar/v0.1.0.md`](../../spec/layer-4-nl-grammar/v0.1.0.md): the NL grammar that lets operators describe what they are doing in natural language during recording.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's existing LLM-to-URML translation reference. Useful for post-hoc annotation passes.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime most likely to host ALOHA-derived policies on hardware.

### Proposed `urml-aloha-bridge` shape

A new `reference/aloha-bridge/` package (and PyPI mirror `urml-aloha-bridge`) that imports the existing ALOHA scripts and extends them.

```
urml_aloha_bridge/
├── pyproject.toml
└── src/
    └── urml_aloha_bridge/
        ├── __init__.py
        ├── record_with_urml.py     # Vector A: in-the-loop URML labelling
        ├── annotate_dataset.py     # Vector B: post-hoc annotation
        └── lerobot_export.py       # convert annotated episodes into LeRobotDataset v3
```

### Vector A: URML-aware teleoperation recording

A thin extension to `aloha_scripts/record_episodes.py`. During recording, the operator selects the current URML primitive (default UI: keyboard shortcut, optional: voice via URML's NL layer). The recorder writes the primitive label alongside the existing observation and action streams. The result is a labelled episode where every frame is tagged with the URML primitive the operator was executing.

```python
# record_with_urml.py
from aloha_scripts.record_episodes import RecordingSession  # documented entry point

class URMLAwareRecordingSession(RecordingSession):
    """Extends ALOHA's recording loop with a URML primitive label per frame."""

    def __init__(self, manifest_path, profile, **aloha_kwargs):
        super().__init__(**aloha_kwargs)
        self._current_primitive = None
        self._manifest = _load_validated(manifest_path)

    def on_primitive_change(self, primitive_name, params):
        # Bound to a keyboard or voice trigger; updates the active label.
        self._current_primitive = (primitive_name, params, self._timestep)

    def record_frame(self, obs, action):
        super().record_frame(obs, action)
        self._dataset.add_label(self._current_primitive)
```

### Vector B: Post-hoc URML annotation

For already-recorded ALOHA datasets, a separate pass infers URML primitive boundaries from the observation and action streams plus any natural-language task captions. The annotator uses URML's existing LLM bridge ([`reference/llm-bridge/`](../../reference/llm-bridge/)) with the chosen provider and emits the same labelled-frame format Vector A produces. The two paths converge on a single annotated-episode shape downstream consumers can rely on.

### Proposed export to LeRobotDataset v3

`lerobot_export.py` writes the labelled episodes into the LeRobotDataset v3 format (per [RFC-0040](0040-hugging-face-lerobot.md)) with the `urml_program` sidecar pattern proposed in [RFC-0046](0046-open-x-embodiment.md). This means policies trained through LeRobot, openpi, MolmoAct, GR00T, TRI LBM, or any other Move #2 target can consume URML-annotated ALOHA data via the standard dataset path.

### Proposed URML v0.1 to ALOHA mapping

| URML v0.1 primitive | ALOHA realisation |
|---|---|
| `move_to` | A contiguous run of joint-target frames on one or both 7-DOF arms. The bridge groups successive frames with similar end-effector trajectories into one `move_to` label. |
| `grasp` / `release` | XM430-W350 gripper-channel transition. Bimanual coordination needs the gripper id (left arm vs. right arm). |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences. ALOHA's bimanual recordings are particularly rich for these. |
| `measure` | A USB-camera reading present in the observation. |
| `wait_for` (event / threshold / signal) | An operator-marked pause (Vector A) or a stall in the action stream (Vector B). |
| `report` (structured status upstream) | An operator-marked annotation in the recording UI (Vector A) or a caption-derived event (Vector B). |

### Proposed conformance integration

`URML_ALOHA_INTEGRATION=1` env-gated CI workflow installs `urml_aloha_bridge`, replays a small URML-annotated fixture episode through `replay_episodes.py` in sim (no physical hardware required for CI), and asserts the URML primitive labels are consistent with the validator's parse of the equivalent URML program.

### Compatibility notes

- **License.** Mobile ALOHA is MIT; original ALOHA is MIT. URML is Apache 2.0. MIT and Apache 2.0 are compatible.
- **Hardware.** ALOHA's reproducibility is the integration's leverage. URML's bridge does not require physical hardware to run the post-hoc annotation pass; it only needs the recorded episodes.
- **Origin.** Stanford University is incorporated in California, US. ALOHA's recipe and Mobile ALOHA's extension both originate from Stanford. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **OXE alignment.** Many OXE datasets are ALOHA-collected. URML annotation at the ALOHA layer feeds URML annotation at the OXE layer; the two RFCs reinforce each other.
- **Research posture.** ALOHA is academic open-research code. The integration is a research-collaboration shape; outreach language reflects that.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The labelled-frame format reuses the OXE annotation shape (RFC-0046).
- Reference runtime: proposed new package `reference/aloha-bridge/`. Not built in this PR.
- Conformance suite: proposed new `aloha-integration.yml` workflow gated by `URML_ALOHA_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. ALOHA scripts are unchanged; the bridge subclasses or wraps them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants ALOHA maintainer input on the in-the-loop labelling UX before writing code, especially because the keyboard-vs-voice trigger question affects operator workflow.
- **Operator-labelled data is expensive to recollect.** Vector A only produces URML-labelled data for newly recorded episodes. Vector B fills the gap for existing recordings but at the cost of annotation quality (heuristic plus LLM, not human).
- **Bimanual coordination is a known URML gap.** ALOHA's bimanual setup exercises a URML expressiveness question that [RFC-0047](0047-allen-institute-molmoact.md) (Ai2 MolmoAct) also raised. Whether URML's Layer-2 vocabulary needs explicit bimanual coordination primitives or whether Layer-3 composition over single-arm primitives is sufficient is still an open question.
- **Academic surface.** ALOHA is maintained by individuals at Stanford and downstream users at other labs, not a sustained engineering team. Response cadence will be slower than for industrial targets.

## Alternatives considered

1. **Ship the bridge first, ask ALOHA maintainers later.** Rejected. ALOHA's in-the-loop labelling UX needs maintainer input.
2. **Vector A only, skip Vector B.** Rejected. Existing ALOHA datasets are valuable; Vector B unlocks them.
3. **Vector B only, skip Vector A.** Rejected. Operator-labelled data is the higher-quality source for any policy that should learn URML natively.
4. **Combine ALOHA with RFC-0046 (OXE).** Considered. The OXE RFC mentions Droid; ALOHA-collected datasets in OXE are a subset of that. The argument for separate RFCs is that ALOHA's leverage point is the recording pipeline itself, which lives upstream of OXE.
5. **Target only the original ALOHA (tonyzhaozh/aloha), skip Mobile ALOHA.** Rejected. Mobile ALOHA is the more active fork and the mobile-base extension is increasingly the production shape.

## Prior art

- `MarkFzp/mobile-aloha`: Mobile ALOHA upstream repo (4.4k stars, MIT, Issues enabled with 16 open, Discussions not visible). Forked from tonyzhaozh/aloha.
- `tonyzhaozh/aloha`: original ALOHA repo (the predecessor). Joint reference.
- Mobile ALOHA paper: arxiv 2401.02117 (January 2024).
- ALOHA hardware tutorial (Stanford Robotics Center demo page).
- [RFC-0040](0040-hugging-face-lerobot.md): URML's LeRobot integration. LeRobotDataset v3 export is the convergence point for ALOHA-annotated data.
- [RFC-0046](0046-open-x-embodiment.md): URML's OXE annotation. ALOHA-collected datasets in OXE benefit from upstream URML annotation.
- [RFC-0047](0047-allen-institute-molmoact.md): URML's Ai2 MolmoAct integration. Shares the bimanual-coordination open question.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): URML's NL-to-URML reference. The post-hoc annotation pass consumes it.

## Unresolved questions

Provisional pending ALOHA maintainer feedback:

1. **Labelling UX.** Keyboard shortcut, voice (via URML's NL layer), pedal trigger, or something else? Which fits operator workflow best?
2. **Bimanual coordination.** Does URML need a Layer-2 bimanual-coordination primitive (e.g., `coordinate(arm0, arm1, ...)`) or is Layer-3 composition over single-arm primitives sufficient? This is the same question RFC-0047 raised.
3. **Annotation provenance.** How should the URML annotation track which path produced it (operator-labelled vs. post-hoc inferred), and how should downstream consumers weight the difference?
4. **Bridge home.** Standalone `urml-aloha-bridge` on PyPI (URML-side), contributed example in `MarkFzp/mobile-aloha` (ALOHA-side), or a separate Stanford-affiliated repo?
5. **Existing-dataset coverage.** Is there an existing list of ALOHA-recorded episodes whose URML annotation would be highest leverage? The OXE-listed Droid subset is one obvious candidate.
6. **Hardware-tutorial alignment.** Should the Stanford Robotics Center hardware-tutorial page include a URML setup step alongside the existing recording instructions?
7. **Anything else.**

## Implementation note

RFC-0056 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/aloha-bridge/` package follows in a later session, gated on ALOHA maintainer feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from MarkFzp/mobile-aloha and tonyzhaozh/aloha maintainers)

1. Labelling UX (keyboard / voice / pedal / other).
2. Bimanual coordination primitive question.
3. Annotation provenance tracking.
4. Bridge home.
5. Existing-dataset coverage priorities.
6. Hardware-tutorial alignment.
7. Anything else.

## How to respond

`MarkFzp/mobile-aloha` has Issues enabled. Discussions are not visible. URML's planned channel: file an Issue on `MarkFzp/mobile-aloha` referencing this RFC, scoped to the labelling-UX question (Q1) and the bimanual-coordination question (Q2) so the maintainers see the questions most relevant to them. A parallel reference Issue on `tonyzhaozh/aloha` is appropriate to reach the original ALOHA maintainer line.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only.
- [x] Motivation grounded in verified facts (verified against the repo on 2026-05-23: MarkFzp/mobile-aloha 4.4k stars, MIT license, Issues enabled with 16 open, Discussions not visible, forked from tonyzhaozh/aloha, hardware spec verified — 4x ViperX 300 arms, 4x XM430-W350 grippers, 3 USB cameras, AgileX Tracer base, $32K full system cost). Mobile ALOHA paper from January 2024 (arxiv 2401.02117).
- [x] Detailed design proposes two concrete vectors that extend the documented ALOHA scripts without replacing them.
- [x] Five alternatives considered.
- [x] Drawbacks are real (proposal-only, recollection cost, bimanual primitive question, academic-surface cadence).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added (the bimanual question is flagged as open rather than presumed answered).
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Issues enabled, Discussions not visible, MIT license, ALOHA scripts catalogued (record_episodes.py, visualize_episodes.py, replay_episodes.py).
- [x] Research-collaboration framing made explicit (Stanford academic, not industrial partner).
- [x] Cross-references to other Move #2 RFCs intact (0040, 0046, 0047).
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant.
