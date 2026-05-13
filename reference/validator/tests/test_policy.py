"""Unit tests for the compliance policy engine and Pass 5 integration."""

from __future__ import annotations

from typing import Any

import pytest

from urml_validator import (
    DEFAULT_POLICY,
    ErrorCode,
    Policy,
    ValidationError,
    evaluate_policy,
    validate,
)
from urml_validator.policy_engine import _resolve_code
from urml_validator.schemas.manifest import (
    CapabilityManifest,
    HBOMRef,
    Provenance,
    ProvenanceComponent,
)
from urml_validator.schemas.policy import (
    OnViolation,
    PolicyRule,
    RulePredicate,
    RuleSelector,
)


# ---------------------------------------------------------------------------
# Fixtures: minimal but realistic data the engine can operate on.
# ---------------------------------------------------------------------------


def _component(
    id: str = "drive_controller",
    role: str = "critical",
    vendor: str = "example_vendor",
    country_of_origin: str = "US",
    country_of_final_assembly: str = "US",
    with_hbom: bool = True,
) -> ProvenanceComponent:
    hbom = (
        HBOMRef(format="cyclonedx-1.7", uri="./hbom/x.json", sha256="abc")
        if with_hbom
        else None
    )
    return ProvenanceComponent(
        id=id,
        role=role,  # type: ignore[arg-type]
        vendor=vendor,
        country_of_origin=country_of_origin,
        country_of_final_assembly=country_of_final_assembly,
        hbom_ref=hbom,
    )


def _provenance(
    *components: ProvenanceComponent,
    attestation: str = "third_party_audited",
) -> Provenance:
    return Provenance(
        manifest_attestation=attestation,  # type: ignore[arg-type]
        components=list(components),
    )


def _manifest(provenance: Provenance | None = None) -> CapabilityManifest:
    return CapabilityManifest(
        robot_id="test_bot",
        provenance=provenance,
    )


def _policy(*rules: PolicyRule, policy_id: str = "test_policy") -> Policy:
    return Policy(policy_id=policy_id, rules=list(rules))


def _country_denylist_rule(
    countries: list[str], role: str = "critical"
) -> PolicyRule:
    return PolicyRule(
        id="country_deny",
        applies_to=RuleSelector(component_role=role),  # type: ignore[arg-type]
        deny=RulePredicate(country_of_origin_in=countries),
        on_violation=OnViolation(code="policy.country_denied"),
    )


def _vendor_denylist_rule(vendors: list[str]) -> PolicyRule:
    return PolicyRule(
        id="vendor_deny",
        applies_to=RuleSelector(component_role="any"),
        deny=RulePredicate(vendor_in=vendors),
        on_violation=OnViolation(code="policy.vendor_denied"),
    )


def _hbom_required_rule() -> PolicyRule:
    return PolicyRule(
        id="hbom_required",
        applies_to=RuleSelector(component_role="critical"),
        require=RulePredicate(hbom_ref_present=True),
        on_violation=OnViolation(code="policy.hbom_missing"),
    )


def _attestation_floor_rule(severity: str = "error") -> PolicyRule:
    return PolicyRule(
        id="attestation_floor",
        applies_to=RuleSelector(scope="manifest"),
        require=RulePredicate(
            manifest_attestation_in=["third_party_audited", "cryptographically_signed"]
        ),
        on_violation=OnViolation(
            code="policy.attestation_insufficient",
            severity=severity,  # type: ignore[arg-type]
        ),
    )


def _trivial_program() -> dict[str, Any]:
    """A minimal program that exercises Pass 5 without Pass 1-4 issues.

    `wait` is the only primitive with zero manifest-capability requirements,
    so it works against the bare-bones test manifests in this file.
    """
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"wait": {"duration": "1s"}}],
        },
    }


# ===========================================================================
# Policy engine — direct evaluation
# ===========================================================================


