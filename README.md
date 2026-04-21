# vnrobo-agent

Lightweight Python agent that sends heartbeat data from your robot to [VnRobo Fleet Monitor](https://app.vnrobo.com).

## Install

```bash
pip install vnrobo-agent
```

## Quick Start

```python
from vnrobo_agent import VnRoboAgent

agent = VnRoboAgent(api_key="your-key", robot_id="robot-01")
agent.start()  # sends heartbeats every 60s in background
```

When shutting down:

```python
agent.stop()
```

## Send Custom Data

```python
agent.send_heartbeat(
    status="busy",
    battery=72.5,
    location={"lat": 21.0285, "lng": 105.8542},
    metadata={"task": "picking", "payload_kg": 3.2},
)
```

## CLI

```bash
# Test connectivity with a single ping
vnrobo-agent ping --api-key=YOUR_KEY --robot-id=robot-01

# Run continuous heartbeats
vnrobo-agent start --api-key=YOUR_KEY --robot-id=robot-01 --interval=30
```

## Environment Variables

Instead of passing flags every time:

```bash
export VNROBO_API_KEY=your-key
export VNROBO_ROBOT_ID=robot-01

vnrobo-agent start
```

## ROS2 Integration

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from vnrobo_agent import VnRoboAgent


class HeartbeatNode(Node):
    def __init__(self):
        super().__init__("vnrobo_heartbeat")
        self.agent = VnRoboAgent(api_key="your-key", robot_id="robot-01", interval=30)
        self.agent.start()
        self.create_subscription(BatteryState, "/battery", self.on_battery, 10)
        self.battery_pct = None

    def on_battery(self, msg):
        self.battery_pct = msg.percentage * 100
        self.agent.send_heartbeat(status="online", battery=self.battery_pct)

    def destroy_node(self):
        self.agent.stop()
        super().destroy_node()


def main():
    rclpy.init()
    node = HeartbeatNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## API

### `VnRoboAgent(api_key, robot_id, endpoint, interval)`

| Param | Default | Description |
|-------|---------|-------------|
| `api_key` | `VNROBO_API_KEY` env | Your API key from app.vnrobo.com |
| `robot_id` | `VNROBO_ROBOT_ID` env | Unique identifier for this robot |
| `endpoint` | `https://app.vnrobo.com/api/heartbeat` | API endpoint |
| `interval` | `60` | Seconds between heartbeats |

### Methods

- **`start()`** — Start background heartbeat thread
- **`stop()`** — Stop heartbeat thread
- **`send_heartbeat(status, battery, location, metadata)`** — Send one heartbeat manually
- **`is_running`** — Property, True if heartbeat thread is active

## License

MIT
