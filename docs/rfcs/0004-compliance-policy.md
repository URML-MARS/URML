---
rfc: 0004
title: Compliance Policy Enforcement
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-13
updated: 2026-05-13
supersedes: —
superseded-by: —
---

# RFC-0004: Compliance Policy Enforcement

## Summary

This RFC specifies the technical mechanism that [RFC-0003](0003-us-alignment.md) authorizes: a way for URML capability manifests to declare hardware provenance, and a way for the URML validator to enforce pluggable policy files against that provenance before any program is accepted for execution.

Three artifacts are introduced:

1. **`provenance:` block on `CapabilityManifest`** — an optional Layer-1 schema addition declaring per-component country of origin, vendor, role (critical/non-critical/informational), and an optional Hardware Bill of Materials reference.
2. **Policy file format** — a YAML schema for allow/deny rules over manifest provenance, with a small fixed predicate vocabulary and no expression language (statically decidable; trivially auditable).
3. **Validator Pass 5 + `--policy` CLI flag** — the validator gains a fifth pass that evaluates a policy against the manifest. The validator ships with a default policy `us_federal_default.yaml` mirroring NDAA Section 889 / FY26 procurement rules and is loaded automatically when `--policy` is not specified. `--no-policy` disables Pass 5 entirely.

The architectural pattern is **Compliance Policy is to the validator what Safety Envelope is**: a deployment-time YAML file that narrows what the manifest already permits. The manifest *declares*; the policy *decides*.

## Motivation

[RFC-0003](0003-us-alignment.md) commits URML to alignment with US federal robotics regulation. That commitment is hollow until URML can actually express the rules and reject programs that violate them. RFC-0004 makes the commitment operational.

Three concrete needs:

- **A robot deployer needs to know, at validation time, whether their target robot is acceptable under the active regulatory frame.** Today the four validator passes (argument typing, capability, envelope, binding) check whether the *program* is well-formed for the *robot*. They do not check whether the *robot* is well-formed for the *deployment*. NDAA-compliance is a robot-vs-deployment check; it belongs at validation.
- **An LLM emitting URML programs needs structured feedback when a program is rejected for compliance reasons.** Without this, the bridge's revision loop will keep trying to fix the program when the actual problem is the hardware. Programs cannot fix hardware; the revision loop must exit fast on compliance violations.
- **The standard needs a non-Turing-tarpit policy DSL.** Regulation changes. Hand-coding NDAA rules into validator source means every regulatory update is a code release. A declarative policy file means regulatory updates are configuration changes — auditable, diffable, reviewable by counsel without reading Python.

## Detailed design

### Spec changes

#### Layer 1 (Hardware Abstraction) — `provenance:` block

Added to `CapabilityManifest` as an optional sibling block alongside `mobility`, `manipulation`, `perception`, etc. Affected document: `spec/layer-1-hal/README.md` (will be amended to document the new block).

Minimum v0.1 fields:

```yaml
provenance:
  manifest_attestation: self_declared    # self_declared | third_party_audited | cryptographically_signed
  attestation_uri: null                  # optional URI to a signed attestation document
  components:
    - id: drive_controller
      role: critical                     # critical | non_critical | informational
      vendor: example_vendor             # free-form machine-readable identifier
      country_of_origin: US              # ISO 3166-1 alpha-2; "unknown" allowed
      country_of_final_assembly: US      # often differs from manufacture
      hbom_ref:                          # optional
        format: cyclonedx-1.7            # recommended; free string
        uri: ./hbom/drive_controller.cdx.json
        sha256: 9f...                    # integrity gate when uri is local
```

Field-by-field rationale:

- **`manifest_attestation`** — Three levels in v0.1. Surfaces who asserts the provenance is true. Policies can require a minimum level (default policy warns on `self_declared`, errors on `unknown`).
- **`components[].role`** — Most policies care about *critical* components; the field is the load-bearing selector. The role values are flat in v0.1 (no profile-specific extensions) — policies select finer cuts via `component_id`.
- **`country_of_origin` vs. `country_of_final_assembly`** — Distinct fields because NDAA-style rules often care about both. No synthesis: the manifest author declares both literally.
- **`hbom_ref`** — Optional. URML records the HBOM reference by URI + integrity hash; URML does not parse SBOM content in v0.1. A future RFC may add structured parsing if vendor demand justifies the dependency on `cyclonedx-python-lib` or similar.

