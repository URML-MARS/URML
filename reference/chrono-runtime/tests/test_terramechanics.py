"""Hermetic unit tests for the Chrono terramechanics scene — no pychrono needed.

An enriched fake ``pychrono`` (with a ``vehicle`` submodule, an SCM terrain
double, and a rigid-body double that sinks and tilts a fixed amount per step) is
injected into ``sys.modules``. The fake makes the scene's physics reads
deterministic, so the test verifies the URML-side behaviour: selecting the
deformable scene from ``ChronoConfig.scene``, driving the rig with the resolved
driver segment, and shaping sinkage / contact force / tip margin into the
validation-evidence payload. The live SCM construction against a real PyChrono
build is the calibration step (``chrono-integration.yml``), not this suite.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterator
from types import ModuleType

import pytest

_SINK_PER_STEP = 5e-4  # m the rig sinks per DoStepDynamics step
_TILT_PER_STEP = 2e-4  # rad the rig rolls per step


class _Vec:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x, self.y, self.z = float(x), float(y), float(z)

    def Length(self) -> float:  # noqa: N802 (mirror Chrono API)
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


class _Quat:
    def __init__(self, e0: float, e1: float, e2: float, e3: float) -> None:
        self.e0, self.e1, self.e2, self.e3 = e0, e1, e2, e3


class _Body:
    def __init__(self) -> None:
        self._z = 0.0
        self._roll = 0.0
        self.mass = 0.0
        self.forces: list[_Vec] = []

    def SetMass(self, m: float) -> None:  # noqa: N802
        self.mass = float(m)

    def GetPos(self) -> _Vec:  # noqa: N802
        return _Vec(0.0, 0.0, self._z)

    def GetRot(self) -> _Quat:  # noqa: N802
        h = self._roll / 2.0
        return _Quat(math.cos(h), math.sin(h), 0.0, 0.0)

    def EmptyAccumulators(self) -> None:  # noqa: N802
        self.forces = []

    def AccumulateForce(self, f: _Vec, pos: _Vec, local: bool) -> None:  # noqa: N802
        self.forces.append(f)


class _SystemSMC:
    def __init__(self) -> None:
        self.t = 0.0
        self.bodies: list[_Body] = []

    def AddBody(self, b: _Body) -> None:  # noqa: N802
        self.bodies.append(b)

    def DoStepDynamics(self, step: float) -> None:  # noqa: N802
        self.t += float(step)
        for b in self.bodies:
            b._z -= _SINK_PER_STEP
            b._roll += _TILT_PER_STEP

    def GetChTime(self) -> float:  # noqa: N802
        return self.t

    def GetNcontacts(self) -> int:  # noqa: N802
        return len(self.bodies)


class _SCMTerrain:
    def __init__(self, system: _SystemSMC) -> None:
        self.system = system
        self.soil: tuple = ()
        self.dims: tuple = ()

    def SetSoilParameters(self, *args: float) -> None:  # noqa: N802
        self.soil = args

    def Initialize(self, *args: float) -> None:  # noqa: N802
        self.dims = args

    def Advance(self, step: float) -> None:  # noqa: N802
        pass

    def GetContactForceBody(self, body: _Body) -> _Vec:  # noqa: N802
        return _Vec(0.0, 0.0, body.mass * 9.81)  # normal support force = weight


class _FakePychrono(ModuleType):
    def __init__(self) -> None:
        super().__init__("pychrono")
        self.ChSystemSMC = _SystemSMC  # type: ignore[attr-defined]
        self.ChSystemNSC = _SystemSMC  # type: ignore[attr-defined]
        self.ChBody = _Body  # type: ignore[attr-defined]
        self.ChVector3d = _Vec  # type: ignore[attr-defined]
        veh = ModuleType("pychrono.vehicle")
        veh.SCMTerrain = _SCMTerrain  # type: ignore[attr-defined]
        self.vehicle = veh  # type: ignore[attr-defined]


@pytest.fixture
def fake_pychrono() -> Iterator[_FakePychrono]:
    fake = _FakePychrono()
    saved = sys.modules.get("pychrono")
    saved_veh = sys.modules.get("pychrono.vehicle")
    sys.modules["pychrono"] = fake
    sys.modules["pychrono.vehicle"] = fake.vehicle
    try:
        yield fake
    finally:
        for key, val in (("pychrono", saved), ("pychrono.vehicle", saved_veh)):
            if val is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = val


def test_terramechanics_scene_enriches_evidence(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig
    from urml_chrono_runtime.adapter import DriverSegment

    steps = 50
    cfg = ChronoConfig(
        scene="terramechanics",
        terrain_fidelity="deformable",
        step_size=1e-3,
        steps_per_command=steps,
        location_to_segment={"ridge": DriverSegment(driver=[0.8])},
    )
    with ChronoAdapter(cfg) as sim:
        r = sim.send_navigation_goal(location="ridge")
        assert r.success and r.final_pose is not None

        meas = sim.take_measurement(what="dynamics", target=None, sensor=None)
        assert meas.payload is not None
        ev = meas.payload
        # Richer terramechanics evidence is present and numeric.
        assert ev["terrain_model"] == "scm_deformable"
        assert ev["sinkage_m"] == pytest.approx(steps * _SINK_PER_STEP)  # 0.025 m
        assert ev["max_contact_force_n"] == pytest.approx(250.0 * 9.81)  # rig weight
        # tip margin = threshold(35) - roll(50*2e-4 rad = 0.573 deg)
        assert ev["tip_margin_deg"] == pytest.approx(35.0 - math.degrees(steps * _TILT_PER_STEP))
        # The base evidence still flows.
        assert ev["terrain_class"] == "deformable"
        assert ev["backend"] == "pychrono"
        assert "terramechanics_notes" not in ev  # all reads succeeded against the fake


def test_driver_force_applied_to_rig(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig, TerramechanicsParams
    from urml_chrono_runtime.adapter import DriverSegment

    cfg = ChronoConfig(
        scene="terramechanics",
        steps_per_command=5,
        terramechanics=TerramechanicsParams(drawbar_gain_n=1000.0),
        location_to_segment={"push": DriverSegment(driver=[0.5])},
    )
    with ChronoAdapter(cfg) as sim:
        sim.send_navigation_goal(location="push")
        rig = sim._scene._rig
        # The last accumulated forward force = driver[0] * drawbar_gain_n.
        assert rig.forces and rig.forces[-1].x == pytest.approx(500.0)


def test_bare_scene_has_no_terramechanics_fields(fake_pychrono: _FakePychrono) -> None:
    """The default 'bare' scene is unchanged: no terramechanics keys, no scene built."""
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig
    from urml_chrono_runtime.adapter import DriverSegment

    cfg = ChronoConfig(location_to_segment={"r": DriverSegment(driver=[0.1])})
    with ChronoAdapter(cfg) as sim:
        sim.send_navigation_goal(location="r")
        assert sim._scene is None
        assert sim._last_evidence is not None
        assert "sinkage_m" not in sim._last_evidence
        assert "terrain_model" not in sim._last_evidence


def test_terramechanics_params_default_when_omitted(fake_pychrono: _FakePychrono) -> None:
    from urml_chrono_runtime import ChronoAdapter, ChronoConfig

    with ChronoAdapter(ChronoConfig(scene="terramechanics", steps_per_command=2)) as sim:
        assert sim.wait_passively(duration_seconds=0.0).success
        # Scene built with default params; rig mass is the documented default.
        assert sim._scene is not None
        assert sim._scene._rig.mass == pytest.approx(250.0)
