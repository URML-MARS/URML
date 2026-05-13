"""Pass 5 — compliance policy enforcement (RFC-0004).

Evaluates a parsed :class:`urml_validator.schemas.policy.Policy` against
a manifest's :attr:`urml_validator.schemas.manifest.CapabilityManifest.provenance`
block. Emits structured :class:`urml_validator.errors.ValidationError`
instances with rich ``detail`` payloads the LLM bridge can consume.

Semantics (normative per RFC-0004):

- Rules evaluate in document order; first-match-wins per (component, dimension).
- ``require`` and ``deny`` are mutually exclusive per rule (enforced by the
  policy schema; the engine relies on the invariant).
- A manifest with no ``provenance`` block triggers no policy errors. This
  is intentional: policy enforcement is opt-in at the manifest level.
- A rule with no matching components is a no-op (vacuously satisfied).
"""

from __future__ import annotations

from typing import Any

from urml_validator.errors import ErrorCode, ValidationError
from urml_validator.schemas.manifest import CapabilityManifest, Provenance, ProvenanceComponent
from urml_validator.schemas.policy import OnViolation, Policy, PolicyRule, RulePredicate, RuleSelector

# =============================================================================
# Public entry point
# =============================================================================


def evaluate_policy(
    manifest: CapabilityManifest,
    policy: Policy,
) -> list[ValidationError]:
    """Evaluate a policy against a manifest's provenance.

    Returns an empty list if the manifest has no ``provenance`` block
    (policy enforcement is opt-in per manifest).

    Args:
        manifest: The validated capability manifest.
        policy:   The validated policy.

    Returns:
        A list of ValidationError instances — one per rule violation.
        Empty if every rule is satisfied (or no provenance is declared).
    """
    if manifest.provenance is None:
        return []

    out: list[ValidationError] = []
    for rule in policy.rules:
        out.extend(_evaluate_rule(rule, manifest.provenance, policy.policy_id))
    return out


# =============================================================================
# Per-rule evaluation
# =============================================================================


def _evaluate_rule(
    rule: PolicyRule,
    provenance: Provenance,
    policy_id: str,
) -> list[ValidationError]:
    """Evaluate one rule. Returns one ValidationError per matched violation."""
    selector = rule.applies_to

    if selector.scope == "manifest":
        return _evaluate_manifest_scope_rule(rule, provenance, policy_id)

    # Component-scoped rule: pick the components this rule applies to.
    targets = _select_components(selector, provenance.components)
    out: list[ValidationError] = []
    for component in targets:
        out.extend(_evaluate_component_rule(rule, component, provenance, policy_id))
    return out


def _select_components(
    selector: RuleSelector, components: list[ProvenanceComponent]
) -> list[ProvenanceComponent]:
    """Return the components a rule applies to per its selector."""
    if selector.component_id is not None:
        return [c for c in components if c.id == selector.component_id]
    if selector.component_role is None:
        return []
    if selector.component_role == "any":
        return list(components)
    return [c for c in components if c.role == selector.component_role]


# =============================================================================
# Component-level rule evaluation
# =============================================================================


def _evaluate_component_rule(
    rule: PolicyRule,
    component: ProvenanceComponent,
    provenance: Provenance,
    policy_id: str,
) -> list[ValidationError]:
    """Evaluate a component-scoped rule against one component.

    First-match-wins per (component, dimension): we check dimensions in
    document order and emit at most one error per (component, rule).
    """
    out: list[ValidationError] = []
    predicate = rule.require or rule.deny
    is_require = rule.require is not None
    if predicate is None:
        return out  # schema enforces require XOR deny; defensive.

    # Iterate predicate fields in declaration order to keep semantics
    # predictable. For each non-None field, check the predicate.
    violations = _check_component_predicate(component, predicate, is_require=is_require)
    if not violations:
        return out

    # Emit one error for the first violation (first-match-wins per component).
    field, offending_value, expected = violations[0]
    detail = _build_component_detail(
        rule=rule,
        component=component,
        provenance=provenance,
        policy_id=policy_id,
        offending_field=field,
        offending_value=offending_value,
        expected=expected,
        is_require=is_require,
    )
    out.append(
        ValidationError(
            code=_resolve_code(rule.on_violation),
            severity=rule.on_violation.severity,
            message=rule.on_violation.message or _default_message(rule, component, field, is_require),
            path=["<manifest>", "provenance", "components", component.id],
            field=field,
            detail=detail,
        )
    )
    return out