#### Policy file format

A new normative artifact at `spec/layer-1-hal/policy.md` (created alongside the existing HAL spec, because policies operate on manifests). The format:

```yaml
policy_version: "0.1"
policy_id: <free-form-identifier>
description: |
  Free-form prose. Must include a "not legal advice" banner for policies
  intended for compliance use.
issued_by: <free-form>
issued_at: <YYYY-MM-DD>

rules:
  - id: <free-form>
    applies_to:
      component_role: critical | non_critical | informational | any
      # OR
      component_id: <specific component id>
      # OR
      scope: manifest

    # Exactly one of `require` or `deny` per rule.
    require:
      country_of_origin_in: [<ISO 3166-1 alpha-2>, ...]
      country_of_final_assembly_in: [<ISO 3166-1 alpha-2>, ...]
      vendor_in: [<free-form>, ...]
      hbom_ref_present: true | false
      manifest_attestation_in: [self_declared, third_party_audited, cryptographically_signed]

    deny:
      # Same shape as `require`; semantics inverted.
      country_of_origin_in: [...]
      country_of_final_assembly_in: [...]
      vendor_in: [...]

    on_violation:
      code: policy.<specific_code>
      message: <free-form, optional>
      severity: error | warning   # default: error
```

**Hard constraints on the DSL (normative; cannot be relaxed without RFC):**

1. **No expressions, conditionals, functions, regular expressions, or computation.** Every rule is a flat predicate over a selector and a finite set-membership assertion. The validator can evaluate a rule in O(1) per component.
2. **`require` and `deny` are mutually exclusive per rule.** Pydantic-level validation rejects rules with both.
3. **Rules are evaluated in document order; first-match-wins per (component, dimension).** Reorderable rule lists are how every policy engine in production gets debugged.
4. **Selectors are tiny:** `component_role`, `component_id`, or `scope: manifest`. v0.1 ships these three. Adding selectors later is non-breaking.
5. **Rule IDs and error codes are arbitrary identifiers chosen by the policy author.** The `policy.*` namespace is reserved. The validator emits the author's `code` verbatim. This is what lets URML ship the mechanism while third parties ship audited rule files with stable codes.

#### Default policy file

`reference/validator/src/urml_validator/policies/us_federal_default.yaml` — shipped with the validator package; loaded automatically when `--policy` is not specified.

```yaml
policy_version: "0.1"
policy_id: urml_us_federal_default
description: |
  Default policy bundled with URML v0.1. Implements provenance restrictions
  derived from NDAA Section 889 (FAR 4.21), the FY26 NDAA expansions, the
  FCC Covered List, Executive Order 14307, and the American Security
  Robotics Act once enacted.

  This file is not legal advice. Deployers must consult counsel for
  binding compliance determinations. Audited and certified policy files
  carrying third-party legal attestation are a separate commercial surface
  (see CORE_COMMITMENT.md).
issued_by: urml_core
issued_at: 2026-05-13

rules:
  - id: critical_country_denylist
    applies_to: { component_role: critical }
    deny:
      country_of_origin_in: [CN, RU, IR, KP]
      country_of_final_assembly_in: [CN, RU, IR, KP]
    on_violation:
      code: policy.country_denied
      message: "Critical component from covered foreign country (NDAA 889 / FY26)."

  - id: covered_vendor_denylist
    applies_to: { component_role: any }
    deny:
      vendor_in: [dji, autel, hesai, unitree]
    on_violation:
      code: policy.vendor_denied
      message: "Vendor named in FCC Covered List or DoD Chinese Military Companies list."

  - id: hbom_required_for_critical
    applies_to: { component_role: critical }
    require:
      hbom_ref_present: true
    on_violation:
      code: policy.hbom_missing
      message: "Critical components must declare a hardware bill-of-materials reference."

  - id: attestation_floor
    applies_to: { scope: manifest }
    require:
      manifest_attestation_in: [third_party_audited, cryptographically_signed]
    on_violation:
      code: policy.attestation_insufficient
      severity: warning
      message: "Self-declared provenance accepted in v0.1 but flagged; v0.2 will promote to error."
```

