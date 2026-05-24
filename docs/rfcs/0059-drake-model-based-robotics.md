---
rfc: 0059
title: Drake model-based robotics integration, request for comment from RobotLocomotion/drake maintainers
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

# RFC-0059: Drake model-based robotics integration, request for comment from RobotLocomotion/drake maintainers

## Summary

URML does not yet ship a Drake integration. RFC-0054 (TRI Large Behavior Models) flagged Drake as future scope; this RFC closes that gap. The proposed `urml-drake-bridge` package implements two complementary integration vectors against `RobotLocomotion/drake`: (a) a `DrakeAdapter` that satisfies URML's substrate Protocol so URML programs execute through Drake's simulation, and (b) a Drake-backed analytical safety lane that consults Drake's collision checking, reachability analysis, and trajectory-optimization tools before URML's validator accepts a program. No spec change on URML's side. This RFC documents both vectors and requests review and feedback from the `RobotLocomotion/drake` maintainers.

Move #2 Outreach RFC. Proposal-only: no bridge code in this PR. Drake's model-based verification is the analytical counterpart to the learned-world-model safety lanes proposed in RFC-0052 (V-JEPA 2) and RFC-0057 (Cosmos-Predict2.5).

## Motivation

Drake is the most mature open-source model-based robotics toolkit. The repo (`RobotLocomotion/drake`, 4k+ stars, BSD-licensed, 672 open issues with Discussions enabled, 23 open PRs, 34,822+ commits, v1.53.0 released 2026-05-15) is the canonical model-based-design surface in robotics open-source. The project originated at MIT (drake.mit.edu) and is maintained under the RobotLocomotion organization with significant TRI involvement. The codebase is primarily C++ (88.4%) with Python bindings (6.1%); both surfaces are first-class.

Drake fills a Move #2 niche the rest of the program does not. The Move #2 targets so far are learning-first: HF LeRobot (RFC-0040), Physical Intelligence (RFC-0045), Open X-Embodiment (RFC-0046), Allen Institute MolmoAct (RFC-0047), Anthropic (RFC-0048), NVIDIA Isaac (RFC-0050), Meta V-JEPA 2 (RFC-0052), TRI LBM (RFC-0054), NVIDIA Cosmos (RFC-0055, RFC-0057), Stanford ALOHA (RFC-0056). Drake is the model-based, analytical counterpart. Trajectory optimization, contact-rich manipulation under model-based control, formal reachability and safety analysis — Drake's strengths are precisely the surfaces where learned-policy work is weakest.

Three reasons this is the right Drake integration shape.

Drake is a substrate, not a policy. The `DrakeAdapter` follows the existing URML substrate pattern (`MockROSAdapter`, `MuJoCoAdapter`, `IsaacAdapter`). URML programs validate and execute through Drake the same way they execute through Gazebo (RFC-0037) or Isaac Sim (RFC-0050). Adding Drake to URML's substrate roster increases substrate-neutrality coverage.

Drake's verification surface is analytical, not learned. The Drake-backed safety lane provides certainty where V-JEPA 2 and Cosmos-Predict2.5 provide statistical confidence. For programs that require formal guarantees (industrial-profile RFC-0013, AUTOSAR substrate RFC-0019), Drake's analytical pass is the natural validation.

The TRI cross-reference makes the institutional path coherent. TRI co-maintains Drake and ships TRI LBMs (RFC-0054). A URML program that compiles down to Drake-verified motion and an LBM-emitted action chunk is the bridge URML needs between learned policies and model-based execution.

## Detailed design

URML's existing artifacts that feed into a Drake bridge:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the 20 Layer-2 primitives.
- [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md): the active safety envelope, extended by the analytical lane.
- [`reference/validator/`](../../reference/validator/): the validator that gates every URML program.
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/) and [`reference/isaac-runtime/`](../../reference/isaac-runtime/): the existing sim sibling adapters; `DrakeAdapter` follows their pattern.
- [`reference/industrial-arm-runtime/`](../../reference/industrial-arm-runtime/): the runtime most likely to benefit from Drake's analytical safety lane.

### Proposed `urml-drake-bridge` shape

A new `reference/drake-runtime/` package plus a sibling `reference/drake-verification/` library. Two surfaces, one bridge:

