"""RFC-0381: the optional `validation` simulation-fidelity manifest block.

Two closed-enum fields (`terrain_fidelity`, `simulator_target_class`) the
validator enforces by membership only. These tests confirm the block parses
when present and valid, is rejected on an out-of-enum value, and is fully
optional (a manifest without it parses unchanged).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from urml_validator.schemas.manifest import CapabilityManifest, ValidationContext

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "manifests"


def _load(name: str) -> dict:
    with (FIXTURE_ROOT / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_chrono_manifest_carries_validation_block() -> None:
    """The shipped chrono_vehicle_cell manifest declares the block and parses."""
    manifest = CapabilityManifest.model_validate(_load("chrono_vehicle_cell.yaml"))
    assert manifest.validation is not None
    assert manifest.validation.terrain_fidelity == "deformable"
    assert manifest.validation.simulator_target_class == "high_fidelity_multibody"


def test_validation_block_is_optional() -> None:
    """A manifest omitting `validation` parses unchanged (backward-compat guard)."""
    manifest = CapabilityManifest.model_validate(_load("turtlebot4_home.yaml"))
    assert manifest.validation is None


def test_unknown_terrain_fidelity_is_rejected() -> None:
    """An out-of-enum terrain value fails to parse (closed-enum discipline)."""
    with pytest.raises(ValidationError):
        ValidationContext.model_validate({"terrain_fidelity": "swamp"})


def test_unknown_simulator_target_class_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ValidationContext.model_validate({"simulator_target_class": "ultrareal"})


def test_extra_keys_forbidden() -> None:
    """The block forbids unknown keys, like every URML schema block."""
    with pytest.raises(ValidationError):
        ValidationContext.model_validate({"terrain_fidelity": "rigid", "made_up": 1})


def test_both_fields_optional_within_block() -> None:
    """An empty `validation: {}` block is valid; both fields default to None."""
    vc = ValidationContext.model_validate({})
    assert vc.terrain_fidelity is None and vc.simulator_target_class is None
