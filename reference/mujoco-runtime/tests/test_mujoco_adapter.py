"""Hermetic unit tests for MujocoAdapter — no mujoco install needed.

A fake ``mujoco`` module is injected into ``sys.modules`` so
``_require_mujoco`` resolves and ``_sim`` runs against a controllable
double (the same technique px4-runtime / marine-runtime use).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import ManipulationResult, ROSAdapter


class _FakeModel:
    pass


class _FakeData:
    def __init__(self) -> None:
        self.ctrl = [0.0, 0.0, 0.0]
        self.sensordata = [42.0]


class _FakeMujoco(ModuleType):
    def __init__(self) -> None:
        super().__init__("mujoco")
        self.steps = 0
        self.last_data: _FakeData | None = None

        class MjModel:
            @staticmethod
            def from_xml_path(path: str) -> _FakeModel:
                return _FakeModel()

        outer = self

        def MjData(model: _FakeModel) -> _FakeData:  # noqa: N802
            d = _FakeData()
            outer.last_data = d
            return d

        def mj_step(model: _FakeModel, data: _FakeData) -> None:
            outer.steps += 1

        self.MjModel = MjModel  # type: ignore[attr-defined]
        self.MjData = MjData  # type: ignore[attr-defined]
        self.mj_step = mj_step  # type: ignore[attr-defined]


@pytest.fixture
def fake_mujoco() -> Iterator[_FakeMujoco]:
    fake = _FakeMujoco()
    saved = sys.modules.get("mujoco")
    sys.modules["mujoco"] = fake
    try:
        yield fake
    finally:
        if saved is None:
            sys.modules.pop("mujoco", None)
        else:
            sys.modules["mujoco"] = saved


def test_navigation_measure_scan_lifecycle(fake_mujoco: _FakeMujoco) -> None:
    from urml_mujoco_runtime import MujocoAdapter, MujocoConfig
    from urml_mujoco_runtime.adapter import ControlTarget

    cfg = MujocoConfig(
        model_path="model.xml",
        steps_per_command=5,
        location_to_target={"home_pose": ControlTarget(ctrl=[1.0, 2.0, 3.0])},
    )
    with MujocoAdapter(cfg) as sim:
        assert isinstance(sim, ROSAdapter)
        ok = sim.send_navigation_goal(location="home_pose")
        assert ok.success and ok.final_pose == {"ctrl0": 1.0, "ctrl1": 2.0, "ctrl2": 3.0}
        assert fake_mujoco.steps >= 5, "the engine was stepped"
        assert fake_mujoco.last_data is not None and fake_mujoco.last_data.ctrl[0] == 1.0
        miss = sim.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert sim.wait_passively(duration_seconds=0.1).success
        meas = sim.take_measurement(what="state", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 42.0
        assert sim.run_scan(
            area={}, pattern="serpentine", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success  # documented stub success


def test_unsupported_and_sim_sentinels(fake_mujoco: _FakeMujoco) -> None:
    from urml_mujoco_runtime import MujocoAdapter, MujocoConfig

    sim = MujocoAdapter(MujocoConfig(model_path="model.xml"))
    bare: ManipulationResult = sim.send_manipulation_goal(action="grasp")
    assert bare.success is False
    assert bare.reason is not None and bare.reason.startswith("not_supported_in_base_sim")
    for r in (sim.send_takeoff_goal(altitude=1.0), sim.send_land_goal(), sim.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_sim")


def test_model_path_required_is_actionable(fake_mujoco: _FakeMujoco) -> None:
    """A construction with no model_path fails clearly at first sim use, not opaquely."""
    from urml_mujoco_runtime import MujocoAdapter

    sim = MujocoAdapter()  # default config, empty model_path
    with pytest.raises(RuntimeError, match=r"model_path not configured"):
        sim.send_navigation_goal(location="x")


def test_missing_mujoco_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without the [sim] extra raises a clear error.

    Setting the sys.modules entry to None forces ``import mujoco`` to
    raise ImportError deterministically, whether or not mujoco is
    actually installed in the test environment.
    """
    from urml_mujoco_runtime import MujocoAdapter

    monkeypatch.setitem(sys.modules, "mujoco", None)
    with pytest.raises(RuntimeError, match=r"\[sim\] extra"):
        MujocoAdapter()


def test_conformance_runner_accepts_factory(fake_mujoco: _FakeMujoco) -> None:
    from urml_conformance import ConformanceRunner

    from urml_mujoco_runtime import MujocoAdapter, MujocoConfig

    assert ConformanceRunner(adapter_factory=lambda: MujocoAdapter(MujocoConfig(model_path="m.xml"))) is not None
