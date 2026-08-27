"""RFC-0682: 3D-camera declaration (point_cloud, parity fields, datasheet_ref, mount).

Schema-level guards: additive optional fields, closed-set channels, the
rate constraint, the one manifest coherence rule (mount.frame must be a
declared frame), the Zivid fixture, and a pre-RFC manifest unchanged.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from urml_validator.schemas.manifest import CapabilityManifest

FIXTURES = Path(__file__).parent / "fixtures" / "manifests"

BASE: dict[str, Any] = {
    "manifest_version": "0.1",
    "robot_id": "cam_bot",
    "frames": [{"name": "base_link", "parent": None}],
    "mobility": {"drive_type": "differential", "max_velocity": 0.5, "station_keeping": False},
    "perception": {
        "cameras": [{"name": "cam", "movable": False}],
        "object_vocabulary": ["widget"],
    },
}


def _with_camera(**extra: Any) -> dict[str, Any]:
    m = copy.deepcopy(BASE)
    m["perception"]["cameras"][0].update(extra)
    return m


def test_pre_rfc_manifest_validates_unchanged() -> None:
    cam = CapabilityManifest.model_validate(BASE).perception.cameras[0]
    assert cam.point_cloud is None and cam.mount is None and cam.datasheet_ref is None


def test_full_3d_camera_declaration() -> None:
    m = _with_camera(
        point_cloud={"channels": ["xyz", "rgba", "snr", "normals"], "organized": True},
        rate_hz_max=10.0,
        time_sync_methods=["ptp"],
        datasheet_ref="vendor://datasheets/model-x",
        mount={"frame": "base_link", "kind": "eye_to_hand", "calibration_ref": "cal://1"},
    )
    cam = CapabilityManifest.model_validate(m).perception.cameras[0]
    assert cam.point_cloud is not None and cam.point_cloud.organized
    assert cam.point_cloud.channels == ["xyz", "rgba", "snr", "normals"]
    assert cam.mount is not None and cam.mount.kind == "eye_to_hand"


def test_channels_are_a_closed_set() -> None:
    with pytest.raises(ValidationError, match="channels"):
        CapabilityManifest.model_validate(_with_camera(point_cloud={"channels": ["xyz", "vibes"]}))


def test_channels_must_be_non_empty() -> None:
    with pytest.raises(ValidationError, match="channels"):
        CapabilityManifest.model_validate(_with_camera(point_cloud={"channels": []}))


def test_rate_hz_max_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="rate_hz_max"):
        CapabilityManifest.model_validate(_with_camera(rate_hz_max=0))


def test_mount_frame_must_be_declared() -> None:
    with pytest.raises(ValidationError, match="not a declared frame"):
        CapabilityManifest.model_validate(_with_camera(mount={"frame": "flange", "kind": "eye_in_hand"}))


def test_mount_kind_is_closed() -> None:
    with pytest.raises(ValidationError, match="kind"):
        CapabilityManifest.model_validate(_with_camera(mount={"frame": "base_link", "kind": "on_a_stick"}))


def test_zivid_fixture_declares_every_field() -> None:
    data = yaml.safe_load((FIXTURES / "zivid_two_cell.yaml").read_text(encoding="utf-8"))
    manifest = CapabilityManifest.model_validate(data)
    zivid = next(c for c in manifest.perception.cameras if c.name == "zivid_two_cell_3d")
    assert zivid.point_cloud is not None
    assert set(zivid.point_cloud.channels) >= {"xyz", "rgba", "snr", "normals"}
    assert zivid.mount is not None and zivid.mount.frame == "base_link"
    assert zivid.datasheet_ref and zivid.rate_hz_max == 10.0
