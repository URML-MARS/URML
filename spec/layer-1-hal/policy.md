<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# Compliance Policy — Normative Specification

**Status:** v0.1 — implemented in the reference validator.
**Authority:** This document is normative. The decision history is in [RFC-0004](../../docs/rfcs/0004-compliance-policy.md); the strategic rationale is in [RFC-0003](../../docs/rfcs/0003-us-alignment.md).

---

## Purpose

A **compliance policy** is a YAML document that the URML validator consumes alongside a capability manifest. It declares allow/deny rules over the manifest's `provenance:` block (see [README.md §Provenance and Compliance](README.md)). The validator's Pass 5 evaluates the policy and emits `policy.*` errors for any violation.

The policy file is to the validator what the safety envelope is: a pluggable, deployment-time YAML input that narrows what the manifest already permits. The manifest *declares*; the policy *decides*.

## Disclaimer

**A policy file passing the validator is not a legal compliance determination.** This specification defines a mechanism. Whether a particular policy file *correctly encodes* a regulatory regime — and whether a deployment that passes its rules is *actually compliant* under the law — is a matter for counsel, not for URML. URML records what the deployer declares; URML does not certify.

The default policy bundled with the URML validator (`us_federal_default.yaml`) mirrors enacted US federal procurement rules at the time of shipping. Deployers must verify the bundled rules against current statute before relying on them, and must consult counsel for binding determinations.

## File format

The policy file is YAML at the top level. The schema is:

```yaml
policy_version: "0.1"          # required, literal "0.1"
policy_id: <identifier>        # required, free-form string

description: |                 # optional
  Free-form prose.

issued_by: <string>            # optional, informational
issued_at: <ISO-8601 date>     # optional, informational; quote strings to avoid YAML date-parsing

rules:                         # required, may be empty
  - id: <free-form>
    applies_to:
      # Exactly one of the following:
      component_role: critical | non_critical | informational | any
      component_id: <component-id>
      scope: manifest

    # Exactly one of `require` or `deny` per rule:
    require:
      <predicate>
    deny:
      <predicate>

    on_violation:
      code: policy.<author-chosen-code>   # required; must start with "policy."
      message: <string>                    # optional; default composed from rule
      severity: error | warning            # optional; default "error"
```

The DSL is intentionally minimal. The following constraints are **normative**:

1. **No expression language.** Rules are flat predicates over a tiny selector set and finite set-membership assertions. The validator evaluates each rule in O(1) per component.
2. **`require` and `deny` are mutually exclusive per rule.** The parser rejects rules that set both or neither.
3. **First-match-wins per (component, dimension).** Rules evaluate in document order. The first dimension within a rule that finds a violation emits the error; later dimensions within the same rule do not fire for the same component.
4. **Selector grammar is fixed.** v0.1 supports exactly three selector forms: `component_role`, `component_id`, `scope: manifest`. The parser rejects any other selector field.
5. **`policy.*` is a reserved namespace.** `on_violation.code` must begin with `policy.` and is otherwise author-chosen. Built-in codes (e.g., `policy.country_denied`) match enum values in `urml_validator.ErrorCode`; author-defined codes round-trip through `ValidationError.code` as strings.

## Selectors

A selector determines *which* manifest entities a rule inspects.

### `component_role`

Selects components by their declared `role`. The allowed values are:

| Value | Matches |
|---|---|
| `critical` | Components with `role: critical`. |
| `non_critical` | Components with `role: non_critical`. |
| `informational` | Components with `role: informational`. |
| `any` | All components, regardless of role. |

Most regulatory rules turn on `role: critical`. Profile-specific role schemas (e.g., distinguishing a drone's flight controller from a home robot's controller) are deferred to a future RFC; v0.1 keeps the role enumeration flat.

### `component_id`

Selects exactly one component by its declared `id`. Useful for component-specific exceptions or audits.

### `scope: manifest`