```
urml_drake_bridge/
├── pyproject.toml
└── src/
    └── urml_drake_bridge/
        ├── __init__.py
        ├── adapter.py              # DrakeAdapter implementing URML substrate Protocol
        ├── verification.py         # analytical safety lane backed by Drake's solvers
        ├── primitives_to_drake.py  # URML primitive to Drake Simulator translation
        └── manifest_alignment.py   # Drake URDF/SDF to URML capability manifest alignment
```

### Vector A: DrakeAdapter as URML substrate

A `DrakeAdapter` class implementing URML's `ROSAdapter` Protocol (the substrate-neutral interface every URML runtime adheres to). The adapter holds a `drake::systems::Simulator` instance, translates URML primitive calls into Drake `Diagram` inputs, and advances the simulation per primitive.

```python
# adapter.py (sketch; concrete signatures track URML's existing adapter conventions)
from pydrake.all import Simulator, Diagram, MultibodyPlant
from urml_runtime.substrate.base import ROSAdapter

class DrakeAdapter(ROSAdapter):
    """URML substrate adapter executing programs through Drake."""

    BRAND = "drake"

    def __init__(self, urdf_path, manifest_path):
        diagram_builder = self._build_diagram(urdf_path)
        self._diagram = diagram_builder.Build()
        self._simulator = Simulator(self._diagram)
        self._manifest = _load_validated(manifest_path)

    def move_to(self, pose, tolerance):
        # Translate to a Drake control input and advance simulation
        self._set_target_pose(pose)
        self._simulator.AdvanceTo(self._simulator.get_context().get_time() + dt)

    def grasp(self, gripper_id):
        # Drive gripper joint via Drake's MultibodyPlant input port
        ...

    # ... rest of the URML Protocol
```

`DrakeAdapter` slots into URML's existing adapter family. URML programs that validate against the manifest run through Drake without any URML-side changes.

### Vector B: Drake-backed analytical safety lane

A second module exposes Drake's verification tools to URML's validator. Before a program is accepted, the validator can request:

- **Collision checking**: Drake's `CollisionChecker` against the workspace geometry declared in the URML manifest.
- **Reachability analysis**: Drake's inverse-kinematics and reachability tools confirm the program's pose targets are reachable on the named robot.
- **Trajectory optimization**: Drake's `DirectCollocation` and related solvers validate that a smooth trajectory satisfying the URML program's constraints exists.

```python
# verification.py (sketch)
from pydrake.all import CollisionChecker, InverseKinematics, DirectCollocation
from urml_validator.envelope import SafetyEnvelope

class DrakeAnalyticalSafetyCheck:
    """URML analytical-safety lane backed by Drake's solvers."""

    def __init__(self, urdf_path, manifest_path):
        self._plant = _build_plant(urdf_path)
        self._envelope = SafetyEnvelope.from_manifest(manifest_path)

    def verify(self, urml_program):
        for primitive in urml_program:
            if not self._check_collision(primitive): return Failed("collision")
            if not self._check_reachability(primitive): return Failed("reach")
            if not self._optimize_trajectory(primitive): return Failed("traj")
        return Passed
```

The analytical lane gives URML formal verification for the subset of primitives Drake can model exactly. The learned-model lanes (V-JEPA 2, Cosmos-Predict2.5) cover the open-world scenarios Drake cannot. The two lanes compose: URML's validator can run the analytical lane for verifiable primitives and the predictive lane for novel ones.

### Proposed URML v0.1 to Drake mapping

| URML v0.1 primitive | Drake realisation |
|---|---|
| `move_to` | Pose target piped into `MultibodyPlant`'s control input; `Simulator.AdvanceTo(target_time)` integrates dynamics. |
| `grasp` / `release` | Gripper joint target driven via the gripper's input port; explicit fixed-joint attach / detach on contact. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, [RFC-0013](0013-industrial-layer2-primitives.md)) | Composed Layer-3 sequences over `move_to` plus `grasp` / `release`. Drake's contact dynamics make these particularly well-behaved. |
| `measure` | Drake sensor model output (force / torque, camera, IMU) consumed from the appropriate output port. |
| `wait_for` (event / threshold / signal) | Drake event-trigger system; latch on first matching event. |
| `report` (structured status upstream) | Drake's logging infrastructure; URML's report channel surfaces alongside. |

### Proposed conformance integration

A `URML_DRAKE_INTEGRATION=1` env-gated CI workflow installs `urml_drake_bridge`, runs the existing red-mug fixture through `DrakeAdapter`, and asserts identical pass / fail outcomes against `MockROSAdapter`. A second test runs the analytical safety lane on a deliberately-infeasible program (unreachable pose target) and asserts it rejects.

