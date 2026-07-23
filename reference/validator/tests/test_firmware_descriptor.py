"""Unit tests for RFC-0669 MCU firmware descriptor.

Covers: the schema accepts a firmware block (STM32 instance and a non-STM32
neutrality case); required series/core and non-empty component names are
enforced; the firmware-token charset admits real MCU punctuation (hyphens, plus,
dots) but rejects whitespace and illegal characters; `firmware` composes with
`minimal_node` (no cross-block rule) and with `mobility` (not mutually exclusive);
and a full manifest carrying `firmware` validates.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.schemas.manifest import Firmware


def _minimal_node_manifest(firmware: dict, **extra: object) -> dict:
    base = {
        "manifest_version": "0.1",
        "robot_id": "mcu_board",
        "minimal_node": {
            "class": "sensor_actuator",
            "declared_sensors": ["light"],
            "declared_outputs": ["led"],
            "has_locomotion": False,
        },
        "firmware": firmware,
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


_PROGRAM = {
    "profile": "educational",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"set_output": {"output": "led", "value": True}}],
    },
}

_STM32 = {
    "series": "STM32F4",
    "core": "cortex-m4",
    "version": "1.28.0",
    "components": [{"name": "cmsis", "version": "5.9.0"}, {"name": "stm32f4xx-hal"}, {"name": "usbx"}],
}
_ESP32 = {
    "series": "esp32s3",
    "core": "xtensa-lx7",
    "version": "5.2.1",
    "components": [{"name": "esp-idf", "version": "5.2"}],
}


def test_schema_accepts_stm32_instance() -> None:
    fw = Firmware.model_validate(_STM32)
    assert fw.series == "STM32F4"
    assert fw.core == "cortex-m4"
    assert [c.name for c in fw.components] == ["cmsis", "stm32f4xx-hal", "usbx"]


def test_schema_accepts_non_stm32_neutrality() -> None:
    fw = Firmware.model_validate(_ESP32)
    assert fw.series == "esp32s3"
    assert fw.core == "xtensa-lx7"


def test_series_and_core_required() -> None:
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"core": "cortex-m4"})
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": "STM32F4"})


def test_empty_series_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": "", "core": "cortex-m4"})


def test_component_name_required_and_nonempty() -> None:
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": "stm32f4", "core": "cortex-m4", "components": [{"version": "1.0"}]})
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": "stm32f4", "core": "cortex-m4", "components": [{"name": ""}]})


@pytest.mark.parametrize("core", ["cortex-m4", "cortex-m0+", "xtensa-lx7", "riscv32", "cortex_m33"])
def test_firmware_token_admits_real_mcu_punctuation(core: str) -> None:
    fw = Firmware.model_validate({"series": "stm32f4", "core": core})
    assert fw.core == core


@pytest.mark.parametrize("bad", ["stm32 f4", "STM32/F4", "stm32\tf4", "-leading"])
def test_firmware_token_rejects_illegal(bad: str) -> None:
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": bad, "core": "cortex-m4"})


def test_extra_fields_forbidden() -> None:
    with pytest.raises(PydanticValidationError):
        Firmware.model_validate({"series": "stm32f4", "core": "cortex-m4", "vendor": "st"})


def test_version_and_components_optional() -> None:
    fw = Firmware.model_validate({"series": "nrf52", "core": "cortex-m4"})
    assert fw.version is None
    assert fw.components == []


def test_full_manifest_with_firmware_validates() -> None:
    # policy=None: this is a capability-shape check, not a compliance check.
    for firmware in (_STM32, _ESP32):
        result = validate(_PROGRAM, _minimal_node_manifest(firmware), profiles=("educational",), policy=None)
        assert result.accepted, [e.code_str for e in result.errors]


def test_firmware_not_mutually_exclusive_with_mobility() -> None:
    # Unlike minimal_node, firmware has no cross-block rule: a mobile robot's
    # compute board also runs firmware. A mobility manifest carrying firmware and
    # no minimal_node must not raise a firmware-specific rejection.
    manifest = {
        "manifest_version": "0.1",
        "robot_id": "mobile_with_firmware",
        "mobility": {"drive_type": "differential", "max_velocity": 0.6},
        "firmware": _ESP32,
    }
    result = validate(
        {"profile": "home", "behavior": {"type": "sequence", "on_error": "abort_and_report",
         "steps": [{"wait": {"seconds": 1}}]}},
        manifest,
        profiles=("home",),
        policy=None,
    )
    # It may or may not accept for unrelated reasons, but no firmware/minimal_node
    # mutual-exclusion error should appear.
    codes = {e.code_str for e in result.errors}
    assert "capability.minimal_node_with_mobility" not in codes
