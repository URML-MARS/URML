---
rfc: 0259
title: provenance.policy_required_scorecard_min — Scorecard-score policy enforcement in the Layer-1 manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0259: `provenance.policy_required_scorecard_min` — Scorecard policy enforcement

## Summary

URML's provenance block (RFC-0253) declares `slsa_level`, `attestation_url`, `scorecard_min_score`, and the SLSA-side `policy_required_min` for `--policy`-gated enforcement. The Scorecard-side policy-enforcement counterpart was scoped for future work in RFC-0253; this RFC delivers it. Adds `provenance.policy_required_scorecard_min` (numeric, 0.0-10.0) to the Layer-1 manifest and extends `urml validate --policy` to gate dispatch when the substrate's declared Scorecard score falls below the policy-required minimum. Optional. Backward compatible.

The surface that demanded this RFC is Move-17 RFC-0216 (OpenSSF Scorecard outreach).

## Motivation

RFC-0253 lands the provenance block with SLSA-side policy enforcement (`policy_required_min`) but defers Scorecard-side enforcement. The deferral was deliberate: SLSA L3 has an enacted-law anchor (EO 14028), while Scorecard scores are a continuous numeric scale that benefit from URML's federal-procurement story being able to express thresholds without requiring substrate adoption to catch up uniformly. The Move-17 RFC-0216 outreach feedback (when it arrives) will inform whether the threshold field semantics are right; this RFC ships the field shape.

Three concrete consequences of landing this field:

1. **Federal-procurement narrative completeness.** With `policy_required_min` (SLSA-side, RFC-0253) and `policy_required_scorecard_min` (Scorecard-side, this RFC) both available, URML's `urml validate --policy` can gate both supply-chain-provenance and ongoing-security-health dimensions. Together they cover the EO 14028 + EO 14110 surface URML's federal-aligned posture targets.
2. **Per-substrate threshold expression.** Different deployments need different Scorecard thresholds. A consumer drone deployment may accept score >= 5; a federal-procurement deployment may require >= 8. URML's manifest declaring per-deployment threshold is the right shape.
3. **Default-policy file compatibility.** The default-policy file (RFC-0003) can be extended with `provenance_scorecard_min: 7.0` once substrate Scorecard adoption catches up; this RFC ships the field shape but does not set a federal-procurement default value yet.

## Detailed design

### Field shape

`policy_required_scorecard_min` is a sibling of `policy_required_min` inside the `provenance` block defined in RFC-0253.

```yaml
provenance:                                  # block defined in RFC-0253
  slsa_level: l3                              # from RFC-0253
  policy_required_min: l2                     # from RFC-0253, SLSA-side
  scorecard_min_score: 8.2                    # from RFC-0253
  policy_required_scorecard_min: 7.0          # NEW — this RFC, Scorecard-side enforcement
```

### Field semantics

- **Type:** number (decimal), inclusive range `[0.0, 10.0]`.
- **Meaning:** the minimum Scorecard aggregate score required for the substrate to pass `urml validate --policy`.
- **Enforcement:** only active when the validator runs with `--policy`. Default (no `--policy` flag) is informational.
- **Comparison:** `scorecard_min_score >= policy_required_scorecard_min` means the substrate passes. Strictly less means the substrate fails.

### Schema fragment (Layer-1, extending RFC-0253's provenance block)

```jsonc
{
  "provenance": {
    "properties": {
      "policy_required_scorecard_min": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 10.0,
        "description": "Minimum Scorecard aggregate score required under --policy. Optional."
      }
    }
  }
}
```

### Validator behavior

`urml validate` adds one check under `--policy`:

1. **Scorecard threshold enforcement.** If both `provenance.scorecard_min_score` and `provenance.policy_required_scorecard_min` are declared, and `scorecard_min_score < policy_required_scorecard_min`, the validator fails with a clear error pointing at this RFC. The error message includes both numeric values for diagnosis.
2. **Missing substrate score under `--policy`.** If `policy_required_scorecard_min` is declared but `scorecard_min_score` is not, the validator fails (cannot enforce a threshold without a measured value). The error message recommends declaring the substrate's actual score or removing the policy requirement.
3. **Range validation.** Both fields are validated as `[0.0, 10.0]`; out-of-range values fail with a clear error.
4. **No interaction without `--policy`.** Default-mode validation treats both fields as informational.

### Default-policy file additions (RFC-0003)

The default-policy file gains an optional `provenance_scorecard_min: <float>` field. The field is **unset for v0.1** of URML's default policy because substrate Scorecard adoption is too uneven to make a federal-procurement default mandatable. The field is documented and available; mandatable in a future policy revision when substrate adoption catches up.

### Reference-runtime behavior

Reference runtimes read both fields for startup-log diagnostics. Provenance enforcement is a static-validation concern; runtimes do not re-check at dispatch time.

