"""Bring up turtlesim + the URML ExecuteURML action server.

This starts the two ROS 2 nodes the worked example needs:

  * ``turtlesim_node`` — the robot under test.
  * the URML ``ExecuteURML`` action server (``urml-ros2-action-server``),
    which validates and executes URML goals against the substrate adapter.

FlexBE itself (the behavior engine + operator app) is launched separately, per
the FlexBE quickstart, e.g.::

    ros2 launch flexbe_app flexbe_full.launch.py

Then load the ``URML Turtle Patrol`` behavior in the FlexBE UI and approve the
plan to watch the turtle execute the validated URML patrol.

Arguments:
  adapter       "ros2" (default here — drives the real turtle) | "mock".
  llm_provider  "none" (default) | "anthropic" | "openai" (for NL goals).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    adapter = LaunchConfiguration("adapter")
    llm_provider = LaunchConfiguration("llm_provider")

    return LaunchDescription(
        [
            DeclareLaunchArgument("adapter", default_value="ros2"),
            DeclareLaunchArgument("llm_provider", default_value="none"),
            Node(
                package="turtlesim",
                executable="turtlesim_node",
                name="turtlesim",
                output="screen",
            ),
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
