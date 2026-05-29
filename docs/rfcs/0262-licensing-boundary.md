---
rfc: 0262
title: licensing.boundary / model_license / commercial_use_gate — declaring license constraints in the Layer-1 manifest
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

# RFC-0262: `licensing.boundary` / `model_license` / `commercial_use_gate`

## Summary

URML's substrate composition spans Apache-2.0 reference runtimes, GPL-3.0 substrates (ORB-SLAM3, Piper TTS), AGPL-3.0 substrates (LibreTranslate), and CC-BY-NC model weights (NLLB-200). The license-boundary integration shape varies: in-source vendoring vs subprocess IPC vs network REST vs cross-citation. URML's manifest has no place today to declare the integration boundary or the commercial-use posture. This RFC adds a `licensing` block with three sibling fields capturing per-component license constraints and validator behavior, extending URML's federal-procurement narrative from substrate-origin (NDAA 889) and substrate-provenance (RFC-0253) to substrate-license-boundary. Optional. Backward compatible.

The surfaces that demanded this RFC are Move-12 RFC-0166 (Piper GPL-3.0 subprocess boundary), RFC-0167 (NLLB-200 CC-BY-NC weights), RFC-0168 (LibreTranslate AGPL-3.0 network boundary), and Move-16 RFC-0206 (ORB-SLAM3 GPL-3.0 cross-citation).

## Motivation

