---
rfc: 0268
title: deployment.commercial_use — closing the commercial-use-gate enforcement loop
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-29
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

# RFC-0268: `deployment.commercial_use` — closing the commercial-use enforcement loop

## Summary

RFC-0262 declared `licensing.components[].commercial_use_gate` for license-bound components (CC-BY-NC weights, AGPL-3.0 network-copyleft surfaces) and noted that the gate's enforcement under `urml validate --policy` depends on a future field declaring whether the deployment itself is commercial. This RFC closes the loop: adds `deployment.commercial_use` as a top-level boolean field, defines the validator's `--policy` enforcement, and updates the default-policy file to recognize the flag. Optional. Backward compatible.

The surface that demanded this RFC is RFC-0262 (licensing.boundary), specifically the unresolved-question on deployment-commercial-flag.

## Motivation

A deployment maintainer running NLLB-200 model weights (CC-BY-NC 4.0) under URML's translation engine class (RFC-0260) is operating under non-commercial constraints from the weight license. If the deployment is non-commercial (research, education, hobby), the constraint is satisfied. If the deployment is commercial (paid service, embedded in a sold product), the deployment violates the weight license.

URML's current state: the manifest can declare `licensing.components[].commercial_use_gate: true` for the gated component but cannot declare whether the deployment itself is commercial. The gate is therefore informational only.

Three concrete consequences of closing the loop:

1. **Federal-procurement narrative completes.** Federal-procurement deployments are commercial by definition (the government is paying); URML's manifest declaring `deployment.commercial_use: true` lets the validator automatically refuse CC-BY-NC components under `--policy`.
2. **Research-vs-production distinction becomes machine-readable.** Research / education deployments declare `commercial_use: false`; the validator accepts CC-BY-NC components without warning. Production deployments declare `commercial_use: true`; the validator gates.
3. **Hybrid deployments need explicit declaration.** Some deployments span research (publishable results) and commercial (consulting). The manifest needs an unambiguous boolean; ambiguity defaults to commercial (most-restrictive default).

## Detailed design

### Field shape

```yaml
deployment:                                 # NEW — this RFC, top-level optional block
  commercial_use: false                      # boolean, defaults to true if missing
  deployment_class: research                 # research | education | production | hobby | unspecified
  organization: example_research_lab         # informational
  declared_at: "2026-05-29"                  # informational
```

The block is **top-level** rather than nested under `substrate` or `licensing` because deployment metadata spans more than license enforcement (audit, observability, federal-procurement attestation).

### Default behavior

If the `deployment` block is missing or `commercial_use` is omitted, the validator treats the deployment as **commercial** by default. The most-restrictive default prevents accidentally bypassing the CC-BY-NC gate.

A deployment that is genuinely non-commercial must explicitly declare `commercial_use: false`.

### Allowed values for `deployment_class`

| Value | Description | `commercial_use` default |
|---|---|---|
| `research` | Academic / non-profit research; no paid service | false |
| `education` | Educational use (FIRST Robotics, university coursework, lab demos) | false |
| `hobby` | Personal / hobbyist deployment | false |
| `production` | Production deployment (commercial or government-procured) | true |
| `unspecified` | Not declared | true (most-restrictive default) |

`deployment_class` is informational; the validator enforces only on `commercial_use`. The two fields can be declared together for documentation but `commercial_use` is the gate.

### Schema fragment (Layer-1)

```jsonc
{
  "deployment": {
    "type": "object",
    "properties": {
      "commercial_use": { "type": "boolean", "default": true },
      "deployment_class": {
        "enum": ["research", "education", "hobby", "production", "unspecified"]
      },
      "organization": { "type": "string" },
      "declared_at": { "type": "string", "format": "date" }
    }
  }
}
```

### Validator behavior