class TestPolicyEngineDirectEvaluation:
    """Tests that call `evaluate_policy()` directly."""

    def test_manifest_without_provenance_yields_no_errors(self) -> None:
        manifest = _manifest(provenance=None)
        policy = _policy(_country_denylist_rule(["CN"]))
        assert evaluate_policy(manifest, policy) == []

    def test_country_denylist_fires_on_match(self) -> None:
        manifest = _manifest(
            _provenance(_component(country_of_origin="CN"))
        )
        policy = _policy(_country_denylist_rule(["CN", "RU"]))
        issues = evaluate_policy(manifest, policy)
        assert len(issues) == 1
        assert str(issues[0].code) == "policy.country_denied"
        assert issues[0].detail is not None
        assert issues[0].detail["offending_value"] == "CN"
        assert issues[0].detail["component_id"] == "drive_controller"
        assert issues[0].detail["denied_values"] == ["CN", "RU"]
        assert issues[0].detail["remediation_hint"] == "swap_component"

    def test_country_denylist_skips_non_matching_components(self) -> None:
        manifest = _manifest(
            _provenance(_component(country_of_origin="US"))
        )
        policy = _policy(_country_denylist_rule(["CN"]))
        assert evaluate_policy(manifest, policy) == []

    def test_country_denylist_role_selector_filters(self) -> None:
        # Critical component is US (clean); non-critical is CN (would match an `any` rule).
        critical = _component(id="ctrl", role="critical", country_of_origin="US")
        non_crit = _component(
            id="trim",
            role="non_critical",
            country_of_origin="CN",
        )
        manifest = _manifest(_provenance(critical, non_crit))
        # Critical-only rule: only inspects critical components, finds none.
        policy = _policy(_country_denylist_rule(["CN"], role="critical"))
        assert evaluate_policy(manifest, policy) == []
        # `any` rule: inspects both, finds the non-critical CN component.
        policy_any = _policy(_country_denylist_rule(["CN"], role="any"))
        issues = evaluate_policy(manifest, policy_any)
        assert len(issues) == 1
        assert issues[0].detail is not None
        assert issues[0].detail["component_id"] == "trim"

    def test_vendor_denylist(self) -> None:
        manifest = _manifest(_provenance(_component(vendor="dji")))
        policy = _policy(_vendor_denylist_rule(["dji", "autel"]))
        issues = evaluate_policy(manifest, policy)
        assert len(issues) == 1
        assert str(issues[0].code) == "policy.vendor_denied"
        assert issues[0].detail is not None
        assert issues[0].detail["offending_field"] == "vendor"

    def test_hbom_required_fires_when_missing(self) -> None:
        manifest = _manifest(_provenance(_component(with_hbom=False)))
        policy = _policy(_hbom_required_rule())
        issues = evaluate_policy(manifest, policy)
        assert len(issues) == 1
        assert str(issues[0].code) == "policy.hbom_missing"

    def test_hbom_required_passes_when_present(self) -> None:
        manifest = _manifest(_provenance(_component(with_hbom=True)))
        policy = _policy(_hbom_required_rule())
        assert evaluate_policy(manifest, policy) == []

    def test_manifest_scope_attestation_floor_fires(self) -> None:
        manifest = _manifest(_provenance(attestation="self_declared"))
        policy = _policy(_attestation_floor_rule())
        issues = evaluate_policy(manifest, policy)
        assert len(issues) == 1
        assert str(issues[0].code) == "policy.attestation_insufficient"
        assert issues[0].detail is not None
        assert issues[0].detail["offending_value"] == "self_declared"
        assert issues[0].detail["allowed_values"] == [
            "third_party_audited",
            "cryptographically_signed",
        ]

    def test_manifest_scope_attestation_floor_passes(self) -> None:
        manifest = _manifest(_provenance(attestation="third_party_audited"))
        policy = _policy(_attestation_floor_rule())
        assert evaluate_policy(manifest, policy) == []

    def test_severity_warning_is_preserved(self) -> None:
        manifest = _manifest(_provenance(attestation="self_declared"))
        policy = _policy(_attestation_floor_rule(severity="warning"))
        issues = evaluate_policy(manifest, policy)
        assert len(issues) == 1
        assert issues[0].severity == "warning"

    def test_first_match_wins_per_component(self) -> None:
        # Two rules both target critical/CN. Only the first emits.
        manifest = _manifest(_provenance(_component(country_of_origin="CN")))
        rule_a = PolicyRule(
            id="rule_a",
            applies_to=RuleSelector(component_role="critical"),
            deny=RulePredicate(country_of_origin_in=["CN"]),
            on_violation=OnViolation(code="policy.country_denied"),
        )
        rule_b = PolicyRule(
            id="rule_b",
            applies_to=RuleSelector(component_role="critical"),
            deny=RulePredicate(country_of_origin_in=["CN"]),
            on_violation=OnViolation(code="policy.country_denied"),
        )
        issues = evaluate_policy(manifest, _policy(rule_a, rule_b))
        # Each component emits at most one error per rule, but both rules
        # process the same component independently. Verify both fire (the
        # "first-match-wins" semantics apply per-dimension within a rule,
        # not across rules).
        assert len(issues) == 2

    def test_component_id_selector(self) -> None:
        a = _component(id="part_a", country_of_origin="US")
        b = _component(id="part_b", country_of_origin="CN")
        manifest = _manifest(_provenance(a, b))
        rule = PolicyRule(
            id="part_b_only",
            applies_to=RuleSelector(component_id="part_b"),
            deny=RulePredicate(country_of_origin_in=["CN"]),
            on_violation=OnViolation(code="policy.country_denied"),
        )
        issues = evaluate_policy(manifest, _policy(rule))
        assert len(issues) == 1
        assert issues[0].detail is not None
        assert issues[0].detail["component_id"] == "part_b"

    def test_empty_rules_list_is_noop(self) -> None:
        manifest = _manifest(_provenance(_component(country_of_origin="CN")))
        assert evaluate_policy(manifest, _policy()) == []