def _check_component_predicate(
    component: ProvenanceComponent,
    predicate: RulePredicate,
    *,
    is_require: bool,
) -> list[tuple[str, Any, list[str] | bool]]:
    """Return [(field, offending_value, expected_set_or_flag), ...] for violated dimensions."""
    violations: list[tuple[str, Any, list[str] | bool]] = []

    if predicate.country_of_origin_in is not None:
        actual = component.country_of_origin
        ok = actual in predicate.country_of_origin_in
        if (is_require and not ok) or (not is_require and ok):
            violations.append(("country_of_origin", actual, predicate.country_of_origin_in))

    if predicate.country_of_final_assembly_in is not None:
        actual = component.country_of_final_assembly
        ok = actual in predicate.country_of_final_assembly_in
        if (is_require and not ok) or (not is_require and ok):
            violations.append(
                ("country_of_final_assembly", actual, predicate.country_of_final_assembly_in)
            )

    if predicate.vendor_in is not None:
        actual_vendor = component.vendor
        ok = actual_vendor in predicate.vendor_in
        if (is_require and not ok) or (not is_require and ok):
            violations.append(("vendor", actual_vendor, predicate.vendor_in))

    if predicate.hbom_ref_present is not None:
        actual_present = component.hbom_ref is not None
        if is_require:
            # require: hbom_ref_present must match the declared flag.
            if actual_present != predicate.hbom_ref_present:
                violations.append(("hbom_ref", actual_present, predicate.hbom_ref_present))
        else:
            # deny: violation iff hbom_ref_present matches the declared flag.
            if actual_present == predicate.hbom_ref_present:
                violations.append(("hbom_ref", actual_present, predicate.hbom_ref_present))

    return violations


# =============================================================================
# Manifest-scope rule evaluation
# =============================================================================


def _evaluate_manifest_scope_rule(
    rule: PolicyRule,
    provenance: Provenance,
    policy_id: str,
) -> list[ValidationError]:
    """Evaluate a `scope: manifest` rule. Only `manifest_attestation_in` is meaningful."""
    predicate = rule.require or rule.deny
    is_require = rule.require is not None
    if predicate is None or predicate.manifest_attestation_in is None:
        return []

    actual = provenance.manifest_attestation
    ok = actual in predicate.manifest_attestation_in
    violated = (is_require and not ok) or (not is_require and ok)
    if not violated:
        return []

    detail = {
        "rule_id": rule.id,
        "policy_id": policy_id,
        "offending_field": "manifest_attestation",
        "offending_value": actual,
        ("allowed_values" if is_require else "denied_values"): list(predicate.manifest_attestation_in),
        "attestation_level": actual,
        "remediation_hint": "request_exception",
    }
    return [
        ValidationError(
            code=_resolve_code(rule.on_violation),
            severity=rule.on_violation.severity,
            message=rule.on_violation.message or (
                f"manifest_attestation {actual!r} not in "
                f"{'allow-list' if is_require else 'deny-list'} "
                f"{predicate.manifest_attestation_in!r}."
            ),
            path=["<manifest>", "provenance", "manifest_attestation"],
            field="manifest_attestation",
            detail=detail,
        )
    ]


# =============================================================================
# Detail and message construction
# =============================================================================


def _build_component_detail(
    *,
    rule: PolicyRule,
    component: ProvenanceComponent,
    provenance: Provenance,
    policy_id: str,
    offending_field: str,
    offending_value: Any,
    expected: list[str] | bool,
    is_require: bool,
) -> dict[str, Any]:
    """Build the structured `detail` payload for a component-rule violation."""
    detail: dict[str, Any] = {
        "rule_id": rule.id,
        "policy_id": policy_id,
        "component_id": component.id,
        "component_role": component.role,
        "offending_field": offending_field,
        "offending_value": offending_value,
        "attestation_level": provenance.manifest_attestation,
        "remediation_hint": _remediation_hint_for_field(offending_field),
    }
    if isinstance(expected, list):
        if is_require:
            detail["allowed_values"] = list(expected)
            detail["denied_values"] = None
        else:
            detail["allowed_values"] = None
            detail["denied_values"] = list(expected)
    else:
        # bool — hbom presence flag
        detail["expected_flag"] = expected
    return detail


def _remediation_hint_for_field(field: str) -> str:
    """Map an offending field to a remediation hint the LLM bridge consumes."""
    if field in ("country_of_origin", "country_of_final_assembly", "vendor"):
        return "swap_component"
    if field == "hbom_ref":
        return "request_exception"
    return "change_deployment_target"


def _default_message(
    rule: PolicyRule,
    component: ProvenanceComponent,
    field: str,
    is_require: bool,
) -> str:
    """Compose a fallback message when on_violation.message is omitted."""
    verb = "must be in the allow-list" if is_require else "is in the deny-list"
    return (
        f"Policy rule {rule.id!r}: component {component.id!r} field {field!r} {verb}."
    )


# =============================================================================
# Code resolution
# =============================================================================


def _resolve_code(on_violation: OnViolation) -> ErrorCode | str:
    """Coerce the policy-author code to an ErrorCode enum value when possible.

    Authors may emit any string in the ``policy.*`` namespace. When the
    string matches a defined ErrorCode, return the enum; otherwise return
    the raw string. Both are accepted by ValidationError.code.
    """
    try:
        return ErrorCode(on_violation.code)
    except ValueError:
        return on_violation.code
