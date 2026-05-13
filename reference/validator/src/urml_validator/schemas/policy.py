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

from typing import Literal

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
    """

    model_config = ConfigDict(extra="forbid")

    country_of_origin_in: list[str] | None = None
    country_of_final_assembly_in: list[str] | None = None
    vendor_in: list[str] | None = None
    hbom_ref_present: bool | None = None
    manifest_attestation_in: list[
        Literal["self_declared", "third_party_audited", "cryptographically_signed"]
    ] | None = None


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
