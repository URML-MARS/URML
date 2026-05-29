---
rfc: 0254
title: substrate.maturity_tier — declaring substrate maturity in the Layer-1 manifest
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

# RFC-0254: `substrate.maturity_tier` — declaring substrate maturity

## Summary

URML deployments today implicitly target production-stable substrates (ROS 2 with Fast DDS, MoveIt 2, Nav2, PX4). The substrate-emerging surface (Zenoh as ROS 2 RMW, iceoryx2 as the next-generation IPC, Stella VSLAM as a community-fork ORB lineage) is real but URML's manifest has no place to declare that a deployment is consciously running on a substrate-emerging stack. This RFC adds `substrate.maturity_tier` to the Layer-1 manifest with a closed three-value enum (`production`, `emerging`, `experimental`), defines validator behavior including a deployment-warning when emerging or experimental tiers are declared, and adds conformance test coverage. Optional with `production` as the implicit default. Backward compatible.

The surface that demanded this RFC most explicitly is RFC-0209 (Eclipse Zenoh outreach), where URML's manifest needs to declare `rmw_zenoh_cpp` as substrate-emerging in a way that's honest about Zenoh's not-yet-default status without rejecting it from URML deployments today.

## Motivation

URML's substrate-neutrality claim works in both directions: a deployment can target production-stable substrates (`rmw_fastrtps_cpp`, `cartographer`, `px4`) or it can target substrate-emerging stacks that may become the default tomorrow but aren't today (`rmw_zenoh_cpp`, `iceoryx2`, `stella_vslam` while license is unclarified). URML's manifest currently has no place to express the difference. Three concrete consequences:

1. **No honest framing for `rmw_zenoh_cpp`.** Sibling RFC-0251 (`substrate.rmw_implementation`) accepts `rmw_zenoh_cpp` as a valid value, but production users targeting Zenoh today should be running with eyes-open about its substrate-emerging status. The manifest needs to capture that.
2. **No mechanism for URML's conformance suite to flag emerging-tier deployments.** A conformance run against an experimental-tier substrate should still pass but should surface a warning that the substrate is not stability-claimed.
3. **No path to declare consciousness of risk.** A deployment maintainer using Stella VSLAM with license-clarification-pending or iceoryx2 (the Rust rewrite of iceoryx, sub-stable) should be able to declare the maturity tier explicitly so downstream operators understand the deployment posture.

The Move-16 RFC-0209 explicitly requests this field. Move-16 RFC-0211 (Stella VSLAM) and RFC-0210 (iceoryx, where iceoryx2 is the sub-stable successor track) also benefit.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_zenoh_cpp
  maturity_tier: emerging                    # NEW — this RFC, optional
  maturity_tier_note: >                       # NEW — required when tier != production
    Zenoh is not yet the ROS 2 default RMW;
    deployment uses Zenoh's WAN-spanning routing
    for the large-fleet topology this deployment
    targets.
