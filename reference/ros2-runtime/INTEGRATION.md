# ROS 2 Integration — `RclpyAdapter`

**Status (v0.1):** Reference `RclpyAdapter` ships in `substrate/rclpy_adapter.py`. Unit tests with mocked rclpy run on every host (including Windows) as part of the default suite. Integration tests against a live ROS 2 + Gazebo stack are gated to a separate Linux-only CI workflow — see `.github/workflows/ros2-integration.yml`.

This document is the blueprint for the adapter. It records the surface area, the per-method ROS 2 mapping, the testing strategy, the configuration surface, and the open design questions.

---

## Development environment

The reference adapter is developed and integration-tested on **WSL2 + ROS 2 Jazzy** (current LTS as of 2026). Specifically:

- Windows 10/11 host with WSL2 enabled.
- Ubuntu 24.04 LTS image.
- ROS 2 Jazzy desktop install (`ros-jazzy-desktop`).
- Nav2 (`ros-jazzy-nav2-bringup`), MoveIt 2 (`ros-jazzy-moveit`), and Gazebo Harmonic for integration tests.
- Python `>=3.11` from the system Python (matches the URML packages' minimum).

This is the recommended path because (a) it works on the author's primary development host without a dual-boot or a separate machine, (b) ROS 2 Linux support is first-class and Windows support is not, (c) WSL2's networking is fast enough for the action client patterns the adapter uses.

Alternatives that also work: a Linux-native dev box, a devcontainer pinned to `osrf/ros:jazzy-desktop`, or a cloud Linux VM with X forwarding for the Gazebo GUI. The adapter code itself is OS-agnostic — only the ROS 2 install isn't.

---

## What the adapter must implement

The `ROSAdapter` Protocol is in [`src/urml_ros2_runtime/substrate/base.py`](src/urml_ros2_runtime/substrate/base.py). Every method maps to one URML primitive's dispatch step. Implementations:

- Must return a typed result (`NavigationResult`, `DetectionResult`, etc.) with a `success: bool` and an optional `reason: str`.
- Must NOT raise on robot-side failures — failures are *returned* in `success=False`, not thrown. The runtime maps them to its on-error policy.
- May raise on unrecoverable errors (the substrate process died, the network broke). The runtime wraps those into `PrimitiveExecutionError`.

The methods:

| Adapter method | URML primitives | ROS 2 mapping |
|---|---|---|
| `send_navigation_goal` | `move_to`, `hover` (location-mode) | Nav2 `NavigateToPose` action; for arm motion, MoveIt 2 `MoveGroup` action |
| `send_docking_goal` | `dock` | Nav2 `DockRobot` action (Iron+); for older distros, a custom action wrapping Nav2's docking server |
| `send_manipulation_goal` | `grasp`, `release` | MoveIt 2 + gripper action server (per-gripper, e.g., `parallel_gripper_action_controller`) |
| `query_detection` | `detect` | Subscribe to a configured perception topic (e.g., `vision_msgs/Detection2DArray`) and resolve a single match. Default suggestion: `vision_msgs` with the URML-validator's `Identifier`-typed object classes as filter |
| `run_scan` | `scan` | Nav2 path-following along a generated pattern with per-waypoint perception triggers. The pattern → waypoint expansion happens *inside* the adapter, not in URML |
| `take_measurement` | `measure` | Subscribe to a configured sensor topic; take one message; return |
| `capture_media` | `capture` | `image_transport` for photos; `rosbag2` (or a configured external sink) for video |
| `wait_for_condition` | `wait_for` | Subscribe to the relevant topic / service with a predicate matcher. For `condition.input: speech`, route through the LLM-bridge speech path |
| `wait_passively` | `wait` | A `rclpy.sleep_for` equivalent or a no-op timer node, depending on whether the robot needs to remain active |
| `emit_report` | `report` | Publish to a configured topic with a structured message. For `to: user`, route through the LLM-bridge response path |
| `emit_speech` (home profile) | `speak` | Publish to a TTS node (e.g., `audio_common` + Festival/Mimic, or a vendor TTS service) |
| `acquire_speech` (home profile) | `listen` | Subscribe to an STT node's transcription topic with `expected: choice|confirmation|free_form` mapping the result |

Drone-profile methods (PR #30 added validator support; runtime executor work is the parallel follow-up):

| Adapter method (future) | URML primitives | PX4 / MAVLink mapping |
|---|---|---|
| `send_takeoff_goal` | `take_off` | `MAV_CMD_NAV_TAKEOFF` via `mavros/cmd/takeoff` service |
| `send_land_goal` | `land` | `MAV_CMD_NAV_LAND` (or `_LAND_LOCAL`) via `mavros/cmd/land` |
| `send_return_to_home_goal` | `return_to_home` | `MAV_CMD_NAV_RETURN_TO_LAUNCH` via `mavros/cmd/return_to_launch` |

The PX4-side belongs in `reference/px4-runtime/` (which doesn't exist yet; Phase 2 target per the manifesto). The ROS 2 adapter could wrap these too if rclpy is paired with mavros, but the cleaner split is two separate reference runtimes.

---

## Where the code lives

- **Adapter:** [`src/urml_ros2_runtime/substrate/rclpy_adapter.py`](src/urml_ros2_runtime/substrate/rclpy_adapter.py) — `RclpyAdapter` class, all 12 ROSAdapter Protocol methods.
- **Config:** [`src/urml_ros2_runtime/substrate/adapter_config.py`](src/urml_ros2_runtime/substrate/adapter_config.py) — `AdapterConfig` pydantic model + `load_adapter_config` YAML loader.
- **Unit tests (hermetic, mocked rclpy):** [`tests/test_rclpy_adapter.py`](tests/test_rclpy_adapter.py) — runs on every host without ROS 2 installed.
- **Integration tests (gated, real ROS 2):** [`tests/integration/test_rclpy_adapter_live.py`](tests/integration/test_rclpy_adapter_live.py) — runs only under `ROS2_INTEGRATION=1` in CI on the Linux ROS 2 runner.

rclpy itself is *not* in `dependencies`; it's an optional extra (`pip install urml-ros2-runtime[ros2]`) because the rclpy wheel is unusual (ships with the ROS 2 distribution rather than PyPI in practice). The adapter imports rclpy lazily at construction time and raises a clear error if it's missing.

---

## Configuration surface (deployment-provided)

The adapter needs a deployment-provided config to know:

- Which ROS 2 namespace to use (default: empty / root).
- Which Nav2 action server to call (default: `/navigate_to_pose`).
- Which MoveIt 2 group to use for arm motion (default: `panda_arm` or `manipulator`).
- Which perception topic to subscribe to (default: `/vision_msgs/detections`).
- Which TTS / STT topic to use (no default; home-profile only).
- Per-station location → pose mapping (the validator resolves names; the adapter resolves the named pose against the actual world).
- Per-gripper action client mapping.

Suggested format: a single `adapter.yaml` next to the manifest, loaded at adapter construction.

```yaml
# adapter.yaml — example
ros2_namespace: ""
action_servers:
  navigate_to_pose: /navigate_to_pose
  move_group: /move_action
  gripper:
    claw_demo: /gripper_controller/follow_joint_trajectory
location_to_pose:
  kitchen: { x: 3.2, y: 1.0, frame: map }
  user:    { x: 0.5, y: 0.5, frame: map }
perception:
  detection_topic: /vision_msgs/detections
speech:
  output_topic: /tts/utter
  input_topic:  /stt/transcription
```

This format is NOT normative URML — the adapter is free to use a different shape. But the v0.1 reference adapter ships with this format documented.

---

## Testing strategy

Two layers:

### 1. Unit tests with rclpy mocks

Replace the action clients with mocks; assert that `send_navigation_goal` sends the right Nav2 message, parses the right Nav2 response. ~30 tests for the full surface. No ROS 2 environment required for these.

### 2. Integration tests with Gazebo simulator

A pinned Gazebo + TurtleBot 4 simulator stack. Eventually every navigation-compatible conformance fixture runs through `RclpyAdapter` against the simulated robot instead of `MockROSAdapter`. Fixtures that pass against the mock should pass against the simulator (modulo nondeterminism for things like timing — see *Open questions* §3).

CI gating: the `gazebo-e2e` job in [`.github/workflows/ros2-integration.yml`](../../.github/workflows/ros2-integration.yml). Manual-dispatch + weekly cron only — never per-push. It uploads sim/Nav2/pytest logs as artifacts on `always()`, so a failed run is diagnosable rather than opaque.

**What runs end-to-end today:** [`tests/integration/test_nav_patrol_gazebo_e2e.py`](tests/integration/test_nav_patrol_gazebo_e2e.py) takes the `home/nav_patrol_positive` fixture (three plain `move_to` goals) and runs it through the *same* `ConformanceRunner` the hermetic suite uses, with `adapter_factory` wired to a live `RclpyAdapter`. This closes the full loop: URML program → validator → ConformanceRunner → RclpyAdapter → Nav2 → a simulated TurtleBot 4 that actually drives. A stock TB4 sim only exposes Nav2 navigation (its dock is iRobot Create 3's `/dock`, not Nav2 `DockRobot`; no gripper/camera), so the navigation slice is what's covered; perception/manipulation/docking e2e need a richer sim and are tracked as follow-ups below.

#### Local repro (WSL2 + ROS 2 Jazzy)

```bash
# In WSL2 Ubuntu 24.04 with ROS 2 Jazzy installed:
sudo apt-get install -y ros-jazzy-turtlebot4-simulator \
  ros-jazzy-turtlebot4-navigation ros-jazzy-nav2-bringup

# Terminal 1 — bring up the sim + Nav2 (headless; drop headless:=true for the GUI):
source /opt/ros/jazzy/setup.bash
export LIBGL_ALWAYS_SOFTWARE=1   # only needed on a GPU-less box
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py \
  nav2:=true slam:=true rviz:=false headless:=true

# Terminal 2 — once /navigate_to_pose is up, run the e2e:
source /opt/ros/jazzy/setup.bash
cd reference/ros2-runtime
URML_GAZEBO_E2E=1 python3 -m pytest tests/integration/test_nav_patrol_gazebo_e2e.py -v
```

The adapter↔world pose mapping lives in [`tests/integration/adapter_nav_patrol.yaml`](tests/integration/adapter_nav_patrol.yaml). If you run a non-default world, edit `location_to_pose` to match — that file *is* the deployment boundary the design intends.

> The CI launch invocations were authored without a Gazebo-capable host. Package and launch-file names follow current TurtleBot 4 / Jazzy docs, but the first real `gazebo-e2e` run is a **calibration run**: if a launch arg or package name differs on the installed TB4 version, the uploaded artifacts show exactly what to pin. Treat the first run's result as setup feedback, not a regression.

---

## Open questions

1. **Which ROS 2 distros?** Jazzy LTS is the most likely first target (current LTS as of 2026). Humble may also be supported. Older distros (Foxy, Galactic) are EOL; not supported.

2. **rclpy vs. rcl/raw bindings.** rclpy is the obvious choice for the reference adapter. A future high-performance adapter might use `rcl` C bindings directly; out of scope here.

3. **Action timing and the validator's static checks.** The validator says "this program can be executed against this manifest." It does NOT say "this program will complete in N seconds." A real robot's action might time out or stall. The adapter's contract is: return `success: True` only when the action completes; return `success: False` with `reason: "timed_out"` if the substrate timed it out. The runtime's `on_error` policy decides what happens next. This is the same contract `MockROSAdapter` follows.

4. **Live-state queries.** Some primitives might want to read live robot state (current battery level for `wait_for(condition.sensor_threshold)`, etc.). The Protocol covers this through `take_measurement` and `wait_for_condition`. A future RFC may extend.

5. **Multi-robot deployments.** v0.1 assumes one adapter ↔ one robot. Fleet management (one URML program orchestrating multiple robots) is a separate concern, likely a future profile or a fleet-manager layer above the runtime.

6. **PX4 / mavros integration in the same adapter.** The cleaner split is two separate reference runtimes (`reference/ros2-runtime` for ROS 2 / Nav2; `reference/px4-runtime` for PX4 / MAVLink). But many drone projects pair them — Nav2 + mavros at the same time. A flexible adapter might support both, configured via the adapter.yaml. Open question; doesn't block the v0.1 home-profile ROS 2 adapter.

---

## Implementation phases

When this work starts (Phase 1+):

**Phase 1**: Skeleton + navigation only.
- `RclpyAdapter` class with construction; rclpy lazy import.
- `send_navigation_goal` against Nav2.
- Adapter.yaml schema (proposed above) + a config loader.
- Unit tests with mocked rclpy.
- Integration test on a Gazebo TurtleBot navigating to a fixed pose.

**Phase 2**: Manipulation.
- `send_manipulation_goal` against MoveIt 2 + a gripper action.
- Gripper config in adapter.yaml.
- Unit + integration tests.

**Phase 3**: Perception.
- `query_detection`, `run_scan`, `take_measurement`, `capture_media`.
- Subscriptions to configurable topics.
- Test fixtures with mocked perception output.

**Phase 4**: Home-profile speech.
- `emit_speech` + `acquire_speech`.
- Adapter.yaml gains speech topics.
- An end-to-end Gazebo + TTS/STT integration test, if a deployable TTS/STT stack is reasonably available.

**Phase 5**: Drone primitives (only if the same adapter handles PX4-via-mavros).
- `send_takeoff_goal` / `send_land_goal` / `send_return_to_home_goal` via `mavros/cmd/*`.
- More likely: a separate `reference/px4-runtime` package owning these. Decision deferred.

---

## What this doc is NOT

- **Not a tutorial.** Once the implementation exists, a tutorial walks through running it locally. This doc is for the implementer, not the user.
- **Not a commitment to ROS 2 only.** URML's Protocol is substrate-neutral by design. Other adapters (PX4, OPC UA, vendor SDKs) implement the same surface and have their own integration docs.
- **Not normative.** The adapter is reference code, not part of the URML specification. Conformance is judged against the fixture suite, not against this implementation.

---

## Related documents

- [`src/urml_ros2_runtime/substrate/base.py`](src/urml_ros2_runtime/substrate/base.py) — the Protocol the adapter implements.
- [`src/urml_ros2_runtime/substrate/mock.py`](src/urml_ros2_runtime/substrate/mock.py) — the hermetic mock that ships in v0.1.
- [`/conformance/`](../../conformance/) — the declarative fixtures that any adapter must satisfy.
- [`/docs/rfcs/0002-initial-primitive-vocabulary.md`](../../docs/rfcs/0002-initial-primitive-vocabulary.md) §Appendix A — per-primitive ROS 2 implementation sketches (and non-ROS sketches for PX4 / OPC UA / KUKA / ABB / IEC 61131-3).
- [`/MANIFESTO.md`](../../MANIFESTO.md) §Roadmap Snapshot — when ROS 2 + PX4 reference runtimes are scheduled.
