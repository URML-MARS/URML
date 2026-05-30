---
rfc: 0273
title: substrate.rmw_options.dds_security — declaring DDS-Security profile in the Layer-1 manifest
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

# RFC-0273: `substrate.rmw_options.dds_security` — DDS-Security profile declaration

## Summary

RFC-0251 (substrate.rmw_implementation) deferred DDS-Security profile declaration as future work. DDS-Security is the OMG-standard layer that provides authentication, access control, cryptographic transform, and logging on top of DDS. Fast DDS, Cyclone DDS, and other RMW implementations support it differently. This RFC adds `dds_security` to `rmw_options` with a closed enum of security profile classes, plugin declarations, and certificate-reference fields. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0251 (deferred from Move-16 substrate-spine engagement).

## Motivation

DDS-Security matters for federally-procured deployments (RFC-0003 default policy gates origin; provenance comes via RFC-0253; security profile is the third pillar) and for any deployment where the DDS network is exposed to untrusted nodes. URML's manifest cannot today declare:

1. Whether DDS-Security is enabled at all.
2. Which authentication plugin is in use (PKI / file-based / external).
3. Where the security artifacts (certificates, governance documents, permissions documents) live in the deployment filesystem.

Three concrete consequences of the gap:

1. **Federal-procurement narrative is incomplete.** RFC-0003 default policy already gates substrate origin; provenance (RFC-0253) was added; security profile is the missing third pillar.
2. **Cross-RMW security-profile portability.** Fast DDS and Cyclone DDS implement DDS-Security with subtly different config formats. URML's manifest needs to declare the profile classsuch that the per-RMW glue layer can interpret correctly.
3. **No way to declare zero-trust posture.** A deployment that explicitly does not use DDS-Security should declare `dds_security.enabled: false` so downstream audit tools can see the choice was deliberate.

## Detailed design

### Field shape

```yaml
substrate:
  class: ros2
  rmw_implementation: rmw_fastrtps_cpp
  rmw_options:
    dds_security:                             # NEW — this RFC
      enabled: true
      profile: standard                       # standard | strict | custom | none
      auth_plugin: pki                         # pki | file_based | external | custom
      access_control_plugin: permissions_doc   # permissions_doc | file_based | external | custom
      crypto_plugin: aes_gcm                   # aes_gcm | aes_ctr | custom
      certificates:
        ca_cert_path: /etc/urml/ca.pem
        identity_cert_path: /etc/urml/identity.pem
        identity_key_path: /etc/urml/identity.key
        governance_doc_path: /etc/urml/governance.smime
        permissions_doc_path: /etc/urml/permissions.smime
      enable_logging: true
```

### Allowed values

**Profile class:**

| Value | Description |
|---|---|
| `standard` | Standard DDS-Security profile (auth + access control + crypto enabled) |
| `strict` | Strict profile (additional integrity checks, all messages signed) |
| `custom` | Vendor-specific profile; requires `profile_note` |
| `none` | DDS-Security explicitly disabled (deployment maintainer declares zero-trust posture) |

**Auth plugin:**

| Value | Description |
|---|---|
| `pki` | X.509 PKI-based authentication (OMG DDS-Security standard) |
| `file_based` | File-based shared-secret authentication |
| `external` | External auth provider (custom plugin) |
| `custom` | Vendor-specific |

**Access-control plugin:**

| Value | Description |
|---|---|
| `permissions_doc` | OMG DDS-Security permissions document (S/MIME-signed XML) |
| `file_based` | File-based ACL |
| `external` | External access-control provider |
| `custom` | Vendor-specific |

**Crypto plugin:**

| Value | Description |
|---|---|
| `aes_gcm` | AES-GCM authenticated encryption (OMG DDS-Security default) |
| `aes_ctr` | AES-CTR (encryption only) |
| `custom` | Vendor-specific |

### Schema fragment (extending RFC-0251)

```jsonc
{
  "substrate": {
    "properties": {
      "rmw_options": {
        "properties": {
          "dds_security": {
            "type": "object",
            "properties": {
              "enabled": { "type": "boolean", "default": false },
              "profile": {
                "enum": ["standard", "strict", "custom", "none"]
              },
              "profile_note": { "type": "string" },
              "auth_plugin": {
                "enum": ["pki", "file_based", "external", "custom"]
              },
              "access_control_plugin": {
                "enum": ["permissions_doc", "file_based", "external", "custom"]
              },
              "crypto_plugin": {
                "enum": ["aes_gcm", "aes_ctr", "custom"]
              },
              "certificates": {
                "type": "object",
                "properties": {
                  "ca_cert_path": { "type": "string" },
                  "identity_cert_path": { "type": "string" },
                  "identity_key_path": { "type": "string" },
                  "governance_doc_path": { "type": "string" },
                  "permissions_doc_path": { "type": "string" }
                }
              },
              "enable_logging": { "type": "boolean" }
            },
            "if": { "properties": { "profile": { "const": "custom" } } },
            "then": { "required": ["profile_note"] }
          }
        }
      }
    }
  }
}
```

### Validator behavior

