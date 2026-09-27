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

# Compatible Runtimes

A runtime is **URML-compatible** when it accepts a Layer-1 capability manifest,
executes only statically-validated programs, needs no cloud, and passes the
public [conformance suite](../conformance/) for the profiles it claims. The
normative contract is [RFC-0014](rfcs/0014-substrate-conformance.md).

This page lists the **first-party reference runtimes** the URML project
maintains and verifies in-repo. Robots and runtimes maintained outside the
project, and the evidence behind each one, are in the
[URML registry](../registry/README.md). Neither list grants a mark or says
anything about fitness for a purpose, and the `URML-Certified` mark is reserved
for a separate, future program (Phase 4) that is not in use today. See
[TRADEMARK.md](../TRADEMARK.md) for what a listing does and does not grant.

If you make **robots or parts** rather than runtimes, the parallel surface is the
[Manufacturer & Product Directory](manufacturers/directory.md).

## URML reference runtimes (first-party)

Maintained by the URML project and verified by the in-repo conformance suite
(`conformance/`), run hermetically against `MockROSAdapter` and
adapter-agnostically against each runtime. All are Apache-2.0. "Live e2e" against
real hardware or a real simulator is gated CI, calibration-staged, and **not** a
hardware claim; see the [claims audit](launch/claims-audit.md).

| Runtime | Substrate | Notes |
| ------- | --------- | ----- |
| [`ros2-runtime`](../reference/ros2-runtime/) | ROS 2 (`rclpy`) + the mock | The reference Protocol implementation; the mock backs the conformance suite. |
| [`px4-runtime`](../reference/px4-runtime/) | PX4 / MAVLink (`pymavlink`, no ROS) | Full Protocol with zero ROS dependency. |
| [`ardupilot-runtime`](../reference/ardupilot-runtime/) | ArduPilot ArduCopter / MAVLink (`pymavlink`, no ROS) | Bench run on a Pixhawk-class board, propellers off, and a local ArduCopter SITL run, both 2026-08-29; no flight claimed. In the [registry](../registry/entries/ardupilot-arducopter-pixhawk.yaml). |
| [`marine-runtime`](../reference/marine-runtime/) | BlueROV2 / ArduSub (MAVLink) | The zero-ROS underwater sibling. |
| [`opcua-runtime`](../reference/opcua-runtime/) | OPC UA Robotics (zero ROS) | Factory-floor companion spec via `asyncua`. |
| [`mujoco-runtime`](../reference/mujoco-runtime/) | MuJoCo simulator (zero ROS) | The purest substrate-neutrality proof: a sim with no robot, no middleware. |
| [`isaac-runtime`](../reference/isaac-runtime/) | NVIDIA Isaac Sim / Lab | RTX-host simulator substrate. |
| [`chrono-runtime`](../reference/chrono-runtime/) | Project Chrono (PyChrono) | High-fidelity multibody **validation**; primitive to driver-input, dynamics as evidence (RFC-0328). |
| [`industrial-arm-runtime`](../reference/industrial-arm-runtime/) | ROS 2 + MoveIt 2 | 16 arm brands (ABB / FANUC / KUKA / Yaskawa / UR / Franka / Kawasaki / Stäubli / Comau / Mitsubishi / Denso / Hyundai / Nachi / Epson / Omron / Hanwha). |
| [`cobot-runtime`](../reference/cobot-runtime/) | Vendor cobot SDKs (zero ROS) | 8 brands (UR / Franka / Doosan / Techman / Kinova / Mecademic / Neura / Kassow) native SDKs. |
| [`legged-runtime`](../reference/legged-runtime/) | Quadruped platforms | Spot / ANYmal. |
| [`humanoid-runtime`](../reference/humanoid-runtime/) | Biped / humanoid platforms | Digit-class. |
| [`mobile-runtime`](../reference/mobile-runtime/) | Ground AMRs | Husky / Jackal. |
| [`edu-runtime`](../reference/edu-runtime/) | Educational platforms | VEX / LEGO SPIKE / Thymio / Robotical Marty / Petoi / CircuitPython / Microduck. |
| [`embedded-runtime`](../reference/embedded-runtime/) | MCU serial | micro:bit / Arduino-class nodes. |
| [`autosar-runtime`](../reference/autosar-runtime/) | AUTOSAR Adaptive | Scaffold (RFC-0019). |

## Integration examples

Worked examples that **validate** URML intent first, then map it onto a specific
target's existing interfaces. Hermetic and deterministic (pure stdlib + the
validator, no robot needed to produce the artifact); each is byte-asserted in CI.

| Example | Target | What it shows |
| ------- | ------ | ------------- |
| [`examples/scenario/`](../examples/scenario/) | ASAM OpenSCENARIO / esmini | Navigation intent to an OpenSCENARIO `.xosc` with the URML agent as the controlled entity. |
| [`examples/manipulation/kortex/`](../examples/manipulation/kortex/) | Kinova `ros2_kortex` | Manipulation intent to the Kortex action / gripper interfaces; an over-rating grasp is rejected before any goal. |
| [`examples/fleet/crazyswarm2/`](../examples/fleet/crazyswarm2/) | Crazyswarm2 | One fleet intent to per-UAV services; a deconfliction conflict is rejected before any command. |

The upstream side of this is open too: URML has contributed a small
`capability_manifest` passthrough to [`Denys88/rl_games`](https://github.com/Denys88/rl_games)
(a maintainer-invited PR) so a trained policy's capability declaration can travel
with its checkpoint.

## Third-party runtimes and robots: the registry

Runtimes and robots maintained outside the URML project are listed in the
[URML registry](../registry/README.md), one YAML entry per robot, each with its
evidence and its limits. A runtime's self-reported URML-compatible claim lives
there as a conformance report produced with the runtime's own adapter
(`urml conformance run --adapter module:attr --output report.json`), which a
checker verifies in CI. Submitting is one pull request: see
[docs/registry/SUBMISSION.md](registry/SUBMISSION.md). The registry is free and
opt-in, and an entry is withdrawn by setting `status: withdrawn`.
