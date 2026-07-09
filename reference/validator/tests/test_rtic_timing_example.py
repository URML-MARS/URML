"""The RTIC cyclic-timing worked example must be deterministic and true.

Mirrors the robotiq-hande / vitra guards: the generator is deterministic, the
committed ``rtic-timing-report.txt`` matches it, a coherent RFC-0016 realtime
declaration validates, and an incoherent one (watchdog shorter than one cycle) is
rejected with the RFC-0016 code. For rtic-rs/rtic#1188.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "rtic-timing"
GEN_PATH = EX / "run_rtic.py"
COMMITTED = EX / "rtic-timing-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_rtic", GEN_PATH)
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
        "examples/rtic-timing/rtic-timing-report.txt is stale; "
        "run `python examples/rtic-timing/run_rtic.py` and commit."
    )


def test_coherent_validates_incoherent_rejected() -> None:
    """The one RFC-0016 check: watchdog must allow at least one control cycle."""
    import copy

    gen = _load_gen()
    from urml_validator import validate

    manifest = gen._load(gen.MANIFEST)

    ok = validate(gen._PROGRAM, manifest, profiles=gen._PROFILES, policy=None)
    assert ok.accepted, "watchdog 50 ms >= cycle 10 ms is coherent"

    bad = copy.deepcopy(manifest)
    bad["realtime"]["watchdog_ms"] = 5.0
    over = validate(gen._PROGRAM, bad, profiles=gen._PROFILES, policy=None)
    assert not over.accepted, "watchdog 5 ms < cycle 10 ms is incoherent"
    assert "capability.watchdog_shorter_than_cycle" in {e.code_str for e in over.errors}


def test_report_shows_mapping_and_altitude() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] watchdog 50.0 ms >= cycle 10.0 ms" in report
    assert "[REJECTED] watchdog 5.0 ms < cycle 10.0 ms" in report
    # The mapping onto an RTIC task set is present and honest about altitude.
    assert "a periodic task released every 10.0 ms" in report
    assert "URML does not schedule, compute WCET, or prove schedulability." in report
