# vnrobo-agent

[![PyPI version](https://badge.fury.io/py/vnrobo-agent.svg)](https://pypi.org/project/vnrobo-agent/)
[![Python](https://img.shields.io/pypi/pyversions/vnrobo-agent.svg)](https://pypi.org/project/vnrobo-agent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/VnRobo/vnrobo-agent/actions/workflows/test.yml/badge.svg)](https://github.com/VnRobo/vnrobo-agent/actions)

Lightweight Python agent that sends robot telemetry to **[VnRobo Fleet Monitor](https://app.vnrobo.com)** — the open fleet monitoring dashboard for robotics teams.

```python
from vnrobo_agent import VnRoboAgent

agent = VnRoboAgent(api_key="your-key", robot_id="robot-01")
agent.start()  # sends heartbeat every 60s in background
```

## Install

```bash
pip install vnrobo-agent
```

Requires Python 3.8+. No dependencies beyond `requests`.

## Quick Start

```python
from vnrobo_agent import VnRoboAgent

agent = VnRoboAgent(
    api_key="your-key",   # or set VNROBO_API_KEY env var
    robot_id="robot-01",  # or set VNROBO_ROBOT_ID env var
    interval=30,          # heartbeat every 30s (default: 60)
)
agent.start()

# ... your robot code runs here ...

agent.stop()
```

Get your free API key at **[app.vnrobo.com](https://app.vnrobo.com)** — free for up to 3 robots.

## Send Rich Telemetry

```python
agent.send_heartbeat(
    status="busy",                               # online | idle | busy | error | offline
    battery=72.5,                                # battery % 0-100
    location={"lat": 21.0285, "lng": 105.8542}, # GPS or indoor coords
    metadata={"task": "picking", "payload_kg": 3.2},
)
```

## ROS 2 Integration

```bash
# Zero-config ROS 2 monitoring (no code required):
# See github.com/VnRobo/ros2-fleet-bridge

# Or use the included example node:
ros2 run your_package vnrobo_heartbeat \
    --ros-args -p api_key:=YOUR_KEY -p robot_id:=my_robot
```

Full example: [`examples/ros2_heartbeat.py`](examples/ros2_heartbeat.py)

## Isaac Lab / RL Training

Track training robots in real-time on the dashboard:

```python
agent = VnRoboAgent(api_key=os.environ["VNROBO_KEY"], robot_id="go2-train-01")

# In your training loop:
agent.send_heartbeat(
    status="training",
    metadata={"episode": ep, "reward": float(mean_reward), "step": total_steps},
)
```

## CLI

```bash
# Test connectivity
vnrobo-agent ping --api-key YOUR_KEY --robot-id robot-01

# Run as daemon
vnrobo-agent start --api-key YOUR_KEY --robot-id robot-01 --interval 30

# Or via environment variables
export VNROBO_API_KEY=your-key
export VNROBO_ROBOT_ID=robot-01
vnrobo-agent start
```

## Compatibility

| Platform | Support |
|---|---|
| ROS 2 (Humble / Iron / Jazzy) | ✅ |
| Isaac Lab / Isaac Sim | ✅ |
| Unitree SDK (Go2, G1, H1) | ✅ |
| MuJoCo / Gymnasium | ✅ |
| Bare Python / embedded | ✅ |

## Contributing

```bash
git clone https://github.com/VnRobo/vnrobo-agent
cd vnrobo-agent
pip install -e .
```

Issues and PRs welcome.

## License

MIT — see [LICENSE](LICENSE).

---

**Monitor your robots for free → [app.vnrobo.com](https://app.vnrobo.com)**
