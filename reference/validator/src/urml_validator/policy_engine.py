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

from pathlib import Path
from typing import Any

from urml_validator.errors import ErrorCode, ValidationError
from urml_validator.hbom import HBOMComponent, HBOMError, resolve_and_parse
from urml_validator.schemas.common import EVIDENCE_SOURCE_RANK, Evidence
from urml_validator.schemas.manifest import CapabilityManifest, Provenance, ProvenanceComponent
from urml_validator.schemas.policy import (
    EvidenceRule,
    OnViolation,
    Policy,
    PolicyRule,
    RulePredicate,
    RuleSelector,
)

# =============================================================================
# Public entry point
# =============================================================================


def evaluate_policy(
    manifest: CapabilityManifest,
    policy: Policy,
    *,
    manifest_base_dir: Path | None = None,
) -> list[ValidationError]:
    """Evaluate a policy against a manifest's provenance.

    Returns an empty list if the manifest has no ``provenance`` block
    (policy enforcement is opt-in per manifest).

    Args:
        manifest: The validated capability manifest.
        policy:   The validated policy.
        manifest_base_dir: Directory a component's relative ``hbom_ref.uri``
            is resolved against (RFC-0005), normally the manifest file's own
            directory. ``None`` disables local-HBOM resolution: HBOM-content
            rules then degrade to a ``policy.hbom_uri_unreachable`` warning
            rather than reading a file. Manifest-declared-fact rules
            (RFC-0004) never need it.

    Returns:
        A list of ValidationError instances — one per rule violation.
        Empty if every rule is satisfied. Provenance rules (RFC-0004/0005) are a
        no-op when the manifest declares no ``provenance``; evidence rules
        (RFC-0631) are evaluated independently of provenance.
    """
    out: list[ValidationError] = []

    # Provenance rules (RFC-0004; HBOM-content sub-pass RFC-0005). Opt-in at the
    # manifest level: a manifest with no provenance triggers none of them.
    if manifest.provenance is not None:
        hbom_cache: dict[tuple[str, str | None], list[HBOMComponent] | HBOMError] = {}
        for rule in policy.rules:
            out.extend(
                _evaluate_rule(
                    rule, manifest.provenance, policy.policy_id, manifest_base_dir, hbom_cache
                )
            )

    # Evidence rules (RFC-0631). Independent of provenance: they gate the
    # traceability of capability claims, not hardware origin.
    for evidence_rule in policy.evidence_rules:
        out.extend(_evaluate_evidence_rule(evidence_rule, manifest, policy.policy_id))

    return out


# =============================================================================
# Per-rule evaluation
# =============================================================================


def _evaluate_rule(
    rule: PolicyRule,
    provenance: Provenance,
    policy_id: str,
    base_dir: Path | None,
    hbom_cache: dict,
) -> list[ValidationError]:
    """Evaluate one rule. Returns one ValidationError per matched violation."""
    selector = rule.applies_to

    if selector.scope == "manifest":
        return _evaluate_manifest_scope_rule(rule, provenance, policy_id)

    # Component-scoped rule: pick the components this rule applies to.
    targets = _select_components(selector, provenance.components)
    predicate = rule.require or rule.deny
    is_hbom = predicate is not None and predicate.uses_hbom_content()

    out: list[ValidationError] = []
    for component in targets:
        if is_hbom:
            out.extend(
                _evaluate_hbom_component_rule(
                    rule, component, provenance, policy_id, base_dir, hbom_cache
                )
            )
        else:
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
# HBOM-content rule evaluation (RFC-0005)
# =============================================================================


