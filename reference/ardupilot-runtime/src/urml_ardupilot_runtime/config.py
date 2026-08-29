"""Deployment-side configuration for ``ArduCopterAdapter``.

Extends ``PX4AdapterConfig`` (the connection URL, MAVLink identity, default
timeouts, and the name -> local-NED binding) with what an ArduPilot
deployment additionally needs:

- A serial ``baud`` (a Pixhawk on USB ignores it; a SiK telemetry radio
  does not).
- ArduPilot-specific timeouts: mode entry, arming, take-off climb,
  arrival at a setpoint.
- A name -> WGS84 binding (``location_to_global``) so a manifest location
  can be flown as a global setpoint. Produced offline by
  ``tools/scripts/geocode_locations.py``; the runtime never geocodes.
- A camera trigger description and named output-line bindings (gripper,
  winch, servo) for ``capture`` and ``set_output``.

All of this is deployment- and aircraft-specific, so it lives in an
``ardupilot_adapter.yaml`` next to the URML artifacts, never in the
program, manifest, or envelope.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
from urml_px4_runtime.config import NEDPosition, PX4AdapterConfig

__all__ = [
    "ArduPilotAdapterConfig",
    "CameraTrigger",
    "GlobalPosition",
    "LookAt",
    "NEDPosition",
    "OutputLineBinding",
    "load_ardupilot_config",
]

_SERIAL_URL = re.compile(r"^(COM\d+|/dev/tty[A-Za-z0-9.]+)$", re.IGNORECASE)


class LookAt(BaseModel):
    """A WGS84 point of interest the aircraft yaws toward after arrival."""

    model_config = ConfigDict(extra="forbid")

    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)


class GlobalPosition(BaseModel):
    """A WGS84 position with altitude above the launch point.

    ``alt_agl`` is metres above home, which is what ArduCopter's
    ``MAV_FRAME_GLOBAL_RELATIVE_ALT_INT`` means. Terrain-following is a
    substrate parameter, not something this config models.
    """

    model_config = ConfigDict(extra="forbid")

    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    alt_agl: float = Field(..., ge=0.0)
    look_at: LookAt | None = None


class CameraTrigger(BaseModel):
    """How ``capture(media: photo)`` fires the on-board camera.

    ``digicam`` sends ``MAV_CMD_DO_DIGICAM_CONTROL`` and lets the
    autopilot's ``CAM_TRIGG_TYPE`` decide the physical output. ``servo``
    pulses a servo channel directly (``MAV_CMD_DO_SET_SERVO``) for shutter
    cables wired to an AUX output.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["digicam", "servo"] = "digicam"
    channel: int | None = Field(None, ge=1, le=16, description="Servo output channel (servo kind only).")
    pwm_on: int = Field(1900, ge=800, le=2200)
    pwm_off: int = Field(1100, ge=800, le=2200)
    pulse_ms: float = Field(300.0, gt=0)
    settle_seconds: float = Field(0.5, ge=0, description="Pause after the trigger before the result is returned.")


class OutputLineBinding(BaseModel):
    """Binds a manifest-declared output line to an ArduPilot mechanism."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["gripper", "winch", "servo"]
    instance: int = Field(1, ge=1, description="Gripper / winch instance number (gripper, winch kinds).")
    channel: int | None = Field(None, ge=1, le=16, description="Servo output channel (servo kind).")
    on_pwm: int = Field(1900, ge=800, le=2200)
    off_pwm: int = Field(1100, ge=800, le=2200)
    deliver_length_m: float = Field(10.0, gt=0, description="Winch: line length paid out on `true`.")
    rate_m_s: float = Field(0.5, gt=0, description="Winch: line rate for deliver / retract.")


class ArduPilotAdapterConfig(PX4AdapterConfig):
    """ArduPilot / MAVLink connection and binding config."""

    model_config = ConfigDict(extra="forbid")

    connection_url: str = Field(
        default="udp:127.0.0.1:14550",
        description=(
            "pymavlink connection string. ArduCopter SITL GCS port: 'udp:127.0.0.1:14550'. "
            "USB: 'COM5' or '/dev/ttyACM0'. Telemetry radio: '/dev/ttyUSB0' with `baud`."
        ),
    )
    baud: int = Field(115200, description="Serial baud rate; appended to serial-shaped URLs without one.")
    component_id: int = Field(
        default=190,
        description="MAV_COMP_ID_MISSIONPLANNER. ArduPilot expects a GCS-class component id from an operator link.",
    )
    vehicle: Literal["copter"] = "copter"

    mode_timeout_seconds: float = 5.0
    arm_timeout_seconds: float = 10.0
    takeoff_timeout_seconds: float = 60.0
    arrival_radius_m: float = Field(1.5, gt=0)
    arrival_alt_tolerance_m: float = Field(1.0, gt=0)
    arrival_timeout_seconds: float = 120.0
    stream_rate_hz: float = Field(2.0, gt=0, description="Requested rate for position and battery telemetry.")

    location_to_global: dict[str, GlobalPosition] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to WGS84 positions. Wins over location_to_pose.",
    )
    camera: CameraTrigger | None = None
    output_lines: dict[str, OutputLineBinding] = Field(
        default_factory=dict,
        description="Map manifest `outputs.lines` names to gripper / winch / servo mechanisms.",
    )

    def effective_connection_url(self) -> str:
        """The URL handed to pymavlink: serial ports get `,<baud>` appended."""
        url = self.connection_url
        if _SERIAL_URL.match(url):
            return f"{url},{self.baud}"
        return url

    def resolve_global(self, name: str) -> GlobalPosition | None:
        """Return the WGS84 binding for a named location, or None."""
        return self.location_to_global.get(name)


def load_ardupilot_config(path: str | Path) -> ArduPilotAdapterConfig:
    """Parse an ``ardupilot_adapter.yaml`` file into an ``ArduPilotAdapterConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"ardupilot-config file {p} did not contain a YAML mapping at the top level.")
    return ArduPilotAdapterConfig.model_validate(data)