### Conformance test additions

`conformance/tests/test_manifest_provenance_scorecard.py`:

1. Manifest with `scorecard_min_score: 8.0` and `policy_required_scorecard_min: 7.0` passes under `--policy`.
2. Manifest with `scorecard_min_score: 5.0` and `policy_required_scorecard_min: 7.0` fails under `--policy`.
3. Manifest with `policy_required_scorecard_min: 7.0` and no `scorecard_min_score` fails under `--policy`.
4. Manifest with `policy_required_scorecard_min: 11.0` fails (out of range).
5. Manifest with `policy_required_scorecard_min: 7.0` passes without `--policy` (informational).

## Backward compatibility

Pre-v1.0. Additive at the field level (extends RFC-0253's provenance block). Existing manifests unchanged. Default-policy file behavior unchanged at v0.1 (the new optional field defaults to unset).

## Drawbacks

- **Threshold value is opinion-soft.** Scorecard scores depend on the upstream's signal coverage; a substrate with no signing and no SAST may score lower than the policy threshold even if the substrate is otherwise solid. URML's manifest accepts the score as the deployment maintainer declares it; the validator does not recompute Scorecard at validate time.
- **No live Scorecard fetch.** Like RFC-0253's `attestation_url`, this RFC does not fetch the Scorecard score live. The maintainer-declared value is the truth-of-record for URML's manifest. A future `urml verify-provenance` (offline) mode could verify against a checked-in Scorecard report.
- **Per-substrate aggregation.** A composite substrate (ROS 2 = rclcpp + rclpy + rmw + plugins) has multiple Scorecard scores; URML's manifest declares one aggregate. The aggregation is the maintainer's call. Same issue as RFC-0253's SLSA aggregation; future RFC could address.
- **`policy_required_*` siblings now number two.** SLSA and Scorecard. Future provenance dimensions (Sigstore signing, SBOM availability) would add more. The discipline is one policy-required field per provenance dimension.

## Alternatives considered

1. **Bundle Scorecard threshold into RFC-0253 instead of separate RFC.** Rejected. RFC-0253 was scoped to SLSA-and-base-fields to keep the landing surface tractable; Scorecard threshold benefits from its own enforcement specification.
2. **Score-and-threshold as combined sibling field.** Rejected. Substrate-declared score and policy-required threshold are different concerns: one is fact-of-substrate, one is fact-of-policy. Separate fields per the same convention RFC-0253 uses.
3. **Use a 0-100 integer scale instead of 0.0-10.0 decimal.** Rejected. Scorecard's published score is decimal 0.0-10.0; URML's manifest matches the upstream convention.
4. **Per-signal threshold (rather than aggregate).** Rejected for v0.1. Aggregate threshold is the federally-cited shape (per EO 14028 references to Scorecard); per-signal thresholds are over-engineered for the v0.1 federal-procurement narrative.

## Prior art

- [RFC-0253 (provenance.slsa_level)](0253-provenance-slsa-level.md) — the parent provenance-block RFC; this RFC extends it with Scorecard-side enforcement.
- [RFC-0216 (OpenSSF Scorecard outreach)](0216-openssf-scorecard-outreach.md) — the outreach RFC that surfaced this field.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — the default-policy file this RFC extends with optional `provenance_scorecard_min`.
- OpenSSF Scorecard checks: https://github.com/ossf/scorecard/blob/main/docs/checks.md.

## Unresolved questions

1. **Per-signal threshold field.** Future field could express "branch-protection must score >= 8 AND signed-releases must score >= 7" rather than aggregate-only. Future RFC if the federal-procurement audience requests it.
2. **Live Scorecard verification mode.** An offline `urml verify-provenance` mode (fetch Scorecard JSON via gh API at deployment-prep time, verify at validate time against a checked-in copy) is plausible. Future RFC.
3. **Default-policy file Scorecard requirement.** When substrate Scorecard adoption catches up, the default policy could mandate `provenance_scorecard_min: 7.0` (or similar). Decision timing is empirical, not in this RFC.

## Implementation plan

1. JSON Schema fragment extending RFC-0253's provenance block.
2. Validator with `--policy`-gated threshold check.
3. Conformance tests (five).
4. Update RFC-0003 (US alignment) documentation to note the new optional default-policy field, with the field unset for v0.1.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (threshold opinion-softness, no live fetch, per-substrate aggregation, policy_required_* sibling growth).
- [x] Backward compatibility additive (optional field; default-policy unchanged at v0.1).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (0216) and sibling Spec RFCs (0253, 0003).
- [x] CLAUDE.md compliance: federal-procurement narrative completes without coupling to a single-administration's interpretation; Scorecard threshold is policy-shaped (per deployment) rather than law-shaped (per executive order).
