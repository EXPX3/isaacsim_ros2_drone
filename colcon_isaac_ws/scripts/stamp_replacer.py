#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.time import Time

from tf2_msgs.msg import TFMessage
from sensor_msgs.msg import PointCloud2


class StampReplacer(Node):
    def __init__(self):
        super().__init__('stamp_replacer')

        # Subscription to /tf → get reference timestamp
        self.sub_tf = self.create_subscription(
            TFMessage,
            '/tf',
            self.tf_callback,
            10
        )

        # Subscription to velodyne_points → the one we want to modify
        self.sub_points = self.create_subscription(
            PointCloud2,
            # '/velodyne_points',
            '/velodyne_points_downsampled',

            self.points_callback,
            10
        )

        # Publisher for modified point cloud
        self.pub = self.create_publisher(
            PointCloud2,
            '/velodyne_points_with_tf_timestamp',
            10
        )

        # We'll store the latest timestamp as rclpy.time.Time object
        self.last_tf_stamp = None

        self.get_logger().info("Stamp replacer node started")
        self.get_logger().info("Waiting for /tf and /velodyne_points messages...")


    def tf_callback(self, msg: TFMessage):
        """Update stored timestamp if we receive a newer one from /tf"""
        if not msg.transforms:
            return

        # Take stamp from the first transform (most common choice)
        stamp_msg = msg.transforms[0].header.stamp

        # Convert to rclpy.time.Time so we can compare properly
        new_stamp = Time.from_msg(stamp_msg)

        # First time or actually newer → update
        if self.last_tf_stamp is None or new_stamp > self.last_tf_stamp:
            self.last_tf_stamp = new_stamp
            # self.get_logger().debug(f"New tf stamp stored: {new_stamp}")


    def points_callback(self, msg: PointCloud2):
        """Replace stamp with the latest known /tf stamp and republish"""
        if self.last_tf_stamp is not None:
            out_msg = msg
            # Convert back to builtin_interfaces/Time for the header
            out_msg.header.stamp = self.last_tf_stamp.to_msg()
            self.pub.publish(out_msg)

            # Optional: log very rarely (uncomment if needed)
            # self.get_logger().debug_throttle(5.0, "Published point cloud with updated tf stamp")
        # else: silently drop until we have at least one /tf timestamp


def main(args=None):
    rclpy.init(args=args)
    node = StampReplacer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error during spin: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()