# ===========================================================================
# Policy schema — pydantic-level constraints
# ===========================================================================


class TestPolicySchemaConstraints:
    def test_require_and_deny_are_mutually_exclusive(self) -> None:
        with pytest.raises(ValueError, match="mutually exclusive"):
            PolicyRule(
                id="bad",
                applies_to=RuleSelector(component_role="critical"),
                require=RulePredicate(country_of_origin_in=["US"]),
                deny=RulePredicate(country_of_origin_in=["CN"]),
                on_violation=OnViolation(code="policy.bad"),
            )

    def test_rule_must_have_require_or_deny(self) -> None:
        with pytest.raises(ValueError, match="must set one of"):
            PolicyRule(
                id="bad",
                applies_to=RuleSelector(component_role="critical"),
                on_violation=OnViolation(code="policy.bad"),
            )

    def test_selector_must_set_exactly_one(self) -> None:
        with pytest.raises(ValueError, match="exactly one"):
            RuleSelector(component_role="critical", scope="manifest")

    def test_selector_must_set_at_least_one(self) -> None:
        with pytest.raises(ValueError, match="exactly one"):
            RuleSelector()

    def test_on_violation_code_must_be_in_policy_namespace(self) -> None:
        with pytest.raises(ValueError, match="policy."):
            OnViolation(code="capability.foo")


# ===========================================================================
# validate() integration — Pass 5 reaches the right places
# ===========================================================================


