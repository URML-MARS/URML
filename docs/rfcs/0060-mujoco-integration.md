---
rfc: 0060
title: MuJoCo physics-engine integration, request for comment from google-deepmind/mujoco maintainers
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

# RFC-0060: MuJoCo physics-engine integration, request for comment from google-deepmind/mujoco maintainers

## Summary

URML already ships a `reference/mujoco-runtime/` stub and a gated `mujoco-integration.yml` CI workflow. This RFC formalizes the in-progress MuJoCo integration and surfaces two integration vectors to the `google-deepmind/mujoco` maintainers: (a) a fully-implemented `MuJoCoAdapter` satisfying URML's substrate Protocol, and (b) an optional MuJoCo engine plugin (using MuJoCo's documented `/plugin/` architecture) that exposes URML primitive semantics inside MuJoCo's simulation loop. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the `google-deepmind/mujoco` maintainers.

Move #2 Outreach RFC. Proposal-only at the adapter-spec level (URML's existing mujoco-runtime stub is the in-tree placeholder).

## Motivation

MuJoCo (`google-deepmind/mujoco`, 13.6k stars, Apache 2.0 code with CC BY 4.0 docs, 158 open issues, 185 open PRs, both Discussions and Issues enabled, v3.8.1 released 2026-05-11, maintained by Google DeepMind) is the open-source physics-engine workhorse of modern robotics research. NVIDIA Isaac uses it for some workflows, Stanford ALOHA uses it for hardware-free validation, openpi documents MuJoCo as a deployment target, every major robot-learning library (LeRobot, RL toolkits, OpenAI Gym descendants) ships a MuJoCo adapter.

Three reasons MuJoCo is worth a focused RFC even though URML already targets it.

The existing `reference/mujoco-runtime/` is a stub. URML claims MuJoCo support but the adapter is not fully implemented and the conformance lane is gated behind `URML_MUJOCO_INTEGRATION=1`. Formalizing the integration via an RFC plus a complete adapter implementation closes that gap and tells the URML user "MuJoCo is a first-class substrate, not a planned one."

MuJoCo has a real plugin convention. The `/plugin/` directory in the repo is a documented extension point with first-party examples. URML's primitive vocabulary plus the validator's safety envelope is a natural target for a MuJoCo plugin: at simulation step, the plugin checks the next URML primitive's preconditions against MuJoCo's state and enforces the envelope without leaving the physics loop.

DeepMind is the institutional surface that overlaps most with the Open X-Embodiment outreach (RFC-0046). MuJoCo is DeepMind's core open-research engine; OXE governance lives in the same organization. A MuJoCo integration plus an OXE annotation pass plus the indirect Gemini Robotics touch via OXE gives URML a coherent, three-surface posture toward Google DeepMind without requiring three separate front-door asks.

## Detailed design

URML's existing artifacts that feed in:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives.
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): URML's existing MuJoCo runtime stub. This RFC formalizes its shape.
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/), [`reference/drake-runtime/`](../../reference/drake-runtime/) (proposed in [RFC-0059](0059-drake-model-based-robotics.md)): the sim sibling adapters; `MuJoCoAdapter` follows their pattern.

### Vector A: MuJoCoAdapter as URML substrate

A full `MuJoCoAdapter` class implementing URML's `ROSAdapter` Protocol. The adapter wraps `mujoco.MjModel`, `mujoco.MjData`, and `mujoco.mj_step` per the documented Python bindings (Python >= 3.10).

```python
# reference/mujoco-runtime/src/urml_mujoco_runtime/adapter.py
import mujoco
from urml_runtime.substrate.base import ROSAdapter

class MuJoCoAdapter(ROSAdapter):
    """URML substrate adapter executing programs through MuJoCo."""

    BRAND = "mujoco"

    def __init__(self, mjcf_path, manifest_path):
        self._model = mujoco.MjModel.from_xml_path(mjcf_path)
        self._data = mujoco.MjData(self._model)
        self._manifest = _load_validated(manifest_path)

    def move_to(self, pose, tolerance):
        # Set joint targets or end-effector pose; step until reached
        self._set_target(pose)
        while not self._reached(pose, tolerance):
            mujoco.mj_step(self._model, self._data)

    def grasp(self, gripper_id):
        ...

    # ... rest of the URML Protocol
```

