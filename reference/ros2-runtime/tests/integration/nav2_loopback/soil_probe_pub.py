#!/usr/bin/env python3
"""Publish std_msgs/Float64 on /sensor/soil_probe at 2 Hz with a slowly changing value.

value = 0.35 + 0.05 * sin(2*pi*t/60), t = seconds since node start: a volumetric
soil-moisture fraction drifting between 0.30 and 0.40 over a 60 s period.
Run with the system python3 after `source /opt/ros/jazzy/setup.bash`.
QoS: reliable, volatile, depth 10.
"""
import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float64

PERIOD_S = 0.5  # 2 Hz


class TestSoilProbe(Node):
    def __init__(self) -> None:
        super().__init__('urml_test_soil_probe')
        self._pub = self.create_publisher(Float64, '/sensor/soil_probe', 10)
        self._t0 = self.get_clock().now()
        self._timer = self.create_timer(PERIOD_S, self._tick)

    def _tick(self) -> None:
        t = (self.get_clock().now() - self._t0).nanoseconds * 1e-9
        self._pub.publish(Float64(data=0.35 + 0.05 * math.sin(2.0 * math.pi * t / 60.0)))


def main() -> None:
    rclpy.init()
    node = TestSoilProbe()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