class TestValidateIntegration:
    def _make_program_and_manifest_dict(
        self, *, country: str = "US", vendor: str = "example_vendor", with_provenance: bool = True
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        program = _trivial_program()
        manifest: dict[str, Any] = {
            "manifest_version": "0.1",
            "robot_id": "test_bot",
        }
        if with_provenance:
            manifest["provenance"] = {
                "manifest_attestation": "third_party_audited",
                "components": [
                    {
                        "id": "drive_controller",
                        "role": "critical",
                        "vendor": vendor,
                        "country_of_origin": country,
                        "country_of_final_assembly": country,
                        "hbom_ref": {
                            "format": "cyclonedx-1.7",
                            "uri": "./hbom/x.json",
                            "sha256": "abc",
                        },
                    }
                ],
            }
        return program, manifest

    def test_default_policy_loads_and_accepts_us_compliant_manifest(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="US")
        result = validate(program, manifest)  # default policy active
        assert result.accepted, result.codes()

    def test_default_policy_rejects_cn_critical_component(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="CN")
        result = validate(program, manifest)
        assert not result.accepted
        assert "policy.country_denied" in result.codes()

    def test_default_policy_rejects_covered_vendor(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(
            country="US", vendor="dji"
        )
        result = validate(program, manifest)
        assert not result.accepted
        assert "policy.vendor_denied" in result.codes()

    def test_policy_none_skips_pass_5(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="CN")
        result = validate(program, manifest, policy=None)
        assert result.accepted, result.codes()

    def test_manifest_without_provenance_skips_pass_5(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(
            with_provenance=False
        )
        result = validate(program, manifest)
        assert result.accepted, result.codes()

    def test_explicit_dict_policy(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="US")
        explicit_policy: dict[str, Any] = {
            "policy_version": "0.1",
            "policy_id": "test_explicit",
            "rules": [
                {
                    "id": "us_denied",
                    "applies_to": {"component_role": "critical"},
                    "deny": {"country_of_origin_in": ["US"]},
                    "on_violation": {"code": "policy.country_denied"},
                }
            ],
        }
        result = validate(program, manifest, policy=explicit_policy)
        assert not result.accepted
        assert "policy.country_denied" in result.codes()

    def test_explicit_policy_model(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="US")
        explicit = _policy(_country_denylist_rule(["US"]), policy_id="test_model")
        result = validate(program, manifest, policy=explicit)
        assert not result.accepted

    def test_malformed_policy_produces_rule_invalid(self) -> None:
        program, manifest = self._make_program_and_manifest_dict(country="US")
        bad: dict[str, Any] = {
            "policy_version": "0.1",
            "policy_id": "bad",
            "rules": [{"id": "missing_required_fields"}],
        }
        result = validate(program, manifest, policy=bad)
        assert not result.accepted
        assert "policy.rule_invalid" in result.codes()

    def test_warning_severity_does_not_block_acceptance(self) -> None:
        # Manifest is fully US-compliant for the default policy rules
        # *except* it self-declares attestation, which triggers a warning.
        program = _trivial_program()
        manifest: dict[str, Any] = {
            "manifest_version": "0.1",
            "robot_id": "test_bot",
            "provenance": {
                "manifest_attestation": "self_declared",
                "components": [
                    {
                        "id": "drive_controller",
                        "role": "critical",
                        "vendor": "example_vendor",
                        "country_of_origin": "US",
                        "country_of_final_assembly": "US",
                        "hbom_ref": {
                            "format": "cyclonedx-1.7",
                            "uri": "./hbom/x.json",
                            "sha256": "abc",
                        },
                    }
                ],
            },
        }
        result = validate(program, manifest)
        assert result.accepted, result.codes()
        # The attestation_floor warning should have fired.
        assert any(
            str(w.code) == "policy.attestation_insufficient" for w in result.warnings
        )


# ===========================================================================
# ValidationError.detail and code-handling
# ===========================================================================


class TestValidationErrorChanges:
    def test_detail_field_is_optional(self) -> None:
        err = ValidationError(
            code=ErrorCode.CAPABILITY_MISSING_MOBILITY,
            message="test",
        )
        assert err.detail is None

    def test_str_code_in_policy_namespace_is_accepted(self) -> None:
        err = ValidationError(code="policy.author_custom_code", message="x")
        # Either coerced to ErrorCode (if matched) or kept as str.
        assert str(err.code) == "policy.author_custom_code"

    def test_resolve_code_coerces_known_codes(self) -> None:
        on_viol = OnViolation(code="policy.country_denied")
        resolved = _resolve_code(on_viol)
        assert resolved is ErrorCode.POLICY_COUNTRY_DENIED

    def test_resolve_code_keeps_unknown_policy_codes_as_str(self) -> None:
        on_viol = OnViolation(code="policy.custom_thing")
        resolved = _resolve_code(on_viol)
        assert resolved == "policy.custom_thing"
        assert not isinstance(resolved, ErrorCode)


# ===========================================================================
# Default policy sanity
# ===========================================================================


class TestBundledDefaultPolicy:
    def test_default_sentinel_loads(self) -> None:
        # Just verifying the bundle loads. If this passes, the package data
        # is present and us_federal_default.yaml parses cleanly.
        program = _trivial_program()
        manifest = {"manifest_version": "0.1", "robot_id": "bot"}
        result = validate(program, manifest, policy=DEFAULT_POLICY)
        assert result.accepted, result.codes()

    def test_default_policy_id(self) -> None:
        from urml_validator.validator import _load_default_policy

        loaded = _load_default_policy()
        assert loaded.policy_id == "urml_us_federal_default"
        assert len(loaded.rules) >= 4