### Compatibility notes

- **License.** Drake is BSD-licensed. URML is Apache-2.0. The bridge ships Apache-2.0. BSD and Apache-2.0 are compatible.
- **C++ vs. Python.** Drake's primary API is C++; Python bindings exist but lag the C++ surface. URML's bridge uses Python bindings for the adapter and verification layers, matching URML's existing reference-runtime convention.
- **MuJoCo, Isaac Sim, Gazebo coexistence.** URML already ships sim siblings (`mujoco-runtime`, `isaac-runtime`); a Gazebo bridge is proposed in RFC-0037; CARLA in RFC-0051. Drake fills the model-based-design niche the others do not. The substrate-neutrality story is reinforced, not duplicated.
- **TRI relationship.** Drake is co-maintained by TRI. RFC-0054 (TRI LBM) cross-references this RFC. The two together cover TRI's learning-and-model dual surface.
- **Origin.** RobotLocomotion is MIT-rooted with TRI investment. Both are US-domiciled. Drake passes URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: the analytical safety lane composes with the (future) predictive-safety spec RFC noted in RFC-0052 and RFC-0057. Drake is one analytical backend; V-JEPA 2 and Cosmos-Predict2.5 are predictive backends. The spec defines the contract; the bridges supply implementations.
- Reference runtime: proposed new package `reference/drake-runtime/` plus `reference/drake-verification/`. Not built in this PR.
- Conformance suite: proposed new `drake-integration.yml` workflow gated by `URML_DRAKE_INTEGRATION`.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Drake itself is unaffected; the bridge consumes its documented public API.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping bridge.** URML wants Drake maintainer input on the substrate-adapter shape (Drake's `Diagram` abstraction does not map one-to-one onto URML's `Protocol`) and on which verification surfaces are the right entry points.
- **Drake's Python bindings lag the C++ surface.** Some verification primitives URML wants to expose may not yet have Python wrappers. The bridge would need to either contribute upstream wrappers (good for Drake and for URML) or fall back to a subset of the C++ surface.
- **The verification lane is expensive.** Optimization-based safety analysis can take seconds to minutes per program. Operators will need cost-aware deployment guidance, similar to the predictive lanes (RFC-0052, RFC-0057).
- **Two-sim-RFC overlap risk with RFC-0037 (Gazebo) and RFC-0050 (Isaac).** Drake is the third-or-fourth simulator-side RFC. Each targets a different niche (Gazebo for ROS workflows, Isaac for GPU-accelerated learning, Drake for model-based verification), but the bridge surface is large and the maintenance cost across all of them is real.

## Alternatives considered

1. **Ship the bridge first, ask Drake maintainers later.** Rejected. Drake's `Diagram` abstraction and verification entry points are non-obvious; a pre-RFC clarifies the shape.
2. **Vector A only (substrate adapter), skip Vector B (analytical safety).** Rejected. The analytical lane is the distinctive Drake value; without it the bridge is a fourth sim adapter.
3. **Vector B only (analytical safety), skip Vector A (substrate adapter).** Rejected. The substrate adapter gives URML programs a direct execution path through Drake's simulation; without it the analytical lane has nowhere to run.
4. **Combine with RFC-0054 (TRI LBM) into a single TRI-stack RFC.** Rejected. Drake and LBM are different shapes (model-based vs. learning), different repos (`RobotLocomotion/drake` vs. `TRI-ML/vla_foundry`), and benefit from separate feedback asks.
5. **Defer until after the predictive-safety spec RFC lands.** Rejected. Drake's analytical lane works under URML's current safety envelope without the predictive-safety spec; landing the spec later only adds the alternative backends, it does not constrain Drake's lane.

## Prior art

- `RobotLocomotion/drake`: the upstream repo (4k+ stars, BSD, 672 open issues, Discussions enabled, v1.53.0 released 2026-05-15, MIT-rooted via drake.mit.edu, TRI co-maintained, 34,822+ commits).
- Drake textbook material at underactuated.mit.edu (Russ Tedrake) and manipulation.mit.edu.
- [RFC-0037](0037-osrf-gazebo-integration.md): URML's OSRF / Gazebo proposal. Sim sibling.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): URML's Isaac integration. Sim sibling.
- [RFC-0051](0051-carla-simulator-integration.md): URML's CARLA integration. AV-sim sibling.
- [RFC-0052](0052-meta-fair-vjepa2.md), [RFC-0057](0057-nvidia-cosmos-predict.md): URML's predictive-safety lanes. Analytical-safety counterpart sits here.
- [RFC-0054](0054-tri-large-behavior-models.md): URML's TRI LBM integration. Cross-references this RFC as the model-based pair to LBM's learning-based shape.
- [`reference/mujoco-runtime/`](../../reference/mujoco-runtime/), [`reference/isaac-runtime/`](../../reference/isaac-runtime/): the existing sim adapter siblings.

