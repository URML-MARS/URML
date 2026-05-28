---
rfc: 0138
title: OpenVLA (Stanford / TRI / DeepMind 7B generalist VLA) integration, request for comment from openvla maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0138: OpenVLA (7B generalist vision-language-action model) integration, request for comment from openvla maintainers

## Summary

URML does not yet ship an OpenVLA manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for OpenVLA's 7B generalist vision-language-action model over [`openvla/openvla`](https://github.com/openvla/openvla) (MIT), and **requests review and feedback from the openvla maintainers**. No spec change.

**This is URML's first net-new VLA RFC after Move #2.** Move #2 (RFC-0040 / RFC-0045 / RFC-0046 / RFC-0050 / RFC-0054 / etc.) engaged 21 AI/ML-layer targets with `response: none` across the board (one engaged via Spot/rai-opensource, one declined). Move #11 picks up the net-new layer.

## Motivation

OpenVLA is the foundational open-source 7B generalist VLA. Built jointly by Stanford, TRI (Toyota Research Institute), and Google DeepMind, it became the de facto open reference for vision-language-action models when published. The repo at [`openvla/openvla`](https://github.com/openvla/openvla) (MIT, 6.3k stars, Issues enabled, last commit `2025-03-23` — borderline-stale by URML's 6-month rule but architecturally still the reference) is the canonical open VLA surface.

URML benefits from documenting the OpenVLA manifest mapping because:

1. **OpenVLA is the closest single example of a model whose output URML's primitive vocabulary can directly type-check.** A robot operator writes English; URML compiles to typed primitives; OpenVLA emits action tokens; URML's validator gates whether the emitted action sequence is consistent with the active capability manifest *before* anything publishes. The pre-flight safety check shape is identical to URML's Move-9 RFC-0108 ROSA framing.
2. **OpenVLA's `extra_inputs` action-head extension pattern** is structurally what URML's manifest needs to declare: which action-head class is active, what input modalities it consumes, what action-space dimensions it emits.
3. **URML can sit above OpenVLA as the validator layer, not in competition.** The same posture URML adopted toward Isaac Lab in Move-2 RFC-0050.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `openvla_generalist_cell.yaml` fixture)

Manifest does not currently declare VLA presence; the closest existing structure is the `actuators` block plus a (new) `model` block. Proposed mapping uses the `custom` mobility / capability escape-hatch to declare an OpenVLA-class controller is present:

| URML field | Maps to OpenVLA attribute |
|---|---|
| `name` | Deployment handle (`openvla_7b_default`, `openvla_7b_finetuned`) |
| `controller_class: custom` (`vla_model`) | Declares a VLA controller is in the loop; v0.1 has no native `vla_model` controller class |
| `controller_class: custom` (`action_head: openvla_default`) | Declares which OpenVLA action head is active (7-DoF default, finetuned, or `extra_inputs`-extended) |
| `controller_class: custom` (`input_modalities: rgb+text`) | Declares the modalities OpenVLA consumes |
| `controller_class: custom` (`output_action_space`) | Declares the action-space (delta-EEF / joint-velocity / etc.) URML primitives translate to |

### What URML v0.1 does not yet express for OpenVLA

1. **Action-head class declaration.** OpenVLA's `extra_inputs` mechanism lets new action heads be added by extending the `OpenVLAOutputs` class. URML's manifest has no first-class field for declaring which action head is loaded; the manifest can today only declare it via the `custom` escape-hatch. Spec RFC for action-head class declaration is queued, shared with RFC-0139 (Octo) and RFC-0151 (Microsoft CogACT).
2. **VLA-as-controller declaration.** URML's v0.1 controller / actuator vocabulary is direct-control (move_to, joint commands, primitive dispatch). A VLA is a learned controller that emits actions URML's manifest does not today reason about.
3. **Pre-flight validation boundary.** Where URML's validator sits in the OpenVLA execution loop (pre-flight check vs validator-only-on-output vs URML emits-to-OpenVLA-and-validates) is a design point worth maintainer input.

### Compatibility notes

