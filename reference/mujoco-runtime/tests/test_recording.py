"""RFC-0668: SignalMap semantics (hermetic) + recording rollout (needs the [sim] extra)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from urml_mujoco_runtime.recording import SignalMap, SignalSpec, load_signal_map


class _FakeData:
    """Duck-typed stand-in for mujoco.MjData (hermetic SignalSpec tests)."""

    def __init__(self) -> None:
        self.qpos = [1.0, 2.0, 5.0]
        self.qvel = [3.0, 4.0, 0.0]
        self.sensordata = [7.5]
        self.time = 0.002


def test_signal_spec_scalar_reads() -> None:
    assert SignalSpec(source="qpos", index=2).read(_FakeData()) == 5.0
    assert SignalSpec(source="sensordata", index=0).read(_FakeData()) == 7.5


def test_signal_spec_norm_read() -> None:
    # speed as the norm of two qvel components: sqrt(3^2 + 4^2) = 5.
    assert SignalSpec(source="qvel", indices=[0, 1]).read(_FakeData()) == 5.0


def test_signal_spec_const_read() -> None:
    assert SignalSpec(source="const", value=100.0).read(_FakeData()) == 100.0


def test_signal_spec_coherence() -> None:
    with pytest.raises(ValidationError, match="const"):
        SignalSpec(source="const")
    with pytest.raises(ValidationError, match="exactly one"):
        SignalSpec(source="qvel")
    with pytest.raises(ValidationError, match="exactly one"):
        SignalSpec(source="qvel", index=0, indices=[0, 1])


def test_load_signal_map(tmp_path: Path) -> None:
    path = tmp_path / "signals.yaml"
    path.write_text(
        "signals:\n"
        "  speed: {source: qvel, indices: [0, 1]}\n"
        "  altitude: {source: qpos, index: 2}\n"
        "  person_distance: {source: const, value: 100.0}\n",
        encoding="utf-8",
    )
    signal_map = load_signal_map(path)
    data = _FakeData()
    assert signal_map.signals["speed"].read(data) == 5.0
    assert signal_map.signals["altitude"].read(data) == 5.0
    assert signal_map.signals["person_distance"].read(data) == 100.0


def test_recording_rollout_produces_increasing_trace() -> None:
    """Real-physics rollout; runs only where the [sim] extra is installed."""
    pytest.importorskip("mujoco")
    from urml_mujoco_runtime import MujocoConfig, RecordingMujocoAdapter
    from urml_mujoco_runtime.config import ControlTarget

    mjcf = Path(__file__).parent / "fixtures" / "pendulum.xml"
    if not mjcf.is_file():
        pytest.skip("no MJCF fixture on this host")
    adapter = RecordingMujocoAdapter(
        MujocoConfig(
            model_path=str(mjcf),
            locations={"target": ControlTarget(ctrl=[0.5])},
            steps_per_command=10,
        ),
        signal_map=SignalMap(
            signals={
                "speed": SignalSpec(source="qvel", indices=[0]),
                "person_distance": SignalSpec(source="const", value=100.0),
            }
        ),
    )
    adapter.send_navigation_goal(location="target")
    trace = adapter.samples()
    assert len(trace) == 10
    times = [s.t for s in trace]
    assert times == sorted(times) and len(set(times)) == len(times)
    assert all("speed" in s.signals for s in trace)
