"""Deployment-side configuration for the educational-platform adapters.

Each platform is driven to *named commands* its firmware understands
(VEX V5 motor-group preset, Pybricks command name on a LEGO hub, Thymio
program name, ``martypy.Marty`` skill method name). Which command a
manifest-declared location maps to is platform- and sketch-specific, so
it does NOT belong in the URML program/manifest/envelope — it lives in
an ``edu_adapter.yaml`` (the embedded/cobot/px4 ``location_to_*``
precedent).

## Two dispatch shapes

A configured command may be either:

1. **A plain string** — the method name, called with no arguments.
   Backwards-compatible with the v0.1 scaffold. Example: ``"walk"``,
   ``"eyes"``, ``"close_claw"``.

2. **An :class:`EduSkillCall`** — a method name plus positional
   ``args`` and keyword ``kwargs``. The richer shape is what real
   ``martypy.Marty`` methods need: ``arms(left_angle, right_angle,
   move_time)``, ``eyes(pose_or_angle)``, ``lean(direction)``,
   ``sidestep(side)``, ``wave(side)``. Required for production-grade
   adapter dispatch per robotical/martypy#52 round-3 maintainer
   guidance (2026-05-27).

In YAML the two shapes look like::

    location_to_command:
      home_pose: walk                                 # string form
      kick_left: { method: kick, args: [left] }       # richer form
      wave_right: { method: wave, args: [right] }
      arms_open: { method: arms, args: [90, -90, 1500] }
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class EduSkillCall(BaseModel):
    """A richer dispatch shape for skill methods that take arguments.

    Example uses (real ``martypy.Marty`` API, per robotical/martypy#52
    round-3 maintainer guidance 2026-05-27)::

        EduSkillCall(method="arms", args=[10, -10, 1000])
        EduSkillCall(method="eyes", args=["angry"])
        EduSkillCall(method="lean", args=["left"])
        EduSkillCall(method="sidestep", args=["right"])
        EduSkillCall(method="wave", args=["right"])

    The string form (plain ``"walk"`` rather than ``{"method": "walk"}``)
    stays valid for methods that take no arguments.
    """

    model_config = ConfigDict(extra="forbid")

    method: str = Field(description="Name of the SDK method to call on the connected device.")
    args: list[Any] = Field(default_factory=list, description="Positional arguments.")
    kwargs: dict[str, Any] = Field(default_factory=dict, description="Keyword arguments.")


#: A configured command is either a bare method name (no args) or an
#: :class:`EduSkillCall` carrying positional / keyword args.
EduCommand = str | EduSkillCall


class EduConfig(BaseModel):
    """Connection + command-mapping config shared by all educational adapters."""

    model_config = ConfigDict(extra="forbid")

    device: str = Field(
        default="auto",
        description=(
            "Platform-specific device identifier. VEX: USB/serial port. "
            "LEGO: BLE address of the hub. Thymio: TDM URL (default 'tcp:localhost:8597'). "
            "Marty: 'usb' (v2 default), 'wifi://<host>' (v2 configurable), 'socket://<host>' (v1)."
        ),
    )
    program_name: str = Field(
        default="main",
        description="Pybricks/VEX/Thymio program name the firmware exposes.",
    )

    #: location name -> the firmware-mapped command (string or richer call).
    location_to_command: dict[str, EduCommand] = Field(default_factory=dict)
    #: 'grasp' / 'release' -> the platform's claw-servo command (string or richer call).
    manipulation_commands: dict[str, EduCommand] = Field(default_factory=dict)

    def resolve_location(self, name: str) -> EduCommand | None:
        return self.location_to_command.get(name)


def load_edu_config(path: str | Path) -> EduConfig:
    """Parse an ``edu_adapter.yaml`` file into an ``EduConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"edu-config file {p} did not contain a YAML mapping at the top level.")
    return EduConfig.model_validate(data)