Citations and source tracking live in the policy file as comments and the `description`. Vendor and country lists are tied to enacted statutes and final FCC/DoD entries per `CLAUDE.md` §What Claude Should Never Do.

### Validator changes

A fifth pass is added to `validate()` in `reference/validator/src/urml_validator/validator.py`. Pass order:

1. Argument type check (unchanged)
2. Capability check (unchanged)
3. Safety-envelope check (unchanged)
4. Variable-binding check (unchanged)
5. **Policy check (new)** — evaluates a policy against the manifest's `provenance` block. Implemented in a new module `reference/validator/src/urml_validator/policy_engine.py` to keep `validator.py` from growing.

The signature of `validate()` gains an optional parameter:

```python
def validate(
    program: dict[str, Any] | URMLProgram,
    manifest: dict[str, Any] | CapabilityManifest,
    envelope: dict[str, Any] | SafetyEnvelope | None = None,
    profiles: list[str] | None = None,
    policy: dict[str, Any] | Policy | None | "DEFAULT" = "DEFAULT",   # new
) -> ValidationResult: ...
```

Behavior of the `policy` parameter:

- **Sentinel `"DEFAULT"` (the default value)** — the validator loads `us_federal_default.yaml` from the package's `policies/` directory. This is the *opinionated default* per `CLAUDE.md` §What Claude Should Do By Default ("Default to opinionated decisions documented in writing").
- **Explicit `None`** — Pass 5 is skipped entirely. Equivalent to the CLI's `--no-policy` flag.
- **Explicit dict or `Policy` instance** — Pass 5 evaluates the given policy.

Errors and warnings from Pass 5 are merged into the existing `ValidationResult.errors` and `ValidationResult.warnings` lists.

#### `ValidationError.detail` field

A new optional `detail: dict | None = None` field is added to `ValidationError`. Policy errors populate it with structured information the LLM bridge consumes:

```python
detail = {
    "rule_id": "critical_country_denylist",
    "policy_id": "urml_us_federal_default",
    "component_id": "lidar",           # omitted when scope == "manifest"
    "component_role": "critical",
    "offending_field": "country_of_origin",
    "offending_value": "CN",
    "denied_values": ["CN", "RU", "IR", "KP"],   # set for deny rules
    "allowed_values": None,                       # set for require rules
    "attestation_level": "self_declared",
    "remediation_hint": "swap_component",  # swap_component | request_exception | change_deployment_target
}
```

Existing producers do not populate `detail`; existing consumers ignore it. Adding the field is fully backward-compatible.

#### Error code namespace

New `ErrorCode` enum values, all in the `policy.*` namespace:

- `POLICY_COUNTRY_DENIED` → `policy.country_denied`
- `POLICY_VENDOR_DENIED` → `policy.vendor_denied`
- `POLICY_HBOM_MISSING` → `policy.hbom_missing`
- `POLICY_ATTESTATION_INSUFFICIENT` → `policy.attestation_insufficient`
- `POLICY_RULE_INVALID` → `policy.rule_invalid` (raised when a policy file fails its own pydantic validation)

Policy authors may emit any string in the `policy.*` namespace as the `code` of an `on_violation` block. The validator surfaces it verbatim; the enum above is for the codes the *default* policy uses. Third-party policies extend the namespace without code changes.

### CLI changes

`reference/validator/src/urml_validator/cli.py` gains two flags on the `validate` subcommand (and on `translate`, which transitively invokes `validate`):

```
urml validate <program> -m <manifest> [-e <envelope>] [-p <profile>] [-P <policy> | --no-policy]
```

- **`--policy / -P <PATH>`** — Path to a policy YAML file. Loaded and passed to `validate(policy=...)`.
- **`--no-policy`** — Skip Pass 5. Equivalent to `validate(policy=None)`.

Behavior when neither flag is given: the validator loads `us_federal_default.yaml` from the package's bundled policies directory.

`urml schema` is extended: `urml schema --name policy` emits the JSON Schema for the policy file format. Implementation: add `"policy"` to `SCHEMA_REGISTRY` in `schema_export.py`.

`urml init` templates (per RFC-0003 follow-up) gain an example `provenance:` block in the scaffolded manifest with `manifest_attestation: self_declared` and a `# TODO: fill in component provenance before deployment` comment.

### LLM bridge changes

`reference/llm-bridge/src/urml_llm_bridge/prompt.py` — `_summarise_manifest()` adds one line summarizing provenance when present:

```
Provenance: 4 components (3 critical), attestation: self_declared
```

The provenance summary is *intentionally minimal*. The LLM is not asked to reason about provenance — provenance is hardware metadata that the LLM cannot fix by rewriting a program. Including it in the prompt at all is defensible only as a hint that compliance is being checked; including the full provenance block would waste tokens.

`reference/llm-bridge/src/urml_llm_bridge/bridge.py` — the revision loop **short-circuits** when only `policy.*` errors are present in a validation result:

```python
if all_errors_are_policy(result):
    raise BridgePolicyViolation(result)
```

If a result contains a mix of `policy.*` and non-`policy.*` errors, the bridge revises only the non-policy errors and surfaces the policy violations as a terminal failure when revision succeeds. The LLM is never asked to "fix" a `policy.*` error.

`BridgePolicyViolation` is a new exception type carrying the full `ValidationResult` for caller inspection.

### Reference runtime changes

**None.** The ROS 2 runtime passes the manifest dict through to the validator and does not parse it locally (see `reference/ros2-runtime/src/urml_ros2_runtime/runtime.py`). Policy enforcement happens at validation time, before any program reaches a runtime. The runtime is unaffected by RFC-0004.

The PX4 runtime, when implemented, will inherit the same property.

### Conformance suite changes

New fixtures under `conformance/fixtures/home/`:

- **`07_policy_country_denied.yaml`** — manifest with `country_of_origin: CN` on a critical component; default policy → rejected with `policy.country_denied`.
- **`08_policy_no_policy_flag.yaml`** — same manifest as fixture 07, validated with `--no-policy` → accepted (proves the escape hatch).
- **`09_policy_vendor_denylist.yaml`** — manifest with `vendor: dji` on a component; default policy → rejected with `policy.vendor_denied`.

Fixture-loader changes in `conformance/src/urml_conformance/fixtures.py`:

- Add `POLICY_REGISTRY` (parallel to existing `MANIFEST_REGISTRY` and `ENVELOPE_REGISTRY`) mapping short names to bundled policy file paths.
- Add optional `policy: str | None = None` field to `FixtureCase`.
- Thread `resolve_policy()` through the harness so fixtures can declare which policy they exercise.

Existing fixtures (01–06) are backfilled with provenance blocks declaring fully US-compliant provenance so they continue to pass under the default policy without modification.

## Backward compatibility

- **`provenance:` is optional on `CapabilityManifest`.** Existing manifests without the block still parse and validate as before.
- **`policy` parameter on `validate()` defaults to the sentinel `"DEFAULT"`.** Callers passing nothing get the bundled US-federal default; callers passing `None` get the prior behavior (no Pass 5).
- **`ValidationError.detail` is optional and defaults to `None`.** Existing producers and consumers are unaffected.
- **Existing conformance fixtures continue to pass** after backfilling them with US-compliant provenance blocks. Programs that target manifests with no provenance at all are evaluated under the default policy's `hbom_required_for_critical` rule, which warns rather than errors when no critical components are declared (an empty `components: []` list satisfies the rule vacuously).

The single behavioral break, for a caller that has been calling `validate()` without an explicit `policy` argument:

- Before this RFC: no Pass 5, no possibility of a `policy.*` error.
- After this RFC: Pass 5 runs against the bundled default policy. A manifest declaring `country_of_origin: CN` on a critical component will now be rejected.

This break is the *point* of RFC-0003. Callers who do not want this behavior pass `policy=None` (or `--no-policy` on the CLI).

The schema versioning approach: `manifest_version` stays at `"0.1"`; adding an optional block to a pre-1.0 schema is permitted within the `0.x` line per existing conventions.

## Drawbacks

1. **The default rule set is opinionated.** Loading `us_federal_default.yaml` by default means URML actively rejects manifests that would have passed before. This is intentional (RFC-0003) but bears repeating: URML now has a regulatory posture, not just a regulatory affordance.

2. **HBOM-as-opaque-hash is a half-measure.** v0.1 verifies a SHA-256 hash but cannot tell you what is *in* the HBOM. Hidden-Chinese-component supply-chain attacks that are downstream of the declared HBOM (e.g., a substituted chip on a board whose CycloneDX still says "fab in Taiwan") are not caught by v0.1. Mitigation: future RFC may add structured CycloneDX parsing if vendor demand justifies the dependency.