URML's existing license-handling extends to two scopes today: substrate-component licenses appear in compatibility notes inside outreach RFCs, and `perception.slam_substrate.slam_options.license_bind` (RFC-0252) declares the SLAM substrate's license class. Neither covers the integration-boundary question (vendoring vs IPC vs REST vs cross-citation) or the commercial-use gate (NLLB-200's non-commercial weight license, for instance).

Three concrete consequences of the gap:

1. **Operational license-handling is opaque.** A deployment running Piper TTS (GPL-3.0) is operating under a subprocess-IPC integration boundary that downstream packagers must respect. URML's manifest doesn't declare the boundary.
2. **Commercial-use gating is undeclared.** NLLB-200 weights are CC-BY-NC; commercial deployment is restricted. A deployment maintainer declaring `translation_engine_class: nllb` should also be able to declare the commercial-use posture so downstream tooling (procurement audit, deployment configurator) can gate.
3. **Federal-procurement narrative is incomplete.** URML's `--policy` gating covers origin (NDAA 889) and provenance (RFC-0253) but not license-boundary. A federally-aligned deployment may need to refuse GPL-3.0 in-source vendoring while accepting GPL-3.0 subprocess-IPC; the manifest should declare which.

## Detailed design

### Field shape

```yaml
licensing:                                  # NEW — this RFC, top-level optional
  components:                                # NEW — per-component license declarations
    - name: piper                            # component identifier
      license: gpl_3_0
      boundary: subprocess                   # vendored | subprocess | network_rest | cross_citation
      commercial_use_gate: false
    - name: nllb_200                         # NLLB-200 translation weights
      license: cc_by_nc_4_0
      boundary: cross_citation
      commercial_use_gate: true              # non-commercial only
    - name: libretranslate
      license: agpl_3_0
      boundary: network_rest
      network_endpoint: https://lt.example.org/
      secret_reference: env:LIBRETRANSLATE_API_KEY
  policy_required_max_restrictiveness: agpl_3_0   # validator gate under --policy
```

### Allowed values

**License values** (canonical SPDX-style identifiers used internally):

| Value | Description |
|---|---|
| `apache_2_0` | Apache License 2.0 (URML default) |
| `bsd_3_clause` | BSD 3-Clause |
| `mit` | MIT |
| `mpl_2_0` | Mozilla Public License 2.0 |
| `epl_2_0` | Eclipse Public License 2.0 |
| `lgpl_3_0` | GNU LGPL 3.0 |
| `gpl_2_0` | GNU GPL 2.0 |
| `gpl_3_0` | GNU GPL 3.0 |
| `agpl_3_0` | GNU AGPL 3.0 |
| `cc_by_4_0` | Creative Commons Attribution 4.0 |
| `cc_by_nc_4_0` | Creative Commons Attribution-NonCommercial 4.0 (commercial-use-gated) |
| `unknown` | License not declared by upstream |

**Boundary values:**

| Value | Description |
|---|---|
| `vendored` | Source vendored into URML adapter (only acceptable for Apache-2.0-compatible licenses) |
| `subprocess` | Component runs as separate process; URML's adapter is a subprocess caller; the boundary insulates URML's Apache-2.0 source from the component's license terms |
| `network_rest` | Component runs as separate network service; URML calls via HTTP / REST; the network boundary is the license isolation for AGPL-3.0 (per AGPL's network-copyleft semantics, both sides may be in scope depending on deployment topology) |
| `cross_citation` | URML cites the component at the API or vocabulary level only; no code reuse |

### Schema fragment (Layer-1)

```jsonc
{
  "licensing": {
    "type": "object",
    "properties": {
      "components": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "license", "boundary"],
          "properties": {
            "name": { "type": "string" },
            "license": { "$ref": "#/$defs/LicenseId" },
            "boundary": {
              "enum": ["vendored", "subprocess", "network_rest", "cross_citation"]
            },
            "commercial_use_gate": { "type": "boolean" },
            "network_endpoint": { "type": "string", "format": "uri" },
            "secret_reference": { "type": "string" }
          },
          "if": { "properties": { "boundary": { "const": "network_rest" } } },
          "then": { "required": ["network_endpoint"] }
        }
      },
      "policy_required_max_restrictiveness": { "$ref": "#/$defs/LicenseId" }
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing `licensing` is acceptable for deployments composing only Apache-2.0 / BSD / MIT substrates.
2. **`vendored` boundary policy.** When a component declares `boundary: vendored`, the license must be Apache-2.0-compatible (Apache-2.0, BSD-3-Clause, MIT, MPL-2.0). Vendoring GPL-3.0 or AGPL-3.0 is a hard error. Cross-citation or subprocess-IPC are the supported integration shapes for those licenses.
3. **`network_rest` requires `network_endpoint`.** Missing endpoint fails.
4. **`commercial_use_gate` cross-check.** When `commercial_use_gate: true` and the deployment is flagged as commercial (via deployment metadata field, future RFC), validation fails under `--policy`. Without `--policy`, the gate is informational.
5. **`policy_required_max_restrictiveness` enforcement.** When set and `--policy` is active, all declared components must have a license at or below the maximum restrictiveness level. The restrictiveness ordering (least-to-most): `apache_2_0 < mit < bsd_3_clause < mpl_2_0 < epl_2_0 < lgpl_3_0 < gpl_2_0 < gpl_3_0 < agpl_3_0 < cc_by_4_0 < cc_by_nc_4_0 < unknown`. CC-BY-NC is treated as most-restrictive due to commercial gate; `unknown` is most-restrictive due to ambiguity.
6. **`secret_reference` opacity.** The validator does not dereference the secret. Format is `env:VAR_NAME` or `vault:path/to/secret` (extensible).
7. **Forward-compat.** Closed enums on license + boundary.

### Reference-runtime behavior

Reference runtimes read the licensing block for startup-log diagnostics. The runtime does not enforce license terms at runtime; that's a deployment-side and packaging concern. URML's manifest declaring the licenses surfaces the audit trail.

### Default-policy file extension

The default-policy file (RFC-0003) gains an optional `licensing_max_restrictiveness: gpl_3_0` field. **Unset for v0.1.** Federal-procurement deployments may set the field via custom policy.

### Conformance test additions

`conformance/tests/test_manifest_licensing.py`:

1. Manifest without `licensing` block passes.
2. `licensing.components` with `boundary: vendored + license: gpl_3_0` fails.
3. `licensing.components` with `boundary: network_rest` and no `network_endpoint` fails.
4. `policy_required_max_restrictiveness: lgpl_3_0` and a component with `license: gpl_3_0` fails under `--policy`.
5. `commercial_use_gate: true` component passes without `--policy` (informational); behavior under `--policy` with deployment commercial-flag is tested in a separate manifest pair.

## Backward compatibility

Pre-v1.0. Additive. No migration required.

## Drawbacks

- **License enum requires maintenance.** Standard SPDX-style identifiers; growth via RFC.
- **Restrictiveness ordering is opinionated.** The least-to-most ordering captures URML's read of how each license restricts downstream packaging; some operators may dispute specific orderings. The ordering is documented; future RFC can revise.
- **`policy_required_max_restrictiveness` enforcement under `--policy` is binary.** Per-component exceptions ("accept GPL-3.0 for the SLAM component but not the TTS component") are out of scope for v0.1.
- **Commercial-use-gate evaluation depends on a future deployment-commercial-flag.** This RFC scopes the gate field but the commercial-flag side is incomplete; the gate is informational at v0.1.
- **`secret_reference` is documentation-only.** URML's validator doesn't dereference, doesn't check the secret exists, doesn't enforce that the deployment has access. The field is for audit trail.

## Alternatives considered

1. **Skip `licensing` block; use per-substrate license_bind fields scattered across SLAM / RMW / etc.** Rejected. A unified `licensing` block reads cleaner and the policy enforcement applies once. Sibling fields (RFC-0252's `slam_options.license_bind`) remain as substrate-specific shorthands; the `licensing` block is the canonical declaration.
2. **Inline license in each substrate field rather than a separate components block.** Rejected. The components-list shape lets non-substrate licenses (model weights, dataset licenses) live in the same block.
3. **Flat license enum without boundary field.** Rejected. The boundary is operationally critical; vendoring GPL-3.0 is illegal for URML, but subprocess-IPC is fine. The manifest must distinguish.
4. **Skip `commercial_use_gate`; rely on license value alone.** Rejected. CC-BY-NC is the canonical case where commercial-gate is the actual constraint, not the license name; the field surfaces the constraint cleanly.

## Prior art

- [Move-12 RFC-0166 (Piper)](0166-piper1-gpl-outreach.md), [Move-12 RFC-0167 (fairseq / NLLB)](0167-fairseq-outreach.md), [Move-12 RFC-0168 (LibreTranslate)](0168-libretranslate-outreach.md), [Move-16 RFC-0206 (ORB-SLAM3)](0206-orb-slam3-outreach.md) — outreach RFCs that surfaced the license-boundary question.
- [RFC-0252 (slam_substrate)](0252-perception-slam-substrate.md) — sibling Spec RFC; the existing `slam_options.license_bind` is the substrate-specific shorthand that this RFC's unified `licensing` block supersedes for deployment-wide declaration.
- [RFC-0253 (provenance.slsa_level)](0253-provenance-slsa-level.md) — sibling Spec RFC; provenance complements license-boundary for the federal-procurement narrative.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — the default-policy file this RFC extends with optional `licensing_max_restrictiveness`.

## Unresolved questions

1. **Deployment-commercial-flag.** A separate field declaring whether the deployment itself is commercial would enable the `commercial_use_gate` to enforce automatically. Future RFC.
2. **Per-component policy exceptions.** Production deployments may need component-level exceptions (accept GPL-3.0 for SLAM but not TTS). v0.1 is deployment-wide policy.
3. **License-bind aggregation with provenance (RFC-0253).** A future federally-procurement-eligible deployment may need both `licensing.policy_required_max_restrictiveness` AND `provenance.policy_required_min`. The two policies compose; documenting the composition is future work.

## Implementation plan

1. JSON Schema fragment with license + boundary enums.
2. Validator with seven checks (vendoring, network_rest, restrictiveness ordering, commercial gate, etc.).
3. Conformance tests.
4. Optional default-policy field documented.

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (enum maintenance, opinion ordering, binary enforcement, commercial-flag dependency, secret-reference opacity).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to outreach RFCs (4 Move-12/16) + sibling Spec RFCs (0252, 0253, 0003).
- [x] CLAUDE.md compliance: federal-procurement narrative extends license-boundary; URML's Apache-2.0 stance preserved (vendoring restricted to Apache-2.0-compatible licenses); license-neutrality across non-vendored boundaries.