## Unresolved questions

Provisional pending Drake maintainer feedback:

1. **Substrate-adapter shape.** Is wrapping a `drake::systems::Simulator` plus `Diagram` the right entry point for the URML adapter, or does Drake recommend a different composition (e.g., `LeafSystem` subclass)?
2. **Verification surface scope.** Which Drake solvers are the most appropriate first targets for the analytical safety lane? `InverseKinematics`, `CollisionChecker`, `DirectCollocation` are the candidates the RFC names; others may be more relevant.
3. **Python binding coverage.** Are the Python bindings for the proposed verification calls complete enough today, or would URML need to contribute upstream wrappers?
4. **Bridge home.** Standalone `urml-drake-bridge` on PyPI (URML-side), `RobotLocomotion/drake/examples/` contributed example (Drake-side), or both?
5. **Composition with learned-model lanes.** RFC-0052 (V-JEPA 2) and RFC-0057 (Cosmos-Predict2.5) propose learned-world-model safety lanes. URML's future predictive-safety spec RFC will need a contract that supports both analytical and predictive backends. Is there a Drake-side maintainer perspective on what that contract should look like?
6. **TRI alignment.** TRI co-maintains Drake and ships TRI LBM (RFC-0054). Should the URML integration with TRI LBM and Drake be threaded together institutionally, or kept separate?
7. **Anything else.**

## Implementation note

RFC-0059 ships as a single RFC document PR. No bridge code in this PR. The actual `reference/drake-runtime/` and `reference/drake-verification/` packages follow in later sessions, gated on Drake maintainer feedback. Draft state. Move #2 RFC. Ledger entry in [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml).

## Requested feedback (from RobotLocomotion/drake maintainers)

1. Substrate-adapter shape (Simulator plus Diagram vs. LeafSystem subclass).
2. Verification surface scope (which solvers first).
3. Python-binding coverage gaps.
4. Bridge home (URML-side vs. Drake-side vs. both).
5. Analytical-plus-predictive safety-lane contract.
6. TRI institutional threading.
7. Anything else.

## How to respond

`RobotLocomotion/drake` has GitHub Discussions enabled. URML's planned channel: open a Discussion on the repo (the equivalent of "Show & Tell" or "Ideas" category, depending on Drake's setup) pointing to this RFC, with a cross-reference Issue if the Discussion gets low visibility. Optional cross-post on the Drake user forum at drake.mit.edu if there is one, and on the underactuated.mit.edu community.

URML's own public Discussions for the broader Move #2 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed and that this is proposal-only. The model-based-vs-learned framing is named explicitly.
- [x] Motivation grounded in verified facts (verified against the repo on 2026-05-23: RobotLocomotion/drake 4k+ stars, BSD-licensed, 672 open issues with Discussions enabled, 23 open PRs, 34,822+ commits, v1.53.0 released 2026-05-15, C++ 88.4% with Python bindings 6.1%, MIT-rooted via drake.mit.edu, TRI co-maintained).
- [x] Detailed design proposes two concrete vectors with code sketches that follow URML's existing substrate-adapter pattern and that compose with the predictive-safety lanes proposed in RFC-0052 and RFC-0057.
- [x] Five alternatives considered.
- [x] Drawbacks are real (proposal-only, Python-binding lag, verification cost, sim-RFC overlap).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no bridge code in this PR.
- [x] Surface verified: Discussions and Issues both enabled, recent release confirmed, MIT and TRI institutional context confirmed.
- [x] Analytical vs. predictive framing made explicit: Drake fills the model-based-verification niche the learned-world-model RFCs do not.
- [x] Cross-references to other Move #2 RFCs intact (0037, 0050, 0051, 0052, 0054, 0057) plus URML's existing simulator runtimes.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and [`AGENTS.md`](../../AGENTS.md) §Outreach verification; compliant. Provider neutrality preserved.