3. **Provenance declarations create paper trails.** A robot maker who self-declares `country_of_origin: US` and is later proven wrong has created a discoverable false attestation. The `manifest_attestation` field is designed to surface this; the default policy warns on `self_declared` and is scheduled to promote that to an error in v0.2. URML's role is to *record* the declaration, not to *certify* it.

4. **Compliance theater risk.** A policy file passing the validator is not a legal compliance determination. The default policy carries an inline "not legal advice" banner; the spec text at `spec/layer-1-hal/policy.md` will repeat the disclaimer normatively.

5. **Default policy maintenance burden.** Monthly review of the FCC Covered List, DoD Chinese Military Companies list, NDAA amendments, and pending legislation. A specific owner must be named (currently: the maintainer, in `GOVERNANCE.md` once that document exists).

6. **Token cost of provenance in LLM prompts.** Even the minimal one-line summary costs tokens on every emission. Mitigation: provenance summary is generated only when the manifest has a `provenance:` block; manifests without one pay no token cost.

7. **The `detail` field on `ValidationError` adds public API surface.** Optional and backward-compatible, but a public field nonetheless. Future RFCs that want to use `detail` for non-policy errors will need to coordinate to avoid namespace clashes within the dict.

## Alternatives considered

1. **Embed policy logic in validator source code.** Hardcode the NDAA rules into `validator.py` as Python conditionals. **Rejected:** every regulatory update is a code release; counsel cannot audit Python; third-party rule sets are impossible.

2. **Use an existing policy language (Open Policy Agent / Rego, JSON Schema with `if`/`then`, CEL).** **Rejected** for v0.1: every option introduces a runtime dependency on a policy engine outside URML's stack, brings non-trivial semantics that complicate the static-checkability guarantee, and reads as endorsing one foundation's tooling over others. The flat-predicate DSL chosen is small enough to specify and implement in a few hundred lines of Python; future RFCs may layer OPA/Rego on top if real demand emerges.

3. **Treat policy as just another safety-envelope.** Make `provenance` a field on the envelope rather than the manifest, and let envelope checks enforce it. **Rejected:** provenance is a property of the *robot*, not the deployment. Envelope tightens *deployment-time* limits (don't fly above X meters, here); policy tightens *deployment-time acceptability of robots* (don't use this robot, here). Separate the two so the manifest stays purely declarative.

4. **Validate HBOM content (parse CycloneDX) in v0.1.** **Rejected** because it adds a CycloneDX library dependency, expands the conformance surface significantly, and freezes URML to one SBOM consortium's evolving HBOM semantics. Deferred to a follow-up RFC.

5. **Ship policy mechanism but no default policy file.** This was the alternative considered by RFC-0003 (option 2 in its *Alternatives*). RFC-0003 chose to ship the default; RFC-0004 implements that choice.

6. **Use `applies_to: {tag: <tag>}` selectors instead of `{component_role: critical}`.** A more flexible selector ("apply this rule to any component tagged 'flight_control'") that requires manifests to declare tags. **Rejected** for v0.1 because (a) `role: critical` covers the load-bearing US-regulatory case, (b) tagging adds manifest-author friction with unclear payoff before profile-extensible compliance is needed, (c) the selector grammar is non-breaking to extend later.

7. **Make `country_of_origin` a list to handle multi-source components.** A single chip may be designed in one country, fabricated in another, packaged in a third. **Rejected:** the manifest author should pick the field whose declared value matches the regulatory framing of the deployment (NDAA cares about *manufacture* and *assembly*; the two existing fields cover both). Multi-source provenance is a HBOM concern, not a top-level manifest concern.

## Prior art

