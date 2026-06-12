"""Compliance policy schema (RFC-0004).

A policy file declares allow/deny rules over a manifest's `provenance` block.
The validator's Pass 5 evaluates these rules against a target manifest and
emits structured `policy.*` errors when a rule fires.

DSL design constraints (normative per RFC-0004):

1. **No expressions, conditionals, or computation.** Every rule is a flat
   predicate over a selector and a finite set-membership assertion.
2. **`require` and `deny` are mutually exclusive per rule.** Pydantic
   validates this at parse time.
3. **Rules evaluate in document order; first-match-wins per (component,
   dimension).** Reorderable rule lists are how policies get debugged.
4. **Selectors are tiny:** `component_role`, `component_id`, or
   `scope: manifest`. Extending is non-breaking.
5. **Rule IDs and `on_violation.code` are author-chosen identifiers.**
   The validator emits the author's `code` verbatim. The `policy.*`
   namespace is reserved.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuleSelector(BaseModel):
    """Which components (or the manifest as a whole) a rule applies to.

    Exactly one of `component_role`, `component_id`, or `scope` must be set.
    """

    model_config = ConfigDict(extra="forbid")

    component_role: Literal["critical", "non_critical", "informational", "any"] | None = None
    component_id: str | None = None
    scope: Literal["manifest"] | None = None

    @model_validator(mode="after")
    def _exactly_one_selector(self) -> "RuleSelector":
        set_fields = sum(
            1
            for v in (self.component_role, self.component_id, self.scope)
            if v is not None
        )
        if set_fields != 1:
            raise ValueError(
                "RuleSelector must set exactly one of "
                "`component_role`, `component_id`, or `scope`."
            )
        return self


class RulePredicate(BaseModel):
    """The set-membership assertions a rule makes about its selected target.

    For `applies_to.scope: manifest` rules, only `manifest_attestation_in`
    is meaningful (the other fields apply to components).

    For component-level rules, the *component-level* fields apply.

    Empty lists are allowed (a rule with `country_of_origin_in: []` is a
    no-op for that dimension — useful as a deliberate placeholder).

    A predicate may assert over *manifest-declared* facts (the original
    five fields) or over *parsed HBOM content* (the ``hbom_*`` fields added
    by RFC-0005), but not both in one rule. Mixing the two is rejected at
    parse time so the two evaluation paths stay separable and auditable;
    split the intent into two rules. The HBOM-content predicates reach into
    the CycloneDX document a component's ``hbom_ref`` points at and walk its
    pedigree, so a covered part hidden behind an integrator's own part number
    (NDAA §889 vendor-of-vendor) is caught at any depth.
    """

    model_config = ConfigDict(extra="forbid")

    # --- manifest-declared facts (RFC-0004) ---
    country_of_origin_in: list[str] | None = None
    country_of_final_assembly_in: list[str] | None = None
    vendor_in: list[str] | None = None
    hbom_ref_present: bool | None = None
    manifest_attestation_in: list[
        Literal["self_declared", "third_party_audited", "cryptographically_signed"]
    ] | None = None

    # --- parsed HBOM content (RFC-0005) ---
    hbom_no_components_from_country: list[str] | None = Field(
        None,
        description=(
            "Reject if any component in the target's HBOM (at any pedigree depth) "
            "declares a supplier/manufacturer country in this list. ISO 3166-1 alpha-2."
        ),
    )
    hbom_no_components_from_vendor: list[str] | None = Field(
        None,
        description=(
            "Reject if any component in the target's HBOM (at any pedigree depth) "
            "declares a supplier/manufacturer name in this list."
        ),
    )

    # The manifest-declared fields and the parsed-HBOM-content fields are the
    # two predicate families. Keeping them un-mixed per rule is what lets the
    # engine evaluate HBOM rules in a separate, file-touching sub-pass without
    # entangling them with the in-memory manifest checks.
    _MANIFEST_FIELDS: ClassVar[tuple[str, ...]] = (
        "country_of_origin_in",
        "country_of_final_assembly_in",
        "vendor_in",
        "hbom_ref_present",
        "manifest_attestation_in",
    )
    _HBOM_FIELDS: ClassVar[tuple[str, ...]] = (
        "hbom_no_components_from_country",
        "hbom_no_components_from_vendor",
    )

    @model_validator(mode="after")
    def _no_mix_manifest_and_hbom(self) -> "RulePredicate":
        has_manifest = any(getattr(self, f) is not None for f in self._MANIFEST_FIELDS)
        has_hbom = any(getattr(self, f) is not None for f in self._HBOM_FIELDS)
        if has_manifest and has_hbom:
            raise ValueError(
                "A policy rule predicate may assert over manifest-declared facts "
                "or over parsed HBOM content, not both. Split into two rules."
            )
        return self

    def uses_hbom_content(self) -> bool:
        """True if this predicate asserts over parsed HBOM content (RFC-0005)."""
        return any(getattr(self, f) is not None for f in self._HBOM_FIELDS)


class OnViolation(BaseModel):
    """What the validator emits when a rule fires."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        ...,
        description="The error code emitted on violation. Must begin with 'policy.'.",
    )
    message: str | None = Field(
        None,
        description="Human-readable explanation. If omitted, a default is composed from the rule.",
    )
    severity: Literal["error", "warning"] = Field(
        "error",
        description="`error` rejects the program; `warning` flags but accepts.",
    )

    @model_validator(mode="after")
    def _code_in_policy_namespace(self) -> "OnViolation":
        if not self.code.startswith("policy."):
            raise ValueError(f"on_violation.code must start with 'policy.'; got {self.code!r}.")
        return self


class PolicyRule(BaseModel):
    """One rule in a policy file.

    Exactly one of `require` or `deny` must be set.

    HBOM-content predicates (RFC-0005) are deny-only. Their field names
    already carry the polarity (``hbom_no_components_from_country``), and a
    match in the parsed HBOM is the violation, so wrapping them in ``require``
    would be a confusing double negation. They are rejected under ``require``
    at parse time.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Free-form identifier; author-chosen.")
    applies_to: RuleSelector
    require: RulePredicate | None = None
    deny: RulePredicate | None = None
    on_violation: OnViolation

    @model_validator(mode="after")
    def _require_xor_deny(self) -> "PolicyRule":
        if self.require is None and self.deny is None:
            raise ValueError(f"PolicyRule {self.id!r}: must set one of `require` or `deny`.")
        if self.require is not None and self.deny is not None:
            raise ValueError(
                f"PolicyRule {self.id!r}: `require` and `deny` are mutually exclusive."
            )
        if self.require is not None and self.require.uses_hbom_content():
            raise ValueError(
                f"PolicyRule {self.id!r}: HBOM-content predicates "
                f"(hbom_no_components_from_*) are deny-only; place them under `deny`."
            )
        return self


class Policy(BaseModel):
    """A complete policy file.

    `rules` are evaluated in document order; first-match-wins per
    (component, dimension). An empty `rules` list is a no-op policy
    (useful as a permissive baseline).
    """

    model_config = ConfigDict(extra="forbid")

    policy_version: Literal["0.1"] = "0.1"
    policy_id: str
    description: str | None = None
    issued_by: str | None = None
    issued_at: str | None = Field(
        None,
        description="ISO-8601 date the policy was issued. Informational.",
    )
    rules: list[PolicyRule] = Field(default_factory=list)