1. **Optional block; defaults to commercial.** Missing block or missing `commercial_use` field means `commercial_use: true` (most-restrictive default).
2. **`--policy` enforcement of commercial-use-gate.** When `--policy` is active and `deployment.commercial_use: true`, any `licensing.components[]` entry with `commercial_use_gate: true` fails validation. The validator emits an error pointing at the specific component and at this RFC.
3. **No enforcement without `--policy`.** Default-mode validation treats both fields as informational; the gate emits a soft warning that the deployment is commercial and a gated component is declared, but does not fail.
4. **Consistency check.** When `deployment_class: research` (or `education`, `hobby`) but `commercial_use: true`, the validator emits a warning surfacing the inconsistency for review. The combination is allowed; the warning surfaces the deliberate choice.
5. **Forward-compat.** Closed enum on `deployment_class`.

### Default-policy file additions (RFC-0003)

The default-policy file gains an optional `require_commercial_use_declaration: true` field. When set:

- Manifests must explicitly declare `deployment.commercial_use` (the implicit-default-to-commercial rule no longer applies).
- A missing `deployment.commercial_use` fails validation under `--policy`.

The field is **unset for v0.1** of the default policy. Federal-procurement deployments may set the field via custom policy.

### Reference-runtime behavior

Reference runtimes read `deployment.commercial_use` and `deployment_class` for startup-log diagnostics and observability metadata. The runtime does not gate based on these fields at runtime; gating is a static-validation concern.

### Conformance test additions

`conformance/tests/test_manifest_deployment_commercial.py`:

1. Manifest without `deployment` block passes default-mode validation; under `--policy` with a `commercial_use_gate: true` component, fails (most-restrictive default).
2. Manifest with `deployment.commercial_use: false` passes under `--policy` even with `commercial_use_gate: true` components.
3. Manifest with `deployment_class: research + commercial_use: true` passes with warning.
4. Manifest with `require_commercial_use_declaration: true` in active policy and no `deployment.commercial_use` field fails.
5. Manifest with `deployment_class: unspecified + commercial_use: false` passes (explicit declaration overrides class-implied default).

## Backward compatibility

