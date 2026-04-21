"""Core VnRoboAgent class — sends heartbeats to VnRobo Fleet Monitor."""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("vnrobo_agent")


class VnRoboAgent:
    """Lightweight agent that sends periodic heartbeats to VnRobo Fleet Monitor.

    Usage:
        agent = VnRoboAgent(api_key="key", robot_id="robot-01")
        agent.start()
        # ... robot does its thing ...
        agent.stop()
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        robot_id: Optional[str] = None,
        endpoint: str = "https://app.vnrobo.com/api/heartbeat",
        interval: int = 60,
    ):
        self.api_key = api_key or os.environ.get("VNROBO_API_KEY", "")
        self.robot_id = robot_id or os.environ.get("VNROBO_ROBOT_ID", "")
        self.endpoint = endpoint
        self.interval = interval

        if not self.api_key:
            raise ValueError(
                "api_key is required. Pass it directly or set VNROBO_API_KEY."
            )
        if not self.robot_id:
            raise ValueError(
                "robot_id is required. Pass it directly or set VNROBO_ROBOT_ID."
            )

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        self._max_retries = 3
        self._base_backoff = 2  # seconds

    def start(self) -> None:
        """Start the background heartbeat thread."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.warning("Agent already running.")
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._heartbeat_loop, daemon=True, name="vnrobo-heartbeat"
            )
            self._thread.start()
            logger.info(
                "VnRobo agent started (robot_id=%s, interval=%ds)",
                self.robot_id,
                self.interval,
            )

    def stop(self) -> None:
        """Stop the background heartbeat thread."""
        self._stop_event.set()
        with self._lock:
            if self._thread is not None:
                self._thread.join(timeout=self.interval + 5)
                self._thread = None
        logger.info("VnRobo agent stopped.")

    def send_heartbeat(
        self,
        status: str = "online",
        battery: Optional[float] = None,
        location: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send a single heartbeat to the fleet monitor.

        Args:
            status: Robot status — "online", "idle", "busy", "error", "offline".
            battery: Battery percentage (0-100), or None if not applicable.
            location: Dict with "lat" and "lng" keys, or None.
            metadata: Any extra key-value pairs to include.

        Returns:
            True if the heartbeat was accepted, False otherwise.
        """
        payload: Dict[str, Any] = {
            "robotId": self.robot_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if battery is not None:
            payload["battery"] = battery
        if location is not None:
            payload["location"] = location
        if metadata is not None:
            payload["metadata"] = metadata

        return self._send_with_retry(payload)

    def _send_with_retry(self, payload: Dict[str, Any]) -> bool:
        """Send payload with exponential backoff retries."""
        for attempt in range(self._max_retries):
            try:
                resp = self._session.post(
                    self.endpoint,
                    data=json.dumps(payload),
                    timeout=10,
                )
                if resp.status_code < 300:
                    logger.debug("Heartbeat sent (robot_id=%s)", self.robot_id)
                    return True

                logger.warning(
                    "Heartbeat rejected: %d %s", resp.status_code, resp.text[:200]
                )
                # Don't retry on 4xx client errors (bad key, bad payload)
                if 400 <= resp.status_code < 500:
                    return False

            except requests.RequestException as exc:
                logger.warning("Heartbeat failed (attempt %d): %s", attempt + 1, exc)

            if attempt < self._max_retries - 1:
                wait = self._base_backoff ** (attempt + 1)
                logger.debug("Retrying in %ds...", wait)
                time.sleep(wait)

        logger.error(
            "Heartbeat failed after %d retries (robot_id=%s)",
            self._max_retries,
            self.robot_id,
        )
        return False

    def _heartbeat_loop(self) -> None:
        """Background loop that sends heartbeats at the configured interval."""
        while not self._stop_event.is_set():
            self.send_heartbeat()
            self._stop_event.wait(self.interval)

    @property
    def is_running(self) -> bool:
        """Check if the heartbeat thread is active."""
        return self._thread is not None and self._thread.is_alive()
