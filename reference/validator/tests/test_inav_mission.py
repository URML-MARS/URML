"""The INAV mission example must be deterministic and true.

Mirrors the VLA / planning / choreo export guards: the generator is
deterministic, the committed ``inav-mission-report.txt`` matches it, and the
validate-then-compile flow decides correctly (a valid mission compiles to an INAV
waypoint list; a leg that crosses the road is rejected at the geofence before any
compile). The worked example for the iNavFlight/inav engagement
(iNavFlight/inav#11651).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "inav-mission"
GEN_PATH = EX / "compile_inav_mission.py"
COMMITTED = EX / "inav-mission-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("compile_inav_mission", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/inav-mission/inav-mission-report.txt is stale; "
        "run `python examples/inav-mission/compile_inav_mission.py` and commit."
    )


def test_valid_compiles_invalid_geofenced() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # The admissible mission compiles to an INAV waypoint mission.
    assert report.count("[COMPILED]") == 1
    assert "WP1  WAYPOINT" in report and "RTH" in report and "LAND" in report
    # The across-the-road leg is rejected at the geofence, nothing compiled.
    assert report.count("[REJECTED]") == 1
    assert "envelope.geofence_violation" in report
    assert "nothing compiled to INAV." in report
