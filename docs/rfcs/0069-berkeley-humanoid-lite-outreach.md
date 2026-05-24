---
rfc: 0069
title: Berkeley Humanoid Lite integration, request for comment from HybridRobotics maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-24
updated: 2026-05-24
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

# RFC-0069: Berkeley Humanoid Lite integration, request for comment from HybridRobotics maintainers

## Summary

URML does not yet ship a Berkeley Humanoid Lite integration. This RFC proposes a `BerkeleyHumanoidLiteAdapter` under [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/) targeting the [`HybridRobotics/Berkeley-Humanoid-Lite`](https://github.com/HybridRobotics/Berkeley-Humanoid-Lite) repository (1.3k stars, MIT code + CC-BY-SA 4.0 assets, Python 99.1%, Issues enabled). The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto the Isaac Lab task interface and the Python control surface that drives the open-hardware sub-$5k humanoid. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the UC Berkeley Hybrid Robotics Lab maintainers.

This is the fifth Move #4 RFC. Berkeley Humanoid Lite anchors **frontier-open humanoid hardware** in the Move #4 sweep: a 2025 release from UC Berkeley with modular 3D-printed gearboxes and a fully open BOM, early enough in the platform's lifecycle that URML can become the default substrate-neutral interface before any other vocabulary anchors.

## Motivation

Berkeley Humanoid Lite is the most distinctive open-hardware humanoid target available right now. The platform is:

- **Genuinely open.** Hardware files, firmware, training code, and Isaac Lab task definitions are all public (1.3k stars on GitHub at time of writing, MIT for code, CC-BY-SA 4.0 for assets).
- **Affordable.** Sub-$5k BOM (3D-printed gearboxes plus widely available components). The price-to-build floor is one order of magnitude below Unitree H1 or Apptronik Apollo.
- **Research-fresh.** Released in 2025 from the UC Berkeley Hybrid Robotics Lab (Koushil Sreenath's group), with arXiv 2504.17249 documenting the design. The platform is too new for entrenched standards to have emerged; URML's adapter can become the default substrate-neutral surface for it.
- **Sim-friendly.** The repo ships Isaac Lab task definitions; URML's existing [RFC-0050 (NVIDIA Isaac Lab + Isaac-GR00T)](0050-nvidia-isaac-lab-integration.md) outreach surface directly composes.

Three things make this RFC concrete rather than aspirational. First, the `HybridRobotics/Berkeley-Humanoid-Lite` repo is Apache-compatible (MIT code, CC-BY-SA 4.0 assets), Python 99.1%, Issues enabled with 8 open at time of writing, "We wholeheartedly welcome contributions from the community" stated in the README. Second, the platform ships Isaac Lab task definitions, which means URML's RFC-0050 outreach to Isaac Lab and the Berkeley Humanoid Lite outreach compose at the task-vocabulary level: a URML program that targets Isaac Lab through the URML adapter immediately gains a real-hardware path through the Berkeley humanoid. Third, the academic-research audience (graduate students replicating sim-to-real on a sub-$5k humanoid) is exactly the audience URML's English-to-primitive translation lane benefits most.

Berkeley Humanoid Lite's posture is fully open: MIT code, CC-BY-SA 4.0 assets, English-first README, US-domiciled (UC Berkeley). URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. The platform does not compete with URML for the substrate-neutral vocabulary role. Berkeley Humanoid Lite is the hardware plus the sim2real training scaffold. URML is the spec the policy's post-processor (and the English-to-program path) can target.

## Detailed design

URML's existing artifacts that feed into a Berkeley Humanoid Lite adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the natural home for the Berkeley platform.
- [RFC-0009](0009-legged-humanoid-mobility.md): the humanoid mobility capability surface.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md) (Draft): the whole-body primitives that the platform's bipedal locomotion exercises.
- [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/): the runtime that hosts humanoid adapters.
- [`reference/isaac-runtime/`](../../reference/isaac-runtime/): the sim sibling. RFC-0050 outreach is the institutional cross-link.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `BerkeleyHumanoidLiteAdapter` shape

One adapter, parameterised by sim-vs-real and by Isaac Lab task version. Package layout:

```
reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/
├── __init__.py
├── adapter_sim.py           # Isaac Lab task dispatch (sim)
├── adapter_real.py          # Hardware control via the published Python interface (real)
├── isaac_lab_tasks.py       # mapping URML primitives to Isaac Lab task vector
└── manifests/
    ├── berkeley_humanoid_lite_sim.yaml
    └── berkeley_humanoid_lite_real.yaml
```

The sim adapter routes through Isaac Lab; the real adapter routes through the platform's Python control interface to the 3D-printed-gearbox actuator stack. Both implement URML's substrate Protocol.

### Proposed URML v0.1 to Berkeley Humanoid Lite mapping

| URML primitive | Sim (Isaac Lab) | Real (Python hardware interface) |
|---|---|---|
| `move_to(pose)` | Isaac Lab task command targeting the humanoid base pose or whole-body end-effector. | Whole-body controller setpoint via the published Python interface. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on stock Berkeley Humanoid Lite (no documented gripper at time of writing). Manifest declares `gripper: none`; static verifier rejects programs that use these primitives on the platform's manifest. | Same. |
| `measure(sensor_id)` | Isaac Lab observation tensor sample. | IMU, joint-state, optional vision via the platform's Python interface. |
| `wait_for(...)` | Isaac Lab episode-level wait. | Polling loop with debounce on the named state. |
| `report(status)` | Isaac Lab episode info dict. | Append to a per-session log file plus stdout, mirroring `MockROSAdapter`. |
| `pose(posture_id)` (Layer-3 composition) | Pre-defined Isaac Lab posture target. | Whole-body controller posture setpoint. |

The crucial design observation: like Petoi ([RFC-0062](0062-petoi-bittle-outreach.md)) and unlike Trossen Interbotix ([RFC-0064](0064-trossen-interbotix-outreach.md)), Berkeley Humanoid Lite is **policy-trained motion**, not per-joint trajectory authoring. URML programs do not emit joint-target sequences; they emit posture and motion primitives, and the platform's trained policy plays them back. This matches the educational and research audience the platform targets.

### Proposed capability manifest

The two manifests live under `reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/manifests/`. A condensed shape for `berkeley_humanoid_lite_real`:

```yaml
brand: berkeley_humanoid_lite_real
profile: research
mobility: legged_bipedal
dof_total: 22  # approximate, per published 2025 design
mass_kg: 15.0  # approximate
height_m: 0.85  # approximate
transport: python_hardware_interface
python_interface:
  module: berkeley_humanoid_lite
  control_loop_hz: 200
gripper: none
controller: custom_isaac_trained
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `controller: custom_isaac_trained` value tells URML's validator that this manifest's motion is policy-driven, not trajectory-driven. The exact DOF / mass / height numbers are flagged for maintainer confirmation; URML records the approximate values to make the manifest concrete and asks for correction in the RFC.

### Proposed conformance integration

A `URML_BERKELEY_HUMANOID_INTEGRATION=1` env-gated CI workflow installs the platform's Python dependencies and Isaac Lab, runs `BerkeleyHumanoidLiteAdapter` in sim mode against a hermetic Isaac Lab task, and asserts that the emitted commands match a recorded golden trace. The in-tree conformance suite continues to use `MockROSAdapter`. A hardware-in-the-loop lane is out of scope for this RFC.

### Cross-link to RFC-0050 (Isaac Lab + GR00T)

The institutional alignment is real and worth surfacing explicitly. [RFC-0050](0050-nvidia-isaac-lab-integration.md) proposes URML as a substrate-neutral vocabulary above Isaac Lab. Berkeley Humanoid Lite ships Isaac Lab task definitions. A URML-aware Berkeley Humanoid Lite branch where Isaac Lab tasks consume URML primitive sequences closes the loop directly: train in URML-aware Isaac Lab sim, deploy on real Berkeley Humanoid Lite hardware via the same adapter family. This RFC observes the alignment; the actual cross-coordination is upstream feedback contingent.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/`. Not built in this PR. The RFC requests HybridRobotics maintainer feedback first.
- Conformance suite: proposed new `berkeley-humanoid-integration.yml` CI workflow and a `URML_BERKELEY_HUMANOID_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Berkeley Humanoid Lite gains nothing yet; the adapter consumes the published Python interface and Isaac Lab task definitions without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants HybridRobotics input on the sim-vs-real adapter split and on the policy-trained-motion primitive mapping before shipping.
- **The platform is too new for stable conventions.** A 2025 release means the Python interface, the Isaac Lab task definitions, and even the BOM are likely to evolve. URML's adapter takes on version-drift risk. Mitigation: pin to the platform's tagged releases, document the compatibility matrix.
- **The DOF / mass / dimensions are approximate.** URML's manifest needs these from the maintainers' authoritative spec; the RFC documents approximate values pending confirmation.
- **No gripper.** Programs written for stationary arms (Interbotix VX300S, WLKATA Haro380) cannot retarget to Berkeley Humanoid Lite without surgery. The same friction documented in [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) applies here.
- **3D-printed gearbox tolerance.** The platform's mechanical accuracy depends on the print quality and gearbox assembly. URML's `move_to` precision claims are bounded by this; the manifest's static-verification can declare a precision tolerance but cannot enforce print quality.
- **Sim-to-real gap inherent in policy-trained motion.** A URML program that validates in sim is not guaranteed to validate on real hardware, because the policy's real-hardware behaviour is the dependent variable. URML's static verifier checks the program against the manifest, not against the trained policy's actual closed-loop behaviour.

## Alternatives considered

1. **Ship the adapter first, ask HybridRobotics maintainers later.** Rejected. The sim-vs-real adapter split and the policy-trained-motion mapping are design choices worth maintainer input on.
2. **Target only the sim path; skip real hardware.** Rejected. The whole point of Berkeley Humanoid Lite for URML is the sim-to-real story; targeting only sim forfeits the engagement frame.
3. **Wait for Berkeley Humanoid Lite v2 before opening outreach.** Rejected. The current 2025 release is the right moment: too late forfeits the standard-setting opportunity; too early would block on instability the URML adapter can paper over.
4. **Fold Berkeley Humanoid Lite into [RFC-0050 (NVIDIA Isaac Lab)](0050-nvidia-isaac-lab-integration.md) as another sim deployment.** Rejected. The institutional audiences are distinct (NVIDIA Isaac team vs. UC Berkeley Hybrid Robotics Lab); the platform offers a real-hardware path that RFC-0050 alone does not.

## Prior art

- `HybridRobotics/Berkeley-Humanoid-Lite`: the upstream repository (1.3k stars, MIT code + CC-BY-SA 4.0 assets, Python 99.1%, Issues enabled with 8 open, "We wholeheartedly welcome contributions" stated).
- arXiv 2504.17249: the paper documenting the platform's design.
- UC Berkeley Hybrid Robotics Lab (Koushil Sreenath's group): the institutional home.
- Isaac Lab documentation at `isaac-sim.github.io/IsaacLab/`: the sim integration surface.
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-humanoid capability schema.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md): the whole-body manipulation Spec RFC (Draft).
- [RFC-0012](0012-research-profile.md): the URML research profile.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): the NVIDIA Isaac Lab Move #2 outreach; institutional cross-link.
- [RFC-0062](0062-petoi-bittle-outreach.md): the parallel Move #3 RFC for policy-driven motion at a different scale (Bittle quadruped).

## Unresolved questions

Provisional pending HybridRobotics maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/` (URML-side), under a new repo in the `HybridRobotics` org as a contributed example, or both?
2. **Sim-vs-real adapter split.** Two adapters (one per substrate) versus one adapter with a `mode:` parameter?
3. **Authoritative manifest values.** Could you confirm the DOF, mass, height, and control-loop frequency for the production design, so URML's manifest reflects ground truth?
4. **Policy-trained-motion primitive mapping.** Is the `move_to` → whole-body-setpoint mapping the right shape, or would HybridRobotics recommend a more explicit `posture()` / `gait()` Layer-3 vocabulary?
5. **Isaac Lab cross-coordination.** Is there interest in coordinating with URML's open RFC-0050 outreach to the NVIDIA Isaac team, given the platform's Isaac Lab task ecosystem?
6. **Hardware-in-the-loop lane.** What is the documented path for a URML conformance run on real hardware?
7. **Conformance lane on the README.** Open to a URML conformance line on the Berkeley Humanoid Lite README?
8. **Anything else.**

## Implementation note

RFC-0069 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/humanoid-runtime/src/humanoid_runtime/berkeley_humanoid_lite/` package follows in a later session, gated on HybridRobotics maintainer feedback. Draft state. Fifth Move #4 RFC. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from HybridRobotics maintainers)

1. Adapter home (URML repo, HybridRobotics contributed example, both).
2. Sim-vs-real adapter split.
3. Authoritative manifest values (DOF, mass, height, control-loop Hz).
4. Policy-trained-motion primitive mapping.
5. Isaac Lab cross-coordination.
6. Hardware-in-the-loop conformance path.
7. Conformance-lane interest on the README.
8. Anything else.

## How to respond

`HybridRobotics/Berkeley-Humanoid-Lite` has Issues enabled with 8 open at time of writing (verified 2026-05-24); the README explicitly welcomes contributions. URML's planned channel: open a single Issue on `HybridRobotics/Berkeley-Humanoid-Lite` labelled with the closest `enhancement` equivalent, pointing to this RFC.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the fifth Move #4 RFC).
- [x] Motivation grounded in verified technical alignment (1.3k stars MIT code + CC-BY-SA 4.0 assets on `HybridRobotics/Berkeley-Humanoid-Lite`, Python 99.1%, Isaac Lab task definitions shipping, arXiv 2504.17249, UC Berkeley Hybrid Robotics Lab institutional home) plus the frontier-open positioning.
- [x] Detailed design uses verified repo name and acknowledges approximate DOF / mass / height pending maintainer confirmation.
- [x] At least one alternative considered (four are: ship-first, sim-only, wait-for-v2, fold-into-RFC-0050).
- [x] Drawbacks are real (proposal-only, platform-too-new churn, approximate manifest values, no gripper, 3D-print tolerance, sim-to-real gap).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of `HybridRobotics/Berkeley-Humanoid-Lite` as of 2026-05-24.
- [x] Provenance row (`origin: US`) recorded; US-federal default policy passes without override.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