```

The note field is required only when `maturity_tier` is `emerging` or `experimental`. The discipline mirrors the `custom` escape-hatch pattern in sibling RFCs 0250-0252: an opinionated-default choice gets a free pass; off-default choices require a note documenting the choice.

### Allowed values

| Value | Description |
|---|---|
| `production` | Substrate is production-stable per its own upstream stability claim. Default when field omitted. |
| `emerging` | Substrate is approaching production stability but not yet default in its ecosystem. Examples: `rmw_zenoh_cpp` in 2026 ROS 2. |
| `experimental` | Substrate is sub-stable; deployment maintainer accepts risk. Examples: iceoryx2 in 2026; Stella VSLAM with license-clarification pending. |

The enum is intentionally small. URML doesn't grade substrates beyond three buckets because finer gradations are subjective and would require per-substrate maturity reviews that URML can't sustain.

### Schema fragment (Layer-1)

```jsonc
{
  "substrate": {
    "properties": {
      "maturity_tier": {
        "type": "string",
        "enum": ["production", "emerging", "experimental"],
        "default": "production"
      },
      "maturity_tier_note": {
        "type": "string",
        "description": "Required when maturity_tier is emerging or experimental."
      }
    },
    "if": {
      "properties": {
        "maturity_tier": {
          "enum": ["emerging", "experimental"]
        }
      }
    },
    "then": {
      "required": ["maturity_tier_note"]
    }
  }
}
```

### Validator behavior

1. **Field is optional.** Missing field means `production` (the default).
2. **Note required when off-default.** `maturity_tier: emerging` or `experimental` requires a non-empty `maturity_tier_note`.
3. **Warning emission at validate time.** When `maturity_tier` is `emerging` or `experimental`, the validator emits a warning to stderr (does not fail validation) noting the substrate's maturity status and pointing at the deployment's `maturity_tier_note` for the operator-facing rationale.
4. **No interaction with `--policy`.** This field is informational. It does not gate procurement. The default-policy file (RFC-0003) is not extended here; if URML's federal-procurement default ever wants to require `production` only, that's a future policy-file revision, not a validator-level enforcement here.
5. **Forward-compat.** Closed enum; unknown values fail.

### Reference-runtime behavior

Runtimes read `maturity_tier` and surface it in startup logs ("deployment runs on substrate-emerging RMW per manifest declaration"). No dispatch-behavior change.

### Conformance test additions

`conformance/tests/test_manifest_maturity_tier.py`:

1. Manifest without `maturity_tier` field passes (implicit `production`).
2. Manifest with `maturity_tier: production` and no note passes.
3. Manifest with `maturity_tier: emerging` and no note fails.
4. Manifest with `maturity_tier: emerging` and a note passes with a warning emitted.
5. Manifest with `maturity_tier: experimental` and a note passes with a warning emitted.

## Backward compatibility

Pre-v1.0. Additive: missing field defaults to `production`, which is the implicit assumption for every existing manifest. No migration required.

## Drawbacks

- **Three-bucket enum is opinionated.** Some users may want finer maturity gradations (alpha / beta / RC / GA). URML's stance: three buckets is the right granularity for a manifest-layer declaration. Per-substrate finer gradations belong in the substrate's own docs, not in URML's manifest.
- **Self-attestation.** The maturity tier is declared by the deployment maintainer, not validated against an upstream source-of-truth. The validator has no way to check that `rmw_zenoh_cpp` is actually emerging vs production. URML accepts the self-attestation because the alternative (URML maintaining its own substrate-maturity database) is unsustainable.
- **Warning emission overlaps with `license_bind` warnings (sibling RFC-0252) and with `unattested` SLSA-level warnings (RFC-0253).** The validator's warning surface grows; the discipline is to keep each warning specific and pointing at the specific manifest field that triggered it.

## Alternatives considered

1. **Skip the field; let users document maturity in narrative.** Rejected. The whole URML-manifest premise is that operational choices belong in the validator-checkable manifest, not in narrative. Maturity is an operational choice.
2. **Finer-grained enum (alpha / beta / rc / ga / stable / legacy / deprecated).** Rejected. Beyond the gradation URML can sustain; per-substrate.
3. **Compute maturity tier from substrate identity automatically.** Rejected. Requires URML to maintain a substrate-maturity database that updates faster than RFC-gated enums can keep up. Self-attestation respects the deployment maintainer's judgment.
4. **Make `maturity_tier` required.** Rejected. Most existing manifests target production substrates implicitly; making the field required would force a no-op `production` declaration across the existing manifest corpus.

## Prior art

- [RFC-0209 (Eclipse Zenoh outreach)](0209-zenoh-outreach.md) — the surface that surfaced this field.
- [RFC-0210 (iceoryx outreach)](0210-iceoryx-outreach.md) — sibling; iceoryx2 is the sub-stable successor.
- [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md) — sibling; license-clarification-pending Tier B substrate.
- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — the field that accepts `rmw_zenoh_cpp` as a value; this RFC complements with the maturity declaration.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the conformance framework this RFC adds a warning category to.

## Unresolved questions

1. **Per-substrate-component maturity.** A deployment running Cyclone DDS (production) + Stella VSLAM (license-clarification pending; emerging) is single-tier in this RFC's shape. Should the manifest declare per-component maturity? Future work, not in v0.1 of this field.
2. **Maturity-tier-based procurement policy.** Should URML's default-policy file gain a `policy_required_maturity_tier: production` setting? Sibling future RFC.
3. **Maturity transitions.** When `rmw_zenoh_cpp` graduates from emerging to production, URML's manifest needs no field change but the deployment-maintainer's note should update. There's no formal mechanism to track substrate-maturity transitions today; future RFC could define one.

## Implementation plan

1. Land JSON Schema fragment.
2. Land validator with warning emission for `emerging` and `experimental`.
3. Land conformance tests.
4. Update example manifests where applicable (Zenoh-targeted examples).
5. Document warning emission in `reference/validator/` docs.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] At least one alternative considered (four).
- [x] Drawbacks named honestly (three-bucket opinion, self-attestation lack of upstream verification, warning-surface growth).
- [x] Backward compatibility additive (default value preserves existing behavior).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Validator behavior fully specified including warning emission.
- [x] Cross-references to outreach RFCs.
- [x] CLAUDE.md compliance: substrate-neutrality preserved (URML accepts emerging-tier substrates rather than refusing them); enum closure preserves the discipline.