The adapter slots into URML's existing reference-runtime family alongside `IsaacAdapter` (RFC-0050), `DrakeAdapter` (RFC-0059), and the proposed Gazebo adapter (RFC-0037).

### Vector B: MuJoCo engine plugin for URML primitive semantics

MuJoCo's `/plugin/` architecture lets external code register simulation-loop callbacks. A `urml_envelope_plugin` registered through this mechanism checks the active URML primitive against MuJoCo's state at every step and triggers a safety-envelope rejection from inside MuJoCo's loop, rather than from URML's validator outside the loop.

The plugin is optional and additive. Vector A works without it. Vector B sharpens the envelope's enforcement granularity for users who want simulation-loop-level safety, the same way Drake's analytical safety lane sharpens it for users who want formal verification (RFC-0059).

### Proposed URML v0.1 to MuJoCo mapping

| URML v0.1 primitive | MuJoCo realisation |
|---|---|
| `move_to` | Joint or end-effector target piped into the actuator inputs; `mj_step` until convergence within tolerance. |
| `grasp` / `release` | Gripper actuator transitions; explicit contact-attach or weld-constraint toggling on grasp. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences. No new Protocol method. |
| `measure` | MuJoCo sensor reading from the appropriate `MjData.sensordata` channel. |
| `wait_for` (event / threshold / signal) | Step until a state condition is satisfied; the URML envelope plugin (Vector B) can short-circuit at the step boundary. |
| `report` (structured status upstream) | URML's report channel; MuJoCo's logging is parallel. |

### Proposed conformance integration

URML already ships `mujoco-integration.yml` as the gated CI workflow against the existing stub. RFC-0060 proposes the workflow's substantive content: the existing red-mug fixture runs through `MuJoCoAdapter` and asserts identical pass/fail against `MockROSAdapter`. A second lane optionally loads `urml_envelope_plugin` and asserts it triggers on a deliberately-envelope-violating program.

### Compatibility notes

- **License.** MuJoCo is Apache 2.0 code with CC BY 4.0 docs. URML is Apache 2.0. The bridge ships Apache 2.0.
- **Python version.** MuJoCo bindings require Python >= 3.10. URML's reference packages already target 3.10+. Compatible.
- **MJCF and URDF.** MuJoCo's native scene format is MJCF. URML manifests reference URDF more commonly. The adapter accepts both via MuJoCo's URDF importer.
- **Origin.** Google DeepMind is the maintainer; MuJoCo was acquired in 2021. DeepMind is US-domiciled for the relevant purposes; Apache 2.0 distribution makes the policy boundary clean. Passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.
- **DeepMind institutional cluster.** This RFC plus RFC-0046 (OXE) plus the indirect Gemini Robotics touch through OXE form a three-surface DeepMind outreach. The maintainers may or may not see them as related; URML should not assume institutional threading.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: formalize `reference/mujoco-runtime/` from stub to full `MuJoCoAdapter`. Not in this PR.
- Conformance suite: substantive content for the existing `mujoco-integration.yml` workflow. Not in this PR.

## Backward compatibility

Pre-v1.0. Purely additive. The existing stub is not deleted; it is completed.

## Drawbacks

- **The stub-to-full transition is large.** URML's `reference/mujoco-runtime/` is currently scaffolding. Filling it in is real work and the RFC is honest about the gap between "URML supports MuJoCo" (claimed) and "URML's MuJoCo adapter is feature-complete" (not yet true).
- **Plugin vector is optional.** Vector B (engine plugin) is conceptually cleaner but operationally adds a build-time MuJoCo plugin dependency. Users who want only Vector A get most of the value without that dependency.
- **DeepMind institutional alignment is unstated.** This RFC plus RFC-0046 (OXE) are two separate front doors at DeepMind. Whether the maintainer groups talk to each other is not URML's business to assume.
- **Many sim-RFC siblings.** Move #2 now has Gazebo (RFC-0037), Isaac (RFC-0050), CARLA (RFC-0051), Drake (RFC-0059), MuJoCo (this RFC), plus Cosmos's video-prediction (RFC-0057) which is sim-adjacent. The substrate-neutrality story is well-supported; the maintenance cost is real.

## Alternatives considered

