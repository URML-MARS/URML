---
rfc: 0253
title: provenance.slsa_level — declaring substrate supply-chain provenance in the Layer-1 manifest
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

# RFC-0253: `provenance.slsa_level` — declaring substrate supply-chain provenance

## Summary

URML's default-policy file (RFC-0003) embeds US-federal procurement alignment: NDAA Section 889, EO 14307, FCC Covered List. EO 14028 (Improving the Nation's Cybersecurity) adds a supply-chain-provenance layer that SLSA (Supply-chain Levels for Software Artifacts, OpenSSF / Linux Foundation) operationalizes. URML's manifest has no place today to declare a substrate's supply-chain provenance level. This RFC adds a `provenance` block to the Layer-1 manifest containing `slsa_level`, `attestation_url`, and `scorecard_min_score`, defines validator behavior including procurement-policy-gated enforcement, and adds conformance test coverage. Optional. Backward compatible.

The surfaces that demanded this RFC are RFC-0215 (OpenSSF SLSA outreach) and RFC-0216 (OpenSSF Scorecard outreach).

## Motivation

URML's default-policy file (RFC-0003) already gates substrate procurement via NDAA 889, EO 14307, and the FCC Covered List. These cover **origin** (which entity / country the substrate comes from) and **designation** (whether the substrate is on a published exclusion list). What they do not cover is **how the substrate was built**: whether its build process produced verifiable provenance, whether its release artifacts are signed, whether the build environment was reproducible.

EO 14028 cites SLSA as the operationalization for that gap. The federally-procurement-eligible posture URML already supports via RFC-0003 is incomplete without a SLSA-level field in the manifest. Three concrete consequences:

1. **Federal-procurement story has a hole.** URML's policy file can gate a substrate based on NDAA 889 (PRC origin) but not on SLSA L3 (which the federal-procurement audience cares about per EO 14028).
2. **Substrate-side adoption is uneven.** Major robotics substrates (PX4, ROS 2, MoveIt 2, Nav2) have varying SLSA-readiness. URML's manifest field surfaces the fragmentation rather than hiding it.
3. **Validator-side enforcement is missing.** URML's `urml validate --policy` could enforce "this deployment requires SLSA L3 substrates" if the manifest could declare both the substrate's provenance level and the deployment's policy-required-minimum level.

The Move-17 RFC-0215 (SLSA outreach) explicitly requests this field shape. The sibling RFC-0216 (Scorecard) covers the security-health-scoring dimension that pairs with SLSA on the federal-procurement-narrative side.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
provenance:                                    # NEW — this RFC, top-level optional block
  slsa_level: l3                                # l1 | l2 | l3 | l4 | unattested
  attestation_url: https://example.org/foo.intoto.jsonl  # optional
  scorecard_min_score: 7.0                      # optional, 0.0-10.0
  policy_required_min: l2                       # optional, validator enforces if --policy
