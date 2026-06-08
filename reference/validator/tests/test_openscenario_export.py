"""The URML to OpenSCENARIO example must be deterministic and must not lie.

Mirrors the README-hero-SVG guard (test_demo_svg.py):

  * ``examples/scenario/urml_to_openscenario.py`` is deterministic, and the
    committed ``examples/scenario/husky-patrol.xosc`` is exactly what it
    produces (a stale or hand-edited asset fails CI).
  * The generator validates the URML program before emitting, and the emitted
    scenario faithfully reflects the program: one OpenSCENARIO event with an
    ``AcquirePositionAction`` per ``move_to``, at the manifest's declared world
    positions.
"""

from __future__ import annotations

import importlib.util
import xml.dom.minidom
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
GEN_PATH = REPO_ROOT / "examples" / "scenario" / "urml_to_openscenario.py"
COMMITTED_XOSC = REPO_ROOT / "examples" / "scenario" / "husky-patrol.xosc"


def _load_gen():
    spec = importlib.util.spec_from_file_location("urml_to_openscenario", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic_and_well_formed() -> None:
    gen = _load_gen()
    a = gen.render_husky_patrol()
    b = gen.render_husky_patrol()
    assert a == b, "render_husky_patrol() is not deterministic"
    xml.dom.minidom.parseString(a)  # raises if not well-formed XML
    assert a.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<OpenSCENARIO>" in a and "</OpenSCENARIO>" in a


def test_committed_xosc_matches_generator() -> None:
    """Guard against a stale committed asset (regenerate before commit)."""
    gen = _load_gen()
    assert COMMITTED_XOSC.exists(), f"missing {COMMITTED_XOSC}"
    on_disk = COMMITTED_XOSC.read_text(encoding="utf-8")
    assert on_disk == gen.render_husky_patrol(), (
        "examples/scenario/husky-patrol.xosc is stale; "
        "run `python examples/scenario/urml_to_openscenario.py` and commit."
    )


def test_one_event_per_move_to_at_declared_positions() -> None:
    """The scenario reflects the program: one AcquirePosition event per move_to."""
    gen = _load_gen()
    program = gen._load(gen.DEFAULT_PROGRAM)
    manifest = gen._load(gen.DEFAULT_MANIFEST)
    n_moves = len(gen._iter_move_to(program["behavior"]))
    assert n_moves == 3  # husky-patrol: waypoint_a, waypoint_b, charge_point

    dom = xml.dom.minidom.parseString(gen.render_husky_patrol())
    assert dom.getElementsByTagName("Event").length == n_moves
    assert dom.getElementsByTagName("AcquirePositionAction").length == n_moves

    # Every acquired position is a declared-location pose from the manifest.
    declared = {(p["pose"].get("x"), p["pose"].get("y")) for p in manifest["declared_locations"]}
    for wp in dom.getElementsByTagName("AcquirePositionAction"):
        world = wp.getElementsByTagName("WorldPosition")[0]
        x = float(world.getAttribute("x"))
        y = float(world.getAttribute("y"))
        assert (x, y) in declared


def test_invalid_program_is_refused() -> None:
    """The generator refuses to emit a scenario for inadmissible intent."""
    gen = _load_gen()
    manifest = gen._load(gen.DEFAULT_MANIFEST)
    bad = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "nowhere_declared"}}]},
    }
    with pytest.raises(ValueError):
        gen.render_xosc(bad, manifest)
