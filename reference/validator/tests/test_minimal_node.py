"""Unit tests for RFC-0018 minimal sensor/actuator MCU-node declaration.

Covers manifest-static coherence: a valid minimal_node board is accepted;
minimal_node + mobility is rejected (mutual exclusion); has_locomotion=True is
rejected; declared outputs must be real outputs.lines; declared sensors must be
in perception.sensors. Also the intra-block class/declaration coherence.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import MinimalNode


def _manifest(minimal_node: dict, **extra: object) -> dict:
    base = {
        "manifest_version": "0.1",
        "robot_id": "mcu_board",
        "minimal_node": minimal_node,
        "perception": {
            "cameras": [],
            "sensors": [
                {"name": "light", "measurement_type": "custom", "range_min": 0.0, "range_max": 1000.0, "units": "lux"}
            ],
            "object_vocabulary": [],
        },
        "outputs": {"lines": [{"name": "led", "kind": "digital", "safe_state": False}]},
    }
    base.update(extra)
    return base


# A program a minimal node can actually run: a single set_output on its line.
_PROGRAM = {
    "profile": "educational",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"set_output": {"output": "led", "value": True}}],
    },
}

_NODE = {"class": "sensor_actuator", "declared_sensors": ["light"], "declared_outputs": ["led"], "has_locomotion": False}


def test_valid_minimal_node_accepted() -> None:
    r = validate(_PROGRAM, _manifest(_NODE), policy=None)
    assert r.accepted, [e.code for e in r.errors]


def test_minimal_node_with_mobility_rejected() -> None:
    man = _manifest(_NODE, mobility={"drive_type": "differential", "max_velocity": 0.5})
    r = validate(_PROGRAM, man, policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_MINIMAL_NODE_WITH_MOBILITY in {e.code for e in r.errors}


def test_minimal_node_has_locomotion_rejected() -> None:
    node = {**_NODE, "has_locomotion": True}
    r = validate(_PROGRAM, _manifest(node), policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_MINIMAL_NODE_LOCOMOTION_INCONSISTENT in {e.code for e in r.errors}


def test_minimal_node_undeclared_output_rejected() -> None:
    node = {"class": "actuator", "declared_outputs": ["buzzer"]}
    r = validate(_PROGRAM, _manifest(node), policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_MINIMAL_NODE_UNDECLARED_OUTPUT in {e.code for e in r.errors}


def test_minimal_node_undeclared_sensor_rejected() -> None:
    node = {"class": "sensor_actuator", "declared_sensors": ["sonar"], "declared_outputs": ["led"]}
    r = validate(_PROGRAM, _manifest(node), policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_MINIMAL_NODE_UNDECLARED_SENSOR in {e.code for e in r.errors}


def test_actuator_class_requires_outputs() -> None:
    with pytest.raises(PydanticValidationError):
        MinimalNode(**{"class": "actuator", "declared_outputs": []})


def test_sensor_class_requires_sensors() -> None:
    with pytest.raises(PydanticValidationError):
        MinimalNode(**{"class": "sensor", "declared_sensors": []})


def test_minimal_node_serializes_with_class_alias() -> None:
    node = MinimalNode(**{"class": "actuator", "declared_outputs": ["led"]})
    assert node.class_ == "actuator"
    assert node.model_dump(by_alias=True)["class"] == "actuator"
