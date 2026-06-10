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

This page has two parts: the **first-party reference runtimes** the URML project
maintains and verifies in-repo, and a **self-reported registry** for third-party
runtimes. Neither is a certification. URML does not certify, audit, or endorse
listed runtimes; the `URML-Certified` mark is a separate, future program (Phase
4) and is not in use today. See [TRADEMARK.md](../TRADEMARK.md) for what a listing
does and does not grant.

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
| [`edu-runtime`](../reference/edu-runtime/) | Educational platforms | VEX / LEGO SPIKE / Thymio / Robotical Marty / Petoi / CircuitPython. |
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

## Third-party registry (self-reported)

For runtimes maintained outside the URML project. Listing is **self-reported**:
the maintainer ran the conformance suite and submitted the result; URML does not
audit it. Open a PR following [docs/registry/SUBMISSION.md](registry/SUBMISSION.md),
five steps and one PR. The registry is free and opt-in.

<!-- Add new entries below this comment, one row per runtime. -->

| Runtime | Maintainer | Substrate | Spec versions | Conformance report | License | Last-verified commit |
| ------- | ---------- | --------- | ------------- | ------------------ | ------- | -------------------- |

_No third-party entries yet. Be the first by following [SUBMISSION.md](registry/SUBMISSION.md)._

### How to read the third-party table

- **Runtime**: the project name, linked to its repository.
- **Maintainer**: the org or person who submitted and maintains the listing.
- **Substrate**: what URML compiles down to in this runtime (ROS 2, PX4, vendor SDK, etc.).
- **Spec versions**: declared coverage. Per-layer semver, e.g. `layer-2: 0.1.0, layer-3: 0.1.0, profiles: home/0.1.0`.
- **Conformance report**: link to the JSON report produced by `urml conformance run --output`, hosted in the runtime's own repository at a pinned commit.
- **License**: the runtime's license. URML is Apache 2.0; listed runtimes may use any OSI-approved license.
- **Last-verified commit**: the runtime commit hash at which the report was produced.

## Delisting

A third-party runtime is delisted if any of the following happens:

- The maintainer requests removal (open a PR removing the row).
- A bumped version of the spec invalidates the prior report and no updated report is filed within 90 days.
- The trademark policy in [TRADEMARK.md](../TRADEMARK.md) is materially violated by the maintainer.

Delisting is recorded in the PR removing the row, so the history is auditable in git.
