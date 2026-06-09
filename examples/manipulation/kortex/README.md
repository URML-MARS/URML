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

# URML to ros2_kortex (Kinova Gen3 manipulation)

A worked example: validate a URML manipulation program against a Kinova Gen3
capability manifest, then show how each validated primitive maps onto the
**existing ros2_kortex ROS 2 interfaces**. This is the concrete example a Kinova
engineer asked for on
[Kinovarobotics/ros2_kortex#413](https://github.com/Kinovarobotics/ros2_kortex/issues/413).

## What it does

[`urml_to_kortex.py`](urml_to_kortex.py):

1. **Validates first.** It runs the URML program against
   [`kinova-gen3.manifest.yaml`](kinova-gen3.manifest.yaml) and refuses to emit
   a dispatch plan unless the intent is admissible. The static gate is URML's
   whole point: a grasp force above the gripper's rating, an undeclared gripper,
   or an object the gripper cannot take is rejected **here**, and no ROS 2 action
   goal is ever sent.
2. **Maps each validated primitive** onto the real ros2_kortex surface:

   | URML | ros2_kortex |
   |---|---|
   | `move_to: { location: X }` | MoveIt 2 (`kortex_moveit_config`) plans to X's declared pose, executed via `joint_trajectory_controller/follow_joint_trajectory` (`control_msgs/action/FollowJointTrajectory`) |
   | `grasp: { force }` | `robotiq_gripper_controller/gripper_cmd` (`control_msgs/action/GripperCommand`): `position=closed`, `max_effort` = the validated force, bounded by the gripper's `force_max_n` |
   | `release` | `robotiq_gripper_controller/gripper_cmd`: `position=open`, `max_effort=0` |
   | `detect: { object }` | perception (the `wrist_rgb` camera + a vision pipeline); not a Kortex motion action |

The input is [`pick-place.urml.yaml`](pick-place.urml.yaml): go to the pick bin,
find the red widget, grasp it, carry it to the red kitting tray, place it, home.

## Validation-first, demonstrated

The same program with `grasp: { force: 200 }` (the gripper is rated to 140 N) is
**rejected** before any goal:

```
URML program does not validate; no Kortex goal dispatched.
Errors: capability.missing_gripper, envelope.force_exceeded
```

That is the difference from sending action goals directly: the inadmissible
command never reaches `gripper_cmd`.

## Run it

```bash
python examples/manipulation/kortex/urml_to_kortex.py   # regenerates dispatch-plan.txt
```

Pure Python stdlib + the URML validator (no ROS 2, no hardware), and
deterministic: the committed [`dispatch-plan.txt`](dispatch-plan.txt) is
byte-asserted against the generator in CI
(`reference/validator/tests/test_kortex_dispatch.py`), the same discipline the
README hero SVG and the esmini example use.

## Scope

This shows the **validated-intent to ros2_kortex-interface mapping**, not a live
ROS 2 node. Running it on a real Gen3 needs `ros2_kortex` + MoveIt 2; the inverse
kinematics and trajectory planning are substrate-side. URML declares the goal
pose and the force bound; ros2_kortex and its controllers execute. A live
rclpy-based dispatcher (URML runtime acting through the Kortex action clients) is
the natural next step. The validator side already ships the `kinova_cobot_cell`
manifest; the zero-ROS cobot path is `reference/cobot-runtime/`.
