"""Deployment-side configuration for the educational-platform adapters.

Each platform is driven to *named commands* its firmware understands
(VEX V5 motor-group preset, Pybricks command name on a LEGO hub, Thymio
program name). Which command string a manifest-declared location maps
to is platform- and sketch-specific, so it does NOT belong in the URML
program/manifest/envelope — it lives in an ``edu_adapter.yaml`` (the
embedded/cobot/px4 ``location_to_*`` precedent).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class EduConfig(BaseModel):
    """Connection + command-mapping config shared by all educational adapters."""

    model_config = ConfigDict(extra="forbid")

    device: str = Field(
        default="auto",
        description=(
            "Platform-specific device identifier. VEX: USB/serial port. "
            "LEGO: BLE address of the hub. Thymio: TDM URL (default 'tcp:localhost:8597')."
        ),
    )
    program_name: str = Field(
        default="main",
        description="Pybricks/VEX/Thymio program name the firmware exposes.",
    )

    #: location name -> the firmware-mapped command string.
    location_to_command: dict[str, str] = Field(default_factory=dict)
    #: 'grasp' / 'release' -> the platform's claw-servo command.
    manipulation_commands: dict[str, str] = Field(default_factory=dict)

    def resolve_location(self, name: str) -> str | None:
        return self.location_to_command.get(name)


def load_edu_config(path: str | Path) -> EduConfig:
    """Parse an ``edu_adapter.yaml`` file into an ``EduConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"edu-config file {p} did not contain a YAML mapping at the top level.")
    return EduConfig.model_validate(data)
