---
rfc: 0005
title: Structured HBOM Parsing for Pass 5
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-13
updated: 2026-06-12
supersedes: —
superseded-by: —
---

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

# RFC-0005: Structured HBOM Parsing for Pass 5

## Summary

[RFC-0004](0004-compliance-policy.md) added a `provenance:` block to capability manifests and a five-pass validator that enforces compliance policy. Hardware Bill of Materials (HBOM) references in v0.1 are *opaque*: URML records `format`, `uri`, and `sha256` but does not parse SBOM content. This means policy rules can only gate on the manifest's *declared* facts (vendor, country, role); they cannot gate on the *parsed* contents of an HBOM (e.g., "no critical component contains a chip from <list>").

RFC-0005 proposes adding **opt-in structured HBOM parsing** to Pass 5. The validator gains optional CycloneDX 1.7 (and later SPDX 3.0) parsing; the policy DSL gains new predicates that operate on parsed HBOM content; the default policy is unchanged. The CycloneDX library becomes an optional dependency, not a required one — manifests that never declare an `hbom_ref` and policies that never use the new predicates incur no runtime cost.

This RFC is **Draft**: it proposes a design and surfaces open questions. Implementation is gated on Phase 1 adoption pull (a real deployer asking for it) — v0.1 ships hash-pinned HBOM-by-reference and is sufficient for the regulatory frame [RFC-0003](0003-us-alignment.md) commits to.

## Motivation

HBOM-as-opaque-hash is a real half-measure. Concrete failure modes the v0.1 surface cannot catch:

1. **Hidden-Chinese-component substitution downstream of declared HBOM.** A manifest declares `country_of_final_assembly: TW` for a board, with a CycloneDX HBOM that names every chip. A new board revision swaps in a covered-foreign-country chip but the manifest author updates the HBOM to match without updating the manifest's top-level provenance. v0.1's validator sees the hash change, accepts it (the hash is just an integrity gate), and never inspects the chip list.

2. **Vendor-of-vendor regulation.** NDAA §889 covers not just direct vendors but components produced *by* covered entities even when an intermediate integrator owns the part number. CycloneDX's `pedigree.descendants` and `pedigree.ancestors` express this chain. v0.1 cannot enforce against the chain.

3. **CISA / NIST attestation requirements.** US federal procurement increasingly references SBOM/HBOM content directly (NIST SP 800-218 release-1.1+). A deployer claiming compliance needs the *parsed* HBOM, not just an integrity hash.

4. **Cross-policy reuse.** A community-maintained "no covered-entity at any depth" policy file can only exist if the policy DSL can talk about parsed HBOM content. RFC-0004's DSL is currently scoped to manifest-declared facts.

These are real needs. They are not *v0.1* needs — v0.1's regulatory frame is *current* US federal procurement, where opaque hash + manifest-declared facts is the procurement-record-keeping floor. Vendor demand pulls the surface forward when audits start naming HBOM-content rejection as a procurement-gating criterion.

## Detailed design

### Optional-dependency strategy

CycloneDX parsing requires `cyclonedx-python-lib`. The dependency must be **optional** for three reasons:

- Deployments that don't use `hbom_ref` (today: most v0.1 manifests; tomorrow: many home-profile manifests) should not pay the install cost.
- The default policy does not yet require HBOM parsing; adding a required dep for an optional surface is wasted weight.
- SPDX-parsing tooling is a separate ecosystem (`spdx-tools`); supporting both requires the same optional-dep treatment.

Strategy: `pip install urml-validator[hbom]` installs the CycloneDX optional. The validator imports lazily — only when a policy rule with HBOM-content predicates fires AND a manifest with an `hbom_ref` is being checked. If the optional is missing and a rule needs it, the validator emits `policy.hbom_parser_missing` with `severity: warning` and skips the rule.

### New policy predicate fields

