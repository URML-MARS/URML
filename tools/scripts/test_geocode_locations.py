"""Hermetic tests for geocode_locations.py: a stub resolver, no network."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geocode_locations as g  # noqa: E402


def _stub(address: str) -> tuple[float, float]:
    table = {"A": (32.0, 34.0), "B": (32.001, 34.0)}
    return table[address]


def test_offset_roundtrip() -> None:
    lat, lon = g.offset_latlon(32.0, 34.0, 100.0, 50.0)
    north, east = g.enu_offset(32.0, 34.0, lat, lon)
    assert math.isclose(north, 100.0, abs_tol=0.01)
    assert math.isclose(east, 50.0, abs_tol=0.01)


def test_orbit_points_are_evenly_spaced() -> None:
    pts = g.orbit_points(32.0, 34.0, 40.0, 5)
    assert len(pts) == 5
    assert pts[0][2] == 0.0 and math.isclose(pts[1][2], 72.0)
    for plat, plon, _ in pts:
        north, east = g.enu_offset(32.0, 34.0, plat, plon)
        assert math.isclose(math.hypot(north, east), 40.0, abs_tol=0.05)


def test_build_bindings_orbit_and_look_at() -> None:
    bindings, _ = g.build_bindings(
        {"home": "A", "site": "B"},
        _stub,
        fixes={},
        alt_agl=100.0,
        orbit="site",
        radius_m=40.0,
        points=5,
        look_at="site",
    )
    assert bindings["home"]["alt_agl"] == 0.0
    assert bindings["site"]["alt_agl"] == 100.0
    assert "look_at" not in bindings["site"]
    for k in range(1, 6):
        e = bindings[f"site_p{k}"]
        assert e["alt_agl"] == 100.0
        assert e["look_at"] == {"lat": 32.001, "lon": 34.0}


def test_fix_skips_resolver() -> None:
    def _boom(_: str) -> tuple[float, float]:
        raise AssertionError("resolver must not be called for fixed names")

    bindings, _ = g.build_bindings(
        {"home": "A"}, _boom, fixes={"home": (1.0, 2.0)}, alt_agl=10, orbit=None, radius_m=1, points=1, look_at=None
    )
    assert bindings["home"] == {"lat": 1.0, "lon": 2.0, "alt_agl": 0.0}


def test_main_writes_and_merges_config(tmp_path: Path) -> None:
    addr = tmp_path / "addr.yaml"
    addr.write_text("home: A\nsite: B\n", encoding="utf-8")
    out = tmp_path / "adapter.yaml"
    out.write_text("connection_url: COM5\ncamera: {kind: digicam}\n", encoding="utf-8")
    rc = g.main(
        [str(addr), "--out", str(out), "--alt-agl", "50", "--orbit", "site", "--points", "3", "--stamp", "2026-01-01"],
        resolver=_stub,
    )
    assert rc == 0
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["connection_url"] == "COM5"  # preserved
    assert data["camera"] == {"kind": "digicam"}
    assert set(data["location_to_global"]) == {"home", "site", "site_p1", "site_p2", "site_p3"}
    assert "geocoded_at: 2026-01-01" in out.read_text(encoding="utf-8")


def test_provider_none_refuses_network(tmp_path: Path, capsys: object) -> None:
    addr = tmp_path / "addr.yaml"
    addr.write_text("home: somewhere\n", encoding="utf-8")
    assert g.main([str(addr), "--provider", "none"]) == 1


def test_declared_locations_block_is_relative_to_home() -> None:
    bindings = {
        "home": {"lat": 32.0, "lon": 34.0, "alt_agl": 0.0},
        "site": {"lat": 32.0009, "lon": 34.0, "alt_agl": 100.0},
    }
    text = g.declared_locations_block(bindings)
    assert "name: site" in text
    assert "x: 100.1" in text or "x: 100.0" in text
    assert "frame: agl" in text