Applies the rule to the manifest as a whole, not to any individual component. Only the `manifest_attestation_in` predicate is meaningful at this scope; other predicates are accepted but have no effect.

## Predicates

A predicate is the set-membership assertion the rule makes about its selected target. Exactly one of `require` or `deny` is set per rule. The same predicate fields appear under both keys; the semantics invert.

### Predicate fields

| Field | Type | Meaning |
|---|---|---|
| `country_of_origin_in` | list of strings | Under `require`: component's `country_of_origin` must be in the list. Under `deny`: must *not* be in the list. ISO 3166-1 alpha-2 codes plus the literal `unknown`. |
| `country_of_final_assembly_in` | list of strings | Same shape, against `country_of_final_assembly`. |
| `vendor_in` | list of strings | Same shape, against `vendor`. Free-string match (case-sensitive). |
| `hbom_ref_present` | boolean | Under `require`: the component's `hbom_ref` field must equal the boolean. Under `deny`: must *not* equal the boolean. |
| `manifest_attestation_in` | list of enums | Only meaningful at `scope: manifest`. Asserts the manifest's `manifest_attestation` field is (or is not) in the list. |

Empty lists are allowed and are intentional no-ops for that dimension.

### HBOM-content predicates (RFC-0005)

The fields above gate on the manifest's *declared* provenance facts. A board can declare `country_of_origin: US` and still carry a covered part inside its Hardware Bill of Materials. The HBOM-content predicates read the parsed CycloneDX document a component's `hbom_ref` points at, and walk its `pedigree` (ancestors, descendants, variants) so a covered part is caught at any depth (the NDAA §889 vendor-of-vendor case).

| Field | Type | Meaning |
|---|---|---|
| `hbom_no_components_from_country` | list of strings | Reject if any component in the target's HBOM, at any pedigree depth, declares a supplier or manufacturer country in this list. ISO 3166-1 alpha-2. |
| `hbom_no_components_from_vendor` | list of strings | Reject if any component in the target's HBOM, at any pedigree depth, declares a supplier or manufacturer name in this list. |

These predicates are **deny-only**: the field name already carries the polarity, so a match in the parsed HBOM is the violation. They are rejected under `require` at parse time. A single rule's predicate asserts over manifest-declared facts *or* over parsed HBOM content, never both; mixing the two is rejected at parse time (split into two rules) so the two evaluation paths stay separable and auditable.

The HBOM file is resolved relative to the manifest's own directory (the `urml` CLI passes it automatically); a remote `uri` is reported `policy.hbom_uri_unreachable` (a warning, since the validator does not fetch) and a hash mismatch or malformed document is `policy.hbom_parse_failed` (an error, so a broken HBOM cannot silently bypass the check). Parsing is dependency-free: the validator reads the CycloneDX JSON subset the predicates need with the standard library, so HBOM-content rules run on any OS and in air-gapped deployments with no extra wheels. Per-program enforcement of "a program may only use primitives the declared HBOM supports" is out of scope; these predicates are deployment-static provenance gates.

## Evaluation semantics

For each rule in document order:

1. Compute the **target set** from `applies_to`. For `component_role` and `component_id`, this is a subset of `manifest.provenance.components`. For `scope: manifest`, this is the single-element set `{manifest.provenance}`.
2. For each target in the set, evaluate each predicate field in declaration order.
3. The **first** predicate field that finds a violation emits a `ValidationError` with `code = on_violation.code`, `severity = on_violation.severity`, and a structured `detail` payload (see below). No further fields within the same rule fire for the same target.
4. Errors with `severity: error` cause the validator to reject the program (`ValidationResult.accepted = False`). Warnings do not.

**A manifest without a `provenance:` block triggers no Pass 5 errors**, regardless of how many rules the policy declares. Policy enforcement is opt-in at the manifest level.

## Error payload — `ValidationError.detail`

Every policy-rule violation populates `ValidationError.detail` with the following structure:

