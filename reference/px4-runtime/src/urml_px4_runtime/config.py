"""Deployment-side configuration for ``PX4Adapter``.

A PX4 / MAVLink connection needs to know:

- Where to connect (UDP for SITL, UDP/TCP for telemetry radios, serial
  for hardware-in-the-loop or wired companions).
- Which MAVLink identity to use (``system_id``, ``component_id``).
- Default per-command timeouts (heartbeat wait, ack wait, message wait).
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
    """A 3D position in the local-NED frame (north, east, down).

    PX4's offboard/guided mode commands positions in NED relative to a
    declared home. Altitude in NED is *negative-down* — 30m above home
    is ``down = -30.0``. We use ``alt`` (positive up, meters AGL) as the
    URML-facing field and convert internally so manifest authors don't
    have to think in NED.
    """

    model_config = ConfigDict(extra="forbid")

    north: float = 0.0
    east: float = 0.0
    alt: float = 0.0  # meters AGL (positive up). Adapter converts to NED down.


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
    location_to_pose: dict[str, NEDPosition] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to local-NED coordinates.",
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
