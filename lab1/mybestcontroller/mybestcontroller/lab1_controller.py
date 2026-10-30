import math
import time

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class Lab1Controller(Node):

    def __init__(self):
        super().__init__('lab1_controller')

        namespace = self.get_namespace().strip('/')

        if namespace.startswith('ns1_'):
            self.role = 'leader'
            self.isu_id = namespace[4:]

        elif namespace.startswith('ns2_'):
            self.role = 'follower'
            self.isu_id = namespace[4:]

        else:
            raise ValueError(
                'Invalid namespace: ' + namespace
            )

        self.pose = None

        self.pose_sub = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            'turtle1/cmd_vel',
            10
        )

        if self.role == 'leader':

            self.points = [
                (4.0, 2.0),
                (7.0, 1.0),
                (5.0, 4.0)
            ]

            self.point_index = 0
            self.start_time = None
            self.finished = False

            self.result_pub = self.create_publisher(
                Float64,
                '/result_' + self.isu_id,
                10
            )

            self.get_logger().info(
                'Leader started. Route: ' +
                str(self.points)
            )

        else:
            self.leader_pose = None

            leader_topic = (
                '/ns1_' + self.isu_id +
                '/turtle1/pose'
            )

            self.leader_sub = self.create_subscription(
                Pose,
                leader_topic,
                self.leader_callback,
                10
            )

            self.get_logger().info(
                'Follower started'
            )

        self.timer = self.create_timer(
            0.05,
            self.control_step
        )

    def pose_callback(self, msg):
        self.pose = msg

    def leader_callback(self, msg):
        self.leader_pose = msg

    def stop_turtle(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def normalize_angle(self, angle):
        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    def move_to(self, target_x, target_y):

        if self.pose is None:
            return None

        dx = target_x - self.pose.x
        dy = target_y - self.pose.y

        distance = math.hypot(dx, dy)

        target_angle = math.atan2(dy, dx)

        angle_error = self.normalize_angle(
            target_angle - self.pose.theta
        )

        cmd = Twist()

        if distance < 0.10:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        else:
            if abs(angle_error) > 0.2:
                cmd.linear.x = 0.0
            else:
                cmd.linear.x = min(
                    2.0,
                    1.5 * distance
                )

            cmd.angular.z = max(
                -3.0,
                min(3.0, 6.0 * angle_error)
            )

        self.cmd_pub.publish(cmd)

        return distance

    def control_step(self):

        if self.pose is None:
            return

        if self.role == 'leader':
            self.control_leader()
        else:
            self.control_follower()

    def control_leader(self):

        if self.finished:
            self.stop_turtle()
            return

        if self.start_time is None:
            self.start_time = time.monotonic()

        target_x, target_y = self.points[
            self.point_index
        ]

        distance = self.move_to(
            target_x,
            target_y
        )

        if distance < 0.10:

            self.get_logger().info(
                'Reached point ' +
                str(self.point_index + 1)
            )

            self.point_index += 1

            if self.point_index >= len(self.points):

                self.stop_turtle()

                elapsed = (
                    time.monotonic() -
                    self.start_time
                )

                result = Float64()
                result.data = elapsed

                self.result_pub.publish(result)

                self.get_logger().info(
                    f'Finished in {elapsed:.2f} seconds'
                )

                self.finished = True

    def control_follower(self):

        if self.leader_pose is None:
            self.stop_turtle()
            return

        distance = math.hypot(
            self.leader_pose.x - self.pose.x,
            self.leader_pose.y - self.pose.y
        )

        if distance < 0.10:
            self.stop_turtle()
            return

        self.move_to(
            self.leader_pose.x,
            self.leader_pose.y
        )


def main(args=None):
    rclpy.init(args=args)

    node = Lab1Controller()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_turtle()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
