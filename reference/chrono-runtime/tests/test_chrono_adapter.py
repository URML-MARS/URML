"""Hermetic unit tests for ChronoAdapter — no pychrono install needed.

A fake ``pychrono`` module is injected into ``sys.modules`` so
``_require_pychrono`` resolves and ``_sim`` runs against a controllable
double (the same technique px4-runtime / mujoco-runtime use). The fake
``ChSystem`` accumulates simulated time per ``DoStepDynamics`` call and
reports zero contacts, which is enough to exercise every Protocol path
and the validation-evidence payload.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType

import pytest
from urml_ros2_runtime.substrate.base import ManipulationResult, ROSAdapter


class _FakeSystem:
    """A minimal ChSystem double: accumulates time, reports no contacts."""

    def __init__(self) -> None:
        self.t = 0.0
        self.steps = 0

    def DoStepDynamics(self, step: float) -> None:  # noqa: N802 (mirror Chrono API)
        self.t += float(step)
        self.steps += 1

    def GetChTime(self) -> float:  # noqa: N802
        return self.t

    def GetNcontacts(self) -> int:  # noqa: N802
        return 0


class _FakePychrono(ModuleType):
    def __init__(self) -> None:
        super().__init__("pychrono")
        self.systems: list[_FakeSystem] = []
        outer = self

        def _make() -> _FakeSystem:
            s = _FakeSystem()
            outer.systems.append(s)
            return s

        self.ChSystemNSC = _make  # type: ignore[attr-defined]
        self.ChSystemSMC = _make  # type: ignore[attr-defined]


@pytest.fixture
def fake_pychrono() -> Iterator[_FakePychrono]:
    fake = _FakePychrono()
    saved = sys.modules.get("pychrono")
    sys.modules["pychrono"] = fake
    try:
        yield fake
    finally:
        if saved is None:
            sys.modules.pop("pychrono", None)
        else:
            sys.modules["pychrono"] = saved


def test_navigation_measure_scan_lifecycle(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig
    from urml_chrono_runtime.adapter import DriverSegment

    cfg = ChronoConfig(
        step_size=1e-3,
        steps_per_command=50,
        location_to_segment={"ridge_waypoint": DriverSegment(driver=[0.8, 0.1, 0.0])},
    )
    with ChronoAdapter(cfg) as sim:
        assert isinstance(sim, ROSAdapter)
        ok = sim.send_navigation_goal(location="ridge_waypoint")
        assert ok.success and ok.final_pose is not None
        assert ok.final_pose["driver0"] == 0.8 and ok.final_pose["driver1"] == 0.1
        # 50 steps at 1e-3 advanced the engine; the evidence is real ChSystem state.
        assert ok.final_pose["sim_time"] == pytest.approx(0.05)
        assert ok.final_pose["n_contacts"] == 0.0
        assert fake_pychrono.systems and fake_pychrono.systems[0].steps >= 50

        miss = sim.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")

        assert sim.wait_passively(duration_seconds=0.1).success

        meas = sim.take_measurement(what="dynamics", target=None, sensor=None)
        assert meas.success and meas.payload is not None
        assert meas.payload["backend"] == "pychrono"
        assert meas.payload["unit"] == "contacts"
        assert meas.payload["what"] == "dynamics"
        assert meas.payload["sim_time"] > 0.0  # time accumulated across the prior steps

        assert sim.run_scan(
            area={}, pattern="serpentine", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success  # documented stub success


def test_smc_system_type_is_honored(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig

    sim = ChronoAdapter(ChronoConfig(system_type="SMC", steps_per_command=3))
    assert sim.wait_passively(duration_seconds=0.0).success
    assert fake_pychrono.systems and fake_pychrono.systems[0].steps == 3


def test_unsupported_and_sim_sentinels(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig

    sim = ChronoAdapter(ChronoConfig())
    bare: ManipulationResult = sim.send_manipulation_goal(action="grasp")
    assert bare.success is False
    assert bare.reason is not None and bare.reason.startswith("not_supported_in_base_sim")
    for r in (sim.send_takeoff_goal(altitude=1.0), sim.send_land_goal(), sim.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_sim")
    prog = sim.call_named_program(name="anything")
    assert prog.success is False and prog.reason is not None
    assert prog.reason.startswith("not_supported_on_chrono_sim")


def test_missing_pychrono_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without pychrono raises a clear, conda-pointing error.

    Setting the sys.modules entry to None forces ``import pychrono`` to
    raise ImportError deterministically, whether or not pychrono is
    actually installed in the test environment.
    """
    from urml_chrono_runtime import ChronoAdapter

    monkeypatch.setitem(sys.modules, "pychrono", None)
    with pytest.raises(RuntimeError, match=r"conda-forge"):
        ChronoAdapter()


def test_conformance_runner_accepts_factory(fake_pychrono: _FakePychrono) -> None:
    from urml_conformance import ConformanceRunner

    from urml_chrono_runtime import ChronoAdapter, ChronoConfig

    assert ConformanceRunner(adapter_factory=lambda: ChronoAdapter(ChronoConfig())) is not None
