"""RFC-0268 — `deployment.commercial_use` and the commercial-use gate.

Closes RFC-0262's loop: a `commercial_use_gate` component is a violation only
when the deployment is commercial. Covers the most-restrictive default, the
policy gate (error) vs default-mode advisory (warning), the
non-commercial override, and the class/commercial consistency warning.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import CapabilityManifest

_BASE = {
    "manifest_version": "0.1",
    "robot_id": "dep_test",
    "mobility": {"drive_type": "differential", "max_velocity": 0.5},
    "frames": [{"name": "map", "parent": None}],
    "declared_locations": [{"name": "kitchen", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"}],
}
_PROG = {
    "profile": "home",
    "behavior": {"type": "sequence", "on_error": "abort_and_report",
                 "steps": [{"move_to": {"location": "kitchen"}}]},
}
_GATED = {"components": [{"name": "nllb", "license": "cc_by_nc_4_0",
                          "boundary": "cross_citation", "commercial_use_gate": True}]}


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_deployment_block_parses():
    CapabilityManifest.model_validate(
        {**_BASE, "deployment": {"commercial_use": False, "deployment_class": "research",
                                 "organization": "lab", "declared_at": "2026-06-12"}}
    )


def test_commercial_use_defaults_true():
    m = CapabilityManifest.model_validate({**_BASE, "deployment": {"deployment_class": "production"}})
    assert m.deployment.commercial_use is True


def test_unknown_deployment_class_rejected():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate({**_BASE, "deployment": {"deployment_class": "military"}})


# ---------------------------------------------------------------------------
# Commercial-use gate (the RFC-0262 loop)
# ---------------------------------------------------------------------------


def test_commercial_default_gated_rejected_under_policy():
    # No deployment block -> commercial by default (most-restrictive).
    r = validate(_PROG, {**_BASE, "licensing": _GATED}, profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)


def test_commercial_explicit_gated_rejected_under_policy():
    m = {**_BASE, "licensing": _GATED, "deployment": {"commercial_use": True}}
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)


def test_noncommercial_gated_accepted_under_policy():
    m = {**_BASE, "licensing": _GATED, "deployment": {"commercial_use": False}}
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert r.accepted


def test_commercial_gated_advisory_warning_without_policy():
    r = validate(_PROG, {**_BASE, "licensing": _GATED}, profiles=("home",), policy=None)
    assert r.accepted  # advisory only in default mode
    assert ErrorCode.CAPABILITY_COMMERCIAL_GATE_ADVISORY.value in _codes(r.warnings)


def test_commercial_gated_under_custom_policy_enforced():
    custom = {"policy_id": "custom_p", "rules": []}
    r = validate(_PROG, {**_BASE, "licensing": _GATED}, profiles=("home",), policy=custom)
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)


def test_no_gated_component_no_gate():
    lic = {"components": [{"name": "piper", "license": "gpl_3_0", "boundary": "subprocess",
                           "commercial_use_gate": False}]}
    r = validate(_PROG, {**_BASE, "licensing": lic}, profiles=("home",), policy="DEFAULT")
    assert r.accepted


def test_no_licensing_block_commercial_passes():
    r = validate(_PROG, {**_BASE, "deployment": {"commercial_use": True}}, profiles=("home",), policy="DEFAULT")
    assert r.accepted


# ---------------------------------------------------------------------------
# Consistency warning
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("klass", ["research", "education", "hobby"])
def test_noncommercial_class_but_commercial_warns(klass):
    m = {**_BASE, "deployment": {"commercial_use": True, "deployment_class": klass}}
    r = validate(_PROG, m, profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_COMMERCIAL_USE_CLASS_INCONSISTENT.value in _codes(r.warnings)


def test_production_commercial_no_consistency_warning():
    m = {**_BASE, "deployment": {"commercial_use": True, "deployment_class": "production"}}
    r = validate(_PROG, m, profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_COMMERCIAL_USE_CLASS_INCONSISTENT.value not in _codes(r.warnings)


def test_research_noncommercial_no_warning():
    m = {**_BASE, "deployment": {"commercial_use": False, "deployment_class": "research"}}
    r = validate(_PROG, m, profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_COMMERCIAL_USE_CLASS_INCONSISTENT.value not in _codes(r.warnings)
