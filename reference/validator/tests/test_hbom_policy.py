"""RFC-0005 — structured HBOM-content policy predicates (Pass 5 sub-pass).

Exercises the country/vendor deny-list predicates against parsed CycloneDX
HBOM fixtures, including the pedigree walk (vendor-of-vendor), and the
resolution-failure diagnostics (hash mismatch, malformed, remote/missing uri).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator.errors import ErrorCode
from urml_validator.policy_engine import evaluate_policy
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.schemas.policy import Policy, PolicyRule, RulePredicate

_MANIFESTS_DIR = Path(__file__).parent / "fixtures" / "manifests"

# SHA-256 of the committed HBOM fixtures (see fixtures/manifests/hbom/).
_SHA = {
    "clean": "ab383cf8f6b5ec1b1a25df88038034eb02edd619153ff369e596fbb41388f5e3",
    "cn_chip": "95873e0edf7f58c310d7811304cb3deb1d2cd82d9213fb76a106ad2543112683",
    "vendor_of_vendor": "7c7cf21ce0a31af0668f28660719960eed12093002f660e32e0c185c5aef8070",
    "malformed": "aed0f916b781ff9a39ff077d4966c2366b6cd3addfd5d000149606f3d7917c56",
}


def _manifest(hbom_file: str, sha: str | None, uri: str | None = None) -> CapabilityManifest:
    """A minimal manifest whose one critical component points at an HBOM file."""
    return CapabilityManifest.model_validate(
        {
            "manifest_version": "0.1",
            "robot_id": "hbom_test",
            "mobility": {"drive_type": "differential", "max_velocity": 0.5},
            "provenance": {
                "manifest_attestation": "self_declared",
                "components": [
                    {
                        "id": "drive_controller",
                        "role": "critical",
                        "vendor": "acme",
                        "country_of_origin": "US",
                        "country_of_final_assembly": "US",
                        "hbom_ref": {
                            "format": "cyclonedx-1.5",
                            "uri": uri if uri is not None else f"hbom/{hbom_file}",
                            **({"sha256": sha} if sha is not None else {}),
                        },
                    }
                ],
            },
        }
    )


def _deny_country_policy(countries: list[str]) -> Policy:
    return Policy(
        policy_id="hbom_test_policy",
        rules=[
            PolicyRule(
                id="no_covered_country_in_hbom",
                applies_to={"component_role": "critical"},
                deny=RulePredicate(hbom_no_components_from_country=countries),
                on_violation={"code": "policy.hbom_component_country_denied"},
            )
        ],
    )


def _deny_vendor_policy(vendors: list[str]) -> Policy:
    return Policy(
        policy_id="hbom_test_policy",
        rules=[
            PolicyRule(
                id="no_covered_vendor_in_hbom",
                applies_to={"component_role": "critical"},
                deny=RulePredicate(hbom_no_components_from_vendor=vendors),
                on_violation={"code": "policy.hbom_component_vendor_denied"},
            )
        ],
    )


# ---------------------------------------------------------------------------
# Content predicates: accept / reject
# ---------------------------------------------------------------------------


def test_clean_hbom_passes_country_denylist():
    manifest = _manifest("clean.cdx.json", _SHA["clean"])
    issues = evaluate_policy(manifest, _deny_country_policy(["CN", "RU"]), manifest_base_dir=_MANIFESTS_DIR)
    assert issues == []


def test_cn_chip_trips_country_denylist():
    manifest = _manifest("cn_chip.cdx.json", _SHA["cn_chip"])
    issues = evaluate_policy(manifest, _deny_country_policy(["CN", "RU"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_COMPONENT_COUNTRY_DENIED
    assert issues[0].severity == "error"
    assert issues[0].detail["hbom_component"] == "wireless_module"
    assert issues[0].detail["hbom_component_country"] == "CN"
    assert issues[0].detail["pedigree_depth"] == 0


def test_vendor_denylist_trips_on_supplier_name():
    manifest = _manifest("cn_chip.cdx.json", _SHA["cn_chip"])
    issues = evaluate_policy(
        manifest, _deny_vendor_policy(["Example Covered Vendor"]), manifest_base_dir=_MANIFESTS_DIR
    )
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_COMPONENT_VENDOR_DENIED
    assert issues[0].detail["hbom_component"] == "wireless_module"


def test_pedigree_ancestor_caught_at_depth_one():
    """Vendor-of-vendor: a covered chip hidden in pedigree.ancestors is caught."""
    manifest = _manifest("vendor_of_vendor.cdx.json", _SHA["vendor_of_vendor"])
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_COMPONENT_COUNTRY_DENIED
    assert issues[0].detail["hbom_component"] == "rebadged_rf_die"
    assert issues[0].detail["pedigree_depth"] == 1


def test_component_without_hbom_ref_is_not_checked():
    manifest = CapabilityManifest.model_validate(
        {
            "manifest_version": "0.1",
            "robot_id": "no_hbom",
            "mobility": {"drive_type": "differential", "max_velocity": 0.5},
            "provenance": {
                "components": [
                    {
                        "id": "drive_controller",
                        "role": "critical",
                        "vendor": "acme",
                        "country_of_origin": "US",
                        "country_of_final_assembly": "US",
                    }
                ]
            },
        }
    )
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert issues == []


# ---------------------------------------------------------------------------
# Resolution failures
# ---------------------------------------------------------------------------


def test_hash_mismatch_is_parse_failed_error():
    manifest = _manifest("clean.cdx.json", "00" * 32)
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_PARSE_FAILED
    assert issues[0].severity == "error"
    assert issues[0].detail["hash_mismatch"] is True


def test_malformed_json_is_parse_failed_error():
    manifest = _manifest("malformed.cdx.json", _SHA["malformed"])
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_PARSE_FAILED
    assert issues[0].detail["reason"] == "malformed_json"


def test_remote_uri_is_unreachable_warning():
    manifest = _manifest("ignored", None, uri="https://example.com/hbom/drive.cdx.json")
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_URI_UNREACHABLE
    assert issues[0].severity == "warning"


def test_missing_base_dir_degrades_to_unreachable_warning():
    manifest = _manifest("clean.cdx.json", _SHA["clean"])
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=None)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_URI_UNREACHABLE
    assert issues[0].severity == "warning"
    assert issues[0].detail["reason"] == "no_base_dir_for_relative_uri"


def test_missing_file_is_unreachable_warning():
    manifest = _manifest("does_not_exist.cdx.json", None)
    issues = evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR)
    assert len(issues) == 1
    assert issues[0].code == ErrorCode.POLICY_HBOM_URI_UNREACHABLE
    assert issues[0].detail["reason"] == "file_not_found"


# ---------------------------------------------------------------------------
# Schema guards
# ---------------------------------------------------------------------------


def test_mixing_manifest_and_hbom_predicates_rejected():
    with pytest.raises(PydanticValidationError):
        RulePredicate(country_of_origin_in=["US"], hbom_no_components_from_country=["CN"])


def test_hbom_predicate_under_require_rejected():
    with pytest.raises(PydanticValidationError):
        PolicyRule(
            id="bad",
            applies_to={"component_role": "critical"},
            require=RulePredicate(hbom_no_components_from_country=["CN"]),
            on_violation={"code": "policy.hbom_component_country_denied"},
        )


def test_no_provenance_means_no_hbom_checks():
    manifest = CapabilityManifest.model_validate(
        {
            "manifest_version": "0.1",
            "robot_id": "no_provenance",
            "mobility": {"drive_type": "differential", "max_velocity": 0.5},
        }
    )
    assert evaluate_policy(manifest, _deny_country_policy(["CN"]), manifest_base_dir=_MANIFESTS_DIR) == []