def _evaluate_hbom_component_rule(
    rule: PolicyRule,
    component: ProvenanceComponent,
    provenance: Provenance,
    policy_id: str,
    base_dir: Path | None,
    hbom_cache: dict,
) -> list[ValidationError]:
    """Evaluate a deny rule whose predicate reaches into the component's HBOM.

    HBOM-content rules apply only to a component that declares an
    ``hbom_ref`` (a component with no HBOM is not subject to content checks;
    use ``hbom_ref_present`` to require one). Resolution failures surface as
    their own ``policy.hbom_*`` diagnostics — a hash mismatch or malformed
    document is an error so it cannot silently bypass the check; a remote or
    missing uri is a warning, since the validator does not fetch.
    """
    if component.hbom_ref is None:
        return []

    predicate = rule.deny  # schema guarantees HBOM predicates are deny-only.
    assert predicate is not None

    components = _resolve_hbom(component, base_dir, hbom_cache)
    if isinstance(components, HBOMError):
        return [_hbom_resolution_error(rule, component, policy_id, components)]

    match = _first_hbom_match(components, predicate)
    if match is None:
        return []

    offending_field, hit, denied_values = match
    detail: dict[str, Any] = {
        "rule_id": rule.id,
        "policy_id": policy_id,
        "component_id": component.id,
        "component_role": component.role,
        "offending_field": offending_field,
        "hbom_component": hit.name,
        "hbom_component_vendor": hit.vendor,
        "hbom_component_country": hit.country,
        "pedigree_depth": hit.pedigree_depth,
        "denied_values": list(denied_values),
        "attestation_level": provenance.manifest_attestation,
        "remediation_hint": "swap_component",
    }
    code = _resolve_code(rule.on_violation)
    if rule.on_violation.message is None and code == rule.on_violation.code:
        # Author chose a default; compose a precise message naming the part.
        where = "" if hit.pedigree_depth == 0 else f" (pedigree depth {hit.pedigree_depth})"
        message = (
            f"Policy rule {rule.id!r}: component {component.id!r} HBOM contains part "
            f"{hit.name!r}{where} with {offending_field} "
            f"{(hit.country if offending_field == 'country' else hit.vendor)!r} "
            f"in the deny-list {list(denied_values)!r}."
        )
    else:
        message = rule.on_violation.message or _default_message(rule, component, offending_field, False)
    return [
        ValidationError(
            code=code,
            severity=rule.on_violation.severity,
            message=message,
            path=["<manifest>", "provenance", "components", component.id, "hbom_ref"],
            field=offending_field,
            detail=detail,
        )
    ]


def _resolve_hbom(
    component: ProvenanceComponent,
    base_dir: Path | None,
    hbom_cache: dict,
) -> list[HBOMComponent] | HBOMError:
    """Resolve + parse a component's HBOM, memoised per (uri, sha256)."""
    ref = component.hbom_ref
    key = (ref.uri, ref.sha256)
    if key in hbom_cache:
        return hbom_cache[key]
    try:
        result: list[HBOMComponent] | HBOMError = resolve_and_parse(ref, base_dir)
    except HBOMError as exc:
        result = exc
    hbom_cache[key] = result
    return result


def _first_hbom_match(
    components: list[HBOMComponent],
    predicate: RulePredicate,
) -> tuple[str, HBOMComponent, list[str]] | None:
    """Return the first (field, component, denied_values) a deny-list catches.

    Country is checked before vendor (declaration order), and components in
    pedigree pre-order, so the result is deterministic.
    """
    deny_countries = predicate.hbom_no_components_from_country
    deny_vendors = predicate.hbom_no_components_from_vendor
    for comp in components:
        if deny_countries and comp.country in deny_countries:
            return ("country", comp, deny_countries)
        if deny_vendors and comp.vendor in deny_vendors:
            return ("vendor", comp, deny_vendors)
    return None


