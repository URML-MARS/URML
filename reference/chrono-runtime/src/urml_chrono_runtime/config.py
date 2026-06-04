"""Deployment-side configuration for ``ChronoAdapter``.

A Chrono validation run needs to know:

- Which contact method the system uses (``system_type``: ``NSC``
  non-smooth complementarity, or ``SMC`` smooth penalty).
- The integration step size and how many steps to advance per command.
- A mapping from manifest-declared location names to a **driver
  segment**: the driver inputs (throttle / steering / braking, model
  ordering) that drive the vehicle toward that named pose for one
  command, mirroring the ROS 2 runtime's ``location_to_pose`` and the
  MuJoCo runtime's ``location_to_target``.

This altitude follows Project Chrono lead Dan Negrut's feedback on
issue #746: align at Chrono's **motion primitives and driver inputs**,
each manifest entry mapping to a concrete ``ChSystem`` configuration.
These facts are model- and deployment-specific, so they do NOT belong
in the URML program, manifest, or envelope. They live in a
``chrono_adapter.yaml`` alongside the URML artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class DriverSegment(BaseModel):
    """A named driver segment: the driver-input vector for one command.

    The adapter applies ``driver`` (model-specific ordering, e.g.
    ``[throttle, steering, braking]``) and advances the Chrono system;
    ``driver`` is model-specific, which is exactly why it is deployment
    config and not a URML-level concept.
    """

    model_config = ConfigDict(extra="forbid")

    driver: list[float] = Field(
        default_factory=list,
        description="Driver-input vector applied for this command (model ordering).",
    )
    steps: int | None = Field(
        default=None,
        ge=1,
        description="Physics steps for this segment; overrides steps_per_command when set.",
    )


class ChronoConfig(BaseModel):
    """Chrono system + driver config."""

    model_config = ConfigDict(extra="forbid")

    system_type: Literal["NSC", "SMC"] = Field(
        default="NSC",
        description="Contact method: NSC (complementarity) or SMC (penalty).",
    )
    step_size: float = Field(
        default=1e-3,
        gt=0.0,
        description="Integration step size in seconds passed to DoStepDynamics.",
    )
    steps_per_command: int = Field(
        default=200,
        ge=1,
        description="Physics steps advanced per navigation/wait command.",
    )
    location_to_segment: dict[str, DriverSegment] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to a driver segment.",
    )

    def resolve_location(self, name: str) -> DriverSegment | None:
        """Return the driver segment for a named location, or None if unmapped.

        Unmapped names produce a ``NavigationResult(success=False)`` with a
        ``location_not_configured`` reason; they do not raise.
        """
        return self.location_to_segment.get(name)


def load_chrono_config(path: str | Path) -> ChronoConfig:
    """Parse a ``chrono_adapter.yaml`` file into a ``ChronoConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"chrono-config file {p} did not contain a YAML mapping at the top level.")
    return ChronoConfig.model_validate(data)