1. **Optional block.** Missing block defaults to `dds_security.enabled: false` (zero-trust default; deployment maintainer must opt-in explicitly).
2. **`enabled: true` requires plugin + certificate declarations.** When `enabled: true` and `profile != none`, the validator requires `auth_plugin`, `access_control_plugin`, `crypto_plugin`, and the relevant `certificates.*` paths.
3. **`profile: none` and `enabled: true` is inconsistent.** Declaring profile=none means security is disabled; declaring enabled=true alongside fails.
4. **`profile: custom` requires note.**
5. **Certificate path opacity.** The validator does not check that the certificate files exist or are valid X.509; that's a deployment-side concern. The paths are documentation.
6. **`--policy` integration.** Default-policy file may set `require_dds_security: true` (extension to RFC-0003); when set, manifests with `dds_security.enabled: false` or missing block fail under `--policy`. Default-policy file ships with `require_dds_security` unset for v0.1.
7. **Forward-compat.** Closed enums.

### Default-policy file additions (RFC-0003)

Adds optional `require_dds_security: true | false` field. Unset for v0.1; federally-procured deployments may set it via custom policy.

### Reference-runtime behavior

Reference runtimes read `dds_security` for startup-log diagnostics and to set the RMW-specific environment variables. Fast DDS reads `FASTRTPS_DEFAULT_PROFILES_FILE` plus security-config files; Cyclone DDS reads `CYCLONEDDS_URI` with security XML. URML's runtime maps the manifest declarations to the RMW-specific config files; the actual security artifacts (certificates) are loaded by the RMW.

### Conformance test additions

`conformance/tests/test_manifest_dds_security.py`:

1. Manifest without `dds_security` passes default-mode validation; enabled defaults to false.
2. Manifest with `dds_security.enabled: true + profile: standard + all plugins + certificate paths` passes.
3. Manifest with `enabled: true + profile: none` fails (inconsistent).
4. Manifest with `enabled: true` missing `auth_plugin` fails.
5. Manifest with `profile: custom` and no `profile_note` fails.

## Backward compatibility

Pre-v1.0. Additive. Existing manifests (which don't declare dds_security) default to enabled=false. The default-policy file is unchanged at v0.1.

## Drawbacks

- **Cross-RMW security-profile portability is partial.** Fast DDS and Cyclone DDS interpret the OMG DDS-Security standard with subtle differences. URML's manifest declares the profile class; the per-RMW glue is substrate-side.
- **Certificate-path opacity weakens validate-time guarantees.** URML can declare the paths but doesn't validate the files. Future RFC could add an offline verification mode.
- **Five-plugin enumeration is opinionated.** Other DDS-Security plugins exist (vendor-specific custom plugins, hybrid file+PKI auth). The `custom` value handles the long tail.
- **`enabled: false` default is conservative.** Some deployments may expect security-on-by-default for federally-procured contexts. URML's discipline: explicit opt-in is safer than implicit always-on (which might silently fail if certificates aren't deployed).

## Alternatives considered

1. **Skip DDS-Security; rely on substrate-side configuration.** Rejected. URML's discipline: manifest is the contract; substrate-side configs hide structure.
2. **Single field `dds_security: standard | strict | none`.** Rejected. Plugin choices and certificate paths are deployment-critical and benefit from explicit declaration.
3. **Default to enabled=true with file-based plugin.** Rejected. Default-enabled would require certificate deployment in every URML manifest, which most non-federally-procured deployments don't need.
4. **Per-topic security profile.** Rejected for v0.1. Deployment-wide security is the standard pattern; per-topic security is over-engineered.

## Prior art

- [RFC-0251 (substrate.rmw_implementation)](0251-substrate-rmw-implementation.md) — parent Spec RFC; this RFC closes the deferred DDS-Security question.
- [RFC-0253 (provenance.slsa_level)](0253-provenance-slsa-level.md), [RFC-0259 (provenance.policy_required_scorecard_min)](0259-provenance-scorecard-policy.md), [RFC-0262 (licensing.boundary)](0262-licensing-boundary.md) — sibling federal-procurement-narrative RFCs; this RFC adds the third pillar (substrate-security alongside provenance and licensing).
- [RFC-0003 (US alignment)](0003-us-alignment.md) — default-policy file this RFC extends.
- OMG DDS-Security specification (cross-cite, not reproduce).

## Unresolved questions

1. **External auth-provider declaration depth.** When `auth_plugin: external`, URML's manifest could declare endpoint URL and credential reference. Future RFC.
2. **DDS-Security log destination.** When `enable_logging: true`, the logs go where? Future RFC could declare a log_destination sub-field.
3. **Cross-domain key management.** Multi-deployment fleets may share keys. URML's manifest is single-deployment-scoped today.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks.
3. Conformance tests (five).
4. Default-policy file documentation update (require_dds_security unset).

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (cross-RMW partial, path opacity, opinion enum, conservative default).
- [x] Backward compatibility additive.
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0251 (parent), RFC-0003 (default policy), RFC-0253/0259/0262 (sibling federal-procurement RFCs).
- [x] CLAUDE.md compliance: federal-procurement narrative completes with security pillar; URML cites OMG DDS-Security standard (open spec) rather than embedding.