def _hbom_resolution_error(
    rule: PolicyRule,
    component: ProvenanceComponent,
    policy_id: str,
    err: HBOMError,
) -> ValidationError:
    """Turn an HBOMError into a ValidationError with the right severity.

    Parse failures (hash mismatch, malformed, unsupported format) are errors:
    a broken HBOM must not silently pass a content rule. Unreachable uris
    (remote, or absent local file) are warnings: the validator does not fetch,
    so it reports "could not check" rather than failing the deployment.
    """
    severity = "error" if err.code == ErrorCode.POLICY_HBOM_PARSE_FAILED else "warning"
    detail = {
        "rule_id": rule.id,
        "policy_id": policy_id,
        "component_id": component.id,
        "component_role": component.role,
        **err.detail,
    }
    return ValidationError(
        code=err.code,
        severity=severity,
        message=(
            f"Policy rule {rule.id!r}: component {component.id!r} HBOM could not be "
            f"checked ({err.detail.get('reason', err.code.value)})."
        ),
        path=["<manifest>", "provenance", "components", component.id, "hbom_ref"],
        field="hbom_ref",
        detail=detail,
    )


# =============================================================================
# Evidence-rule evaluation (RFC-0631)
# =============================================================================


def _collect_evidenced_capabilities(
    manifest: CapabilityManifest, applies_to: str
) -> list[tuple[str, str, Evidence | None, list[str]]]:
    """Return (kind, label, evidence, path) for each capability the rule covers.

    `kind` is the capability class (gripper / camera / sensor / mobility /
    whole_body), `label` names the instance, `evidence` is its tag (or None when
    absent), and `path` locates it in the manifest for the error payload. A
    single-instance block (mobility, whole_body) is skipped when not declared.
    """
    out: list[tuple[str, str, Evidence | None, list[str]]] = []

    want = {"gripper", "camera", "sensor", "mobility", "whole_body"} if applies_to == "any" else {applies_to}

    if "gripper" in want and manifest.manipulation is not None:
        for g in manifest.manipulation.grippers:
            out.append(("gripper", g.name, g.evidence, ["<manifest>", "manipulation", "grippers", g.name]))
    if "camera" in want and manifest.perception is not None:
        for c in manifest.perception.cameras:
            out.append(("camera", c.name, c.evidence, ["<manifest>", "perception", "cameras", c.name]))
    if "sensor" in want and manifest.perception is not None:
        for s in manifest.perception.sensors:
            out.append(("sensor", s.name, s.evidence, ["<manifest>", "perception", "sensors", s.name]))
    if "mobility" in want and manifest.mobility is not None:
        out.append(("mobility", "mobility", manifest.mobility.evidence, ["<manifest>", "mobility"]))
    if "whole_body" in want and manifest.whole_body is not None:
        out.append(("whole_body", "whole_body", manifest.whole_body.evidence, ["<manifest>", "whole_body"]))

    return out


def _evaluate_evidence_rule(
    rule: EvidenceRule,
    manifest: CapabilityManifest,
    policy_id: str,
) -> list[ValidationError]:
    """Evaluate one evidence rule (RFC-0631).

    Emits one error per covered capability whose evidence source is below
    `min_source` (an absent `evidence` tag ranks below the weakest source, so it
    always violates a rule that requires any). A rule covering a capability the
    manifest does not declare is vacuously satisfied.
    """
    required = EVIDENCE_SOURCE_RANK[rule.min_source]
    out: list[ValidationError] = []
    for kind, label, evidence, path in _collect_evidenced_capabilities(manifest, rule.applies_to):
        actual_source = evidence.source if evidence is not None else None
        actual_rank = EVIDENCE_SOURCE_RANK[actual_source] if actual_source is not None else -1
        if actual_rank >= required:
            continue
        detail = {
            "rule_id": rule.id,
            "policy_id": policy_id,
            "capability_kind": kind,
            "capability_label": label,
            "required_min_source": rule.min_source,
            "actual_source": actual_source,
            "remediation_hint": "add_evidence",
        }
        had = f"source {actual_source!r}" if actual_source is not None else "no evidence tag"
        message = rule.on_violation.message or (
            f"Evidence rule {rule.id!r}: {kind} {label!r} has {had}, "
            f"below the required minimum {rule.min_source!r}."
        )
        out.append(
            ValidationError(
                code=_resolve_code(rule.on_violation),
                severity=rule.on_violation.severity,
                message=message,
                path=path,
                field="evidence",
                detail=detail,
            )
        )
    return out


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
