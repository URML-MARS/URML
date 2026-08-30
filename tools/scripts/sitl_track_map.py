"""sitl_track_map.py: draw a recorded SITL track over aerial imagery.

Companion to sitl_flight_track.py. Reads <name>.track.csv from the current
directory and the matching examples/drone/<adapter>.adapter.yaml bindings,
and writes <name>.map.png over Esri World Imagery tiles (network at
documentation time only; needs `pip install contextily`).

Usage: python tools/scripts/sitl_track_map.py  (run inside the track directory)
"""

import csv
import math
import yaml
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import contextily as cx

EX = Path(__file__).resolve().parents[2] / "examples" / "drone"


def load_track(name):
    rows = list(csv.DictReader(open(f"{name}.track.csv", encoding="utf-8")))
    return (
        [float(r["lon"]) for r in rows],
        [float(r["lat"]) for r in rows],
        [float(r["alt"]) for r in rows],
    )


def merc(lon, lat):
    x = lon * 20037508.34 / 180.0
    y = (
        math.log(math.tan((90 + lat) * math.pi / 360.0))
        / (math.pi / 180.0)
        * 20037508.34
        / 180.0
    )
    return x, y


for name, adapter, title, source in [
    (
        "site-photogrammetry.gemini",
        "site-photogrammetry",
        "Five-station photogrammetry orbit at 100 m AGL (ArduCopter SITL)",
        cx.providers.Esri.WorldImagery,
    ),
    (
        "parcel-delivery.gemini",
        "parcel-delivery",
        "Parcel delivery to Duffy Square, winch + latch (ArduCopter SITL)",
        cx.providers.Esri.WorldImagery,
    ),
]:
    lons, lats, alts = load_track(name)
    xs, ys = zip(*[merc(a, b) for a, b in zip(lons, lats)])
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(xs, ys, "-", color="#00e5ff", lw=3, alpha=0.95, label="flight path")
    ax.plot(
        xs[0],
        ys[0],
        "s",
        color="#7CFC00",
        ms=12,
        mec="black",
        label="launch (Times Square)",
    )
    g = yaml.safe_load((EX / f"{adapter}.adapter.yaml").read_text(encoding="utf-8"))[
        "location_to_global"
    ]
    for n, p in g.items():
        if n == "home":
            continue
        x, y = merc(p["lon"], p["lat"])
        star = n.startswith("site_p") or n == "dropoff"
        ax.plot(
            x,
            y,
            "*" if star else "o",
            color="#ff3b3b" if star else "white",
            ms=18 if star else 10,
            mec="black",
        )
        ax.annotate(
            n,
            (x, y),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=10,
            color="white",
            bbox=dict(boxstyle="round,pad=0.2", fc="black", alpha=0.6, ec="none"),
        )
    pad = 60
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    cx.add_basemap(
        ax, source=source, zoom=18, attribution="Imagery: Esri World Imagery"
    )
    ax.set_axis_off()
    ax.set_title(
        f"URML on ArduPilot: {title}\nsimulated flight, Gemini-emitted program, max alt {max(alts):.0f} m",
        fontsize=12,
    )
    ax.legend(loc="lower left")
    out = f"{name}.map.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print("wrote", out)
