"""sitl_flight_track.py: fly a drone example against ArduCopter SITL and plot the track.

A simulation you can look at before a real flight. SITL must be running
with two links to this host: the URML link on udp 14550 and a telemetry
link on udp 14551, for example (from an ArduPilot checkout):

    build/sitl/bin/arducopter --model + --speedup 2 -w \\
        --home 40.7570095,-73.9859724,10,0 \\
        --defaults Tools/autotest/default_params/copter.parm,urml_sitl.parm \\
        --serial0 udpclient:<this-host>:14550 --serial1 udpclient:<this-host>:14551

Usage:

    python tools/scripts/sitl_flight_track.py <out_dir> [program] [manifest] [adapter]

Writes <program>.track.csv, <program>.events.txt, <program>.track.png.
Needs matplotlib (pip install matplotlib); not a runtime dependency.
Listens on the second SITL link in a thread, logging GLOBAL_POSITION_INT,
HEARTBEAT (mode/armed), STATUSTEXT, and COMMAND_ACK; runs the URML program
through URMLRuntime on the first link; then plots the track with capture
markers and the altitude profile.
"""

from __future__ import annotations

import csv
import math
import sys
import threading
import time
from pathlib import Path
from typing import Any

import yaml
from pymavlink import mavutil

REPO = Path(__file__).resolve().parents[2]
EX = REPO / "examples" / "drone"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
PROGRAM = sys.argv[2] if len(sys.argv) > 2 else "site-photogrammetry"
MANIFEST = sys.argv[3] if len(sys.argv) > 3 else PROGRAM
ADAPTER = sys.argv[4] if len(sys.argv) > 4 else PROGRAM
MODES = {0: "STABILIZE", 4: "GUIDED", 5: "LOITER", 6: "RTL", 9: "LAND"}

rows: list[dict[str, Any]] = []
events: list[dict[str, Any]] = []
stop = threading.Event()


def listener() -> None:
    c = mavutil.mavlink_connection("udp:0.0.0.0:14551")
    c.wait_heartbeat(timeout=60)
    # SITL sends nothing on this link until a client asks: request everything at 4 Hz.
    c.mav.request_data_stream_send(c.target_system, c.target_component, mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1)
    mode, armed = None, None
    while not stop.is_set():
        m = c.recv_match(blocking=True, timeout=1)
        if m is None:
            continue
        t = time.time()
        k = m.get_type()
        if k == "GLOBAL_POSITION_INT":
            rows.append(
                {"t": t, "lat": m.lat / 1e7, "lon": m.lon / 1e7, "alt": m.relative_alt / 1000.0, "mode": mode, "armed": armed}
            )
        elif k == "HEARTBEAT" and m.get_srcSystem() == 1:
            mode = MODES.get(m.custom_mode, str(m.custom_mode))
            armed = bool(m.base_mode & 128)
        elif k == "STATUSTEXT":
            events.append({"t": t, "kind": "statustext", "text": m.text})
        elif k == "COMMAND_ACK":
            events.append({"t": t, "kind": "ack", "text": f"cmd {m.command} result {m.result}"})
    c.close()


def load(name: str) -> dict[str, Any]:
    return yaml.safe_load((EX / name).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def main() -> int:
    th = threading.Thread(target=listener, daemon=True)
    th.start()
    from urml_ardupilot_runtime import ArduCopterAdapter, load_ardupilot_config
    from urml_ros2_runtime import URMLRuntime

    cfg = load_ardupilot_config(EX / f"{ADAPTER}.adapter.yaml").model_copy(
        update={
            "connection_url": "udp:0.0.0.0:14550",
            "takeoff_timeout_seconds": 180.0,
            "arrival_timeout_seconds": 240.0,
            "arm_timeout_seconds": 60.0,
        }
    )
    t0 = time.time()
    env_path = EX / f"{MANIFEST}.envelope.yaml"
    with ArduCopterAdapter(cfg) as adapter:
        result = URMLRuntime(adapter).execute(
            load(f"{PROGRAM}.urml.yaml"),
            load(f"{MANIFEST}.manifest.yaml"),
            envelope=load(env_path.name) if env_path.exists() else None,
            profiles=("drone",),
        )
    print("RESULT", result.success, result.steps_executed, result.last_outcome if not result.success else "")
    caps = {k: v for k, v in result.bindings.items() if k.startswith("shot_")}
    for k, v in caps.items():
        print(k, v.get("pose"), v.get("uri"))
    time.sleep(2)
    stop.set()
    th.join(timeout=3)

    with (OUT / f"{PROGRAM}.track.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["t", "lat", "lon", "alt", "mode", "armed"])
        w.writeheader()
        w.writerows(rows)
    with (OUT / f"{PROGRAM}.events.txt").open("w", encoding="utf-8") as fh:
        for e in events:
            fh.write(f"{e['t'] - t0:8.1f}s  {e['kind']:10s} {e['text']}\n")

    if not rows:
        print("no positions recorded on 14551; skipping plot")
        return 0 if result.success else 1

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 12), gridspec_kw={"height_ratios": [3, 1]})
    lats = [r["lat"] for r in rows]
    lons = [r["lon"] for r in rows]
    alts = [r["alt"] for r in rows]
    ts = [r["t"] - t0 for r in rows]
    ax1.plot(lons, lats, "-", color="#1f77b4", lw=1.5, label="flight path")
    ax1.plot(lons[0], lats[0], "s", color="green", ms=9, label="home / launch")
    for name, gp in cfg.location_to_global.items():
        if name == "home":
            continue
        ax1.plot(gp.lon, gp.lat, "o", mfc="none", mec="gray", ms=10)
        ax1.annotate(name, (gp.lon, gp.lat), textcoords="offset points", xytext=(6, 6), fontsize=8, color="gray")
    for k, v in caps.items():
        p = v.get("pose") or {}
        if p:
            ax1.plot(p["lon"], p["lat"], "*", color="crimson", ms=14)
            ax1.annotate(k, (p["lon"], p["lat"]), textcoords="offset points", xytext=(6, -12), fontsize=8, color="crimson")
    ax1.set_aspect(1 / max(1e-9, math.cos(math.radians(lats[0]))))
    ax1.set_xlabel("longitude")
    ax1.set_ylabel("latitude")
    ax1.grid(alpha=0.3)
    ax1.set_title(f"URML `{PROGRAM}` on ArduCopter SITL, home {lats[0]:.5f}, {lons[0]:.5f}")
    ax1.legend(loc="lower right")
    ax2.plot(ts, alts, color="#1f77b4")
    ax2.set_xlabel("seconds since execute()")
    ax2.set_ylabel("alt AGL (m)")
    ax2.grid(alpha=0.3)
    for v in caps.values():
        ax2.axvline(x=v.get("timestamp", t0) - t0, color="crimson", alpha=0.5, lw=1)
    fig.tight_layout()
    png = OUT / f"{PROGRAM}.track.png"
    fig.savefig(png, dpi=130)
    print("wrote", png, len(rows), "positions,", len(events), "events")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
