"""Deployment-side configuration for ``EmbeddedAdapter``.

A micro:bit / Arduino-class buggy is driven by writing short ASCII
commands over a serial line (the firmware on the board interprets
them). Which command string a manifest-declared location maps to is
board- and sketch-specific, so it does NOT belong in the URML
program/manifest/envelope — it lives in an ``embedded_adapter.yaml``
(the same principle as the PX4 runtime's ``location_to_pose``).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class EmbeddedConfig(BaseModel):
    """Serial connection + command-mapping config."""

    model_config = ConfigDict(extra="forbid")

    port: str = Field(
        default="loop://",
        description="pyserial port. A real micro:bit: 'COM3' / '/dev/ttyACM0'. 'loop://' is the test loopback.",
    )
    baudrate: int = Field(default=115200, gt=0)
    read_timeout_seconds: float = 2.0

    #: location name -> the ASCII command the firmware drives on.
    location_to_command: dict[str, str] = Field(default_factory=dict)
    #: 'grasp' / 'release' -> the ASCII command for the gripper servo.
    manipulation_commands: dict[str, str] = Field(default_factory=dict)

    def resolve_location(self, name: str) -> str | None:
        return self.location_to_command.get(name)


def load_embedded_config(path: str | Path) -> EmbeddedConfig:
    """Parse an ``embedded_adapter.yaml`` file into an ``EmbeddedConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"embedded-config file {p} did not contain a YAML mapping at the top level.")
    return EmbeddedConfig.model_validate(data)