1. **Ship a complete MuJoCoAdapter and reference the new code in a tiny RFC.** Considered. The current document is closer to "RFC plus stub-to-full plan" than to "proposal-only". The hybrid is appropriate because the adapter is partially shipped already.
2. **Vector A only, skip the plugin work.** Reasonable. The plugin (Vector B) adds value but is not required for substrate parity.
3. **Combine MuJoCo with RFC-0046 (OXE) and RFC-0050 (Isaac) into one DeepMind RFC.** Rejected. Different repos, different maintainer groups inside DeepMind, different feedback asks.
4. **Skip MuJoCo because URML already supports it.** Rejected. The current support is a stub; treating it as done would be the kind of overclaiming the project explicitly avoids.

## Prior art

- `google-deepmind/mujoco`: the upstream repo (13.6k stars, Apache 2.0 code, CC BY 4.0 docs, both Discussions and Issues enabled, v3.8.1 released 2026-05-11, plugin architecture in `/plugin/`, first-party JS/WASM and C#/Unity bindings).
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/): URML's existing MuJoCo runtime stub. This RFC formalizes its shape.
- [RFC-0037](0037-osrf-gazebo-integration.md), [RFC-0050](0050-nvidia-isaac-lab-integration.md), [RFC-0051](0051-carla-simulator-integration.md), [RFC-0059](0059-drake-model-based-robotics.md): the other sim and substrate sibling RFCs.
- [RFC-0046](0046-open-x-embodiment.md): URML's OXE annotation. Same DeepMind institutional cluster.
- MuJoCo `STYLEGUIDE.md` and `CONTRIBUTING.md`: the documented contribution conventions URML's adapter follows.

## Unresolved questions

Provisional pending MuJoCo maintainer feedback:

1. **Adapter shape.** Is wrapping `MjModel` plus `MjData` plus `mj_step` directly the right entry point for URML's Protocol, or does DeepMind recommend a different composition?
2. **MJCF vs URDF.** URML manifests reference URDF more commonly; MuJoCo's native is MJCF. Is MuJoCo's URDF importer sufficient, or should the adapter expect MJCF first-class?
3. **Plugin viability.** Is the `urml_envelope_plugin` (Vector B) a use case the MuJoCo plugin architecture supports cleanly, or are there constraints that change the shape?
4. **DeepMind alignment.** Should URML coordinate the MuJoCo integration with the OXE annotation work (RFC-0046)? The two are technically independent but institutionally adjacent.
5. **Conformance lane.** Would DeepMind be open to MuJoCo's CI exercising a URML-validated scenario as one of its integration tests, similar to how MuJoCo's tests already cover OpenAI Gym integration shape?
6. **Anything else.**

## Implementation note

RFC-0060 ships as a single RFC document PR. The actual fill-in of `reference/mujoco-runtime/` from stub to full `MuJoCoAdapter` follows in a later session, gated on MuJoCo maintainer feedback. The optional engine plugin follows separately. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from google-deepmind/mujoco maintainers)

1. Adapter shape (`MjModel` plus `MjData` plus `mj_step` vs. alternative).
2. MJCF vs URDF first-class question.
3. Plugin viability for the URML envelope use case.
4. DeepMind institutional alignment with the OXE annotation work.
5. MuJoCo CI integration appetite.
6. Anything else.

## How to respond

`google-deepmind/mujoco` has Discussions enabled. URML's planned channel: open a Discussion on the repo (the help / questions category, since this is a substantive integration proposal rather than a bug report or feature request) pointing to this RFC. Optional Issue cross-reference if the Discussion gets low visibility.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that URML already has a stub.
- [x] Motivation grounded in verified facts (verified against the repo on 2026-05-23: google-deepmind/mujoco 13.6k stars, Apache 2.0 code + CC BY 4.0 docs, 158 open issues + 185 open PRs, both Discussions and Issues enabled, v3.8.1 released 2026-05-11, plugin architecture in /plugin/, first-party JS/WASM and C#/Unity bindings, Python >= 3.10).
- [x] Detailed design names two vectors with concrete code sketches following URML's existing substrate-adapter pattern.
- [x] Four alternatives considered.
- [x] Drawbacks are real (stub-to-full work, optional plugin, institutional ambiguity, sim-RFC siblings).
- [x] Backward compatibility: purely additive (stub is completed, not replaced).
- [x] No Layer-2 primitive added.
- [x] Implementation note honest about the stub-vs-full state.
- [x] Surface verified: Discussions and Issues both enabled, plugin architecture confirmed, recent release confirmed.
- [x] DeepMind institutional context noted without overclaiming threading.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant. Provider neutrality preserved.