- **Vendor org.** [`openvla`](https://github.com/openvla) — vendor-direct.
- **Flagship repo.** [`openvla/openvla`](https://github.com/openvla/openvla) — MIT, 6.3k stars, Issues enabled, last commit 2025-03-23 (borderline-stale; architecture still the reference).
- **Origin.** Stanford / TRI / Google DeepMind collaboration (US). Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Foundational open-source VLA; multiple downstream finetunes; the repo is the reference for the architecture even when push cadence is slower than the original release flurry.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; action-head class declaration Spec RFC queued in parallel (shared with RFC-0139 / RFC-0151).
- Reference runtime: future `reference/vla-bridge/` package with `OpenVLABridge` (URML-validates-OpenVLA-output pre-publish) is the strong candidate; the bridge composes above the existing `reference/llm-bridge/` natural-language layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Last-commit staleness.** Push date 2025-03-23 puts OpenVLA outside URML's 6-month recency window from 2026-05-28; the project is foundational rather than actively-iterating. The engagement here may yield a redirect to a successor.
- **Action-head class Spec RFC prerequisite.** Same gap as RFC-0139 / RFC-0151.
- **VLA-vs-validator execution-path boundary is novel design territory.** The natural-language-bridge + OpenVLA composition is the first time URML's NL layer meets a generalist learned controller; the architecture question is genuinely open.

## Alternatives considered

1. **Defer OpenVLA until action-head class Spec RFC lands.** Rejected. OpenVLA's maintainer input shapes the Spec RFC; deferral guarantees no input.
2. **Bundle OpenVLA + Octo + CogACT into one VLA RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor; the action-head Spec RFC is the shared piece.
3. **Engage TRI broader (vla_foundry from Move-2 RFC-0054) instead of openvla directly.** Considered. TRI-LBM is the model-program engagement; OpenVLA is the model-architecture engagement. Different scope.

## Prior art

- [`openvla/openvla`](https://github.com/openvla/openvla) — the upstream repo.
- [`huggingface/lerobot`](https://github.com/huggingface/lerobot) — RFC-0040 Move-2 engaged HuggingFace LeRobot at the policy-library layer.
- [`Physical-Intelligence/openpi`](https://github.com/Physical-Intelligence/openpi) — RFC-0045 Move-2 engaged Pi0 at the foundation-model layer.
- [`TRI-ML/vla_foundry`](https://github.com/TRI-ML/vla_foundry) — RFC-0054 Move-2 engaged TRI-LBM at the model-program layer.
- [RFC-0108 (NASA-JPL ROSA)](0108-nasa-jpl-rosa-outreach.md) — URML's NL-bridge engagement on the agent-tool layer (structurally similar pre-flight-check shape).
- [RFC-0021 (NL layer)](0021-on-device-llm-bridge.md) — URML's NL substrate that composes with OpenVLA.

## Unresolved questions

For the openvla maintainers:

1. **Repository status.** Is `openvla/openvla` actively maintained, dormant-but-supported, or has the active development moved to successor projects (`openvla/openvla-mini`, `openvla/openvla-oft`, etc.)? Where does engagement live in 2026?
2. **Action-head class manifest fields.** URML's v0.1 has no `vla_model` controller class. A Spec RFC adding it (and the `action_head` / `input_modalities` / `output_action_space` declarations) is queued. What manifest fields would an OpenVLA deployment expect?
3. **Pre-flight validation boundary.** Should URML's validator sit (a) above OpenVLA's output (URML validates emitted actions against manifest before publish), (b) below the NL input (URML compiles NL to typed primitives that OpenVLA's planner consumes), or (c) in a side-channel that monitors but does not gate?
4. **`extra_inputs` declaration.** OpenVLA's action-head extension mechanism is the natural place URML's manifest could plug in. Would the maintainers prefer URML's bridge ship as a contributed `extra_inputs` example, or as an external bridge that reads OpenVLA outputs without modification?
5. **Bridge home.** URML repo (`reference/vla-bridge/`), `openvla/openvla-urml-bridge` repo, or external?
6. **Conformance listing.** Would the openvla maintainers consider a README link to URML's compatible-runtimes registry once a working bridge ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0138 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`openvla/openvla` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the push-date staleness.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 6.3k stars, Issues enabled, last commit 2025-03-23, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, action-head Spec-RFC prerequisite, validator-boundary design novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Stanford / TRI / Google DeepMind US; default policy passes.
- [x] CLAUDE.md compliance check passed.
