"""ROS2 node that sends heartbeats to VnRobo Fleet Monitor.

Run:
    ros2 run your_package vnrobo_heartbeat

Or standalone:
    python3 ros2_heartbeat.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from geometry_msgs.msg import PoseStamped

from vnrobo_agent import VnRoboAgent


class VnRoboHeartbeatNode(Node):
    def __init__(self):
        super().__init__("vnrobo_heartbeat")

        # Declare ROS2 parameters
        self.declare_parameter("api_key", "")
        self.declare_parameter("robot_id", "")
        self.declare_parameter("interval", 30)

        api_key = self.get_parameter("api_key").get_parameter_value().string_value
        robot_id = self.get_parameter("robot_id").get_parameter_value().string_value
        interval = self.get_parameter("interval").get_parameter_value().integer_value

        self.agent = VnRoboAgent(
            api_key=api_key,
            robot_id=robot_id,
            interval=interval,
        )
        self.agent.start()
        self.get_logger().info(f"VnRobo heartbeat started for {robot_id}")

        # Subscribe to battery and pose topics
        self.battery_pct = None
        self.location = None

        self.create_subscription(BatteryState, "/battery", self._on_battery, 10)
        self.create_subscription(PoseStamped, "/robot_pose", self._on_pose, 10)

        # Periodic heartbeat with latest sensor data
        self.create_timer(float(interval), self._send_heartbeat)

    def _on_battery(self, msg: BatteryState):
        self.battery_pct = msg.percentage * 100.0

    def _on_pose(self, msg: PoseStamped):
        self.location = {
            "lat": msg.pose.position.x,  # Replace with actual GPS conversion
            "lng": msg.pose.position.y,
        }

    def _send_heartbeat(self):
        self.agent.send_heartbeat(
            status="online",
            battery=self.battery_pct,
            location=self.location,
            metadata={"framework": "ros2"},
        )

    def destroy_node(self):
        self.agent.stop()
        self.get_logger().info("VnRobo heartbeat stopped.")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VnRoboHeartbeatNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