```

The block is **top-level** rather than nested under `substrate` because future provenance fields (model-card-license, dataset-origin) may apply to non-substrate concerns. v0.1 only ships SLSA and Scorecard fields.

### Allowed values for `slsa_level`

| Value | SLSA Levels v1.0 mapping |
|---|---|
| `l1` | Documented build process |
| `l2` | Tamper-resistance via signed provenance |
| `l3` | Build platform isolation, non-falsifiable provenance |
| `l4` | Hermetic builds, two-party-review |
| `unattested` | Substrate has not published a SLSA attestation |

The values map to SLSA Levels v1.0. URML's value enum is closed at five entries; future SLSA spec versions add via follow-up RFC.

### Allowed values for `attestation_url`

Free-string URL pointing to a SLSA in-toto attestation file (typically `.intoto.jsonl`). The validator does not fetch the URL at validate time; the URL is documentation. Future RFC could add `urml validate --provenance` that fetches and verifies the attestation via `slsa-verifier`. v0.1 of this field is documentation-only.

### Allowed values for `scorecard_min_score`

Numeric, 0.0 to 10.0. Maps to the OpenSSF Scorecard aggregate score. A deployment can declare both the substrate's current score (informational) and the policy-required-minimum the validator enforces. v0.1 ships only the score field; the minimum-policy-enforcement field (`policy_required_scorecard_min`) is a sibling future RFC.

### Validator behavior

`urml validate` adds three checks:

1. **Default mode (no `--policy`).** All provenance fields are informational. The validator does not gate on them.
2. **`--policy` mode.** If the manifest declares `provenance.policy_required_min`, the validator checks that `provenance.slsa_level` meets or exceeds the required level. The level ordering is `unattested < l1 < l2 < l3 < l4`. If the manifest declares a required minimum and the substrate's declared level is below it, validation fails.
3. **Forward-compat for unknown values.** Closed enum; unknown values fail with a pointer to this RFC's amendment process.

### Default-policy file additions (RFC-0003)

The default-policy file gains an optional `provenance_min: l2` field. When set, deployments without `provenance.slsa_level >= l2` fail under `urml validate --policy`. The default-policy file ships **without** this field set for v0.1; the field is documented and available, but the federal-procurement default does not yet mandate SLSA L2 because substrate adoption is too uneven. The field becomes mandatable in a future policy revision when substrate adoption catches up.

### Reference-runtime behavior

Reference runtimes read `provenance.slsa_level` for logging and conformance reporting but do not change dispatch behavior based on it. Provenance is a static-validation concern, not a runtime concern.

### Conformance test additions

`conformance/tests/test_manifest_provenance.py`:

1. A manifest with no `provenance` block passes (optional).
2. A manifest with `provenance.slsa_level: l3` passes validation without `--policy`.
3. A manifest with `provenance.slsa_level: l1` and `provenance.policy_required_min: l3` fails under `--policy`.
4. A manifest with `provenance.slsa_level: unknown_value` fails (closed enum).
5. A manifest with `provenance.scorecard_min_score: 11.0` fails (out of range).

## Backward compatibility

Pre-v1.0. Additive: all fields optional. Existing manifests pass unchanged. The default-policy file gains a new optional field (`provenance_min`) that defaults to unset; existing `--policy` invocations behave identically to v0.1.

## Drawbacks

- **Substrate adoption is uneven today.** Declaring `provenance.slsa_level: l3` for ROS 2 or PX4 is mostly aspirational at v0.1 of this field. The field exists to surface the gap, not to pretend it's solved. Honest framing matters more than coverage.
- **`attestation_url` is not validated.** The validator does not fetch the URL. A future `urml validate --provenance` mode (not landed here) would fetch and verify. The current shape is documentation-only.
- **`scorecard_min_score` is partly redundant with future `policy_required_scorecard_min`.** The current shape ships the substrate's declared score; the policy-enforced minimum is a sibling future field. v0.1 ships only the declared score.
- **Top-level block.** Placing `provenance` outside `substrate` creates an asymmetry with `substrate.autopilot_class`, `substrate.rmw_implementation`, etc. The asymmetry is intentional: provenance is not substrate-specific; future fields (model-card, dataset-origin) are non-substrate-specific too.

## Alternatives considered

1. **Nest provenance under `substrate.provenance`.** Rejected. Provenance concerns extend beyond substrate (model cards, dataset provenance, training-data origin) and a top-level block keeps the future RFC space clean.
2. **Use Scorecard score alone, skip SLSA.** Rejected. SLSA L3 is the EO 14028-cited level that federal-procurement teams already track; URML's federal-aligned posture requires the SLSA field.
3. **Make `provenance.slsa_level` required when `substrate.class` is set.** Rejected. Substrate adoption is too uneven at v0.1; making it required would force `unattested` declarations across most existing manifests for no policy benefit.
4. **Validate attestation_url at validate time.** Considered; rejected for v0.1. The fetch-and-verify path adds network dependency to the validator that violates URML's no-cloud invariant per CLAUDE.md. A separate `urml verify-provenance` mode (offline-runnable with a pre-fetched attestation file) is the future-correct shape.

## Prior art

- [RFC-0215 (OpenSSF SLSA outreach)](0215-openssf-slsa-outreach.md) — the outreach RFC that surfaced this field.
- [RFC-0216 (OpenSSF Scorecard outreach)](0216-openssf-scorecard-outreach.md) — sibling outreach for `scorecard_min_score`.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — the default-policy file this RFC extends.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the conformance framework this RFC adds a test category to.
- SLSA Levels v1.0 spec: https://slsa.dev/spec/v1.0/levels (URML doesn't embed; we cross-cite).
- OpenSSF Scorecard checks: https://github.com/ossf/scorecard/blob/main/docs/checks.md.

## Unresolved questions

1. **Multi-component substrate aggregation.** A ROS 2 deployment composes rclcpp + rclpy + rmw + plugins; each has its own SLSA level. How URML's manifest aggregates is unresolved. Options: (a) declare the lowest level among components (conservative); (b) declare each component separately (verbose); (c) declare the deployment-as-a-whole level (vague). v0.1 stance: single level applies to the substrate as declared; components-level breakdown is future work.
2. **`policy_required_scorecard_min` parallel.** Should the default-policy file also gain `policy_required_scorecard_min`? Sibling future RFC; not in this RFC's scope.
3. **`provenance.signing` field.** Sigstore / cosign signature declarations. Future work, not landed here.

## Implementation plan

1. Land JSON Schema fragment for the top-level `provenance` block.
2. Land validator with `--policy`-gated `provenance.policy_required_min` check.
3. Land conformance tests.
4. Update example manifests in `examples/` to optionally declare provenance fields where the substrate has a real SLSA level.
5. Document the default-policy file's new optional `provenance_min` field; ship default-policy file with it unset for v0.1.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] At least one alternative considered (four).
- [x] Drawbacks named honestly (uneven substrate adoption today, `attestation_url` opacity, scorecard partial-redundancy, top-level placement asymmetry).
- [x] Backward compatibility additive at every field; default-policy file unchanged at v0.1 default.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Validator behavior fully specified including `--policy` gating.
- [x] Cross-references to outreach RFCs and to RFC-0003 default policy.
- [x] No-cloud invariant honored: validator does not fetch URLs at validate time.
- [x] CLAUDE.md compliance: federal-procurement story strengthens without coupling to a single administration's interpretation; SLSA Levels are part of EO 14028 (enacted), not draft guidance.
