"""Deployment-side configuration for ``RclpyAdapter``.

The URML validator resolves *names* (location names, object classes,
gripper names, sensor names) against the capability manifest. The
adapter then needs deployment-specific facts to turn those names into
real ROS 2 action servers, topics, and poses:

- Which Nav2 action server to send a NavigateToPose goal to.
- Which MoveIt 2 move-group governs the arm.
- Which gripper-action server backs each declared gripper.
- Which perception topic carries detections.
- Which TTS / STT topics back the home-profile speech primitives.
- Where, in the substrate's map frame, the manifest's named locations
  and areas actually live, and how wide one scan sample is.

These facts are deployment- and substrate-specific, so they do NOT
belong in the URML program, manifest, or envelope. They live in an
adapter-side YAML alongside those URML artifacts.

The shape below is the v0.1 reference format. Operators are free to use
a different format — the adapter's constructor accepts any compatible
``AdapterConfig`` instance.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ActionServerConfig(BaseModel):
    """Names of the ROS 2 action servers the adapter calls.

    Defaults match the conventions in Nav2 and MoveIt 2 vanilla installs.
    Most deployments keep these defaults; sites that namespace their
    robots override the ``ros2_namespace`` and these auto-prefix.
    """

    model_config = ConfigDict(extra="forbid")

    navigate_to_pose: str = "/navigate_to_pose"
    dock_robot: str = "/dock_robot"
    move_group: str = "/move_action"
    gripper: dict[str, str] = Field(
        default_factory=dict,
        description="Map of gripper name (matches the manifest's gripper.name) to its action server.",
    )


class PerceptionTopics(BaseModel):
    """Topic names the adapter subscribes to for perception primitives."""

    model_config = ConfigDict(extra="forbid")

    detection_topic: str = "/vision_msgs/detections"
    image_topic: str = "/camera/image_raw"


class SpeechTopics(BaseModel):
    """Topic names for home-profile speech primitives.

    Both are optional. If unset, ``emit_speech`` / ``acquire_speech``
    return a documented "speech-not-configured" failure rather than
    raising — the same shape any other capability-missing failure takes.
    """

    model_config = ConfigDict(extra="forbid")

    output_topic: str | None = None
    input_topic: str | None = None


class PoseLiteral(BaseModel):
    """A 2D/3D pose with an explicit frame.

    Used when the deployer pins a manifest-declared location to a
    specific point in the substrate's coordinate system. The validator
    enforces that the *name* is declared; the adapter resolves it to
    *coordinates* via this map.
    """

    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float = 0.0
    yaw: float | None = None
    frame: str = "map"


class RegionLiteral(BaseModel):
    """A named area's boundary in substrate coordinates, for ``scan`` over a named region.

    The manifest declares the area by name (RFC-0615); this map pins the name
    to a polygon the adapter can plan over, the way ``location_to_pose`` pins a
    location name to a pose.
    """

    model_config = ConfigDict(extra="forbid")

    polygon: list[tuple[float, float]] = Field(..., min_length=3, description="Boundary vertices as [x, y].")
    frame: str = "map"


class ScanSettings(BaseModel):
    """How ``run_scan`` turns an area into waypoints.

    ``swath_m`` is the width one sample covers (for a camera, its footprint on
    the ground); samples and lanes sit ``swath_m * (1 - overlap)`` apart. The
    default suits a ground robot's camera; set it to the real footprint.
    """

    model_config = ConfigDict(extra="forbid")

    swath_m: float = Field(1.0, gt=0, description="Width one sample covers, in metres.")
    max_waypoints: int = Field(
        200, gt=0, description="A plan with more waypoints is refused rather than driven."
    )
    frame: str = Field("map", description="Frame for a literal polygon or bounding box, which carry none.")


class AdapterConfig(BaseModel):
    """The deployment-side adapter config loaded from ``adapter.yaml``."""

    model_config = ConfigDict(extra="forbid")

    ros2_namespace: str = ""
    action_servers: ActionServerConfig = Field(default_factory=ActionServerConfig)
    perception: PerceptionTopics = Field(default_factory=PerceptionTopics)
    speech: SpeechTopics = Field(default_factory=SpeechTopics)
    location_to_pose: dict[str, PoseLiteral] = Field(
        default_factory=dict,
        description="Map manifest-declared location names to substrate coordinates.",
    )
    region_to_polygon: dict[str, RegionLiteral] = Field(
        default_factory=dict,
        description="Map manifest-declared area names to substrate polygons, for scan.",
    )
    scan: ScanSettings = Field(default_factory=ScanSettings)

    def resolve_location(self, name: str) -> PoseLiteral | None:
        """Return the pose for a named location, or None if unmapped.

        Unmapped names produce a ``NavigationResult(success=False)`` with a
        ``location_not_configured`` reason — they do not raise. This lets
        the runtime's on-error policy decide what happens next.
        """
        return self.location_to_pose.get(name)


def load_adapter_config(path: str | Path) -> AdapterConfig:
    """Parse an ``adapter.yaml`` file into an ``AdapterConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"adapter-config file {p} did not contain a YAML mapping at the top level.")
    return AdapterConfig.model_validate(data)