- **CycloneDX 1.7** ([OWASP CycloneDX](https://cyclonedx.org/specification/overview/)) — Adds Hardware Bill of Materials (HBOM), pedigree, and provenance fields. URML points at CycloneDX 1.7 as the recommended `hbom_ref.format` value but stays format-agnostic so SPDX, in-toto, or future formats can be used.
- **SPDX 3.0** — Parallel SBOM standard, Linux Foundation governance. Equivalent expressive power for hardware provenance; URML treats it symmetrically with CycloneDX.
- **Blue UAS / Green UAS (DIU)** — A *positive allow-list* of NDAA-compliant drones. URML's default policy is in the same spirit but expressed as a *rule predicate* rather than a *device enumeration*: rather than name which robots URML accepts, URML accepts any robot whose declared provenance satisfies the predicates. A future RFC may add an `allow_robot_ids_in: [...]` selector to express positive lists directly.
- **NIST Software Supply Chain Security Guidance (NIST SP 800-218 + NIST IR 8425)** — The framework anchor for SBOM/HBOM in US federal procurement. URML's HBOM-by-reference design follows NIST's posture: the procurement entity verifies the SBOM exists and is authenticated; URML records the reference and integrity hash.
- **AUTOSAR Adaptive's Identity and Access Management profiles** — Industrial-vehicle precedent for attestation levels (self-asserted vs. signed). URML's `manifest_attestation` enum draws from this.
- **Behavior trees / PDDL precondition formalism** — Predicate-over-state model that URML's policy DSL deliberately echoes; rules are preconditions on the manifest's declared facts.
- **Kubernetes admission controllers and Open Policy Agent** — The "policy file consumed by a gating component before resource admission" pattern. URML's Pass 5 is the same shape, applied to URML programs rather than Kubernetes resources.
- **Section 889 / FAR 4.21** — Statutory anchor; cited inline in `us_federal_default.yaml`.

## Unresolved questions

1. **ISO 3166-1 alpha-2 vs. alpha-3 vs. both.** Recommended: alpha-2 in v0.1 with an explicit `"unknown"` literal. Future RFC may allow alpha-3 if integration with systems that prefer it justifies the parser change.
2. **`vendor` as free string vs. registered identifier (DUNS, ROR, OpenCorporates, NAICS).** Recommended: free string in v0.1. Future RFC may add `vendor_registered_id_in: [...]` once a registry is chosen.
3. **HBOM hash verification responsibility.** v0.1: the validator records the declared hash; verification (fetching the URI and comparing) is the deployer's responsibility. Centralizing verification in the validator requires URI scheme handling and network/filesystem access, which expands the trust surface. Revisit in a follow-up RFC.
4. **Multi-jurisdiction policy composition.** A deployer subject to *both* NDAA and EU AI Act may want to load both policies and take the union of restrictions. v0.1 supports one `--policy` at a time. Future RFC may add `--policy a.yaml --policy b.yaml` with documented composition semantics (most likely: conjunction — all rules from all files must pass).
5. **Severity escalation across policy versions.** The `attestation_floor` rule ships as a warning in v0.1 and is scheduled to promote to error in v0.2. The mechanism for documenting this scheduled change in the policy file itself (vs. in spec text) is open.
6. **The relationship between `policy.*` error codes and certification labels.** A robot whose validation passes under `us_federal_default.yaml` is *not* automatically "URML-Certified — NDAA compliant" (certification is a separate, currently-future program per `CORE_COMMITMENT.md`). The naming convention to prevent this confusion is open.

## Implementation note

This RFC reaches **Accepted** when the comment window closes. Per `0001-rfc-process.md`, the 30-day Core Commitment window applies (RFC-0003 added the default policy file to the Core Commitment; modifying the default policy file thereafter is constrained by that window).

The RFC reaches **Implemented** when the following land, in this order:

**PR-1 — Schema additions + validator Pass 5 + default policy file.**
Files:
- `reference/validator/src/urml_validator/schemas/manifest.py` (add `Provenance`, `ProvenanceComponent`, `HBOMRef` models; optional `provenance` field on `CapabilityManifest`).
- `reference/validator/src/urml_validator/schemas/policy.py` (new — `Policy`, `PolicyRule`, `RuleSelector`, `RulePredicate`, `OnViolation` models).
- `reference/validator/src/urml_validator/errors.py` (extend `ErrorCode` enum; add optional `detail` to `ValidationError`).
- `reference/validator/src/urml_validator/policy_engine.py` (new — `evaluate_policy()` and helpers).
- `reference/validator/src/urml_validator/validator.py` (add `policy` parameter; add Pass 5).
- `reference/validator/src/urml_validator/policies/us_federal_default.yaml` (new — default policy).
- `reference/validator/src/urml_validator/policies/__init__.py` (new — empty, marks directory as package data).
- Tests under `reference/validator/tests/` covering each rule type, default-policy loading, `policy=None` skip, malformed-policy rejection.

**PR-2 — CLI wiring.**
Files:
- `reference/validator/src/urml_validator/cli.py` (`--policy`, `--no-policy` on `validate` and `translate`; pretty-print of `detail` for policy errors).
- `reference/validator/src/urml_validator/schema_export.py` (register `policy` in `SCHEMA_REGISTRY`).
- Tests under `reference/validator/tests/` covering the new flags and exit codes.

**PR-3 — LLM bridge.**
Files:
- `reference/llm-bridge/src/urml_llm_bridge/prompt.py` (`_summarise_manifest()` provenance line).
- `reference/llm-bridge/src/urml_llm_bridge/bridge.py` (revision short-circuit; `BridgePolicyViolation` exception).
- Tests covering the short-circuit semantics.

**PR-4 — Conformance fixtures + manifest provenance backfill.**
Files:
- `conformance/src/urml_conformance/fixtures.py` (add `POLICY_REGISTRY`, optional `policy` field on `FixtureCase`).
- `conformance/fixtures/home/07_policy_country_denied.yaml` (new).
- `conformance/fixtures/home/08_policy_no_policy_flag.yaml` (new).
- `conformance/fixtures/home/09_policy_vendor_denylist.yaml` (new).
- `reference/validator/tests/fixtures/policies/` (new directory: `us_federal_default.yaml` mirror, `permissive_default.yaml`, `eu_ai_act_override.yaml` placeholder).
- `reference/validator/tests/fixtures/manifests/turtlebot4_home.yaml` (backfill US-compliant `provenance:` block).
- `reference/validator/tests/fixtures/manifests/industrial_cell.yaml` (same).

**PR-5 — Spec docs.**
Files:
- `spec/layer-1-hal/README.md` (document the `provenance:` block).
- `spec/layer-1-hal/policy.md` (new — normative policy file format).

**PR-6 — `urml init` template updates.**
Files:
- `reference/validator/src/urml_validator/init_templates.py` (add `provenance:` to scaffolded manifests).

PR-1 blocks PR-2, PR-3, PR-4, PR-6 (each depends on schema/error/engine being present). PR-5 may land at any time. The expected sequence is PR-1 → PR-2 + PR-3 + PR-4 in parallel → PR-5 + PR-6 in parallel.

## Self-review (Phase 0)

The author has reviewed against the checklist in [`0001-rfc-process.md`](0001-rfc-process.md) §Self-review:

- [x] The **Summary** alone tells a reader what is being proposed.
- [x] The **Motivation** is grounded in concrete needs (RFC-0003's commitment is hollow without this mechanism; the LLM revision loop has a real failure mode without policy-error short-circuit; declarative policy is auditable in a way Python code is not).
- [x] The **Detailed design** names every affected spec document (`spec/layer-1-hal/README.md`, new `spec/layer-1-hal/policy.md`) and every affected reference component (validator, CLI, LLM bridge, conformance, init templates, ROS 2 runtime — last one explicitly unaffected).
- [x] At least seven **alternatives** are genuinely considered, with rejection reasoning for each.
- [x] **Drawbacks** lists seven downsides; HBOM-as-opaque-hash, compliance theater, and the public-API growth of `ValidationError.detail` are real costs.
- [x] **Backward compatibility** is honest: one behavioral break (manifests with non-US-compliant provenance now reject by default), explicitly chosen, with an escape hatch.
- [x] **Substrate-neutrality acid test**: this RFC adds no Layer-2 primitive, but the analogous test — *"can a non-ROS substrate's manifest declare provenance and be policy-checked identically?"* — passes by inspection: provenance is a property of declared hardware metadata, independent of the runtime that executes the program. The conformance suite's `industrial_cell.yaml` fixture (currently ROS-targeted) will be validated under the default policy identically to `turtlebot4_home.yaml`; a PX4-targeted manifest with the same provenance block would behave identically.
- [x] The **implementation note** explains how this lands (six PRs, sequenced), not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do. The new "Never embed a specific US administration's executive-order interpretation" bullet is honored: the default policy cites enacted statutes (NDAA 889, FY26 NDAA, FCC Covered List entries) and the American Security Robotics Act *once enacted* (no draft language). No interpretive memos are encoded.
