"""``python -m urml_ardupilot_runtime.probe COM5`` — read-only bring-up check.

Opens the link, waits for a heartbeat, prints what the autopilot says it
is, and closes. Sends no mode, arm, or motion command. Exit 0 on a
heartbeat from an ArduCopter, 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys

from urml_ardupilot_runtime.adapter import probe
from urml_ardupilot_runtime.config import ArduPilotAdapterConfig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m urml_ardupilot_runtime.probe",
        description="Read-only identity probe of a connected ArduPilot autopilot.",
    )
    parser.add_argument("connection", help="pymavlink URL: COM5, /dev/ttyACM0, udp:127.0.0.1:14550 ...")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--listen", type=float, default=3.0, help="Seconds to listen for telemetry.")
    args = parser.parse_args(argv)

    cfg = ArduPilotAdapterConfig(connection_url=args.connection, baud=args.baud)
    try:
        info = probe(cfg, listen_seconds=args.listen)
    except RuntimeError as exc:
        print(f"probe failed: {exc}", file=sys.stderr)
        return 1
    for key, value in info.items():
        if key == "statustext":
            continue
        print(f"{key}: {value}")
    if info.get("statustext"):
        print("statustext:")
        for line in info["statustext"]:
            print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
