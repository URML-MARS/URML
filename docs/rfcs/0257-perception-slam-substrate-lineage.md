---
rfc: 0257
title: perception.slam_substrate.lineage — declaring community-fork lineage for SLAM substrates
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

# RFC-0257: `perception.slam_substrate.lineage` — community-fork lineage

## Summary

URML's `perception.slam_substrate` field (RFC-0252) accepts values like `stella_vslam` that are community continuations of archived upstreams (OpenVSLAM in Stella VSLAM's case). The lineage matters: a deployment maintainer reading the manifest should be able to see that Stella VSLAM is the maintained fork of OpenVSLAM that was archived in 2019, and that the relationship affects citation, license posture, and operational risk. This RFC extends `perception.slam_options` with a `lineage` sub-field declaring the archived-upstream ancestry. Optional, with the discipline that any `slam_substrate` value flagged as community-fork in URML's documentation should declare lineage. Backward compatible.

The surface that demanded this RFC is Move-16 RFC-0211 (Stella VSLAM outreach).

## Motivation

Some SLAM substrates carry archived-upstream lineage. Stella VSLAM is the maintained continuation of OpenVSLAM after that project was archived in 2019 over a license dispute (DBoW2 vocabulary derivation). RTAB-Map has dependency lineage on visual-feature libraries with mixed licenses. URML's manifest has no way today to declare the community-fork ancestry explicitly. Three concrete consequences:

1. **Provenance documentation gap.** A deployment maintainer running Stella VSLAM should be able to see in the manifest that it's the OpenVSLAM successor; otherwise the manifest implies a fresh-upstream substrate when it isn't.
2. **License-clarification audit trail.** OpenVSLAM was archived over a license dispute. Stella VSLAM's continuation license posture is still pending clarification (per RFC-0211 unresolved questions). URML's manifest declaring lineage surfaces the audit trail at validate time.
3. **Future archived-upstream cases.** Stella VSLAM is the first; future SLAM substrates may inherit similar lineage relationships. URML's manifest needs the field shape now so subsequent community forks fit.

## Detailed design

### Field shape

`lineage` is a sub-field of `slam_options` (which RFC-0252 defines as the SLAM-substrate options block).

```yaml
perception:
  slam_substrate: stella_vslam
  slam_mode: stereo
  slam_options:
    lineage: openvslam                       # NEW — this RFC
    lineage_archived_at: 2019                 # NEW — optional, year of upstream archive
    lineage_note: >                           # NEW — optional, human-readable rationale
      Stella VSLAM is the maintained community
      fork of OpenVSLAM, which was archived in
      2019 over a license dispute concerning
      the DBoW2 vocabulary derivation.
    license_bind: unknown                     # from RFC-0252
```

### Allowed values for `lineage`

`lineage` is a free-string with a recommended convention: lowercase short name of the archived upstream. URML does not maintain a closed enum because lineage relationships are not URML's to enumerate; the field is documentation of an external fact (the project archive history).

Recommended values appearing in URML's documentation today:

| Value | Description | Used by |
|---|---|---|
| `openvslam` | OpenVSLAM, archived 2019 | `stella_vslam` |
| `orb_slam2` | ORB-SLAM2, predecessor to ORB-SLAM3 | Cross-reference only; `orb_slam3` is the actively-maintained continuation, not a fork |
| `none` | Substrate is not a community fork | Default when omitted |

Note that `orb_slam3` cross-references `orb_slam2` but is **not a community fork**; ORB-SLAM3 is the actively-maintained continuation by the original authors. URML's lineage field is specifically for community-fork-after-upstream-archive relationships.

### Schema fragment (Layer-1, extending RFC-0252)