Pre-v1.0. Additive at the field level. Existing manifests without `deployment` block default to `commercial_use: true`; under `--policy` against the v0.1 default-policy file (which doesn't set `require_commercial_use_declaration`), the implicit default applies and existing manifests continue to validate.

The only breaking change is for existing manifests that declare `licensing.components[].commercial_use_gate: true` AND are run under `--policy`. Those manifests previously had the gate as informational; now the gate enforces. The migration: add `deployment.commercial_use: false` to research-class manifests; commercial deployments accept the gate enforcement.

## Drawbacks

- **Most-restrictive default may surprise.** A deployment maintainer omitting `deployment.commercial_use` discovers the deployment is treated as commercial. The default is safe but unintuitive for hobbyist users. The default is justified: the cost of accidentally violating CC-BY-NC is higher than the cost of an explicit declaration.
- **`deployment_class` is informational only.** The validator enforces only `commercial_use`. The class is documentation; the gate is enforcement.
- **Hybrid deployments need a binary choice.** A research lab that occasionally consults commercially must declare `commercial_use: true` to be safe. URML doesn't support per-program-run commercial flag; the manifest is deployment-static.
- **Federal-procurement narrative depends on operator honesty.** URML cannot verify that a `commercial_use: false` declaration is truthful. The validator accepts the maintainer's declaration; downstream audit is responsibility-of-the-operator.

## Alternatives considered

1. **Default to non-commercial (least-restrictive default).** Rejected. The cost of accidentally violating CC-BY-NC weight licenses is operationally serious; most-restrictive default protects deployments by default.
2. **Skip `deployment_class`; use only `commercial_use`.** Considered. The deployment_class is documentation; the boolean is enforcement. Both together provide useful context for audit.
3. **Per-component commercial flag (override deployment-wide for specific components).** Rejected for v0.1. Deployment-wide flag is the standard case; per-component override is over-engineering.
4. **Use `licensing.deployment_is_commercial` instead of top-level `deployment.commercial_use`.** Rejected. Deployment metadata applies beyond licensing (audit, observability, federal-procurement attestation); top-level placement matches the broader scope.

## Prior art

- [RFC-0262 (licensing.boundary)](0262-licensing-boundary.md) — parent Spec RFC; this RFC closes its deferred commercial-flag question.
- [RFC-0003 (US alignment)](0003-us-alignment.md) — the default-policy file this RFC extends with optional `require_commercial_use_declaration`.
- Move-12 RFC-0167 (fairseq / NLLB) — surfaced the CC-BY-NC weight-license case that motivates this gate.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — conformance framework this RFC adds tests to.

## Unresolved questions

1. **Per-program-run commercial flag.** A deployment that occasionally runs commercial work (consulting) needs program-run-granularity. v0.1 of this field is deployment-static; per-run flagging is future work.
2. **Federal-procurement-specific declaration.** Federal deployments are commercial by definition; URML's manifest could declare `deployment_class: federal_procurement` for richer audit. Future RFC.
3. **Verification of declaration honesty.** URML cannot verify a `commercial_use: false` claim. Future RFC could declare attestation requirements (signed declaration, organization-affiliation proof) for federally-procured deployments.

## Implementation plan

1. JSON Schema fragment.
2. Validator with five checks.
3. Conformance tests.
4. Default-policy file optional field documented (unset at v0.1).

Single atomic PR.

## How to respond

Spec RFC. PR thread.

## Shipped (Draft → Implemented, 2026-06-12)

Landed as the single additive top-level block proposed (every existing manifest
stays valid; `manifest_version` stays `0.1`). Third piece of the
translation-licensing stack: it closes RFC-0262's commercial-use-gate loop and
is the last prerequisite before RFC-0304.

- **Schema** (`manifest.py`, spec §2.20): `Deployment` (`commercial_use`
  defaulting to **true**, `deployment_class`, `organization`, `declared_at`) +
  `CapabilityManifest.deployment`.
- **Validator**: a Pass-5 commercial-use gate (`_check_commercial_gate`) — a
  commercial deployment (declared or the most-restrictive default) with a
  `licensing.components[].commercial_use_gate` component is an error under a
  policy (`policy.commercial_use_gate_violated`) and a soft advisory in default
  mode (`capability.commercial_gate_advisory`); plus a Pass-2 class-consistency
  warning (`capability.commercial_use_class_inconsistent`).
- **Conformance**: `conformance/fixtures/deployment/` (commercial+gated
  rejected under policy; non-commercial+gated accepted; commercial+gated
  accepted-with-advisory under no policy) + two registered manifests.
- **Example**: `examples/deployment/commercial-gate` — a production deployment
  declaring CC-BY-NC NLLB weights, refused under the default policy and a soft
  advisory under `--no-policy`.
- **Tests**: `reference/validator/tests/test_deployment.py` (15 cases).

Because RFC-0262's `commercial_use_gate` is now enforced, the RFC-0262
`licensing_clean` conformance manifest and the `licensing/license-boundary`
example were updated to declare `deployment.commercial_use: false` (a deployment
composing CC-BY-NC weights is, honestly, non-commercial), which is exactly the
migration this RFC's backward-compatibility section anticipated.

Scoping: the default-policy `require_commercial_use_declaration` field is left
unset / unimplemented for v0.1 as specified; the most-restrictive default
(missing block ⇒ commercial) is in force. Per-program-run and federal-class
declarations stay deferred (Unresolved §1, §2). With this, the
translation-licensing stack's prerequisites for RFC-0304 (the permissive-
translation alternative serving the engaged NLLB maintainer) are all in place.

## Self-review (Phase 0)

- [x] Four alternatives considered.
- [x] Drawbacks named honestly (most-restrictive default may surprise, informational class, hybrid deployments need binary choice, operator-honesty dependency).
- [x] Backward compatibility additive (existing manifests under v0.1 default policy unchanged).
- [x] No new Layer-2 primitive.
- [x] Conformance tests added (five).
- [x] Cross-references to RFC-0262 (parent), RFC-0003 (default policy), RFC-0167 (motivating outreach RFC).
- [x] CLAUDE.md compliance: federal-procurement narrative completes; declaration-not-verification respects URML's static-validation property (the validator is not an attestation engine).
