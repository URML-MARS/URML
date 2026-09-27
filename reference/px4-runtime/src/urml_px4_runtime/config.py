"""Deployment-side configuration for ``PX4Adapter``.

A PX4 / MAVLink connection needs to know:

- Where to connect (UDP for SITL, UDP/TCP for telemetry radios, serial
  for hardware-in-the-loop or wired companions).
- Which MAVLink identity to use (``system_id``, ``component_id``).
- Default per-command timeouts (heartbeat wait, ack wait, message wait).
- How long each flight phase may take and how close counts as arrived:
  the adapter reports a flight primitive as done only when telemetry
  shows it (armed, at altitude, inside the acceptance radius, on the
  ground), and gives up with a failure after these timeouts.
- A mapping from manifest-declared location names to local-NED
  coordinates, mirroring the ROS 2 runtime's ``location_to_pose``.

These facts are deployment- and aircraft-specific, so they do NOT
belong in the URML program, manifest, or envelope. They live in a
``px4_adapter.yaml`` alongside the URML artifacts.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class NEDPosition(BaseModel):
    """A 3D position as an offset from home (north, east, altitude).

    ``north`` and ``east`` are metres from PX4's home position; ``alt`` is
    metres above home (positive up), so authors never think in NED's
    negative-down. ``PX4Adapter`` converts the offset to a WGS84 target
    from home and flies it with ``MAV_CMD_DO_REPOSITION``.
    """

    model_config = ConfigDict(extra="forbid")

    north: float = 0.0
    east: float = 0.0
    alt: float = 0.0  # metres above home (positive up)


class PX4AdapterConfig(BaseModel):
    """PX4 / MAVLink connection config."""

    model_config = ConfigDict(extra="forbid")

    connection_url: str = Field(
        default="udp:127.0.0.1:14540",
        description=(
            "pymavlink connection string. PX4 SITL: 'udp:127.0.0.1:14540'. "
            "Serial: '/dev/ttyACM0,57600'. TCP telemetry: 'tcp:1.2.3.4:5760'."
        ),
    )
    system_id: int = Field(
        default=255,
        description="MAVLink system_id this adapter identifies as. PX4 expects "
        "GCS-style IDs (typically 255) for offboard control.",
    )
    component_id: int = Field(
        default=1,
        description="MAVLink component_id (1 = autopilot, 190 = GCS, etc.).",
    )
    heartbeat_timeout_seconds: float = 5.0
    ack_timeout_seconds: float = 5.0
    message_timeout_seconds: float = 5.0
    arm_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        description="take_off: how long to wait for the armed bit on HEARTBEAT after PX4 accepts the arm command.",
    )
    takeoff_timeout_seconds: float = Field(
        default=120.0,
        gt=0,
        description="take_off: how long the climb to the target altitude may take. PX4 climbs at MPC_TKO_SPEED "
        "(1.5 m/s by default), so 120 s covers a 120 m take-off with margin.",
    )
    arrival_radius_m: float = Field(
        default=1.5,
        gt=0,
        description="move_to, hover and return_to_home: horizontal distance (m) from the target that counts as "
        "arrived.",
    )
    arrival_alt_tolerance_m: float = Field(
        default=1.0,
        gt=0,
        description="take_off and move_to: altitude difference (m) from the target that counts as arrived. For "
        "take_off it is capped at half the target altitude.",
    )
    arrival_timeout_seconds: float = Field(
        default=120.0,
        gt=0,
        description="move_to, hover and return_to_home: how long the flight to the target may take. Raise it for "
        "long legs (PX4 cruises at MPC_XY_CRUISE, 5 m/s by default).",
    )
    land_timeout_seconds: float = Field(
        default=180.0,
        gt=0,
        description="land: how long the descent may take before PX4 must report landed_state ON_GROUND.",
    )
    location_to_pose: dict[str, NEDPosition] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to offsets from home (north, east, alt above home).",
    )

    def resolve_location(self, name: str) -> NEDPosition | None:
        """Return the NED position for a named location, or None if unmapped.

        Unmapped names produce a ``NavigationResult(success=False)`` with a
        ``location_not_configured`` reason — they do not raise.
        """
        return self.location_to_pose.get(name)


def load_px4_config(path: str | Path) -> PX4AdapterConfig:
    """Parse a ``px4_adapter.yaml`` file into a ``PX4AdapterConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"px4-config file {p} did not contain a YAML mapping at the top level.")
    return PX4AdapterConfig.model_validate(data)
