"""CLI interface for vnrobo-agent."""

import argparse
import logging
import signal
import sys

from vnrobo_agent import __version__
from vnrobo_agent.agent import VnRoboAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vnrobo-agent",
        description="VnRobo Fleet Monitor heartbeat agent",
    )
    parser.add_argument(
        "--version", action="version", version=f"vnrobo-agent {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- start ---
    start_parser = subparsers.add_parser("start", help="Start sending heartbeats")
    start_parser.add_argument("--api-key", help="API key (or set VNROBO_API_KEY)")
    start_parser.add_argument("--robot-id", help="Robot ID (or set VNROBO_ROBOT_ID)")
    start_parser.add_argument(
        "--interval", type=int, default=60, help="Heartbeat interval in seconds (default: 60)"
    )
    start_parser.add_argument(
        "--endpoint", default="https://app.vnrobo.com/api/heartbeat", help="API endpoint"
    )

    # --- ping ---
    ping_parser = subparsers.add_parser("ping", help="Send a single test heartbeat")
    ping_parser.add_argument("--api-key", help="API key (or set VNROBO_API_KEY)")
    ping_parser.add_argument("--robot-id", help="Robot ID (or set VNROBO_ROBOT_ID)")
    ping_parser.add_argument(
        "--endpoint", default="https://app.vnrobo.com/api/heartbeat", help="API endpoint"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [vnrobo-agent] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.command == "ping":
        agent = VnRoboAgent(
            api_key=args.api_key,
            robot_id=args.robot_id,
            endpoint=args.endpoint,
        )
        ok = agent.send_heartbeat(status="online")
        if ok:
            print("Heartbeat sent successfully.")
        else:
            print("Heartbeat failed. Check logs above.")
            sys.exit(1)

    elif args.command == "start":
        agent = VnRoboAgent(
            api_key=args.api_key,
            robot_id=args.robot_id,
            endpoint=args.endpoint,
            interval=args.interval,
        )

        stop = lambda *_: (agent.stop(), sys.exit(0))
        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

        agent.start()
        print(f"Heartbeat running every {args.interval}s. Press Ctrl+C to stop.")

        # Block main thread until signal
        signal.pause()


if __name__ == "__main__":
    main()
