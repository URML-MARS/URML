"""Deployment-side configuration for ``AutosarAdaptiveAdapter``.

An AUTOSAR Adaptive cell exposes its capabilities as method and variable
*nodes* under a server endpoint. Which node ids carry "move to a named
location", "run a station service", "grip", "read a sensor" are
deployment- and vendor-specific, so they do NOT belong in the URML
program, manifest, or envelope — they live in an ``autosar_adapter.yaml``
alongside the URML artifacts (the same principle as the PX4 runtime's
``location_to_pose`` and the marine runtime's ``location_to_waypoint``).

The adapter calls methods on the server's ObjectsNode by node id; the
objects node id and per-capability method node ids are all config.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class MethodTarget(BaseModel):
    """A node-id of an AUTOSAR Adaptive method plus the literal args to call it with."""

    model_config = ConfigDict(extra="forbid")

    method: str = Field(..., description="NodeId of the method to call, e.g. 'sid=MoveTo'.")
    args: list[str] = Field(default_factory=list, description="Literal string args passed to the method.")


class AutosarConfig(BaseModel):
    """AUTOSAR Adaptive connection + node-mapping config."""

    model_config = ConfigDict(extra="forbid")

    endpoint_url: str = Field(
        default="someip://127.0.0.1:4840/urml/",
        description="AUTOSAR Adaptive server endpoint. A local ara demo server uses someip://127.0.0.1:4840/.",
    )
    objects_node: str = Field(
        default="i=85",
        description="NodeId of the parent object the capability methods hang off (default: Objects).",
    )
    connect_timeout_seconds: float = 5.0

    #: location name -> the MoveTo-style method + args that drives there.
    location_to_method: dict[str, MethodTarget] = Field(default_factory=dict)
    #: station-service name (e.g. swap_tool, park) -> its method + args.
    service_to_method: dict[str, MethodTarget] = Field(default_factory=dict)
    #: 'grasp' / 'release' -> their method nodes.
    manipulation_methods: dict[str, MethodTarget] = Field(default_factory=dict)
    #: a variable NodeId read by `measure` / polled by `wait_for`.
    measurement_node: str | None = None

    def resolve_location(self, name: str) -> MethodTarget | None:
        return self.location_to_method.get(name)

    def resolve_service(self, name: str) -> MethodTarget | None:
        return self.service_to_method.get(name)


def load_autosar_config(path: str | Path) -> AutosarConfig:
    """Parse an ``autosar_adapter.yaml`` file into an ``AutosarConfig``."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"autosar-config file {p} did not contain a YAML mapping at the top level.")
    return AutosarConfig.model_validate(data)
