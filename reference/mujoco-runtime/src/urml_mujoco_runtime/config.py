"""Deployment-side configuration for ``MujocoAdapter``.

A MuJoCo simulation needs to know:

- Which MJCF/XML model to load (``model_path``).
- A mapping from manifest-declared location names to a control target
  (the actuator ``ctrl`` vector that drives the model toward that named
  pose), mirroring the ROS 2 runtime's ``location_to_pose`` and the PX4
  runtime's ``location_to_pose``.
- How many physics steps to advance per command and the optional
  per-step settle budget.

These facts are model- and deployment-specific, so they do NOT belong
in the URML program, manifest, or envelope. They live in a
``mujoco_adapter.yaml`` alongside the URML artifacts.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ControlTarget(BaseModel):
    """A named control target: the actuator ``ctrl`` vector for a pose.

    The adapter writes ``ctrl`` onto ``mjData`` and steps the engine;
    ``ctrl`` is model-specific, which is exactly why it is deployment
    config and not a URML-level concept.
    """

    model_config = ConfigDict(extra="forbid")

    ctrl: list[float] = Field(default_factory=list, description="Actuator control vector for this pose.")


class MujocoConfig(BaseModel):
    """MuJoCo model + control config."""

    model_config = ConfigDict(extra="forbid")

    model_path: str = Field(
        default="",
        description=(
            "Path to the MJCF/XML model. Required at construction time; an "
            "empty value yields a clear 'model_path not configured' error "
            "rather than a crash."
        ),
    )
    steps_per_command: int = Field(
        default=100,
        ge=1,
        description="Physics steps advanced per navigation/wait command.",
    )
    location_to_target: dict[str, ControlTarget] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to a control target.",
    )

    def resolve_location(self, name: str) -> ControlTarget | None:
        """Return the control target for a named location, or None if unmapped.

        Unmapped names produce a ``NavigationResult(success=False)`` with a
        ``location_not_configured`` reason — they do not raise.
        """
        return self.location_to_target.get(name)


def load_mujoco_config(path: str | Path) -> MujocoConfig:
    """Parse a ``mujoco_adapter.yaml`` file into a ``MujocoConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"mujoco-config file {p} did not contain a YAML mapping at the top level.")
    return MujocoConfig.model_validate(data)