The current policy DSL ([`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md)) has these predicate fields:

- `country_of_origin_in`
- `country_of_final_assembly_in`
- `vendor_in`
- `hbom_ref_present`
- `manifest_attestation_in`

RFC-0005 adds:

```yaml
require:  # (same shape under deny)
  hbom_no_components_from_country:
    [<ISO 3166-1 alpha-2>, ...]   # rejects if any HBOM component has supplier.country in the list
  hbom_no_components_from_vendor:
    [<string>, ...]               # rejects if any HBOM component has supplier name in the list
  hbom_pedigree_clean:
    true | false                  # rejects if any component's pedigree has an ancestor flagged
  hbom_attestation_chain_required:
    true                          # requires the HBOM to carry an attestation predicate
                                  # (CycloneDX `attestation` / in-toto layout)
```

Selectors and the `applies_to` shape are unchanged. Rules using these new predicates are evaluated only when:

- The targeted component has an `hbom_ref` set;
- The HBOM file is fetchable (locally or via a URI scheme the validator can resolve — see *Unresolved questions* §1);
- The integrity hash matches;
- The optional `cyclonedx-python-lib` dependency is installed.

### New error codes

- `policy.hbom_component_country_denied`
- `policy.hbom_component_vendor_denied`
- `policy.hbom_pedigree_unclean`
- `policy.hbom_attestation_chain_missing`
- `policy.hbom_parse_failed` (the file exists but pydantic-equivalent parsing failed)
- `policy.hbom_parser_missing` (the optional dep is not installed; warning, not error)
- `policy.hbom_uri_unreachable` (the URI cannot be fetched; warning by default, configurable to error)

### Validator behavior

Pass 5 gains a sub-pass for HBOM-content rules:

1. For each component with an `hbom_ref`, if any HBOM-content rule applies (selector matches AND predicate uses one of the new fields), the validator:
   - Fetches the HBOM file (local URI: read the file; remote URI: only if the validator's `--allow-hbom-fetch` flag is set, per Unresolved §1).
   - Verifies the SHA-256 hash matches the declared one. If not, emits `policy.hbom_parse_failed` with `detail.hash_mismatch: True` and skips further rules for this component.
   - Parses the file as CycloneDX (or SPDX, when supported).
   - Evaluates the rule's HBOM-content predicate against the parsed structure.
2. HBOM-content rule evaluation is **separate** from manifest-content rule evaluation. A single rule cannot mix both (`require: { country_of_origin_in: [...], hbom_no_components_from_country: [...] }` is rejected at parse time — split into two rules).

The validator caches parsed HBOMs per-process (key: SHA-256 hash) so a policy with multiple HBOM rules against the same component doesn't re-parse.

### Default policy changes

The bundled `us_federal_default.yaml` gains **optional** HBOM-content rules — present in the file as commented-out templates, **not active by default in v0.1.5**. Deployers who install the `[hbom]` optional and want the deeper checks uncomment them. The v0.2 default may activate them.

Example commented-template:

```yaml
# Uncomment to enforce HBOM-content rules (requires urml-validator[hbom]):
#
# - id: hbom_critical_no_covered_country_components
#   applies_to: { component_role: critical }
#   deny:
#     hbom_no_components_from_country: [CN, RU, IR, KP]
#   on_violation:
#     code: policy.hbom_component_country_denied
#     message: Critical component's HBOM declares a chip from a covered foreign country.
```

## Backward compatibility

- Manifests without `hbom_ref`: unaffected.
- Policy files without HBOM-content predicates: unaffected.
- The optional dependency: installing without `[hbom]` retains current behavior.
- The CycloneDX-format string convention from RFC-0004 (`format: cyclonedx-1.7`) is the format identifier the parser dispatches on; SPDX support is a separate format identifier (`format: spdx-3.0`).

The single behavioral surface change for v0.2 (if the default policy activates HBOM rules):

- Manifests declaring HBOM refs whose parsed content trips a denylist will newly reject. Mitigation: the change goes through the standard RFC + comment-window process; the default-policy update is a clear flag-day.

## Drawbacks

1. **Dependency surface growth.** CycloneDX (and eventually SPDX) parsers are non-trivial. Optional-dep status helps but doesn't eliminate the install-size and security-surface cost.

2. **Network-resolution policy questions.** Remote HBOM URIs raise: when is the validator allowed to fetch? Caching strategy? Air-gapped deployments? See Unresolved §1.

3. **Parse failures degrade validation.** A malformed HBOM (broken JSON, unexpected schema version) emits a warning but the policy rule is skipped. This is a soft-failure mode that might be exploited (file a deliberately broken HBOM to bypass content checks). Mitigation: the validator's behavior on parse failure is configurable per-rule (`on_parse_failure: warn | reject | skip`); a security-conscious deployment chooses `reject`.

4. **CycloneDX evolution.** v1.7 (current as of mid-2025) added HBOM specifics; v1.8 may change semantics. URML's predicates are version-pinned via the `format:` string but predicate compatibility across CycloneDX versions is a maintenance burden.

5. **SPDX equivalence is non-trivial.** SPDX 3.0's data model differs from CycloneDX's. URML's predicates need a translation layer that may not be exact. Vendor-neutrality argues for both; engineering cost argues for one. RFC-0005 picks CycloneDX-first and adds SPDX in a follow-up if demand exists.

6. **In-toto attestation chains are out of scope.** The `hbom_attestation_chain_required` predicate is named here but its semantics depend on which attestation format URML accepts. v0.2 likely defers full in-toto support.

## Alternatives considered

1. **Defer indefinitely.** Keep v0.1's opaque-hash model. **Rejected**: the gap is real and named in RFC-0004's drawbacks list; not addressing it leaves audit-quality compliance to deployers' bespoke tooling.

2. **Require HBOM parsing (not optional).** Make CycloneDX a hard dependency. **Rejected**: the install cost (~10MB plus transitive deps) and the security-surface cost (JSON-schema parsing in a validator) are real. Most v0.1 deployments don't need it.

3. **Use a generic JSON-path predicate.** Let policy rules express "find a value at this JSONPath in the HBOM and check membership in a list." **Rejected**: this is Turing-tarpit creep — the policy DSL becomes a query language, and the "statically decidable, auditable by counsel without reading Python" guarantee from RFC-0004 weakens.

4. **Externalize HBOM checks entirely.** Have URML emit a "needs HBOM check" sentinel and let a separate tool decide. **Rejected**: the LLM bridge's revision short-circuit (RFC-0004) depends on policy violations being surfaced *during* validation; externalizing breaks that integration.

5. **Per-format separate predicates** (`cyclonedx_no_components_from_country`, `spdx_no_components_from_country`). **Rejected**: doubles the DSL surface and reads as a vendor war. The proposal here uses format-agnostic predicate names (`hbom_no_components_from_country`) and dispatches to per-format parsers internally.

## Prior art

- **CycloneDX 1.7 HBOM section** ([cyclonedx.org/specification/overview](https://cyclonedx.org/specification/overview/)) — the canonical reference for hardware bill-of-materials structure. OWASP-stewarded.
- **SPDX 3.0** — Linux Foundation-stewarded; equivalent expressive power for hardware. The format URML's design accommodates as a peer to CycloneDX.
- **NIST SP 800-218 (SSDF) + IR 8425** — US federal procurement guidance referencing SBOM/HBOM as procurement records.
- **CISA SBOM "minimum elements" guidance** — defines what must be in a federally-procured SBOM; URML's HBOM-content predicates draw selector names from this guidance.
- **in-toto attestation framework** — the canonical "what was built where, by whom, with what" attestation. Cited in the `hbom_attestation_chain_required` predicate; full integration is RFC-0006+ territory.
- **OPA / Rego policy-over-data** — the alternative-considered §3 path. URML's flat-predicate DSL is deliberately less expressive.

## Unresolved questions

1. **Remote HBOM-URI fetching.** What's the validator's posture on URIs that require network?
   - Conservative (the v0.1 stance): never fetch automatically; require the HBOM to be on the local filesystem at the declared URI path; emit a warning if the URI is remote.
   - Permissive: fetch if `--allow-hbom-fetch` is passed, with a default 5-second timeout and a per-URI cache.
   - Hybrid: local-only by default, remote-with-explicit-opt-in via CLI flag.
   Recommendation: hybrid. CLI flag is `--allow-hbom-fetch`; default is local-only.

2. **Air-gapped deployments.** Some federal-procurement deployments are air-gapped. The HBOM-content rules must work locally even without `pip install` access. Implication: the optional dep needs to be installable from a wheelhouse, and the parser cannot phone home.

3. **SPDX-first or CycloneDX-first?** This RFC picks CycloneDX-first based on the OWASP-list adoption inertia and the explicit HBOM section in 1.7. Some federal procurement guidance prefers SPDX. Open: do we commit to CycloneDX as the canonical reference and add SPDX as a peer, or treat them symmetrically from day one?
   Recommendation: CycloneDX-first for v0.2; SPDX support in a follow-up RFC when at least one deployer asks for it.

4. **Streaming parse for large HBOMs?** Large industrial-cell HBOMs (tens of thousands of components) may not fit comfortably in memory. v0.2 implementation can use a streaming parser; the predicate semantics don't require full-tree access for the v0.5 predicates proposed here.

5. **Policy-file syntax for HBOM-content predicates.** The current proposal uses `hbom_*` prefixed fields. An alternative is a nested block. Recommendation: the prefixed form is more discoverable in `urml schema --name policy` output. Stick with prefixes.

6. **Attestation-chain depth limit.** The pedigree-clean predicate as proposed is unlimited-depth. Most procurement guidance is satisfied with depth 2 or 3. Open: add a `max_depth` parameter to the predicate.

## Implementation note

This RFC is **Draft**. It does not advance to Accepted until at least one of:

- An adopter formally requests HBOM-content enforcement for their deployment.
- A regulatory development materially changes the gap (e.g., a Section 889 amendment that specifically requires HBOM-content audit, not just HBOM-hash record-keeping).
- Phase 1 begins (real contributors / steering committee) and the work fits a milestone.

If/when accepted, the implementation phases:

**Phase A** (~1 PR): add the optional `[hbom]` extra to `pyproject.toml`; gate CycloneDX import behind it; add the new policy predicates to the Policy pydantic schema; add error codes; the schema accepts the new fields but the engine still treats them as no-ops with a warning.

**Phase B** (~1-2 PRs): implement the CycloneDX-only HBOM parser-and-evaluator; wire it into Pass 5; add unit tests against curated HBOM fixtures.

**Phase C** (~1 PR): default-policy templates added as commented-out rules; documentation updates.

**Phase D** (out-of-scope for v0.2, possibly v0.3): SPDX support; in-toto attestation-chain support; the `max_depth` parameter and other selector refinements.

Tests required per phase:

- Phase A: schema-parse tests for the new predicate fields; engine-skip tests (rule using new fields emits `policy.hbom_parser_missing` warning and skips when the optional is uninstalled).
- Phase B: per-predicate unit tests using small hand-authored CycloneDX fixtures; integration test against `red-mug.cn-critical.manifest.yaml` extended with a CN-chip HBOM.
- Phase C: docs-only.

### Shipped (Draft → Implemented, 2026-06-12)

Landed as Phases A through C of the plan above, as an opt-in Pass-5 sub-pass.
Fully additive: every existing manifest and policy is unaffected, and the
bundled default policy's behavior is unchanged (the HBOM-content rules ship as
commented-out templates).

- **Schema** ([`policy.py`](../../reference/validator/src/urml_validator/schemas/policy.py)):
  two predicate fields on `RulePredicate`, `hbom_no_components_from_country`
  and `hbom_no_components_from_vendor`. They are deny-only (rejected under
  `require` at parse time) and may not be mixed with manifest-declared-fact
  predicates in the same rule (split into two rules). Spec:
  [`policy.md`](../../spec/layer-1-hal/policy.md) Predicates.
- **Parser** ([`hbom.py`](../../reference/validator/src/urml_validator/hbom.py)):
  resolves a component's `hbom_ref` to a local file relative to the manifest's
  directory, verifies the declared SHA-256, and flattens the CycloneDX document
  (walking `pedigree.ancestors` / `descendants` / `variants` and nested
  `components`) into the country/vendor records the predicates need.
- **Engine** ([`policy_engine.py`](../../reference/validator/src/urml_validator/policy_engine.py)):
  a per-component HBOM sub-pass with a per-call parse cache. Four error codes
  (`policy.hbom_component_country_denied`, `policy.hbom_component_vendor_denied`,
  `policy.hbom_parse_failed`, `policy.hbom_uri_unreachable`). Hash mismatch /
  malformed / unsupported-format are errors (a broken HBOM cannot silently
  bypass a content rule); remote or missing uris are warnings (the validator
  does not fetch). The CLI threads the manifest directory automatically.
- **Conformance**: three `conformance/fixtures/compliance/` cases (clean
  accepted, hidden-CN-chip rejected, vendor-of-vendor pedigree-ancestor
  rejected) + their manifests and an HBOM-content policy.
- **Example**: [`examples/compliance/hidden-cn-chip`](../../examples/compliance/)
  — a manifest with clean top-level provenance (`country_of_origin: US`) whose
  referenced HBOM hides a covered part; rejects under `--policy`, validates
  under `--no-policy`.
- **Tests**: [`test_hbom_policy.py`](../../reference/validator/tests/test_hbom_policy.py)
  (13 cases). Default policy templates added (commented) to
  `us_federal_default.yaml`.

Two deliberate departures from the Draft design, both noted here for the
record:

1. **Dependency-free parsing, not `cyclonedx-python-lib`.** The Draft proposed
   an optional `[hbom]` extra gating a third-party CycloneDX library. The ship
   parses the CycloneDX JSON subset the predicates need with the standard
   library instead. This matches URML's hermetic posture (MockROSAdapter,
   the pure-Python demo hero), keeps the validator installable and runnable on
   any OS and in air-gapped deployments with no extra wheels, and removes the
   install-size / security-surface drawback the Draft listed. Consequently the
   proposed `policy.hbom_parser_missing` warning is not needed and was not
   shipped. Strict, full-schema CycloneDX validation against the library
   remains available as a future option (Phase D) if an adopter needs it.
2. **Two predicates shipped, two deferred.** The well-specified country and
   vendor deny-lists ship, made recursive over the pedigree so they cover the
   vendor-of-vendor case the Draft's separate `hbom_pedigree_clean` predicate
   was meant to address. `hbom_pedigree_clean` and
   `hbom_attestation_chain_required` (which depend on an attestation-format
   decision and in-toto, out of scope per the Drawbacks and Unresolved
   sections) are deferred. SPDX support and remote-fetch (`--allow-hbom-fetch`)
   are likewise deferred to Phase D.

## Self-review (Phase 0)

The author has reviewed against the checklist in [`0001-rfc-process.md`](0001-rfc-process.md) §Self-review:

- [x] The **Summary** alone tells a reader what is being proposed and that this is Draft, not implemented.
- [x] The **Motivation** is grounded in four concrete failure modes the v0.1 surface cannot catch (substituted chips, vendor-of-vendor regulation, CISA/NIST attestation, cross-policy reuse).
- [x] The **Detailed design** names every affected component (Policy schema, Pass 5 engine, default policy, error codes, optional dependency, CLI flag).
- [x] At least one **alternative** is genuinely considered (five are, with rejection reasoning for each).
- [x] **Drawbacks** lists at least one real downside; six are listed, including the in-toto-out-of-scope acknowledgment.
- [x] **Backward compatibility** is honest: existing manifests / policies unaffected; v0.2 default-policy activation is a clear flag-day.
- [x] **Substrate-neutrality acid test**: N/A. This RFC adds no Layer-2 primitive; it extends Layer-1 manifest-evaluation semantics. HBOM parsing is substrate-independent.
- [x] The **implementation note** explains how this lands (four phases, three test categories per phase), not just what. It also explicitly defers acceptance pending adopter pull.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do. This RFC does not introduce a substrate dependency, does not embed a specific US administration's interpretation (it tracks enacted CycloneDX / SPDX / NIST documents), and does not gather user data.
