#!/usr/bin/env python3
"""Publish a small synthetic sensor_msgs/Image on /camera/image_raw at 2 Hz.

16x16 mono8, header.frame_id 'camera_link', header.stamp from the node clock.
The gradient shifts by one step per frame, so consecutive frames differ.
Run with the system python3 after `source /opt/ros/jazzy/setup.bash`.
QoS: reliable, volatile, depth 10 (matches both reliable and best-effort subscribers).
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image

WIDTH = 16
HEIGHT = 16
PERIOD_S = 0.5  # 2 Hz


class TestCamera(Node):
    def __init__(self) -> None:
        super().__init__('urml_test_camera')
        self._pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self._seq = 0
        self._timer = self.create_timer(PERIOD_S, self._tick)

    def _tick(self) -> None:
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_link'
        msg.height = HEIGHT
        msg.width = WIDTH
        msg.encoding = 'mono8'
        msg.is_bigendian = 0
        msg.step = WIDTH
        msg.data = bytes(
            ((x + y + self._seq) * 8) % 256 for y in range(HEIGHT) for x in range(WIDTH)
        )
        self._pub.publish(msg)
        self._seq += 1


def main() -> None:
    rclpy.init()
    node = TestCamera()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
