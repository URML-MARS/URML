"""RFC-0668: trace-recording MuJoCo adapter for the rehearsal gate.

`MujocoAdapter` advances real physics but records nothing: each command
returns only a final pose. Rehearsal needs the trajectory, so
`RecordingMujocoAdapter` overrides the step loop and samples the engine
state per tick into `urml_validator.monitor.Sample`s, mapped to envelope
signal names by a declared `SignalMap`.

The signal map is the honest seam: which `qvel` components mean "speed" is
a property of the MJCF model, not of URML, so the deployment declares it.
A map that lies produces a rehearsal that lies.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator
from urml_validator.monitor import Sample

from urml_mujoco_runtime.adapter import MujocoAdapter
from urml_mujoco_runtime.config import MujocoConfig

__all__ = ["RecordingMujocoAdapter", "SignalMap", "SignalSpec", "load_signal_map"]


class SignalSpec(BaseModel):
    """How one envelope signal reads out of the MuJoCo state.

    - `source: qpos | qvel | sensordata` with `index` reads one scalar.
    - `source: qvel` (or `qpos`) with `indices` reads the Euclidean norm
      over those components (the usual way "speed" comes out of a free
      joint's linear velocity).
    - `source: const` with `value` pins a signal the model cannot measure
      (declare it openly; a pinned `person_distance: 100.0` means "this
      rehearsal assumes nobody is present").
    """

    model_config = ConfigDict(extra="forbid")

    source: Literal["qpos", "qvel", "sensordata", "const"]
    index: int | None = Field(None, ge=0)
    indices: list[int] | None = None
    value: float | None = None

    @model_validator(mode="after")
    def _coherent(self) -> SignalSpec:
        if self.source == "const":
            if self.value is None:
                raise ValueError("source: const requires `value`")
            return self
        if (self.index is None) == (self.indices is None):
            raise ValueError(f"source: {self.source} requires exactly one of `index` or `indices`")
        return self

    def read(self, data: Any) -> float:
        if self.source == "const":
            assert self.value is not None
            return float(self.value)
        vector = getattr(data, self.source)
        if self.index is not None:
            return float(vector[self.index])
        assert self.indices is not None
        return math.sqrt(sum(float(vector[i]) ** 2 for i in self.indices))


class SignalMap(BaseModel):
    """Envelope signal name -> readout spec."""

    model_config = ConfigDict(extra="forbid")

    signals: dict[str, SignalSpec]


def load_signal_map(path: Path) -> SignalMap:
    """Load a signal map from YAML (`signals: {speed: {source: qvel, indices: [0,1]}}`)."""
    with Path(path).open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ValueError(f"signal map did not parse as a mapping: {path}")
    return SignalMap.model_validate(raw)


class RecordingMujocoAdapter(MujocoAdapter):
    """MujocoAdapter that samples the engine per tick, for rehearsal traces.

    Satisfies the rehearsal `TraceRecorder` protocol via `samples()`.
    Timestamps are the engine's own `data.time`, so the trace clock is the
    physics clock.
    """

    def __init__(
        self,
        config: MujocoConfig | None = None,
        *,
        signal_map: SignalMap,
        sample_every_n_steps: int = 1,
    ) -> None:
        super().__init__(config)
        if sample_every_n_steps < 1:
            raise ValueError("sample_every_n_steps must be >= 1")
        self._signal_map = signal_map
        self._sample_every = sample_every_n_steps
        self._recorded: list[Sample] = []
        self._tick = 0

    def samples(self) -> tuple[Sample, ...]:
        return tuple(self._recorded)

    def _step(self, n: int) -> None:
        model, data = self._sim()
        for _ in range(max(1, n)):
            self._mujoco.mj_step(model, data)
            self._tick += 1
            if self._tick % self._sample_every == 0:
                self._recorded.append(self._sample_from(data))

    def _sample_from(self, data: Any) -> Sample:
        return Sample(
            t=float(data.time),
            signals={name: spec.read(data) for name, spec in self._signal_map.signals.items()},
        )
