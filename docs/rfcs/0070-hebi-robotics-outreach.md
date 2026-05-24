---
rfc: 0070
title: HEBI Robotics integration, request for comment from HebiRobotics maintainers
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

# RFC-0070: HEBI Robotics integration, request for comment from HebiRobotics maintainers

## Summary

URML does not yet ship a HEBI integration. This RFC proposes a `HebiAdapter` under [`reference/cobot-runtime/`](../../reference/cobot-runtime/) targeting the [`HebiRobotics` GitHub org](https://github.com/HebiRobotics) published surfaces: `hebi-python-examples`, `hebi-cpp-examples`, `hebi_ros2_examples`, `hebi_description`, `hebi_msgs`, `hebi_cpp_api_ros` (all Apache-2.0). The adapter routes URML Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile extensions ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`) onto HEBI's modular X-Series and R-Series actuators via the HEBI C++ API plus the ROS 2 message and description packages. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the HebiRobotics maintainers.

This is the sixth and final Move #4 RFC. HEBI Robotics anchors **modular research robotics** in the Move #4 sweep: a CMU-rooted US vendor selling Series Elastic Actuator modules that customers compose into custom arm and quadruped geometries, with a research-tier audience that is distinctly different from Move #3's Trossen Interbotix X-Series (fixed-geometry arms).

## Motivation

HEBI's distinctive value proposition for URML is **per-deployment kinematic modularity**. A HEBI customer at a research lab assembles actuators into a custom robot geometry (a five-DOF arm for one experiment, a seven-DOF arm for another, a four-leg quadruped for a third), and the same software stack drives all configurations. URML's capability manifest is the natural vocabulary for declaring those custom geometries: the manifest declares the kinematic chain, the joint limits, the actuator capabilities, and URML's static verifier reasons about programs against the declared geometry. No other URML outreach target offers this composability story.

Three things make this RFC concrete rather than aspirational. First, the `HebiRobotics` org publishes 46 public repos with Apache-2.0 predominant: `hebi-python-examples` (14 stars), `hebi-cpp-examples` (9 stars), `hebi-matlab-examples` (22 stars), `hebi-cad` (9 stars), plus the ROS 2 packages `hebi_ros2_examples`, `hebi_description`, `hebi_msgs`, `hebi_cpp_api_ros`. The star counts are small but the user base is the right one: research institutions and the Robotarium at Georgia Tech. Second, HEBI's actuators expose a unified Python / C++ / MATLAB API surface across X-Series (X-5, X-8 series) and R-Series, so URML's adapter has one programming surface to wrap regardless of which kinematic configuration the customer assembled. Third, HEBI is CMU-rooted (spun out of the CMU Robotics Institute), so the institutional credibility lands in URML's research-tier audience naturally.

HEBI's posture is open ROS 2 examples (BSD / Apache-2.0) plus a proprietary actuator-firmware stack. The URML adapter consumes the public API and example code without proposing changes to the firmware. HEBI is US-domiciled (Pittsburgh, PA); URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level without override.

## Detailed design

URML's existing artifacts that feed into a HEBI adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the natural home for HEBI deployments.
- [`spec/profiles/industrial/`](../../spec/profiles/industrial/) plus [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile extensions for the manipulator configurations.
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability surface for the quadruped configurations (the Igor and Rosie example kits).
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime that hosts arm-style adapters today.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `HebiAdapter` shape

One adapter, parameterised by the customer's assembled kinematic configuration. Unlike fixed-geometry targets (Interbotix, WLKATA), HEBI requires the customer to declare the geometry in their URML manifest; the adapter does not ship with a fixed list of pre-defined manifests. Package layout:

```
reference/cobot-runtime/src/cobot_runtime/hebi/
├── __init__.py
├── adapter.py             # HebiAdapter (geometry from manifest)
├── kinematics.py          # builds a URDF / kinematic chain from the manifest declaration
├── api_bindings.py        # HEBI C++ API bindings via the published Python wrapper
└── manifests/
    ├── hebi_x_series_5dof_example.yaml   # example, not an authoritative product manifest
    ├── hebi_x_series_7dof_example.yaml
    ├── hebi_igor_balancing_example.yaml  # example for the 14-DoF Igor kit
    └── hebi_rosie_double_shoulder_example.yaml
```

The four example manifests are starting points; the customer-side URML deployment writes a manifest matching the specific actuator configuration they assembled. The adapter implements URML's substrate Protocol against the HEBI C++ API.

### Proposed URML v0.1 to HEBI mapping

| URML primitive | HEBI realisation |
|---|---|
| `move_to(pose)` | A joint-target or end-effector-pose command via the HEBI `Group.send_command()` API, parameterised by the manifest-declared kinematic chain. URML's static verifier checks the pose against the declared joint limits before dispatch. |
| `grasp(gripper_id)` / `release(gripper_id)` | If the manifest declares a gripper actuator (or an external gripper service), grasp / release dispatch to its position-control surface. Standard HEBI actuators are not grippers; gripper integration is per-deployment. |
| `measure(sensor_id)` | A `Group.get_feedback()` call on the named actuator's IMU, position, velocity, or torque feedback. HEBI actuators expose all of these natively. |
| `wait_for(...)` | A polling loop on `get_feedback()` with debounce and timeout, or (if a ROS 2 deployment) a subscriber on the named topic. |
| `report(status)` | Append to a per-session log file plus stdout. Optional ROS 2 publish to `/urml/<adapter>/report` if a ROS bridge is loaded. |
| `pick_from(source)` / `place_at(destination)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Layer-3 composition over `move_to` plus `grasp` / `release`, contingent on a gripper being declared in the manifest. |
| `swap_tool(tool_id)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Composes onto a docking-goal sequence if a tool-changer is declared. |

### Proposed capability manifest

The example manifests live under `reference/cobot-runtime/src/cobot_runtime/hebi/manifests/`. The shape is more declarative than other URML manifests because the customer declares the kinematic chain themselves. A condensed shape for a 5-DOF X-Series arm example:

```yaml
brand: hebi_x_series_5dof_example
profile: research
arm:
  dof: 5
  kinematic_chain:
    - actuator: X-8-9
      link_length_m: 0.0
      axis: z
    - actuator: X-8-9
      link_length_m: 0.325
      axis: y
    - actuator: X-8-9
      link_length_m: 0.325
      axis: y
    - actuator: X-5-9
      link_length_m: 0.175
      axis: y
    - actuator: X-5-4
      link_length_m: 0.105
      axis: x
  end_effector: none
transport: hebi_api
hebi_api:
  group_name: User-Defined
  python_module: hebi
  cpp_lib: hebi-cpp-api
ros2_bridge_optional:
  package: HebiRobotics/hebi_ros2_examples
gripper: none
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `kinematic_chain` declaration is the new shape. URML's manifest schema supports a generic chain declaration; HEBI is the first target where every customer writes their own. The example manifests document the pattern; the production manifests are written by the deploying organisation.

### Proposed conformance integration

A `URML_HEBI_INTEGRATION=1` env-gated CI workflow installs the HEBI Python API (a pip-installable wheel from `pypi.org/project/hebi-py`), runs `HebiAdapter` against a hermetic mock that replays group-feedback responses, and asserts that the emitted commands match a recorded golden trace for each example manifest. The in-tree conformance suite continues to use `MockROSAdapter`.

### Cross-link to URML's industrial profile

[RFC-0013 (industrial-profile Layer-2 primitives)](0013-industrial-layer2-primitives.md) defined `pick_from`, `place_at`, and `swap_tool` against fixed-geometry industrial arms. HEBI's modular configurations exercise these primitives against geometries that URML's existing adapter family does not ship. A HEBI conformance lane validates the industrial-profile primitives' substrate-neutrality claim against a geometry URML has never targeted before.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The `kinematic_chain` field in the manifest already exists in URML's research-profile schema; HEBI is the first deployment that fully populates it.
- Reference runtime: proposed new sub-package `reference/cobot-runtime/src/cobot_runtime/hebi/`. Not built in this PR. The RFC requests HebiRobotics maintainer feedback first.
- Conformance suite: proposed new `hebi-integration.yml` CI workflow and a `URML_HEBI_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. HEBI gains nothing yet; the adapter consumes the published Python / C++ / ROS 2 surface without proposing changes to it.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants HebiRobotics input on the per-customer kinematic-chain manifest shape and on the recommended ROS 2 bridge mode before shipping.
- **Per-customer manifests shift authoring burden onto the user.** Fixed-geometry vendors (Interbotix, WLKATA) ship per-product manifests; HEBI's modularity means the URML manifest is partly user-authored. This is the right shape but the documentation burden is real.
- **Small public-facing footprint.** The org's star counts are modest (22 / 14 / 9 across MATLAB / Python / C++ examples). HEBI's user base is concentrated in research institutions with direct sales relationships; the GitHub footprint understates the actual deployment count.
- **Multiple language surfaces.** Python, C++, and MATLAB are all first-class HEBI surfaces. URML's adapter prioritises Python; the C++ binding layer is available; MATLAB is out of scope. The choice forfeits the MATLAB-only research deployments.
- **No fixed product manifests.** Unlike every other URML adapter target, HEBI ships no canonical product. The four example manifests in the proposal are illustrative; production manifests are per-deployment. This is honest but breaks the "demo against a known reference" testing pattern URML uses elsewhere.

## Alternatives considered

1. **Ship the adapter first, ask HebiRobotics maintainers later.** Rejected. The per-customer manifest shape is a design choice with user-visible documentation consequences; a pre-RFC saves rework.
2. **Ship pre-defined manifests for the Igor and Rosie example kits only and skip the modular composition.** Rejected. The modularity is what makes HEBI distinctive for URML; restricting to two kits forfeits the value proposition.
3. **Fold HEBI into [RFC-0064 (Trossen Interbotix)](0064-trossen-interbotix-outreach.md) as another stationary-arm vendor.** Rejected. The audiences and product models are different (Trossen is fixed-geometry production arms with Dynamixel servos; HEBI is modular Series Elastic Actuators); collapsing them forfeits the modularity story.
4. **Target only ROS 2 deployments; skip the direct HEBI API path.** Rejected. Many HEBI deployments do not run ROS 2 (the platform is API-first); skipping the direct path would forfeit the research-lab use case.

## Prior art

- `HebiRobotics` org (46 public repos, 35 followers).
- `HebiRobotics/hebi-python-examples` (14 stars), `hebi-cpp-examples` (9 stars), `hebi-matlab-examples` (22 stars): the canonical API example surface.
- `HebiRobotics/hebi-cad` (9 stars): CAD files and meshes.
- `HebiRobotics/hebi_ros2_examples`, `hebi_description`, `hebi_msgs`, `hebi_cpp_api_ros`: the ROS 2 packages.
- HEBI documentation at `docs.hebi.us`: the canonical product reference.
- HEBI's Igor (14-DoF self-balancing kit) and Rosie (7-DoF double-shoulder kit): the example kits.
- Robotarium at Georgia Tech (`robotarium.gatech.edu`): a documented HEBI deployment.
- [RFC-0009](0009-legged-humanoid-mobility.md): the capability-manifest schema.
- [RFC-0012](0012-research-profile.md): the URML research profile.
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives the HEBI adapter exercises.
- [RFC-0064](0064-trossen-interbotix-outreach.md): the parallel fixed-geometry-arm Move #3 RFC.

## Unresolved questions

Provisional pending HebiRobotics maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/cobot-runtime/src/cobot_runtime/hebi/` (URML-side), under a new repo in the `HebiRobotics` org as a contributed example, or both?
2. **Kinematic-chain manifest shape.** Is the URML manifest's `kinematic_chain` declaration the right shape for per-customer configurations, or would HEBI recommend a different vocabulary (URDF reference, MoveIt config import)?
3. **Example manifests.** Are the proposed examples (5-DoF X-Series arm, 7-DoF X-Series arm, Igor balancing kit, Rosie double-shoulder) the right starting set, or are there other canonical configurations URML should document?
4. **ROS 2 bridge default.** Should URML's adapter default to direct HEBI API calls or to the ROS 2 bridge for deployments that have ROS 2 loaded?
5. **MATLAB surface.** Is the MATLAB-only deployment population large enough that URML should expose a MATLAB-facing adapter, or is Python sufficient?
6. **Robotarium cross-link.** Is there interest in coordinating with Robotarium @ Georgia Tech for a documented URML conformance deployment?
7. **Conformance lane.** Open to a URML conformance line in the HEBI documentation site or in `hebi_ros2_examples` README?
8. **Anything else.**

## Implementation note

RFC-0070 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/cobot-runtime/src/cobot_runtime/hebi/` package follows in a later session, gated on HebiRobotics maintainer feedback. Draft state. Sixth Move #4 RFC; closes the Move #4 pilot batch. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from HebiRobotics maintainers)

1. Adapter home (URML repo, HebiRobotics contributed example, both).
2. Kinematic-chain manifest shape.
3. Example manifest set.
4. ROS 2 vs direct-API default.
5. MATLAB-surface scope.
6. Robotarium cross-link.
7. Conformance-lane interest.
8. Anything else.

## How to respond

`HebiRobotics` org has 46 public repos (verified 2026-05-24); per-repo Issue / Discussion settings were not visible from the org landing page. The most-active customer-facing repo is `hebi-python-examples` (14 stars). URML's planned channel: open a single Issue on `HebiRobotics/hebi-python-examples` or `HebiRobotics/hebi_ros2_examples` (whichever maintainers prefer) labelled with the closest `enhancement` equivalent, pointing to this RFC.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the sixth and final Move #4 RFC).
- [x] Motivation grounded in verified technical alignment (`HebiRobotics` org 46 public repos with Apache-2.0 predominant, Series Elastic Actuator modular hardware, Python / C++ / MATLAB API surfaces, Robotarium @ Georgia Tech documented deployment, CMU lineage) plus the modular-research positioning.
- [x] Detailed design uses verified repo names (`hebi-python-examples`, `hebi-cpp-examples`, `hebi-matlab-examples`, `hebi-cad`, `hebi_ros2_examples`, `hebi_description`, `hebi_msgs`, `hebi_cpp_api_ros`).
- [x] At least one alternative considered (four are: ship-first, kit-manifests-only, fold-into-Trossen, ROS-2-only).
- [x] Drawbacks are real (proposal-only, per-customer manifest burden, small public footprint, multi-language complexity, no canonical product manifests).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The `kinematic_chain` field is already in the manifest schema; HEBI is the first deployment that fully populates it.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the `HebiRobotics` GitHub org as of 2026-05-24.
- [x] Provenance row (`origin: US`) recorded; US-federal default policy passes without override.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