```jsonc
{
  "perception": {
    "properties": {
      "slam_options": {
        "properties": {
          "lineage": {
            "type": "string",
            "description": "Free-string declaring archived-upstream ancestry (e.g., openvslam for Stella VSLAM)."
          },
          "lineage_archived_at": {
            "type": "integer",
            "minimum": 2000,
            "maximum": 2100,
            "description": "Year the upstream was archived (optional)."
          },
          "lineage_note": {
            "type": "string",
            "description": "Human-readable rationale (optional)."
          }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional.** Missing field is the default; substrate is not a community fork (or the maintainer chose not to declare).
2. **Documentation, not enforcement.** The validator does not gate on `lineage`. It surfaces the field in validate-output for downstream consumers (audit logs, conformance reports).
3. **Recommended-when-flagged.** URML's documentation for `slam_substrate` values flags which ones are community forks. When the manifest declares one of those substrates without `lineage`, the validator emits a soft suggestion (not a warning) pointing at this RFC. The suggestion exists for documentation hygiene; the deployment validates fine without it.
4. **Year sanity check.** If `lineage_archived_at` is set, the year must be in `[2000, 2100]`.

### Reference-runtime behavior

Reference runtimes log `lineage` in startup diagnostics ("running SLAM substrate stella_vslam, OpenVSLAM lineage, declared archive year 2019"). No dispatch-behavior change.

### Conformance test additions

`conformance/tests/test_manifest_slam_lineage.py`:

1. Manifest with `slam_substrate: stella_vslam` and `lineage: openvslam` passes.
2. Manifest with `slam_substrate: stella_vslam` and no lineage passes with soft suggestion.
3. Manifest with `slam_substrate: cartographer` and no lineage passes silently (Cartographer is not a community fork).
4. Manifest with `lineage_archived_at: 1985` fails (out of range).
5. Manifest with `lineage: "free-form anything"` passes (free-string field).

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **Free-string field is opinion-soft.** URML doesn't enumerate lineage values because they're external facts. The cost is that two manifests describing the same lineage relationship can differ on the string. The discipline is documentation in URML's own docs (which the field then cites by convention).
- **Soft suggestion is novel for the validator.** The validator currently has errors and warnings; adding soft suggestions extends the output surface. The suggestion is opt-in to URML's documentation-hygiene posture.
- **`orb_slam3` looks like it should declare lineage but doesn't qualify.** The field is specifically for community-fork-after-archive; actively-maintained continuations like ORB-SLAM3 do not. The boundary is documented in this RFC and in RFC-0252; URML's convention is "community fork means upstream was archived and a separate group picked it up."

## Alternatives considered

1. **Skip the field; rely on RFC-0252's substrate enum + URML documentation.** Rejected. RFC-0252's enum doesn't capture the lineage relationship in the manifest itself; manifests reading-without-docs lose the audit trail.
2. **Closed enum of lineage values.** Rejected. Lineage is an external fact, not URML's to enumerate; closing the enum would force URML to track every community-fork relationship in robotics, which it can't sustain.
3. **Top-level `lineage` field instead of nested under `slam_options`.** Rejected. Lineage is SLAM-substrate-scoped today; future RFCs may surface lineage for other substrate classes, at which point the field shape generalizes.
4. **Add lineage to the validator's error surface (fail-without-declaration for community forks).** Rejected. The hygiene cost would dominate; soft suggestion is the right strength.

## Prior art

- [RFC-0211 (Stella VSLAM outreach)](0211-stella-vslam-outreach.md) — the outreach RFC that surfaced this field.
- [RFC-0252 (perception.slam_substrate)](0252-perception-slam-substrate.md) — parent Spec RFC; this RFC extends `slam_options`.
- OpenVSLAM archive history (referenced in RFC-0211).

## Unresolved questions

1. **Generalizing lineage to non-SLAM substrates.** Other substrates may eventually carry community-fork lineage (e.g., a hypothetical `rmw_zenoh_cpp_community` fork after Zenoh maintainer changes). The field shape generalizes by moving from `slam_options.lineage` to a top-level `substrate.lineage` field; future RFC.
2. **Standardizing lineage string values.** URML's documentation could ship a registry of canonical lineage strings to prevent drift; v0.1 of this field uses convention plus the SLAM-substrate documentation.
3. **Archived-upstream metadata.** Year-of-archive is captured. License-at-archive, reason-for-archive, replacement-relationship are not. Future RFC if the demand surfaces.

## Implementation plan

1. JSON Schema fragment.
2. Validator with soft-suggestion emission.
3. Conformance tests.
4. Update RFC-0252 cross-reference and example manifests.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (free-string opinion-softness, soft-suggestion novelty, ORB-SLAM3 boundary explanation).
- [x] Backward compatibility additive (optional sub-field).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (0211) and sibling Spec RFCs (0252).
- [x] CLAUDE.md compliance: documentation discipline preserves audit trail without growing URML's enforcement surface.
