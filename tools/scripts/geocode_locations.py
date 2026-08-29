"""geocode_locations.py — turn street addresses into ArduPilot adapter bindings.

Configuration-time tool, never a runtime dependency. URML reference
runtimes execute fully offline; the one network step in a drone
deployment (address -> lat/lon) happens here, once, and its output is
committed next to the URML artifacts as an adapter config.

Input (YAML):

    home: "1 Example Street, Example City"
    site: "10 Example Street, Example City"

Output: a merged ``location_to_global`` block in the adapter config, plus
a printed ``declared_locations`` block for the manifest with local-metre
ENU offsets from ``home``, so the validator's geofence and altitude
passes have coordinates to check.

Usage:

    python tools/scripts/geocode_locations.py addresses.yaml \
        --out examples/drone/site.adapter.yaml \
        --alt-agl 100 --orbit site --radius-m 40 --points 5 --look-at site

    # No network: supply coordinates directly (also what the tests do).
    python tools/scripts/geocode_locations.py addresses.yaml \
        --fix home=32.0853,34.7818 --fix site=32.0858,34.7818 ...

The default resolver is Nominatim (OpenStreetMap) with a descriptive
User-Agent and a one-request-per-second pace, per its usage policy.
``--provider none`` refuses to touch the network and requires every
address to be supplied with ``--fix``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

Resolver = Callable[[str], tuple[float, float]]

_EARTH_RADIUS_M = 6_371_000.0
_USER_AGENT = "urml-geocode-locations/0.1 (+https://urml.dev)"


def nominatim_resolver(address: str) -> tuple[float, float]:
    """Resolve one address via Nominatim. One request per second, by policy."""
    query = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{query}",
        headers={"User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 - fixed https host
        data = json.loads(resp.read().decode("utf-8"))
    time.sleep(1.0)
    if not data:
        raise LookupError(f"no geocoding result for {address!r}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def refusing_resolver(address: str) -> tuple[float, float]:
    raise LookupError(f"--provider none: supply --fix <name>=<lat>,<lon> for {address!r}")


def offset_latlon(lat: float, lon: float, north_m: float, east_m: float) -> tuple[float, float]:
    """Move a WGS84 point by local metres (flat-earth, fine at survey scale)."""
    dlat = north_m / _EARTH_RADIUS_M
    dlon = east_m / (_EARTH_RADIUS_M * math.cos(math.radians(lat)))
    return lat + math.degrees(dlat), lon + math.degrees(dlon)


def enu_offset(lat0: float, lon0: float, lat: float, lon: float) -> tuple[float, float]:
    """Local (north, east) metres of (lat, lon) from (lat0, lon0)."""
    north = math.radians(lat - lat0) * _EARTH_RADIUS_M
    east = math.radians(lon - lon0) * _EARTH_RADIUS_M * math.cos(math.radians(lat0))
    return north, east


def orbit_points(lat: float, lon: float, radius_m: float, points: int) -> list[tuple[float, float, float]]:
    """``points`` stations evenly spaced on a circle, starting due north, clockwise.

    Returns (lat, lon, bearing_deg) per station.
    """
    out = []
    for k in range(points):
        bearing = 360.0 * k / points
        north = radius_m * math.cos(math.radians(bearing))
        east = radius_m * math.sin(math.radians(bearing))
        plat, plon = offset_latlon(lat, lon, north, east)
        out.append((plat, plon, bearing))
    return out


def build_bindings(
    addresses: dict[str, str],
    resolver: Resolver,
    *,
    fixes: dict[str, tuple[float, float]],
    alt_agl: float,
    orbit: str | None,
    radius_m: float,
    points: int,
    look_at: str | None,
) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[float, float]]]:
    """Resolve every address, then expand the orbit. Returns (bindings, raw coords)."""
    coords: dict[str, tuple[float, float]] = {}
    for name, address in addresses.items():
        coords[name] = fixes[name] if name in fixes else resolver(address)
    for name, fix in fixes.items():
        coords.setdefault(name, fix)

    bindings: dict[str, dict[str, Any]] = {}
    look = None
    if look_at is not None:
        if look_at not in coords:
            raise KeyError(f"--look-at {look_at!r} is not a resolved location")
        look = {"lat": round(coords[look_at][0], 7), "lon": round(coords[look_at][1], 7)}

    for name, (lat, lon) in coords.items():
        if name == "home":
            bindings[name] = {"lat": round(lat, 7), "lon": round(lon, 7), "alt_agl": 0.0}
            continue
        entry: dict[str, Any] = {"lat": round(lat, 7), "lon": round(lon, 7), "alt_agl": float(alt_agl)}
        if look is not None and name != look_at:
            entry["look_at"] = dict(look)
        bindings[name] = entry

    if orbit is not None:
        if orbit not in coords:
            raise KeyError(f"--orbit {orbit!r} is not a resolved location")
        clat, clon = coords[orbit]
        for k, (plat, plon, _bearing) in enumerate(orbit_points(clat, clon, radius_m, points), start=1):
            entry = {"lat": round(plat, 7), "lon": round(plon, 7), "alt_agl": float(alt_agl)}
            entry["look_at"] = {"lat": round(clat, 7), "lon": round(clon, 7)}
            bindings[f"{orbit}_p{k}"] = entry
    return bindings, coords


def declared_locations_block(bindings: dict[str, dict[str, Any]]) -> str:
    """Manifest snippet: local-metre `agl` poses relative to `home`."""
    if "home" not in bindings:
        return "# (no `home` binding; cannot express local offsets)\n"
    lat0, lon0 = bindings["home"]["lat"], bindings["home"]["lon"]
    lines = ["declared_locations:"]
    for name, entry in bindings.items():
        north, east = enu_offset(lat0, lon0, entry["lat"], entry["lon"])
        lines.append(f"  - name: {name}")
        lines.append(f"    pose: {{ x: {north:.1f}, y: {east:.1f}, z: {entry['alt_agl']:.1f} }}")
        lines.append("    frame: agl")
    return "\n".join(lines) + "\n"


def merge_into_config(path: Path, bindings: dict[str, dict[str, Any]], *, provider: str, stamp: str) -> None:
    """Write/merge `location_to_global` into an adapter config, preserving other keys."""
    existing: dict[str, Any] = {}
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            existing = yaml.safe_load(fh) or {}
    existing.setdefault("location_to_global", {})
    existing["location_to_global"].update(bindings)
    header = (
        "# location_to_global written by tools/scripts/geocode_locations.py\n"
        f"# provider: {provider}   geocoded_at: {stamp}\n"
        "# The runtime never geocodes; edit or regenerate this file, never the program.\n"
    )
    path.write_text(header + yaml.safe_dump(existing, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _parse_fix(text: str) -> tuple[str, tuple[float, float]]:
    name, _, coords = text.partition("=")
    lat_s, _, lon_s = coords.partition(",")
    if not (name and lat_s and lon_s):
        raise argparse.ArgumentTypeError(f"--fix expects name=lat,lon, got {text!r}")
    return name, (float(lat_s), float(lon_s))


def main(argv: list[str] | None = None, *, resolver: Resolver | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("addresses", type=Path, help="YAML mapping of location name -> street address.")
    parser.add_argument("--out", type=Path, default=None, help="Adapter config to write / merge into.")
    parser.add_argument("--alt-agl", type=float, default=30.0, help="Altitude (m above home) for every non-home location.")
    parser.add_argument("--orbit", default=None, help="Location name to ring with orbit stations.")
    parser.add_argument("--radius-m", type=float, default=40.0)
    parser.add_argument("--points", type=int, default=5)
    parser.add_argument("--look-at", default=None, help="Location every station yaws toward.")
    parser.add_argument("--fix", type=_parse_fix, action="append", default=[], help="name=lat,lon; skips lookup.")
    parser.add_argument("--provider", choices=("nominatim", "none"), default="nominatim")
    parser.add_argument("--stamp", default=None, help="Override the geocoded_at stamp (tests).")
    args = parser.parse_args(argv)

    with args.addresses.open(encoding="utf-8") as fh:
        addresses = yaml.safe_load(fh) or {}
    if not isinstance(addresses, dict):
        print("addresses file must be a YAML mapping of name -> address", file=sys.stderr)
        return 2

    fixes = dict(args.fix)
    if resolver is None:
        resolver = nominatim_resolver if args.provider == "nominatim" else refusing_resolver
    try:
        bindings, _ = build_bindings(
            {k: str(v) for k, v in addresses.items()},
            resolver,
            fixes=fixes,
            alt_agl=args.alt_agl,
            orbit=args.orbit,
            radius_m=args.radius_m,
            points=args.points,
            look_at=args.look_at,
        )
    except (LookupError, KeyError) as exc:
        print(f"geocode failed: {exc}", file=sys.stderr)
        return 1

    stamp = args.stamp or datetime.now(UTC).strftime("%Y-%m-%d")
    if args.out is not None:
        merge_into_config(args.out, bindings, provider=args.provider, stamp=stamp)
        print(f"wrote {len(bindings)} location(s) to {args.out}", file=sys.stderr)
    else:
        print(yaml.safe_dump({"location_to_global": bindings}, sort_keys=False))
    print("# manifest snippet (local metres from home, frame agl):")
    print(declared_locations_block(bindings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