```python
{
  "rule_id": "<the rule's id>",
  "policy_id": "<the policy's id>",
  "component_id": "<id of the offending component, or absent for scope:manifest>",
  "component_role": "<role of the offending component, or absent for scope:manifest>",
  "offending_field": "<country_of_origin | country_of_final_assembly | vendor | hbom_ref | manifest_attestation>",
  "offending_value": "<the declared value that violated>",
  "allowed_values": [...],   # populated for `require` rules
  "denied_values": [...],    # populated for `deny` rules
  "attestation_level": "<manifest_attestation at validation time>",
  "remediation_hint": "swap_component" | "request_exception" | "change_deployment_target",
}
```

The `remediation_hint` field lets the LLM bridge exit revision loops fast: the LLM cannot fix hardware by editing a URML program, so the bridge raises `BridgePolicyViolation` and surfaces the error to the user.

## The default policy

The reference validator ships with a default policy at `urml_validator/policies/us_federal_default.yaml`. It is loaded automatically when no `--policy` flag is passed. Per [RFC-0003](../../docs/rfcs/0003-us-alignment.md), this default mirrors US federal procurement rules: NDAA Section 889 / FY26, the FCC Covered List, EO 14307, and the American Security Robotics Act (once enacted).

Per [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) item 7, the default policy file remains Apache 2.0 forever and may not move behind a paywall. *Audited* or *certified* policy files carrying third-party legal attestation are a separate commercial surface.

Deployers outside the US must override the default with their own policy file via `urml validate --policy <file.yaml>`. The default may also be disabled entirely with `--no-policy` (or `policy=None` via the Python API).

## Conformance

A URML-compatible validator must:

1. Parse policy files conforming to the schema above, rejecting any file that violates the structural constraints in *File format*.
2. Implement the selector and predicate semantics in *Evaluation semantics* exactly.
3. Emit `ValidationError` instances with the `detail` payload structure in *Error payload* for every fired rule.
4. Skip Pass 5 entirely when the manifest does not declare a `provenance:` block.
5. Skip Pass 5 entirely when the caller passes `policy=None` (or the CLI `--no-policy`).
6. Load the bundled US-federal default policy when no explicit policy is supplied.

The v0.1 reference test fixtures under `reference/validator/tests/fixtures/policies/` and the conformance fixtures `conformance/fixtures/home/07_*` through `09_*` exercise each conformance point.

## Future work

The following are explicitly **not** in v0.1 and are scheduled for follow-up RFCs:

- **Structured HBOM parsing.** v0.1 records the HBOM URI + integrity hash but does not parse SBOM/HBOM content. A future RFC may add CycloneDX/SPDX-aware predicates (e.g., "no critical component contains a chip from <list>").
- **Multi-policy composition.** v0.1 accepts a single `--policy` per validation. A future RFC may add `--policy a.yaml --policy b.yaml` with conjunction semantics for deployers subject to multiple jurisdictions (e.g., NDAA + EU AI Act).
- **Profile-specific role enumerations.** v0.1 keeps `role: critical | non_critical | informational` flat. Domain profiles may need finer-grained roles (`role: flight_controller` for drone-profile manifests).
- **Registered vendor identifiers.** v0.1 treats `vendor` as a free string. A future RFC may add `vendor_registered_id_in: [<DUNS>, <ROR>, ...]` for vendors registered with a recognized identifier authority.
- **Certified-policy attestation chain.** A future RFC may specify how an audited policy file declares its audit chain so that downstream consumers can verify certification without fetching external documents.

## Related documents

- [README.md](README.md) — Layer-1 hardware abstraction overview and the `provenance:` block field reference.
- [RFC-0003](../../docs/rfcs/0003-us-alignment.md) — strategic alignment to US federal regulation.
- [RFC-0004](../../docs/rfcs/0004-compliance-policy.md) — technical specification of the policy mechanism.
- [CORE_COMMITMENT.md](../../CORE_COMMITMENT.md) §The Commitment item 7 — the default policy file as a public good.
