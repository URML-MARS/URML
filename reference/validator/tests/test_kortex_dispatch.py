"""The URML to ros2_kortex example must be deterministic and must not lie.

Mirrors the esmini export guard (test_openscenario_export.py):

  * ``examples/manipulation/kortex/urml_to_kortex.py`` is deterministic, and the
    committed ``dispatch-plan.txt`` is exactly what it produces (a stale or
    hand-edited asset fails CI).
  * The generator validates the URML program before emitting, and refuses to
    emit for inadmissible intent (an over-rating grasp force).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "manipulation" / "kortex"
GEN_PATH = EX / "urml_to_kortex.py"
COMMITTED = EX / "dispatch-plan.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("urml_to_kortex", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    a = gen.render_pick_place()
    b = gen.render_pick_place()
    assert a == b, "render_pick_place() is not deterministic"
    assert a.startswith("URML -> ros2_kortex dispatch plan")


def test_committed_plan_matches_generator() -> None:
    """Guard against a stale committed asset (regenerate before commit)."""
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    on_disk = COMMITTED.read_text(encoding="utf-8")
    assert on_disk == gen.render_pick_place(), (
        "examples/manipulation/kortex/dispatch-plan.txt is stale; "
        "run `python examples/manipulation/kortex/urml_to_kortex.py` and commit."
    )


def test_plan_targets_real_ros2_kortex_interfaces() -> None:
    gen = _load_gen()
    plan = gen.render_pick_place()
    assert "joint_trajectory_controller/follow_joint_trajectory" in plan
    assert "robotiq_gripper_controller/gripper_cmd" in plan
    assert "control_msgs/action/GripperCommand" in plan
    # The static gate is stated, and the gripper bound is shown.
    assert "validation: ACCEPTED" in plan
    assert "140" in plan  # the gripper's force_max_n rating


def test_over_rating_grasp_is_refused() -> None:
    """A grasp force above the gripper rating is rejected before any goal."""
    gen = _load_gen()
    manifest = gen._load(gen.DEFAULT_MANIFEST)
    bad = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"move_to": {"location": "pick_bin"}},
                {"detect": {"object": "widget_red", "store_as": "t"}},
                {"grasp": {"target": "$t", "force": 200.0}},
            ],
        },
    }
    with pytest.raises(ValueError):
        gen.render_dispatch_plan(bad, manifest)
