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

# URML + FlexBE worked example

This example wires URML into [FlexBE](https://github.com/FlexBE/flexbe_behavior_engine),
the operator-in-the-loop hierarchical state machine engine for ROS 2. A FlexBE
state dispatches a validated URML program through a ROS 2 action; URML validates
it against the robot's capability manifest and safety envelope before anything
actuates, and the verdict surfaces to the operator. This is the seam proposed in
[RFC-0474](../../docs/rfcs/0474-flexbe-outreach.md) and the one David Conner
(CHRISLab, Christopher Newport University) suggested: give FlexBE a ROS 2 action
to call, and write the FlexBE states for it.

```
FlexBE HFSM (operator approves)
   └─ ExecuteUrmlState ──(ROS 2 action: ExecuteURML)──▶ URML action server
                                                           │  validate → execute
                                                           ▼
                                                    URMLRuntime ──▶ turtlesim
```

## The pieces

| Piece | Path |
|-------|------|
| `ExecuteURML` action interface | [`ros2_ws/src/urml_ros2_msgs/`](ros2_ws/src/urml_ros2_msgs/) |
| URML action server (node + rclpy-free core) | [`reference/ros2-runtime/.../action_server.py`](../../reference/ros2-runtime/src/urml_ros2_runtime/action_server.py) |
| `ExecuteUrmlState` FlexBE state | [`ros2_ws/src/urml_flexbe_states/`](ros2_ws/src/urml_flexbe_states/) |
| `URML Turtle Patrol` behavior + launch | [`ros2_ws/src/urml_flexbe_behaviors/`](ros2_ws/src/urml_flexbe_behaviors/) |
| The URML program / manifest | [`turtle-patrol.urml.yaml`](turtle-patrol.urml.yaml), [`turtle.manifest.yaml`](turtle.manifest.yaml) |

## Run the URML side hermetically (no ROS 2 needed)

The URML program validates and executes against the mock substrate on any host,
including Windows. This is what CI runs:

```bash
urml validate examples/flexbe/turtle-patrol.urml.yaml \
  -m examples/flexbe/turtle.manifest.yaml --profile home --no-policy

urml execute examples/flexbe/turtle-patrol.urml.yaml \
  -m examples/flexbe/turtle.manifest.yaml --profile home --no-policy --adapter mock
```

The natural-language path uses the hermetic echo provider:

```bash
urml translate "Patrol the two waypoints, then come home." \
  -m examples/flexbe/turtle.manifest.yaml --profile home \
  --provider echo --echo-response-file examples/flexbe/turtle-patrol.echo-response.json
```

## Run the full stack (real ROS 2 + FlexBE + turtlesim)

This part needs a sourced ROS 2 environment (Jazzy / Kilted / Rolling), FlexBE,
and turtlesim. It cannot run in URML's hermetic CI, so it ships as a documented,
gated example (see [`.github/workflows/flexbe-integration.yml`](../../.github/workflows/flexbe-integration.yml)).

```bash
# 1. Install URML's Python packages into your ROS 2 Python environment.
pip install -e reference/validator -e reference/ros2-runtime -e reference/llm-bridge

# 2. Build the action interface + FlexBE packages.
cd examples/flexbe/ros2_ws
colcon build
source install/setup.bash

# 3. Install FlexBE and turtlesim if you have not already.
sudo apt install ros-$ROS_DISTRO-flexbe-behavior-engine ros-$ROS_DISTRO-flexbe-app ros-$ROS_DISTRO-turtlesim

# 4. Bring up turtlesim + the URML action server (adapter:=ros2 drives the turtle).
ros2 launch urml_flexbe_behaviors urml_flexbe_turtlesim.launch.py adapter:=ros2

# 5. In another sourced terminal, start FlexBE and load "URML Turtle Patrol".
ros2 launch flexbe_app flexbe_full.launch.py
```

Approve the plan in the FlexBE operator UI. `ExecuteUrmlState` sends the program
to the URML action server, which validates it (you see the verdict), then drives
the turtle through the patrol. Change a waypoint in
[`turtle.manifest.yaml`](turtle.manifest.yaml) to an undeclared location and the
server returns `refused` with the validator's reason instead of moving.

## Why this shape

URML is not a state machine engine and does not want to be one. FlexBE is, and a
good one, with a human in the loop. URML's job is the typed, validated intent and
the static check that the intent is admissible on this robot before it runs. The
two compose: FlexBE's human gate and URML's static gate guard the same actuation
from different sides. Conner et al.'s capability-based synthesis treats each
"capability" as a state with pre/post-conditions; a validated URML primitive is
exactly such a capability, with the manifest + envelope as its precondition.
