"""Simplest possible vnrobo-agent usage."""

import time

from vnrobo_agent import VnRoboAgent

# Create agent (or set VNROBO_API_KEY and VNROBO_ROBOT_ID env vars)
agent = VnRoboAgent(api_key="your-api-key", robot_id="robot-01")

# Option 1: Start background heartbeats (every 60s by default)
agent.start()

# Your robot code runs here...
time.sleep(120)

agent.stop()

# Option 2: Send a single heartbeat manually
agent.send_heartbeat(
    status="busy",
    battery=85.0,
    location={"lat": 21.0285, "lng": 105.8542},
    metadata={"task": "delivery", "floor": 3},
)
