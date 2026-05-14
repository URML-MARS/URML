# ROS 2 Integration — design notes for the real `RclpyAdapter`

**Status:** Design only. v0.1 ships `MockROSAdapter` (in `substrate/mock.py`). A real `rclpy`-backed adapter is Phase 1+ work.

This document is what someone with a working ROS 2 environment needs in order to implement the real adapter. It records the surface area, the per-method ROS 2 mapping, the testing strategy, and the open design questions that did not need to be answered to ship the mock.

The implementation itself lives in a future PR. This doc is the blueprint.

---

## Why this isn't done yet

Three reasons, ordered:

1. **The author's primary development environment is Windows.** ROS 2 has nominal Windows support but the integration-test loop is much smoother on Linux + simulator (Gazebo). Doing the real adapter half-blind would produce code that compiles but is hard to verify end-to-end.
2. **The conformance suite already exercises the Protocol.** `ROSAdapter` is implemented by `MockROSAdapter` and tested by 21 declarative fixtures. The shape is locked in. The real adapter has a target.
3. **The validator + bridge + conformance + LLM-bridge surface ships independent of the real adapter.** Most adopters in Phase 0 / early Phase 1 will write their own substrate-specific adapter (PX4, OPC UA, vendor SDK) anyway. The MockROSAdapter covers the development case until a real ROS 2 deployment forces the integration.

These are honest reasons, not excuses. When someone with ROS 2 experience picks this up, this doc is their starting point.

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

## Implementation skeleton

```python
# reference/ros2-runtime/src/urml_ros2_runtime/substrate/rclpy_adapter.py
# THIS FILE DOES NOT EXIST YET. This is the recommended starting structure.

from typing import Any, Literal

# rclpy is an optional dependency:
#   pip install urml-ros2-runtime[real]
try:
    import rclpy
    from rclpy.action import ActionClient
    from rclpy.node import Node
    HAS_RCLPY = True
except ImportError:
    HAS_RCLPY = False


class RclpyAdapter:
    """Real ROS 2 adapter — implements the ROSAdapter Protocol via rclpy.

    Construction requires a running ROS 2 environment. Each adapter instance
    owns one rclpy Node; multiple adapters in the same process share an
    rclpy.init() call (the adapter does not re-init).

    Action clients (Nav2, MoveIt 2, etc.) are created lazily on first use,
    so an instance that never calls navigation doesn't pay the action-client
    cost.
    """

    def __init__(self, node_name: str = "urml_runtime_adapter") -> None:
        if not HAS_RCLPY:
            raise RuntimeError(
                "rclpy is not installed. Install with: pip install urml-ros2-runtime[real]"
            )
        # rclpy.init() is the caller's responsibility — adapters in production
        # often share a single init across multiple subsystems.
        self._node = rclpy.create_node(node_name)
        # Lazy action-client slots; created on first use.
        self._nav_client: ActionClient | None = None
        self._dock_client: ActionClient | None = None
        # ... per-method slots ...

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        # 1. Resolve `location` against a deployment-configured location-to-pose map
        #    (NOT part of URML; the deployer provides this, typically via a ROS 2
        #    parameter file or a topic). For pose-mode, use `pose` directly.
        # 2. Build a Nav2 NavigateToPose goal.
        # 3. Submit via self._nav_client and wait for the result.
        # 4. Map Nav2 status to NavigationResult{success, reason, final_pose, frame}.
        raise NotImplementedError("see INTEGRATION.md")

    # ... one method per ROSAdapter Protocol entry ...
```

The full implementation is ~600-800 lines for the home profile; the drone-profile additions add ~200-300 more.

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

A pinned Gazebo + TurtleBot 4 simulator stack. The conformance suite's 21 existing fixtures all run, but instead of `MockROSAdapter` the runner uses `RclpyAdapter` against the simulated robot. Fixtures that pass against the mock should pass against the simulator (modulo nondeterminism for things like timing — see *Open questions* §3).

Suggested CI gating: a separate `make integration-test` target that requires a Linux runner with ROS 2 Jazzy + Gazebo. This is **not** the default `pytest` target; integration tests are too heavy for routine CI.

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
