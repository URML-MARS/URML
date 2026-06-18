"""Bring up the URML ExecuteURML action server for the UR-3e worked example.

Unlike the turtlesim example, the robot under test here is a real Universal
Robots UR-3e arm, brought up by CNURobotics/flexbe_ur_demo (chris_ur3e_bringup
+ flexbe_universal_robots + flexbe_moveit2 + the UR ROS 2 driver). That stack is
launched separately; this launch file starts only the URML side:

  * the URML ``ExecuteURML`` action server (``urml-ros2-action-server``), which
    validates and executes URML goals against the substrate adapter.

A typical session brings up three things in three sourced terminals:

    # 1. The UR-3e (mock hardware shown; swap for bringup_arm_hardware.launch.py).
    ros2 launch chris_ur3e_bringup bringup_arm_mock.launch.py

    # 2. The URML action server (this file). adapter:=ros2 drives MoveIt 2.
    ros2 launch urml_flexbe_behaviors urml_flexbe_ur3e.launch.py adapter:=ros2

    # 3. FlexBE itself.
    ros2 launch flexbe_app flexbe_full.launch.py

Then load the ``URML UR-3e Pick-Place`` behavior in the FlexBE UI and approve
the plan to watch the arm execute the validated URML pick-and-place.

Arguments:
  adapter       "ros2" (default — drives MoveIt 2 / the UR driver) | "mock".
  llm_provider  "none" (default) | "anthropic" | "openai" (for NL goals).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    adapter = LaunchConfiguration("adapter")
    llm_provider = LaunchConfiguration("llm_provider")

    return LaunchDescription(
        [
            DeclareLaunchArgument("adapter", default_value="ros2"),
            DeclareLaunchArgument("llm_provider", default_value="none"),
            # The URML action server is a pip console-script entry point
            # (urml-ros2-action-server), not an ament executable, so launch it
            # as a process and pass ROS params via --ros-args.
            ExecuteProcess(
                cmd=[
                    "urml-ros2-action-server",
                    "--ros-args",
                    "-p",
                    ["adapter:=", adapter],
                    "-p",
                    ["llm_provider:=", llm_provider],
                ],
                output="screen",
            ),
        ]
    )
