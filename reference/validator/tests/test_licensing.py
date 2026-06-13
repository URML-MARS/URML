"""RFC-0262 — license-boundary (`licensing`) declarations.

Covers the schema (closed license/boundary enums, network_rest-requires-endpoint),
the vendored-copyleft hard error (policy-independent), and the
`policy_required_max_restrictiveness` gate (policy-dependent).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import CapabilityManifest

_BASE = {
    "manifest_version": "0.1",
    "robot_id": "lic_test",
    "mobility": {"drive_type": "differential", "max_velocity": 0.5},
    "frames": [{"name": "map", "parent": None}],
    "declared_locations": [{"name": "kitchen", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"}],
}
_PROG = {
    "profile": "home",
    "behavior": {"type": "sequence", "on_error": "abort_and_report",
                 "steps": [{"move_to": {"location": "kitchen"}}]},
}


def _m(licensing: dict) -> dict:
    return {**_BASE, "licensing": licensing}


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_clean_components_parse_and_accept():
    lic = {
        "components": [
            {"name": "piper", "license": "gpl_3_0", "boundary": "subprocess", "commercial_use_gate": False},
            {"name": "nllb", "license": "cc_by_nc_4_0", "boundary": "cross_citation", "commercial_use_gate": True},
            {"name": "lt", "license": "agpl_3_0", "boundary": "network_rest",
             "network_endpoint": "https://lt.example.org/", "secret_reference": "env:LT_KEY"},
        ]
    }
    r = validate(_PROG, _m(lic), profiles=("home",), policy=None)
    assert r.accepted


def test_network_rest_requires_endpoint():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(
            _m({"components": [{"name": "lt", "license": "agpl_3_0", "boundary": "network_rest"}]})
        )


def test_unknown_license_rejected():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(
            _m({"components": [{"name": "x", "license": "wtfpl", "boundary": "subprocess"}]})
        )


def test_unknown_boundary_rejected():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(
            _m({"components": [{"name": "x", "license": "mit", "boundary": "statically_linked"}]})
        )


# ---------------------------------------------------------------------------
# Vendored-copyleft hard error (policy-independent)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lic_id", ["gpl_3_0", "agpl_3_0", "cc_by_nc_4_0", "lgpl_3_0", "unknown"])
def test_vendored_non_permissive_rejected(lic_id):
    r = validate(_PROG, _m({"components": [{"name": "c", "license": lic_id, "boundary": "vendored"}]}),
                 profiles=("home",), policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_LICENSE_VENDORED_COPYLEFT.value in _codes(r.errors)


@pytest.mark.parametrize("lic_id", ["apache_2_0", "bsd_3_clause", "mit", "mpl_2_0"])
def test_vendored_permissive_accepted(lic_id):
    r = validate(_PROG, _m({"components": [{"name": "c", "license": lic_id, "boundary": "vendored"}]}),
                 profiles=("home",), policy=None)
    assert r.accepted


def test_copyleft_subprocess_accepted():
    r = validate(_PROG, _m({"components": [{"name": "piper", "license": "gpl_3_0", "boundary": "subprocess"}]}),
                 profiles=("home",), policy=None)
    assert r.accepted


# ---------------------------------------------------------------------------
# policy_required_max_restrictiveness gate (policy-dependent)
# ---------------------------------------------------------------------------


def test_restrictiveness_cap_rejected_under_policy():
    lic = {"components": [{"name": "orb", "license": "gpl_3_0", "boundary": "cross_citation"}],
           "policy_required_max_restrictiveness": "lgpl_3_0"}
    r = validate(_PROG, _m(lic), profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_LICENSE_TOO_RESTRICTIVE.value in _codes(r.errors)


def test_restrictiveness_cap_accepted_without_policy():
    lic = {"components": [{"name": "orb", "license": "gpl_3_0", "boundary": "cross_citation"}],
           "policy_required_max_restrictiveness": "lgpl_3_0"}
    r = validate(_PROG, _m(lic), profiles=("home",), policy=None)
    assert r.accepted  # the cap is enforced only under a policy


def test_restrictiveness_cap_at_or_below_accepted_under_policy():
    lic = {"components": [{"name": "ok", "license": "mit", "boundary": "vendored"}],
           "policy_required_max_restrictiveness": "lgpl_3_0"}
    r = validate(_PROG, _m(lic), profiles=("home",), policy="DEFAULT")
    assert r.accepted


def test_restrictiveness_cap_under_custom_policy_enforced():
    lic = {"components": [{"name": "orb", "license": "agpl_3_0", "boundary": "cross_citation"}],
           "policy_required_max_restrictiveness": "gpl_3_0"}
    custom = {"policy_id": "custom_p", "rules": []}
    r = validate(_PROG, _m(lic), profiles=("home",), policy=custom)
    assert not r.accepted  # any active policy enforces the manifest's own cap
    assert ErrorCode.POLICY_LICENSE_TOO_RESTRICTIVE.value in _codes(r.errors)


def test_no_licensing_block_passes():
    r = validate(_PROG, _BASE, profiles=("home",), policy="DEFAULT")
    assert r.accepted
