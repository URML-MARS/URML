"""The URML to Crazyswarm2 fleet example must be deterministic and must not lie.

Mirrors the esmini / ros2_kortex export guards:

  * ``examples/fleet/crazyswarm2/urml_to_crazyswarm2.py`` is deterministic, and
    the committed ``dispatch-plan.txt`` is exactly what it produces.
  * The generator validates the whole fleet with ``validate_fleet`` first, maps
    onto the real crazyflie_interfaces services, and refuses to emit when two
    drones are sent to the same formation corner (deconfliction).
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "fleet" / "crazyswarm2"
GEN_PATH = EX / "urml_to_crazyswarm2.py"
COMMITTED = EX / "dispatch-plan.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("urml_to_crazyswarm2", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_swarm_formation() == gen.render_swarm_formation()
    assert gen.render_swarm_formation().startswith("URML -> Crazyswarm2 dispatch plan")


def test_committed_plan_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_swarm_formation(), (
        "examples/fleet/crazyswarm2/dispatch-plan.txt is stale; "
        "run `python examples/fleet/crazyswarm2/urml_to_crazyswarm2.py` and commit."
    )


def test_plan_targets_real_crazyswarm2_services() -> None:
    gen = _load_gen()
    plan = gen.render_swarm_formation()
    for iface in (
        "/cf1/takeoff",
        "crazyflie_interfaces/srv/Takeoff",
        "/cf1/go_to",
        "crazyflie_interfaces/srv/GoTo",
        "crazyflie_interfaces/srv/Land",
    ):
        assert iface in plan, iface
    assert "validate_fleet: ACCEPTED" in plan
    assert "Barrier" in plan  # the rendezvous is shown


def test_two_drones_to_same_corner_is_refused() -> None:
    """A deconfliction conflict is rejected before any command goes out."""
    gen = _load_gen()
    roster, members, program = gen._load_fleet()
    program = copy.deepcopy(program)
    for step in program["behavior"]["steps"]:
        if step.get("type") == "parallel" and any("move_to" in (b.get("body") or {}) for b in step["branches"]):
            for b in step["branches"]:
                if b["member"] == "cf2":
                    b["body"] = {"move_to": {"location": "corner_a"}}  # collide with cf1
    with pytest.raises(ValueError, match="concurrent_shared_workspace"):
        gen.render_dispatch_plan(roster, members, program)
